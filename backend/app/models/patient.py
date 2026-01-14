"""Patient models for STORY-006: New Patient Registration

This module defines the Patient, EmergencyContact, and PatientInsurance models
for managing patient information in the SIMRS system.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.session import Base


class Gender(str, Enum):
    """Gender options for patients"""
    MALE = "male"
    FEMALE = "female"


class BloodType(str, Enum):
    """Blood type options for patients"""
    A = "A"
    B = "B"
    AB = "AB"
    O = "O"
    NONE = "none"


class MaritalStatus(str, Enum):
    """Marital status options for patients"""
    SINGLE = "single"
    MARRIED = "married"
    WIDOWED = "widowed"
    DIVORCED = "divorced"


class InsuranceType(str, Enum):
    """Insurance type options for patients"""
    BPJS = "bpjs"
    ASURANSI = "asuransi"
    UMUM = "umum"


class Patient(Base):
    """Patient model for managing patient demographic and medical information

    This model stores comprehensive patient data including personal information,
    contact details, and medical demographics required for hospital registration.
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    medical_record_number = Column(String(20), unique=True, index=True, nullable=False, comment="No. RM - Medical Record Number")
    nik = Column(String(16), unique=True, index=True, nullable=True, comment="Indonesian National ID Number")
    full_name = Column(String(255), nullable=False, comment="Patient full name")
    date_of_birth = Column(Date, nullable=False, index=True, comment="Patient date of birth")
    gender = Column(SQLEnum(Gender), nullable=False, comment="Patient gender")
    phone = Column(String(20), index=True, nullable=True, comment="Primary phone number")
    email = Column(String(255), nullable=True, comment="Email address")
    address = Column(Text, nullable=True, comment="Residential address")
    city = Column(String(100), nullable=True, comment="City of residence")
    province = Column(String(100), nullable=True, comment="Province of residence")
    postal_code = Column(String(10), nullable=True, comment="Postal code")
    blood_type = Column(SQLEnum(BloodType), default=BloodType.NONE, nullable=True, comment="Blood type")
    marital_status = Column(SQLEnum(MaritalStatus), nullable=True, comment="Marital status")
    religion = Column(String(50), nullable=True, comment="Religion")
    occupation = Column(String(100), nullable=True, comment="Occupation")
    photo_url = Column(String(500), nullable=True, comment="URL to patient photo")
    country = Column(String(100), default="Indonesia", nullable=True, comment="Country of residence")
    bpjs_card_number = Column(String(20), nullable=True, index=True, comment="BPJS card number")
    satusehat_patient_id = Column(String(100), nullable=True, index=True, comment="SATUSEHAT FHIR Patient resource ID")
    is_active = Column(Boolean, default=True, nullable=False, comment="Patient active status")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    emergency_contacts = relationship("EmergencyContact", back_populates="patient", cascade="all, delete-orphan")
    insurance_policies = relationship("PatientInsurance", back_populates="patient", cascade="all, delete-orphan")
    encounters = relationship("Encounter", back_populates="patient", cascade="all, delete-orphan")


class EmergencyContact(Base):
    """Emergency contact model for patient emergency contacts

    This model stores emergency contact information associated with a patient.
    Multiple emergency contacts can be registered per patient.
    """
    __tablename__ = "emergency_contacts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to patient")
    name = Column(String(255), nullable=False, comment="Emergency contact full name")
    relationship = Column(String(100), nullable=False, comment="Relationship to patient (e.g., spouse, parent, sibling)")
    phone = Column(String(20), nullable=False, comment="Emergency contact phone number")
    address = Column(Text, nullable=True, comment="Emergency contact address")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    patient = relationship("Patient", back_populates="emergency_contacts")


class PatientInsurance(Base):
    """Patient insurance model for insurance policy information

    This model stores insurance details for patients including BPJS, private insurance,
    or general/self-pay information.
    """
    __tablename__ = "patient_insurances"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True, comment="Reference to patient")
    insurance_type = Column(SQLEnum(InsuranceType), nullable=False, comment="Type of insurance (BPJS, Asuransi, Umum)")
    insurance_number = Column(String(100), nullable=True, comment="Insurance policy/member number")
    member_name = Column(String(255), nullable=True, comment="Insurance member name if different from patient")
    expiry_date = Column(Date, nullable=True, comment="Insurance policy expiry date")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Record creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="Record last update timestamp")

    # Relationships
    patient = relationship("Patient", back_populates="insurance_policies")
