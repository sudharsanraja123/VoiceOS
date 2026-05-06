"""
VoiceOS Plugin Monitoring and Metrics System

This module provides comprehensive monitoring and metrics collection for plugins
while maintaining VoiceOS security boundaries and architectural purity.
"""

import asyncio
import logging
import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque

from core.config import config
from permissions.permission_engine import PermissionLevel
from core.plugins.secure_plugin_integration import SecurityLevel, SecurityPolicy
from core.plugins.plugin_lifecycle import PluginState, PluginInstance


class MetricType(Enum):
    """Metric types"""
    COUNTER = "counter"           # Incrementing counter
    GAUGE = "gauge"              # Current value
    HISTOGRAM = "histogram"      # Distribution of values
    TIMER = "timer"              # Duration measurements
    RATE = "rate"                # Rate per time unit


class MetricCategory(Enum):
    """Metric categories"""
    PERFORMANCE = "performance"   # Performance metrics
    SECURITY = "security"         # Security-related metrics
    RESOURCE = "resource"         # Resource usage metrics
    ERROR = "error"               # Error metrics
    BUSINESS = "business"         # Business logic metrics
    SYSTEM = "system"             # System-level metrics


@dataclass
class MetricDefinition:
    """Metric definition"""
    name: str
    metric_type: MetricType
    category: MetricCategory
    description: str
    unit: str
    labels: List[str] = field(default_factory=list)
    aggregation_method: Optional[str] = None


@dataclass
class MetricValue:
    """Metric value with timestamp"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class PluginMetrics:
    """Plugin-specific metrics"""
    plugin_name: str
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
    total_plugins: int = 0
    active_plugins: int = 0
    total_operations: int = 0
    total_errors: int = 0
    system_memory_usage: float = 0.0
    system_cpu_usage: float = 0.0
    average_response_time: float = 0.0
    plugin_health_score: float = 0.0


class PluginMonitor:
    """
    Monitors plugin performance, resource usage, and health metrics.
    
    This class provides comprehensive monitoring while maintaining VoiceOS
    security boundaries and architectural purity.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.logger = logging.getLogger(__name__)
        
        # Metrics storage
        self.metrics_path = workspace_root / "metrics" / "plugin_metrics.json"
        self.metrics_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Metric definitions
        self.metric_definitions: Dict[str, MetricDefinition] = {}
        self._register_default_metrics()
        
        # Metrics storage
        self.plugin_metrics: Dict[str, PluginMetrics] = {}
        self.system_metrics = SystemMetrics()
        self.time_series_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_interval = 30.0  # seconds
        self.resource_monitoring_enabled = True
        
        # Monitoring tasks
        self._monitoring_task = None
        self._resource_monitor_task = None
        self._metrics_aggregation_task = None
        
        # Alert thresholds
        self.alert_thresholds = {
            "memory_usage_mb": 500,
            "cpu_usage_percent": 80,
            "error_rate_percent": 10,
            "response_time_seconds": 5.0,
            "security_violations": 5
        }
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # Process monitoring
        self.process_monitor = psutil.Process()
        self.plugin_processes: Dict[str, psutil.Process] = {}
    
    async def start_monitoring(self):
        """Start plugin monitoring"""
        self.logger.info("Starting plugin monitoring system...")
        
        # Load existing metrics
        await self._load_metrics()
        
        # Start monitoring tasks
        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._resource_monitor_task = asyncio.create_task(self._resource_monitoring_loop())
        self._metrics_aggregation_task = asyncio.create_task(self._metrics_aggregation_loop())
        
        self.logger.info("Plugin monitoring system started")
    
    async def stop_monitoring(self):
        """Stop plugin monitoring"""
        self.logger.info("Stopping plugin monitoring system...")
        
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
        
        self.logger.info("Plugin monitoring system stopped")
    
    async def register_plugin(self, plugin_name: str, plugin_instance: PluginInstance):
        """Register a plugin for monitoring"""
        if plugin_name not in self.plugin_metrics:
            self.plugin_metrics[plugin_name] = PluginMetrics(
                plugin_name=plugin_name,
                start_time=datetime.now()
            )
            
            self.logger.info(f"Registered plugin for monitoring: {plugin_name}")
    
    async def unregister_plugin(self, plugin_name: str):
        """Unregister a plugin from monitoring"""
        if plugin_name in self.plugin_metrics:
            # Calculate final uptime
            metrics = self.plugin_metrics[plugin_name]
            metrics.uptime = (datetime.now() - metrics.start_time).total_seconds()
            
            del self.plugin_metrics[plugin_name]
            
            self.logger.info(f"Unregistered plugin from monitoring: {plugin_name}")
    
    async def record_operation(self, plugin_name: str, operation: str,
                             execution_time: float, success: bool,
                             labels: Optional[Dict[str, str]] = None):
        """Record plugin operation metrics"""
        if plugin_name not in self.plugin_metrics:
            await self.register_plugin(plugin_name, None)
        
        metrics = self.plugin_metrics[plugin_name]
        
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
        metric_labels = labels or {}
        metric_labels.update({"plugin": plugin_name, "operation": operation})
        
        self._record_metric("operation_duration", execution_time, timestamp, metric_labels)
        self._record_metric("operation_success", 1.0 if success else 0.0, timestamp, metric_labels)
        self._record_metric("operation_count", 1.0, timestamp, metric_labels)
    
    async def record_resource_usage(self, plugin_name: str, memory_mb: float, cpu_percent: float):
        """Record plugin resource usage"""
        if plugin_name not in self.plugin_metrics:
            return
        
        metrics = self.plugin_metrics[plugin_name]
        
        # Update resource metrics
        metrics.current_memory_usage = memory_mb
        metrics.peak_memory_usage = max(metrics.peak_memory_usage, memory_mb)
        metrics.cpu_usage_total += cpu_percent
        
        # Record time series data
        timestamp = datetime.now()
        labels = {"plugin": plugin_name}
        
        self._record_metric("memory_usage_mb", memory_mb, timestamp, labels)
        self._record_metric("cpu_usage_percent", cpu_percent, timestamp, labels)
        
        # Check alert thresholds
        await self._check_resource_alerts(plugin_name, memory_mb, cpu_percent)
    
    async def record_security_event(self, plugin_name: str, event_type: str,
                                  severity: str, details: Dict[str, Any]):
        """Record security-related event"""
        if plugin_name not in self.plugin_metrics:
            await self.register_plugin(plugin_name, None)
        
        metrics = self.plugin_metrics[plugin_name]
        metrics.security_violations += 1
        
        # Record time series data
        timestamp = datetime.now()
        labels = {
            "plugin": plugin_name,
            "event_type": event_type,
            "severity": severity
        }
        
        self._record_metric("security_events", 1.0, timestamp, labels)
        
        # Check security alert threshold
        if metrics.security_violations >= self.alert_thresholds["security_violations"]:
            await self._emit_alert("security", plugin_name, f"Security violations threshold exceeded: {metrics.security_violations}")
    
    async def get_plugin_metrics(self, plugin_name: str, 
                                time_range_hours: int = 24) -> Dict[str, Any]:
        """Get metrics for a specific plugin"""
        if plugin_name not in self.plugin_metrics:
            return {"error": f"Plugin {plugin_name} not found"}
        
        metrics = self.plugin_metrics[plugin_name]
        
        # Calculate uptime
        current_uptime = (datetime.now() - metrics.start_time).total_seconds()
        
        # Calculate success rate
        success_rate = (metrics.successful_operations / metrics.total_operations * 100) if metrics.total_operations > 0 else 0
        
        # Calculate error rate
        error_rate = (metrics.failed_operations / metrics.total_operations * 100) if metrics.total_operations > 0 else 0
        
        # Get time series data
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        time_series = self._get_time_series_data(plugin_name, cutoff_time)
        
        return {
            "plugin_name": plugin_name,
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
            "security_violations": metrics.security_violations,
            "error_count": metrics.error_count,
            "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None,
            "time_series_data": time_series,
            "health_score": self._calculate_health_score(metrics)
        }
    
    async def get_system_metrics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get system-wide metrics"""
        # Update system metrics
        self._update_system_metrics()
        
        # Calculate system-wide statistics
        total_operations = sum(m.total_operations for m in self.plugin_metrics.values())
        total_errors = sum(m.error_count for m in self.plugin_metrics.values())
        
        # Calculate average response time
        avg_response_times = [m.average_execution_time for m in self.plugin_metrics.values() if m.total_operations > 0]
        avg_response_time = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0
        
        # Calculate plugin health score
        health_scores = [self._calculate_health_score(m) for m in self.plugin_metrics.values()]
        avg_health_score = sum(health_scores) / len(health_scores) if health_scores else 100
        
        # Get system resource usage
        system_memory = psutil.virtual_memory().percent
        system_cpu = psutil.cpu_percent()
        
        return {
            "total_plugins": len(self.plugin_metrics),
            "active_plugins": len([m for m in self.plugin_metrics.values() if m.last_activity and 
                                 (datetime.now() - m.last_activity).total_seconds() < 300]),
            "total_operations": total_operations,
            "total_errors": total_errors,
            "error_rate_percent": (total_errors / total_operations * 100) if total_operations > 0 else 0,
            "average_response_time_seconds": avg_response_time,
            "system_memory_usage_percent": system_memory,
            "system_cpu_usage_percent": system_cpu,
            "plugin_health_score": avg_health_score,
            "monitoring_active": self.monitoring_active,
            "metrics_collection_time": datetime.now().isoformat()
        }
    
    async def get_metric_definitions(self) -> List[Dict[str, Any]]:
        """Get all metric definitions"""
        return [
            {
                "name": defn.name,
                "type": defn.metric_type.value,
                "category": defn.category.value,
                "description": defn.description,
                "unit": defn.unit,
                "labels": defn.labels
            }
            for defn in self.metric_definitions.values()
        ]
    
    async def query_metrics(self, metric_name: str, plugin_name: Optional[str] = None,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          aggregation: Optional[str] = None) -> Dict[str, Any]:
        """Query metrics with filters and aggregation"""
        # Get time series data
        data = self.time_series_data.get(metric_name, deque())
        
        # Apply filters
        filtered_data = []
        for point in data:
            timestamp, value, labels = point
            
            # Time range filter
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            
            # Plugin filter
            if plugin_name and labels.get("plugin") != plugin_name:
                continue
            
            filtered_data.append({
                "timestamp": timestamp.isoformat(),
                "value": value,
                "labels": labels
            })
        
        # Apply aggregation
        if aggregation and filtered_data:
            values = [point["value"] for point in filtered_data]
            
            if aggregation == "avg":
                aggregated_value = sum(values) / len(values)
            elif aggregation == "sum":
                aggregated_value = sum(values)
            elif aggregation == "min":
                aggregated_value = min(values)
            elif aggregation == "max":
                aggregated_value = max(values)
            else:
                aggregated_value = None
            
            return {
                "metric_name": metric_name,
                "aggregation": aggregation,
                "aggregated_value": aggregated_value,
                "data_points": len(filtered_data),
                "data": filtered_data
            }
        else:
            return {
                "metric_name": metric_name,
                "data_points": len(filtered_data),
                "data": filtered_data
            }
    
    async def register_alert_callback(self, callback: Callable):
        """Register alert callback"""
        self.alert_callbacks.append(callback)
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """Set alert threshold for metric"""
        self.alert_thresholds[metric] = threshold
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(self.monitoring_interval)
                
                # Update system metrics
                self._update_system_metrics()
                
                # Check plugin health
                await self._check_plugin_health()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
    
    async def _resource_monitoring_loop(self):
        """Resource monitoring loop"""
        while self.monitoring_active and self.resource_monitoring_enabled:
            try:
                await asyncio.sleep(10)  # Resource monitoring every 10 seconds
                
                # Monitor system resources
                system_memory = psutil.virtual_memory()
                system_cpu = psutil.cpu_percent()
                
                self._record_metric("system_memory_percent", system_memory.percent, datetime.now(), {})
                self._record_metric("system_cpu_percent", system_cpu, datetime.now(), {})
                
                # Monitor plugin resources
                for plugin_name, metrics in self.plugin_metrics.items():
                    # This would get actual plugin resource usage
                    # For now, simulate with system metrics
                    await self.record_resource_usage(plugin_name, 50.0, 10.0)
                
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
    
    def _record_metric(self, metric_name: str, value: float, timestamp: datetime,
                       labels: Dict[str, str]):
        """Record metric value"""
        self.time_series_data[metric_name].append((timestamp, value, labels))
    
    def _get_time_series_data(self, plugin_name: str, cutoff_time: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """Get time series data for plugin"""
        plugin_data = {}
        
        for metric_name, data in self.time_series_data.items():
            metric_data = []
            
            for timestamp, value, labels in data:
                if labels.get("plugin") == plugin_name and timestamp >= cutoff_time:
                    metric_data.append({
                        "timestamp": timestamp.isoformat(),
                        "value": value,
                        "labels": labels
                    })
            
            if metric_data:
                plugin_data[metric_name] = metric_data
        
        return plugin_data
    
    def _update_system_metrics(self):
        """Update system-wide metrics"""
        self.system_metrics.total_plugins = len(self.plugin_metrics)
        self.system_metrics.active_plugins = len([
            m for m in self.plugin_metrics.values() 
            if m.last_activity and (datetime.now() - m.last_activity).total_seconds() < 300
        ])
        self.system_metrics.total_operations = sum(m.total_operations for m in self.plugin_metrics.values())
        self.system_metrics.total_errors = sum(m.error_count for m in self.plugin_metrics.values())
        
        # Calculate average response time
        avg_times = [m.average_execution_time for m in self.plugin_metrics.values() if m.total_operations > 0]
        self.system_metrics.average_response_time = sum(avg_times) / len(avg_times) if avg_times else 0
        
        # Calculate plugin health score
        health_scores = [self._calculate_health_score(m) for m in self.plugin_metrics.values()]
        self.system_metrics.plugin_health_score = sum(health_scores) / len(health_scores) if health_scores else 100
    
    def _calculate_health_score(self, metrics: PluginMetrics) -> float:
        """Calculate plugin health score (0-100)"""
        score = 100.0
        
        # Penalize high error rate
        if metrics.total_operations > 0:
            error_rate = metrics.failed_operations / metrics.total_operations
            score -= error_rate * 50  # Up to 50 points penalty
        
        # Penalize high memory usage
        if metrics.peak_memory_usage > 500:  # 500MB threshold
            score -= min((metrics.peak_memory_usage - 500) / 10, 30)  # Up to 30 points penalty
        
        # Penalize security violations
        score -= metrics.security_violations * 10  # 10 points per violation
        
        # Penalize long response times
        if metrics.average_execution_time > 5.0:  # 5 second threshold
            score -= min((metrics.average_execution_time - 5.0) * 5, 20)  # Up to 20 points penalty
        
        return max(0, score)
    
    async def _check_plugin_health(self):
        """Check plugin health and emit alerts"""
        for plugin_name, metrics in self.plugin_metrics.items():
            health_score = self._calculate_health_score(metrics)
            
            # Emit alert for low health score
            if health_score < 50:
                await self._emit_alert("health", plugin_name, f"Low health score: {health_score:.1f}")
            
            # Check for inactive plugins
            if metrics.last_activity:
                inactive_time = (datetime.now() - metrics.last_activity).total_seconds()
                if inactive_time > 3600:  # 1 hour
                    await self._emit_alert("inactivity", plugin_name, f"Plugin inactive for {inactive_time:.0f} seconds")
    
    async def _check_resource_alerts(self, plugin_name: str, memory_mb: float, cpu_percent: float):
        """Check resource usage alerts"""
        # Memory alert
        if memory_mb > self.alert_thresholds["memory_usage_mb"]:
            await self._emit_alert("resource", plugin_name, f"High memory usage: {memory_mb:.1f}MB")
        
        # CPU alert
        if cpu_percent > self.alert_thresholds["cpu_usage_percent"]:
            await self._emit_alert("resource", plugin_name, f"High CPU usage: {cpu_percent:.1f}%")
    
    async def _emit_alert(self, alert_type: str, plugin_name: str, message: str):
        """Emit alert to callbacks"""
        alert_data = {
            "type": alert_type,
            "plugin_name": plugin_name,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "severity": "warning"
        }
        
        self.logger.warning(f"Alert [{alert_type}] {plugin_name}: {message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
    
    def _register_default_metrics(self):
        """Register default metric definitions"""
        default_metrics = [
            MetricDefinition(
                name="operation_duration",
                metric_type=MetricType.TIMER,
                category=MetricCategory.PERFORMANCE,
                description="Duration of plugin operations",
                unit="seconds",
                labels=["plugin", "operation"]
            ),
            MetricDefinition(
                name="operation_success",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.BUSINESS,
                description="Success indicator for operations",
                unit="boolean",
                labels=["plugin", "operation"]
            ),
            MetricDefinition(
                name="memory_usage_mb",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.RESOURCE,
                description="Memory usage in MB",
                unit="megabytes",
                labels=["plugin"]
            ),
            MetricDefinition(
                name="cpu_usage_percent",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.RESOURCE,
                description="CPU usage percentage",
                unit="percent",
                labels=["plugin"]
            ),
            MetricDefinition(
                name="security_events",
                metric_type=MetricType.COUNTER,
                category=MetricCategory.SECURITY,
                description="Security-related events",
                unit="count",
                labels=["plugin", "event_type", "severity"]
            ),
            MetricDefinition(
                name="system_memory_percent",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="System memory usage percentage",
                unit="percent",
                labels=[]
            ),
            MetricDefinition(
                name="system_cpu_percent",
                metric_type=MetricType.GAUGE,
                category=MetricCategory.SYSTEM,
                description="System CPU usage percentage",
                unit="percent",
                labels=[]
            )
        ]
        
        for metric in default_metrics:
            self.metric_definitions[metric.name] = metric
    
    async def _load_metrics(self):
        """Load metrics from storage"""
        if self.metrics_path.exists():
            try:
                with open(self.metrics_path, 'r') as f:
                    data = json.load(f)
                
                # Load plugin metrics
                for plugin_data in data.get("plugin_metrics", []):
                    plugin_name = plugin_data["plugin_name"]
                    metrics = PluginMetrics(
                        plugin_name=plugin_name,
                        start_time=datetime.fromisoformat(plugin_data["start_time"]),
                        total_operations=plugin_data.get("total_operations", 0),
                        successful_operations=plugin_data.get("successful_operations", 0),
                        failed_operations=plugin_data.get("failed_operations", 0),
                        average_execution_time=plugin_data.get("average_execution_time", 0.0),
                        peak_memory_usage=plugin_data.get("peak_memory_usage", 0.0),
                        current_memory_usage=plugin_data.get("current_memory_usage", 0.0),
                        cpu_usage_total=plugin_data.get("cpu_usage_total", 0.0),
                        security_violations=plugin_data.get("security_violations", 0),
                        error_count=plugin_data.get("error_count", 0),
                        last_activity=datetime.fromisoformat(plugin_data["last_activity"]) if plugin_data.get("last_activity") else None,
                        uptime=plugin_data.get("uptime", 0.0)
                    )
                    self.plugin_metrics[plugin_name] = metrics
                
                self.logger.info(f"Loaded metrics for {len(self.plugin_metrics)} plugins")
                
            except Exception as e:
                self.logger.error(f"Error loading metrics: {e}")
    
    async def _save_metrics(self):
        """Save metrics to storage"""
        try:
            data = {
                "plugin_metrics": [
                    {
                        "plugin_name": metrics.plugin_name,
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
                        "last_activity": metrics.last_activity.isoformat() if metrics.last_activity else None,
                        "uptime": metrics.uptime
                    }
                    for metrics in self.plugin_metrics.values()
                ],
                "system_metrics": {
                    "total_plugins": self.system_metrics.total_plugins,
                    "active_plugins": self.system_metrics.active_plugins,
                    "total_operations": self.system_metrics.total_operations,
                    "total_errors": self.system_metrics.total_errors,
                    "system_memory_usage": self.system_metrics.system_memory_usage,
                    "system_cpu_usage": self.system_metrics.system_cpu_usage,
                    "average_response_time": self.system_metrics.average_response_time,
                    "plugin_health_score": self.system_metrics.plugin_health_score
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
plugin_monitor = None

def get_plugin_monitor() -> PluginMonitor:
    """Get or create plugin monitor instance"""
    global plugin_monitor
    if plugin_monitor is None:
        plugin_monitor = PluginMonitor(config.project_root / "workspace")
    return plugin_monitor
