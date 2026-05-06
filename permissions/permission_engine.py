"""
VoiceOS Permission Engine

This module provides permission management and validation for VoiceOS operations,
ensuring safe and controlled access to system resources and tools.
"""

from enum import Enum
from functools import wraps
from typing import Callable, Any
import logging
from core.events.events import Events
from core.event import Event
from core.logger import logger


class PermissionLevel(Enum):
    """
    Permission levels for VoiceOS operations.
    
    Defines hierarchical permission levels for controlling access
    to different types of operations and resources.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PermissionEngine:
    """
    Permission validation and management system for VoiceOS.
    
    This engine handles permission checking, user permission levels,
    and provides decorators for enforcing permissions on tool methods.
    
    Attributes:
        event_bus: Event bus for permission events
        current_user_level (PermissionLevel): Current user permission level
    """

    def __init__(self, event_bus=None):
        """
        Initialize permission engine.
        
        Args:
            event_bus: Event bus for publishing permission events
        """
        self.event_bus = event_bus
        self.current_user_level = PermissionLevel.MEDIUM  # Default user permission
        
        if event_bus:
            event_bus.subscribe(Events.LLM_DECISION, self.check_permission)

    async def check_permission(self, event):
        """
        Check permission for LLM decision event.
        
        Args:
            event: Permission check event with decision payload
        """
        decision = event.payload

        if decision["requires_permission"]:
            logger.info("\nAssistant:")
            logger.info(decision["reasoning"])
            logger.info("Do you approve? (yes/no)")

            answer = input("> ")

            if answer.lower() == "yes":
                await self.event_bus.publish(
                    Event(
                        Events.PERMISSION_GRANTED,
                        decision,
                        "permission_engine"
                    )
                )
            else:
                await self.event_bus.publish(
                    Event(
                        Events.PERMISSION_DENIED,
                        decision,
                        "permission_engine"
                    )
                )

    def set_user_permission_level(self, level: PermissionLevel):
        """
        Set the current user's permission level.
        
        Args:
            level (PermissionLevel): Permission level to set
        """
        self.current_user_level = level
        logger.info(f"User permission level set to: {level.value}")

    def check_tool_permission(self, required_level: PermissionLevel) -> bool:
        """
        Check if current user has permission for required level.
        
        Args:
            required_level (PermissionLevel): Required permission level
            
        Returns:
            bool: True if user has sufficient permissions
        """
        level_hierarchy = {
            PermissionLevel.LOW: 0,
            PermissionLevel.MEDIUM: 1,
            PermissionLevel.HIGH: 2
        }
        
        user_level = level_hierarchy.get(self.current_user_level, 0)
        required_level_value = level_hierarchy.get(required_level, 0)
        
        return user_level >= required_level_value

    def request_permission(self, tool_name: str, method: str, required_level: PermissionLevel, context: dict = None) -> bool:
        """
        Request permission for a tool operation.
        
        Args:
            tool_name (str): Name of the tool
            method (str): Method name
            required_level (PermissionLevel): Required permission level
            context (dict, optional): Additional context
            
        Returns:
            bool: True if permission granted
        """
        if self.check_tool_permission(required_level):
            logger.info(f"Permission granted for {tool_name}.{method} (level: {required_level.value})")
            return True
        
        logger.warning(f"Permission denied for {tool_name}.{method} - requires {required_level.value}, user has {self.current_user_level.value}")
        
        # Could implement interactive permission request here
        if self.event_bus:
            # Publish permission request event
            pass
        
        return False


# Global permission engine instance
permission_engine = PermissionEngine()


def check_permission(required_level: PermissionLevel):
    """
    Decorator to check permissions before executing a method.
    
    Args:
        required_level (PermissionLevel): Required permission level
        
    Returns:
        Callable: Decorated function with permission checking
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get tool name from class if available
            tool_name = "unknown"
            if args and hasattr(args[0], '__class__'):
                tool_name = args[0].__class__.__name__.lower()
            
            method_name = func.__name__
            
            # Check permission
            if not permission_engine.check_tool_permission(required_level):
                raise PermissionError(f"Insufficient permissions for {tool_name}.{method_name}. Requires: {required_level.value}")
            
            # Execute function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator