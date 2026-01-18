"""Prescription Dispensing Schemas for STORY-025

This module provides Pydantic schemas for prescription dispensing:
- Dispensing queue management
- Prescription verification
- Drug barcode scanning
- Stock availability checking
- Label generation
- Patient counseling documentation
- Dispensing history
"""
from typing import List, Optional, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from app.schemas.prescription import PrescriptionItemResponse


# =============================================================================
# Dispensing Enums
# =============================================================================

class DispensingStatus(str, Enum):
    """Dispensing workflow status"""
    QUEUED = "queued"  # In queue for dispensing
    IN_PROGRESS = "in_progress"  # Being dispensed
    AWAITING_VERIFICATION = "awaiting_verification"  # Waiting for pharmacist check
    VERIFIED = "verified"  # Pharmacist verified
    READY_FOR_PICKUP = "ready_for_pickup"  # Ready for patient
    DISPENSED = "dispensed"  # Given to patient
    CANCELLED = "cancelled"  # Cancelled
    ON_HOLD = "on_hold"  # Temporarily on hold


class DispenseStatus(str, Enum):
    """Individual dispense status for tracking prescription item dispensing"""
    PENDING = "pending"  # Pending dispensing
    COMPLETED = "completed"  # Successfully dispensed
    CANCELLED = "cancelled"  # Cancelled
    PARTIAL = "partial"  # Partially dispensed


class DispensePriority(str, Enum):
    """Dispensing priority levels"""
    STAT = "stat"  # Immediate
    URGENT = "urgent"  # Within 30 minutes
    ROUTINE = "routine"  # Within 2 hours


class VerificationStatus(str, Enum):
    """Verification status"""
    PENDING = "pending"  # Not verified
    APPROVED = "approved"  # Verified and approved
    FLAGGED = "flagged"  # Issues found, requires attention
    REJECTED = "rejected"  # Rejected by pharmacist


# =============================================================================
# Dispensing Queue Schemas
# =============================================================================

class DispensingQueueItem(BaseModel):
    """Schema for item in dispensing queue"""
    prescription_id: int
    prescription_number: str
    patient_id: int
    patient_name: str
    patient_bpjs_number: Optional[str] = None
    priority: DispensePriority
    status: DispensingStatus
    submitted_date: datetime
    estimated_ready_time: Optional[datetime] = None

    # Prescriber info
    prescriber_name: Optional[str] = None

    # Item count
    total_items: int
    items_dispensed: int
    narcotic_count: int = 0
    antibiotic_count: int = 0

    # Special flags
    requires_cold_storage: bool = False
    has_special_instructions: bool = False

    # Queue position
    queue_position: Optional[int] = None
    estimated_wait_minutes: Optional[int] = None

    # Verification
    verified: bool = False
    verified_by: Optional[str] = None
    verified_date: Optional[datetime] = None

    created_at: datetime


class DispensingQueueResponse(BaseModel):
    """Schema for dispensing queue response"""
    queue: List[DispensingQueueItem]
    total: int
    by_priority: Dict[str, int]  # {"stat": 1, "urgent": 3, "routine": 15}
    by_status: Dict[str, int]  # {"queued": 5, "in_progress": 2, ...}
    page: int
    page_size: int


# =============================================================================
# Prescription Verification Schemas
# =============================================================================

class PrescriptionVerificationRequest(BaseModel):
    """Schema for prescription verification request"""
    prescription_id: int
    patient_verified: bool = True
    verification_notes: Optional[str] = None
    issues_found: Optional[List[str]] = None
    requires_intervention: bool = False
    intervention_notes: Optional[str] = None
    interactions_overridden: bool = False
    override_reason: Optional[str] = None


class PrescriptionVerificationResponse(BaseModel):
    """Schema for prescription verification response"""
    prescription_id: int
    verification_id: int
    status: VerificationStatus
    verified_by: str
    verified_by_role: str
    verified_date: datetime
    notes: Optional[str] = None
    issues_found: Optional[List[str]] = None
    can_proceed: bool
    requires_intervention: bool
    intervention_notes: Optional[str] = None


# =============================================================================
# Drug Scanning Schemas
# =============================================================================

class DrugScanRequest(BaseModel):
    """Schema for drug barcode scan request"""
    barcode: str = Field(..., description="Drug barcode scanned")
    prescription_item_id: int
    quantity_expected: int
    pharmacist_id: int


class DrugScanResponse(BaseModel):
    """Schema for drug scan response"""
    match: bool
    scanned_drug: Optional[dict] = None
    expected_drug: Optional[dict] = None
    quantity_match: bool
    quantity_scanned: int
    quantity_remaining: int
    can_proceed: bool
    warnings: List[str] = []
    errors: List[str] = []


class DispensingItemProgress(BaseModel):
    """Schema for dispensing item progress"""
    prescription_item_id: int
    drug_name: str
    generic_name: str
    expected_quantity: int
    scanned_quantity: int
    fully_scanned: bool
    scans_completed: List[Dict]  # List of scan records


# =============================================================================
# Stock Availability Schemas
# =============================================================================

class StockCheckResult(BaseModel):
    """Schema for stock availability check result"""
    drug_id: int
    drug_name: str
    generic_name: str
    required_quantity: int
    available_quantity: int
    stock_available: bool
    alternative_drugs: Optional[List[Dict]] = None  # Alternative drugs if stock insufficient
    estimated_restock_date: Optional[date] = None


# =============================================================================
# Label Generation Schemas
# =============================================================================

class DispensingLabel(BaseModel):
    """Schema for dispensing label"""
    prescription_number: str
    patient_name: str
    patient_id: int
    drug_name: str
    generic_name: str
    dosage: str
    dose_unit: str
    frequency: str
    route: str
    duration_days: Optional[int] = None
    quantity_dispensed: int
    special_instructions: Optional[str] = None
    warnings: List[str] = []
    preparation_instructions: Optional[str] = None
    storage_instructions: Optional[str] = None
    dispensed_date: datetime
    expires_at: Optional[datetime] = None  # For compounded medications
    dispenser_name: str
    barcode: str  # Label barcode
    warning_emoji: str = ""  # ⚠️ for special warnings


class LabelGenerationRequest(BaseModel):
    """Schema for label generation request"""
    prescription_id: int
    prescription_item_id: int
    include_barcode: bool = True
    include_warnings: bool = True
    copies: int = Field(default=1, ge=1, le=4)


class LabelGenerationResponse(BaseModel):
    """Schema for label generation response"""
    labels: List[DispensingLabel]
    label_urls: List[str]  # URLs to printable labels
    generated_at: datetime
    generated_by: str


# =============================================================================
# Patient Counseling Schemas
# =============================================================================

class CounselingNote(BaseModel):
    """Schema for patient counseling documentation"""
    prescription_id: int
    patient_id: int
    counselor_id: int  # Pharmacist ID
    counselor_name: str
    counseling_date: datetime

    # Counseling topics covered
    discussed_purpose: bool = False
    discussed_dosage: bool = False
    discussed_timing: bool = False
    discussed_side_effects: bool = False
    discussed_interactions: bool = False
    discussed_storage: bool = False
    discussed_special_instructions: bool = False

    # Patient understanding
    patient_understood: bool = True
    patient_questions: Optional[List[str]] = None
    concerns_raised: Optional[List[str]] = None

    # Additional notes
    counseling_notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None

    # Verification
    patient_signature: Optional[bool] = False  # Electronic signature captured
    caregiver_name: Optional[str] = None  # If patient is minor/incapacitated


class CounselingRequest(BaseModel):
    """Schema for creating counseling record"""
    prescription_id: int
    discussed_purpose: bool = True
    discussed_dosage: bool = True
    discussed_timing: bool = True
    discussed_side_effects: bool = True
    discussed_interactions: bool = True
    discussed_storage: bool = True
    discussed_special_instructions: bool = True
    patient_understood: bool = True
    patient_questions: Optional[List[str]] = None
    concerns_raised: Optional[List[str]] = None
    counseling_notes: Optional[str] = None
    follow_up_required: bool = False
    follow_up_notes: Optional[str] = None
    patient_signature: bool = False
    caregiver_name: Optional[str] = None


# =============================================================================
# Dispensing Completion Schemas
# =============================================================================

class DispensingCompletion(BaseModel):
    """Schema for completing dispensing"""
    prescription_id: int
    all_items_verified: bool = True
    dispenser_id: int
    dispenser_notes: Optional[str] = None
    partial_dispense: bool = False
    partial_dispense_reason: Optional[str] = None
    partial_dispense_items: Optional[List[int]] = None  # Item IDs not dispensed


class DispensingCompletionResponse(BaseModel):
    """Schema for dispensing completion response"""
    prescription_id: int
    prescription_number: str
    status: DispensingStatus
    dispensed_date: datetime
    dispensed_by: str
    items_dispensed: int
    total_items: int
    ready_for_pickup: bool
    estimated_ready_time: Optional[datetime] = None
    patient_notified: bool = False


# =============================================================================
# Dispensing History Schemas
# =============================================================================

class DispensingHistoryItem(BaseModel):
    """Schema for dispensing history item"""
    prescription_id: int
    prescription_number: str
    patient_id: int
    patient_name: str
    dispensed_date: datetime
    dispenser_name: str
    items_dispensed: List[PrescriptionItemResponse]
    total_items: int
    total_cost: Optional[float] = None
    bpjs_claimed: Optional[float] = None
    patient_paid: Optional[float] = None
    counseling_documented: bool = False
    counselor_name: Optional[str] = None


class DispensingHistoryResponse(BaseModel):
    """Schema for dispensing history response"""
    patient_id: Optional[int] = None
    history: List[DispensingHistoryItem]
    total: int
    date_range: Optional[Dict[str, date]] = None
    page: int
    page_size: int


# =============================================================================
# Barcode Verification Schemas
# =============================================================================

class PatientBarcodeVerify(BaseModel):
    """Schema for patient barcode verification"""
    patient_id: int
    barcode_scanned: str
    verified: bool
    patient_name: Optional[str] = None
    bpjs_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    errors: List[str] = []


# =============================================================================
# Statistics Schemas
# =============================================================================

class DispensingStatistics(BaseModel):
    """Schema for dispensing statistics"""
    today_dispensed: int
    today_pending: int
    today_completed: int
    average_dispensing_time_minutes: float
    queue_length: int
    by_priority: Dict[str, int]
    by_dispenser: Dict[str, int]  # Count by pharmacist
    narcotic_dispensed_today: int
    antibiotic_dispensed_today: int
