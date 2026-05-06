"""
VoiceOS System Verification and Configuration Check

This module verifies that all integration components are properly configured
and ready for operation while maintaining VoiceOS security boundaries.
"""

import asyncio
import logging
import importlib
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import traceback

from core.config import config
from tools.tool_registry import ToolRegistry


class VerificationStatus(Enum):
    """Verification status levels"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ComponentVerification:
    """Component verification result"""
    component_name: str
    status: VerificationStatus
    message: str
    details: Dict[str, Any] = None
    errors: List[str] = None
    warnings: List[str] = None


class VoiceOSSystemVerifier:
    """
    Verifies VoiceOS integration system configuration and readiness.
    
    This class ensures all components are properly configured while maintaining
    VoiceOS security boundaries and architectural purity.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tool_registry = ToolRegistry()
        self.verification_results: List[ComponentVerification] = []
    
    async def verify_system_configuration(self) -> Dict[str, Any]:
        """
        Verify complete system configuration.
        
        Returns:
            Comprehensive verification results
        """
        self.logger.info("Starting VoiceOS system verification...")
        self.verification_results = []
        
        # Verify core components
        await self._verify_core_dependencies()
        await self._verify_plugin_system()
        await self._verify_helper_system()
        await self._verify_extension_system()
        await self._verify_monitoring_system()
        await self._verify_dashboard_system()
        await self._verify_security_configuration()
        await self._verify_workspace_configuration()
        
        # Generate summary
        summary = self._generate_verification_summary()
        
        self.logger.info(f"System verification completed: {summary['overall_status']}")
        
        return {
            "overall_status": summary["overall_status"],
            "total_components": summary["total_components"],
            "passed_components": summary["passed_components"],
            "failed_components": summary["failed_components"],
            "warning_components": summary["warning_components"],
            "skipped_components": summary["skipped_components"],
            "verification_results": [
                {
                    "component": result.component_name,
                    "status": result.status.value,
                    "message": result.message,
                    "details": result.details or {},
                    "errors": result.errors or [],
                    "warnings": result.warnings or []
                }
                for result in self.verification_results
            ],
            "recommendations": summary["recommendations"],
            "next_steps": summary["next_steps"]
        }
    
    async def _verify_core_dependencies(self):
        """Verify core system dependencies"""
        self.logger.info("Verifying core dependencies...")
        
        # Check required modules
        required_modules = [
            "core.config",
            "permissions.permission_engine",
            "tools.tool_registry",
            "core.plugins.secure_plugin_integration",
            "core.helpers.secure_helper_integration",
            "core.extensions.secure_extension_integration"
        ]
        
        errors = []
        warnings = []
        passed_modules = []
        
        for module_name in required_modules:
            try:
                module = importlib.import_module(module_name)
                passed_modules.append(module_name)
                self.logger.debug(f"✓ {module_name} - imported successfully")
            except ImportError as e:
                errors.append(f"Failed to import {module_name}: {e}")
                self.logger.error(f"✗ {module_name} - import failed: {e}")
            except Exception as e:
                warnings.append(f"Warning importing {module_name}: {e}")
                self.logger.warning(f"⚠ {module_name} - import warning: {e}")
        
        # Determine status
        if errors:
            status = VerificationStatus.FAILED
            message = f"Core dependencies verification failed: {len(errors)} errors"
        elif warnings:
            status = VerificationStatus.WARNING
            message = f"Core dependencies verification passed with {len(warnings)} warnings"
        else:
            status = VerificationStatus.PASSED
            message = f"All {len(passed_modules)} core dependencies verified successfully"
        
        self.verification_results.append(ComponentVerification(
            component_name="core_dependencies",
            status=status,
            message=message,
            details={
                "required_modules": required_modules,
                "passed_modules": passed_modules,
                "total_modules": len(required_modules)
            },
            errors=errors,
            warnings=warnings
        ))
    
    async def _verify_plugin_system(self):
        """Verify plugin system configuration"""
        self.logger.info("Verifying plugin system...")
        
        try:
            # Import plugin system components
            from core.plugins.complete_plugin_integration import get_complete_plugin_system
            from core.plugins.plugin_lifecycle import get_lifecycle_manager
            from core.plugins.plugin_registry import get_plugin_registry
            from core.plugins.plugin_configuration import get_plugin_config_manager
            from core.plugins.plugin_error_handling import get_plugin_error_handler
            from core.plugins.plugin_monitoring import get_plugin_monitor
            from core.plugins.plugin_testing import get_plugin_test_framework
            
            # Check plugin system instantiation
            plugin_system = get_complete_plugin_system()
            lifecycle_manager = get_lifecycle_manager()
            plugin_registry = get_plugin_registry()
            config_manager = get_plugin_config_manager()
            error_handler = get_plugin_error_handler()
            monitor = get_plugin_monitor()
            test_framework = get_plugin_test_framework()
            
            # Verify plugin system components
            components = {
                "complete_plugin_system": plugin_system,
                "lifecycle_manager": lifecycle_manager,
                "plugin_registry": plugin_registry,
                "config_manager": config_manager,
                "error_handler": error_handler,
                "monitor": monitor,
                "test_framework": test_framework
            }
            
            all_present = all(component is not None for component in components.values())
            
            if all_present:
                status = VerificationStatus.PASSED
                message = "All plugin system components are properly configured"
            else:
                status = VerificationStatus.FAILED
                message = "Some plugin system components are missing"
            
            self.verification_results.append(ComponentVerification(
                component_name="plugin_system",
                status=status,
                message=message,
                details={
                    "components_present": list(components.keys()),
                    "total_components": len(components)
                }
            ))
            
        except Exception as e:
            self.verification_results.append(ComponentVerification(
                component_name="plugin_system",
                status=VerificationStatus.FAILED,
                message=f"Plugin system verification failed: {e}",
                errors=[str(e)]
            ))
    
    async def _verify_helper_system(self):
        """Verify helper system configuration"""
        self.logger.info("Verifying helper system...")
        
        try:
            # Import helper system components
            from core.helpers.secure_helper_integration import get_secure_helper_adapter
            from core.helpers.helper_bridge_integration import get_helper_bridge_manager
            
            # Check helper system instantiation
            helper_adapter = get_secure_helper_adapter()
            bridge_manager = get_helper_bridge_manager(self.tool_registry)
            
            # Verify helper system components
            components = {
                "secure_helper_adapter": helper_adapter,
                "helper_bridge_manager": bridge_manager
            }
            
            all_present = all(component is not None for component in components.values())
            
            # Check helper registration
            registered_helpers = helper_adapter.get_registered_helpers()
            
            if all_present:
                status = VerificationStatus.PASSED
                message = f"Helper system configured with {len(registered_helpers)} registered helpers"
            else:
                status = VerificationStatus.FAILED
                message = "Some helper system components are missing"
            
            self.verification_results.append(ComponentVerification(
                component_name="helper_system",
                status=status,
                message=message,
                details={
                    "components_present": list(components.keys()),
                    "total_components": len(components),
                    "registered_helpers": len(registered_helpers)
                }
            ))
            
        except Exception as e:
            self.verification_results.append(ComponentVerification(
                component_name="helper_system",
                status=VerificationStatus.FAILED,
                message=f"Helper system verification failed: {e}",
                errors=[str(e)]
            ))
    
    async def _verify_extension_system(self):
        """Verify extension system configuration"""
        self.logger.info("Verifying extension system...")
        
        try:
            # Import extension system components
            from core.extensions.secure_extension_integration import get_secure_extension_manager
            from core.extensions.extension_point_system import get_extension_point_system
            from core.helpers.helper_extension_discovery import get_helper_extension_discovery
            
            # Check extension system instantiation
            extension_manager = get_secure_extension_manager()
            extension_point_system = get_extension_point_system()
            discovery_system = get_helper_extension_discovery()
            
            # Verify extension system components
            components = {
                "secure_extension_manager": extension_manager,
                "extension_point_system": extension_point_system,
                "discovery_system": discovery_system
            }
            
            all_present = all(component is not None for component in components.values())
            
            # Check extension registration
            registered_extensions = extension_manager.get_registered_extensions()
            extension_points = extension_point_system.get_system_status()
            
            if all_present:
                status = VerificationStatus.PASSED
                message = f"Extension system configured with {len(registered_extensions)} extensions and {len(extension_points.get('extension_points', {}))} extension points"
            else:
                status = VerificationStatus.FAILED
                message = "Some extension system components are missing"
            
            self.verification_results.append(ComponentVerification(
                component_name="extension_system",
                status=status,
                message=message,
                details={
                    "components_present": list(components.keys()),
                    "total_components": len(components),
                    "registered_extensions": len(registered_extensions),
                    "extension_points": len(extension_points.get('extension_points', {}))
                }
            ))
            
        except Exception as e:
            self.verification_results.append(ComponentVerification(
                component_name="extension_system",
                status=VerificationStatus.FAILED,
                message=f"Extension system verification failed: {e}",
                errors=[str(e)]
            ))
    
    async def _verify_monitoring_system(self):
        """Verify monitoring system configuration"""
        self.logger.info("Verifying monitoring system...")
        
        try:
            # Import monitoring system components
            from core.helpers.helper_extension_monitoring import get_helper_extension_monitor
            from core.plugins.plugin_monitoring import get_plugin_monitor
            
            # Check monitoring system instantiation
            helper_monitor = get_helper_extension_monitor()
            plugin_monitor = get_plugin_monitor()
            
            # Verify monitoring system components
            components = {
                "helper_extension_monitor": helper_monitor,
                "plugin_monitor": plugin_monitor
            }
            
            all_present = all(component is not None for component in components.values())
            
            if all_present:
                status = VerificationStatus.PASSED
                message = "All monitoring system components are properly configured"
            else:
                status = VerificationStatus.FAILED
                message = "Some monitoring system components are missing"
            
            self.verification_results.append(ComponentVerification(
                component_name="monitoring_system",
                status=status,
                message=message,
                details={
                    "components_present": list(components.keys()),
                    "total_components": len(components)
                }
            ))
            
        except Exception as e:
            self.verification_results.append(ComponentVerification(
                component_name="monitoring_system",
                status=VerificationStatus.FAILED,
                message=f"Monitoring system verification failed: {e}",
                errors=[str(e)]
            ))
    
    async def _verify_dashboard_system(self):
        """Verify dashboard system configuration"""
        self.logger.info("Verifying dashboard system...")
        
        try:
            # Import dashboard system components
            from core.system.unified_integration_dashboard import get_unified_integration_dashboard
            
            # Check dashboard system instantiation
            dashboard = get_unified_integration_dashboard()
            
            # Verify dashboard system components
            components = {
                "unified_integration_dashboard": dashboard
            }
            
            all_present = all(component is not None for component in components.values())
            
            if all_present:
                status = VerificationStatus.PASSED
                message = "Dashboard system is properly configured"
            else:
                status = VerificationStatus.FAILED
                message = "Dashboard system components are missing"
            
            self.verification_results.append(ComponentVerification(
                component_name="dashboard_system",
                status=status,
                message=message,
                details={
                    "components_present": list(components.keys()),
                    "total_components": len(components)
                }
            ))
            
        except Exception as e:
            self.verification_results.append(ComponentVerification(
                component_name="dashboard_system",
                status=VerificationStatus.FAILED,
                message=f"Dashboard system verification failed: {e}",
                errors=[str(e)]
            ))
    
    async def _verify_security_configuration(self):
        """Verify security configuration"""
        self.logger.info("Verifying security configuration...")
        
        try:
            # Check permission engine
            from permissions.permission_engine import permission_engine, PermissionLevel
            
            # Verify permission levels
            permission_levels = list(PermissionLevel)
            required_levels = [PermissionLevel.LOW, PermissionLevel.MEDIUM, PermissionLevel.HIGH]
            
            missing_levels = [level for level in required_levels if level not in permission_levels]
            
            # Check security policies
            from core.plugins.secure_plugin_integration import SecurityLevel, SecurityPolicy
            
            security_levels = list(SecurityLevel)
            required_security_levels = [SecurityLevel.SAFE, SecurityLevel.RESTRICTED, SecurityLevel.SANDBOXED, SecurityLevel.ISOLATED]
            
            missing_security_levels = [level for level in required_security_levels if level not in security_levels]
            
            errors = []
            if missing_levels:
                errors.append(f"Missing permission levels: {missing_levels}")
            if missing_security_levels:
                errors.append(f"Missing security levels: {missing_security_levels}")
            
            if errors:
                status = VerificationStatus.FAILED
                message = f"Security configuration has issues: {len(errors)} errors"
            else:
                status = VerificationStatus.PASSED
                message = "Security configuration is properly set up"
            
            self.verification_results.append(ComponentVerification(
                component_name="security_configuration",
                status=status,
                message=message,
                details={
                    "permission_levels": [level.value for level in permission_levels],
                    "security_levels": [level.value for level in security_levels],
                    "permission_engine_present": permission_engine is not None
                },
                errors=errors
            ))
            
        except Exception as e:
            self.verification_results.append(ComponentVerification(
                component_name="security_configuration",
                status=VerificationStatus.FAILED,
                message=f"Security configuration verification failed: {e}",
                errors=[str(e)]
            ))
    
    async def _verify_workspace_configuration(self):
        """Verify workspace configuration"""
        self.logger.info("Verifying workspace configuration...")
        
        try:
            workspace_root = config.project_root / "workspace"
            
            # Check workspace directories
            required_dirs = [
                "plugins",
                "helpers",
                "extensions",
                "registry",
                "config",
                "logs",
                "metrics",
                "tests",
                "executions",
                "sandboxes"
            ]
            
            existing_dirs = []
            missing_dirs = []
            
            for dir_name in required_dirs:
                dir_path = workspace_root / dir_name
                if dir_path.exists():
                    existing_dirs.append(dir_name)
                else:
                    missing_dirs.append(dir_name)
            
            # Create missing directories
            created_dirs = []
            for dir_name in missing_dirs:
                dir_path = workspace_root / dir_name
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(dir_name)
                    self.logger.info(f"Created missing directory: {dir_path}")
                except Exception as e:
                    self.logger.error(f"Failed to create directory {dir_path}: {e}")
            
            # Check configuration files
            config_files = [
                "plugins/plugin_registry.json",
                "config/plugins.yaml",
                "logs/plugin_errors.json",
                "metrics/plugin_metrics.json"
            ]
            
            existing_files = []
            for file_path in config_files:
                full_path = workspace_root / file_path
                if full_path.exists():
                    existing_files.append(file_path)
            
            if missing_dirs and not created_dirs:
                status = VerificationStatus.FAILED
                message = f"Workspace configuration failed: {len(missing_dirs)} missing directories"
            elif missing_dirs and created_dirs:
                status = VerificationStatus.WARNING
                message = f"Workspace configuration: Created {len(created_dirs)} missing directories"
            else:
                status = VerificationStatus.PASSED
                message = f"Workspace configuration is properly set up with {len(existing_dirs)} directories"
            
            self.verification_results.append(ComponentVerification(
                component_name="workspace_configuration",
                status=status,
                message=message,
                details={
                    "workspace_root": str(workspace_root),
                    "existing_dirs": existing_dirs,
                    "missing_dirs": missing_dirs,
                    "created_dirs": created_dirs,
                    "existing_files": existing_files,
                    "required_dirs": required_dirs
                },
                warnings=[] if status == VerificationStatus.PASSED else [f"Created {len(created_dirs)} directories"]
            ))
            
        except Exception as e:
            self.verification_results.append(ComponentVerification(
                component_name="workspace_configuration",
                status=VerificationStatus.FAILED,
                message=f"Workspace configuration verification failed: {e}",
                errors=[str(e)]
            ))
    
    def _generate_verification_summary(self) -> Dict[str, Any]:
        """Generate verification summary"""
        total_components = len(self.verification_results)
        passed_components = len([r for r in self.verification_results if r.status == VerificationStatus.PASSED])
        failed_components = len([r for r in self.verification_results if r.status == VerificationStatus.FAILED])
        warning_components = len([r for r in self.verification_results if r.status == VerificationStatus.WARNING])
        skipped_components = len([r for r in self.verification_results if r.status == VerificationStatus.SKIPPED])
        
        # Determine overall status
        if failed_components > 0:
            overall_status = VerificationStatus.FAILED
        elif warning_components > 0:
            overall_status = VerificationStatus.WARNING
        else:
            overall_status = VerificationStatus.PASSED
        
        # Generate recommendations
        recommendations = []
        next_steps = []
        
        if failed_components > 0:
            recommendations.append("Fix failed components before proceeding")
            next_steps.append("Review error messages and fix configuration issues")
        
        if warning_components > 0:
            recommendations.append("Address warnings for optimal performance")
            next_steps.append("Review warnings and implement suggested improvements")
        
        if passed_components == total_components:
            recommendations.append("System is ready for operation")
            next_steps.append("Start the integration system and begin using plugins, helpers, and extensions")
        
        return {
            "overall_status": overall_status.value,
            "total_components": total_components,
            "passed_components": passed_components,
            "failed_components": failed_components,
            "warning_components": warning_components,
            "skipped_components": skipped_components,
            "recommendations": recommendations,
            "next_steps": next_steps
        }


# Global verifier instance
system_verifier = None

def get_system_verifier() -> VoiceOSSystemVerifier:
    """Get or create system verifier instance"""
    global system_verifier
    if system_verifier is None:
        system_verifier = VoiceOSSystemVerifier()
    return system_verifier


async def verify_voiceos_system():
    """Verify complete VoiceOS system configuration"""
    verifier = get_system_verifier()
    return await verifier.verify_system_configuration()


if __name__ == "__main__":
    # Run system verification
    import asyncio
    
    async def main():
        result = await verify_voiceos_system()
        print("\n" + "="*60)
        print("VOICEOS SYSTEM VERIFICATION RESULTS")
        print("="*60)
        print(f"Overall Status: {result['overall_status'].upper()}")
        print(f"Total Components: {result['total_components']}")
        print(f"Passed: {result['passed_components']}")
        print(f"Failed: {result['failed_components']}")
        print(f"Warnings: {result['warning_components']}")
        print("="*60)
        
        if result['recommendations']:
            print("\nRECOMMENDATIONS:")
            for rec in result['recommendations']:
                print(f"• {rec}")
        
        if result['next_steps']:
            print("\nNEXT STEPS:")
            for step in result['next_steps']:
                print(f"• {step}")
        
        # Show failed components
        failed = [r for r in result['verification_results'] if r['status'] == 'failed']
        if failed:
            print("\nFAILED COMPONENTS:")
            for comp in failed:
                print(f"• {comp['component']}: {comp['message']}")
                if comp['errors']:
                    for error in comp['errors']:
                        print(f"  - {error}")
        
        print("="*60)
    
    asyncio.run(main())
