"""
VoiceOS Complete Plugin Integration System

This module demonstrates the complete integration of all plugin system components
while maintaining VoiceOS security boundaries, architectural purity, and permission-first principles.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

from core.config import config
from tools.tool_registry import ToolRegistry
from core.plugins.secure_plugin_integration import get_secure_plugin_adapter
from core.integration.integration_patterns import get_integration_manager
from core.integration.controlled_execution import get_controlled_execution_manager
from core.plugins.plugin_lifecycle import get_lifecycle_manager
from core.plugins.plugin_registry import get_plugin_registry, DiscoveryConfig
from core.plugins.plugin_configuration import get_plugin_config_manager
from core.plugins.plugin_error_handling import get_plugin_error_handler
from core.plugins.plugin_monitoring import get_plugin_monitor
from core.plugins.plugin_testing import get_plugin_test_framework


class VoiceOSCompletePluginSystem:
    """
    Complete plugin integration system for VoiceOS.
    
    This class orchestrates all plugin system components while maintaining
    security boundaries, architectural purity, and permission-first principles.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger(__name__)
        
        # Initialize all components
        self.tool_registry = ToolRegistry()
        self.secure_adapter = get_secure_plugin_adapter(self.tool_registry)
        self.integration_manager = get_integration_manager(None, self.tool_registry)
        self.execution_manager = get_controlled_execution_manager()
        self.lifecycle_manager = get_lifecycle_manager()
        self.plugin_registry = get_plugin_registry()
        self.config_manager = get_plugin_config_manager()
        self.error_handler = get_plugin_error_handler()
        self.monitor = get_plugin_monitor()
        self.test_framework = get_plugin_test_framework()
        
        # System state
        self.system_initialized = False
        self.system_running = False
    
    async def initialize_system(self, discovery_directories: Optional[List[Path]] = None) -> Dict[str, Any]:
        """
        Initialize the complete plugin system.
        
        Args:
            discovery_directories: Directories to scan for plugins
            
        Returns:
            Initialization result
        """
        self.logger.info("Initializing VoiceOS Complete Plugin System...")
        
        try:
            # Initialize component systems
            await self.lifecycle_manager.start_lifecycle_management()
            await self.error_handler.start_error_handling()
            await self.monitor.start_monitoring()
            
            # Initialize plugin registry with discovery configuration
            discovery_config = DiscoveryConfig(
                scan_directories=discovery_directories or [
                    self.workspace_root / "plugins",
                    Path("plugins")
                ],
                auto_discovery=True,
                discovery_interval=300
            )
            
            await self.plugin_registry.initialize(discovery_config)
            
            # Discover plugins
            discovery_result = await self.plugin_registry.discover_plugins(
                discovery_config.scan_directories
            )
            
            # Load and initialize discovered plugins
            loaded_plugins = []
            for plugin_name in discovery_result.get("discovered", []):
                try:
                    # Load plugin
                    load_result = await self.lifecycle_manager.load_plugin(plugin_name)
                    if load_result["success"]:
                        # Initialize plugin
                        init_result = await self.lifecycle_manager.initialize_plugin(
                            plugin_name, {
                                "workspace": self.workspace_root,
                                "tool_registry": self.tool_registry,
                                "permission_engine": None  # Would be actual permission engine
                            }
                        )
                        
                        if init_result["success"]:
                            loaded_plugins.append(plugin_name)
                            self.logger.info(f"Successfully loaded and initialized plugin: {plugin_name}")
                        else:
                            self.logger.error(f"Failed to initialize plugin {plugin_name}: {init_result.get('error')}")
                    else:
                        self.logger.error(f"Failed to load plugin {plugin_name}: {load_result.get('error')}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing plugin {plugin_name}: {e}")
            
            self.system_initialized = True
            
            return {
                "success": True,
                "discovered_plugins": discovery_result.get("discovered_count", 0),
                "loaded_plugins": len(loaded_plugins),
                "plugin_names": loaded_plugins,
                "system_components": {
                    "secure_adapter": "initialized",
                    "integration_manager": "initialized",
                    "execution_manager": "initialized",
                    "lifecycle_manager": "initialized",
                    "plugin_registry": "initialized",
                    "config_manager": "initialized",
                    "error_handler": "initialized",
                    "monitor": "initialized",
                    "test_framework": "initialized"
                }
            }
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            return {
                "success": False,
                "error": f"Initialization failed: {e}"
            }
    
    async def start_system(self) -> Dict[str, Any]:
        """Start the plugin system"""
        if not self.system_initialized:
            return {
                "success": False,
                "error": "System not initialized"
            }
        
        self.logger.info("Starting VoiceOS Plugin System...")
        self.system_running = True
        
        return {
            "success": True,
            "message": "Plugin system started successfully"
        }
    
    async def stop_system(self) -> Dict[str, Any]:
        """Stop the plugin system"""
        self.logger.info("Stopping VoiceOS Plugin System...")
        
        try:
            self.system_running = False
            
            # Unload all plugins
            unload_result = await self.lifecycle_manager.unload_all_plugins()
            
            # Stop component systems
            await self.monitor.stop_monitoring()
            await self.error_handler.stop_error_handling()
            await self.lifecycle_manager.stop_lifecycle_management()
            await self.plugin_registry.shutdown()
            
            return {
                "success": True,
                "unloaded_plugins": unload_result.get("total_unloaded", 0),
                "message": "Plugin system stopped successfully"
            }
            
        except Exception as e:
            self.logger.error(f"System shutdown failed: {e}")
            return {
                "success": False,
                "error": f"Shutdown failed: {e}"
            }
    
    async def execute_plugin_operation(self, plugin_name: str, operation: str,
                                    params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a plugin operation with full security and monitoring.
        
        Args:
            plugin_name: Name of plugin
            operation: Operation to execute
            params: Operation parameters
            
        Returns:
            Execution result
        """
        if not self.system_running:
            return {
                "success": False,
                "error": "Plugin system not running"
            }
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Execute through lifecycle manager (includes error handling)
            result = await self.lifecycle_manager.execute_plugin_operation(
                plugin_name, operation, params
            )
            
            # Record metrics
            execution_time = asyncio.get_event_loop().time() - start_time
            await self.monitor.record_operation(
                plugin_name, operation, execution_time, 
                result.get("success", False)
            )
            
            return result
            
        except Exception as e:
            # Handle error through error handler
            error_result = await self.error_handler.handle_plugin_error(
                plugin_name, e, {"operation": operation, "params": params}
            )
            
            # Record metrics
            execution_time = asyncio.get_event_loop().time() - start_time
            await self.monitor.record_operation(
                plugin_name, operation, execution_time, False
            )
            
            return {
                "success": False,
                "error": str(e),
                "error_handling": error_result
            }
    
    async def validate_plugin(self, plugin_path: Path) -> Dict[str, Any]:
        """
        Validate a plugin with comprehensive testing.
        
        Args:
            plugin_path: Path to plugin directory
            
        Returns:
            Validation result
        """
        self.logger.info(f"Validating plugin: {plugin_path}")
        
        try:
            # Run comprehensive validation
            validation_report = await self.test_framework.validate_plugin(plugin_path)
            
            return {
                "success": validation_report.overall_result.value == "passed",
                "validation_report": {
                    "plugin_name": validation_report.plugin_name,
                    "plugin_version": validation_report.plugin_version,
                    "overall_result": validation_report.overall_result.value,
                    "security_score": validation_report.security_score,
                    "performance_score": validation_report.performance_score,
                    "compatibility_score": validation_report.compatibility_score,
                    "total_tests": validation_report.total_tests,
                    "passed_tests": validation_report.passed_tests,
                    "failed_tests": validation_report.failed_tests,
                    "recommendations": validation_report.recommendations
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Validation failed: {e}"
            }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        if not self.system_initialized:
            return {
                "system_initialized": False,
                "system_running": False
            }
        
        try:
            # Get component statuses
            lifecycle_metrics = self.lifecycle_manager.get_lifecycle_metrics()
            registry_metrics = self.plugin_registry.get_registry_metrics()
            error_metrics = self.error_handler.get_metrics()
            system_metrics = await self.monitor.get_system_metrics()
            
            # Get plugin statuses
            plugin_statuses = self.lifecycle_manager.get_all_plugin_status()
            
            return {
                "system_initialized": True,
                "system_running": self.system_running,
                "components": {
                    "lifecycle": {
                        "total_plugins": lifecycle_metrics.total_plugins,
                        "active_plugins": lifecycle_metrics.active_plugins,
                        "error_plugins": lifecycle_metrics.error_plugins,
                        "total_executions": lifecycle_metrics.total_executions,
                        "total_errors": lifecycle_metrics.total_errors
                    },
                    "registry": {
                        "total_plugins": registry_metrics["total_plugins"],
                        "enabled_plugins": registry_metrics["enabled_plugins"],
                        "verified_plugins": registry_metrics["verified_plugins"],
                        "last_discovery_time": registry_metrics["last_discovery_time"]
                    },
                    "error_handling": {
                        "total_errors": error_metrics.total_errors,
                        "recovery_attempts": error_metrics.recovery_attempts,
                        "successful_recoveries": error_metrics.successful_recoveries,
                        "quarantined_plugins": error_metrics.quarantined_plugins
                    },
                    "monitoring": {
                        "total_plugins": system_metrics["total_plugins"],
                        "active_plugins": system_metrics["active_plugins"],
                        "total_operations": system_metrics["total_operations"],
                        "plugin_health_score": system_metrics["plugin_health_score"]
                    }
                },
                "plugins": plugin_statuses,
                "system_health": "healthy" if system_metrics["plugin_health_score"] > 80 else "degraded"
            }
            
        except Exception as e:
            return {
                "system_initialized": True,
                "system_running": self.system_running,
                "error": f"Status check failed: {e}"
            }
    
    async def get_plugin_details(self, plugin_name: str) -> Dict[str, Any]:
        """Get detailed information about a plugin"""
        try:
            # Get plugin status
            plugin_status = self.lifecycle_manager.get_plugin_status(plugin_name)
            if not plugin_status:
                return {
                    "success": False,
                    "error": f"Plugin not found: {plugin_name}"
                }
            
            # Get plugin metrics
            plugin_metrics = await self.monitor.get_plugin_metrics(plugin_name)
            
            # Get plugin configuration
            plugin_config = await self.config_manager.load_plugin_config(plugin_name)
            
            # Get error statistics
            error_stats = await self.error_handler.get_error_statistics(plugin_name)
            
            return {
                "success": True,
                "plugin_name": plugin_name,
                "status": plugin_status,
                "metrics": plugin_metrics,
                "configuration": plugin_config,
                "error_statistics": error_stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get plugin details: {e}"
            }
    
    async def configure_plugin(self, plugin_name: str, config_data: Dict[str, Any],
                             changed_by: str = "user") -> Dict[str, Any]:
        """Configure a plugin"""
        try:
            result = await self.config_manager.save_plugin_config(
                plugin_name, config_data, changed_by=changed_by
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Configuration failed: {e}"
            }
    
    async def enable_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Enable a plugin"""
        try:
            # Enable in registry
            registry_result = await self.plugin_registry.enable_plugin(plugin_name)
            
            # Resume if suspended
            lifecycle_result = await self.lifecycle_manager.resume_plugin(plugin_name)
            
            return {
                "success": registry_result["success"] and lifecycle_result["success"],
                "registry_result": registry_result,
                "lifecycle_result": lifecycle_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to enable plugin: {e}"
            }
    
    async def disable_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """Disable a plugin"""
        try:
            # Disable in registry
            registry_result = await self.plugin_registry.disable_plugin(plugin_name)
            
            # Suspend in lifecycle
            lifecycle_result = await self.lifecycle_manager.suspend_plugin(
                plugin_name, "Disabled by user"
            )
            
            return {
                "success": registry_result["success"] and lifecycle_result["success"],
                "registry_result": registry_result,
                "lifecycle_result": lifecycle_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to disable plugin: {e}"
            }


# Global plugin system instance
complete_plugin_system = None

def get_complete_plugin_system() -> VoiceOSCompletePluginSystem:
    """Get or create complete plugin system instance"""
    global complete_plugin_system
    if complete_plugin_system is None:
        complete_plugin_system = VoiceOSCompletePluginSystem(config.project_root / "workspace")
    return complete_plugin_system


# Example usage
async def demonstrate_complete_system():
    """Demonstrate the complete plugin system"""
    logger = logging.getLogger(__name__)
    logger.info("Demonstrating VoiceOS Complete Plugin System...")
    
    # Get the complete system
    system = get_complete_plugin_system()
    
    # Initialize system
    init_result = await system.initialize_system()
    logger.info(f"System initialization: {init_result}")
    
    if init_result["success"]:
        # Start system
        start_result = await system.start_system()
        logger.info(f"System start: {start_result}")
        
        if start_result["success"]:
            # Get system status
            status = await system.get_system_status()
            logger.info(f"System status: {status}")
            
            # Execute a plugin operation (example)
            if status["plugins"]:
                plugin_name = list(status["plugins"].keys())[0]
                operation_result = await system.execute_plugin_operation(
                    plugin_name, "example_operation", {"param": "value"}
                )
                logger.info(f"Operation result: {operation_result}")
            
            # Stop system
            stop_result = await system.stop_system()
            logger.info(f"System stop: {stop_result}")
    
    return init_result


if __name__ == "__main__":
    # Run demonstration
    asyncio.run(demonstrate_complete_system())
