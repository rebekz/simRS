from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, audit, monitoring, patients, encounters, bpjs, bpjs_verification, bpjs_aplicare, bpjs_claims, icd10, allergies, clinical_notes, consultation, sep, inventory, user_management, medications, drug_interactions, prescriptions, dispensing, queue, bed, hospital, admission, daily_care, discharge, satusehat, lab_orders, radiology_orders, procedure_codes, training, appointments, billing, payments, patient_portal, patient_portal_auth, patient_portal_linking, patient_portal_health, patient_portal_appointments, patient_portal_prescriptions, patient_portal_lab_results, patient_portal_radiology

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

# Include BPJS Aplicare endpoints
api_router.include_router(bpjs_aplicare.router, prefix="/bpjs-aplicare", tags=["bpjs-aplicare"])

# Include BPJS Claims endpoints
api_router.include_router(bpjs_claims.router, prefix="/bpjs-claims", tags=["BPJS Claims"])

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

# Include Queue Management endpoints
api_router.include_router(queue.router, tags=["queue"])

# Include Bed Management endpoints
api_router.include_router(bed.router, tags=["bed"])

# Include Hospital Configuration endpoints
api_router.include_router(hospital.router, prefix="/hospital", tags=["hospital"])

# Include Admission Workflow endpoints
api_router.include_router(admission.router, prefix="/admission", tags=["admission"])

# Include Daily Care Documentation endpoints
api_router.include_router(daily_care.router, prefix="/daily-care", tags=["daily-care"])

# Include Discharge Planning endpoints
api_router.include_router(discharge.router, prefix="/discharge", tags=["discharge"])

# Include SATUSEHAT FHIR endpoints
api_router.include_router(satusehat.router, prefix="/satusehat", tags=["satusehat"])

# Include Lab Orders endpoints
api_router.include_router(lab_orders.router, prefix="/lab", tags=["Lab Orders"])

# Include Radiology Orders endpoints
api_router.include_router(radiology_orders.router, prefix="/radiology", tags=["Radiology Orders"])

# Include Procedure Codes endpoints
api_router.include_router(procedure_codes.router, prefix="/procedure-codes", tags=["Procedure Codes"])

# Include Training endpoints
api_router.include_router(training.router, prefix="/training", tags=["Training"])

# Include Appointment Booking endpoints
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])

# Include Billing endpoints
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])

# Include Payments endpoints
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])

# Include Patient Portal endpoints
api_router.include_router(patient_portal.router, prefix="/portal", tags=["Patient Portal"])

# Include Patient Portal Auth endpoints
api_router.include_router(patient_portal_auth.router, prefix="/portal", tags=["Patient Portal Auth"])

# Include Patient Portal Linking endpoints
api_router.include_router(patient_portal_linking.router, prefix="/portal", tags=["Patient Portal Linking"])

# Include Patient Portal Health Record endpoints
api_router.include_router(patient_portal_health.router, prefix="/portal", tags=["Patient Portal Health"])

# Include Patient Portal Appointments endpoints
api_router.include_router(patient_portal_appointments.router, prefix="/portal/appointments", tags=["Patient Portal Appointments"])

# Include Patient Portal Prescriptions endpoints
api_router.include_router(patient_portal_prescriptions.router, prefix="/portal", tags=["Patient Portal Prescriptions"])

# Include Patient Portal Lab Results endpoints
api_router.include_router(patient_portal_lab_results.router, prefix="/portal", tags=["Patient Portal Lab Results"])

# Include Patient Portal Radiology Results endpoints
api_router.include_router(patient_portal_radiology.router, prefix="/portal", tags=["Patient Portal Radiology Results"])

