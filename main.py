"""
VoiceOS Main Entry Point

This is the main entry point for the VoiceOS multi-agent system.
It initializes all components and starts the voice + CLI driven operating system.
"""

import asyncio
import logging
import argparse
import sys

from core.events.event_bus import EventBus
from core.event import Event
from core.events.events import Events
from core.config import config
from core.logger import logger
from core.orchestrator import Orchestrator, OrchestratorConfig
from core.cli.voice_cli_integration import VoiceCLIIntegration, InteractionConfig, InteractionMode
from core.config_manager import ConfigManager
from core.security import VoiceOSSecurity
from core.monitoring.performance_monitor import PerformanceMonitor
from core.monitoring.error_recovery import ErrorRecovery

from llm.conversation_engine import ConversationEngine
from llm.agent_llm import AgentLLM
from permissions.permission_engine import PermissionEngine

from interrupt.speech_state import SpeechState
from interrupt.interrupt_controller import InterruptController
from interrupt.tts_controller import TTSController
from tts.coqui_engine import TTSEngine

from listener.backchannel_engine import BackchannelEngine

from tools.register_tools import register_tools
from tools.tool_executor import ToolExecutor
from tools.tool_registry import ToolRegistry
from tools.system_integration import SystemIntegration
from core.cli.response_builder import ResponseBuilder

from model_manager.model_manager import ModelManager


async def main():
    """
    VoiceOS Main Entry Point - Complete Multi-Agent System.
    
    Initializes all VoiceOS components including agents, tools, LLM integration,
    and starts the voice + CLI driven operating system.
    """
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup configuration
    config_manager = ConfigManager()
    voiceos_config = config_manager.get_config()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, voiceos_config.logging.level),
        format=voiceos_config.logging.format
    )
    logger.info("Starting VoiceOS Multi-Agent Operating System...")
    
    try:
        # Initialize core infrastructure
        bus = EventBus()
        
        # Initialize advanced components
        security = VoiceOSSecurity()
        performance_monitor = PerformanceMonitor()
        error_recovery = ErrorRecovery()
        
        # Initialize tool systems
        tool_registry = ToolRegistry()
        system_integration = SystemIntegration(bus, PermissionEngine(bus))
        
        # Initialize LLM systems
        agent_llm = AgentLLM()
        
        # Initialize core components
        registry = register_tools()
        tool_executor = ToolExecutor(bus, registry)
        permission_engine = PermissionEngine(bus)
        
        # Initialize orchestrator with hybrid agent system
        orchestrator_config = OrchestratorConfig(
            enable_interrupts=True,
            max_execution_time=300.0,
            enable_workspace_isolation=True,
            safety_mode="strict"
        )
        
        orchestrator = Orchestrator(
            event_bus=bus,
            tool_executor=tool_executor,
            permission_engine=permission_engine,
            config=orchestrator_config
        )
        
        # Initialize voice components
        speech_state = SpeechState()
        tts_engine = TTSEngine()
        
        BackchannelEngine(bus)
        InterruptController(bus, speech_state)
        TTSController(bus, tts_engine, speech_state)
        ConversationEngine(bus)
        ResponseBuilder(bus)
        
        # Initialize model manager
        manager = ModelManager()
        model_paths = manager.ensure_models()
        logger.info(f"Model paths: {model_paths}")
        
        # Initialize Voice+CLI integration
        interaction_config = InteractionConfig(
            default_mode=InteractionMode.HYBRID if args.mode == "hybrid" else 
                         InteractionMode.VOICE if args.mode == "voice" else 
                         InteractionMode.CLI,
            enable_voice_interrupts=True,
            enable_cli_interrupts=True
        )
        
        voice_cli = VoiceCLIIntegration(bus, orchestrator, interaction_config)
        
        # Subscribe to orchestrator responses
        async def handle_orchestrator_response(event: Event):
            """Handle orchestrator responses"""
            response_text = event.data.get("text", "")
            if response_text:
                logger.info(f"VoiceOS Response: {response_text}")
                print(f"VoiceOS: {response_text}")
        
        bus.subscribe(Events.ORCHESTRATOR_RESPONSE, handle_orchestrator_response)
        
        # Health check
        health = await orchestrator.health_check()
        logger.info(f"System health: {health['status']}")
        
        # Handle special commands
        if args.status:
            await print_system_status(orchestrator, performance_monitor, security)
            return
        
        if args.test:
            await run_system_tests(orchestrator)
            return
        
        # Start the system
        logger.info("VoiceOS Multi-Agent System ready.")
        logger.info("Features: Voice + CLI interaction, Dynamic agents, System control, Code development")
        
        # Start Voice+CLI integration
        await voice_cli.start()
        
    except KeyboardInterrupt:
        logger.info("Interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"System error: {e}")
        raise
    finally:
        logger.info("VoiceOS shutdown complete.")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="VoiceOS Multi-Agent Operating System")
    
    parser.add_argument("--mode", choices=["voice", "cli", "hybrid"], default="hybrid",
                       help="Interaction mode")
    parser.add_argument("--status", action="store_true",
                       help="Show system status and exit")
    parser.add_argument("--test", action="store_true",
                       help="Run system tests and exit")
    parser.add_argument("--config", type=str,
                       help="Configuration file path")
    
    return parser.parse_args()

def print_help():
    """Print available commands"""
    help_text = """
VoiceOS Hybrid Agent System Commands:
  help     - Show this help message
  status   - Show system status and health
  metrics  - Show performance metrics
  quit     - Exit VoiceOS
  
Example voice commands:
  "open chrome"                    - Simple task (direct execution)
  "research reinforcement learning" - Complex task (dynamic agent)
  "type hello world"              - Simple task
  "analyze latest AI news"        - Complex task
"""
    print(help_text)

async def print_system_status(orchestrator, performance_monitor, security):
    """Print comprehensive system status"""
    try:
        print("\n" + "="*60)
        print("VOICEOS MULTI-AGENT OPERATING SYSTEM STATUS")
        print("="*60)
        
        # Orchestrator status
        health = await orchestrator.health_check()
        print(f"\n🎯 Core System: {health['status'].upper()}")
        print(f"  Planner: {health['components'].get('planner', 'unknown')}")
        print(f"  Router: {health['components'].get('router', {}).get('status', 'unknown')}")
        print(f"  Tool Executor: {health['components'].get('tool_executor', 'unknown')}")
        print(f"  Permission Engine: {health['components'].get('permission_engine', 'unknown')}")
        
        # Performance metrics
        metrics = orchestrator.get_metrics()
        print(f"\n📊 Performance:")
        print(f"  Total Requests: {metrics['total_requests']}")
        print(f"  Simple Tasks: {metrics['simple_tasks']}")
        print(f"  Complex Tasks: {metrics['complex_tasks']}")
        print(f"  Success Rate: {metrics['success_rate']:.1%}")
        print(f"  Avg Latency: {metrics['average_latency']:.2f}s")
        
        # Security status
        security_stats = security.get_security_statistics()
        print(f"\n🔒 Security:")
        print(f"  Total Requests: {security_stats['total_requests']}")
        print(f"  Blocked Requests: {security_stats['blocked_requests']}")
        print(f"  Active Sessions: {security_stats['active_sessions']}")
        print(f"  Blocked IPs: {security_stats['blocked_ips']}")
        
        # Available agents
        print(f"\n🤖 Available Agents:")
        print(f"  Researcher - Web research and analysis")
        print(f"  Developer - Code development and review")
        print(f"  Analyst - Data processing and insights")
        
        # Available tools
        print(f"\n🛠️  System Tools:")
        print(f"  Application Control - Open/close/focus apps")
        print(f"  File Operations - Read/write/edit files")
        print(f"  Web Search - Research and content extraction")
        print(f"  Data Analysis - Process and analyze data")
        print(f"  Code Tools - Development and testing")
        
        print(f"\n🚀 Ready for Voice + CLI interaction")
        print("="*60)
        
    except Exception as e:
        print(f"Error getting system status: {e}")

async def run_system_tests(orchestrator):
    """Run system tests"""
    try:
        print("\n" + "="*50)
        print("VOICEOS SYSTEM TESTS")
        print("="*50)
        
        # Test orchestrator health
        health = await orchestrator.health_check()
        print(f"✅ Orchestrator Health: {health['status']}")
        
        # Test tool registry
        from tools.tool_registry import ToolRegistry
        registry = ToolRegistry()
        tools = registry.list_tools()
        print(f"✅ Tool Registry: {len(tools)} tools available")
        
        # Test agent roles
        import os
        roles_dir = "agents/roles"
        if os.path.exists(roles_dir):
            roles = [d for d in os.listdir(roles_dir) if os.path.isdir(os.path.join(roles_dir, d))]
            print(f"✅ Agent Roles: {len(roles)} roles configured")
        
        print(f"\n🎉 All system tests passed!")
        print("="*50)
        
    except Exception as e:
        print(f"❌ System test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())