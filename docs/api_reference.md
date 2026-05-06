# 📚 VoiceOS API Reference

This document provides comprehensive API documentation for all VoiceOS modules, tools, and components.

## 🏗️ Core API

### Configuration API

#### `core.config.Config`

```python
class Config:
    """Central configuration management for VoiceOS"""
    
    @property
    def project_root(self) -> Path:
        """Get the project root directory"""
        
    @property
    def workspace(self) -> Path:
        """Get the workspace directory"""
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        
    def load_from_file(self, config_path: Path) -> None:
        """Load configuration from YAML file"""
```

#### Event System API

```python
class Event:
    """Base event class for VoiceOS event system"""
    
    def __init__(self, event_type: str, data: Dict[str, Any]):
        """Initialize event with type and data"""
        
    @property
    def timestamp(self) -> datetime:
        """Get event timestamp"""
        
    @property
    def event_type(self) -> str:
        """Get event type"""
        
    @property
    def data(self) -> Dict[str, Any]:
        """Get event data"""

class EventBus:
    """Event bus for publishing and subscribing to events"""
    
    def subscribe(self, event_type: str, callback: Callable) -> str:
        """Subscribe to event type with callback"""
        
    def unsubscribe(self, subscription_id: str) -> None:
        """Unsubscribe from event"""
        
    def publish(self, event: Event) -> None:
        """Publish event to all subscribers"""
```

## 🛠️ Tools API

### File Tools API

#### `tools.file_tools.enhanced_file_manager.EnhancedFileManager`

```python
class EnhancedFileManager:
    """Safe file operations within workspace boundaries"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize file manager with workspace root"""
        
    @check_permission(PermissionLevel.LOW)
    def read_file(self, path: str) -> str:
        """Safely read file within workspace"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def write_file(self, path: str, content: str) -> str:
        """Safely write file within workspace"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def create_file(self, path: str) -> str:
        """Create empty file within workspace"""
        
    @check_permission(PermissionLevel.HIGH)
    def delete_file(self, path: str) -> str:
        """Delete file within workspace (requires high permission)"""
        
    @check_permission(PermissionLevel.LOW)
    def list_directory(self, path: str = ".") -> List[Dict[str, Any]]:
        """List directory contents within workspace"""
        
    @check_permission(PermissionLevel.LOW)
    def file_exists(self, path: str) -> bool:
        """Check if file exists within workspace"""
```

### Web Tools API

#### `tools.web_tools.browser_tool.BrowserTool`

```python
class BrowserTool:
    """Safe web browsing and scraping with security constraints"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize browser tool with workspace root"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def open_page(self, url: str) -> Dict[str, Any]:
        """Safely open web page and retrieve content"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def scrape_content(self, url: str, selectors: Optional[List[str]] = None) -> Dict[str, Any]:
        """Scrape content from web page with optional CSS selectors"""
        
    @check_permission(PermissionLevel.LOW)
    def search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Perform web search (using safe search endpoints)"""
        
    @check_permission(PermissionLevel.LOW)
    def get_page_info(self, url: str) -> Dict[str, Any]:
        """Get basic page information without full content"""
```

### Code Tools API

#### `tools.code_tools.code_executor.CodeExecutor`

```python
class CodeExecutor:
    """Safe code execution in sandboxed environment"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize code executor with workspace root"""
        
    @check_permission(PermissionLevel.HIGH)
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Execute code in sandboxed environment"""
        
    def _validate_code(self, code: str, language: str) -> str:
        """Validate code for security patterns"""
        
    def _validate_language(self, language: str) -> None:
        """Validate supported programming language"""
```

### Document Tools API

#### `tools.document_tools.document_processor.DocumentProcessor`

```python
class DocumentProcessor:
    """Safe document processing with validation and sandboxing"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize document processor with workspace root"""
        
    @check_permission(PermissionLevel.LOW)
    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from document"""
        
    @check_permission(PermissionLevel.LOW)
    def summarize_document(self, file_path: str, max_length: int = 500) -> Dict[str, Any]:
        """Generate document summary"""
        
    @check_permission(PermissionLevel.LOW)
    def search_in_document(self, file_path: str, query: str) -> Dict[str, Any]:
        """Search for text within document"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Analyze document structure and metadata"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def convert_document(self, file_path: str, output_format: str) -> Dict[str, Any]:
        """Convert document to different format"""
```

### Scheduler Tools API

#### `tools.scheduler_tools.task_scheduler.TaskScheduler`

```python
class TaskScheduler:
    """Safe task scheduling with validation and logging"""
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Initialize task scheduler with workspace root"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def schedule_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a new task"""
        
    @check_permission(PermissionLevel.LOW)
    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List scheduled tasks"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a scheduled task"""
        
    @check_permission(PermissionLevel.LOW)
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task"""
        
    @check_permission(PermissionLevel.MEDIUM)
    def reschedule_task(self, task_id: str, new_time: datetime) -> Dict[str, Any]:
        """Reschedule existing task"""
```

## 🔐 Permissions API

### Permission Engine API

#### `permissions.permission_engine.PermissionEngine`

```python
class PermissionEngine:
    """Permission validation and management system"""
    
    def __init__(self):
        """Initialize permission engine"""
        
    def check_tool_permission(self, required_level: PermissionLevel) -> bool:
        """Check if user has required permission level"""
        
    def set_user_permission_level(self, level: PermissionLevel) -> None:
        """Set current user permission level"""
        
    def get_user_permission_level(self) -> PermissionLevel:
        """Get current user permission level"""
        
    def request_permission(self, operation: str, level: PermissionLevel) -> bool:
        """Request permission from user"""
```

#### Permission Decorator

```python
def check_permission(level: PermissionLevel):
    """Decorator to enforce permission levels on methods"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check permission before execution
            if not permission_engine.check_tool_permission(level):
                raise PermissionError(f"Insufficient permissions for {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## 🤖 Agents API

### Core Agents API

#### `agents.core.planner.Planner`

```python
class Planner:
    """Task classification and execution planning"""
    
    def analyze_input(self, user_input: str) -> TaskPlan:
        """Analyze user input and create task plan"""
        
    def generate_plan(self, task_type: str, input_data: Dict[str, Any]) -> TaskPlan:
        """Generate execution plan for task"""
        
    def estimate_execution_time(self, plan: TaskPlan) -> float:
        """Estimate task execution time in seconds"""
```

#### `agents.core.router.Router`

```python
class Router:
    """Task routing and agent selection"""
    
    def route_task(self, task_plan: TaskPlan) -> Agent:
        """Route task to appropriate agent"""
        
    def select_agent(self, task_type: str, requirements: Dict[str, Any]) -> Agent:
        """Select best agent for task"""
        
    def balance_load(self, agents: List[Agent]) -> Agent:
        """Balance load across available agents"""
```

#### `agents.core.safety.Safety`

```python
class Safety:
    """Risk assessment and permission validation"""
    
    def assess_risk(self, task: Task) -> RiskLevel:
        """Assess risk level of task"""
        
    def validate_action(self, action: Action) -> bool:
        """Validate action for safety"""
        
    def check_permissions(self, user: User, action: Action) -> bool:
        """Check user permissions for action"""
```

### Autonomous Agent API

#### `agents.autonomous.agent_loop.AutonomousAgentLoop`

```python
class AutonomousAgentLoop:
    """Autonomous agent with iterative reasoning"""
    
    def __init__(self, goal: str, tools: List[Tool]):
        """Initialize autonomous agent with goal and tools"""
        
    async def execute(self) -> Result:
        """Execute autonomous agent loop"""
        
    def think_phase(self) -> Thought:
        """Analyze current state and plan next steps"""
        
    def decide_phase(self) -> Decision:
        """Select optimal action based on context"""
        
    def act_phase(self, decision: Decision) -> ActionResult:
        """Execute selected action"""
        
    def observe_phase(self, result: ActionResult) -> Observation:
        """Analyze results and update state"""
```

### Agent Tool Integration API

#### `agents.agent_tool_integration.AgentToolBridge`

```python
class AgentToolBridge:
    """Bridge between agents and VoiceOS tools"""
    
    def __init__(self, tool_registry: ToolRegistry = None):
        """Initialize tool bridge"""
        
    def get_available_tools_for_agent(self, agent_type: str = "general") -> List[str]:
        """Get list of available tools for specific agent type"""
        
    async def execute_tool_for_agent(self, agent_type: str, tool_name: str, 
                                   method_name: str = None, **kwargs) -> Dict[str, Any]:
        """Execute tool for agent with permission checking"""
        
    def get_tool_info_for_agent(self, agent_type: str, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool information for agent"""
```

#### `agents.agent_tool_integration.AgentToolManager`

```python
class AgentToolManager:
    """High-level manager for agent tool access"""
    
    def __init__(self):
        """Initialize agent tool manager"""
        
    async def execute_agent_task(self, agent_type: str, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task plan for a specific agent type"""
        
    def get_agent_capabilities(self, agent_type: str) -> Dict[str, Any]:
        """Get capabilities summary for agent type"""
```

## 🔧 Tool Registry API

### Tool Registry API

#### `tools.tool_registry.ToolRegistry`

```python
class ToolRegistry:
    """Central tool management and registration system"""
    
    def __init__(self):
        """Initialize tool registry"""
        
    def register_tool(self, tool_class: Type) -> bool:
        """Register tool with registry"""
        
    def get_tool(self, tool_name: str) -> Optional[ToolRegistration]:
        """Get tool registration by name"""
        
    def list_tools(self, category: Optional[ToolCategory] = None) -> List[str]:
        """List all registered tools"""
        
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute tool with parameters"""
        
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool information and metadata"""
```

#### Tool Metadata API

```python
@dataclass
class ToolMetadata:
    """Tool metadata and configuration"""
    name: str
    description: str
    category: ToolCategory
    version: str
    author: str
    dependencies: List[str]
    safety_level: str
    async_execution: bool
    timeout: float
    tags: List[str]

@dataclass
class ToolRegistration:
    """Tool registration information"""
    tool_class: Type
    metadata: ToolMetadata
    status: ToolStatus
    registration_time: datetime
    last_used: Optional[datetime]
    usage_count: int
```

## 📊 Monitoring API

### Metrics API

#### `core.metrics.MetricsCollector`

```python
class MetricsCollector:
    """System metrics collection and reporting"""
    
    def collect_execution_metrics(self) -> Dict[str, Any]:
        """Collect execution performance metrics"""
        
    def collect_resource_metrics(self) -> Dict[str, Any]:
        """Collect system resource usage metrics"""
        
    def collect_tool_metrics(self) -> Dict[str, Any]:
        """Collect tool usage metrics"""
        
    def get_health_status(self) -> HealthStatus:
        """Get overall system health status"""
```

### Logging API

#### `core.logger.VoiceOSLogger`

```python
class VoiceOSLogger:
    """Structured logging for VoiceOS operations"""
    
    def log_tool_execution(self, tool_name: str, method: str, result: Any, error: Optional[str] = None):
        """Log tool execution with structured data"""
        
    def log_agent_action(self, agent_type: str, action: str, context: Dict[str, Any]):
        """Log agent action with context"""
        
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        
    def get_logs(self, level: Optional[str] = None, limit: int = 100) -> List[LogEntry]:
        """Retrieve logs with optional filtering"""
```

## 🔌 Plugin API

### Plugin System API

#### `plugins.plugin_loader.PluginLoader`

```python
class PluginLoader:
    """Dynamic plugin discovery and loading"""
    
    def __init__(self, plugin_directory: Path):
        """Initialize plugin loader"""
        
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover available plugins"""
        
    def load_plugin(self, plugin_name: str) -> Plugin:
        """Load specific plugin"""
        
    def validate_plugin(self, plugin_path: Path) -> bool:
        """Validate plugin for security and compatibility"""
        
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload plugin"""
```

#### Plugin Interface

```python
class Plugin:
    """Base plugin interface"""
    
    @property
    def name(self) -> str:
        """Get plugin name"""
        
    @property
    def version(self) -> str:
        """Get plugin version"""
        
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration"""
        
    def get_tools(self) -> List[Tool]:
        """Get tools provided by plugin"""
        
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
```

## 🧠 Memory API

### Memory Management API

#### `memory.memory_manager.MemoryManager`

```python
class MemoryManager:
    """Memory storage and retrieval system"""
    
    def store_memory(self, key: str, value: Any, category: str = "general") -> None:
        """Store memory with key and category"""
        
    def retrieve_memory(self, key: str) -> Optional[Any]:
        """Retrieve memory by key"""
        
    def search_memories(self, query: str, category: Optional[str] = None) -> List[Memory]:
        """Search memories by query and category"""
        
    def get_recent_memories(self, limit: int = 10, category: Optional[str] = None) -> List[Memory]:
        """Get recent memories"""
        
    def cleanup_old_memories(self, max_age: timedelta) -> int:
        """Clean up old memories"""
```

## 🎵 Audio API

### Audio Processing API

#### `audio.microphone.Microphone`

```python
class Microphone:
    """Microphone input handling"""
    
    def __init__(self, device_id: Optional[int] = None):
        """Initialize microphone with device ID"""
        
    def start_recording(self) -> None:
        """Start recording audio"""
        
    def stop_recording(self) -> bytes:
        """Stop recording and return audio data"""
        
    def list_devices(self) -> List[Dict[str, Any]]:
        """List available audio devices"""
        
    def test_microphone(self) -> bool:
        """Test microphone functionality"""
```

#### `audio.streaming_stt.StreamingSTT`

```python
class StreamingSTT:
    """Streaming speech-to-text processing"""
    
    def __init__(self, model_name: str = "base"):
        """Initialize STT with model"""
        
    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[str]:
        """Transcribe audio stream to text"""
        
    def transcribe_file(self, audio_file: Path) -> str:
        """Transcribe audio file to text"""
```

#### `audio.tts_controller.TTSController`

```python
class TTSController:
    """Text-to-speech processing"""
    
    def __init__(self, model_name: str = "ljspeech"):
        """Initialize TTS with model"""
        
    def synthesize(self, text: str, output_file: Optional[Path] = None) -> bytes:
        """Synthesize text to speech"""
        
    async def stream_speak(self, text: str) -> AsyncIterator[bytes]:
        """Stream synthesized speech"""
```

## 🔍 LLM API

### LLM Integration API

#### `llm.llm_client.LLMClient`

```python
class LLMClient:
    """Large Language Model client interface"""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """Initialize LLM client"""
        
    async def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """Generate response from prompt"""
        
    async def generate_with_context(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> str:
        """Generate response with conversation context"""
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
```

#### `llm.conversation_engine.ConversationEngine`

```python
class ConversationEngine:
    """Conversation management and context"""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize conversation engine"""
        
    def add_message(self, role: str, content: str) -> None:
        """Add message to conversation"""
        
    def get_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get conversation context"""
        
    async def generate_response(self, user_input: str) -> str:
        """Generate response with context"""
        
    def clear_conversation(self) -> None:
        """Clear conversation history"""
```

## 📝 Usage Examples

### Basic Tool Usage

```python
from tools.file_tools.enhanced_file_manager import EnhancedFileManager
from permissions.permission_engine import PermissionLevel, permission_engine

# Initialize file manager
file_manager = EnhancedFileManager()

# Set permission level
permission_engine.set_user_permission_level(PermissionLevel.MEDIUM)

# Use file operations
content = file_manager.read_file("example.txt")
file_manager.write_file("output.txt", "Hello World")
```

### Agent Integration

```python
from agents.agent_tool_integration import AgentToolManager

# Initialize agent manager
agent_manager = AgentToolManager()

# Execute task
result = await agent_manager.execute_agent_task(
    agent_type="autonomous",
    task_plan={
        "steps": [
            {
                "tool": "enhanced_file_manager",
                "method": "write_file",
                "parameters": {"path": "test.txt", "content": "Hello"}
            }
        ]
    }
)
```

### Tool Registration

```python
from tools.voiceos_tools_integration import VoiceOSToolsIntegration
from tools.tool_registry import ToolRegistry

# Initialize integration
tool_registry = ToolRegistry()
integration = VoiceOSToolsIntegration(tool_registry)

# Register tools
registered_count = integration.register_voiceos_tools()
print(f"Registered {registered_count} tools")
```

---

## � Core Integration Systems API

### Plugin System API

#### Complete Plugin Integration

```python
from core.plugins.complete_plugin_integration import get_complete_plugin_system

# Get plugin system instance
plugin_system = get_complete_plugin_system()

# Enable a plugin
result = await plugin_system.enable_plugin("my_plugin")

# Disable a plugin
result = await plugin_system.disable_plugin("my_plugin")

# Get system status
status = await plugin_system.get_system_status()
```

#### Plugin Registry

```python
from core.plugins.plugin_registry import get_plugin_registry

# Get registry instance
registry = get_plugin_registry()

# Discover plugins
discovered = await registry.discover_plugins()

# Register plugin
result = await registry.register_plugin(plugin_path)

# Get registry state
state = registry.get_registry_state()
```

#### Plugin Lifecycle

```python
from core.plugins.plugin_lifecycle import get_lifecycle_manager

# Get lifecycle manager
lifecycle = get_lifecycle_manager()

# Load plugin
result = await lifecycle.load_plugin("my_plugin")

# Activate plugin
result = await lifecycle.activate_plugin("my_plugin")

# Suspend plugin
result = await lifecycle.suspend_plugin("my_plugin", "Maintenance")
```

### Helper System API

#### Secure Helper Integration

```python
from core.helpers.secure_helper_integration import get_secure_helper_adapter

# Get helper adapter
adapter = get_secure_helper_adapter()

# Register helper module
result = await adapter.register_helper_module("my_helpers", "/path/to/helpers")

# Get registered helpers
helpers = adapter.get_registered_helpers()

# Execute helper function
result = await adapter.execute_helper("my_helpers", "my_function", args, kwargs)
```

#### Helper Bridge Integration

```python
from core.helpers.helper_bridge_integration import get_helper_bridge_manager
from tools.tool_registry import ToolRegistry

# Get bridge manager
tool_registry = ToolRegistry()
bridge_manager = get_helper_bridge_manager(tool_registry)

# Create bridge
result = await bridge_manager.create_bridge(
    helper_name="my_helpers",
    function_name="my_function",
    voiceos_tool_name="my_tool",
    bridge_mode=BridgeMode.WRAPPED
)

# Execute bridge
result = await bridge_manager.execute_bridge("my_helpers.my_function", args, kwargs)
```

### Extension System API

#### Secure Extension Integration

```python
from core.extensions.secure_extension_integration import get_secure_extension_manager

# Get extension manager
manager = get_secure_extension_manager()

# Register extension
result = await manager.register_extension("my_extension", extension_path)

# Execute extension
result = await manager.execute_extension("my_extension", ExtensionPoint.BEFORE_TOOL_EXECUTION, context)

# Get registered extensions
extensions = manager.get_registered_extensions()
```

#### Extension Point System

```python
from core.extensions.extension_point_system import get_extension_point_system

# Get extension point system
system = get_extension_point_system()

# Register extension hook
system.register_hook(ExtensionPoint.BEFORE_TOOL_EXECUTION, my_hook_function, priority=HookPriority.HIGH)

# Execute extension point
result = await system.execute_extension_point(ExtensionPoint.BEFORE_TOOL_EXECUTION, context)

# Use decorators
@before_tool_execution
async def my_tool_hook(context):
    print("Before tool execution")
```

### Integration Framework API

#### Integration Patterns

```python
from core.integration.integration_patterns import get_integration_manager

# Get integration manager
manager = get_integration_manager(event_bus, tool_registry)

# Create integration contract
contract = IntegrationContract(
    interface_name="my_interface",
    required_methods=["execute", "validate"],
    security_policy=SecurityPolicy.RESTRICTED
)

# Register integration
result = await manager.register_integration("my_integration", contract)
```

#### Controlled Execution

```python
from core.integration.controlled_execution import get_controlled_execution_manager

# Get execution manager
manager = get_controlled_execution_manager()

# Execute with limits
result = await manager.execute_with_limits(
    target_function,
    args,
    kwargs,
    limits=ExecutionLimits(
        max_execution_time=30.0,
        max_memory_mb=512,
        max_cpu_percent=80
    )
)
```

### Monitoring System API

#### Performance Monitor

```python
from core.monitoring.performance_monitor import get_performance_monitor

# Get performance monitor
monitor = get_performance_monitor()

# Record metric
monitor.record_metric("operation_time", 1.5, {"operation": "tool_execution"})

# Get metrics
metrics = monitor.get_metrics()

# Get system health
health = monitor.get_system_health()
```

#### Error Recovery

```python
from core.monitoring.error_recovery import get_error_recovery

# Get error recovery
recovery = get_error_recovery()

# Handle error
result = await recovery.handle_error(error, context)

# Get error statistics
stats = recovery.get_error_statistics()
```

### Unified Dashboard API

```python
from core.system.unified_integration_dashboard import get_unified_integration_dashboard

# Get dashboard
dashboard = get_unified_integration_dashboard()

# Get system status
status = dashboard.get_system_status()

# Get system metrics
metrics = dashboard.get_system_metrics()

# Get available views
views = dashboard.get_available_views()
```

---

## �🔗 Related Documentation

- [Setup Guide](setup.md)
- [Architecture Overview](architecture.md)
- [Agent System](agents.md)
- [Usage Guide](usage.md)
- [VoiceOS Tools Integration](voiceos_tools_integration_guide.md)

---

**API documentation is continuously updated. Check for new features and changes regularly!**
