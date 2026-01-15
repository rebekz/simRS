"""Integration Monitoring API Endpoints for STORY-024-11

This module provides API endpoints for:
- Integration endpoint monitoring
- Health check operations
- Error tracking and alerting
- Performance metrics

Python 3.5+ compatible
"""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.integration_monitoring import get_monitoring_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class HealthCheckRequest(BaseModel):
    """Request to perform health check"""
    check_type: str = Field("full", description="Type of check (connectivity, authentication, full)")


class ErrorCreateRequest(BaseModel):
    """Request to create error record"""
    endpoint_id: Optional[int] = Field(None, description="Endpoint ID")
    log_id: Optional[int] = Field(None, description="Log ID")
    error_type: str = Field(..., description="Error type")
    error_category: str = Field(..., description="Error category")
    error_message: str = Field(..., description="Error message")
    severity: str = Field("error", description="Error severity (info, warning, error, critical)")
    error_details: Optional[dict] = Field(None, description="Additional error details")


class MetricRecordRequest(BaseModel):
    """Request to record metric"""
    endpoint_id: Optional[int] = Field(None, description="Endpoint ID")
    metric_type: str = Field(..., description="Metric type")
    metric_name: str = Field(..., description="Metric name")
    metric_value: float = Field(..., description="Metric value")
    metric_unit: Optional[str] = Field(None, description="Metric unit")
    dimensions: Optional[dict] = Field(None, description="Metric dimensions")
    interval: str = Field("minute", description="Time interval")


# =============================================================================
# Health Check Endpoints
# =============================================================================

@router.post("/health-check/{endpoint_id}", status_code=status.HTTP_200_OK)
async def perform_health_check(
    endpoint_id: int,
    request: HealthCheckRequest = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform health check on endpoint"""
    try:
        service = get_monitoring_service(db)

        check_type = request.check_type if request else "full"

        result = await service.perform_health_check(endpoint_id, check_type)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error performing health check: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform health check"
        )


@router.post("/health-check/all", status_code=status.HTTP_200_OK)
async def health_check_all_endpoints(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform health check on all active endpoints (admin only)"""
    try:
        service = get_monitoring_service(db)

        results = await service.health_check_all_endpoints()

        return {
            "health_checks": results,
            "total_endpoints": len(results),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("Error performing health checks: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform health checks"
        )


# =============================================================================
# Endpoint Status Endpoints
# =============================================================================

@router.get("/endpoints/{endpoint_id}/status")
async def get_endpoint_status(
    endpoint_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed status for endpoint"""
    try:
        service = get_monitoring_service(db)

        result = await service.get_endpoint_status(endpoint_id)

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting endpoint status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get endpoint status"
        )


# =============================================================================
# Error Tracking Endpoints
# =============================================================================

@router.post("/errors", status_code=status.HTTP_201_CREATED)
async def create_error(
    request: ErrorCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create integration error record"""
    try:
        service = get_monitoring_service(db)

        result = await service.create_error(
            endpoint_id=request.endpoint_id,
            log_id=request.log_id,
            error_type=request.error_type,
            error_category=request.error_category,
            error_message=request.error_message,
            severity=request.severity,
            error_details=request.error_details
        )

        return result

    except Exception as e:
        logger.error("Error creating error record: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create error record"
        )


@router.post("/errors/{error_id}/resolve")
async def resolve_error(
    error_id: str,
    resolution_notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark error as resolved"""
    try:
        service = get_monitoring_service(db)

        result = await service.resolve_error(
            error_id=error_id,
            resolved_by=current_user.id,
            resolution_notes=resolution_notes
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error resolving error: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve error"
        )


@router.get("/errors")
async def get_recent_errors(
    endpoint_id: Optional[int] = Query(None, description="Filter by endpoint ID"),
    unresolved_only: bool = Query(True, description="Show only unresolved errors"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent integration errors"""
    try:
        service = get_monitoring_service(db)

        errors = await service.get_recent_errors(
            endpoint_id=endpoint_id,
            unresolved_only=unresolved_only,
            limit=limit
        )

        return {
            "errors": errors,
            "count": len(errors)
        }

    except Exception as e:
        logger.error("Error getting recent errors: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get errors"
        )


# =============================================================================
# Metrics Endpoints
# =============================================================================

@router.post("/metrics", status_code=status.HTTP_201_CREATED)
async def record_metric(
    request: MetricRecordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record integration metric"""
    try:
        service = get_monitoring_service(db)

        result = await service.record_metric(
            endpoint_id=request.endpoint_id,
            metric_type=request.metric_type,
            metric_name=request.metric_name,
            metric_value=request.metric_value,
            metric_unit=request.metric_unit,
            dimensions=request.dimensions,
            interval=request.interval
        )

        return result

    except Exception as e:
        logger.error("Error recording metric: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record metric"
        )


@router.get("/metrics")
async def get_metrics(
    endpoint_id: Optional[int] = Query(None, description="Filter by endpoint ID"),
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get integration metrics"""
    try:
        service = get_monitoring_service(db)

        # Parse dates
        start_time = None
        end_time = None
        if start_date:
            start_time = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_time = datetime.strptime(end_date, "%Y-%m-%d")

        metrics = await service.get_metrics(
            endpoint_id=endpoint_id,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )

        return {
            "metrics": metrics,
            "count": len(metrics)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD."
        )
    except Exception as e:
        logger.error("Error getting metrics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics"
        )


# =============================================================================
# Logs Endpoints
# =============================================================================

@router.get("/logs")
async def get_recent_logs(
    endpoint_id: Optional[int] = Query(None, description="Filter by endpoint ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent integration logs"""
    try:
        service = get_monitoring_service(db)

        logs = await service.get_recent_logs(
            endpoint_id=endpoint_id,
            limit=limit
        )

        return {
            "logs": logs,
            "count": len(logs)
        }

    except Exception as e:
        logger.error("Error getting recent logs: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get logs"
        )


# =============================================================================
# Alerts Endpoints
# =============================================================================

@router.get("/alerts")
async def get_alerts(
    status: Optional[str] = Query(None, description="Filter by status (open, acknowledged, resolved)"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get integration alerts"""
    try:
        service = get_monitoring_service(db)

        alerts = await service.get_alerts(
            status=status,
            severity=severity,
            limit=limit
        )

        return {
            "alerts": alerts,
            "count": len(alerts)
        }

    except Exception as e:
        logger.error("Error getting alerts: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get alerts"
        )


# =============================================================================
# Overview Endpoints
# =============================================================================

@router.get("/overview")
async def get_monitoring_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get integration monitoring overview"""
    try:
        service = get_monitoring_service(db)

        overview = await service.get_monitoring_overview()

        return overview

    except Exception as e:
        logger.error("Error getting monitoring overview: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get overview"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_monitoring_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get integration monitoring statistics"""
    try:
        from app.models.integration_monitoring import (
            IntegrationEndpoint, IntegrationLog, IntegrationError, IntegrationAlert
        )
        from sqlalchemy import select, func, and_

        # Get endpoint statistics
        endpoint_query = select(func.count(IntegrationEndpoint.id))
        endpoint_result = await db.execute(endpoint_query)
        total_endpoints = endpoint_result.scalar() or 0

        online_query = select(func.count(IntegrationEndpoint.id)).where(
            IntegrationEndpoint.status == "online"
        )
        online_result = await db.execute(online_query)
        online_endpoints = online_result.scalar() or 0

        # Get log statistics
        log_query = select(func.count(IntegrationLog.id))
        log_result = await db.execute(log_query)
        total_logs = log_result.scalar() or 0

        success_log_query = select(func.count(IntegrationLog.id)).where(
            IntegrationLog.status == "success"
        )
        success_result = await db.execute(success_log_query)
        successful_logs = success_result.scalar() or 0

        # Get error statistics
        error_query = select(func.count(IntegrationError.id))
        error_result = await db.execute(error_query)
        total_errors = error_result.scalar() or 0

        unresolved_query = select(func.count(IntegrationError.id)).where(
            IntegrationError.is_resolved == False
        )
        unresolved_result = await db.execute(unresolved_query)
        unresolved_errors = unresolved_result.scalar() or 0

        # Get alert statistics
        alert_query = select(func.count(IntegrationAlert.id))
        alert_result = await db.execute(alert_query)
        total_alerts = alert_result.scalar() or 0

        open_alert_query = select(func.count(IntegrationAlert.id)).where(
            IntegrationAlert.status == "open"
        )
        open_result = await db.execute(open_alert_query)
        open_alerts = open_result.scalar() or 0

        # Get average response time
        time_query = select(func.avg(IntegrationLog.response_time_ms)).where(
            IntegrationLog.response_time_ms.isnot(None)
        )
        time_result = await db.execute(time_query)
        avg_response_time = time_result.scalar() or 0

        return {
            "endpoints": {
                "total": total_endpoints,
                "online": online_endpoints,
                "offline": total_endpoints - online_endpoints
            },
            "logs": {
                "total": total_logs,
                "successful": successful_logs,
                "failed": total_logs - successful_logs,
                "success_rate": (successful_logs / total_logs * 100) if total_logs > 0 else 0
            },
            "errors": {
                "total": total_errors,
                "unresolved": unresolved_errors,
                "resolved": total_errors - unresolved_errors
            },
            "alerts": {
                "total": total_alerts,
                "open": open_alerts,
                "acknowledged_resolved": total_alerts - open_alerts
            },
            "performance": {
                "average_response_time_ms": float(avg_response_time)
            }
        }

    except Exception as e:
        logger.error("Error getting monitoring statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
