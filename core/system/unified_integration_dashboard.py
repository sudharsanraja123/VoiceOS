"""
VoiceOS Unified Integration Dashboard

This module provides a unified dashboard for managing plugins, helpers,
and extensions while maintaining VoiceOS security boundaries and architectural purity.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
from datetime import datetime

from core.config import config
from tools.tool_registry import ToolRegistry
from core.plugins.complete_plugin_integration import get_complete_plugin_system
from core.helpers.secure_helper_integration import get_secure_helper_adapter, HelperCategory
from core.extensions.secure_extension_integration import get_secure_extension_manager, ExtensionType
from core.helpers.helper_extension_discovery import get_helper_extension_discovery
from core.helpers.helper_bridge_integration import get_helper_bridge_manager
from core.extensions.extension_point_system import get_extension_point_system
from core.helpers.helper_extension_monitoring import get_helper_extension_monitor


class DashboardView(Enum):
    """Dashboard view types"""
    OVERVIEW = "overview"
    PLUGINS = "plugins"
    HELPERS = "helpers"
    EXTENSIONS = "extensions"
    BRIDGES = "bridges"
    MONITORING = "monitoring"
    SECURITY = "security"
    CONFIGURATION = "configuration"


class IntegrationStatus(Enum):
    """Integration status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class SystemOverview:
    """System overview data"""
    total_components: int
    active_components: int
    healthy_components: int
    warning_components: int
    critical_components: int
    offline_components: int
    total_operations: int
    total_errors: int
    system_health_score: float
    last_update: datetime


@dataclass
class ComponentSummary:
    """Component summary data"""
    component_type: str
    total_count: int
    active_count: int
    healthy_count: int
    warning_count: int
    critical_count: int
    offline_count: int
    recent_operations: int
    recent_errors: int
    average_response_time: float


class UnifiedIntegrationDashboard:
    """
    Unified dashboard for managing all VoiceOS integrations.
    
    This class provides comprehensive management while maintaining VoiceOS
    security boundaries and architectural purity.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger(__name__)
        
        # Tool registry
        self.tool_registry = ToolRegistry()
        
        # Integration systems
        self.plugin_system = get_complete_plugin_system()
        self.helper_adapter = get_secure_helper_adapter()
        self.extension_manager = get_secure_extension_manager()
        self.discovery_system = get_helper_extension_discovery()
        self.bridge_manager = get_helper_bridge_manager(self.tool_registry)
        self.extension_point_system = get_extension_point_system()
        self.monitor = get_helper_extension_monitor()
        
        # Dashboard state
        self.current_view = DashboardView.OVERVIEW
        self.last_update = datetime.now()
        
        # Cached data
        self._cached_overview: Optional[SystemOverview] = None
        self._cache_timeout = 30  # seconds
    
    async def initialize_dashboard(self) -> Dict[str, Any]:
        """Initialize the dashboard"""
        self.logger.info("Initializing Unified Integration Dashboard...")
        
        try:
            # Initialize all systems
            await self.discovery_system.start_discovery_service()
            await self.monitor.start_monitoring(self.tool_registry)
            
            # Perform initial discovery
            discovery_result = await self.discovery_system.discover_all()
            
            self.last_update = datetime.now()
            
            return {
                "success": True,
                "discovery_result": discovery_result,
                "dashboard_initialized": True,
                "last_update": self.last_update.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Dashboard initialization failed: {e}")
            return {
                "success": False,
                "error": f"Initialization failed: {e}"
            }
    
    async def get_dashboard_data(self, view: DashboardView = None, 
                               refresh: bool = False) -> Dict[str, Any]:
        """
        Get dashboard data for specific view.
        
        Args:
            view: Dashboard view to get data for
            refresh: Force refresh of cached data
            
        Returns:
            Dashboard data
        """
        if view is None:
            view = self.current_view
        
        # Check cache validity
        if not refresh and self._cached_overview and \
           (datetime.now() - self.last_update).total_seconds() < self._cache_timeout:
            if view == DashboardView.OVERVIEW:
                return {
                    "view": view.value,
                    "data": self._overview_to_dict(self._cached_overview),
                    "cached": True
                }
        
        # Get fresh data
        if view == DashboardView.OVERVIEW:
            data = await self._get_overview_data()
        elif view == DashboardView.PLUGINS:
            data = await self._get_plugins_data()
        elif view == DashboardView.HELPERS:
            data = await self._get_helpers_data()
        elif view == DashboardView.EXTENSIONS:
            data = await self._get_extensions_data()
        elif view == DashboardView.BRIDGES:
            data = await self._get_bridges_data()
        elif view == DashboardView.MONITORING:
            data = await self._get_monitoring_data()
        elif view == DashboardView.SECURITY:
            data = await self._get_security_data()
        elif view == DashboardView.CONFIGURATION:
            data = await self._get_configuration_data()
        else:
            data = {"error": f"Unknown view: {view.value}"}
        
        self.last_update = datetime.now()
        
        return {
            "view": view.value,
            "data": data,
            "cached": False,
            "last_update": self.last_update.isoformat()
        }
    
    async def _get_overview_data(self) -> Dict[str, Any]:
        """Get system overview data"""
        # Get component summaries
        plugin_summary = await self._get_component_summary("plugins")
        helper_summary = await self._get_component_summary("helpers")
        extension_summary = await self._get_component_summary("extensions")
        bridge_summary = await self._get_component_summary("bridges")
        
        # Calculate totals
        total_components = (plugin_summary.total_count + helper_summary.total_count + 
                          extension_summary.total_count + bridge_summary.total_count)
        active_components = (plugin_summary.active_count + helper_summary.active_count + 
                           extension_summary.active_count + bridge_summary.active_count)
        healthy_components = (plugin_summary.healthy_count + helper_summary.healthy_count + 
                            extension_summary.healthy_count + bridge_summary.healthy_count)
        warning_components = (plugin_summary.warning_count + helper_summary.warning_count + 
                            extension_summary.warning_count + bridge_summary.warning_count)
        critical_components = (plugin_summary.critical_count + helper_summary.critical_count + 
                             extension_summary.critical_count + bridge_summary.critical_count)
        offline_components = (plugin_summary.offline_count + helper_summary.offline_count + 
                            extension_summary.offline_count + bridge_summary.offline_count)
        
        total_operations = (plugin_summary.recent_operations + helper_summary.recent_operations + 
                          extension_summary.recent_operations + bridge_summary.recent_operations)
        total_errors = (plugin_summary.recent_errors + helper_summary.recent_errors + 
                       extension_summary.recent_errors + bridge_summary.recent_errors)
        
        # Calculate system health score
        system_health_score = self._calculate_system_health_score(
            total_components, healthy_components, warning_components, 
            critical_components, total_operations, total_errors
        )
        
        # Create overview
        overview = SystemOverview(
            total_components=total_components,
            active_components=active_components,
            healthy_components=healthy_components,
            warning_components=warning_components,
            critical_components=critical_components,
            offline_components=offline_components,
            total_operations=total_operations,
            total_errors=total_errors,
            system_health_score=system_health_score,
            last_update=self.last_update
        )
        
        self._cached_overview = overview
        
        return {
            "system_overview": self._overview_to_dict(overview),
            "component_summaries": {
                "plugins": self._component_summary_to_dict(plugin_summary),
                "helpers": self._component_summary_to_dict(helper_summary),
                "extensions": self._component_summary_to_dict(extension_summary),
                "bridges": self._component_summary_to_dict(bridge_summary)
            },
            "recent_activity": await self._get_recent_activity(),
            "system_alerts": await self._get_system_alerts()
        }
    
    async def _get_plugins_data(self) -> Dict[str, Any]:
        """Get plugins data"""
        # Get plugin system status
        plugin_status = await self.plugin_system.get_system_status()
        
        # Get plugin details
        plugin_details = {}
        for plugin_name in plugin_status.get("plugins", {}):
            details = await self.plugin_system.get_plugin_details(plugin_name)
            if details.get("success"):
                plugin_details[plugin_name] = details
        
        return {
            "system_status": plugin_status,
            "plugin_details": plugin_details,
            "plugin_operations": await self._get_plugin_operations(),
            "plugin_errors": await self._get_plugin_errors()
        }
    
    async def _get_helpers_data(self) -> Dict[str, Any]:
        """Get helpers data"""
        # Get registered helpers
        registered_helpers = self.helper_adapter.get_registered_helpers()
        
        # Get helper functions
        helper_functions = {}
        for helper in registered_helpers:
            functions = self.helper_adapter.get_helper_functions(helper["name"])
            helper_functions[helper["name"]] = functions
        
        # Get helper metrics
        helper_metrics = {}
        for helper in registered_helpers:
            metrics = await self.monitor.get_helper_metrics(helper["name"])
            if metrics:
                helper_metrics[helper["name"]] = metrics
        
        return {
            "registered_helpers": registered_helpers,
            "helper_functions": helper_functions,
            "helper_metrics": helper_metrics,
            "helper_categories": self._get_helper_categories()
        }
    
    async def _get_extensions_data(self) -> Dict[str, Any]:
        """Get extensions data"""
        # Get registered extensions
        registered_extensions = self.extension_manager.get_registered_extensions()
        
        # Get extension point status
        extension_point_status = self.extension_point_system.get_system_status()
        
        # Get extension metrics
        extension_metrics = {}
        for extension in registered_extensions:
            metrics = await self.monitor.get_extension_metrics(extension["name"])
            if metrics:
                extension_metrics[extension["name"]] = metrics
        
        return {
            "registered_extensions": registered_extensions,
            "extension_point_status": extension_point_status,
            "extension_metrics": extension_metrics,
            "extension_types": self._get_extension_types()
        }
    
    async def _get_bridges_data(self) -> Dict[str, Any]:
        """Get bridges data"""
        # Get bridge statistics
        bridge_statistics = self.bridge_manager.get_bridge_statistics()
        
        # Get bridge details
        bridges = self.bridge_manager.get_bridges()
        
        # Get bridge metrics
        bridge_metrics = {}
        for bridge in bridges:
            # This would get actual bridge metrics
            bridge_metrics[bridge["bridge_id"]] = {
                "execution_count": bridge_statistics.get("total_executions", 0),
                "success_rate": bridge_statistics.get("success_rate", 0)
            }
        
        return {
            "bridge_statistics": bridge_statistics,
            "bridges": bridges,
            "bridge_metrics": bridge_metrics,
            "bridge_modes": self._get_bridge_modes()
        }
    
    async def _get_monitoring_data(self) -> Dict[str, Any]:
        """Get monitoring data"""
        # Get system metrics
        system_metrics = await self.monitor.get_system_metrics()
        
        # Get recent alerts
        recent_alerts = await self._get_recent_alerts()
        
        # Get performance trends
        performance_trends = await self._get_performance_trends()
        
        return {
            "system_metrics": system_metrics,
            "recent_alerts": recent_alerts,
            "performance_trends": performance_trends,
            "resource_usage": await self._get_resource_usage()
        }
    
    async def _get_security_data(self) -> Dict[str, Any]:
        """Get security data"""
        # Get security violations
        security_violations = await self._get_security_violations()
        
        # Get security scores
        security_scores = await self._get_security_scores()
        
        # Get security policies
        security_policies = await self._get_security_policies()
        
        return {
            "security_violations": security_violations,
            "security_scores": security_scores,
            "security_policies": security_policies,
            "security_status": await self._get_security_status()
        }
    
    async def _get_configuration_data(self) -> Dict[str, Any]:
        """Get configuration data"""
        # Get system configuration
        system_config = await self._get_system_configuration()
        
        # Get component configurations
        component_configs = await self._get_component_configurations()
        
        # Get discovery configuration
        discovery_config = self.discovery_system.get_discovery_status()
        
        return {
            "system_configuration": system_config,
            "component_configurations": component_configs,
            "discovery_configuration": discovery_config,
            "configuration_history": await self._get_configuration_history()
        }
    
    async def execute_component_action(self, component_type: str, component_name: str,
                                    action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute action on a component.
        
        Args:
            component_type: Type of component (plugin, helper, extension, bridge)
            component_name: Name of component
            action: Action to execute
            parameters: Action parameters
            
        Returns:
            Action execution result
        """
        try:
            if component_type == "plugin":
                return await self._execute_plugin_action(component_name, action, parameters or {})
            elif component_type == "helper":
                return await self._execute_helper_action(component_name, action, parameters or {})
            elif component_type == "extension":
                return await self._execute_extension_action(component_name, action, parameters or {})
            elif component_type == "bridge":
                return await self._execute_bridge_action(component_name, action, parameters or {})
            else:
                return {
                    "success": False,
                    "error": f"Unknown component type: {component_type}"
                }
                
        except Exception as e:
            self.logger.error(f"Component action execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_plugin_action(self, plugin_name: str, action: str, 
                                   parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin action"""
        if action == "enable":
            return await self.plugin_system.enable_plugin(plugin_name)
        elif action == "disable":
            return await self.plugin_system.disable_plugin(plugin_name)
        elif action == "execute":
            operation = parameters.get("operation", "default_operation")
            params = parameters.get("params", {})
            return await self.plugin_system.execute_plugin_operation(plugin_name, operation, params)
        elif action == "configure":
            config_data = parameters.get("config", {})
            return await self.plugin_system.configure_plugin(plugin_name, config_data)
        else:
            return {
                "success": False,
                "error": f"Unknown plugin action: {action}"
            }
    
    async def _execute_helper_action(self, helper_name: str, action: str,
                                   parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute helper action"""
        if action == "execute":
            function_name = parameters.get("function", "default_function")
            params = parameters.get("params", {})
            return await self.helper_adapter.execute_helper_function(helper_name, function_name, params)
        else:
            return {
                "success": False,
                "error": f"Unknown helper action: {action}"
            }
    
    async def _execute_extension_action(self, extension_name: str, action: str,
                                      parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute extension action"""
        if action == "enable":
            return self.extension_manager.enable_extension(extension_name)
        elif action == "disable":
            return self.extension_manager.disable_extension(extension_name)
        elif action == "unload":
            return self.extension_manager.unload_extension(extension_name)
        else:
            return {
                "success": False,
                "error": f"Unknown extension action: {action}"
            }
    
    async def _execute_bridge_action(self, bridge_id: str, action: str,
                                   parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute bridge action"""
        if action == "enable":
            return self.bridge_manager.enable_bridge(bridge_id)
        elif action == "disable":
            return self.bridge_manager.disable_bridge(bridge_id)
        elif action == "remove":
            return self.bridge_manager.remove_bridge(bridge_id)
        elif action == "execute":
            params = parameters.get("params", {})
            return await self.bridge_manager.execute_bridge(bridge_id, params)
        else:
            return {
                "success": False,
                "error": f"Unknown bridge action: {action}"
            }
    
    async def _get_component_summary(self, component_type: str) -> ComponentSummary:
        """Get component summary"""
        if component_type == "plugins":
            status = await self.plugin_system.get_system_status()
            return ComponentSummary(
                component_type="plugins",
                total_count=status.get("components", {}).get("lifecycle", {}).get("total_plugins", 0),
                active_count=status.get("components", {}).get("lifecycle", {}).get("active_plugins", 0),
                healthy_count=status.get("components", {}).get("lifecycle", {}).get("active_plugins", 0),  # Simplified
                warning_count=0,
                critical_count=status.get("components", {}).get("lifecycle", {}).get("error_plugins", 0),
                offline_count=0,
                recent_operations=status.get("components", {}).get("lifecycle", {}).get("total_executions", 0),
                recent_errors=status.get("components", {}).get("lifecycle", {}).get("total_errors", 0),
                average_response_time=0.0
            )
        elif component_type == "helpers":
            helpers = self.helper_adapter.get_registered_helpers()
            return ComponentSummary(
                component_type="helpers",
                total_count=len(helpers),
                active_count=len(helpers),  # Simplified
                healthy_count=len(helpers),
                warning_count=0,
                critical_count=0,
                offline_count=0,
                recent_operations=0,
                recent_errors=0,
                average_response_time=0.0
            )
        elif component_type == "extensions":
            extensions = self.extension_manager.get_registered_extensions()
            return ComponentSummary(
                component_type="extensions",
                total_count=len(extensions),
                active_count=len([e for e in extensions if e["enabled"]]),
                healthy_count=len([e for e in extensions if e["enabled"]]),
                warning_count=0,
                critical_count=0,
                offline_count=len([e for e in extensions if not e["enabled"]]),
                recent_operations=0,
                recent_errors=0,
                average_response_time=0.0
            )
        elif component_type == "bridges":
            bridges = self.bridge_manager.get_bridges()
            return ComponentSummary(
                component_type="bridges",
                total_count=len(bridges),
                active_count=len([b for b in bridges if b["enabled"]]),
                healthy_count=len([b for b in bridges if b["enabled"]]),
                warning_count=0,
                critical_count=0,
                offline_count=len([b for b in bridges if not b["enabled"]]),
                recent_operations=0,
                recent_errors=0,
                average_response_time=0.0
            )
        else:
            return ComponentSummary(
                component_type=component_type,
                total_count=0, active_count=0, healthy_count=0,
                warning_count=0, critical_count=0, offline_count=0,
                recent_operations=0, recent_errors=0, average_response_time=0.0
            )
    
    def _calculate_system_health_score(self, total_components: int, healthy_components: int,
                                     warning_components: int, critical_components: int,
                                     total_operations: int, total_errors: int) -> float:
        """Calculate system health score"""
        if total_components == 0:
            return 100.0
        
        # Component health (70% weight)
        component_health = (healthy_components / total_components) * 70
        
        # Error rate (30% weight)
        error_rate = (total_errors / total_operations * 100) if total_operations > 0 else 0
        error_health = max(0, (100 - error_rate) * 0.3)
        
        return component_health + error_health
    
    def _overview_to_dict(self, overview: SystemOverview) -> Dict[str, Any]:
        """Convert overview to dict"""
        return {
            "total_components": overview.total_components,
            "active_components": overview.active_components,
            "healthy_components": overview.healthy_components,
            "warning_components": overview.warning_components,
            "critical_components": overview.critical_components,
            "offline_components": overview.offline_components,
            "total_operations": overview.total_operations,
            "total_errors": overview.total_errors,
            "system_health_score": overview.system_health_score,
            "last_update": overview.last_update.isoformat()
        }
    
    def _component_summary_to_dict(self, summary: ComponentSummary) -> Dict[str, Any]:
        """Convert component summary to dict"""
        return {
            "component_type": summary.component_type,
            "total_count": summary.total_count,
            "active_count": summary.active_count,
            "healthy_count": summary.healthy_count,
            "warning_count": summary.warning_count,
            "critical_count": summary.critical_count,
            "offline_count": summary.offline_count,
            "recent_operations": summary.recent_operations,
            "recent_errors": summary.recent_errors,
            "average_response_time": summary.average_response_time
        }
    
    # Placeholder methods for additional functionality
    async def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent activity"""
        return []
    
    async def _get_system_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts"""
        return []
    
    async def _get_plugin_operations(self) -> List[Dict[str, Any]]:
        """Get plugin operations"""
        return []
    
    async def _get_plugin_errors(self) -> List[Dict[str, Any]]:
        """Get plugin errors"""
        return []
    
    def _get_helper_categories(self) -> List[str]:
        """Get helper categories"""
        return [category.value for category in HelperCategory]
    
    def _get_extension_types(self) -> List[str]:
        """Get extension types"""
        return [ext_type.value for ext_type in ExtensionType]
    
    def _get_bridge_modes(self) -> List[str]:
        """Get bridge modes"""
        return ["direct", "wrapped", "sandboxed", "proxy"]
    
    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return []
    
    async def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends"""
        return {}
    
    async def _get_resource_usage(self) -> Dict[str, Any]:
        """Get resource usage"""
        return {}
    
    async def _get_security_violations(self) -> List[Dict[str, Any]]:
        """Get security violations"""
        return []
    
    async def _get_security_scores(self) -> Dict[str, Any]:
        """Get security scores"""
        return {}
    
    async def _get_security_policies(self) -> Dict[str, Any]:
        """Get security policies"""
        return {}
    
    async def _get_security_status(self) -> Dict[str, Any]:
        """Get security status"""
        return {}
    
    async def _get_system_configuration(self) -> Dict[str, Any]:
        """Get system configuration"""
        return {}
    
    async def _get_component_configurations(self) -> Dict[str, Any]:
        """Get component configurations"""
        return {}
    
    async def _get_configuration_history(self) -> List[Dict[str, Any]]:
        """Get configuration history"""
        return []


# Global dashboard instance
unified_integration_dashboard = None

def get_unified_integration_dashboard() -> UnifiedIntegrationDashboard:
    """Get or create unified integration dashboard instance"""
    global unified_integration_dashboard
    if unified_integration_dashboard is None:
        unified_integration_dashboard = UnifiedIntegrationDashboard(config.project_root / "workspace")
    return unified_integration_dashboard
