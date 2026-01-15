"""Caregiver/Proxy Access Schemas

Pydantic schemas for caregiver and proxy access management.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, Literal


class ProxyAccessLevel(str):
    """Proxy access levels"""
    FULL_ACCESS = "full_access"
    LIMITED_ACCESS = "limited_access"
    BILLING_ONLY = "billing_only"


class CaregiverLinkCreate(BaseModel):
    """Schema for creating a caregiver link"""
    linked_patient_nik: str = Field(..., pattern=r'^[0-9]{16}$', description="NIK of patient to link")
    relationship_type: str = Field(..., min_length=3, max_length=100, description="Relationship (e.g., parent, spouse, child, guardian)")
    access_level: Literal["full_access", "limited_access", "billing_only"] = Field(
        default="full_access",
        description="Level of access to grant"
    )
    verification_document_path: Optional[str] = Field(None, max_length=500, description="Path to verification document")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "linked_patient_nik": "3201010101010002",
            "relationship_type": "child",
            "access_level": "full_access"
        }
    })


class CaregiverLinkResponse(BaseModel):
    """Schema for caregiver link response"""
    id: int
    linked_patient_id: int
    linked_patient_name: Optional[str] = None
    linked_patient_mrn: Optional[str] = None
    relationship_type: str
    access_level: str
    is_verified: bool
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CaregiverLinkListResponse(BaseModel):
    """Schema for caregiver links list response"""
    links: list[CaregiverLinkResponse]
    total: int


class CaregiverAccessLevelUpdate(BaseModel):
    """Schema for updating caregiver access level"""
    access_level: Literal["full_access", "limited_access", "billing_only"] = Field(
        ...,
        description="New access level"
    )


class CaregiverVerificationRequest(BaseModel):
    """Schema for caregiver verification document upload"""
    document_type: Literal["birth_certificate", "power_of_attorney", "court_order", "other"] = Field(..., description="Type of verification document")
    document_path: str = Field(..., max_length=500, description="Path to uploaded document")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class CaregiverVerificationResponse(BaseModel):
    """Schema for caregiver verification response"""
    success: bool
    message: str
    is_verified: bool
    verification_status: str


class CaregiverDeactivateRequest(BaseModel):
    """Schema for deactivating caregiver link"""
    reason: Optional[str] = Field(None, max_length=500, description="Reason for deactivation")
