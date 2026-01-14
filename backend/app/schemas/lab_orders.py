"""Laboratory Order Schemas for STORY-018

This module provides Pydantic schemas for laboratory test ordering:
- Lab order creation and management
- Lab order status tracking
- Lab priority levels
- Lab result integration
- BPJS coverage for lab tests
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# =============================================================================
# Lab Order Enums
# =============================================================================

class LabOrderStatus(str, Enum):
    """Laboratory order status following FHIR ServiceRequest status"""
    DRAFT = "draft"  # Being composed
    ACTIVE = "active"  # Submitted to lab
    ON_HOLD = "on_hold"  # Temporarily suspended
    COMPLETED = "completed"  # Results available
    CANCELLED = "cancelled"  # Cancelled by ordering provider
    ENTERED_IN_ERROR = "entered_in_error"
    IN_PROGRESS = "in_progress"  # Being processed by lab
    SUSPENDED = "suspended"  # Sample rejected or requires recollection


class LabPriority(str, Enum):
    """Laboratory test priority levels"""
    ROUTINE = "routine"  # Normal processing (24-48 hours)
    URGENT = "urgent"  # Expedited processing (within 4-6 hours)
    STAT = "stat"  # Immediate processing (within 1 hour)
    ASAP = "asap"  # As soon as possible (between routine and urgent)


class SpecimenType(str, Enum):
    """Types of laboratory specimens"""
    BLOOD = "blood"
    URINE = "urine"
    SWAB = "swab"
    TISSUE = "tissue"
    CEREOSPINAL_FLUID = "cerebrospinal_fluid"
    SPUTUM = "sputum"
    STOOL = "stool"
    OTHER = "other"


# =============================================================================
# Lab Order Item Schemas
# =============================================================================

class LabOrderItemBase(BaseModel):
    """Base lab order item schema"""
    procedure_code_id: int
    procedure_code: str = Field(..., description="Procedure code (e.g., 'CBC', 'HBA1C')")
    procedure_name: str = Field(..., description="Name of the lab test")
    specimen_type: SpecimenType
    clinical_indication: Optional[str] = Field(None, description="Reason for test")


class LabOrderItemCreate(LabOrderItemBase):
    """Schema for creating a lab order item"""
    special_instructions: Optional[str] = Field(None, description="Special handling or processing instructions")
    is_add_on: bool = Field(False, description="Add-on test to existing specimen")


class LabOrderItemUpdate(BaseModel):
    """Schema for updating a lab order item"""
    specimen_type: Optional[SpecimenType] = None
    clinical_indication: Optional[str] = None
    special_instructions: Optional[str] = None


class LabOrderItemResponse(LabOrderItemBase):
    """Schema for lab order item response"""
    id: int
    lab_order_id: int
    special_instructions: Optional[str] = None
    is_add_on: bool

    # Result information
    result_status: str = Field(..., description="Status of results: pending, partial, complete")
    result_value: Optional[str] = None
    result_units: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None  # H, L, HH, LL, etc
    critical_value: bool = False
    result_date: Optional[datetime] = None
    performed_by: Optional[str] = None
    verified_by: Optional[str] = None
    verified_date: Optional[datetime] = None

    # Specimen tracking
    specimen_id: Optional[str] = Field(None, description="Specimen barcode/ID")
    specimen_collected: bool = False
    specimen_collected_date: Optional[datetime] = None
    specimen_collected_by: Optional[int] = None
    specimen_collected_by_name: Optional[str] = None
    specimen_received_date: Optional[datetime] = None
    specimen_rejected: bool = False
    specimen_rejection_reason: Optional[str] = None

    # Procedure details
    bpjs_code: Optional[str] = None
    bpjs_covered: bool = True
    estimated_cost: Optional[float] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Lab Order Schemas
# =============================================================================

class LabOrderBase(BaseModel):
    """Base lab order schema"""
    patient_id: int
    encounter_id: int
    ordering_provider_id: int


class LabOrderCreate(LabOrderBase):
    """Schema for creating a new lab order"""
    items: List[LabOrderItemCreate] = Field(..., min_items=1, max_items=50)
    priority: LabPriority = LabPriority.ROUTINE
    diagnosis: Optional[str] = Field(None, description="Primary diagnosis (ICD-10)")
    clinical_history: Optional[str] = Field(None, description="Relevant clinical history")
    fasting_required: bool = Field(False, description="Patient must fast before specimen collection")
    special_instructions: Optional[str] = Field(None, description="General instructions for lab")
    is_draft: bool = Field(False, description="Save as draft (not yet submitted)")
    specimen_collection_site: Optional[str] = Field(None, description="Location for specimen collection")

    @field_validator("items")
    @classmethod
    def validate_items(cls, items: List[LabOrderItemCreate]) -> List[LabOrderItemCreate]:
        """Validate lab order items"""
        procedure_codes = [item.procedure_code for item in items]
        if len(procedure_codes) != len(set(procedure_codes)):
            raise ValueError("Duplicate procedure codes are not allowed in a single order")
        return items


class LabOrderUpdate(BaseModel):
    """Schema for updating lab order"""
    priority: Optional[LabPriority] = None
    status: Optional[LabOrderStatus] = None
    diagnosis: Optional[str] = None
    clinical_history: Optional[str] = None
    fasting_required: Optional[bool] = None
    special_instructions: Optional[str] = None
    specimen_collection_site: Optional[str] = None


class LabOrderResponse(LabOrderBase):
    """Schema for lab order response"""
    id: int
    order_number: str = Field(..., description="Human-readable order number (e.g., 'LAB-2025-001234')")
    status: LabOrderStatus
    priority: LabPriority
    diagnosis: Optional[str] = None
    clinical_history: Optional[str] = None
    fasting_required: bool
    special_instructions: Optional[str] = None
    specimen_collection_site: Optional[str] = None

    # Patient and encounter details
    patient_name: Optional[str] = None
    patient_medical_record_number: Optional[str] = None
    patient_date_of_birth: Optional[date] = None
    patient_gender: Optional[str] = None
    patient_bpjs_number: Optional[str] = None
    encounter_type: Optional[str] = None
    encounter_date: Optional[datetime] = None

    # Ordering provider details
    ordering_provider_name: Optional[str] = None
    ordering_provider_license: Optional[str] = None

    # Items
    items: List[LabOrderItemResponse]

    # Summary
    total_items: int
    items_completed: int
    items_in_progress: int
    items_pending: int
    has_critical_results: bool = False

    # Specimen collection
    all_specimens_collected: bool = False
    specimen_collection_scheduled: bool = False
    specimen_collection_date: Optional[datetime] = None

    # Results
    results_available: bool = False
    results_available_date: Optional[datetime] = None
    all_results_complete: bool = False

    # Verification
    verified_by_id: Optional[int] = None
    verified_by_name: Optional[str] = None
    verified_date: Optional[datetime] = None

    # Cost estimate
    estimated_cost: Optional[float] = None
    bpjs_coverage_estimate: Optional[float] = None
    patient_cost_estimate: Optional[float] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Lab Order List Schemas
# =============================================================================

class LabOrderListResponse(BaseModel):
    """Schema for lab order list response with pagination"""
    orders: List[LabOrderResponse]
    total: int
    page: int
    page_size: int
    filters_applied: Optional[Dict[str, Any]] = None


# =============================================================================
# Lab Result Schemas
# =============================================================================

class LabResultDetail(BaseModel):
    """Schema for detailed lab result"""
    item_id: int
    procedure_code: str
    procedure_name: str
    result_value: Optional[str] = None
    result_units: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None
    critical_value: bool = False
    result_date: Optional[datetime] = None
    performed_by: Optional[str] = None
    verified_by: Optional[str] = None
    verified_date: Optional[datetime] = None
    comments: Optional[str] = None


class LabResultReport(BaseModel):
    """Schema for complete lab result report"""
    order_id: int
    order_number: str
    patient_id: int
    patient_name: str
    patient_medical_record_number: str
    patient_date_of_birth: Optional[date] = None
    patient_gender: Optional[str] = None
    ordering_provider_name: Optional[str] = None
    specimen_collection_date: Optional[datetime] = None
    results: List[LabResultDetail]
    report_generated_date: datetime
    has_critical_results: bool = False
    pathologist_reviewed: bool = False
    pathologist_name: Optional[str] = None


# =============================================================================
# Specimen Collection Schemas
# =============================================================================

class SpecimenCollectionUpdate(BaseModel):
    """Schema for updating specimen collection status"""
    item_ids: List[int] = Field(..., min_items=1)
    collected: bool = True
    specimen_id: Optional[str] = Field(None, description="Specimen barcode/ID")
    collected_by: Optional[int] = None
    collection_notes: Optional[str] = None
    rejection_reason: Optional[str] = Field(None, description="Required if rejected")


class SpecimenCollectionResponse(BaseModel):
    """Schema for specimen collection response"""
    order_id: int
    items_updated: int
    collection_status: str  # "partial", "complete"
    specimen_collected_at: Optional[datetime] = None
    received_by_lab_at: Optional[datetime] = None
