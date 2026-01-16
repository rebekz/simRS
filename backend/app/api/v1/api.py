from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, audit, monitoring, patients, encounters, bpjs, bpjs_verification, bpjs_aplicare, bpjs_claims, icd10, allergies, clinical_notes, consultation, sep, inventory, user_management, medications, drug_interactions, prescriptions, dispensing, queue, bed, hospital, admission, daily_care, discharge, satusehat, lab_orders, radiology_orders, procedure_codes, training, appointments, appointment_reminders, billing, payments, patient_portal, patient_portal_auth, patient_portal_linking, patient_portal_health, patient_portal_appointments, patient_portal_prescriptions, patient_portal_lab_results, patient_portal_radiology, patient_portal_billing, patient_portal_account, patient_portal_vaccinations, patient_portal_messaging, patient_portal_medical_records, notifications, system_alerts, critical_values, notification_preferences, medication_reminders, lab_result_notifications, payment_reminders, queue_status_notifications, notification_templates, reporting, hl7_messaging, fhir, lis_integration, pacs_integration, device_integration, analytics_dashboard, emr_integration, billing_integration, pharmacy_integration, identification, transformation, integration_monitoring, backup, system_monitoring, patient_registration, patient_checkin, queue_management

api_router = APIRouter()

# Include health check endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Include authentication endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include audit log endpoints (admin only)
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])

# Include backup management endpoints (admin only)
api_router.include_router(backup.router, prefix="/backup", tags=["backup"])

# Include system monitoring endpoints (admin only)
api_router.include_router(system_monitoring.router, prefix="/system-monitoring", tags=["system-monitoring"])

# Include monitoring endpoints
api_router.include_router(monitoring.router, tags=["monitoring"])

# Include patient registration endpoints
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])

# Include enhanced patient registration endpoints
api_router.include_router(patient_registration.router, prefix="/patient-registration", tags=["patient-registration"])

# Include patient check-in endpoints
api_router.include_router(patient_checkin.router, prefix="/patient-checkin", tags=["patient-checkin"])

# Include queue management endpoints
api_router.include_router(queue_management.router, prefix="/queue-management", tags=["queue-management"])

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

# Include Appointment Reminders endpoints
api_router.include_router(appointment_reminders.router, prefix="/appointment-reminders", tags=["Appointment Reminders"])

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

# Include Patient Portal Billing & Payments endpoints
api_router.include_router(patient_portal_billing.router, prefix="/portal", tags=["Patient Portal Billing"])

# Include Patient Portal Account Settings endpoints
api_router.include_router(patient_portal_account.router, prefix="/portal", tags=["Patient Portal Account"])

# Include Patient Portal Vaccinations endpoints
api_router.include_router(patient_portal_vaccinations.router, prefix="/portal", tags=["Patient Portal Vaccinations"])

# Include Patient Portal Messaging endpoints
api_router.include_router(patient_portal_messaging.router, prefix="/portal", tags=["Patient Portal Messaging"])

# Include Patient Portal Medical Records endpoints
api_router.include_router(patient_portal_medical_records.router, prefix="/portal", tags=["Patient Portal Medical Records"])

# Include Notification endpoints
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Include System Alerts endpoints
api_router.include_router(system_alerts.router, tags=["System Alerts"])

# Include Critical Values endpoints
api_router.include_router(critical_values.router, prefix="/critical-values", tags=["Critical Values"])

# Include Notification Preferences endpoints
api_router.include_router(notification_preferences.router, prefix="/notification-preferences", tags=["Notification Preferences"])

# Include Medication Reminders endpoints
api_router.include_router(medication_reminders.router, prefix="/medication-reminders", tags=["Medication Reminders"])

# Include Lab Result Notifications endpoints
api_router.include_router(lab_result_notifications.router, prefix="/lab-result-notifications", tags=["Lab Result Notifications"])

# Include Payment Reminders endpoints
api_router.include_router(payment_reminders.router, prefix="/payment-reminders", tags=["Payment Reminders"])

# Include Queue Status Notifications endpoints
api_router.include_router(queue_status_notifications.router, prefix="/queue-status-notifications", tags=["Queue Status Notifications"])

# Include Notification Templates endpoints
api_router.include_router(notification_templates.router, prefix="/notification-templates", tags=["Notification Templates"])

# Include Reporting & Analytics endpoints
api_router.include_router(reporting.router, prefix="/reporting", tags=["Reporting & Analytics"])

# Include HL7 Messaging endpoints
api_router.include_router(hl7_messaging.router, prefix="/integration/hl7", tags=["HL7 Integration"])

# Include FHIR R4 Server endpoints
api_router.include_router(fhir.router, prefix="/fhir", tags=["FHIR R4 Server"])

# Include LIS Integration endpoints
api_router.include_router(lis_integration.router, prefix="/integration/lis", tags=["LIS Integration"])

# Include PACS Integration endpoints
api_router.include_router(pacs_integration.router, prefix="/integration/pacs", tags=["PACS Integration"])

# Include Device Integration endpoints
api_router.include_router(device_integration.router, prefix="/integration/devices", tags=["Device Integration"])

# Include Analytics Dashboard endpoints
api_router.include_router(analytics_dashboard.router, prefix="/analytics", tags=["Analytics Dashboard"])

# Include EMR/EHR Integration endpoints
api_router.include_router(emr_integration.router, prefix="/integration/emr", tags=["EMR/EHR Integration"])

# Include Billing Integration endpoints
api_router.include_router(billing_integration.router, prefix="/integration/billing", tags=["Billing Integration"])

# Include Pharmacy Integration endpoints
api_router.include_router(pharmacy_integration.router, prefix="/integration/pharmacy", tags=["Pharmacy Integration"])

# Include Identification System Integration endpoints
api_router.include_router(identification.router, prefix="/integration/identification", tags=["Identification System Integration"])

# Include Message Transformation endpoints
api_router.include_router(transformation.router, prefix="/integration/transformation", tags=["Message Transformation"])

# Include Integration Monitoring endpoints
api_router.include_router(integration_monitoring.router, prefix="/integration/monitoring", tags=["Integration Monitoring"])

