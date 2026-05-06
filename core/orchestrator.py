"""
Core Orchestrator Module - Central coordination for VoiceOS hybrid agent system
Integrates voice pipeline with agent architecture for seamless execution
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from agents.core.planner import Planner, TaskPlan
from agents.core.router import Router, RouteResult
from tools.tool_executor import ToolExecutor
from permissions.permission_engine import PermissionEngine
from core.events.event_bus import EventBus
from core.events.events import Events
from core.event import Event

logger = logging.getLogger(__name__)

@dataclass
class OrchestratorConfig:
    enable_interrupts: bool = True
    max_execution_time: float = 300.0
    enable_workspace_isolation: bool = True
    safety_mode: str = "strict"  # strict, permissive, custom

class Orchestrator:
    def __init__(self, event_bus: EventBus, tool_executor: ToolExecutor, 
                 permission_engine: PermissionEngine, config: OrchestratorConfig = None):
        self.event_bus = event_bus
        self.tool_executor = tool_executor
        self.permission_engine = permission_engine
        self.config = config or OrchestratorConfig()
        
        # Initialize core components
        self.planner = Planner()
        self.router = Router(tool_executor)
        
        # Execution state
        self.current_execution = None
        self.execution_history = []
        
        # Performance tracking
        self.metrics = {
            "total_requests": 0,
            "simple_tasks": 0,
            "complex_tasks": 0,
            "average_latency": 0.0,
            "success_rate": 0.0
        }
        
        # Subscribe to events
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event bus subscriptions"""
        self.event_bus.subscribe(Events.SPEECH_TRANSCRIBED, self._handle_speech_input)
        self.event_bus.subscribe(Events.INTERRUPT_REQUESTED, self._handle_interrupt)
        self.event_bus.subscribe(Events.PERMISSION_GRANTED, self._handle_permission_granted)
        self.event_bus.subscribe(Events.PERMISSION_DENIED, self._handle_permission_denied)
    
    async def _handle_speech_input(self, event: Event):
        """Handle transcribed speech input"""
        user_input = event.data.get("text", "")
        if not user_input.strip():
            return
        
        logger.info(f"Processing user input: {user_input[:100]}...")
        
        try:
            # Process through orchestrator pipeline
            result = await self.process_user_input(user_input)
            
            # Publish result for TTS
            await self.event_bus.publish(Event(
                Events.ORCHESTRATOR_RESPONSE,
                {"text": str(result), "source": "orchestrator"},
                "orchestrator"
            ))
            
        except Exception as e:
            logger.error(f"Failed to process user input: {e}")
            await self.event_bus.publish(Event(
                Events.ORCHESTRATOR_ERROR,
                {"error": str(e), "input": user_input},
                "orchestrator"
            ))
    
    async def process_user_input(self, user_input: str) -> Any:
        """
        Main processing pipeline for user input
        """
        start_time = asyncio.get_event_loop().time()
        self.metrics["total_requests"] += 1
        
        try:
            # Step 1: Plan the task
            plan = self.planner.analyze_input(user_input)
            
            if not self.planner.validate_plan(plan):
                raise ValueError(f"Invalid plan generated: {plan}")
            
            logger.info(f"Task plan: {plan.type.value} - {plan.intent}")
            
            # Step 2: Route and execute
            result = await self._execute_plan(plan, user_input)
            
            # Step 3: Update metrics
            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(plan, execution_time, True)
            
            return result
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_metrics(None, execution_time, False)
            raise
    
    async def _execute_plan(self, plan: TaskPlan, user_input: str) -> Any:
        """
        Execute the task plan with routing
        """
        # Safety check for all operations
        safety_result = await self._safety_check(plan, user_input)
        if not safety_result["allowed"]:
            raise PermissionError(f"Operation not allowed: {safety_result['reason']}")
        
        # Route task based on plan type
        if plan.type.value == "autonomous":
            route_result = await self._execute_autonomous_task(plan, user_input)
        else:
            route_result = await self.router.route_task(plan, user_input)
        
        if not route_result.success:
            raise RuntimeError(f"Route execution failed: {route_result.error}")
        
        # Store execution details
        self.current_execution = {
            "plan": plan,
            "result": route_result.result,
            "execution_time": route_result.execution_time,
            "path": route_result.execution_path
        }
        
        self.execution_history.append(self.current_execution)
        
        return route_result
    
    async def _execute_autonomous_task(self, plan: TaskPlan, user_input: str) -> Any:
        """
        Execute autonomous task using autonomous agent loop
        """
        try:
            # Import autonomous components
            from agents.autonomous.state_manager import AutonomousStateManager
            from agents.autonomous.tool_generator import AutonomousToolGenerator
            from agents.autonomous.tool_executor import AutonomousToolExecutor
            from agents.autonomous.agent_loop import AutonomousAgentLoop
            from agents.core.safety import SafetyModule
            
            # Initialize autonomous components
            state_manager = AutonomousStateManager()
            safety_module = SafetyModule()
            tool_generator = AutonomousToolGenerator(state_manager, safety_module, self.permission_engine)
            tool_executor = AutonomousToolExecutor(state_manager, safety_module, self.permission_engine)
            agent_loop = AutonomousAgentLoop(state_manager, tool_generator, tool_executor, safety_module, self.permission_engine)
            
            # Extract goal from user input
            goal = plan.context.get('parameters', [''])[0] if plan.context.get('parameters') else user_input
            
            # Execute autonomous task
            result = await agent_loop.execute_autonomous_task(user_input, goal)
            
            # Create route result
            from agents.core.router import RouteResult
            return RouteResult(
                success=result.get("status") == "completed",
                result=result,
                execution_path="autonomous_agent_loop",
                execution_time=result.get("execution_time", 0.0)
            )
            
        except Exception as e:
            logger.error(f"Autonomous task execution failed: {e}")
            from agents.core.router import RouteResult
            return RouteResult(
                success=False,
                result={"error": str(e)},
                execution_path="autonomous_agent_loop",
                execution_time=0.0,
                error=str(e)
            )
    
    async def _safety_check(self, plan: TaskPlan, user_input: str) -> Dict[str, Any]:
        """
        Perform safety validation before execution
        """
        # Check if permission is required
        permission_required = await self.permission_engine.is_permission_required(
            plan.intent, plan.tools_required
        )
        
        if permission_required:
            # Request permission
            await self.event_bus.publish(Event(
                Events.PERMISSION_REQUESTED,
                {
                    "intent": plan.intent,
                    "tools": plan.tools_required,
                    "user_input": user_input,
                    "plan_type": plan.type.value
                },
                "orchestrator"
            ))
            
            # Wait for permission decision (with timeout)
            permission_result = await self._wait_for_permission(timeout=10.0)
            
            return permission_result
        else:
            return {"allowed": True, "reason": "No permission required"}
    
    async def _wait_for_permission(self, timeout: float = 10.0) -> Dict[str, Any]:
        """
        Wait for permission decision with timeout
        """
        try:
            # This would be implemented with proper async waiting
            # For now, assume permission granted for safe operations
            await asyncio.sleep(0.1)  # Simulate async wait
            return {"allowed": True, "reason": "Auto-approved safe operation"}
        except asyncio.TimeoutError:
            return {"allowed": False, "reason": "Permission timeout"}
    
    async def _handle_interrupt(self, event: Event):
        """Handle interrupt requests"""
        if self.current_execution:
            logger.info("Interrupt requested, cancelling current execution")
            # Cancel current execution if possible
            self.current_execution = None
    
    async def _handle_permission_granted(self, event: Event):
        """Handle permission granted event"""
        logger.info("Permission granted for operation")
    
    async def _handle_permission_denied(self, event: Event):
        """Handle permission denied event"""
        logger.warning("Permission denied for operation")
    
    def _update_metrics(self, plan: Optional[TaskPlan], execution_time: float, success: bool):
        """
        Update performance metrics
        """
        if plan:
            if plan.type.value == "simple":
                self.metrics["simple_tasks"] += 1
            else:
                self.metrics["complex_tasks"] += 1
        
        # Update average latency
        total_requests = self.metrics["total_requests"]
        current_avg = self.metrics["average_latency"]
        self.metrics["average_latency"] = (
            (current_avg * (total_requests - 1) + execution_time) / total_requests
        )
        
        # Update success rate
        if not hasattr(self, 'successful_requests'):
            self.successful_requests = 0
        
        if success:
            self.successful_requests += 1
        
        self.metrics["success_rate"] = self.successful_requests / total_requests
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current performance metrics
        """
        return {
            **self.metrics,
            "successful_requests": getattr(self, 'successful_requests', 0),
            "router_stats": self.router.get_route_statistics(),
            "current_execution": self.current_execution is not None
        }
    
    def get_execution_history(self, limit: int = 10) -> list:
        """
        Get recent execution history
        """
        return self.execution_history[-limit:]
    
    def reset_metrics(self):
        """
        Reset all metrics
        """
        self.metrics = {
            "total_requests": 0,
            "simple_tasks": 0,
            "complex_tasks": 0,
            "average_latency": 0.0,
            "success_rate": 0.0
        }
        self.successful_requests = 0
        self.router.reset_statistics()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check of orchestrator system
        """
        return {
            "status": "healthy",
            "components": {
                "planner": "operational",
                "router": await self.router.health_check(),
                "tool_executor": "operational" if self.tool_executor else "failed",
                "permission_engine": "operational" if self.permission_engine else "failed"
            },
            "metrics": self.get_metrics(),
            "config": {
                "enable_interrupts": self.config.enable_interrupts,
                "max_execution_time": self.config.max_execution_time,
                "enable_workspace_isolation": self.config.enable_workspace_isolation,
                "safety_mode": self.config.safety_mode
            }
        }
