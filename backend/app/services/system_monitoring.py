"""System Monitoring Service for STORY-005: System Monitoring

This module provides services for:
- System metrics collection (CPU, memory, disk)
- Database performance monitoring
- Application performance tracking
- Health check execution
- Threshold-based alerting

Python 3.5+ compatible
"""

import logging
import psutil
import socket
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.system_monitoring import (
    SystemMetric, DatabaseMetric, ApplicationMetric,
    HealthCheckResult, MonitoringThreshold,
    MetricType, MetricUnit,
)
from app.models.system_alerts import SystemAlert, AlertSeverity, AlertStatus


logger = logging.getLogger(__name__)


class MetricsCollectionService(object):
    """Service for collecting system metrics"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.hostname = socket.gethostname()

    async def collect_system_metrics(self) -> List[SystemMetric]:
        """Collect current system metrics

        Returns:
            List of SystemMetric instances
        """
        import uuid
        timestamp = datetime.utcnow()
        metrics = []

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(self._create_metric(
            metric_name="cpu.usage",
            metric_value=cpu_percent,
            metric_unit=MetricUnit.PERCENT,
            tags={"type": "cpu", "host": self.hostname},
            timestamp=timestamp,
        ))

        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.append(self._create_metric(
            metric_name="memory.usage",
            metric_value=memory.percent,
            metric_unit=MetricUnit.PERCENT,
            tags={"type": "memory", "host": self.hostname},
            timestamp=timestamp,
        ))
        metrics.append(self._create_metric(
            metric_name="memory.available",
            metric_value=memory.available,
            metric_unit=MetricUnit.BYTES,
            tags={"type": "memory", "host": self.hostname},
            timestamp=timestamp,
        ))

        # Disk metrics
        disk = psutil.disk_usage("/")
        metrics.append(self._create_metric(
            metric_name="disk.usage",
            metric_value=disk.percent,
            metric_unit=MetricUnit.PERCENT,
            tags={"type": "disk", "host": self.hostname, "path": "/"},
            timestamp=timestamp,
        ))
        metrics.append(self._create_metric(
            metric_name="disk.free",
            metric_value=disk.free,
            metric_unit=MetricUnit.BYTES,
            tags={"type": "disk", "host": self.hostname, "path": "/"},
            timestamp=timestamp,
        ))

        # Network metrics
        net_io = psutil.net_io_counters()
        metrics.append(self._create_metric(
            metric_name="network.bytes_sent",
            metric_value=net_io.bytes_sent,
            metric_unit=MetricUnit.BYTES,
            tags={"type": "network", "host": self.hostname},
            timestamp=timestamp,
        ))
        metrics.append(self._create_metric(
            metric_name="network.bytes_recv",
            metric_value=net_io.bytes_recv,
            metric_unit=MetricUnit.BYTES,
            tags={"type": "network", "host": self.hostname},
            timestamp=timestamp,
        ))

        # Process count
        process_count = len(psutil.pids())
        metrics.append(self._create_metric(
            metric_name="system.process_count",
            metric_value=process_count,
            metric_unit=MetricUnit.COUNT,
            tags={"type": "system", "host": self.hostname},
            timestamp=timestamp,
        ))

        # Save to database
        for metric in metrics:
            self.db.add(metric)

        await self.db.flush()

        logger.info("Collected {} system metrics".format(len(metrics)))
        return metrics

    async def collect_database_metrics(self) -> DatabaseMetric:
        """Collect database performance metrics

        Returns:
            DatabaseMetric instance
        """
        import uuid
        timestamp = datetime.utcnow()

        # Get database metrics from PostgreSQL
        try:
            # Connection counts
            connections_query = """
            SELECT
                count(*) FILTER (WHERE state = 'active') as active,
                count(*) FILTER (WHERE state = 'idle') as idle,
                count(*) as total
            FROM pg_stat_activity
            WHERE datname = current_database()
            """

            result = await self.db.execute(connections_query)
            row = result.first()
            active_connections = row[0] if row else 0
            idle_connections = row[1] if row else 0
            total_connections = row[2] if row else 0

            # Get max connections
            max_query = "SELECT setting::int FROM pg_settings WHERE name = 'max_connections'"
            max_result = await self.db.execute(max_query)
            max_connections = max_result.scalar() or 100

        except Exception as e:
            logger.error("Failed to collect database metrics: {}".format(e))
            active_connections = 0
            idle_connections = 0
            total_connections = 0
            max_connections = 100

        # Create metric
        metric_id = "db_metric_{}".format(uuid.uuid4().hex[:12])
        metric = DatabaseMetric(
            metric_id=metric_id,
            active_connections=active_connections,
            idle_connections=idle_connections,
            total_connections=total_connections,
            max_connections=max_connections,
            timestamp=timestamp,
            interval="minute",
            hostname=self.hostname,
        )

        self.db.add(metric)
        await self.db.flush()

        logger.info("Collected database metrics: {} connections".format(total_connections))
        return metric

    def _create_metric(
        self,
        metric_name: str,
        metric_value: float,
        metric_unit: str = None,
        tags: Dict[str, str] = None,
        timestamp: datetime = None,
    ) -> SystemMetric:
        """Create a system metric instance

        Args:
            metric_name: Metric name
            metric_value: Metric value
            metric_unit: Unit of measurement
            tags: Tags for filtering
            timestamp: When metric was recorded

        Returns:
            SystemMetric instance
        """
        import uuid

        return SystemMetric(
            metric_id="sys_metric_{}".format(uuid.uuid4().hex[:12]),
            metric_type=MetricType.SYSTEM,
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            tags=tags or {},
            timestamp=timestamp or datetime.utcnow(),
            interval="minute",
            source=self.hostname,
        )


class HealthCheckService(object):
    """Service for executing health checks"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_all_health_checks(self) -> List[HealthCheckResult]:
        """Execute all system health checks

        Returns:
            List of HealthCheckResult instances
        """
        results = []

        # System health check
        results.append(await self._check_system_health())

        # Database health check
        results.append(await self._check_database_health())

        # Disk space health check
        results.append(await self._check_disk_health())

        # Memory health check
        results.append(await self._check_memory_health())

        # Save to database
        for result in results:
            self.db.add(result)

        await self.db.flush()

        return results

    async def _check_system_health(self) -> HealthCheckResult:
        """Check overall system health"""
        import uuid

        start_time = datetime.utcnow()

        try:
            # Check load average
            load_avg = psutil.getloadavg()
            cpu_count = psutil.cpu_count()

            # Determine status
            if cpu_count > 0:
                load_ratio = load_avg[0] / cpu_count
            else:
                load_ratio = 0

            if load_ratio < 1.0:
                status = "healthy"
                message = "System load is normal"
            elif load_ratio < 2.0:
                status = "degraded"
                message = "System load is elevated"
            else:
                status = "unhealthy"
                message = "System load is critical"

            # Create result
            result = HealthCheckResult(
                check_id="health_{}".format(uuid.uuid4().hex[:12]),
                check_name="system.health",
                check_type="system",
                component="system",
                status=status,
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                message=message,
                details={
                    "load_average_1m": load_avg[0],
                    "load_average_5m": load_avg[1],
                    "load_average_15m": load_avg[2],
                    "cpu_count": cpu_count,
                    "load_ratio": load_ratio,
                },
                timestamp=start_time,
            )

            return result

        except Exception as e:
            return HealthCheckResult(
                check_id="health_{}".format(uuid.uuid4().hex[:12]),
                check_name="system.health",
                check_type="system",
                component="system",
                status="unhealthy",
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                message="Health check failed",
                error=str(e),
                error_type=type(e).__name__,
                timestamp=start_time,
            )

    async def _check_database_health(self) -> HealthCheckResult:
        """Check database health"""
        import uuid

        start_time = datetime.utcnow()

        try:
            # Simple query to check connectivity
            result = await self.db.execute("SELECT 1")
            value = result.scalar()

            if value == 1:
                status = "healthy"
                message = "Database is responsive"
            else:
                status = "unhealthy"
                message = "Database returned unexpected value"

            # Get connection count
            conn_query = "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
            conn_result = await self.db.execute(conn_query)
            connection_count = conn_result.scalar() or 0

            health_result = HealthCheckResult(
                check_id="health_{}".format(uuid.uuid4().hex[:12]),
                check_name="database.health",
                check_type="database",
                component="database",
                status=status,
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                message=message,
                details={
                    "active_connections": connection_count,
                },
                timestamp=start_time,
            )

            return health_result

        except Exception as e:
            return HealthCheckResult(
                check_id="health_{}".format(uuid.uuid4().hex[:12]),
                check_name="database.health",
                check_type="database",
                component="database",
                status="unhealthy",
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                message="Database health check failed",
                error=str(e),
                error_type=type(e).__name__,
                timestamp=start_time,
            )

    async def _check_disk_health(self) -> HealthCheckResult:
        """Check disk space health"""
        import uuid

        start_time = datetime.utcnow()

        try:
            disk = psutil.disk_usage("/")
            usage_percent = disk.percent

            if usage_percent < 80:
                status = "healthy"
                message = "Disk space is normal"
            elif usage_percent < 90:
                status = "degraded"
                message = "Disk space is low"
            else:
                status = "unhealthy"
                message = "Disk space is critical"

            return HealthCheckResult(
                check_id="health_{}".format(uuid.uuid4().hex[:12]),
                check_name="disk.health",
                check_type="system",
                component="disk",
                status=status,
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                message=message,
                details={
                    "path": "/",
                    "usage_percent": usage_percent,
                    "free_gb": disk.free / (1024**3),
                    "total_gb": disk.total / (1024**3),
                },
                timestamp=start_time,
            )

        except Exception as e:
            return HealthCheckResult(
                check_id="health_{}".format(uuid.uuid4().hex[:12]),
                check_name="disk.health",
                check_type="system",
                component="disk",
                status="unhealthy",
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                message="Disk health check failed",
                error=str(e),
                error_type=type(e).__name__,
                timestamp=start_time,
            )

    async def _check_memory_health(self) -> HealthCheckResult:
        """Check memory health"""
        import uuid

        start_time = datetime.utcnow()

        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            if usage_percent < 80:
                status = "healthy"
                message = "Memory usage is normal"
            elif usage_percent < 90:
                status = "degraded"
                message = "Memory usage is elevated"
            else:
                status = "unhealthy"
                message = "Memory usage is critical"

            return HealthCheckResult(
                check_id="health_{}".format(uuid.uuid4().hex[:12]),
                check_name="memory.health",
                check_type="system",
                component="memory",
                status=status,
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                message=message,
                details={
                    "usage_percent": usage_percent,
                    "available_gb": memory.available / (1024**3),
                    "total_gb": memory.total / (1024**3),
                },
                timestamp=start_time,
            )

        except Exception as e:
            return HealthCheckResult(
                check_id="health_{}".format(uuid.uuid4().hex[:12]),
                check_name="memory.health",
                check_type="system",
                component="memory",
                status="unhealthy",
                response_time_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                message="Memory health check failed",
                error=str(e),
                error_type=type(e).__name__,
                timestamp=start_time,
            )


class ThresholdAlertingService(object):
    """Service for threshold-based alerting"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_thresholds(self, metric: SystemMetric) -> Optional[SystemAlert]:
        """Check if metric violates any thresholds

        Args:
            metric: The metric to check

        Returns:
            SystemAlert if threshold violated, None otherwise
        """
        # Get active thresholds for this metric
        query = select(MonitoringThreshold).where(
            and_(
                MonitoringThreshold.metric_name == metric.metric_name,
                MonitoringThreshold.is_active == True,
            )
        )

        result = await self.db.execute(query)
        thresholds = result.scalars().all()

        for threshold in thresholds:
            # Check if value violates threshold
            violation = await self._check_threshold(metric, threshold)

            if violation:
                # Create alert
                alert = await self._create_threshold_alert(metric, threshold)

                if alert:
                    return alert

        return None

    async def _check_threshold(
        self,
        metric: SystemMetric,
        threshold: MonitoringThreshold,
    ) -> Optional[str]:
        """Check if metric violates threshold

        Returns:
            "warning" or "critical" if violated, None otherwise
        """
        value = metric.metric_value
        comparison = threshold.comparison

        # Check critical threshold
        if threshold.critical_threshold is not None:
            critical = threshold.critical_threshold
            if self._compare(value, critical, comparison):
                return "critical"

        # Check warning threshold
        if threshold.warning_threshold is not None:
            warning = threshold.warning_threshold
            if self._compare(value, warning, comparison):
                return "warning"

        return None

    def _compare(self, value: float, threshold: float, comparison: str) -> bool:
        """Compare value to threshold using comparison operator

        Args:
            value: Metric value
            threshold: Threshold value
            comparison: Comparison operator

        Returns:
            True if comparison is true
        """
        if comparison == ">":
            return value > threshold
        elif comparison == ">=":
            return value >= threshold
        elif comparison == "<":
            return value < threshold
        elif comparison == "<=":
            return value <= threshold
        elif comparison == "=":
            return value == threshold
        else:
            return False

    async def _create_threshold_alert(
        self,
        metric: SystemMetric,
        threshold: MonitoringThreshold,
    ) -> Optional[SystemAlert]:
        """Create alert for threshold violation

        Args:
            metric: The metric that violated threshold
            threshold: The violated threshold

        Returns:
            SystemAlert instance
        """
        try:
            # Determine severity
            if metric.metric_value >= (threshold.critical_threshold or float('inf')):
                severity = AlertSeverity.CRITICAL
                level = "critical"
            else:
                severity = AlertSeverity.HIGH
                level = "warning"

            # Create alert
            alert = SystemAlert(
                severity=severity,
                component="monitoring",
                alert_type="threshold_violation",
                message="Threshold violation: {} {} is {}".format(
                    metric.metric_name,
                    level,
                    metric.metric_value,
                ),
                details={
                    "metric_name": metric.metric_name,
                    "metric_value": metric.metric_value,
                    "threshold_name": threshold.name,
                    "threshold_value": threshold.critical_threshold or threshold.warning_threshold,
                    "comparison": threshold.comparison,
                    "tags": metric.tags,
                },
                status=AlertStatus.OPEN,
            )

            self.db.add(alert)
            await self.db.flush()

            logger.warning("Threshold violation alert created: {}".format(metric.metric_name))
            return alert

        except Exception as e:
            logger.error("Failed to create threshold alert: {}".format(e))
            return None


class MonitoringQueryService(object):
    """Service for querying monitoring data"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_system_metrics(
        self,
        metric_name: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SystemMetric]:
        """Query system metrics

        Args:
            metric_name: Filter by metric name
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum records to return

        Returns:
            List of SystemMetric instances
        """
        query = select(SystemMetric)

        conditions = []
        if metric_name:
            conditions.append(SystemMetric.metric_name == metric_name)
        if start_time:
            conditions.append(SystemMetric.timestamp >= start_time)
        if end_time:
            conditions.append(SystemMetric.timestamp <= end_time)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(desc(SystemMetric.timestamp)).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status

        Returns:
            Dict with health status summary
        """
        # Get latest health check results
        query = select(HealthCheckResult).order_by(
            desc(HealthCheckResult.timestamp)
        ).limit(20)

        result = await self.db.execute(query)
        recent_checks = result.scalars().all()

        # Group by component
        component_status = {}
        for check in recent_checks:
            if check.component not in component_status:
                component_status[check.component] = check

        # Determine overall status
        statuses = [c.status for c in component_status.values()]
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return {
            "overall_status": overall_status,
            "components": {
                name: {
                    "status": check.status,
                    "message": check.message,
                    "timestamp": check.timestamp.isoformat(),
                }
                for name, check in component_status.items()
            },
            "last_updated": recent_checks[0].timestamp.isoformat() if recent_checks else None,
        }


# Factory functions
def get_metrics_service(db: AsyncSession) -> MetricsCollectionService:
    """Get metrics collection service"""
    return MetricsCollectionService(db)


def get_health_check_service(db: AsyncSession) -> HealthCheckService:
    """Get health check service"""
    return HealthCheckService(db)


def get_alerting_service(db: AsyncSession) -> ThresholdAlertingService:
    """Get threshold alerting service"""
    return ThresholdAlertingService(db)


def get_query_service(db: AsyncSession) -> MonitoringQueryService:
    """Get monitoring query service"""
    return MonitoringQueryService(db)
