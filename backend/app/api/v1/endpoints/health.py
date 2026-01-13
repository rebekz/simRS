from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime
import asyncio

from app.db.session import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns the API status and basic information.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint.
    Checks the status of database, redis, and minio connections.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Check database connection
    try:
        from app.db.session import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": str(e)
        }

    # Check Redis connection
    try:
        from app.db.redis import get_redis_client
        redis = get_redis_client()
        await redis.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": str(e)
        }

    # Check MinIO connection
    try:
        from app.db.minio import get_minio_client
        minio_client = get_minio_client()
        buckets = minio_client.list_buckets()
        health_status["checks"]["minio"] = {
            "status": "healthy",
            "message": "MinIO connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["minio"] = {
            "status": "unhealthy",
            "message": str(e)
        }

    return health_status


@router.get("/live")
async def liveness() -> Dict[str, str]:
    """
    Liveness probe - indicates if the container is still running.
    """
    return {"status": "alive"}


@router.get("/ready")
async def readiness() -> Dict[str, Any]:
    """
    Readiness probe - indicates if the container is ready to serve traffic.
    """
    ready = True
    checks = {}

    # Check database
    try:
        from app.db.session import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ready"
    except Exception as e:
        ready = False
        checks["database"] = f"not ready: {str(e)}"

    # Check Redis
    try:
        from app.db.redis import get_redis_client
        redis = get_redis_client()
        await redis.ping()
        checks["redis"] = "ready"
    except Exception as e:
        ready = False
        checks["redis"] = f"not ready: {str(e)}"

    return {
        "status": "ready" if ready else "not_ready",
        "checks": checks
    }
