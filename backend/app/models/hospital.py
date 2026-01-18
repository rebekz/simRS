"""Hospital Configuration Models for STORY-039

This module provides SQLAlchemy models for:
- Hospital profile and branding
- Department management (wards, polyclinics, units)
- Room and bed configuration
- Doctor and staff directory
- Working hours and shifts
- Hospital branding (logo, letterhead)
"""
from datetime import time, date
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Time, Text, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


# =============================================================================
# Hospital Profile Model
# =============================================================================

class HospitalProfile(Base):
    """Hospital profile model - singleton table (only one row)"""
    __tablename__ = "hospital_profiles"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    name = Column(String(200), nullable=False)
    name_alias = Column(String(200), nullable=True)
    license_number = Column(String(100), nullable=False, unique=True)

    # Address
    address_line = Column(String(500), nullable=False)
    address_city = Column(String(100), nullable=False)
    address_province = Column(String(100), nullable=False)
    address_postal_code = Column(String(10), nullable=False)
    country = Column(String(100), nullable=False, default="Indonesia")

    # Contact
    phone = Column(String(50), nullable=False)
    phone_alternate = Column(String(50), nullable=True)
    email = Column(String(255), nullable=False)
    website = Column(String(255), nullable=True)

    # BPJS Information
    bpjs_ppk_code = Column(String(20), nullable=False, unique=True)
    bpjs_pcare_code = Column(String(20), nullable=True)
    bpjs_antrian_code = Column(String(20), nullable=True)

    # Hospital Classification
    hospital_class = Column(String(10), nullable=True)  # A, B, C, D
    hospital_type = Column(String(100), nullable=True)  # Umum, Khusus, Pendidikan
    ownership = Column(String(100), nullable=True)  # Pemerintah, Swasta, BUMN

    # Branding
    logo_url = Column(String(500), nullable=True)
    letterhead_url = Column(String(500), nullable=True)

    # Statistics (denormalized for quick access)
    total_departments = Column(Integer, nullable=False, default=0)
    total_beds = Column(Integer, nullable=False, default=0)
    total_doctors = Column(Integer, nullable=False, default=0)
    total_staff = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(Date, server_default=func.current_date(), nullable=False)
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.current_date(), nullable=False)

    # Relationships
    departments = relationship("Department", back_populates="hospital")
    branding = relationship("BrandingConfig", back_populates="hospital", uselist=False)
    staff_profiles = relationship("StaffProfile", back_populates="hospital")


# =============================================================================
# Department Model
# =============================================================================

class Department(Base):
    """Department model for wards, polyclinics, and units"""
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)

    # Hospital reference
    hospital_id = Column(Integer, ForeignKey("hospital_profiles.id"), nullable=False)

    # Basic Information
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    department_type = Column(
        SQLEnum("ward", "poli", "unit", "icu", "er", "or", name="departmenttype"),
        nullable=False
    )
    description = Column(Text, nullable=True)

    # Hierarchy
    parent_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    # Leadership
    head_of_department_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=True)

    # Location and Capacity
    location = Column(String(200), nullable=True)
    capacity = Column(Integer, nullable=True)  # Maximum capacity (for wards)
    current_count = Column(Integer, nullable=False, default=0)

    # Contact
    phone_extension = Column(String(20), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(Date, server_default=func.current_date(), nullable=False)
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.current_date(), nullable=False)

    # Table options - allow extending from user_management.Department
    __table_args__ = {'extend_existing': True}

    # Relationships
    hospital = relationship("HospitalProfile", back_populates="departments")
    parent_department = relationship("Department", remote_side=[id], backref="sub_departments")
    head_of_department = relationship("StaffProfile", foreign_keys=[head_of_department_id], backref="headed_departments")
    staff = relationship("StaffProfile", foreign_keys="StaffProfile.primary_department_id", back_populates="primary_department")
    working_hours = relationship("WorkingHours", back_populates="department", cascade="all, delete-orphan")
    users = relationship("User", back_populates="department")


# =============================================================================
# Staff Profile Model
# =============================================================================

class StaffProfile(Base):
    """Staff profile model extending user with hospital-specific information"""
    __tablename__ = "staff_profiles"

    id = Column(Integer, primary_key=True, index=True)

    # User reference
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    hospital_id = Column(Integer, ForeignKey("hospital_profiles.id"), nullable=False)

    # Employment Information
    employee_id = Column(String(50), nullable=False, unique=True)
    full_name = Column(String(100), nullable=False)
    role = Column(
        SQLEnum("doctor", "nurse", "midwife", "pharmacist", "lab_technician",
                "radiologist", "administrator", "receptionist", "security", "cleaning", "other",
                name="staffrole"),
        nullable=False
    )
    specialization = Column(
        SQLEnum("general_practitioner", "internist", "pediatrician", "surgeon",
                "obstetrician", "cardiologist", "neurologist", "orthopedist",
                "dermatologist", "psychiatrist", "ophthalmologist", "ent_specialist",
                "urologist", "anesthesiologist", "radiologist", "pathologist", "other",
                name="doctorspecialization"),
        nullable=True
    )

    # Professional Licenses
    sip_number = Column(String(100), nullable=True)  # Surat Izin Praktik
    str_number = Column(String(100), nullable=True)  # Surat Tanda Registrasi
    license_expiry_date = Column(Date, nullable=True)

    # Department Assignments
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    primary_department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    # Employment Details
    employment_type = Column(String(50), nullable=True)  # PNS, Honorer, Kontrak
    employment_status = Column(String(50), nullable=False, default="active")  # active, inactive, on_leave

    # Timestamps
    created_at = Column(Date, server_default=func.current_date(), nullable=False)
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.current_date(), nullable=False)

    # Relationships
    hospital = relationship("HospitalProfile", back_populates="staff_profiles")
    user = relationship("User", backref="staff_profile")
    department = relationship("Department", foreign_keys=[department_id], backref="staff_members")
    primary_department = relationship("Department", foreign_keys=[primary_department_id], backref="primary_staff")
    shift_assignments = relationship("ShiftAssignment", back_populates="staff", cascade="all, delete-orphan")


# =============================================================================
# Shift Configuration Model
# =============================================================================

class Shift(Base):
    """Shift model for working hour configuration"""
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)

    # Shift Information
    name = Column(String(50), nullable=False)  # e.g., "Pagi", "Siang", "Malam"
    shift_type = Column(
        SQLEnum("morning", "afternoon", "night", "flexible", "on_call", name="shifttype"),
        nullable=False
    )
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    break_duration_minutes = Column(Integer, nullable=False, default=0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(Date, server_default=func.current_date(), nullable=False)
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.current_date(), nullable=False)

    # Relationships
    assignments = relationship("ShiftAssignment", back_populates="shift", cascade="all, delete-orphan")


# =============================================================================
# Shift Assignment Model
# =============================================================================

class ShiftAssignment(Base):
    """Shift assignment model linking staff to shifts"""
    __tablename__ = "shift_assignments"

    id = Column(Integer, primary_key=True, index=True)

    # Staff and Shift
    staff_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)

    # Assignment Period
    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(Date, server_default=func.current_date(), nullable=False)

    # Relationships
    staff = relationship("StaffProfile", back_populates="shift_assignments")
    shift = relationship("Shift", back_populates="assignments")
    department = relationship("Department")


# =============================================================================
# Working Hours Model
# =============================================================================

class WorkingHours(Base):
    """Working hours model per department and day"""
    __tablename__ = "working_hours"

    id = Column(Integer, primary_key=True, index=True)

    # Department
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)

    # Day of Week (0=Monday, 6=Sunday)
    day_of_week = Column(Integer, nullable=False)

    # Working Hours
    is_working_day = Column(Boolean, nullable=False, default=True)
    opening_time = Column(Time, nullable=True)
    closing_time = Column(Time, nullable=True)

    # Relationships
    department = relationship("Department", back_populates="working_hours")


# =============================================================================
# Branding Configuration Model
# =============================================================================

class BrandingConfig(Base):
    """Branding configuration model for hospital customization"""
    __tablename__ = "branding_configs"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospital_profiles.id"), nullable=False, unique=True)

    # Colors (hex codes)
    primary_color = Column(String(7), nullable=False, default="#0ea5e9")
    secondary_color = Column(String(7), nullable=False, default="#06b6d4")
    accent_color = Column(String(7), nullable=False, default="#f97316")
    text_color = Column(String(7), nullable=False, default="#1f2937")
    background_color = Column(String(7), nullable=False, default="#ffffff")

    # Assets
    logo_url = Column(String(500), nullable=True)
    letterhead_url = Column(String(500), nullable=True)
    favicon_url = Column(String(500), nullable=True)

    # Custom Styling
    custom_css = Column(Text, nullable=True)

    # Timestamps
    updated_at = Column(Date, server_default=func.current_date(), onupdate=func.current_date(), nullable=False)

    # Relationships
    hospital = relationship("HospitalProfile", back_populates="branding")
