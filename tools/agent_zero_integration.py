"""
Agent Zero Integration - Bridge between VoiceOS tool registry and Agent Zero components
Safely integrates imported Agent Zero tools with VoiceOS architecture
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from core.config import config
from permissions.permission_engine import PermissionLevel
from tools.tool_registry import ToolRegistry, ToolMetadata, ToolCategory, ToolStatus

# Import our wrapped Agent Zero tools
from tools.file_tools.enhanced_file_manager import enhanced_file_manager
from tools.web_tools.browser_tool import browser_tool
from tools.code_tools.code_executor import code_executor
from tools.document_tools.document_processor import document_processor
from tools.scheduler_tools.task_scheduler import task_scheduler

logger = logging.getLogger(__name__)


class AgentZeroIntegration:
    """
    Integration layer that registers Agent Zero tools with VoiceOS tool registry
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
        self.logger = logging.getLogger(__name__)
        
        # Tool definitions with metadata
        self.agent_zero_tools = {
            "enhanced_file_manager": {
                "instance": enhanced_file_manager,
                "metadata": ToolMetadata(
                    name="enhanced_file_manager",
                    description="Safe file operations within workspace boundaries using Agent Zero capabilities",
                    category=ToolCategory.FILE_OPERATIONS,
                    version="1.0.0",
                    author="VoiceOS Agent Zero Integration",
                    dependencies=[],
                    safety_level="medium",
                    async_execution=False,
                    timeout=30.0,
                    tags=["file", "workspace", "agent_zero"]
                ),
                "methods": {
                    "read_file": PermissionLevel.LOW,
                    "write_file": PermissionLevel.MEDIUM,
                    "create_file": PermissionLevel.MEDIUM,
                    "delete_file": PermissionLevel.HIGH,
                    "list_directory": PermissionLevel.LOW,
                    "file_exists": PermissionLevel.LOW
                }
            },
            "browser_tool": {
                "instance": browser_tool,
                "metadata": ToolMetadata(
                    name="browser_tool",
                    description="Safe web browsing and scraping with URL validation and content limits",
                    category=ToolCategory.WEB_TOOLS,
                    version="1.0.0",
                    author="VoiceOS Agent Zero Integration",
                    dependencies=[],
                    safety_level="medium",
                    async_execution=False,
                    timeout=30.0,
                    tags=["web", "browser", "scraping", "agent_zero"]
                ),
                "methods": {
                    "open_page": PermissionLevel.MEDIUM,
                    "scrape_content": PermissionLevel.MEDIUM,
                    "search_web": PermissionLevel.LOW,
                    "get_page_info": PermissionLevel.LOW
                }
            },
            "code_executor": {
                "instance": code_executor,
                "metadata": ToolMetadata(
                    name="code_executor",
                    description="Safe code execution in sandboxed environment with resource limits",
                    category=ToolCategory.SYSTEM_TOOLS,
                    version="1.0.0",
                    author="VoiceOS Agent Zero Integration",
                    dependencies=[],
                    safety_level="high",
                    async_execution=False,
                    timeout=60.0,
                    tags=["code", "execution", "sandbox", "agent_zero"]
                ),
                "methods": {
                    "execute_code": PermissionLevel.HIGH
                }
            },
            "document_processor": {
                "instance": document_processor,
                "metadata": ToolMetadata(
                    name="document_processor",
                    description="Document processing and analysis with file validation",
                    category=ToolCategory.ANALYSIS,
                    version="1.0.0",
                    author="VoiceOS Agent Zero Integration",
                    dependencies=[],
                    safety_level="low",
                    async_execution=False,
                    timeout=45.0,
                    tags=["document", "processing", "analysis", "agent_zero"]
                ),
                "methods": {
                    "extract_text": PermissionLevel.LOW,
                    "summarize_document": PermissionLevel.LOW,
                    "search_in_document": PermissionLevel.LOW,
                    "analyze_document": PermissionLevel.MEDIUM,
                    "convert_document": PermissionLevel.MEDIUM
                }
            },
            "task_scheduler": {
                "instance": task_scheduler,
                "metadata": ToolMetadata(
                    name="task_scheduler",
                    description="Task scheduling with validation and permission checks",
                    category=ToolCategory.SYSTEM_TOOLS,
                    version="1.0.0",
                    author="VoiceOS Agent Zero Integration",
                    dependencies=[],
                    safety_level="medium",
                    async_execution=False,
                    timeout=30.0,
                    tags=["scheduler", "tasks", "automation", "agent_zero"]
                ),
                "methods": {
                    "schedule_task": PermissionLevel.MEDIUM,
                    "list_tasks": PermissionLevel.LOW,
                    "cancel_task": PermissionLevel.MEDIUM,
                    "get_task_status": PermissionLevel.LOW,
                    "reschedule_task": PermissionLevel.MEDIUM
                }
            }
        }
    
    def register_agent_zero_tools(self) -> int:
        """Register all Agent Zero tools with the tool registry"""
        registered_count = 0
        
        for tool_name, tool_config in self.agent_zero_tools.items():
            try:
                # Create wrapper class for the tool
                wrapper_class = self._create_tool_wrapper(tool_name, tool_config)
                
                # Register with tool registry
                success = self.tool_registry.register_tool(wrapper_class)
                
                if success:
                    registered_count += 1
                    self.logger.info(f"Registered Agent Zero tool: {tool_name}")
                else:
                    self.logger.error(f"Failed to register Agent Zero tool: {tool_name}")
                    
            except Exception as e:
                self.logger.error(f"Error registering Agent Zero tool {tool_name}: {e}")
        
        self.logger.info(f"Successfully registered {registered_count} out of {len(self.agent_zero_tools)} Agent Zero tools")
        return registered_count
    
    def _create_tool_wrapper(self, tool_name: str, tool_config: Dict[str, Any]):
        """Create a wrapper class for Agent Zero tool integration"""
        
        class AgentZeroToolWrapper:
            TOOL_METADATA = tool_config["metadata"]
            
            def __init__(self):
                self.tool_instance = tool_config["instance"]
                self.tool_name = tool_name
                self.methods = tool_config["methods"]
                self.logger = logging.getLogger(__name__)
            
            def execute(self, method_name: str = None, **kwargs) -> Any:
                """
                Execute tool method with permission validation
                """
                try:
                    # Default method if not specified
                    if not method_name:
                        method_name = list(self.methods.keys())[0]
                    
                    # Check if method exists
                    if method_name not in self.methods:
                        raise ValueError(f"Method {method_name} not available in {tool_name}")
                    
                    # Check method exists on instance
                    if not hasattr(self.tool_instance, method_name):
                        raise ValueError(f"Method {method_name} not implemented on {tool_name}")
                    
                    # Get permission level for method
                    required_permission = self.methods[method_name]
                    
                    # Execute method (permission checking is handled by decorators on the methods)
                    method = getattr(self.tool_instance, method_name)
                    result = method(**kwargs)
                    
                    self.logger.info(f"Executed {tool_name}.{method_name} successfully")
                    return result
                    
                except Exception as e:
                    self.logger.error(f"Failed to execute {tool_name}.{method_name}: {e}")
                    raise
        
        return AgentZeroToolWrapper
    
    def get_tool_methods(self, tool_name: str) -> List[str]:
        """Get available methods for a specific tool"""
        if tool_name in self.agent_zero_tools:
            return list(self.agent_zero_tools[tool_name]["methods"].keys())
        return []
    
    def get_tool_permissions(self, tool_name: str) -> Dict[str, PermissionLevel]:
        """Get permission levels for all methods of a specific tool"""
        if tool_name in self.agent_zero_tools:
            return self.agent_zero_tools[tool_name]["methods"].copy()
        return {}
    
    def validate_tool_access(self, tool_name: str, method_name: str, user_permission: PermissionLevel) -> bool:
        """Validate if user has permission to access tool method"""
        if tool_name not in self.agent_zero_tools:
            return False
        
        if method_name not in self.agent_zero_tools[tool_name]["methods"]:
            return False
        
        required_permission = self.agent_zero_tools[tool_name]["methods"][method_name]
        
        # Permission hierarchy: LOW < MEDIUM < HIGH
        permission_hierarchy = {
            PermissionLevel.LOW: 0,
            PermissionLevel.MEDIUM: 1,
            PermissionLevel.HIGH: 2
        }
        
        user_level = permission_hierarchy.get(user_permission, 0)
        required_level = permission_hierarchy.get(required_permission, 0)
        
        return user_level >= required_level
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status and statistics"""
        registered_tools = []
        for tool_name in self.agent_zero_tools.keys():
            if self.tool_registry.get_tool(tool_name):
                registered_tools.append(tool_name)
        
        return {
            "total_agent_zero_tools": len(self.agent_zero_tools),
            "registered_tools": len(registered_tools),
            "unregistered_tools": len(self.agent_zero_tools) - len(registered_tools),
            "registered_tool_names": registered_tools,
            "unregistered_tool_names": [name for name in self.agent_zero_tools.keys() if name not in registered_tools]
        }


# Initialize integration
def initialize_agent_zero_integration(tool_registry: ToolRegistry) -> AgentZeroIntegration:
    """Initialize Agent Zero integration with tool registry"""
    integration = AgentZeroIntegration(tool_registry)
    registered_count = integration.register_agent_zero_tools()
    
    logger.info(f"Agent Zero integration initialized with {registered_count} tools registered")
    return integration
