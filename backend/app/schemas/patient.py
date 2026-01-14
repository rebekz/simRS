"""Patient schemas for STORY-006: New Patient Registration

This module defines Pydantic schemas for patient data validation and serialization.
All schemas match the Patient, EmergencyContact, and PatientInsurance models.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from app.models.patient import Gender, BloodType, MaritalStatus, InsuranceType


class EmergencyContactBase(BaseModel):
    """Base emergency contact schema"""
    name: str = Field(..., min_length=1, max_length=255)
    relationship: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    address: Optional[str] = Field(None, max_length=500)


class EmergencyContactCreate(EmergencyContactBase):
    """Schema for creating emergency contact"""
    pass


class EmergencyContactResponse(EmergencyContactBase):
    """Schema for emergency contact response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientInsuranceBase(BaseModel):
    """Base patient insurance schema"""
    insurance_type: InsuranceType
    insurance_number: Optional[str] = Field(None, max_length=100)
    member_name: Optional[str] = Field(None, max_length=255)
    expiry_date: Optional[date] = None


class PatientInsuranceCreate(PatientInsuranceBase):
    """Schema for creating patient insurance"""
    pass


class PatientInsuranceResponse(PatientInsuranceBase):
    """Schema for patient insurance response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientBase(BaseModel):
    """Base patient schema with common fields"""
    full_name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    gender: Gender
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    blood_type: Optional[BloodType] = BloodType.NONE
    marital_status: Optional[MaritalStatus] = None
    religion: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    photo_url: Optional[str] = Field(None, max_length=500)


class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    nik: str = Field(..., min_length=16, max_length=16, description="16-digit Indonesian ID number")
    emergency_contacts: List[EmergencyContactCreate] = Field(default_factory=list, max_items=5)
    insurance_policies: List[PatientInsuranceCreate] = Field(default_factory=list, max_items=3)

    @validator('nik')
    def validate_nik(cls, v):
        """Validate NIK is exactly 16 digits and numeric only"""
        if not v.isdigit():
            raise ValueError('NIK must contain only digits')
        if len(v) != 16:
            raise ValueError('NIK must be exactly 16 digits')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        """Validate Indonesian phone format"""
        if v is None:
            return v
        cleaned = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits')
        if not (cleaned.startswith('0') or cleaned.startswith('62')):
            raise ValueError('Phone number must start with 0 or 62')
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        return v

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate reasonable age range (0-150 years)"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 0:
            raise ValueError('Date of birth cannot be in the future')
        if age > 150:
            raise ValueError('Date of birth indicates age over 150 years')
        return v


class PatientUpdate(BaseModel):
    """Schema for updating a patient (all fields optional)"""
    nik: Optional[str] = Field(None, min_length=16, max_length=16)
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=10)
    blood_type: Optional[BloodType] = None
    marital_status: Optional[MaritalStatus] = None
    religion: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=100)
    photo_url: Optional[str] = Field(None, max_length=500)
    emergency_contacts: Optional[List[EmergencyContactCreate]] = None
    insurance_policies: Optional[List[PatientInsuranceCreate]] = None

    @validator('nik')
    def validate_nik(cls, v):
        """Validate NIK is exactly 16 digits and numeric only"""
        if v is None:
            return v
        if not v.isdigit():
            raise ValueError('NIK must contain only digits')
        if len(v) != 16:
            raise ValueError('NIK must be exactly 16 digits')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        """Validate Indonesian phone format"""
        if v is None:
            return v
        cleaned = v.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits')
        if not (cleaned.startswith('0') or cleaned.startswith('62')):
            raise ValueError('Phone number must start with 0 or 62')
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise ValueError('Phone number must be between 10-15 digits')
        return v

    @validator('date_of_birth')
    def validate_date_of_birth(cls, v):
        """Validate reasonable age range (0-150 years)"""
        if v is None:
            return v
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 0:
            raise ValueError('Date of birth cannot be in the future')
        if age > 150:
            raise ValueError('Date of birth indicates age over 150 years')
        return v


class PatientResponse(PatientBase):
    """Schema for full patient data response"""
    id: int
    medical_record_number: str
    nik: Optional[str]
    is_active: bool
    emergency_contacts: List[EmergencyContactResponse] = Field(default_factory=list)
    insurance_policies: List[PatientInsuranceResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schema for paginated patient list response"""
    items: List[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DuplicatePatientWarning(BaseModel):
    """Schema for duplicate patient warning"""
    is_duplicate: bool
    existing_patient: Optional[PatientResponse] = None
    message: str


class PatientCheckInResponse(BaseModel):
    """Schema for patient check-in response"""
    patient: PatientResponse
    queue_number: Optional[str] = None
    check_in_time: datetime
    message: str
    last_visit: Optional[datetime] = None
    insurance_status: Optional[str] = None


class PatientLookupResponse(BaseModel):
    """Schema for enhanced patient lookup response"""
    patient: PatientResponse
    last_visit_date: Optional[datetime] = None
    last_diagnoses: Optional[list] = []
    allergies: Optional[list] = []
    insurance_status: str = "Unknown"
    has_unpaid_bills: bool = False
