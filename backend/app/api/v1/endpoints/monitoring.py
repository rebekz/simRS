"""
Monitoring and health check endpoints.

Provides endpoints for system health monitoring and metrics.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any
import logging
from datetime import datetime

from app.api.deps import get_current_user, get_db, require_permission
from app.core.config import settings
from app.core.metrics import (
    system_health_status,
    db_connections_active,
    auth_sessions_active
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check with system status.

    Checks health of:
    - Database
    - Redis
    - MinIO/S3
    - External APIs (BPJS, SATUSEHAT)
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    all_healthy = True

    # Check database
    try:
        result = await db.execute(text("SELECT version()"))
        db_version = result.scalar()
        health_status["checks"]["database"] = {
            "status": "healthy",
            "version": db_version
        }
        system_health_status.labels(service="database").set(1)
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        system_health_status.labels(service="database").set(0)
        all_healthy = False

    # Check Redis
    try:
        import redis.asyncio as redis
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
        await redis_client.ping()
        await redis_client.close()
        health_status["checks"]["redis"] = {
            "status": "healthy"
        }
        system_health_status.labels(service="redis").set(1)
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        system_health_status.labels(service="redis").set(0)
        all_healthy = False

    # Check MinIO
    try:
        from minio import Minio
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        buckets = client.list_buckets()
        health_status["checks"]["minio"] = {
            "status": "healthy",
            "buckets": [b.name for b in buckets]
        }
        system_health_status.labels(service="minio").set(1)
    except Exception as e:
        logger.error(f"MinIO health check failed: {e}")
        health_status["checks"]["minio"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        system_health_status.labels(service="minio").set(0)
        all_healthy = False

    # Check BPJS API (only if configured)
    if settings.BPJS_CONSUMER_ID and settings.BPJS_CONSUMER_SECRET:
        try:
            # We can't actually call BPJS here without a patient SEP
            # Just check if credentials are set
            health_status["checks"]["bpjs"] = {
                "status": "configured",
                "message": "Credentials configured (actual API check requires SEP)"
            }
        except Exception as e:
            health_status["checks"]["bpjs"] = {
                "status": "error",
                "error": str(e)
            }
    else:
        health_status["checks"]["bpjs"] = {
            "status": "not_configured"
        }

    # Check SATUSEHAT (only if configured)
    if settings.SATUSEHAT_CLIENT_ID and settings.SATUSEHAT_CLIENT_SECRET:
        health_status["checks"]["satusehat"] = {
            "status": "configured",
            "message": "Credentials configured"
        }
    else:
        health_status["checks"]["satusehat"] = {
            "status": "not_configured"
        }

    if not all_healthy:
        health_status["status"] = "degraded"

    return health_status


@router.get("/stats")
async def get_statistics(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get system statistics.

    Requires authentication.
    Returns counts for various entities in the system.
    """
    from app.crud.user import count_users
    from app.crud.audit_log import count_audit_logs
    from app.core.metrics import auth_sessions_active

    stats = {
        "timestamp": datetime.utcnow().isoformat(),
        "users": {},
        "sessions": {},
        "audit_logs": {}
    }

    try:
        # User statistics
        stats["users"]["total"] = await count_users(db)
        stats["users"]["active_sessions"] = auth_sessions_active._value.get() if auth_sessions_active._value else 0
    except Exception as e:
        logger.error(f"Error getting user stats: {e}")
        stats["users"]["error"] = str(e)

    try:
        # Audit log statistics
        stats["audit_logs"]["total"] = await count_audit_logs(db)
    except Exception as e:
        logger.error(f"Error getting audit log stats: {e}")
        stats["audit_logs"]["error"] = str(e)

    return stats


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.

    This is a proxy to the actual metrics endpoint exposed
    by the PrometheusInstrumentator.
    """
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from starlette.responses import Response

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/monitoring/config")
async def get_monitoring_config(
    current_user = Depends(get_current_user),
    _: None = Depends(require_permission("system", "read"))
):
    """
    Get monitoring configuration.

    Requires system:read permission.
    Returns current monitoring and alerting configuration.
    """
    return {
        "environment": settings.ENVIRONMENT,
        "log_level": settings.LOG_LEVEL,
        "version": settings.VERSION,
        "monitoring": {
            "prometheus": {
                "enabled": True,
                "metrics_path": "/metrics",
                "retention": "15d"
            },
            "alerts": {
                "enabled": True,
                "channels": ["email", "log"]
            }
        },
        "health_checks": {
            "database": True,
            "redis": True,
            "minio": True,
            "external_apis": True
        }
    }


@router.post("/monitoring/test-alert")
async def test_alert(
    current_user = Depends(get_current_user),
    _: None = Depends(require_permission("system", "admin"))
):
    """
    Test alerting system.

    Requires system:admin permission.
    Sends a test alert to verify alerting configuration.
    """
    from app.core.metrics import errors_total

    # Log test alert
    logger.warning(f"Test alert triggered by user {current_user.username}")

    # Increment error counter for testing
    errors_total.labels(
        type='test_alert',
        severity='warning'
    ).inc()

    return {
        "status": "success",
        "message": "Test alert sent",
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user.username
    }
