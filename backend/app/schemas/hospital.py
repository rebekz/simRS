"""Hospital Configuration Schemas for STORY-039

This module provides Pydantic schemas for:
- Hospital profile and branding
- Department management (wards, polyclinics, units)
- Room and bed configuration
- Doctor and staff directory
- Working hours and shifts
- Hospital branding (logo, letterhead)
"""
from typing import List, Optional, Dict
from datetime import time, date
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


# =============================================================================
# Department Enums
# =============================================================================

class DepartmentType(str, Enum):
    """Hospital department types"""
    WARD = "ward"  # Ruang rawat inap
    POLI = "poli"  # Poli rawat jalan
    UNIT = "unit"  # Unit penunjang (lab, radiologi, farmasi)
    ICU = "icu"  # Unit perawatan intensif
    ER = "er"  # Unit gawat darurat
    OR = "or"  # Ruang operasi


class ShiftType(str, Enum):
    """Working shift types"""
    MORNING = "morning"  # Pagi (07:00-14:00)
    AFTERNOON = "afternoon"  # Siang (14:00-21:00)
    NIGHT = "night"  # Malam (21:00-07:00)
    FLEXIBLE = "flexible"  # Fleksibel
    ON_CALL = "on_call"  # Siaga


class StaffRole(str, Enum):
    """Hospital staff roles"""
    DOCTOR = "doctor"
    NURSE = "nurse"
    MIDWIFE = "midwife"
    PHARMACIST = "pharmacist"
    LAB_TECHNICIAN = "lab_technician"
    RADIOLOGIST = "radiologist"
    ADMINISTRATOR = "administrator"
    RECEPTIONIST = "receptionist"
    SECURITY = "security"
    CLEANING = "cleaning"
    OTHER = "other"


class DoctorSpecialization(str, Enum):
    """Doctor specializations"""
    GENERAL_PRACTITIONER = "general_practitioner"  # Dokter umum
    INTERNIST = "internist"  # Penyakit dalam
    PEDIATRICIAN = "pediatrician"  # Anak
    SURGEON = "surgeon"  # Bedah
    OBSTETRICIAN = "obstetrician"  # Kandungan
    CARDIOLOGIST = "cardiologist"  # Jantung
    NEUROLOGIST = "neurologist"  # Saraf
    ORTHOPEDIST = "orthopedist"  # Tulang
    DERMATOLOGIST = "dermatologist"  # Kulit & kelamin
    PSYCHIATRIST = "psychiatrist"  # Jiwa
    OPHTHALMOLOGIST = "ophthalmologist"  # Mata
    ENT_SPECIALIST = "ent_specialist"  # THT
    UROLOGIST = "urologist"  # Urologi
    ANESTHESIOLOGIST = "anesthesiologist"  # Anestesi
    RADIOLOGIST = "radiologist"  # Radiologi
    PATHOLOGIST = "pathologist"  # Patologi anatomis
    OTHER = "other"


# =============================================================================
# Hospital Profile Schemas
# =============================================================================

class HospitalProfileBase(BaseModel):
    """Base hospital profile schema"""
    name: str = Field(..., min_length=2, max_length=200, description="Hospital name")
    name_alias: Optional[str] = Field(None, max_length=200, description="Hospital alias/abbreviation")
    license_number: str = Field(..., description="Hospital license number (IZIN OPERASIONAL)")

    # Address
    address_line: str = Field(..., description="Street address")
    address_city: str = Field(..., description="City/Kabupaten")
    address_province: str = Field(..., description="Province")
    address_postal_code: str = Field(..., description="Postal code")
    country: str = Field("Indonesia", description="Country")

    # Contact
    phone: str = Field(..., description="Main phone number")
    phone_alternate: Optional[str] = None
    email: EmailStr
    website: Optional[str] = None

    # BPJS Information
    bpjs_ppk_code: str = Field(..., description="BPJS PPK code (Kode Faskes)")
    bpjs_pcare_code: Optional[str] = None
    bpjs_antrian_code: Optional[str] = None

    # Hospital Classification
    hospital_class: Optional[str] = Field(None, description="Hospital class (A, B, C, D)")
    hospital_type: Optional[str] = Field(None, description="Hospital type (Umum, Khusus, Pendidikan, etc)")
    ownership: Optional[str] = Field(None, description="Ownership type (Pemerintah, Swasta, BUMN)")


class HospitalProfileCreate(HospitalProfileBase):
    """Schema for creating hospital profile"""
    pass


class HospitalProfileUpdate(BaseModel):
    """Schema for updating hospital profile"""
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    name_alias: Optional[str] = Field(None, max_length=200)
    license_number: Optional[str] = None
    address_line: Optional[str] = None
    address_city: Optional[str] = None
    address_province: Optional[str] = None
    address_postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    phone_alternate: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    bpjs_ppk_code: Optional[str] = None
    bpjs_pcare_code: Optional[str] = None
    bpjs_antrian_code: Optional[str] = None
    hospital_class: Optional[str] = None
    hospital_type: Optional[str] = None
    ownership: Optional[str] = None


class HospitalProfileResponse(HospitalProfileBase):
    """Schema for hospital profile response"""
    id: int
    logo_url: Optional[str] = None
    letterhead_url: Optional[str] = None

    # Statistics (denormalized for quick access)
    total_departments: int = 0
    total_beds: int = 0
    total_doctors: int = 0
    total_staff: int = 0

    # Timestamps
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# =============================================================================
# Department Schemas
# =============================================================================

class DepartmentBase(BaseModel):
    """Base department schema"""
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=1, max_length=20, description="Department code")
    department_type: DepartmentType
    description: Optional[str] = None
    parent_department_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    """Schema for creating a department"""
    head_of_department_id: Optional[int] = None
    location: Optional[str] = None
    capacity: Optional[int] = Field(None, ge=0, description="Maximum capacity (for wards)")


class DepartmentResponse(DepartmentBase):
    """Schema for department response"""
    id: int
    head_of_department_id: Optional[int] = None
    head_name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    current_count: int = 0  # Current patient/occupant count

    # Contact
    phone_extension: Optional[str] = None
    is_active: bool = True

    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# =============================================================================
# Staff Directory Schemas
# =============================================================================

class StaffProfileBase(BaseModel):
    """Base staff profile schema"""
    user_id: int
    employee_id: str = Field(..., description="Employee ID/NIP")
    full_name: str = Field(..., min_length=2, max_length=100)
    role: StaffRole
    specialization: Optional[DoctorSpecialization] = None
    sip_number: Optional[str] = Field(None, description="Surat Izin Praktik (SIP)")
    str_number: Optional[str] = Field(None, description="Surat Tanda Registrasi (STR)")


class StaffProfileCreate(StaffProfileBase):
    """Schema for creating staff profile"""
    department_id: Optional[int] = None
    primary_department_id: Optional[int] = None
    license_expiry_date: Optional[date] = None
    employment_type: Optional[str] = Field(None, description="PNS, Honorer, Kontrak, etc")
    employment_status: str = Field("active", description="active, inactive, on_leave")


class StaffProfileResponse(StaffProfileBase):
    """Schema for staff profile response"""
    id: int
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    primary_department_id: Optional[int] = None
    primary_department_name: Optional[str] = None
    license_expiry_date: Optional[date] = None
    employment_type: Optional[str] = None
    employment_status: str

    # Contact (denormalized from user)
    email: Optional[str] = None
    phone: Optional[str] = None

    # Assigned shifts
    assigned_shifts: List[str] = []

    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# =============================================================================
# Shift Configuration Schemas
# =============================================================================

class ShiftBase(BaseModel):
    """Base shift schema"""
    name: str = Field(..., min_length=2, max_length=50)
    shift_type: ShiftType
    start_time: time
    end_time: time
    break_duration_minutes: int = Field(0, ge=0, description="Break duration in minutes")


class ShiftCreate(ShiftBase):
    """Schema for creating a shift"""
    description: Optional[str] = None
    is_active: bool = True


class ShiftResponse(ShiftBase):
    """Schema for shift response"""
    id: int
    description: Optional[str] = None
    is_active: bool
    total_assigned_staff: int = 0

    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class ShiftAssignmentBase(BaseModel):
    """Base shift assignment schema"""
    staff_id: int
    shift_id: int
    department_id: Optional[int] = None
    effective_date: date
    expiry_date: Optional[date] = None


class ShiftAssignmentCreate(ShiftAssignmentBase):
    """Schema for creating shift assignment"""
    pass


class ShiftAssignmentResponse(ShiftAssignmentBase):
    """Schema for shift assignment response"""
    id: int
    staff_name: Optional[str] = None
    shift_name: Optional[str] = None
    department_name: Optional[str] = None
    is_active: bool = True

    created_at: date

    class Config:
        from_attributes = True


# =============================================================================
# Branding Schemas
# =============================================================================

class BrandingConfigBase(BaseModel):
    """Base branding configuration schema"""
    primary_color: str = Field("#0ea5e9", description="Primary color (hex)")
    secondary_color: str = Field("#06b6d4", description="Secondary color (hex)")
    accent_color: str = Field("#f97316", description="Accent color (hex)")
    text_color: str = Field("#1f2937", description="Text color (hex)")
    background_color: str = Field("#ffffff", description="Background color (hex)")


class BrandingConfigUpdate(BrandingConfigBase):
    """Schema for updating branding configuration"""
    logo_url: Optional[str] = None
    letterhead_url: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = Field(None, description="Custom CSS for additional styling")


class BrandingConfigResponse(BrandingConfigBase):
    """Schema for branding configuration response"""
    id: int
    hospital_id: int
    logo_url: Optional[str] = None
    letterhead_url: Optional[str] = None
    favicon_url: Optional[str] = None
    custom_css: Optional[str] = None

    updated_at: date

    class Config:
        from_attributes = True


# =============================================================================
# Configuration Summary Schema
# =============================================================================

class HospitalConfigurationSummary(BaseModel):
    """Schema for hospital configuration summary"""
    hospital_profile: HospitalProfileResponse
    total_departments: int
    departments_by_type: Dict[str, int]
    total_staff: int
    staff_by_role: Dict[str, int]
    total_shifts: int
    branding_configured: bool

    configuration_completion: float = Field(..., description="Completion percentage (0-100)")
    missing_configurations: List[str] = []


# =============================================================================
# Working Hours Schema
# =============================================================================

class WorkingHoursBase(BaseModel):
    """Base working hours schema"""
    department_id: int
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    is_working_day: bool = True
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None


class WorkingHoursCreate(WorkingHoursBase):
    """Schema for creating working hours"""
    pass


class WorkingHoursResponse(WorkingHoursBase):
    """Schema for working hours response"""
    id: int
    department_name: Optional[str] = None

    class Config:
        from_attributes = True
