"""System Monitoring API Endpoints for STORY-005: System Monitoring

This module provides API endpoints for:
- System metrics collection and querying
- Database performance monitoring
- Health check execution
- Threshold-based alerting
- Monitoring dashboards

Python 3.5+ compatible
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.db.session import get_db
from app.models.user import User
from app.models.system_monitoring import (
    SystemMetric, DatabaseMetric, HealthCheckResult,
    MonitoringThreshold,
)
from app.services.system_monitoring import (
    get_metrics_service,
    get_health_check_service,
    get_alerting_service,
    get_query_service,
)
from app.core.deps import get_current_user, get_current_admin_user


logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class HealthStatusResponse(BaseModel):
    """Response model for health status"""
    overall_status: str
    components: Dict[str, Dict[str, Any]]
    last_updated: Optional[str]


class MetricResponse(BaseModel):
    """Response model for a single metric"""
    id: int
    metric_name: str
    metric_value: float
    metric_unit: Optional[str]
    tags: Optional[Dict[str, str]]
    timestamp: datetime

    class Config:
        from_attributes = True


class MetricListResponse(BaseModel):
    """Response model for metric list"""
    total: int
    items: List[MetricResponse]
    limit: int
    has_more: bool


class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    id: int
    check_name: str
    component: str
    status: str
    message: Optional[str]
    details: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Metrics Collection Endpoints
# =============================================================================

@router.post("/metrics/collect")
async def collect_system_metrics(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger system metrics collection (admin only)"""
    try:
        service = get_metrics_service(db)

        # Collect system metrics
        system_metrics = await service.collect_system_metrics()

        # Collect database metrics
        db_metric = await service.collect_database_metrics()

        # Check thresholds for alerts
        alerting_service = get_alerting_service(db)
        for metric in system_metrics:
            await alerting_service.check_thresholds(metric)

        await db.commit()

        return {
            "message": "Metrics collected successfully",
            "system_metrics_count": len(system_metrics),
            "database_metrics_collected": 1,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        await db.rollback()
        logger.error("Error collecting metrics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to collect metrics"
        )


# =============================================================================
# Metrics Query Endpoints
# =============================================================================

@router.get("/metrics", response_model=MetricListResponse)
async def get_system_metrics(
    metric_name: Optional[str] = Query(None, description="Filter by metric name"),
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    limit: int = Query(100, ge=1, le=1000, description="Max records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get system metrics with filters"""
    try:
        service = get_query_service(db)

        metrics = await service.get_system_metrics(
            metric_name=metric_name,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

        return MetricListResponse(
            total=len(metrics),
            items=[MetricResponse.model_validate(m) for m in metrics],
            limit=limit,
            has_more=len(metrics) >= limit,
        )

    except Exception as e:
        logger.error("Error querying metrics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query metrics"
        )


@router.get("/metrics/summary")
async def get_metrics_summary(
    hours: int = Query(24, description="Hours of history to summarize", ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get metrics summary for the specified time period"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)

        # Get CPU metrics
        cpu_query = select(
            func.avg(SystemMetric.metric_value).label("avg"),
            func.max(SystemMetric.metric_value).label("max"),
            func.min(SystemMetric.metric_value).label("min"),
        ).where(
            and_(
                SystemMetric.metric_name == "cpu.usage",
                SystemMetric.timestamp >= start_time,
            )
        )

        cpu_result = await db.execute(cpu_query)
        cpu_row = cpu_result.first()

        # Get memory metrics
        mem_query = select(
            func.avg(SystemMetric.metric_value).label("avg"),
            func.max(SystemMetric.metric_value).label("max"),
            func.min(SystemMetric.metric_value).label("min"),
        ).where(
            and_(
                SystemMetric.metric_name == "memory.usage",
                SystemMetric.timestamp >= start_time,
            )
        )

        mem_result = await db.execute(mem_query)
        mem_row = mem_result.first()

        # Get disk metrics
        disk_query = select(
            func.avg(SystemMetric.metric_value).label("avg"),
            func.max(SystemMetric.metric_value).label("max"),
        ).where(
            and_(
                SystemMetric.metric_name == "disk.usage",
                SystemMetric.timestamp >= start_time,
            )
        )

        disk_result = await db.execute(disk_query)
        disk_row = disk_result.first()

        return {
            "period_hours": hours,
            "cpu": {
                "avg": round(cpu_row.avg or 0, 2),
                "max": round(cpu_row.max or 0, 2),
                "min": round(cpu_row.min or 0, 2),
            } if cpu_row else None,
            "memory": {
                "avg": round(mem_row.avg or 0, 2),
                "max": round(mem_row.max or 0, 2),
                "min": round(mem_row.min or 0, 2),
            } if mem_row else None,
            "disk": {
                "avg": round(disk_row.avg or 0, 2),
                "max": round(disk_row.max or 0, 2),
            } if disk_row else None,
        }

    except Exception as e:
        logger.error("Error getting metrics summary: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics summary"
        )


# =============================================================================
# Health Check Endpoints
# =============================================================================

@router.post("/health-check/run")
async def run_health_checks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute all health checks"""
    try:
        service = get_health_check_service(db)

        results = await service.execute_all_health_checks()

        await db.commit()

        return {
            "message": "Health checks completed",
            "checks_performed": len(results),
            "results": [
                {
                    "name": r.check_name,
                    "component": r.component,
                    "status": r.status,
                    "message": r.message,
                }
                for r in results
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        await db.rollback()
        logger.error("Error running health checks: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to run health checks"
        )


@router.get("/health", response_model=HealthStatusResponse)
async def get_health_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current system health status"""
    try:
        service = get_query_service(db)

        status = await service.get_health_status()

        return HealthStatusResponse(**status)

    except Exception as e:
        logger.error("Error getting health status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get health status"
        )


@router.get("/health/history")
async def get_health_history(
    hours: int = Query(24, description="Hours of history", ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get health check history"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)

        query = select(HealthCheckResult).where(
            HealthCheckResult.timestamp >= start_time
        ).order_by(desc(HealthCheckResult.timestamp))

        result = await db.execute(query)
        checks = result.scalars().all()

        return {
            "period_hours": hours,
            "total_checks": len(checks),
            "checks": [
                {
                    "name": c.check_name,
                    "component": c.component,
                    "status": c.status,
                    "message": c.message,
                    "timestamp": c.timestamp.isoformat(),
                }
                for c in checks
            ],
        }

    except Exception as e:
        logger.error("Error getting health history: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get health history"
        )


# =============================================================================
# Database Metrics Endpoints
# =============================================================================

@router.get("/metrics/database")
async def get_database_metrics(
    hours: int = Query(24, description="Hours of history", ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get database performance metrics"""
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)

        query = select(DatabaseMetric).where(
            DatabaseMetric.timestamp >= start_time
        ).order_by(desc(DatabaseMetric.timestamp))

        result = await db.execute(query)
        metrics = result.scalars().all()

        return {
            "period_hours": hours,
            "total_records": len(metrics),
            "metrics": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "active_connections": m.active_connections,
                    "total_connections": m.total_connections,
                    "max_connections": m.max_connections,
                }
                for m in metrics
            ],
        }

    except Exception as e:
        logger.error("Error getting database metrics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get database metrics"
        )


# =============================================================================
# Monitoring Info Endpoints
# =============================================================================

@router.get("/info")
async def get_monitoring_info(
    current_user: User = Depends(get_current_user),
):
    """Get monitoring system information"""
    return {
        "description": "System monitoring service",
        "metrics_collected": [
            "cpu.usage",
            "memory.usage",
            "memory.available",
            "disk.usage",
            "disk.free",
            "network.bytes_sent",
            "network.bytes_recv",
            "system.process_count",
        ],
        "health_checks": [
            "system.health",
            "database.health",
            "disk.health",
            "memory.health",
        ],
        "collection_interval": "1 minute",
        "retention_period": "30 days",
    }


@router.get("/statistics")
async def get_monitoring_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get monitoring statistics"""
    try:
        # Count total metrics
        system_metric_count = await db.execute(
            select(func.count()).select_from(SystemMetric.__table__)
        )
        total_system_metrics = system_metric_count.scalar() or 0

        db_metric_count = await db.execute(
            select(func.count()).select_from(DatabaseMetric.__table__)
        )
        total_db_metrics = db_metric_count.scalar() or 0

        health_check_count = await db.execute(
            select(func.count()).select_from(HealthCheckResult.__table__)
        )
        total_health_checks = health_check_count.scalar() or 0

        # Get latest timestamps
        latest_system = await db.execute(
            select(func.max(SystemMetric.timestamp))
        )
        latest_system_metric = latest_system.scalar()

        latest_health = await db.execute(
            select(func.max(HealthCheckResult.timestamp))
        )
        latest_health_check = latest_health.scalar()

        return {
            "total_system_metrics": total_system_metrics,
            "total_database_metrics": total_db_metrics,
            "total_health_checks": total_health_checks,
            "latest_system_metric": latest_system_metric.isoformat() if latest_system_metric else None,
            "latest_health_check": latest_health_check.isoformat() if latest_health_check else None,
        }

    except Exception as e:
        logger.error("Error getting monitoring statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
