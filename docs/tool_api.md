# 🛠️ VoiceOS Tools API Reference

This document provides detailed API documentation for all VoiceOS native tools, their methods, and usage patterns.

## Overview

VoiceOS provides a comprehensive suite of native tools that enable secure, sandboxed operations across multiple domains including file management, web browsing, code execution, document processing, and task scheduling.

## Tool Categories

### 1. File Operations Tools
- **Enhanced File Manager**: Secure file operations within workspace boundaries
- **Location**: `tools.file_tools.enhanced_file_manager`

### 2. Web Tools
- **Browser Tool**: Safe web browsing and content scraping
- **Location**: `tools.web_tools.browser_tool`

### 3. Code Tools
- **Code Executor**: Sandboxed code execution with resource limits
- **Location**: `tools.code_tools.code_executor`

### 4. Document Tools
- **Document Processor**: Document analysis and processing
- **Location**: `tools.document_tools.document_processor`

### 5. Scheduler Tools
- **Task Scheduler**: Task scheduling and management
- **Location**: `tools.scheduler_tools.task_scheduler`

## Enhanced File Manager API

### Class Definition

```python
class EnhancedFileManager:
    """Safe file operations within workspace boundaries"""
```

### Constructor

```python
def __init__(self, workspace_root: Optional[str] = None):
    """
    Initialize file manager with workspace root directory.
    
    Args:
        workspace_root (Optional[str]): Path to workspace directory.
            Defaults to project_root/workspace if not specified.
    """
```

### Methods

#### read_file
```python
@check_permission(PermissionLevel.LOW)
def read_file(self, path: str) -> str:
    """
    Safely read file within workspace.
    
    Args:
        path (str): Relative path to file within workspace
        
    Returns:
        str: File contents as UTF-8 text
        
    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If user lacks read permissions
        ValueError: If path is outside workspace
        
    Example:
        >>> file_manager = EnhancedFileManager()
        >>> content = file_manager.read_file("data.txt")
        >>> print(content)
        "Hello World"
    """
```

#### write_file
```python
@check_permission(PermissionLevel.MEDIUM)
def write_file(self, path: str, content: str) -> str:
    """
    Safely write file within workspace.
    
    Args:
        path (str): Relative path to file within workspace
        content (str): Content to write to file
        
    Returns:
        str: Success message with file path
        
    Raises:
        PermissionError: If user lacks write permissions
        ValueError: If path is outside workspace
        
    Example:
        >>> file_manager = EnhancedFileManager()
        >>> result = file_manager.write_file("output.txt", "Hello World")
        >>> print(result)
        "File written to output.txt"
    """
```

#### create_file
```python
@check_permission(PermissionLevel.MEDIUM)
def create_file(self, path: str) -> str:
    """
    Create empty file within workspace.
    
    Args:
        path (str): Relative path to file within workspace
        
    Returns:
        str: Success message with file path
        
    Example:
        >>> file_manager = EnhancedFileManager()
        >>> result = file_manager.create_file("new_file.txt")
        >>> print(result)
        "File created at new_file.txt"
    """
```

#### delete_file
```python
@check_permission(PermissionLevel.HIGH)
def delete_file(self, path: str) -> str:
    """
    Delete file within workspace (requires high permission).
    
    Args:
        path (str): Relative path to file within workspace
        
    Returns:
        str: Success message with file path
        
    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If user lacks delete permissions
        
    Example:
        >>> file_manager = EnhancedFileManager()
        >>> result = file_manager.delete_file("old_file.txt")
        >>> print(result)
        "File deleted: old_file.txt"
    """
```

#### list_directory
```python
@check_permission(PermissionLevel.LOW)
def list_directory(self, path: str = ".") -> List[Dict[str, Any]]:
    """
    List directory contents within workspace.
    
    Args:
        path (str): Relative path to directory within workspace.
            Defaults to workspace root.
            
    Returns:
        List[Dict[str, Any]]: List of directory items with metadata
        
    Example:
        >>> file_manager = EnhancedFileManager()
        >>> items = file_manager.list_directory()
        >>> for item in items:
        ...     print(f"{item['name']} ({item['type']})")
        "data.txt (file)"
        "logs/ (directory)"
    """
```

#### file_exists
```python
@check_permission(PermissionLevel.LOW)
def file_exists(self, path: str) -> bool:
    """
    Check if file exists within workspace.
    
    Args:
        path (str): Relative path to file within workspace
        
    Returns:
        bool: True if file exists, False otherwise
        
    Example:
        >>> file_manager = EnhancedFileManager()
        >>> exists = file_manager.file_exists("data.txt")
        >>> print(exists)
        True
    """
```

## Browser Tool API

### Class Definition

```python
class BrowserTool:
    """Safe web browsing and scraping with security constraints"""
```

### Constructor

```python
def __init__(self, workspace_root: Optional[str] = None):
    """
    Initialize browser tool with workspace root directory.
    
    Args:
        workspace_root (Optional[str]): Path to workspace directory.
            Defaults to project_root/workspace if not specified.
    """
```

### Methods

#### open_page
```python
@check_permission(PermissionLevel.MEDIUM)
def open_page(self, url: str) -> Dict[str, Any]:
    """
    Safely open web page and retrieve content.
    
    Args:
        url (str): URL of the web page to open
        
    Returns:
        Dict[str, Any]: Page content including status code, content, and headers
        
    Raises:
        ValueError: If URL is invalid or blocked
        PermissionError: If user lacks web access permissions
        
    Example:
        >>> browser = BrowserTool()
        >>> result = browser.open_page("https://example.com")
        >>> print(f"Status: {result['status_code']}")
        "Status: 200"
    """
```

#### scrape_content
```python
@check_permission(PermissionLevel.MEDIUM)
def scrape_content(self, url: str, selectors: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Scrape content from web page with optional CSS selectors.
    
    Args:
        url (str): URL of the web page to scrape
        selectors (Optional[List[str]]): CSS selectors for content filtering
        
    Returns:
        Dict[str, Any]: Scraped content with metadata
        
    Example:
        >>> browser = BrowserTool()
        >>> result = browser.scrape_content(
        ...     "https://example.com", 
        ...     selectors=[".content", ".title"]
        ... )
        >>> print(f"Content length: {len(result['content'])}")
        "Content length: 1024"
    """
```

#### search_web
```python
@check_permission(PermissionLevel.LOW)
def search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Perform web search (using safe search endpoints).
    
    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: Search results with titles, URLs, and snippets
        
    Example:
        >>> browser = BrowserTool()
        >>> results = browser.search_web("Python tutorials")
        >>> for result in results[:3]:
        ...     print(f"Title: {result['title']}")
        "Title: Python Tutorial for Beginners"
        "Title: Advanced Python Programming"
        "Title: Python Best Practices"
    """
```

#### get_page_info
```python
@check_permission(PermissionLevel.LOW)
def get_page_info(self, url: str) -> Dict[str, Any]:
    """
    Get basic page information without full content.
    
    Args:
        url (str): URL of the web page
        
    Returns:
        Dict[str, Any]: Page information including status and headers
        
    Example:
        >>> browser = BrowserTool()
        >>> info = browser.get_page_info("https://example.com")
        >>> print(f"Accessible: {info['accessible']}")
        "Accessible: True"
    """
```

## Code Executor API

### Class Definition

```python
class CodeExecutor:
    """Safe code execution in sandboxed environment"""
```

### Constructor

```python
def __init__(self, workspace_root: Optional[str] = None):
    """
    Initialize code executor with workspace root directory.
    
    Args:
        workspace_root (Optional[str]): Path to workspace directory.
            Defaults to project_root/workspace if not specified.
    """
```

### Methods

#### execute_code
```python
@check_permission(PermissionLevel.HIGH)
def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
    """
    Execute code in sandboxed environment.
    
    Args:
        code (str): Code to execute
        language (str): Programming language (python, bash, javascript)
        
    Returns:
        Dict[str, Any]: Execution result including output and error information
        
    Raises:
        ValueError: If code contains dangerous patterns
        PermissionError: If user lacks code execution permissions
        
    Example:
        >>> executor = CodeExecutor()
        >>> result = executor.execute_code("print('Hello World')", "python")
        >>> print(result['output'])
        "Hello World"
    """
```

## Document Processor API

### Class Definition

```python
class DocumentProcessor:
    """Safe document processing with validation and sandboxing"""
```

### Constructor

```python
def __init__(self, workspace_root: Optional[str] = None):
    """
    Initialize document processor with workspace root directory.
    
    Args:
        workspace_root (Optional[str]): Path to workspace directory.
            Defaults to project_root/workspace if not specified.
    """
```

### Methods

#### extract_text
```python
@check_permission(PermissionLevel.LOW)
def extract_text(self, file_path: str) -> Dict[str, Any]:
    """
    Extract text from document.
    
    Args:
        file_path (str): Path to document file
        
    Returns:
        Dict[str, Any]: Extracted text with metadata
        
    Example:
        >>> processor = DocumentProcessor()
        >>> result = processor.extract_text("document.pdf")
        >>> print(f"Text length: {len(result['text'])}")
        "Text length: 2048"
    """
```

#### summarize_document
```python
@check_permission(PermissionLevel.LOW)
def summarize_document(self, file_path: str, max_length: int = 500) -> Dict[str, Any]:
    """
    Generate document summary.
    
    Args:
        file_path (str): Path to document file
        max_length (int): Maximum summary length
        
    Returns:
        Dict[str, Any]: Document summary with metadata
        
    Example:
        >>> processor = DocumentProcessor()
        >>> result = processor.summarize_document("report.pdf")
        >>> print(result['summary'])
        "This report covers quarterly financial performance..."
    """
```

#### search_in_document
```python
@check_permission(PermissionLevel.LOW)
def search_in_document(self, file_path: str, query: str) -> Dict[str, Any]:
    """
    Search for text within document.
    
    Args:
        file_path (str): Path to document file
        query (str): Search query
        
    Returns:
        Dict[str, Any]: Search results with match locations
        
    Example:
        >>> processor = DocumentProcessor()
        >>> result = processor.search_in_document("doc.pdf", "Python")
        >>> print(f"Found {result['total_matches']} matches")
        "Found 5 matches"
    """
```

#### analyze_document
```python
@check_permission(PermissionLevel.MEDIUM)
def analyze_document(self, file_path: str) -> Dict[str, Any]:
    """
    Analyze document structure and metadata.
    
    Args:
        file_path (str): Path to document file
        
    Returns:
        Dict[str, Any]: Document analysis results
        
    Example:
        >>> processor = DocumentProcessor()
        >>> result = processor.analyze_document("data.pdf")
        >>> print(f"Word count: {result['statistics']['word_count']}")
        "Word count: 1250"
    """
```

#### convert_document
```python
@check_permission(PermissionLevel.MEDIUM)
def convert_document(self, file_path: str, output_format: str) -> Dict[str, Any]:
    """
    Convert document to different format.
    
    Args:
        file_path (str): Path to document file
        output_format (str): Target format (txt, md, json)
        
    Returns:
        Dict[str, Any]: Conversion result with output path
        
    Example:
        >>> processor = DocumentProcessor()
        >>> result = processor.convert_document("doc.pdf", "txt")
        >>> print(result['message'])
        "Successfully converted to txt"
    """
```

## Task Scheduler API

### Class Definition

```python
class TaskScheduler:
    """Safe task scheduling with validation and logging"""
```

### Constructor

```python
def __init__(self, workspace_root: Optional[str] = None):
    """
    Initialize task scheduler with workspace root directory.
    
    Args:
        workspace_root (Optional[str]): Path to workspace directory.
            Defaults to project_root/workspace if not specified.
    """
```

### Methods

#### schedule_task
```python
@check_permission(PermissionLevel.MEDIUM)
def schedule_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Schedule a new task.
    
    Args:
        task_data (Dict[str, Any]): Task configuration including name, type, and scheduled_time
        
    Returns:
        Dict[str, Any]: Task scheduling result with task ID
        
    Example:
        >>> from datetime import datetime, timedelta
        >>> scheduler = TaskScheduler()
        >>> future_time = datetime.now() + timedelta(hours=1)
        >>> task_data = {
        ...     "name": "backup_task",
        ...     "task_type": "file_operation",
        ...     "scheduled_time": future_time.isoformat(),
        ...     "parameters": {"path": "backup"}
        ... }
        >>> result = scheduler.schedule_task(task_data)
        >>> print(f"Task ID: {result['task_id']}")
        "Task ID: task_1234567890"
    """
```

#### list_tasks
```python
@check_permission(PermissionLevel.LOW)
def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List scheduled tasks.
    
    Args:
        status (Optional[str]): Filter by task status (scheduled, running, completed, cancelled)
        
    Returns:
        List[Dict[str, Any]]: List of tasks with metadata
        
    Example:
        >>> scheduler = TaskScheduler()
        >>> tasks = scheduler.list_tasks("scheduled")
        >>> for task in tasks:
        ...     print(f"{task['name']} - {task['status']}")
        "backup_task - scheduled"
    """
```

#### cancel_task
```python
@check_permission(PermissionLevel.MEDIUM)
def cancel_task(self, task_id: str) -> Dict[str, Any]:
    """
    Cancel a scheduled task.
    
    Args:
        task_id (str): ID of task to cancel
        
    Returns:
        Dict[str, Any]: Cancellation result
        
    Example:
        >>> scheduler = TaskScheduler()
        >>> result = scheduler.cancel_task("task_1234567890")
        >>> print(result['message'])
        "Task cancelled successfully"
    """
```

#### get_task_status
```python
@check_permission(PermissionLevel.LOW)
def get_task_status(self, task_id: str) -> Dict[str, Any]:
    """
    Get status of a specific task.
    
    Args:
        task_id (str): ID of task
        
    Returns:
        Dict[str, Any]: Task status information
        
    Example:
        >>> scheduler = TaskScheduler()
        >>> status = scheduler.get_task_status("task_1234567890")
        >>> print(f"Status: {status['status']}")
        "Status: scheduled"
    """
```

#### reschedule_task
```python
@check_permission(PermissionLevel.MEDIUM)
def reschedule_task(self, task_id: str, new_time: datetime) -> Dict[str, Any]:
    """
    Reschedule existing task.
    
    Args:
        task_id (str): ID of task to reschedule
        new_time (datetime): New scheduled time
        
    Returns:
        Dict[str, Any]: Rescheduling result
        
    Example:
        >>> from datetime import datetime, timedelta
        >>> scheduler = TaskScheduler()
        >>> new_time = datetime.now() + timedelta(hours=2)
        >>> result = scheduler.reschedule_task("task_1234567890", new_time)
        >>> print(result['message'])
        "Task rescheduled successfully"
    """
```

## Tool Registration and Integration

### Tool Registry Integration

All tools are automatically registered with the VoiceOS Tool Registry through the `VoiceOSToolsIntegration` class:

```python
from tools.voiceos_tools_integration import initialize_voiceos_tools_integration
from tools.tool_registry import ToolRegistry

# Initialize tool registry
tool_registry = ToolRegistry()

# Register all VoiceOS tools
integration = initialize_voiceos_tools_integration(tool_registry)
registered_count = integration.register_voiceos_tools()
```

### Permission Levels

Tools use a hierarchical permission system:

- **LOW**: Safe read operations (file_exists, list_directory, get_page_info, search_web)
- **MEDIUM**: File creation and modification (write_file, create_file, open_page, scrape_content)
- **HIGH**: System operations (delete_file, execute_code)

### Error Handling

All tools implement comprehensive error handling:

```python
try:
    result = tool.method(param1, param2)
except PermissionError as e:
    print(f"Permission denied: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Logging

All tool operations are logged for security and audit purposes:

```python
# Logs are stored in workspace/logs/
# File operations: workspace/logs/file_operations.log
# Web operations: workspace/logs/browser_operations.log
# Code execution: workspace/logs/code_execution.log
# Document processing: workspace/logs/document_operations.log
# Task scheduling: workspace/logs/scheduler_operations.log
```

## Usage Examples

### File Operations Workflow

```python
from tools.file_tools.enhanced_file_manager import enhanced_file_manager

# Write configuration file
config_content = """
database_url = "sqlite:///data.db"
max_connections = 10
"""
result = enhanced_file_manager.write_file("config.ini", config_content)

# Read configuration back
content = enhanced_file_manager.read_file("config.ini")
print(content)

# List files in workspace
files = enhanced_file_manager.list_directory()
print(f"Found {len(files)} files")
```

### Web Research Workflow

```python
from tools.web_tools.browser_tool import browser_tool

# Search for information
results = browser_tool.search_web("Python async programming", max_results=5)

# Get detailed content from top result
if results:
    top_result = results[0]
    content = browser_tool.scrape_content(top_result['url'])
    print(f"Content length: {len(content['content'])} characters")
```

### Code Execution Workflow

```python
from tools.code_tools.code_executor import code_executor

# Execute Python code
code = """
import json
data = {"name": "VoiceOS", "version": "1.0"}
print(json.dumps(data, indent=2))
"""
result = code_executor.execute_code(code, "python")
print(result['output'])
```

### Document Analysis Workflow

```python
from tools.document_tools.document_processor import document_processor

# Analyze document
analysis = document_processor.analyze_document("report.pdf")
print(f"Word count: {analysis['statistics']['word_count']}")

# Generate summary
summary = document_processor.summarize_document("report.pdf", max_length=200)
print(f"Summary: {summary['summary']}")
```

### Task Scheduling Workflow

```python
from tools.scheduler_tools.task_scheduler import task_scheduler
from datetime import datetime, timedelta

# Schedule recurring task
future_time = datetime.now() + timedelta(hours=1)
task_data = {
    "name": "daily_backup",
    "task_type": "file_operation",
    "scheduled_time": future_time.isoformat(),
    "parameters": {"source": "data", "destination": "backup"}
}

result = task_scheduler.schedule_task(task_data)
print(f"Task scheduled with ID: {result['task_id']}")

# Check task status
status = task_scheduler.get_task_status(result['task_id'])
print(f"Task status: {status['status']}")
```

---

**Tool API documentation is continuously updated. Check for new features and changes regularly!**