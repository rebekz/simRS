"""Integration Monitoring Service for STORY-024-11

This module provides services for:
- Integration endpoint health monitoring
- Error tracking and alerting
- Performance metrics collection
- Integration log management

Python 3.5+ compatible
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration_monitoring import (
    IntegrationEndpoint, IntegrationLog, IntegrationError,
    HealthCheck, IntegrationMetric, IntegrationAlert,
    EndpointStatus, MessageDirection, ErrorSeverity
)


logger = logging.getLogger(__name__)


# =============================================================================
# Service Factory
# =============================================================================

_monitoring_service_instance = None


def get_monitoring_service(db: AsyncSession):
    """Get or create monitoring service instance"""
    global _monitoring_service_instance
    if _monitoring_service_instance is None:
        _monitoring_service_instance = MonitoringService(db)
    else:
        _monitoring_service_instance.db = db
    return _monitoring_service_instance


# =============================================================================
# Health Check Service
# =============================================================================

class HealthCheckService(object):
    """Health check service for integration endpoints"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def perform_health_check(
        self,
        endpoint_id: int,
        check_type: str = "full"
    ) -> Dict[str, Any]:
        """Perform health check on endpoint

        Args:
            endpoint_id: Endpoint ID
            check_type: Type of check (connectivity, authentication, full)

        Returns:
            Health check result
        """
        check_id = "HC-{}".format(uuid.uuid4())
        start_time = datetime.utcnow()

        try:
            # Get endpoint
            query = select(IntegrationEndpoint).where(
                IntegrationEndpoint.id == endpoint_id
            )
            result = await self.db.execute(query)
            endpoint = result.scalar_one_or_none()

            if not endpoint:
                raise ValueError("Endpoint not found")

            # Perform health check
            check_result = await self._execute_health_check(endpoint, check_type)

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Create health check record
            health_check = HealthCheck(
                check_id=check_id,
                endpoint_id=endpoint_id,
                check_type=check_type,
                status=check_result["status"],
                response_time_ms=processing_time,
                is_reachable=check_result.get("is_reachable", False),
                is_authenticated=check_result.get("is_authenticated"),
                details=check_result.get("details"),
                error_code=check_result.get("error_code"),
                error_message=check_result.get("error_message")
            )
            self.db.add(health_check)

            # Update endpoint status
            await self._update_endpoint_status(endpoint, check_result)

            await self.db.commit()

            return {
                "check_id": check_id,
                "endpoint_id": endpoint_id,
                "endpoint_name": endpoint.endpoint_name,
                "check_type": check_type,
                "status": check_result["status"],
                "is_reachable": check_result.get("is_reachable"),
                "is_authenticated": check_result.get("is_authenticated"),
                "response_time_ms": processing_time,
                "details": check_result.get("details"),
                "checked_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Health check failed: {}".format(e))
            raise

    async def _execute_health_check(
        self,
        endpoint: IntegrationEndpoint,
        check_type: str
    ) -> Dict[str, Any]:
        """Execute actual health check

        This is a mock implementation - in production, use actual connection attempts.
        """
        # Mock implementation - always return healthy
        # In production, make actual connection attempt
        import asyncio
        await asyncio.sleep(0.1)  # Simulate network delay

        return {
            "status": "healthy",
            "is_reachable": True,
            "is_authenticated": True,
            "details": {
                "connection_time_ms": 50,
                "auth_time_ms": 30
            }
        }

    async def _update_endpoint_status(
        self,
        endpoint: IntegrationEndpoint,
        check_result: Dict[str, Any]
    ) -> None:
        """Update endpoint status based on health check"""
        if check_result["status"] == "healthy":
            endpoint.status = EndpointStatus.ONLINE
            endpoint.last_health_check = datetime.utcnow()
            endpoint.last_success = datetime.utcnow()
        else:
            endpoint.status = EndpointStatus.ERROR
            endpoint.last_health_check = datetime.utcnow()
            endpoint.last_error = datetime.utcnow()
            endpoint.last_error_message = check_result.get("error_message", "Health check failed")


# =============================================================================
# Error Tracking Service
# =============================================================================

class ErrorTrackingService(object):
    """Error tracking and alerting service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_error(
        self,
        endpoint_id: Optional[int],
        log_id: Optional[int],
        error_type: str,
        error_category: str,
        error_message: str,
        severity: str = ErrorSeverity.ERROR,
        error_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create integration error record

        Args:
            endpoint_id: Related endpoint ID
            log_id: Related log ID
            error_type: Type of error
            error_category: Category of error
            error_message: Error message
            severity: Error severity
            error_details: Additional error details

        Returns:
            Created error record
        """
        try:
            error_id = "ERR-{}".format(uuid.uuid4())

            error = IntegrationError(
                error_id=error_id,
                endpoint_id=endpoint_id,
                log_id=log_id,
                error_type=error_type,
                error_category=error_category,
                severity=severity,
                error_message=error_message,
                error_details=error_details,
                occurred_at=datetime.utcnow()
            )

            self.db.add(error)
            await self.db.commit()

            # Check if alert should be sent
            if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]:
                await self._create_alert_for_error(error)

            return {
                "error_id": error_id,
                "error_type": error_type,
                "error_category": error_category,
                "severity": severity,
                "error_message": error_message,
                "occurred_at": error.occurred_at.isoformat()
            }

        except Exception as e:
            logger.error("Error creating error record: {}".format(e))
            await self.db.rollback()
            raise

    async def _create_alert_for_error(
        self,
        error: IntegrationError
    ) -> None:
        """Create alert for error"""
        try:
            alert_id = "ALERT-{}".format(uuid.uuid4())

            # Get endpoint name if available
            endpoint_name = "Unknown"
            if error.endpoint_id:
                query = select(IntegrationEndpoint.endpoint_name).where(
                    IntegrationEndpoint.id == error.endpoint_id
                )
                result = await self.db.execute(query)
                endpoint_name = result.scalar_one_or_none() or "Unknown"

            alert = IntegrationAlert(
                alert_id=alert_id,
                endpoint_id=error.endpoint_id,
                error_id=error.id,
                alert_type="integration_error",
                severity=error.severity,
                title="Integration Error: {}".format(error.error_type),
                message="{} endpoint reported {}: {}".format(
                    endpoint_name,
                    error.error_type,
                    error.error_message
                ),
                details={
                    "error_category": error.error_category,
                    "error_code": error.error_code,
                    "error_details": error.error_details
                },
                created_at=datetime.utcnow()
            )

            self.db.add(alert)

            # Update error alert flag
            error.alert_sent = True
            error.alert_sent_at = datetime.utcnow()

            await self.db.commit()

        except Exception as e:
            logger.error("Error creating alert: {}".format(e))
            await self.db.rollback()

    async def resolve_error(
        self,
        error_id: str,
        resolved_by: int,
        resolution_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark error as resolved

        Args:
            error_id: Error ID
            resolved_by: User ID who resolved
            resolution_notes: Optional resolution notes

        Returns:
            Updated error record
        """
        try:
            query = select(IntegrationError).where(
                IntegrationError.error_id == error_id
            )
            result = await self.db.execute(query)
            error = result.scalar_one_or_none()

            if not error:
                raise ValueError("Error not found")

            error.is_resolved = True
            error.resolved_at = datetime.utcnow()
            error.resolved_by = resolved_by
            error.resolution_notes = resolution_notes

            await self.db.commit()

            return {
                "error_id": error.error_id,
                "is_resolved": True,
                "resolved_at": error.resolved_at.isoformat()
            }

        except Exception as e:
            logger.error("Error resolving error: {}".format(e))
            await self.db.rollback()
            raise


# =============================================================================
# Metrics Collection Service
# =============================================================================

class MetricsService(object):
    """Metrics collection and aggregation service"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_metric(
        self,
        endpoint_id: Optional[int],
        metric_type: str,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None,
        dimensions: Optional[Dict[str, Any]] = None,
        interval: str = "minute"
    ) -> Dict[str, Any]:
        """Record integration metric

        Args:
            endpoint_id: Endpoint ID
            metric_type: Metric type
            metric_name: Metric name
            metric_value: Metric value
            metric_unit: Metric unit
            dimensions: Metric dimensions
            interval: Time interval

        Returns:
            Recorded metric
        """
        try:
            metric_id = "METRIC-{}".format(uuid.uuid4())

            metric = IntegrationMetric(
                metric_id=metric_id,
                endpoint_id=endpoint_id,
                metric_type=metric_type,
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit,
                timestamp=datetime.utcnow(),
                interval=interval,
                dimensions=dimensions
            )

            self.db.add(metric)
            await self.db.commit()

            return {
                "metric_id": metric_id,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "recorded_at": metric.timestamp.isoformat()
            }

        except Exception as e:
            logger.error("Error recording metric: {}".format(e))
            await self.db.rollback()
            raise

    async def get_metrics(
        self,
        endpoint_id: Optional[int] = None,
        metric_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get metrics with filtering

        Args:
            endpoint_id: Filter by endpoint
            metric_type: Filter by metric type
            start_time: Start time filter
            end_time: End time filter
            limit: Max records

        Returns:
            List of metrics
        """
        try:
            query = select(IntegrationMetric)

            filters = []
            if endpoint_id:
                filters.append(IntegrationMetric.endpoint_id == endpoint_id)
            if metric_type:
                filters.append(IntegrationMetric.metric_type == metric_type)
            if start_time:
                filters.append(IntegrationMetric.timestamp >= start_time)
            if end_time:
                filters.append(IntegrationMetric.timestamp <= end_time)

            if filters:
                query = query.where(and_(*filters))

            query = query.order_by(desc(IntegrationMetric.timestamp)).limit(limit)

            result = await self.db.execute(query)
            metrics = result.scalars().all()

            return [
                {
                    "metric_id": m.metric_id,
                    "endpoint_id": m.endpoint_id,
                    "metric_type": m.metric_type,
                    "metric_name": m.metric_name,
                    "metric_value": m.metric_value,
                    "metric_unit": m.metric_unit,
                    "timestamp": m.timestamp.isoformat(),
                    "dimensions": m.dimensions
                }
                for m in metrics
            ]

        except Exception as e:
            logger.error("Error getting metrics: {}".format(e))
            raise


# =============================================================================
# Main Monitoring Service
# =============================================================================

class MonitoringService(object):
    """Main monitoring service

    Coordinates all monitoring operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.health_check = HealthCheckService(db)
        self.error_tracking = ErrorTrackingService(db)
        self.metrics = MetricsService(db)

    # Health check operations
    async def perform_health_check(
        self,
        endpoint_id: int,
        check_type: str = "full"
    ) -> Dict[str, Any]:
        """Perform health check on endpoint"""
        return await self.health_check.perform_health_check(endpoint_id, check_type)

    async def health_check_all_endpoints(self) -> List[Dict[str, Any]]:
        """Perform health check on all active endpoints"""
        try:
            query = select(IntegrationEndpoint).where(
                IntegrationEndpoint.is_active == True
            )
            result = await self.db.execute(query)
            endpoints = result.scalars().all()

            results = []
            for endpoint in endpoints:
                try:
                    check_result = await self.health_check.perform_health_check(endpoint.id)
                    results.append(check_result)
                except Exception as e:
                    logger.error("Health check failed for endpoint {}: {}".format(
                        endpoint.endpoint_name, e
                    ))
                    results.append({
                        "endpoint_id": endpoint.id,
                        "endpoint_name": endpoint.endpoint_name,
                        "status": "error",
                        "error_message": str(e)
                    })

            return results

        except Exception as e:
            logger.error("Error performing health checks: {}".format(e))
            raise

    # Error tracking operations
    async def create_error(
        self,
        endpoint_id: Optional[int],
        log_id: Optional[int],
        error_type: str,
        error_category: str,
        error_message: str,
        severity: str = ErrorSeverity.ERROR,
        error_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create integration error record"""
        return await self.error_tracking.create_error(
            endpoint_id, log_id, error_type, error_category,
            error_message, severity, error_details
        )

    async def resolve_error(
        self,
        error_id: str,
        resolved_by: int,
        resolution_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mark error as resolved"""
        return await self.error_tracking.resolve_error(
            error_id, resolved_by, resolution_notes
        )

    # Metrics operations
    async def record_metric(
        self,
        endpoint_id: Optional[int],
        metric_type: str,
        metric_name: str,
        metric_value: float,
        metric_unit: Optional[str] = None,
        dimensions: Optional[Dict[str, Any]] = None,
        interval: str = "minute"
    ) -> Dict[str, Any]:
        """Record integration metric"""
        return await self.metrics.record_metric(
            endpoint_id, metric_type, metric_name, metric_value,
            metric_unit, dimensions, interval
        )

    async def get_metrics(
        self,
        endpoint_id: Optional[int] = None,
        metric_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get metrics with filtering"""
        return await self.metrics.get_metrics(
            endpoint_id, metric_type, start_time, end_time, limit
        )

    # Statistics and overview
    async def get_monitoring_overview(self) -> Dict[str, Any]:
        """Get integration monitoring overview"""
        try:
            # Get endpoint counts
            endpoint_query = select(func.count(IntegrationEndpoint.id)).where(
                IntegrationEndpoint.is_active == True
            )
            endpoint_result = await self.db.execute(endpoint_query)
            total_endpoints = endpoint_result.scalar() or 0

            online_query = select(func.count(IntegrationEndpoint.id)).where(
                and_(
                    IntegrationEndpoint.is_active == True,
                    IntegrationEndpoint.status == EndpointStatus.ONLINE
                )
            )
            online_result = await self.db.execute(online_query)
            online_endpoints = online_result.scalar() or 0

            error_query = select(func.count(IntegrationEndpoint.id)).where(
                and_(
                    IntegrationEndpoint.is_active == True,
                    IntegrationEndpoint.status == EndpointStatus.ERROR
                )
            )
            error_result = await self.db.execute(error_query)
            error_endpoints = error_result.scalar() or 0

            # Get recent error count
            recent_error_query = select(func.count(IntegrationError.id)).where(
                and_(
                    IntegrationError.occurred_at >= datetime.utcnow() - timedelta(hours=1),
                    IntegrationError.is_resolved == False
                )
            )
            recent_error_result = await self.db.execute(recent_error_query)
            recent_errors = recent_error_result.scalar() or 0

            # Get open alerts
            alert_query = select(func.count(IntegrationAlert.id)).where(
                IntegrationAlert.status == "open"
            )
            alert_result = await self.db.execute(alert_query)
            open_alerts = alert_result.scalar() or 0

            return {
                "total_endpoints": total_endpoints,
                "online_endpoints": online_endpoints,
                "error_endpoints": error_endpoints,
                "offline_endpoints": total_endpoints - online_endpoints - error_endpoints,
                "recent_errors": recent_errors,
                "open_alerts": open_alerts,
                "health_percentage": (online_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
            }

        except Exception as e:
            logger.error("Error getting monitoring overview: {}".format(e))
            raise

    async def get_endpoint_status(self, endpoint_id: int) -> Dict[str, Any]:
        """Get detailed status for specific endpoint"""
        try:
            query = select(IntegrationEndpoint).where(
                IntegrationEndpoint.id == endpoint_id
            )
            result = await self.db.execute(query)
            endpoint = result.scalar_one_or_none()

            if not endpoint:
                raise ValueError("Endpoint not found")

            # Get recent errors
            error_query = select(func.count(IntegrationError.id)).where(
                and_(
                    IntegrationError.endpoint_id == endpoint_id,
                    IntegrationError.occurred_at >= datetime.utcnow() - timedelta(hours=24),
                    IntegrationError.is_resolved == False
                )
            )
            error_result = await self.db.execute(error_query)
            recent_errors = error_result.scalar() or 0

            # Get last health check
            health_query = select(HealthCheck).where(
                HealthCheck.endpoint_id == endpoint_id
            ).order_by(desc(HealthCheck.checked_at)).limit(1)
            health_result = await self.db.execute(health_query)
            last_health_check = health_result.scalar_one_or_none()

            return {
                "endpoint_id": endpoint.id,
                "endpoint_name": endpoint.endpoint_name,
                "endpoint_type": endpoint.endpoint_type,
                "status": endpoint.status,
                "last_health_check": endpoint.last_health_check.isoformat() if endpoint.last_health_check else None,
                "last_success": endpoint.last_success.isoformat() if endpoint.last_success else None,
                "last_error": endpoint.last_error.isoformat() if endpoint.last_error else None,
                "last_error_message": endpoint.last_error_message,
                "total_requests": endpoint.total_requests,
                "successful_requests": endpoint.successful_requests,
                "failed_requests": endpoint.failed_requests,
                "average_response_time_ms": endpoint.average_response_time_ms,
                "uptime_percentage": endpoint.uptime_percentage,
                "recent_errors_24h": recent_errors,
                "last_health_check_result": {
                    "status": last_health_check.status,
                    "response_time_ms": last_health_check.response_time_ms,
                    "checked_at": last_health_check.checked_at.isoformat()
                } if last_health_check else None
            }

        except Exception as e:
            logger.error("Error getting endpoint status: {}".format(e))
            raise

    async def get_recent_logs(
        self,
        endpoint_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent integration logs"""
        try:
            query = select(IntegrationLog)

            filters = []
            if endpoint_id:
                filters.append(IntegrationLog.endpoint_id == endpoint_id)

            if filters:
                query = query.where(and_(*filters))

            query = query.order_by(desc(IntegrationLog.created_at)).limit(limit)

            result = await self.db.execute(query)
            logs = result.scalars().all()

            return [
                {
                    "log_id": log.log_id,
                    "endpoint_id": log.endpoint_id,
                    "message_type": log.message_type,
                    "direction": log.direction,
                    "status": log.status,
                    "response_time_ms": log.response_time_ms,
                    "error_code": log.error_code,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat()
                }
                for log in logs
            ]

        except Exception as e:
            logger.error("Error getting recent logs: {}".format(e))
            raise

    async def get_recent_errors(
        self,
        endpoint_id: Optional[int] = None,
        unresolved_only: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent integration errors"""
        try:
            query = select(IntegrationError)

            filters = []
            if endpoint_id:
                filters.append(IntegrationError.endpoint_id == endpoint_id)
            if unresolved_only:
                filters.append(IntegrationError.is_resolved == False)

            if filters:
                query = query.where(and_(*filters))

            query = query.order_by(desc(IntegrationError.occurred_at)).limit(limit)

            result = await self.db.execute(query)
            errors = result.scalars().all()

            return [
                {
                    "error_id": error.error_id,
                    "endpoint_id": error.endpoint_id,
                    "error_type": error.error_type,
                    "error_category": error.error_category,
                    "severity": error.severity,
                    "error_message": error.error_message,
                    "is_resolved": error.is_resolved,
                    "occurred_at": error.occurred_at.isoformat()
                }
                for error in errors
            ]

        except Exception as e:
            logger.error("Error getting recent errors: {}".format(e))
            raise

    async def get_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get integration alerts"""
        try:
            query = select(IntegrationAlert)

            filters = []
            if status:
                filters.append(IntegrationAlert.status == status)
            if severity:
                filters.append(IntegrationAlert.severity == severity)

            if filters:
                query = query.where(and_(*filters))

            query = query.order_by(desc(IntegrationAlert.created_at)).limit(limit)

            result = await self.db.execute(query)
            alerts = result.scalars().all()

            return [
                {
                    "alert_id": alert.alert_id,
                    "endpoint_id": alert.endpoint_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "message": alert.message,
                    "status": alert.status,
                    "escalation_level": alert.escalation_level,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ]

        except Exception as e:
            logger.error("Error getting alerts: {}".format(e))
            raise
