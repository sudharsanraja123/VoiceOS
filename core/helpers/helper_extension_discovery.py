"""
VoiceOS Helper and Extension Discovery System

This module provides secure discovery and loading for helpers and extensions
while maintaining VoiceOS security boundaries and architectural purity.
"""

import asyncio
import logging
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import time

from core.config import config
from core.helpers.secure_helper_integration import get_secure_helper_adapter, HelperCategory
from core.extensions.secure_extension_integration import get_secure_extension_manager, ExtensionType


class DiscoveryStatus(Enum):
    """Discovery status"""
    PENDING = "pending"
    DISCOVERING = "discovering"
    VALIDATING = "validating"
    LOADING = "loading"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DiscoveryResult:
    """Discovery result"""
    item_type: str  # "helper" or "extension"
    item_name: str
    path: Path
    status: DiscoveryStatus
    security_score: int = 0
    issues: List[str] = None
    loaded: bool = False
    load_time: float = 0.0
    error_message: str = ""


class HelperExtensionDiscovery:
    """
    Discovers and loads helpers and extensions securely.
    
    This class provides comprehensive discovery while maintaining VoiceOS
    security boundaries and architectural purity.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger(__name__)
        
        # Discovery paths
        self.helper_paths = [
            workspace_root / "helpers",
            Path("helpers"),
            Path("agent-zero-main/agent-zero-main/helpers")
        ]
        
        self.extension_paths = [
            workspace_root / "extensions",
            Path("extensions"),
            Path("agent-zero-main/agent-zero-main/extensions")
        ]
        
        # Component managers
        self.helper_adapter = get_secure_helper_adapter()
        self.extension_manager = get_secure_extension_manager()
        
        # Discovery state
        self.discovery_results: List[DiscoveryResult] = []
        self.last_discovery_time = 0.0
        self.auto_discovery_enabled = True
        self.discovery_interval = 300  # 5 minutes
        
        # Background task
        self._discovery_task = None
    
    async def start_discovery_service(self):
        """Start the discovery service"""
        self.logger.info("Starting helper and extension discovery service...")
        
        # Initial discovery
        await self.discover_all()
        
        # Start background discovery
        if self.auto_discovery_enabled:
            self._discovery_task = asyncio.create_task(self._background_discovery())
        
        self.logger.info("Discovery service started")
    
    async def stop_discovery_service(self):
        """Stop the discovery service"""
        self.logger.info("Stopping discovery service...")
        
        if self._discovery_task:
            self._discovery_task.cancel()
            try:
                await self._discovery_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Discovery service stopped")
    
    async def discover_all(self) -> Dict[str, Any]:
        """Discover all helpers and extensions"""
        self.logger.info("Starting comprehensive discovery...")
        
        start_time = time.time()
        
        # Discover helpers
        helper_results = await self.discover_helpers()
        
        # Discover extensions
        extension_results = await self.discover_extensions()
        
        # Load discovered items
        load_results = await self.load_discovered_items()
        
        self.last_discovery_time = time.time()
        
        total_time = time.time() - start_time
        
        return {
            "success": True,
            "discovery_time": total_time,
            "helpers": {
                "discovered": len(helper_results),
                "loaded": len([r for r in helper_results if r.loaded]),
                "failed": len([r for r in helper_results if r.status == DiscoveryStatus.FAILED])
            },
            "extensions": {
                "discovered": len(extension_results),
                "loaded": len([r for r in extension_results if r.loaded]),
                "failed": len([r for r in extension_results if r.status == DiscoveryStatus.FAILED])
            },
            "load_results": load_results
        }
    
    async def discover_helpers(self) -> List[DiscoveryResult]:
        """Discover helper modules"""
        self.logger.info("Discovering helper modules...")
        
        results = []
        
        for helper_path in self.helper_paths:
            if not helper_path.exists():
                self.logger.debug(f"Helper path not found: {helper_path}")
                continue
            
            # Find Python files
            py_files = list(helper_path.glob("*.py"))
            
            for py_file in py_files:
                result = await self._discover_helper_file(py_file)
                results.append(result)
        
        # Find helper subdirectories
        for helper_path in self.helper_paths:
            if not helper_path.exists():
                continue
            
            for helper_dir in helper_path.iterdir():
                if helper_dir.is_dir():
                    result = await self._discover_helper_directory(helper_dir)
                    results.append(result)
        
        self.logger.info(f"Discovered {len(results)} helper modules")
        return results
    
    async def discover_extensions(self) -> List[DiscoveryResult]:
        """Discover extensions"""
        self.logger.info("Discovering extensions...")
        
        results = []
        
        for extension_path in self.extension_paths:
            if not extension_path.exists():
                self.logger.debug(f"Extension path not found: {extension_path}")
                continue
            
            # Look for extension directories with manifest
            for item in extension_path.iterdir():
                if item.is_dir():
                    manifest_path = item / "extension.yaml"
                    if manifest_path.exists():
                        result = await self._discover_extension_directory(item)
                        results.append(result)
        
        self.logger.info(f"Discovered {len(results)} extensions")
        return results
    
    async def load_discovered_items(self) -> Dict[str, Any]:
        """Load all discovered items"""
        self.logger.info("Loading discovered helpers and extensions...")
        
        load_results = {
            "helpers": {"loaded": 0, "failed": 0, "errors": []},
            "extensions": {"loaded": 0, "failed": 0, "errors": []}
        }
        
        for result in self.discovery_results:
            if result.loaded:
                continue
            
            try:
                if result.item_type == "helper":
                    load_result = await self._load_helper(result)
                    if load_result["success"]:
                        result.loaded = True
                        load_results["helpers"]["loaded"] += 1
                    else:
                        load_results["helpers"]["failed"] += 1
                        load_results["helpers"]["errors"].append({
                            "item": result.item_name,
                            "error": load_result.get("error", "Unknown error")
                        })
                
                elif result.item_type == "extension":
                    load_result = await self._load_extension(result)
                    if load_result["success"]:
                        result.loaded = True
                        load_results["extensions"]["loaded"] += 1
                    else:
                        load_results["extensions"]["failed"] += 1
                        load_results["extensions"]["errors"].append({
                            "item": result.item_name,
                            "error": load_result.get("error", "Unknown error")
                        })
                
            except Exception as e:
                self.logger.error(f"Failed to load {result.item_type} {result.item_name}: {e}")
                load_results[result.item_type]["failed"] += 1
                load_results[result.item_type]["errors"].append({
                    "item": result.item_name,
                    "error": str(e)
                })
        
        self.logger.info(f"Loading completed - Helpers: {load_results['helpers']['loaded']} loaded, {load_results['helpers']['failed']} failed")
        self.logger.info(f"Loading completed - Extensions: {load_results['extensions']['loaded']} loaded, {load_results['extensions']['failed']} failed")
        
        return load_results
    
    async def _discover_helper_file(self, helper_file: Path) -> DiscoveryResult:
        """Discover a single helper file"""
        result = DiscoveryResult(
            item_type="helper",
            item_name=helper_file.stem,
            path=helper_file,
            status=DiscoveryStatus.PENDING
        )
        
        try:
            result.status = DiscoveryStatus.VALIDATING
            
            # Validate helper
            validation_result = self.helper_adapter.validator.validate_helper_module(helper_file)
            
            result.security_score = validation_result["security_score"]
            result.issues = [f"{issue['type']}: {issue.get('pattern', issue.get('content', 'Unknown'))}" 
                            for issue in validation_result["issues"]]
            
            if validation_result["valid"]:
                result.status = DiscoveryStatus.COMPLETED
            else:
                result.status = DiscoveryStatus.FAILED
                result.error_message = "Security validation failed"
            
        except Exception as e:
            result.status = DiscoveryStatus.FAILED
            result.error_message = str(e)
        
        return result
    
    async def _discover_helper_directory(self, helper_dir: Path) -> DiscoveryResult:
        """Discover a helper directory"""
        result = DiscoveryResult(
            item_type="helper",
            item_name=helper_dir.name,
            path=helper_dir,
            status=DiscoveryStatus.PENDING
        )
        
        try:
            result.status = DiscoveryStatus.VALIDATING
            
            # Look for main.py or __init__.py
            main_file = helper_dir / "main.py"
            init_file = helper_dir / "__init__.py"
            
            target_file = None
            if main_file.exists():
                target_file = main_file
            elif init_file.exists():
                target_file = init_file
            
            if not target_file:
                result.status = DiscoveryStatus.FAILED
                result.error_message = "No main.py or __init__.py found"
                return result
            
            # Validate helper
            validation_result = self.helper_adapter.validator.validate_helper_module(target_file)
            
            result.security_score = validation_result["security_score"]
            result.issues = [f"{issue['type']}: {issue.get('pattern', issue.get('content', 'Unknown'))}" 
                            for issue in validation_result["issues"]]
            
            if validation_result["valid"]:
                result.status = DiscoveryStatus.COMPLETED
            else:
                result.status = DiscoveryStatus.FAILED
                result.error_message = "Security validation failed"
            
        except Exception as e:
            result.status = DiscoveryStatus.FAILED
            result.error_message = str(e)
        
        return result
    
    async def _discover_extension_directory(self, extension_dir: Path) -> DiscoveryResult:
        """Discover an extension directory"""
        result = DiscoveryResult(
            item_type="extension",
            item_name=extension_dir.name,
            path=extension_dir,
            status=DiscoveryStatus.PENDING
        )
        
        try:
            result.status = DiscoveryStatus.VALIDATING
            
            # Validate extension
            validation_result = self.extension_manager.validator.validate_extension(extension_dir)
            
            result.security_score = validation_result["security_score"]
            result.issues = [f"{issue['type']}: {issue.get('pattern', issue.get('content', 'Unknown'))}" 
                            for issue in validation_result["issues"]]
            
            if validation_result["valid"]:
                result.status = DiscoveryStatus.COMPLETED
            else:
                result.status = DiscoveryStatus.FAILED
                result.error_message = "Security validation failed"
            
        except Exception as e:
            result.status = DiscoveryStatus.FAILED
            result.error_message = str(e)
        
        return result
    
    async def _load_helper(self, result: DiscoveryResult) -> Dict[str, Any]:
        """Load a helper"""
        try:
            result.status = DiscoveryStatus.LOADING
            start_time = time.time()
            
            # Determine category based on path or name
            category = self._determine_helper_category(result.path, result.item_name)
            
            # Register helper
            load_result = await self.helper_adapter.register_helper_module(result.path, category)
            
            result.load_time = time.time() - start_time
            
            if load_result["success"]:
                result.status = DiscoveryStatus.COMPLETED
                return load_result
            else:
                result.status = DiscoveryStatus.FAILED
                result.error_message = load_result.get("error", "Load failed")
                return load_result
            
        except Exception as e:
            result.status = DiscoveryStatus.FAILED
            result.error_message = str(e)
            return {"success": False, "error": str(e)}
    
    async def _load_extension(self, result: DiscoveryResult) -> Dict[str, Any]:
        """Load an extension"""
        try:
            result.status = DiscoveryStatus.LOADING
            start_time = time.time()
            
            # Load extension
            load_result = await self.extension_manager.load_extension(result.path)
            
            result.load_time = time.time() - start_time
            
            if load_result["success"]:
                result.status = DiscoveryStatus.COMPLETED
                return load_result
            else:
                result.status = DiscoveryStatus.FAILED
                result.error_message = load_result.get("error", "Load failed")
                return load_result
            
        except Exception as e:
            result.status = DiscoveryStatus.FAILED
            result.error_message = str(e)
            return {"success": False, "error": str(e)}
    
    def _determine_helper_category(self, path: Path, name: str) -> HelperCategory:
        """Determine helper category from path and name"""
        name_lower = name.lower()
        path_str = str(path).lower()
        
        # File operations
        if any(keyword in name_lower or keyword in path_str for keyword in ["file", "directory", "folder", "path"]):
            return HelperCategory.FILE_OPERATIONS
        
        # Web operations
        if any(keyword in name_lower or keyword in path_str for keyword in ["web", "browser", "http", "url", "internet"]):
            return HelperCategory.WEB_OPERATIONS
        
        # Data processing
        if any(keyword in name_lower or keyword in path_str for keyword in ["data", "process", "parse", "transform", "convert"]):
            return HelperCategory.DATA_PROCESSING
        
        # System operations
        if any(keyword in name_lower or keyword in path_str for keyword in ["system", "os", "process", "command"]):
            return HelperCategory.SYSTEM_OPERATIONS
        
        # Communication
        if any(keyword in name_lower or keyword in path_str for keyword in ["comm", "network", "socket", "email", "message"]):
            return HelperCategory.COMMUNICATION
        
        # Security
        if any(keyword in name_lower or keyword in path_str for keyword in ["security", "crypto", "auth", "encrypt", "decrypt"]):
            return HelperCategory.SECURITY
        
        # Validation
        if any(keyword in name_lower or keyword in path_str for keyword in ["valid", "check", "verify", "test"]):
            return HelperCategory.VALIDATION
        
        # Default to utilities
        return HelperCategory.UTILITIES
    
    async def _background_discovery(self):
        """Background discovery task"""
        while True:
            try:
                await asyncio.sleep(self.discovery_interval)
                
                if self.auto_discovery_enabled:
                    await self.discover_all()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Background discovery error: {e}")
    
    def get_discovery_status(self) -> Dict[str, Any]:
        """Get discovery status"""
        helpers = [r for r in self.discovery_results if r.item_type == "helper"]
        extensions = [r for r in self.discovery_results if r.item_type == "extension"]
        
        return {
            "last_discovery_time": self.last_discovery_time,
            "auto_discovery_enabled": self.auto_discovery_enabled,
            "discovery_interval": self.discovery_interval,
            "helpers": {
                "total": len(helpers),
                "discovered": len([h for h in helpers if h.status == DiscoveryStatus.COMPLETED]),
                "loaded": len([h for h in helpers if h.loaded]),
                "failed": len([h for h in helpers if h.status == DiscoveryStatus.FAILED]),
                "average_security_score": sum(h.security_score for h in helpers) / len(helpers) if helpers else 0
            },
            "extensions": {
                "total": len(extensions),
                "discovered": len([e for e in extensions if e.status == DiscoveryStatus.COMPLETED]),
                "loaded": len([e for e in extensions if e.loaded]),
                "failed": len([e for e in extensions if e.status == DiscoveryStatus.FAILED]),
                "average_security_score": sum(e.security_score for e in extensions) / len(extensions) if extensions else 0
            },
            "discovery_results": [
                {
                    "type": r.item_type,
                    "name": r.item_name,
                    "path": str(r.path),
                    "status": r.status.value,
                    "security_score": r.security_score,
                    "loaded": r.loaded,
                    "load_time": r.load_time,
                    "issues": r.issues,
                    "error_message": r.error_message
                }
                for r in self.discovery_results
            ]
        }
    
    def set_discovery_paths(self, helper_paths: List[Path] = None, extension_paths: List[Path] = None):
        """Set custom discovery paths"""
        if helper_paths:
            self.helper_paths = helper_paths
        
        if extension_paths:
            self.extension_paths = extension_paths
    
    def enable_auto_discovery(self, enabled: bool = True, interval: int = 300):
        """Enable or disable auto discovery"""
        self.auto_discovery_enabled = enabled
        self.discovery_interval = interval


# Global discovery instance
helper_extension_discovery = None

def get_helper_extension_discovery() -> HelperExtensionDiscovery:
    """Get or create discovery instance"""
    global helper_extension_discovery
    if helper_extension_discovery is None:
        helper_extension_discovery = HelperExtensionDiscovery(config.project_root / "workspace")
    return helper_extension_discovery
