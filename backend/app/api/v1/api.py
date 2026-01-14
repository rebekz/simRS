from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, audit, monitoring, patients

api_router = APIRouter()

# Include health check endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Include authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include audit log endpoints (admin only)
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])

# Include monitoring endpoints
api_router.include_router(monitoring.router, tags=["monitoring"])

# Include patient registration endpoints
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
