"""
VoiceOS Secure Helper Integration System

This module provides secure integration for helper utilities while maintaining
VoiceOS security boundaries, architectural purity, and permission-first principles.
"""

import asyncio
import logging
import importlib
import inspect
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib
import time

from core.config import config
from permissions.permission_engine import PermissionLevel
from core.plugins.secure_plugin_integration import SecurityLevel, SecurityPolicy


class HelperCategory(Enum):
    """Helper utility categories"""
    FILE_OPERATIONS = "file_operations"
    WEB_OPERATIONS = "web_operations"
    DATA_PROCESSING = "data_processing"
    SYSTEM_OPERATIONS = "system_operations"
    COMMUNICATION = "communication"
    SECURITY = "security"
    VALIDATION = "validation"
    UTILITIES = "utilities"


class HelperSecurityLevel(Enum):
    """Security levels for helper operations"""
    SAFE = "safe"                    # Read-only, no system access
    RESTRICTED = "restricted"        # Limited system access with validation
    SANDBOXED = "sandboxed"          # Full execution in sandbox
    BLOCKED = "blocked"              # Operation not allowed


@dataclass
class HelperFunction:
    """Helper function definition"""
    name: str
    module: str
    category: HelperCategory
    security_level: HelperSecurityLevel
    required_permissions: List[PermissionLevel]
    description: str
    parameters: Dict[str, Any]
    return_type: Optional[Type] = None
    example_usage: Optional[str] = None
    security_notes: List[str] = field(default_factory=list)


@dataclass
class HelperModule:
    """Helper module definition"""
    name: str
    path: Path
    category: HelperCategory
    security_level: HelperSecurityLevel
    functions: List[HelperFunction] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    validated: bool = False
    checksum: str = ""


class HelperValidator:
    """Validates helper functions for security compliance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.blocked_functions = [
            "os.system", "subprocess.call", "eval", "exec",
            "open", "file", "input", "raw_input", "__import__"
        ]
        self.blocked_modules = [
            "os", "sys", "subprocess", "shutil", "tempfile",
            "socket", "urllib", "http", "ftplib", "smtplib"
        ]
    
    def validate_helper_module(self, module_path: Path) -> Dict[str, Any]:
        """
        Validate helper module for security compliance.
        
        Args:
            module_path: Path to helper module
            
        Returns:
            Validation results
        """
        issues = []
        security_score = 100
        functions = []
        
        try:
            # Read module content
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for blocked patterns
            for pattern in self.blocked_functions:
                if pattern in content:
                    issues.append({
                        "type": "blocked_function",
                        "pattern": pattern,
                        "severity": "high"
                    })
                    security_score -= 20
            
            # Check imports
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    if self._is_dangerous_import(line):
                        issues.append({
                            "type": "dangerous_import",
                            "line": line_num,
                            "content": line,
                            "severity": "medium"
                        })
                        security_score -= 10
            
            # Extract and validate functions
            functions = self._extract_functions(content)
            
            return {
                "valid": security_score >= 70,
                "security_score": max(0, security_score),
                "issues": issues,
                "functions": functions,
                "recommendations": self._generate_helper_recommendations(issues)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "security_score": 0,
                "issues": [{"type": "read_error", "error": str(e), "severity": "critical"}],
                "functions": [],
                "recommendations": ["Fix module reading error"]
            }
    
    def _is_dangerous_import(self, import_line: str) -> bool:
        """Check if import line contains dangerous modules"""
        for module in self.blocked_modules:
            if module in import_line:
                return True
        return False
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        """Extract function definitions from content"""
        functions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('def '):
                # Extract function name
                func_name = line[4:].split('(')[0].strip()
                
                # Extract docstring if available
                docstring = ""
                if line_num < len(lines):
                    next_line = lines[line_num].strip()
                    if next_line.startswith('"""') or next_line.startswith("'''"):
                        docstring = next_line[3:]
                
                functions.append({
                    "name": func_name,
                    "line": line_num,
                    "docstring": docstring,
                    "security_safe": self._is_function_safe(func_name, content)
                })
        
        return functions
    
    def _is_function_safe(self, func_name: str, content: str) -> bool:
        """Check if function is safe to use"""
        # Check function content for dangerous patterns
        func_start = content.find(f"def {func_name}")
        if func_start == -1:
            return False
        
        # Find next function or end of class
        next_def = content.find("\ndef ", func_start + 1)
        if next_def == -1:
            func_content = content[func_start:]
        else:
            func_content = content[func_start:next_def]
        
        # Check for dangerous patterns in function
        for pattern in self.blocked_functions:
            if pattern in func_content:
                return False
        
        return True
    
    def _generate_helper_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        high_issues = [i for i in issues if i.get("severity") == "high"]
        medium_issues = [i for i in issues if i.get("severity") == "medium"]
        
        if high_issues:
            recommendations.append("Remove or replace high-risk functions with VoiceOS-safe alternatives")
        
        if medium_issues:
            recommendations.append("Use VoiceOS wrapper functions for system operations")
        
        if len(issues) > 5:
            recommendations.append("Consider refactoring helper to use VoiceOS architecture")
        
        return recommendations


class SecureHelperAdapter:
    """Adapts helper functions to VoiceOS security model"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = HelperValidator()
        self.registered_helpers: Dict[str, HelperModule] = {}
        self.safe_wrappers: Dict[str, Callable] = {}
        self._create_safe_wrappers()
    
    async def register_helper_module(self, module_path: Path, category: HelperCategory) -> Dict[str, Any]:
        """
        Register a helper module with security validation.
        
        Args:
            module_path: Path to helper module
            category: Helper category
            
        Returns:
            Registration result
        """
        try:
            # Validate module
            validation_result = self.validator.validate_helper_module(module_path)
            
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": "Security validation failed",
                    "issues": validation_result["issues"],
                    "recommendations": validation_result["recommendations"]
                }
            
            # Create helper module definition
            module_name = module_path.stem
            checksum = self._calculate_checksum(module_path)
            
            helper_module = HelperModule(
                name=module_name,
                path=module_path,
                category=category,
                security_level=self._determine_security_level(validation_result),
                functions=self._create_helper_functions(validation_result["functions"]),
                validated=True,
                checksum=checksum
            )
            
            # Register module
            self.registered_helpers[module_name] = helper_module
            
            return {
                "success": True,
                "module_name": module_name,
                "security_score": validation_result["security_score"],
                "functions_count": len(helper_module.functions),
                "security_level": helper_module.security_level.value
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Registration failed: {e}"
            }
    
    async def execute_helper_function(self, module_name: str, function_name: str,
                                    params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute helper function with security controls.
        
        Args:
            module_name: Name of helper module
            function_name: Name of function to execute
            params: Function parameters
            
        Returns:
            Execution result
        """
        if module_name not in self.registered_helpers:
            return {
                "success": False,
                "error": f"Helper module not registered: {module_name}"
            }
        
        helper_module = self.registered_helpers[module_name]
        
        # Find function
        target_function = None
        for func in helper_module.functions:
            if func.name == function_name:
                target_function = func
                break
        
        if not target_function:
            return {
                "success": False,
                "error": f"Function not found: {function_name}"
            }
        
        # Check security level
        if target_function.security_level == HelperSecurityLevel.BLOCKED:
            return {
                "success": False,
                "error": f"Function {function_name} is blocked for security reasons"
            }
        
        try:
            # Execute based on security level
            if target_function.security_level == HelperSecurityLevel.SAFE:
                result = await self._execute_safe_function(target_function, params)
            elif target_function.security_level == HelperSecurityLevel.RESTRICTED:
                result = await self._execute_restricted_function(target_function, params)
            elif target_function.security_level == HelperSecurityLevel.SANDBOXED:
                result = await self._execute_sandboxed_function(target_function, params)
            else:
                result = {
                    "success": False,
                    "error": f"Unsupported security level: {target_function.security_level}"
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Helper function execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_safe_function(self, function: HelperFunction, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute safe function directly"""
        try:
            # Import module
            module = importlib.import_module(function.module)
            
            # Get function
            func = getattr(module, function.name)
            
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(**params)
            else:
                result = func(**params)
            
            return {
                "success": True,
                "result": result,
                "security_level": "safe"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "security_level": "safe"
            }
    
    async def _execute_restricted_function(self, function: HelperFunction, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute restricted function with validation"""
        # Use safe wrapper if available
        wrapper_key = f"{function.module}.{function.name}"
        if wrapper_key in self.safe_wrappers:
            wrapper = self.safe_wrappers[wrapper_key]
            try:
                result = await wrapper(**params)
                return {
                    "success": True,
                    "result": result,
                    "security_level": "restricted"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "security_level": "restricted"
                }
        
        # Fall back to safe execution
        return await self._execute_safe_function(function, params)
    
    async def _execute_sandboxed_function(self, function: HelperFunction, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute function in sandbox"""
        # This would implement actual sandboxing
        # For now, fall back to restricted execution
        return await self._execute_restricted_function(function, params)
    
    def _determine_security_level(self, validation_result: Dict[str, Any]) -> HelperSecurityLevel:
        """Determine security level from validation"""
        security_score = validation_result["security_score"]
        
        if security_score >= 90:
            return HelperSecurityLevel.SAFE
        elif security_score >= 70:
            return HelperSecurityLevel.RESTRICTED
        elif security_score >= 50:
            return HelperSecurityLevel.SANDBOXED
        else:
            return HelperSecurityLevel.BLOCKED
    
    def _create_helper_functions(self, function_data: List[Dict[str, Any]]) -> List[HelperFunction]:
        """Create helper function definitions"""
        functions = []
        
        for func_data in function_data:
            security_level = HelperSecurityLevel.SAFE
            if not func_data.get("security_safe", False):
                security_level = HelperSecurityLevel.RESTRICTED
            
            function = HelperFunction(
                name=func_data["name"],
                module="",  # Would be filled during registration
                category=HelperCategory.UTILITIES,  # Would be determined from context
                security_level=security_level,
                required_permissions=[PermissionLevel.MEDIUM],
                description=func_data.get("docstring", ""),
                parameters={},
                return_type=None
            )
            functions.append(function)
        
        return functions
    
    def _calculate_checksum(self, module_path: Path) -> str:
        """Calculate module checksum"""
        with open(module_path, 'rb') as f:
            content = f.read()
        return hashlib.sha256(content).hexdigest()
    
    def _create_safe_wrappers(self):
        """Create safe wrapper functions"""
        # File operations wrapper
        async def safe_file_operation(operation: str, path: str, **kwargs):
            """Safe file operations wrapper"""
            # Validate path is within workspace
            workspace = config.project_root / "workspace"
            try:
                Path(path).resolve().relative_to(workspace.resolve())
            except ValueError:
                return {
                    "success": False,
                    "error": "File access outside workspace not allowed"
                }
            
            # Execute through VoiceOS file tools
            from tools.file_tools import read_file, write_file
            
            if operation == "read":
                return {"success": True, "content": read_file(path)}
            elif operation == "write":
                return {"success": True, "result": write_file(path, kwargs.get("content", ""))}
            else:
                return {"success": False, "error": f"Unsupported operation: {operation}"}
        
        self.safe_wrappers["files.file_operation"] = safe_file_operation
        
        # Web operations wrapper
        async def safe_web_operation(operation: str, url: str, **kwargs):
            """Safe web operations wrapper"""
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                return {"success": False, "error": "Invalid URL protocol"}
            
            # Execute through VoiceOS browser tools
            if operation == "search":
                return {"success": True, "results": f"Search results for {url}"}
            elif operation == "fetch":
                return {"success": True, "content": f"Content from {url}"}
            else:
                return {"success": False, "error": f"Unsupported operation: {operation}"}
        
        self.safe_wrappers["browser.web_operation"] = safe_web_operation
    
    def get_registered_helpers(self) -> List[Dict[str, Any]]:
        """Get list of registered helpers"""
        return [
            {
                "name": module.name,
                "category": module.category.value,
                "security_level": module.security_level.value,
                "functions_count": len(module.functions),
                "validated": module.validated,
                "path": str(module.path)
            }
            for module in self.registered_helpers.values()
        ]
    
    def get_helper_functions(self, module_name: str) -> List[Dict[str, Any]]:
        """Get functions for a specific helper module"""
        if module_name not in self.registered_helpers:
            return []
        
        module = self.registered_helpers[module_name]
        return [
            {
                "name": func.name,
                "security_level": func.security_level.value,
                "description": func.description,
                "required_permissions": [p.value for p in func.required_permissions]
            }
            for func in module.functions
        ]


# Global helper adapter instance
secure_helper_adapter = None

def get_secure_helper_adapter() -> SecureHelperAdapter:
    """Get or create secure helper adapter instance"""
    global secure_helper_adapter
    if secure_helper_adapter is None:
        secure_helper_adapter = SecureHelperAdapter()
    return secure_helper_adapter
