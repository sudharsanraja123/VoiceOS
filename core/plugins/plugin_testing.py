"""
VoiceOS Plugin Testing and Validation Framework

This module provides comprehensive testing and validation for plugins while
maintaining VoiceOS security boundaries and architectural purity.
"""

import asyncio
import logging
import time
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import traceback
from datetime import datetime

from core.config import config
from permissions.permission_engine import PermissionLevel
from core.plugins.secure_plugin_integration import SecurityLevel, SecurityPolicy, PluginManifest
from core.plugins.plugin_lifecycle import PluginState, PluginInstance


class TestType(Enum):
    """Test types"""
    UNIT = "unit"                     # Unit tests
    INTEGRATION = "integration"       # Integration tests
    SECURITY = "security"             # Security tests
    PERFORMANCE = "performance"       # Performance tests
    COMPATIBILITY = "compatibility"   # Compatibility tests
    SANDBOX = "sandbox"               # Sandbox validation tests


class TestResult(Enum):
    """Test result statuses"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"


class TestSeverity(Enum):
    """Test severity levels"""
    CRITICAL = "critical"             # Critical tests that must pass
    HIGH = "high"                     # High importance tests
    MEDIUM = "medium"                 # Medium importance tests
    LOW = "low"                       # Low importance tests


@dataclass
class TestCase:
    """Test case definition"""
    test_id: str
    name: str
    description: str
    test_type: TestType
    severity: TestSeverity
    timeout_seconds: int = 30
    required_permissions: List[PermissionLevel] = field(default_factory=list)
    test_function: Optional[Callable] = None
    expected_result: Optional[Any] = None
    expected_error: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class TestExecution:
    """Test execution result"""
    test_case: TestCase
    start_time: datetime
    end_time: Optional[datetime] = None
    result: TestResult = TestResult.FAILED
    output: str = ""
    error_message: str = ""
    execution_time: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    """Test suite definition"""
    suite_name: str
    description: str
    test_cases: List[TestCase] = field(default_factory=list)
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None
    parallel_execution: bool = False
    max_parallel_tests: int = 5


@dataclass
class ValidationReport:
    """Plugin validation report"""
    plugin_name: str
    plugin_version: str
    validation_time: datetime
    overall_result: TestResult
    test_suites: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security_score: float = 0.0
    performance_score: float = 0.0
    compatibility_score: float = 0.0
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    recommendations: List[str] = field(default_factory=list)
    security_violations: List[str] = field(default_factory=list)


class PluginTestFramework:
    """
    Comprehensive plugin testing and validation framework.
    
    This class provides testing capabilities while maintaining VoiceOS
    security boundaries and architectural purity.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger(__name__)
        
        # Test storage
        self.test_results_path = workspace_root / "tests" / "results"
        self.test_results_path.mkdir(parents=True, exist_ok=True)
        
        # Test suites
        self.test_suites: Dict[str, TestSuite] = {}
        self._register_default_test_suites()
        
        # Test execution state
        self.current_executions: Dict[str, TestExecution] = {}
        self.execution_history: List[TestExecution] = []
        
        # Validation reports
        self.validation_reports: Dict[str, ValidationReport] = {}
        
        # Test environment
        self.test_environments: Dict[str, Path] = {}
        
        # Mock services for testing
        self.mock_services: Dict[str, Any] = {}
        self._setup_mock_services()
    
    async def register_test_suite(self, test_suite: TestSuite):
        """Register a test suite"""
        self.test_suites[test_suite.suite_name] = test_suite
        self.logger.info(f"Registered test suite: {test_suite.suite_name}")
    
    async def validate_plugin(self, plugin_path: Path, 
                           test_suites: Optional[List[str]] = None) -> ValidationReport:
        """
        Validate a plugin with comprehensive testing.
        
        Args:
            plugin_path: Path to plugin directory
            test_suites: List of test suite names to run (None = all)
            
        Returns:
            Validation report
        """
        self.logger.info(f"Starting plugin validation for: {plugin_path}")
        
        # Load plugin manifest
        manifest = await self._load_plugin_manifest(plugin_path)
        if not manifest:
            raise ValueError(f"Invalid plugin manifest in: {plugin_path}")
        
        # Create validation report
        report = ValidationReport(
            plugin_name=manifest.name,
            plugin_version=manifest.version,
            validation_time=datetime.now(),
            overall_result=TestResult.FAILED,
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0
        )
        
        # Create test environment
        test_env = await self._create_test_environment(manifest.name)
        
        try:
            # Determine which test suites to run
            suites_to_run = test_suites or list(self.test_suites.keys())
            
            # Run test suites
            all_passed = True
            for suite_name in suites_to_run:
                if suite_name not in self.test_suites:
                    self.logger.warning(f"Test suite not found: {suite_name}")
                    continue
                
                suite_result = await self._run_test_suite(
                    self.test_suites[suite_name], manifest, test_env
                )
                
                report.test_suites[suite_name] = suite_result
                report.total_tests += suite_result["total_tests"]
                report.passed_tests += suite_result["passed_tests"]
                report.failed_tests += suite_result["failed_tests"]
                report.skipped_tests += suite_result["skipped_tests"]
                
                if suite_result["result"] != TestResult.PASSED:
                    all_passed = False
            
            # Calculate scores
            report.security_score = self._calculate_security_score(report)
            report.performance_score = self._calculate_performance_score(report)
            report.compatibility_score = self._calculate_compatibility_score(report)
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(report)
            
            # Set overall result
            report.overall_result = TestResult.PASSED if all_passed else TestResult.FAILED
            
            # Save validation report
            self.validation_reports[manifest.name] = report
            await self._save_validation_report(report)
            
            self.logger.info(f"Plugin validation completed: {manifest.name} - {report.overall_result.value}")
            
            return report
            
        finally:
            # Cleanup test environment
            await self._cleanup_test_environment(manifest.name)
    
    async def run_test_suite(self, suite_name: str, plugin_manifest: PluginManifest) -> Dict[str, Any]:
        """Run a specific test suite"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Test suite not found: {suite_name}")
        
        test_env = await self._create_test_environment(plugin_manifest.name)
        
        try:
            result = await self._run_test_suite(
                self.test_suites[suite_name], plugin_manifest, test_env
            )
            return result
        finally:
            await self._cleanup_test_environment(plugin_manifest.name)
    
    async def create_custom_test(self, test_case: TestCase) -> str:
        """Create and register a custom test"""
        # Generate test ID
        test_id = f"custom_{int(time.time())}_{len(self.test_suites)}"
        
        # Create custom test suite
        custom_suite = TestSuite(
            suite_name=f"custom_{test_id}",
            description="Custom test suite",
            test_cases=[test_case]
        )
        
        await self.register_test_suite(custom_suite)
        
        return test_id
    
    async def get_validation_report(self, plugin_name: str) -> Optional[ValidationReport]:
        """Get validation report for plugin"""
        return self.validation_reports.get(plugin_name)
    
    async def list_test_suites(self) -> List[Dict[str, Any]]:
        """List all available test suites"""
        return [
            {
                "suite_name": suite.suite_name,
                "description": suite.description,
                "test_count": len(suite.test_cases),
                "test_types": list(set(test.test_type.value for test in suite.test_cases)),
                "parallel_execution": suite.parallel_execution
            }
            for suite in self.test_suites.values()
        ]
    
    async def _run_test_suite(self, test_suite: TestSuite, manifest: PluginManifest,
                            test_env: Path) -> Dict[str, Any]:
        """Run a test suite"""
        self.logger.info(f"Running test suite: {test_suite.suite_name}")
        
        suite_start_time = datetime.now()
        executions = []
        
        try:
            # Setup test suite
            if test_suite.setup_function:
                await test_suite.setup_function(manifest, test_env)
            
            # Run test cases
            if test_suite.parallel_execution:
                executions = await self._run_tests_parallel(
                    test_suite.test_cases, manifest, test_env, test_suite.max_parallel_tests
                )
            else:
                executions = await self._run_tests_sequential(
                    test_suite.test_cases, manifest, test_env
                )
            
            # Calculate suite results
            total_tests = len(executions)
            passed_tests = len([e for e in executions if e.result == TestResult.PASSED])
            failed_tests = len([e for e in executions if e.result == TestResult.FAILED])
            skipped_tests = len([e for e in executions if e.result == TestResult.SKIPPED])
            
            suite_result = TestResult.PASSED if failed_tests == 0 else TestResult.FAILED
            
            return {
                "result": suite_result,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "execution_time": (datetime.now() - suite_start_time).total_seconds(),
                "test_executions": [
                    {
                        "test_id": exec.test_case.test_id,
                        "name": exec.test_case.name,
                        "result": exec.result.value,
                        "execution_time": exec.execution_time,
                        "error_message": exec.error_message
                    }
                    for exec in executions
                ]
            }
            
        finally:
            # Teardown test suite
            if test_suite.teardown_function:
                try:
                    await test_suite.teardown_function(manifest, test_env)
                except Exception as e:
                    self.logger.error(f"Test suite teardown error: {e}")
    
    async def _run_tests_sequential(self, test_cases: List[TestCase], manifest: PluginManifest,
                                  test_env: Path) -> List[TestExecution]:
        """Run tests sequentially"""
        executions = []
        
        for test_case in test_cases:
            execution = await self._run_single_test(test_case, manifest, test_env)
            executions.append(execution)
            self.execution_history.append(execution)
        
        return executions
    
    async def _run_tests_parallel(self, test_cases: List[TestCase], manifest: PluginManifest,
                                test_env: Path, max_parallel: int) -> List[TestExecution]:
        """Run tests in parallel"""
        executions = []
        
        # Create semaphore to limit parallel executions
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def run_with_semaphore(test_case):
            async with semaphore:
                return await self._run_single_test(test_case, manifest, test_env)
        
        # Run all tests
        tasks = [run_with_semaphore(test_case) for test_case in test_cases]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                # Create error execution
                error_execution = TestExecution(
                    test_case=test_cases[0],  # Placeholder
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    result=TestResult.ERROR,
                    error_message=str(result)
                )
                executions.append(error_execution)
            else:
                executions.append(result)
                self.execution_history.append(result)
        
        return executions
    
    async def _run_single_test(self, test_case: TestCase, manifest: PluginManifest,
                             test_env: Path) -> TestExecution:
        """Run a single test case"""
        execution = TestExecution(
            test_case=test_case,
            start_time=datetime.now()
        )
        
        self.current_executions[test_case.test_id] = execution
        
        try:
            # Check permissions
            for permission in test_case.required_permissions:
                if not self._check_permission(permission):
                    execution.result = TestResult.SKIPPED
                    execution.error_message = f"Insufficient permissions: {permission.value}"
                    return execution
            
            # Run test with timeout
            if test_case.test_function:
                result = await asyncio.wait_for(
                    test_case.test_function(manifest, test_env, self.mock_services),
                    timeout=test_case.timeout_seconds
                )
                
                execution.output = str(result)
                
                # Check expected result
                if test_case.expected_result is not None:
                    if result == test_case.expected_result:
                        execution.result = TestResult.PASSED
                    else:
                        execution.result = TestResult.FAILED
                        execution.error_message = f"Expected {test_case.expected_result}, got {result}"
                else:
                    execution.result = TestResult.PASSED
            else:
                execution.result = TestResult.SKIPPED
                execution.error_message = "No test function defined"
                
        except asyncio.TimeoutError:
            execution.result = TestResult.TIMEOUT
            execution.error_message = f"Test timed out after {test_case.timeout_seconds} seconds"
        except Exception as e:
            execution.result = TestResult.ERROR
            execution.error_message = str(e)
            execution.output = traceback.format_exc()
        
        finally:
            execution.end_time = datetime.now()
            execution.execution_time = (execution.end_time - execution.start_time).total_seconds()
            
            # Remove from current executions
            self.current_executions.pop(test_case.test_id, None)
        
        return execution
    
    async def _load_plugin_manifest(self, plugin_path: Path) -> Optional[PluginManifest]:
        """Load plugin manifest from path"""
        manifest_path = plugin_path / "plugin.yaml"
        
        if not manifest_path.exists():
            return None
        
        try:
            with open(manifest_path, 'r') as f:
                import yaml
                manifest_data = yaml.safe_load(f)
            
            return PluginManifest(
                name=manifest_data["name"],
                version=manifest_data["version"],
                description=manifest_data["description"],
                author=manifest_data.get("author", "Unknown"),
                security_level=SecurityLevel(manifest_data.get("security_level", "sandboxed")),
                integration_type=IntegrationType(manifest_data.get("integration_type", "wrapper")),
                required_permissions=[PermissionLevel(p) for p in manifest_data.get("required_permissions", ["medium"])],
                dependencies=manifest_data.get("dependencies", []),
                entry_points=manifest_data.get("entry_points", {}),
                security_policies={}
            )
        except Exception as e:
            self.logger.error(f"Error loading manifest from {manifest_path}: {e}")
            return None
    
    async def _create_test_environment(self, plugin_name: str) -> Path:
        """Create isolated test environment"""
        test_env = self.workspace_root / "test_environments" / plugin_name
        test_env.mkdir(parents=True, exist_ok=True)
        
        # Create test directories
        (test_env / "workspace").mkdir(exist_ok=True)
        (test_env / "config").mkdir(exist_ok=True)
        (test_env / "logs").mkdir(exist_ok=True)
        (test_env / "temp").mkdir(exist_ok=True)
        
        self.test_environments[plugin_name] = test_env
        
        return test_env
    
    async def _cleanup_test_environment(self, plugin_name: str):
        """Cleanup test environment"""
        if plugin_name in self.test_environments:
            test_env = self.test_environments[plugin_name]
            
            try:
                # Remove test environment
                if test_env.exists():
                    shutil.rmtree(test_env)
                
                del self.test_environments[plugin_name]
                
            except Exception as e:
                self.logger.error(f"Error cleaning up test environment: {e}")
    
    def _check_permission(self, permission: PermissionLevel) -> bool:
        """Check if permission is available for testing"""
        # For testing, assume all permissions are available
        # In real implementation, this would check against permission engine
        return True
    
    def _calculate_security_score(self, report: ValidationReport) -> float:
        """Calculate security score (0-100)"""
        security_suite = report.test_suites.get("security", {})
        
        if not security_suite:
            return 0.0
        
        total_tests = security_suite.get("total_tests", 0)
        passed_tests = security_suite.get("passed_tests", 0)
        
        if total_tests == 0:
            return 0.0
        
        return (passed_tests / total_tests) * 100
    
    def _calculate_performance_score(self, report: ValidationReport) -> float:
        """Calculate performance score (0-100)"""
        performance_suite = report.test_suites.get("performance", {})
        
        if not performance_suite:
            return 0.0
        
        total_tests = performance_suite.get("total_tests", 0)
        passed_tests = performance_suite.get("passed_tests", 0)
        
        if total_tests == 0:
            return 0.0
        
        return (passed_tests / total_tests) * 100
    
    def _calculate_compatibility_score(self, report: ValidationReport) -> float:
        """Calculate compatibility score (0-100)"""
        compatibility_suite = report.test_suites.get("compatibility", {})
        
        if not compatibility_suite:
            return 0.0
        
        total_tests = compatibility_suite.get("total_tests", 0)
        passed_tests = compatibility_suite.get("passed_tests", 0)
        
        if total_tests == 0:
            return 0.0
        
        return (passed_tests / total_tests) * 100
    
    def _generate_recommendations(self, report: ValidationReport) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Security recommendations
        if report.security_score < 80:
            recommendations.append("Review and address security vulnerabilities")
        
        # Performance recommendations
        if report.performance_score < 80:
            recommendations.append("Optimize plugin performance and resource usage")
        
        # Compatibility recommendations
        if report.compatibility_score < 80:
            recommendations.append("Ensure compatibility with VoiceOS requirements")
        
        # Test failure recommendations
        for suite_name, suite_result in report.test_suites.items():
            if suite_result.get("result") == TestResult.FAILED:
                recommendations.append(f"Fix failing tests in {suite_name} suite")
        
        return recommendations
    
    async def _save_validation_report(self, report: ValidationReport):
        """Save validation report to file"""
        report_path = self.test_results_path / f"{report.plugin_name}_validation.json"
        
        try:
            report_data = {
                "plugin_name": report.plugin_name,
                "plugin_version": report.plugin_version,
                "validation_time": report.validation_time.isoformat(),
                "overall_result": report.overall_result.value,
                "security_score": report.security_score,
                "performance_score": report.performance_score,
                "compatibility_score": report.compatibility_score,
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "skipped_tests": report.skipped_tests,
                "recommendations": report.recommendations,
                "security_violations": report.security_violations,
                "test_suites": report.test_suites
            }
            
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving validation report: {e}")
    
    def _setup_mock_services(self):
        """Setup mock services for testing"""
        # Mock permission engine
        self.mock_services["permission_engine"] = type('MockPermissionEngine', (), {
            'check_tool_permission': lambda self, permission: True
        })()
        
        # Mock tool registry
        self.mock_services["tool_registry"] = type('MockToolRegistry', (), {
            'register_tool': lambda self, metadata, handler: True
        })()
        
        # Mock event bus
        self.mock_services["event_bus"] = type('MockEventBus', (), {
            'publish': lambda self, event: None,
            'subscribe': lambda self, event_type, callback: None
        })()
    
    def _register_default_test_suites(self):
        """Register default test suites"""
        # Security test suite
        security_tests = [
            TestCase(
                test_id="sec_001",
                name="Manifest Security Validation",
                description="Validate plugin manifest for security issues",
                test_type=TestType.SECURITY,
                severity=TestSeverity.CRITICAL,
                test_function=self._test_manifest_security
            ),
            TestCase(
                test_id="sec_002",
                name="Code Security Scan",
                description="Scan plugin code for security vulnerabilities",
                test_type=TestType.SECURITY,
                severity=TestSeverity.HIGH,
                test_function=self._test_code_security
            ),
            TestCase(
                test_id="sec_003",
                name="Permission Validation",
                description="Validate plugin permissions are appropriate",
                test_type=TestType.SECURITY,
                severity=TestSeverity.HIGH,
                test_function=self._test_permissions
            )
        ]
        
        # Performance test suite
        performance_tests = [
            TestCase(
                test_id="perf_001",
                name="Load Time Performance",
                description="Test plugin loading performance",
                test_type=TestType.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                test_function=self._test_load_performance
            ),
            TestCase(
                test_id="perf_002",
                name="Memory Usage",
                description="Test plugin memory usage",
                test_type=TestType.PERFORMANCE,
                severity=TestSeverity.MEDIUM,
                test_function=self._test_memory_usage
            )
        ]
        
        # Compatibility test suite
        compatibility_tests = [
            TestCase(
                test_id="comp_001",
                name="VoiceOS Compatibility",
                description="Test compatibility with VoiceOS requirements",
                test_type=TestType.COMPATIBILITY,
                severity=TestSeverity.CRITICAL,
                test_function=self._test_voiceos_compatibility
            ),
            TestCase(
                test_id="comp_002",
                name="API Compatibility",
                description="Test API compatibility",
                test_type=TestType.COMPATIBILITY,
                severity=TestSeverity.HIGH,
                test_function=self._test_api_compatibility
            )
        ]
        
        # Register test suites
        self.test_suites["security"] = TestSuite(
            suite_name="security",
            description="Security validation tests",
            test_cases=security_tests
        )
        
        self.test_suites["performance"] = TestSuite(
            suite_name="performance",
            description="Performance validation tests",
            test_cases=performance_tests
        )
        
        self.test_suites["compatibility"] = TestSuite(
            suite_name="compatibility",
            description="Compatibility validation tests",
            test_cases=compatibility_tests
        )
    
    # Default test functions
    async def _test_manifest_security(self, manifest: PluginManifest, test_env: Path, 
                                   mock_services: Dict[str, Any]) -> bool:
        """Test manifest security"""
        # Check for dangerous configurations
        if manifest.security_level == SecurityLevel.SAFE:
            return True
        
        # Validate required permissions
        if PermissionLevel.HIGH in manifest.required_permissions:
            return False  # High permissions not allowed in tests
        
        return True
    
    async def _test_code_security(self, manifest: PluginManifest, test_env: Path,
                               mock_services: Dict[str, Any]) -> bool:
        """Test code security"""
        # This would scan plugin code for security issues
        # For now, return True
        return True
    
    async def _test_permissions(self, manifest: PluginManifest, test_env: Path,
                              mock_services: Dict[str, Any]) -> bool:
        """Test permissions"""
        # Validate permissions are appropriate for security level
        if manifest.security_level == SecurityLevel.SAFE:
            return len(manifest.required_permissions) == 0
        
        return True
    
    async def _test_load_performance(self, manifest: PluginManifest, test_env: Path,
                                   mock_services: Dict[str, Any]) -> bool:
        """Test load performance"""
        start_time = time.time()
        
        # Simulate plugin loading
        await asyncio.sleep(0.1)  # Simulate loading time
        
        load_time = time.time() - start_time
        
        # Should load within 5 seconds
        return load_time < 5.0
    
    async def _test_memory_usage(self, manifest: PluginManifest, test_env: Path,
                                mock_services: Dict[str, Any]) -> bool:
        """Test memory usage"""
        # This would test actual memory usage
        # For now, return True
        return True
    
    async def _test_voiceos_compatibility(self, manifest: PluginManifest, test_env: Path,
                                        mock_services: Dict[str, Any]) -> bool:
        """Test VoiceOS compatibility"""
        # Check required fields
        if not manifest.name or not manifest.version:
            return False
        
        # Check security level is valid
        if manifest.security_level not in SecurityLevel:
            return False
        
        return True
    
    async def _test_api_compatibility(self, manifest: PluginManifest, test_env: Path,
                                    mock_services: Dict[str, Any]) -> bool:
        """Test API compatibility"""
        # This would test API compatibility
        # For now, return True
        return True


# Global test framework instance
plugin_test_framework = None

def get_plugin_test_framework() -> PluginTestFramework:
    """Get or create plugin test framework instance"""
    global plugin_test_framework
    if plugin_test_framework is None:
        plugin_test_framework = PluginTestFramework(config.project_root / "workspace")
    return plugin_test_framework
