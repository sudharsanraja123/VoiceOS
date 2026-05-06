# VoiceOS Tools Integration Guide

## Overview

This guide documents the native VoiceOS tools integration, maintaining security boundaries while leveraging built-in VoiceOS capabilities.

## Architecture

### Integration Layers

```
VoiceOS Agents
    ↓
Agent Tool Bridge
    ↓
Tool Registry
    ↓
VoiceOS Tools Integration
    ↓
Native VoiceOS Tools
    ↓
VoiceOS Core Services
```

### Safety Boundaries

- **Workspace Isolation**: All operations confined to workspace directory
- **Permission Validation**: Multi-level permission system (LOW/MEDIUM/HIGH)
- **Input Sanitization**: All inputs validated before execution
- **Resource Limits**: Timeouts, memory limits, content size restrictions
- **Audit Logging**: All operations logged for security monitoring

## Native VoiceOS Tools

### 1. Enhanced File Manager
- **Location**: `tools/file_tools/enhanced_file_manager.py`
- **Capabilities**: Safe file operations within workspace
- **Permission Levels**:
  - LOW: read_file, list_directory, file_exists
  - MEDIUM: write_file, create_file
  - HIGH: delete_file

### 2. Browser Tool
- **Location**: `tools/web_tools/browser_tool.py`
- **Capabilities**: Safe web browsing and scraping
- **Security Features**:
  - URL validation (only http/https)
  - Blocked domains (localhost, 127.0.0.1)
  - Content size limits
  - Timeout restrictions

### 3. Code Executor
- **Location**: `tools/code_tools/code_executor.py`
- **Capabilities**: Sandboxed code execution
- **Security Features**:
  - Workspace-only execution
  - Resource limits (CPU/memory)
  - Dangerous pattern detection
  - Isolated sandbox environments

### 4. Document Processor
- **Location**: `tools/document_tools/document_processor.py`
- **Capabilities**: Document analysis and processing
- **Security Features**:
  - File type validation
  - Size limits
  - Content truncation
  - Workspace restriction

### 5. Task Scheduler
- **Location**: `tools/scheduler_tools/task_scheduler.py`
- **Capabilities**: Task scheduling and management
- **Security Features**:
  - Task validation
  - Time range restrictions
  - Parameter sanitization

## Permission System

### Permission Levels

```python
class PermissionLevel(Enum):
    LOW = "low"      # Safe read operations
    MEDIUM = "medium"  # File creation, web access
    HIGH = "high"      # System operations, deletion
```

### Permission Enforcement

1. **Decorator-based**: `@check_permission(PermissionLevel.HIGH)`
2. **Runtime validation**: Permission checks before execution
3. **Agent-specific**: Different agents have different permission levels
4. **Audit trail**: All permission checks logged

## Agent Integration

### Agent Types and Permissions

| Agent Type | Default Permission | Allowed Categories | Max Tools |
|------------|-------------------|-------------------|-----------|
| Autonomous | HIGH | All categories | 5 |
| Researcher | MEDIUM | web_tools, analysis | 3 |
| Developer | HIGH | system_tools, file_operations | 4 |
| Analyst | MEDIUM | analysis, web_tools | 3 |
| General | MEDIUM | file_operations, web_tools | 2 |

### Tool Access Pattern

```python
# Agents access tools through the bridge
result = await agent_tool_manager.execute_agent_task(
    agent_type="autonomous",
    task_plan={
        "steps": [
            {
                "tool": "enhanced_file_manager",
                "method": "write_file",
                "parameters": {"path": "output.txt", "content": "data"}
            }
        ]
    }
)
```

## Plugin System

### Plugin Loader
- **Location**: `plugins/plugin_loader.py`
- **Features**:
  - Dynamic plugin discovery
  - Configuration validation
  - Security scanning
  - Dependency management

### Plugin Structure
```
plugins/
├── plugin_name/
│   ├── plugin.yaml          # Plugin metadata
│   ├── main.py             # Plugin implementation
│   └── tests/              # Plugin tests
```

### Plugin Configuration
```yaml
name: "example_plugin"
version: "1.0.0"
description: "Example plugin"
author: "VoiceOS Team"
permission_level: "medium"
entry_point: "main.py"
dependencies: []
enabled: true
```

## Safety Validation

### Input Validation
- Path traversal prevention
- URL validation
- Code pattern detection
- Parameter type checking

### Resource Limits
- Execution timeouts
- Memory limits
- File size restrictions
- Content length limits

### Workspace Isolation
- All operations confined to workspace
- No access to system files
- Temporary sandbox creation
- Automatic cleanup

## Usage Examples

### Basic File Operations
```python
from tools.file_tools.enhanced_file_manager import enhanced_file_manager

# Write file (requires MEDIUM permission)
result = enhanced_file_manager.write_file("test.txt", "Hello World")

# Read file (requires LOW permission)
content = enhanced_file_manager.read_file("test.txt")
```

### Web Scraping
```python
from tools.web_tools.browser_tool import browser_tool

# Scrape web page (requires MEDIUM permission)
result = browser_tool.scrape_content(
    url="https://example.com",
    selectors=[".content"]
)
```

### Code Execution
```python
from tools.code_tools.code_executor import code_executor

# Execute Python code (requires HIGH permission)
result = code_executor.execute_code(
    code="print('Hello from sandbox')",
    language="python"
)
```

### Agent Task Execution
```python
from agents.agent_tool_integration import agent_tool_manager

# Execute task as autonomous agent
result = await agent_tool_manager.execute_agent_task(
    agent_type="autonomous",
    task_plan={
        "steps": [
            {
                "tool": "browser_tool",
                "method": "search_web",
                "parameters": {"query": "Python tutorials"}
            },
            {
                "tool": "enhanced_file_manager",
                "method": "write_file",
                "parameters": {"path": "results.txt", "content": "search results"}
            }
        ]
    }
)
```

## Testing

### Running Tests
```bash
python tests/test_voiceos_tools_integration.py
```

### Test Coverage
- Safety validation tests
- Permission enforcement tests
- Workspace isolation tests
- Integration functionality tests

## Monitoring and Logging

### Log Locations
- File operations: `workspace/logs/file_operations.log`
- Browser operations: `workspace/logs/browser_operations.log`
- Code execution: `workspace/logs/code_execution.log`
- Document processing: `workspace/logs/document_operations.log`
- Task scheduling: `workspace/logs/scheduler_operations.log`
- Plugin operations: `workspace/logs/plugin_operations.log`

### Log Format
```json
{
    "timestamp": "2024-01-01T12:00:00",
    "operation": "read_file",
    "path": "test.txt",
    "result": "success",
    "error": null
}
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Check user permission level
   - Verify tool permission requirements
   - Review agent configuration

2. **Path Access Denied**
   - Ensure path is within workspace
   - Check path traversal attempts
   - Verify workspace permissions

3. **Tool Not Found**
   - Check tool registration
   - Verify plugin loading
   - Review integration status

### Debug Commands
```python
# Check integration status
from tools.voiceos_tools_integration import VoiceOSToolsIntegration
integration = VoiceOSToolsIntegration(tool_registry)
status = integration.get_integration_status()

# Check agent capabilities
from agents.agent_tool_integration import agent_tool_manager
capabilities = agent_tool_manager.get_agent_capabilities("autonomous")

# Check permission levels
from permissions.permission_engine import permission_engine
permission_engine.set_user_permission_level(PermissionLevel.HIGH)
```

## Best Practices

### Security
1. Always validate inputs before processing
2. Use the principle of least privilege
3. Log all operations for audit trails
4. Regularly review permission settings

### Performance
1. Use appropriate timeouts for operations
2. Limit content sizes to prevent memory issues
3. Clean up temporary resources
4. Monitor execution times

### Maintenance
1. Keep plugin configurations updated
2. Regular security scans of plugins
3. Test integration after updates
4. Monitor log files for issues

## Future Enhancements

### Planned Features
- Advanced plugin management
- Dynamic permission adjustment
- Enhanced monitoring dashboard
- Automated security scanning
- Performance optimization

### Extension Points
- Custom tool wrappers
- Additional permission levels
- New agent types
- Enhanced logging formats

## Conclusion

The VoiceOS tools integration provides a secure, modular way to leverage native VoiceOS capabilities while maintaining strict security boundaries. The layered architecture ensures that all operations are validated, logged, and executed within safe parameters.

For questions or issues, refer to the test suite and log files for detailed information about integration behavior.
