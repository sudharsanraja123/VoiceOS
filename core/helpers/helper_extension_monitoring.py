"""
VoiceOS Helper and Extension Monitoring System

This module provides comprehensive monitoring for helpers and extensions
while maintaining VoiceOS security boundaries and architectural purity.
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque

from core.config import config
from core.helpers.secure_helper_integration import get_secure_helper_adapter, HelperCategory
from core.extensions.secure_extension_integration import get_secure_extension_manager, ExtensionType
from core.helpers.helper_bridge_integration import get_helper_bridge_manager
from core.extensions.extension_point_system import get_extension_point_system


class MonitoringMetricType(Enum):
    """Monitoring metric types"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class ComponentType(Enum):
    """Component types"""
    HELPER = "helper"
    EXTENSION = "extension"
    BRIDGE = "bridge"
    EXTENSION_POINT = "extension_point"


@dataclass
class ComponentMetrics:
    """Metrics for a component"""
    component_name: str
    component_type: ComponentType
    start_time: datetime
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_execution_time: float = 0.0
    peak_memory_usage: float = 0.0
    current_memory_usage: float = 0.0
    cpu_usage_total: float = 0.0
    security_violations: int = 0
    error_count: int = 0
    last_activity: Optional[datetime] = None
    uptime: float = 0.0


@dataclass
class SystemMetrics:
    """System-wide metrics"""
    total_helpers: int = 0
    active_helpers: int = 0
    total_extensions: int = 0
    active_extensions: int = 0
    total_bridges: int = 0
    active_bridges: int = 0
    total_extension_points: int = 0
    active_hooks: int = 0
    total_operations: int = 0
    total_errors: int = 0
    system_memory_usage: float = 0.0
    system_cpu_usage: float = 0.0
    average_response_time: float = 0.0
    component_health_score: float = 0.0


class HelperExtensionMonitor:
    """
    Monitors helpers, extensions, bridges, and extension points.
    
    This class provides comprehensive monitoring while maintaining VoiceOS
    security boundaries and architectural purity.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics_path = workspace_root / "metrics" / "helper_extension_metrics.json"
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Component metrics
        self.helper_metrics: Dict[str, ComponentMetrics] = {}
        self.extension_metrics: Dict[str, ComponentMetrics] = {}
        self.bridge_metrics: Dict[str, ComponentMetrics] = {}
        self.extension_point_metrics: Dict[str, ComponentMetrics] = {}
        
        # System metrics
        self.system_metrics = SystemMetrics()
        
        # Time series data
        self.time_series_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_interval = 30.0  # seconds
        
        # Monitoring tasks
        self._monitoring_task = None
        self._resource_monitor_task = None
        self._metrics_aggregation_task = None
        
        # Alert thresholds
        self.alert_thresholds = {
            "memory_usage_mb": 200,
            "cpu_usage_percent": 70,
            "error_rate_percent": 15,
            "response_time_seconds": 3.0,
            "security_violations": 3
        }
        
        # Alert callbacks
        self.alert_callbacks: List[callable] = []
        
        # Component managers
        self.helper_adapter = get_secure_helper_adapter()
        self.extension_manager = get_secure_extension_manager()
        self.bridge_manager = None  # Will be set when tool registry is available
        self.extension_point_system = get_extension_point_system()
    
    async def start_monitoring(self, tool_registry=None):
        """Start monitoring system"""
        self.logger.info("Starting helper and extension monitoring system...")
        
        # Initialize bridge manager if tool registry provided
        if tool_registry:
            self.bridge_manager = get_helper_bridge_manager(tool_registry)
        
        # Load existing metrics
        await self._load_metrics()
        
        # Initialize component metrics
        await self._initialize_component_metrics()
        
        # Start monitoring tasks
        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._resource_monitor_task = asyncio.create_task(self._resource_monitoring_loop())
        self._metrics_aggregation_task = asyncio.create_task(self._metrics_aggregation_loop())
        
        self.logger.info("Helper and extension monitoring system started")
    
    async def stop_monitoring(self):
        """Stop monitoring system"""
        self.logger.info("Stopping helper and extension monitoring system...")
        
        self.monitoring_active = False
        
        # Cancel monitoring tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._resource_monitor_task:
            self._resource_monitor_task.cancel()
        if self._metrics_aggregation_task:
            self._metrics_aggregation_task.cancel()
        
        # Save metrics
        await self._save_metrics()
        
        self.logger.info("Helper and extension monitoring system stopped")
    
    async def record_helper_operation(self, helper_name: str, function_name: str,
                                   execution_time: float, success: bool,
                                   memory_usage: float = 0.0, cpu_usage: float = 0.0):
        """Record helper operation metrics"""
        if helper_name not in self.helper_metrics:
            await self._register_helper_metrics(helper_name)
        
        metrics = self.helper_metrics[helper_name]
        
        # Update operation counters
        metrics.total_operations += 1
        if success:
            metrics.successful_operations += 1
        else:
            metrics.failed_operations += 1
            metrics.error_count += 1
        
        # Update execution time
        if metrics.total_operations == 1:
            metrics.average_execution_time = execution_time
        else:
            metrics.average_execution_time = (
                (metrics.average_execution_time * (metrics.total_operations - 1) + execution_time) /
                metrics.total_operations
            )
        
        # Update resource usage
        metrics.current_memory_usage = memory_usage
        metrics.peak_memory_usage = max(metrics.peak_memory_usage, memory_usage)
        metrics.cpu_usage_total += cpu_usage
        
        # Update last activity
        metrics.last_activity = datetime.now()
        
        # Record time series data
        timestamp = datetime.now()
        labels = {"helper": helper_name, "function": function_name}
        
        self._record_metric("helper_operation_duration", execution_time, timestamp, labels)
        self._record_metric("helper_operation_success", 1.0 if success else 0.0, timestamp, labels)
        self._record_metric("helper_memory_usage", memory_usage, timestamp, labels)
        self._record_metric("helper_cpu_usage", cpu_usage, timestamp, labels)
    
    async def record_extension_operation(self, extension_name: str, operation: str,
                                       execution_time: float, success: bool,
                                       memory_usage: float = 0.0, cpu_usage: float = 0.0):
        """Record extension operation metrics"""
        if extension_name not in self.extension_metrics:
            await self._register_extension_metrics(extension_name)
        
        metrics = self.extension_metrics[extension_name]
        
        # Update operation counters
        metrics.total_operations += 1
        if success:
            metrics.successful_operations += 1
        else:
            metrics.failed_operations += 1
            metrics.error_count += 1
        
        # Update execution time
        if metrics.total_operations == 1:
            metrics.average_execution_time = execution_time
        else:
            metrics.average_execution_time = (
                (metrics.average_execution_time * (metrics.total_operations - 1) + execution_time) /
                metrics.total_operations
            )
        
        # Update resource usage
        metrics.current_memory_usage = memory_usage
        metrics.peak_memory_usage = max(metrics.peak_memory_usage, memory_usage)
        metrics.cpu_usage_total += cpu_usage
        
        # Update last activity
        metrics.last_activity = datetime.now()
        
        # Record time series data
        timestamp = datetime.now()
        labels = {"extension": extension_name, "operation": operation}
        
        self._record_metric("extension_operation_duration", execution_time, timestamp, labels)
        self._record_metric("extension_operation_success", 1.0 if success else 0.0, timestamp, labels)
        self._record_metric("extension_memory_usage", memory_usage, timestamp, labels)
        self._record_metric("extension_cpu_usage", cpu_usage, timestamp, labels)
    
    async def record_bridge_operation(self, bridge_id: str, execution_time: float, success: bool):
        """Record bridge operation metrics"""
        if bridge_id not in self.bridge_metrics:
            await self._register_bridge_metrics(bridge_id)
        
        metrics = self.bridge_metrics[bridge_id]
        
        # Update operation counters
        metrics.total_operations += 1
        if success:
            metrics.successful_operations += 1
        else:
            metrics.failed_operations += 1
            metrics.error_count += 1
        
        # Update execution time
        if metrics.total_operations == 1:
            metrics.average_execution_time = execution_time
        else:
            metrics.average_execution_time = (
                (metrics.average_execution_time * (metrics.total_operations - 1) + execution_time) /
                metrics.total_operations
            )
        
        # Update last activity
        metrics.last_activity = datetime.now()
        
        # Record time series data
        timestamp = datetime.now()
        labels = {"bridge": bridge_id}
        
        self._record_metric("bridge_operation_duration", execution_time, timestamp, labels)
        self._record_metric("bridge_operation_success", 1.0 if success else 0.0, timestamp, labels)
    
    async def record_extension_point_execution(self, point_name: str, execution_time: float,
                                             hooks_executed: int, success: bool):
        """Record extension point execution metrics"""
        if point_name not in self.extension_point_metrics:
            await self._register_extension_point_metrics(point_name)
        
        metrics = self.extension_point_metrics[point_name]
        
        # Update operation counters
        metrics.total_operations += 1
        if success:
            metrics.successful_operations += 1
        else:
            metrics.failed_operations += 1
            metrics.error_count += 1
        
        # Update execution time
        if metrics.total_operations == 1:
            metrics.average_execution_time = execution_time
        else:
            metrics.average_execution_time = (
                (metrics.average_execution_time * (metrics.total_operations - 1) + execution_time) /
                metrics.total_operations
            )
        
        # Update last activity
        metrics.last_activity = datetime.now()
        
        # Record time series data
        timestamp = datetime.now()
        labels = {"extension_point": point_name}
        
        self._record_metric("extension_point_duration", execution_time, timestamp, labels)
        self._record_metric("extension_point_hooks_executed", hooks_executed, timestamp, labels)
        self._record_metric("extension_point_success", 1.0 if success else 0.0, timestamp, labels)
    
    async def get_helper_metrics(self, helper_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific helper"""
        if helper_name not in self.helper_metrics:
            return None
        
        metrics = self.helper_metrics[helper_name]
        
        # Calculate uptime
        current_uptime = (datetime.now() - metrics.start_time).total_seconds()
        
        # Calculate success rate
        success_rate = (metrics.successful_operations / metrics.total_operations * 100) if metrics.total_operations > 0 else 0
        
        # Calculate error rate
        error_rate = (metrics.failed_operations / metrics.total_operations * 100) if metrics.total_operations > 0 else 0
        
        return {
            "helper_name": helper_name,
            "uptime_seconds": current_uptime,
            "total_operations": metrics.total_operations,
            "successful_operations": metrics.successful_operations,
            "failed_operations": metrics.failed_operations,
            "success_rate_percent": success_rate,
            "error_rate_percent": error_rate,
            "average_execution_time": metrics.average_execution_time,
            "peak_memory_usage_mb": metrics.peak_memory_usage,
            "current_memory_usage_mb": metrics.current_memory_usage,
            "cpu_usage_total": metrics.cpu_usage_total,
            "error_count": metrics.error_count,
            "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None,
            "health_score": self._calculate_health_score(metrics)
        }
    
    async def get_extension_metrics(self, extension_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific extension"""
        if extension_name not in self.extension_metrics:
            return None
        
        metrics = self.extension_metrics[extension_name]
        
        # Calculate uptime
        current_uptime = (datetime.now() - metrics.start_time).total_seconds()
        
        # Calculate success rate
        success_rate = (metrics.successful_operations / metrics.total_operations * 100) if metrics.total_operations > 0 else 0
        
        # Calculate error rate
        error_rate = (metrics.failed_operations / metrics.total_operations * 100) if metrics.total_operations > 0 else 0
        
        return {
            "extension_name": extension_name,
            "uptime_seconds": current_uptime,
            "total_operations": metrics.total_operations,
            "successful_operations": metrics.successful_operations,
            "failed_operations": metrics.failed_operations,
            "success_rate_percent": success_rate,
            "error_rate_percent": error_rate,
            "average_execution_time": metrics.average_execution_time,
            "peak_memory_usage_mb": metrics.peak_memory_usage,
            "current_memory_usage_mb": metrics.current_memory_usage,
            "cpu_usage_total": metrics.cpu_usage_total,
            "error_count": metrics.error_count,
            "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None,
            "health_score": self._calculate_health_score(metrics)
        }
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics"""
        # Update system metrics
        await self._update_system_metrics()
        
        return {
            "helpers": {
                "total_helpers": self.system_metrics.total_helpers,
                "active_helpers": self.system_metrics.active_helpers,
                "total_operations": sum(m.total_operations for m in self.helper_metrics.values()),
                "total_errors": sum(m.error_count for m in self.helper_metrics.values()),
                "average_response_time": (
                    sum(m.average_execution_time for m in self.helper_metrics.values() if m.total_operations > 0) /
                    len([m for m in self.helper_metrics.values() if m.total_operations > 0])
                    if self.helper_metrics else 0
                )
            },
            "extensions": {
                "total_extensions": self.system_metrics.total_extensions,
                "active_extensions": self.system_metrics.active_extensions,
                "total_operations": sum(m.total_operations for m in self.extension_metrics.values()),
                "total_errors": sum(m.error_count for m in self.extension_metrics.values()),
                "average_response_time": (
                    sum(m.average_execution_time for m in self.extension_metrics.values() if m.total_operations > 0) /
                    len([m for m in self.extension_metrics.values() if m.total_operations > 0])
                    if self.extension_metrics else 0
                )
            },
            "bridges": {
                "total_bridges": self.system_metrics.total_bridges,
                "active_bridges": self.system_metrics.active_bridges,
                "total_operations": sum(m.total_operations for m in self.bridge_metrics.values()),
                "total_errors": sum(m.error_count for m in self.bridge_metrics.values()),
                "average_response_time": (
                    sum(m.average_execution_time for m in self.bridge_metrics.values() if m.total_operations > 0) /
                    len([m for m in self.bridge_metrics.values() if m.total_operations > 0])
                    if self.bridge_metrics else 0
                )
            },
            "extension_points": {
                "total_extension_points": self.system_metrics.total_extension_points,
                "active_hooks": self.system_metrics.active_hooks,
                "total_executions": sum(m.total_operations for m in self.extension_point_metrics.values()),
                "total_errors": sum(m.error_count for m in self.extension_point_metrics.values()),
                "average_execution_time": (
                    sum(m.average_execution_time for m in self.extension_point_metrics.values() if m.total_operations > 0) /
                    len([m for m in self.extension_point_metrics.values() if m.total_operations > 0])
                    if self.extension_point_metrics else 0
                )
            },
            "system": {
                "system_memory_usage_percent": self.system_metrics.system_memory_usage,
                "system_cpu_usage_percent": self.system_metrics.system_cpu_usage,
                "component_health_score": self.system_metrics.component_health_score,
                "monitoring_active": self.monitoring_active
            }
        }
    
    async def _initialize_component_metrics(self):
        """Initialize metrics for all components"""
        # Initialize helper metrics
        registered_helpers = self.helper_adapter.get_registered_helpers()
        for helper in registered_helpers:
            await self._register_helper_metrics(helper["name"])
        
        # Initialize extension metrics
        registered_extensions = self.extension_manager.get_registered_extensions()
        for extension in registered_extensions:
            await self._register_extension_metrics(extension["name"])
        
        # Initialize bridge metrics
        if self.bridge_manager:
            bridges = self.bridge_manager.get_bridges()
            for bridge in bridges:
                await self._register_bridge_metrics(bridge["bridge_id"])
        
        # Initialize extension point metrics
        extension_points = self.extension_point_system.get_system_status()
        for point_name in extension_points["extension_points"]:
            await self._register_extension_point_metrics(point_name)
    
    async def _register_helper_metrics(self, helper_name: str):
        """Register metrics for a helper"""
        if helper_name not in self.helper_metrics:
            self.helper_metrics[helper_name] = ComponentMetrics(
                component_name=helper_name,
                component_type=ComponentType.HELPER,
                start_time=datetime.now()
            )
    
    async def _register_extension_metrics(self, extension_name: str):
        """Register metrics for an extension"""
        if extension_name not in self.extension_metrics:
            self.extension_metrics[extension_name] = ComponentMetrics(
                component_name=extension_name,
                component_type=ComponentType.EXTENSION,
                start_time=datetime.now()
            )
    
    async def _register_bridge_metrics(self, bridge_id: str):
        """Register metrics for a bridge"""
        if bridge_id not in self.bridge_metrics:
            self.bridge_metrics[bridge_id] = ComponentMetrics(
                component_name=bridge_id,
                component_type=ComponentType.BRIDGE,
                start_time=datetime.now()
            )
    
    async def _register_extension_point_metrics(self, point_name: str):
        """Register metrics for an extension point"""
        if point_name not in self.extension_point_metrics:
            self.extension_point_metrics[point_name] = ComponentMetrics(
                component_name=point_name,
                component_type=ComponentType.EXTENSION_POINT,
                start_time=datetime.now()
            )
    
    def _record_metric(self, metric_name: str, value: float, timestamp: datetime,
                       labels: Dict[str, str]):
        """Record metric value"""
        self.time_series_data[metric_name].append((timestamp, value, labels))
    
    def _calculate_health_score(self, metrics: ComponentMetrics) -> float:
        """Calculate component health score (0-100)"""
        score = 100.0
        
        # Penalize high error rate
        if metrics.total_operations > 0:
            error_rate = metrics.failed_operations / metrics.total_operations
            score -= error_rate * 50  # Up to 50 points penalty
        
        # Penalize high memory usage
        if metrics.peak_memory_usage > 200:  # 200MB threshold
            score -= min((metrics.peak_memory_usage - 200) / 10, 30)  # Up to 30 points penalty
        
        # Penalize security violations
        score -= metrics.security_violations * 15  # 15 points per violation
        
        # Penalize long response times
        if metrics.average_execution_time > 3.0:  # 3 second threshold
            score -= min((metrics.average_execution_time - 3.0) * 10, 20)  # Up to 20 points penalty
        
        return max(0, score)
    
    async def _update_system_metrics(self):
        """Update system-wide metrics"""
        # Update component counts
        self.system_metrics.total_helpers = len(self.helper_metrics)
        self.system_metrics.active_helpers = len([
            m for m in self.helper_metrics.values()
            if m.last_activity and (datetime.now() - m.last_activity).total_seconds() < 300
        ])
        
        self.system_metrics.total_extensions = len(self.extension_metrics)
        self.system_metrics.active_extensions = len([
            m for m in self.extension_metrics.values()
            if m.last_activity and (datetime.now() - m.last_activity).total_seconds() < 300
        ])
        
        self.system_metrics.total_bridges = len(self.bridge_metrics)
        self.system_metrics.active_bridges = len([
            m for m in self.bridge_metrics.values()
            if m.last_activity and (datetime.now() - m.last_activity).total_seconds() < 300
        ])
        
        self.system_metrics.total_extension_points = len(self.extension_point_metrics)
        self.system_metrics.active_hooks = sum(
            len([h for h in self.extension_point_system.extension_points[point].values() if h.enabled])
            for point in self.extension_point_system.extension_points
        )
        
        # Calculate total operations and errors
        self.system_metrics.total_operations = (
            sum(m.total_operations for m in self.helper_metrics.values()) +
            sum(m.total_operations for m in self.extension_metrics.values()) +
            sum(m.total_operations for m in self.bridge_metrics.values()) +
            sum(m.total_operations for m in self.extension_point_metrics.values())
        )
        
        self.system_metrics.total_errors = (
            sum(m.error_count for m in self.helper_metrics.values()) +
            sum(m.error_count for m in self.extension_metrics.values()) +
            sum(m.error_count for m in self.bridge_metrics.values()) +
            sum(m.error_count for m in self.extension_point_metrics.values())
        )
        
        # Calculate average response time
        all_response_times = []
        for metrics_dict in [self.helper_metrics, self.extension_metrics, self.bridge_metrics, self.extension_point_metrics]:
            for metrics in metrics_dict.values():
                if metrics.total_operations > 0:
                    all_response_times.append(metrics.average_execution_time)
        
        self.system_metrics.average_response_time = (
            sum(all_response_times) / len(all_response_times) if all_response_times else 0
        )
        
        # Calculate component health score
        all_health_scores = []
        for metrics_dict in [self.helper_metrics, self.extension_metrics, self.bridge_metrics, self.extension_point_metrics]:
            for metrics in metrics_dict.values():
                all_health_scores.append(self._calculate_health_score(metrics))
        
        self.system_metrics.component_health_score = (
            sum(all_health_scores) / len(all_health_scores) if all_health_scores else 100
        )
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(self.monitoring_interval)
                
                # Update system metrics
                await self._update_system_metrics()
                
                # Check component health
                await self._check_component_health()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
    
    async def _resource_monitoring_loop(self):
        """Resource monitoring loop"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(10)  # Resource monitoring every 10 seconds
                
                # Monitor system resources
                system_memory = psutil.virtual_memory()
                system_cpu = psutil.cpu_percent()
                
                self.system_metrics.system_memory_usage = system_memory.percent
                self.system_metrics.system_cpu_usage = system_cpu
                
                # Record system metrics
                timestamp = datetime.now()
                self._record_metric("system_memory_percent", system_memory.percent, timestamp, {})
                self._record_metric("system_cpu_percent", system_cpu, timestamp, {})
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
    
    async def _metrics_aggregation_loop(self):
        """Metrics aggregation loop"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(300)  # Aggregate every 5 minutes
                
                # Save aggregated metrics
                await self._save_metrics()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics aggregation error: {e}")
    
    async def _check_component_health(self):
        """Check component health and emit alerts"""
        # Check helpers
        for helper_name, metrics in self.helper_metrics.items():
            health_score = self._calculate_health_score(metrics)
            
            if health_score < 60:
                await self._emit_alert("health", "helper", helper_name, f"Low health score: {health_score:.1f}")
            
            # Check resource usage
            if metrics.current_memory_usage > self.alert_thresholds["memory_usage_mb"]:
                await self._emit_alert("resource", "helper", helper_name, f"High memory usage: {metrics.current_memory_usage:.1f}MB")
        
        # Check extensions
        for extension_name, metrics in self.extension_metrics.items():
            health_score = self._calculate_health_score(metrics)
            
            if health_score < 60:
                await self._emit_alert("health", "extension", extension_name, f"Low health score: {health_score:.1f}")
    
    async def _emit_alert(self, alert_type: str, component_type: str, component_name: str, message: str):
        """Emit alert to callbacks"""
        alert_data = {
            "type": alert_type,
            "component_type": component_type,
            "component_name": component_name,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "severity": "warning"
        }
        
        self.logger.warning(f"Alert [{alert_type}] {component_type} {component_name}: {message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
    
    async def _load_metrics(self):
        """Load metrics from storage"""
        if self.metrics_path.exists():
            try:
                with open(self.metrics_path, 'r') as f:
                    data = json.load(f)
                
                # Load component metrics (simplified)
                for component_data in data.get("helper_metrics", []):
                    helper_name = component_data["component_name"]
                    self.helper_metrics[helper_name] = ComponentMetrics(
                        component_name=helper_name,
                        component_type=ComponentType.HELPER,
                        start_time=datetime.fromisoformat(component_data["start_time"]),
                        total_operations=component_data.get("total_operations", 0),
                        successful_operations=component_data.get("successful_operations", 0),
                        failed_operations=component_data.get("failed_operations", 0),
                        average_execution_time=component_data.get("average_execution_time", 0.0),
                        peak_memory_usage=component_data.get("peak_memory_usage", 0.0),
                        current_memory_usage=component_data.get("current_memory_usage", 0.0),
                        cpu_usage_total=component_data.get("cpu_usage_total", 0.0),
                        security_violations=component_data.get("security_violations", 0),
                        error_count=component_data.get("error_count", 0),
                        last_activity=datetime.fromisoformat(component_data["last_activity"]) if component_data.get("last_activity") else None
                    )
                
                self.logger.info(f"Loaded metrics for {len(self.helper_metrics)} helpers")
                
            except Exception as e:
                self.logger.error(f"Error loading metrics: {e}")
    
    async def _save_metrics(self):
        """Save metrics to storage"""
        try:
            data = {
                "helper_metrics": [
                    {
                        "component_name": metrics.component_name,
                        "component_type": metrics.component_type.value,
                        "start_time": metrics.start_time.isoformat(),
                        "total_operations": metrics.total_operations,
                        "successful_operations": metrics.successful_operations,
                        "failed_operations": metrics.failed_operations,
                        "average_execution_time": metrics.average_execution_time,
                        "peak_memory_usage": metrics.peak_memory_usage,
                        "current_memory_usage": metrics.current_memory_usage,
                        "cpu_usage_total": metrics.cpu_usage_total,
                        "security_violations": metrics.security_violations,
                        "error_count": metrics.error_count,
                        "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None
                    }
                    for metrics in self.helper_metrics.values()
                ],
                "extension_metrics": [
                    {
                        "component_name": metrics.component_name,
                        "component_type": metrics.component_type.value,
                        "start_time": metrics.start_time.isoformat(),
                        "total_operations": metrics.total_operations,
                        "successful_operations": metrics.successful_operations,
                        "failed_operations": metrics.failed_operations,
                        "average_execution_time": metrics.average_execution_time,
                        "peak_memory_usage": metrics.peak_memory_usage,
                        "current_memory_usage": metrics.current_memory_usage,
                        "cpu_usage_total": metrics.cpu_usage_total,
                        "security_violations": metrics.security_violations,
                        "error_count": metrics.error_count,
                        "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None
                    }
                    for metrics in self.extension_metrics.values()
                ],
                "system_metrics": {
                    "total_helpers": self.system_metrics.total_helpers,
                    "active_helpers": self.system_metrics.active_helpers,
                    "total_extensions": self.system_metrics.total_extensions,
                    "active_extensions": self.system_metrics.active_extensions,
                    "total_bridges": self.system_metrics.total_bridges,
                    "active_bridges": self.system_metrics.active_bridges,
                    "total_extension_points": self.system_metrics.total_extension_points,
                    "active_hooks": self.system_metrics.active_hooks,
                    "total_operations": self.system_metrics.total_operations,
                    "total_errors": self.system_metrics.total_errors,
                    "system_memory_usage": self.system_metrics.system_memory_usage,
                    "system_cpu_usage": self.system_metrics.system_cpu_usage,
                    "average_response_time": self.system_metrics.average_response_time,
                    "component_health_score": self.system_metrics.component_health_score
                },
                "metadata": {
                    "last_saved": datetime.now().isoformat(),
                    "monitoring_active": self.monitoring_active
                }
            }
            
            with open(self.metrics_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")


# Global monitor instance
helper_extension_monitor = None

def get_helper_extension_monitor() -> HelperExtensionMonitor:
    """Get or create helper extension monitor instance"""
    global helper_extension_monitor
    if helper_extension_monitor is None:
        helper_extension_monitor = HelperExtensionMonitor(config.project_root / "workspace")
    return helper_extension_monitor
