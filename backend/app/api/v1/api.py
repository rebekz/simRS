from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, audit, monitoring, patients, encounters, bpjs, bpjs_verification, icd10

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

# Include encounter endpoints
api_router.include_router(encounters.router, prefix="/encounters", tags=["encounters"])

# Include BPJS endpoints
api_router.include_router(bpjs.router, prefix="/bpjs", tags=["bpjs"])

# Include BPJS verification endpoints
api_router.include_router(bpjs_verification.router, prefix="/bpjs-verification", tags=["bpjs-verification"])

# Include ICD-10 and Problem List endpoints
api_router.include_router(icd10.router, tags=["icd10", "problems"])
