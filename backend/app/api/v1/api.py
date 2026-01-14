from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, audit, monitoring, patients, encounters, bpjs, bpjs_verification, icd10, allergies, clinical_notes, consultation, sep, inventory, user_management, medications, drug_interactions, prescriptions, dispensing

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

# Include Allergy Tracking endpoints
api_router.include_router(allergies.router, tags=["allergies"])

# Include Clinical Notes endpoints
api_router.include_router(clinical_notes.router, tags=["clinical-notes"])

# Include Consultation Workflow endpoints
api_router.include_router(consultation.router, tags=["consultation"])

# Include BPJS SEP endpoints
api_router.include_router(sep.router, tags=["sep"])

# Include Pharmacy Inventory endpoints
api_router.include_router(inventory.router, tags=["inventory"])

# Include User Management endpoints
api_router.include_router(user_management.router, tags=["user-management"])

# Include Medication List endpoints
api_router.include_router(medications.router, tags=["medications"])

# Include Drug Interaction Database endpoints
api_router.include_router(drug_interactions.router, tags=["drug-interactions"])

# Include Electronic Prescriptions endpoints
api_router.include_router(prescriptions.router, tags=["prescriptions"])

# Include Prescription Dispensing endpoints
api_router.include_router(dispensing.router, tags=["dispensing"])
