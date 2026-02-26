# Models module
# This file exports commonly used models and enums.
# For other models, import them directly from their respective modules.

# Core models
from app.models.user import User, UserRole
from app.models.session import Session
from app.models.permission import Permission, PREDEFINED_PERMISSIONS
from app.models.audit_log import AuditLog
from app.models.password_reset import PasswordResetToken

# Patient Portal models
from app.models.patient_portal import (
    PatientPortalUser,
    PatientPortalVerification,
    PatientPortalSession,
    PatientPortalPasswordReset,
    CaregiverLink,
    ProxyAccessLevel,
    VerificationType,
    VerificationStatus,
)

# Training models
from app.models.training import (
    TrainingModule,
    TrainingAssignment,
    TrainingProgress,
    TrainingMaterial,
    TrainingCompletion,
    TrainingCategory,
    TrainingStatus,
    DifficultyLevel,
)

# Appointment models
from app.models.appointments import (
    Appointment,
    AppointmentSlot,
    AppointmentReminder,
    AppointmentType,
    AppointmentStatus,
    BookingChannel,
    AppointmentPriority,
    ReminderType,
    ReminderStatus,
)

# Billing models
from app.models.billing import (
    Invoice,
    InvoiceItem,
    BillingRule,
    InvoiceApproval,
    InvoiceType,
    PayerType,
    PackageType,
    InvoiceStatus,
    InvoiceItemType,
    BillingRuleType,
    ApprovalStatus,
)

# BPJS models
from app.models.bpjs_claims import (
    BPJSClaim,
    BPJSClaimItem,
    BPJSClaimDocument,
    BPJSSubmissionLog,
    BPJSVerificationQuery,
    BPJSClaimType,
    BPJSClaimStatus,
    BPJSClaimItemType,
    BPJSDocumentType,
    BPJSSubmissionStatus,
    BPJSQueryStatus,
)

# Refill Request models
from app.models.refill_request import (
    PrescriptionRefillRequest,
    PrescriptionRefillItem,
    RefillRequestStatus,
)

__all__ = [
    "User",
    "UserRole",
    "Session",
    "Permission",
    "PREDEFINED_PERMISSIONS",
    "AuditLog",
    "PasswordResetToken",
    "PatientPortalUser",
    "PatientPortalVerification",
    "PatientPortalSession",
    "PatientPortalPasswordReset",
    "CaregiverLink",
    "ProxyAccessLevel",
    "VerificationType",
    "VerificationStatus",
    "TrainingModule",
    "TrainingAssignment",
    "TrainingProgress",
    "TrainingMaterial",
    "TrainingCompletion",
    "TrainingCategory",
    "TrainingStatus",
    "DifficultyLevel",
    "Appointment",
    "AppointmentSlot",
    "AppointmentReminder",
    "AppointmentType",
    "AppointmentStatus",
    "BookingChannel",
    "AppointmentPriority",
    "ReminderType",
    "ReminderStatus",
    "Invoice",
    "InvoiceItem",
    "BillingRule",
    "InvoiceApproval",
    "InvoiceType",
    "PayerType",
    "PackageType",
    "InvoiceStatus",
    "InvoiceItemType",
    "BillingRuleType",
    "ApprovalStatus",
    "BPJSClaim",
    "BPJSClaimItem",
    "BPJSClaimDocument",
    "BPJSSubmissionLog",
    "BPJSVerificationQuery",
    "BPJSClaimType",
    "BPJSClaimStatus",
    "BPJSClaimItemType",
    "BPJSDocumentType",
    "BPJSSubmissionStatus",
    "BPJSQueryStatus",
    "PrescriptionRefillRequest",
    "PrescriptionRefillItem",
    "RefillRequestStatus",
]
