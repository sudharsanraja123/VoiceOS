"""
VoiceOS Plugin System

This module contains all components related to plugin management,
including secure integration, lifecycle management, registry,
configuration, error handling, monitoring, and testing.
"""

from .secure_plugin_integration import get_secure_plugin_adapter
from .plugin_lifecycle import get_lifecycle_manager
from .plugin_registry import get_plugin_registry
from .plugin_configuration import get_plugin_config_manager
from .plugin_error_handling import get_plugin_error_handler
from .plugin_monitoring import get_plugin_monitor
from .plugin_testing import get_plugin_test_framework
from .complete_plugin_integration import get_complete_plugin_system

__all__ = [
    'get_secure_plugin_adapter',
    'get_lifecycle_manager',
    'get_plugin_registry',
    'get_plugin_config_manager',
    'get_plugin_error_handler',
    'get_plugin_monitor',
    'get_plugin_test_framework',
    'get_complete_plugin_system'
]
