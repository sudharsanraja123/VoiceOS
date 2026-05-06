"""
Dynamic Agent Runner Module
Executes dynamic agents with LLM integration and tool invocation
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import logging

from agents.dynamic.agent_builder import DynamicAgent, AgentConfig
from agents.core.planner import TaskPlan
from llm.streaming_llm import StreamingLLM
from workspace.workspace_manager import WorkspaceManager

logger = logging.getLogger(__name__)

@dataclass
class AgentStep:
    step_number: int
    action: str
    tool: Optional[str]
    parameters: Dict[str, Any]
    result: Any
    timestamp: float
    duration: float

@dataclass
class AgentExecution:
    agent_id: str
    workspace_id: str
    steps: List[AgentStep]
    final_result: Any
    success: bool
    total_time: float
    error: Optional[str] = None

class AgentRunner:
    def __init__(self, tool_executor):
        self.tool_executor = tool_executor
        self.llm = StreamingLLM()
        self.workspace_manager = WorkspaceManager()
        
        # Execution tracking
        self.active_executions = {}
        self.execution_history = []
    
    async def run_agent(self, agent: DynamicAgent, user_input: str, plan: TaskPlan) -> AgentExecution:
        """
        Run a dynamic agent with the given input and plan
        """
        execution_id = f"{agent.workspace_id}_{int(time.time())}"
        start_time = time.time()
        
        logger.info(f"Starting agent execution: {execution_id}")
        
        try:
            # Create workspace for this execution
            workspace = await self.workspace_manager.create_workspace(
                workspace_id=agent.workspace_id,
                agent_config=agent.config
            )
            
            # Initialize execution state
            execution = AgentExecution(
                agent_id=agent.config.name,
                workspace_id=agent.workspace_id,
                steps=[],
                final_result=None,
                success=False,
                total_time=0.0
            )
            
            # Track active execution
            self.active_executions[execution_id] = execution
            
            # Execute agent loop
            result = await self._execute_agent_loop(
                agent=agent,
                user_input=user_input,
                plan=plan,
                workspace=workspace,
                execution=execution
            )
            
            # Finalize execution
            execution.final_result = result
            execution.success = True
            execution.total_time = time.time() - start_time
            
            # Store execution history
            self.execution_history.append(execution)
            
            # Clean up workspace
            await self.workspace_manager.cleanup_workspace(agent.workspace_id)
            
            logger.info(f"Agent execution completed: {execution_id} in {execution.total_time:.2f}s")
            
            return execution
            
        except Exception as e:
            execution.total_time = time.time() - start_time
            execution.error = str(e)
            execution.success = False
            
            logger.error(f"Agent execution failed: {execution_id} - {e}")
            
            return execution
            
        finally:
            # Remove from active executions
            self.active_executions.pop(execution_id, None)
    
    async def _execute_agent_loop(self, agent: DynamicAgent, user_input: str, plan: TaskPlan, 
                                 workspace, execution: AgentExecution) -> Any:
        """
        Execute the main agent loop with LLM and tools
        """
        # Prepare initial context
        context = {
            "user_input": user_input,
            "plan": {
                "intent": plan.intent,
                "steps": plan.steps,
                "tools_required": plan.tools_required
            },
            "workspace": workspace.workspace_id,
            "available_tools": list(agent.tools.keys()),
            "step_count": 0,
            "max_steps": agent.config.max_steps
        }
        
        # Build system prompt
        system_prompt = self._build_system_prompt(agent.config, context)
        
        # Start conversation
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        step_count = 0
        final_result = None
        
        while step_count < agent.config.max_steps:
            step_count += 1
            step_start_time = time.time()
            
            logger.info(f"Agent step {step_count}/{agent.config.max_steps}")
            
            try:
                # Get LLM response
                response = await self._get_llm_response(messages, agent.config)
                
                # Parse action from response
                action = await self._parse_action(response)
                
                if not action:
                    logger.warning("No action parsed from LLM response")
                    break
                
                # Execute action
                step_result = await self._execute_action(action, agent, workspace)
                
                # Record step
                step = AgentStep(
                    step_number=step_count,
                    action=action.get("action", "unknown"),
                    tool=action.get("tool"),
                    parameters=action.get("parameters", {}),
                    result=step_result,
                    timestamp=step_start_time,
                    duration=time.time() - step_start_time
                )
                execution.steps.append(step)
                
                # Update context
                context["step_count"] = step_count
                context["last_result"] = step_result
                
                # Check if task is complete
                if action.get("action") == "complete" or self._is_task_complete(action, step_result):
                    final_result = action.get("result", step_result)
                    break
                
                # Add response to conversation
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "system", "content": f"Step {step_count} result: {step_result}"})
                
                # Check timeout
                if time.time() - step_start_time > agent.config.timeout:
                    logger.warning(f"Agent timeout after {agent.config.timeout}s")
                    break
                
            except Exception as e:
                logger.error(f"Agent step {step_count} failed: {e}")
                break
        
        if not final_result:
            final_result = context.get("last_result", "Task incomplete")
        
        return final_result
    
    def _build_system_prompt(self, config: AgentConfig, context: Dict[str, Any]) -> str:
        """
        Build system prompt for the agent
        """
        base_prompt = config.system_prompt
        
        # Add context information
        context_info = f"""
Context:
- User Input: {context['user_input']}
- Intent: {context['plan']['intent']}
- Available Tools: {', '.join(context['available_tools'])}
- Max Steps: {context['max_steps']}
- Workspace: {context['workspace']}

You must respond with a JSON action in this format:
{{
    "action": "tool_name|complete|think",
    "tool": "tool_name_if_applicable",
    "parameters": {{"key": "value"}},
    "reasoning": "why you chose this action"
}}

Available actions:
- Use any tool from available_tools
- "complete" if task is done
- "think" to reason without tools
"""
        
        return f"{base_prompt}\n\n{context_info}"
    
    async def _get_llm_response(self, messages: List[Dict], config: AgentConfig) -> str:
        """
        Get response from LLM
        """
        try:
            # Stream response for low latency
            response_chunks = []
            
            async for chunk in self.llm.stream_response(messages):
                response_chunks.append(chunk)
                
                # Early termination if we detect a complete action
                if len(response_chunks) > 50 and "complete" in ''.join(response_chunks[-10:]):
                    break
            
            return ''.join(response_chunks)
            
        except Exception as e:
            logger.error(f"LLM response failed: {e}")
            return '{"action": "complete", "result": "LLM error occurred"}'
    
    async def _parse_action(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse action from LLM response
        """
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            
            # Fallback: try to parse simple action
            if "complete" in response.lower():
                return {"action": "complete", "result": response}
            elif "think" in response.lower():
                return {"action": "think", "reasoning": response}
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse action: {e}")
            return None
    
    async def _execute_action(self, action: Dict[str, Any], agent: DynamicAgent, workspace) -> Any:
        """
        Execute the parsed action
        """
        action_type = action.get("action")
        
        if action_type == "complete":
            return action.get("result", "Task completed")
        
        elif action_type == "think":
            return {"thought": action.get("reasoning", "Thinking")}
        
        elif action_type in agent.tools:
            tool_name = action_type
            tool = agent.tools[tool_name]
            parameters = action.get("parameters", {})
            
            # Add workspace context to parameters
            parameters["workspace_id"] = workspace.workspace_id
            
            # Execute tool
            try:
                result = await self.tool_executor.execute_tool(tool_name, parameters)
                return result
            except Exception as e:
                logger.error(f"Tool execution failed {tool_name}: {e}")
                return {"error": str(e)}
        
        else:
            return {"error": f"Unknown action: {action_type}"}
    
    def _is_task_complete(self, action: Dict[str, Any], result: Any) -> bool:
        """
        Check if the task is complete based on action and result
        """
        if action.get("action") == "complete":
            return True
        
        # Check if result indicates completion
        if isinstance(result, dict) and result.get("status") == "completed":
            return True
        
        # Check for success indicators
        if isinstance(result, str) and any(indicator in result.lower() 
                                          for indicator in ["completed", "done", "finished", "summary"]):
            return True
        
        return False
    
    def get_active_executions(self) -> Dict[str, AgentExecution]:
        """
        Get currently active executions
        """
        return self.active_executions.copy()
    
    def get_execution_history(self, limit: int = 10) -> List[AgentExecution]:
        """
        Get recent execution history
        """
        return self.execution_history[-limit:]
    
    def clear_history(self):
        """
        Clear execution history
        """
        self.execution_history.clear()
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an active execution
        """
        if execution_id in self.active_executions:
            execution = self.active_executions[execution_id]
            execution.success = False
            execution.error = "Cancelled by user"
            return True
        return False
