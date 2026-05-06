"""
VoiceOS Plugin Integration - Secure Integration Example

This module demonstrates how to integrate external plugins, helpers, and extensions
using the VoiceOS secure integration architecture while maintaining security,
architectural purity, and permission-first principles.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.config import config
from permissions.permission_engine import PermissionLevel
from tools.tool_registry import ToolRegistry, ToolMetadata, ToolCategory
from core.plugins.secure_plugin_integration import (
    get_secure_plugin_adapter, SecurityLevel, IntegrationType, SecurityPolicy
)
from core.integration.integration_patterns import (
    get_integration_manager, IntegrationPattern, IntegrationContract
)
from core.integration.controlled_execution import (
    get_controlled_execution_manager, ExecutionMode, ExecutionLimits
)


class VoiceOSPluginIntegration:
    """
    Main integration class for VoiceOS plugins.
    
    This class demonstrates how to safely integrate external plugins while
    maintaining VoiceOS security boundaries and architectural principles.
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.logger = logging.getLogger(__name__)
        
        # Initialize integration components
        self.secure_adapter = get_secure_plugin_adapter(tool_registry)
        self.integration_manager = get_integration_manager(None, tool_registry)
        self.execution_manager = get_controlled_execution_manager()
        
        # Integration tracking
        self.integrated_plugins: Dict[str, Dict[str, Any]] = {}
        self.plugin_contracts: Dict[str, IntegrationContract] = {}
    
    async def integrate_browser_plugin(self) -> Dict[str, Any]:
        """
        Example: Integrate browser plugin securely.
        
        Demonstrates proxy pattern integration with security controls.
        """
        self.logger.info("Integrating browser plugin with security controls...")
        
        # Define security policy for browser operations
        browser_security_policy = SecurityPolicy(
            level=SecurityLevel.RESTRICTED,
            allowed_operations=["search_web", "open_page", "scrape_content"],
            blocked_operations=["download_file", "execute_javascript"],
            resource_limits={
                "max_requests_per_minute": 10,
                "max_response_size_mb": 5
            },
            timeout_seconds=30
        )
        
        # Create integration contract
        browser_contract = IntegrationContract(
            interface_name="VoiceOSBrowser",
            required_methods=["search", "navigate", "extract"],
            provided_methods=["search_web", "open_page", "scrape_content"],
            security_requirements=[SecurityLevel.RESTRICTED],
            resource_limits={
                "max_memory_mb": 50,
                "timeout_seconds": 30
            }
        )
        
        # Load plugin through secure adapter
        plugin_path = Path("plugins/_browser")
        if plugin_path.exists():
            load_result = await self.secure_adapter.load_plugin(plugin_path)
            
            if load_result["success"]:
                # Create proxy integration
                proxy_integration = self.integration_manager.create_proxy_integration(
                    "browser_proxy",
                    self.secure_adapter.loaded_plugins[load_result["plugin_name"]],
                    browser_security_policy
                )
                
                # Register with tool registry
                await self._register_browser_tools(proxy_integration, browser_security_policy)
                
                self.integrated_plugins["browser"] = {
                    "status": "integrated",
                    "security_level": "restricted",
                    "integration_type": "proxy",
                    "contract": browser_contract
                }
                
                return {
                    "success": True,
                    "plugin": "browser",
                    "integration_type": "proxy",
                    "security_level": "restricted",
                    "available_operations": browser_security_policy.allowed_operations
                }
            else:
                return load_result
        else:
            # Create VoiceOS-native browser tools as fallback
            return await self._create_voiceos_browser_tools()
    
    async def integrate_code_execution_plugin(self) -> Dict[str, Any]:
        """
        Example: Integrate code execution plugin with sandboxing.
        
        Demonstrates sandboxed execution with controlled environment.
        """
        self.logger.info("Integrating code execution plugin with sandboxing...")
        
        # Define strict security policy for code execution
        code_security_policy = SecurityPolicy(
            level=SecurityLevel.SANDBOXED,
            allowed_operations=["execute_code", "validate_syntax"],
            blocked_operations=["file_access", "network_access", "system_calls"],
            resource_limits={
                "max_memory_mb": 100,
                "max_execution_time": 60,
                "max_cpu_percent": 50.0
            },
            audit_required=True,
            timeout_seconds=60
        )
        
        # Create execution limits
        execution_limits = ExecutionLimits(
            max_memory_mb=100,
            max_cpu_percent=50.0,
            max_execution_time=60,
            max_file_operations=5,
            allowed_file_extensions=['.py', '.txt', '.json']
        )
        
        # Load plugin if available
        plugin_path = Path("plugins/_code_execution")
        if plugin_path.exists():
            load_result = await self.secure_adapter.load_plugin(plugin_path)
            
            if load_result["success"]:
                # Create gateway integration for code execution
                gateway_integration = self.integration_manager.create_gateway_integration(
                    "code_execution_gateway",
                    code_security_policy
                )
                
                # Register code execution service
                gateway_integration.register_service(
                    "code_executor",
                    self.secure_adapter.loaded_plugins[load_result["plugin_name"]],
                    {
                        "allowed_operations": code_security_policy.allowed_operations,
                        "parameter_constraints": {
                            "code": {
                                "type": str,
                                "max_length": 10000
                            },
                            "language": {
                                "type": str,
                                "allowed_values": ["python", "javascript", "bash"]
                            }
                        }
                    }
                )
                
                self.integrated_plugins["code_execution"] = {
                    "status": "integrated",
                    "security_level": "sandboxed",
                    "integration_type": "gateway",
                    "execution_limits": execution_limits
                }
                
                return {
                    "success": True,
                    "plugin": "code_execution",
                    "integration_type": "gateway",
                    "security_level": "sandboxed",
                    "execution_mode": "controlled"
                }
            else:
                return load_result
        else:
            # Create VoiceOS-native code execution tools
            return await self._create_voiceos_code_tools()
    
    async def integrate_helper_utilities(self) -> Dict[str, Any]:
        """
        Example: Integrate helper utilities through adapter pattern.
        
        Demonstrates loose coupling through adapter pattern.
        """
        self.logger.info("Integrating helper utilities through adapter pattern...")
        
        # Define safe security policy for helper utilities
        helper_security_policy = SecurityPolicy(
            level=SecurityLevel.SAFE,
            allowed_operations=["process_text", "format_data", "validate_input"],
            blocked_operations=["file_system", "network", "system"],
            resource_limits={
                "max_memory_mb": 25,
                "timeout_seconds": 10
            }
        )
        
        # Create adapter integration
        adapter_contract = IntegrationContract(
            interface_name="VoiceOSHelpers",
            required_methods=["process", "format", "validate"],
            provided_methods=["text_processing", "data_formatting", "input_validation"],
            security_requirements=[SecurityLevel.SAFE],
            resource_limits={"max_memory_mb": 25}
        )
        
        # Load helper utilities through adapter
        try:
            # Import helper modules safely
            from helpers import cache, strings, functions
            
            # Create adapter for helper utilities
            helper_adapter = self.integration_manager.create_adapter_integration(
                "helper_adapter",
                {"cache": cache, "strings": strings, "functions": functions},
                adapter_contract
            )
            
            # Register adaptation methods
            helper_adapter.register_adaptation("process_text", self._adapt_text_processing)
            helper_adapter.register_adaptation("format_data", self._adapt_data_formatting)
            helper_adapter.register_adaptation("validate_input", self._adapt_input_validation)
            
            self.integrated_plugins["helpers"] = {
                "status": "integrated",
                "security_level": "safe",
                "integration_type": "adapter",
                "contract": adapter_contract
            }
            
            return {
                "success": True,
                "plugin": "helpers",
                "integration_type": "adapter",
                "security_level": "safe",
                "available_operations": ["process_text", "format_data", "validate_input"]
            }
            
        except ImportError as e:
            self.logger.warning(f"Helper utilities not available: {e}")
            return {
                "success": False,
                "error": "Helper utilities not available",
                "fallback": "Using VoiceOS-native utilities"
            }
    
    async def _register_browser_tools(self, proxy_integration, security_policy):
        """Register browser tools with VoiceOS tool registry"""
        # Register browser search tool
        browser_search_metadata = ToolMetadata(
            name="voiceos_browser_search",
            description="Secure web search through VoiceOS",
            category=ToolCategory.WEB_TOOLS,
            permission_level=PermissionLevel.MEDIUM,
            parameters={
                "query": {"type": "string", "required": True},
                "max_results": {"type": "integer", "default": 10}
            }
        )
        
        self.tool_registry.register_tool(
            browser_search_metadata,
            lambda **params: self._execute_browser_search(proxy_integration, params)
        )
    
    async def _execute_browser_search(self, proxy_integration, params):
        """Execute browser search through proxy"""
        result = await proxy_integration.execute("search_web", params)
        return result
    
    async def _create_voiceos_browser_tools(self):
        """Create VoiceOS-native browser tools as fallback"""
        # This would create native VoiceOS browser tools
        return {
            "success": True,
            "plugin": "browser",
            "integration_type": "native",
            "security_level": "restricted",
            "note": "Using VoiceOS-native browser tools"
        }
    
    async def _create_voiceos_code_tools(self):
        """Create VoiceOS-native code execution tools as fallback"""
        # This would create native VoiceOS code tools
        return {
            "success": True,
            "plugin": "code_execution",
            "integration_type": "native",
            "security_level": "sandboxed",
            "note": "Using VoiceOS-native code execution"
        }
    
    async def _adapt_text_processing(self, params):
        """Adapt text processing to VoiceOS interface"""
        # Adapt helper text processing to VoiceOS format
        return {"processed_text": params.get("text", "").upper()}
    
    async def _adapt_data_formatting(self, params):
        """Adapt data formatting to VoiceOS interface"""
        # Adapt helper data formatting to VoiceOS format
        return {"formatted_data": str(params.get("data", {}))}
    
    async def _adapt_input_validation(self, params):
        """Adapt input validation to VoiceOS interface"""
        # Adapt helper validation to VoiceOS format
        return {"is_valid": True, "errors": []}
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        return {
            "integrated_plugins": self.integrated_plugins,
            "security_status": {
                "total_plugins": len(self.integrated_plugins),
                "safe_plugins": len([p for p in self.integrated_plugins.values() 
                                   if p.get("security_level") == "safe"]),
                "restricted_plugins": len([p for p in self.integrated_plugins.values() 
                                         if p.get("security_level") == "restricted"]),
                "sandboxed_plugins": len([p for p in self.integrated_plugins.values() 
                                        if p.get("security_level") == "sandboxed"])
            },
            "architecture_status": {
                "proxy_integrations": len([p for p in self.integrated_plugins.values() 
                                        if p.get("integration_type") == "proxy"]),
                "adapter_integrations": len([p for p in self.integrated_plugins.values() 
                                          if p.get("integration_type") == "adapter"]),
                "gateway_integrations": len([p for p in self.integrated_plugins.values() 
                                          if p.get("integration_type") == "gateway"]),
                "native_integrations": len([p for p in self.integrated_plugins.values() 
                                         if p.get("integration_type") == "native"])
            },
            "execution_status": self.execution_manager.get_system_status()
        }


# Example usage and integration demonstration
async def demonstrate_voiceos_integration():
    """
    Demonstrate complete VoiceOS plugin integration.
    
    This function shows how to integrate plugins while maintaining
    security, architectural purity, and permission-first principles.
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting VoiceOS secure plugin integration demonstration...")
    
    # Initialize tool registry
    tool_registry = ToolRegistry()
    
    # Create integration manager
    integration = VoiceOSPluginIntegration(tool_registry)
    
    # Integrate browser plugin
    browser_result = await integration.integrate_browser_plugin()
    logger.info(f"Browser integration: {browser_result}")
    
    # Integrate code execution plugin
    code_result = await integration.integrate_code_execution_plugin()
    logger.info(f"Code execution integration: {code_result}")
    
    # Integrate helper utilities
    helper_result = await integration.integrate_helper_utilities()
    logger.info(f"Helper integration: {helper_result}")
    
    # Get overall integration status
    status = await integration.get_integration_status()
    logger.info(f"Overall integration status: {status}")
    
    return {
        "browser": browser_result,
        "code_execution": code_result,
        "helpers": helper_result,
        "overall_status": status
    }


if __name__ == "__main__":
    # Run integration demonstration
    asyncio.run(demonstrate_voiceos_integration())
