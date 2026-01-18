from __future__ import annotations

"""Patient Linking Schemas

Pydantic schemas for linking portal accounts to existing patient records.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime, date
from typing import Optional, Literal


class PatientLinkRequest(BaseModel):
    """Schema for linking portal account to patient record"""
    link_method: Literal["nik", "mrn", "bpjs"] = Field(
        ...,
        description="Method to locate existing patient record"
    )
    nik: Optional[str] = Field(None, pattern=r'^[0-9]{16}$', description="16-digit NIK")
    mrn: Optional[str] = Field(None, min_length=1, max_length=20, description="Medical Record Number")
    bpjs_card_number: Optional[str] = Field(None, min_length=13, max_length=20, description="BPJS card number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth for verification")

    @field_validator('date_of_birth')
    @classmethod
    def validate_dob_for_method(cls, v, info):
        """Require DOB for BPJS linking"""
        if info.data.get('link_method') == 'bpjs' and not v:
            raise ValueError('Date of birth is required for BPJS card linking')
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "link_method": "nik",
            "nik": "3201010101010001",
            "date_of_birth": "1990-01-01"
        }
    })


class PatientLinkResponse(BaseModel):
    """Schema for patient link response"""
    success: bool
    message: str
    patient_id: Optional[int] = None
    medical_record_number: Optional[str] = None
    patient_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    is_verified: bool = False
    requires_additional_verification: bool = False


class PatientSummary(BaseModel):
    """Schema for patient summary in search results"""
    patient_id: int
    medical_record_number: str
    full_name: str
    date_of_birth: date
    gender: str
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool
    bpjs_card_number: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ExistingPatientSearchRequest(BaseModel):
    """Schema for searching existing patients"""
    search_type: Literal["nik", "bpjs"] = Field(..., description="Search by NIK or BPJS")
    nik: Optional[str] = Field(None, pattern=r'^[0-9]{16}$')
    bpjs_card_number: Optional[str] = Field(None, min_length=13, max_length=20)
    include_inactive: bool = Field(default=False, description="Include inactive patients")


class ExistingPatientSearchResponse(BaseModel):
    """Schema for existing patient search response"""
    found: bool
    patients: list[PatientSummary] = Field(default_factory=list)
    message: str


class BPJSCardLinkRequest(BaseModel):
    """Schema for BPJS card linking"""
    bpjs_card_number: str = Field(..., min_length=13, max_length=20, description="BPJS card number")
    date_of_birth: date = Field(..., description="Date of birth for verification")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "bpjs_card_number": "1234567890123",
            "date_of_birth": "1990-01-01"
        }
    })


class BPJSEligibilityVerify(BaseModel):
    """Schema for BPJS eligibility verification"""
    bpjs_card_number: str = Field(..., min_length=13, max_length=20)
    visit_date: date = Field(..., description="Planned visit date")


class MedicalRecordNumberSearchRequest(BaseModel):
    """Schema for MRN search"""
    mrn: str = Field(..., min_length=1, max_length=20, description="Medical Record Number")
    date_of_birth: Optional[date] = Field(None, description="Date of birth for verification")


class MedicalRecordNumberSearchResponse(BaseModel):
    """Schema for MRN search response"""
    found: bool
    patient: Optional[PatientSummary] = None
    verification_required: bool = False
    message: str


class NewPatientRecordRequest(BaseModel):
    """Schema for creating new patient record during portal registration"""
    full_name: str = Field(..., min_length=3, max_length=255)
    nik: str = Field(..., pattern=r'^[0-9]{16}$')
    date_of_birth: date
    gender: Literal["male", "female"]
    phone: str = Field(..., pattern=r'^\+?62[0-9]{9,13}$|^08[0-9]{8,11}$')
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=1000)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    blood_type: Optional[Literal["A", "B", "AB", "O", "none"]] = None
    marital_status: Optional[Literal["single", "married", "widowed", "divorced"]] = None
    religion: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    bpjs_card_number: Optional[str] = Field(None, min_length=13, max_length=20)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "full_name": "John Doe",
            "nik": "3201010101010001",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "phone": "+6281234567890",
            "email": "john@example.com",
            "address": "Jl. Sudirman No. 1",
            "city": "Jakarta",
            "province": "DKI Jakarta",
            "postal_code": "10110",
            "blood_type": "A",
            "marital_status": "single",
            "bpjs_card_number": "1234567890123"
        }
    })


class NewPatientRecordResponse(BaseModel):
    """Schema for new patient record creation response"""
    success: bool
    message: str
    patient_id: int
    medical_record_number: str
