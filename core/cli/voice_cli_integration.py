"""
Voice + CLI Integration Module - Unified interface for VoiceOS
Provides seamless switching between voice and CLI interaction modes
"""

import asyncio
import logging
import threading
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import time

from core.events.event_bus import EventBus
from core.events.events import Events
from core.event import Event
from core.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

class InteractionMode(Enum):
    VOICE = "voice"
    CLI = "cli"
    HYBRID = "hybrid"

@dataclass
class InteractionConfig:
    default_mode: InteractionMode = InteractionMode.HYBRID
    enable_voice_interrupts: bool = True
    enable_cli_interrupts: bool = True
    voice_timeout: float = 30.0
    cli_prompt: str = "VoiceOS> "
    show_voice_indicators: bool = True
    auto_switch_to_voice: bool = False

class VoiceCLIIntegration:
    def __init__(self, event_bus: EventBus, orchestrator: Orchestrator, 
                 config: InteractionConfig = None):
        self.event_bus = event_bus
        self.orchestrator = orchestrator
        self.config = config or InteractionConfig()
        
        # Interaction state
        self.current_mode = self.config.default_mode
        self.voice_active = False
        self.cli_active = False
        self.current_input = ""
        
        # Control flags
        self.running = False
        self.interrupt_requested = False
        
        # Callbacks
        self.mode_change_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            "voice_interactions": 0,
            "cli_interactions": 0,
            "interrupts": 0,
            "mode_switches": 0,
            "total_interactions": 0
        }
    
    async def start(self):
        """
        Start the unified interaction system
        """
        self.running = True
        logger.info(f"Starting Voice+CLI Integration in {self.current_mode.value} mode")
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Start interaction loop
        await self._interaction_loop()
    
    def _setup_event_handlers(self):
        """
        Setup event bus subscriptions
        """
        self.event_bus.subscribe(Events.INTERRUPT_REQUESTED, self._handle_interrupt)
        self.event_bus.subscribe(Events.SPEECH_TRANSCRIBED, self._handle_voice_input)
    
    async def _interaction_loop(self):
        """
        Main interaction loop handling both voice and CLI
        """
        try:
            while self.running:
                if self.current_mode == InteractionMode.VOICE:
                    await self._voice_interaction_loop()
                elif self.current_mode == InteractionMode.CLI:
                    await self._cli_interaction_loop()
                else:  # HYBRID
                    await self._hybrid_interaction_loop()
                
                await asyncio.sleep(0.1)  # Prevent busy waiting
                
        except Exception as e:
            logger.error(f"Interaction loop error: {e}")
        finally:
            self.running = False
    
    async def _voice_interaction_loop(self):
        """
        Voice-only interaction loop
        """
        if not self.voice_active:
            logger.info("Voice mode activated")
            self.voice_active = True
            self._notify_mode_change(InteractionMode.VOICE)
        
        # In voice mode, we wait for voice input events
        # The actual voice processing is handled by the STT system
        await asyncio.sleep(0.1)
    
    async def _cli_interaction_loop(self):
        """
        CLI-only interaction loop
        """
        if not self.cli_active:
            logger.info("CLI mode activated")
            self.cli_active = True
            self._notify_mode_change(InteractionMode.CLI)
        
        try:
            # Get CLI input
            user_input = input(self.config.cli_prompt).strip()
            
            if user_input:
                await self._process_cli_input(user_input)
                self.stats["cli_interactions"] += 1
                self.stats["total_interactions"] += 1
            
        except EOFError:
            logger.info("CLI input ended")
            self.running = False
        except KeyboardInterrupt:
            logger.info("CLI interrupt received")
            await self._handle_keyboard_interrupt()
    
    async def _hybrid_interaction_loop(self):
        """
        Hybrid interaction loop supporting both voice and CLI
        """
        if not (self.voice_active and self.cli_active):
            logger.info("Hybrid mode activated - Voice + CLI available")
            self.voice_active = True
            self.cli_active = True
            self._notify_mode_change(InteractionMode.HYBRID)
        
        # In hybrid mode, we check for CLI input while also listening for voice
        try:
            # Non-blocking CLI input check
            user_input = await self._get_cli_input_nonblocking()
            
            if user_input:
                await self._process_cli_input(user_input)
                self.stats["cli_interactions"] += 1
                self.stats["total_interactions"] += 1
            
        except Exception as e:
            logger.debug(f"CLI input check failed: {e}")
        
        # Voice input is handled via events
        await asyncio.sleep(0.1)
    
    async def _get_cli_input_nonblocking(self) -> Optional[str]:
        """
        Get CLI input without blocking
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you'd use a non-blocking input library
            loop = asyncio.get_event_loop()
            
            # Run input in a thread to avoid blocking
            future = loop.run_in_executor(None, input, self.config.cli_prompt)
            
            # Wait with timeout
            try:
                result = await asyncio.wait_for(future, timeout=0.1)
                return result.strip() if result else None
            except asyncio.TimeoutError:
                future.cancel()
                return None
                
        except Exception:
            return None
    
    async def _process_cli_input(self, user_input: str):
        """
        Process CLI input through the orchestrator
        """
        # Handle special CLI commands
        if user_input.lower() in ['quit', 'exit']:
            self.running = False
            return
        elif user_input.lower() == 'voice':
            await self.switch_mode(InteractionMode.VOICE)
            return
        elif user_input.lower() == 'cli':
            await self.switch_mode(InteractionMode.CLI)
            return
        elif user_input.lower() == 'hybrid':
            await self.switch_mode(InteractionMode.HYBRID)
            return
        elif user_input.lower() == 'help':
            self._show_help()
            return
        elif user_input.lower() == 'status':
            await self._show_status()
            return
        elif user_input.lower() == 'mode':
            print(f"Current mode: {self.current_mode.value}")
            return
        
        # Process through orchestrator
        await self.event_bus.publish(Event(
            Events.SPEECH_TRANSCRIBED,
            {"text": user_input, "source": "cli"},
            "voice_cli_integration"
        ))
    
    async def _handle_voice_input(self, event: Event):
        """
        Handle voice input events
        """
        user_input = event.data.get("text", "")
        if not user_input.strip():
            return
        
        # Show voice indicator if enabled
        if self.config.show_voice_indicators:
            print(f"🎤 Voice: {user_input}")
        
        # Process through orchestrator
        self.stats["voice_interactions"] += 1
        self.stats["total_interactions"] += 1
        
        await self.event_bus.publish(Event(
            Events.SPEECH_TRANSCRIBED,
            {"text": user_input, "source": "voice"},
            "voice_cli_integration"
        ))
    
    async def _handle_interrupt(self, event: Event):
        """
        Handle interrupt requests
        """
        reason = event.data.get("reason", "User interrupt")
        logger.info(f"Interrupt received: {reason}")
        
        self.interrupt_requested = True
        self.stats["interrupts"] += 1
        
        # Cancel current operations
        if self.orchestrator.current_execution:
            await self.orchestrator._handle_interrupt(event)
    
    async def _handle_keyboard_interrupt(self):
        """
        Handle keyboard interrupt (Ctrl+C)
        """
        logger.info("Keyboard interrupt received")
        
        if self.current_mode == InteractionMode.HYBRID:
            # In hybrid mode, switch to CLI mode
            await self.switch_mode(InteractionMode.CLI)
        else:
            # In single mode, handle as interrupt
            await self._handle_interrupt(Event(
                Events.INTERRUPT_REQUESTED,
                {"reason": "Keyboard interrupt"},
                "voice_cli_integration"
            ))
    
    async def switch_mode(self, new_mode: InteractionMode):
        """
        Switch interaction mode
        """
        if new_mode == self.current_mode:
            return
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.stats["mode_switches"] += 1
        
        logger.info(f"Switched from {old_mode.value} to {new_mode.value} mode")
        self._notify_mode_change(new_mode)
        
        # Update active states
        if new_mode == InteractionMode.VOICE:
            self.cli_active = False
        elif new_mode == InteractionMode.CLI:
            self.voice_active = False
        else:  # HYBRID
            self.voice_active = True
            self.cli_active = True
    
    def _notify_mode_change(self, new_mode: InteractionMode):
        """
        Notify callbacks of mode change
        """
        for callback in self.mode_change_callbacks:
            try:
                callback(self.current_mode, new_mode)
            except Exception as e:
                logger.error(f"Mode change callback failed: {e}")
    
    def _show_help(self):
        """
        Show help information
        """
        help_text = f"""
VoiceOS Hybrid Interface - Current Mode: {self.current_mode.value}

Commands:
  help     - Show this help
  status   - Show system status
  mode     - Show current mode
  voice    - Switch to voice-only mode
  cli      - Switch to CLI-only mode
  hybrid   - Switch to hybrid mode (voice + CLI)
  quit     - Exit VoiceOS

Voice Commands:
  "open chrome"                    - Open application
  "type hello world"              - Type text
  "research reinforcement learning" - Research topic
  "write python function"         - Code development
  "analyze data.csv"              - Data analysis

Interrupts:
  Ctrl+C                           - Interrupt current operation
  "stop" / "cancel"               - Voice interrupt
"""
        print(help_text)
    
    async def _show_status(self):
        """
        Show system status
        """
        try:
            health = await self.orchestrator.health_check()
            metrics = self.orchestrator.get_metrics()
            
            print(f"""
=== VoiceOS Status ===
Mode: {self.current_mode.value}
System Health: {health['status']}

Interactions:
  Total: {self.stats['total_interactions']}
  Voice: {self.stats['voice_interactions']}
  CLI: {self.stats['cli_interactions']}
  Interrupts: {self.stats['interrupts']}
  Mode Switches: {self.stats['mode_switches']}

Performance:
  Requests: {metrics['total_requests']}
  Simple Tasks: {metrics['simple_tasks']}
  Complex Tasks: {metrics['complex_tasks']}
  Success Rate: {metrics['success_rate']:.1%}
  Avg Latency: {metrics['average_latency']:.2f}s

Configuration:
  Voice Interrupts: {self.config.enable_voice_interrupts}
  CLI Interrupts: {self.config.enable_cli_interrupts}
  Voice Timeout: {self.config.voice_timeout}s
========================
""")
        except Exception as e:
            print(f"Error getting status: {e}")
    
    def add_mode_change_callback(self, callback: Callable):
        """
        Add callback for mode changes
        """
        self.mode_change_callbacks.append(callback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get interaction statistics
        """
        return {
            **self.stats,
            "current_mode": self.current_mode.value,
            "voice_active": self.voice_active,
            "cli_active": self.cli_active,
            "running": self.running
        }
    
    def reset_statistics(self):
        """
        Reset interaction statistics
        """
        self.stats = {
            "voice_interactions": 0,
            "cli_interactions": 0,
            "interrupts": 0,
            "mode_switches": 0,
            "total_interactions": 0
        }
    
    async def stop(self):
        """
        Stop the interaction system
        """
        self.running = False
        self.voice_active = False
        self.cli_active = False
        logger.info("Voice+CLI Integration stopped")
