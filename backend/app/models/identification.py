"""Identification System Integration Models for STORY-024-09

This module provides database models for:
- KTP-el (Electronic ID) integration
- BPJS card validation
- Face recognition verification
- Biometric data management
- ID verification tracking

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class VerificationStatus:
    """Verification status constants"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    NOT_VERIFIED = "not_verified"
    FAILED = "failed"
    EXPIRED = "expired"


class MatchScore:
    """Match score thresholds"""
    EXCELLENT = 0.95
    GOOD = 0.85
    FAIR = 0.70
    POOR = 0.50


class IDVerification(Base):
    """ID verification tracking model

    Stores all ID verification attempts and results.
    """
    __tablename__ = "id_verifications"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(100), unique=True, nullable=False, index=True, comment="Verification ID")

    # Entity mapping
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True, comment="Patient ID")
    verification_type = Column(String(50), nullable=False, index=True, comment="Verification type (ktp_el, bpjs, face, fingerprint)")

    # ID information
    id_number = Column(String(100), nullable=False, index=True, comment="ID number (NIK/BPJS)")
    id_name = Column(String(255), nullable=False, comment="Name on ID")
    id_dob = Column(DateTime(timezone=True), nullable=True, comment="Date of birth from ID")
    id_gender = Column(String(10), nullable=True, comment="Gender from ID")
    id_address = Column(Text, nullable=True, comment="Address from ID")

    # Verification details
    verification_source = Column(String(100), nullable=False, comment="Verification source (dukcapil, bpjs, internal)")
    verification_method = Column(String(50), nullable=False, comment="Verification method (api, manual, biometric)")
    request_data = Column(JSON, nullable=True, comment="Request payload")
    response_data = Column(JSON, nullable=True, comment="Response data")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default=VerificationStatus.PENDING, comment="Verification status")
    match_score = Column(Float, nullable=True, comment="Match score (0-1)")
    match_confidence = Column(String(20), nullable=True, comment="Match confidence (excellent, good, fair, poor)")
    is_match = Column(Boolean, nullable=True, comment="Whether ID matches provided data")

    # Additional data
    photo_url = Column(String(500), nullable=True, comment="Photo URL from ID")
    photo_data = Column(Text, nullable=True, comment="Base64 photo data")
    biometric_data = Column(JSON, nullable=True, comment="Biometric template data")
    biometric_quality = Column(Float, nullable=True, comment="Biometric quality score")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=True, comment="Error message")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")

    # Metadata
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Verified by (manual)")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="Verification timestamp")
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="Verification expiration")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])

    __table_args__ = (
        {"extend_existing": True, "comment": "ID verification tracking"},
    )


class KTPData(Base):
    """KTP-el data cache model

    Stores cached KTP-el data from Dukcapil API.
    """
    __tablename__ = "ktp_data_cache"

    id = Column(Integer, primary_key=True, index=True)
    nik = Column(String(16), unique=True, nullable=False, index=True, comment="NIK (16 digits)")

    # Personal data from KTP-el
    full_name = Column(String(255), nullable=False, comment="Full name")
    place_of_birth = Column(String(100), nullable=True, comment="Place of birth")
    date_of_birth = Column(DateTime(timezone=True), nullable=False, comment="Date of birth")
    gender = Column(String(10), nullable=False, comment="Gender (LAKILAKI/PEREMPUAN)")
    blood_type = Column(String(5), nullable=True, comment="Blood type")
    address = Column(Text, nullable=False, comment="Full address")
    rt = Column(String(5), nullable=True, comment="RT (neighborhood)")
    rw = Column(String(5), nullable=True, comment="RW (hamlet)")
    kelurahan = Column(String(100), nullable=True, comment="Village")
    kecamatan = Column(String(100), nullable=True, comment="District")
    kabupaten_kota = Column(String(100), nullable=True, comment="Regency/City")
    province = Column(String(100), nullable=True, comment="Province")
    postal_code = Column(String(10), nullable=True, comment="Postal code")

    # Marital and religion
    marital_status = Column(String(50), nullable=True, comment="Marital status")
    religion = Column(String(50), nullable=True, comment="Religion")
    occupation = Column(String(100), nullable=True, comment="Occupation")
    nationality = Column(String(50), nullable=False, default="WNI", comment="Nationality")

    # Validity
    is_valid = Column(Boolean, nullable=False, default=True, comment="Whether NIK is valid")
    is_active = Column(Boolean, nullable=False, default=True, comment="Whether NIK is active (not deceased)")
    validation_date = Column(DateTime(timezone=True), nullable=False, comment="When validated")
    expires_at = Column(DateTime(timezone=True), nullable=True, comment="Cache expiration")

    # Family data (KK)
    kk_number = Column(String(16), nullable=True, index=True, comment="Family card number")
    family_relationship = Column(String(50), nullable=True, comment="Relationship to head of family")
    family_members = Column(JSON, nullable=True, comment="Family members list")

    # Photo
    photo_url = Column(String(500), nullable=True, comment="Photo URL")
    photo_data = Column(Text, nullable=True, comment="Base64 photo data")

    # Metadata
    data_source = Column(String(100), nullable=False, comment="Data source (dukcapil_api)")
    api_response = Column(JSON, nullable=True, comment="Full API response")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "KTP-el cached data"},
    )


class BPJSCardValidation(Base):
    """BPJS card validation model

    Stores BPJS card validation results.
    """
    __tablename__ = "bpjs_card_validations"

    id = Column(Integer, primary_key=True, index=True)
    validation_id = Column(String(100), unique=True, nullable=False, index=True, comment="Validation ID")

    # Entity mapping
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True, comment="Patient ID")

    # BPJS card information
    bpjs_card_number = Column(String(13), unique=True, nullable=False, index=True, comment="BPJS card number (13 digits)")
    bpjs_name = Column(String(255), nullable=False, comment="Name on BPJS card")
    nik = Column(String(16), nullable=False, index=True, comment="NIK from BPJS")
    bpjs_member_id = Column(String(50), nullable=True, comment="BPJS member ID")

    # Membership details
    membership_tier = Column(String(20), nullable=False, comment="Membership tier (Kelas 1, 2, 3)")
    membership_type = Column(String(50), nullable=True, comment="Membership type (PBI, Non-PBI)")
    membership_status = Column(String(50), nullable=False, index=True, comment="Membership status (ACTIVE, SUSPENDED, TERMINATED)")
    membership_start_date = Column(DateTime(timezone=True), nullable=True, comment="Membership start date")
    membership_end_date = Column(DateTime(timezone=True), nullable=True, comment="Membership end date")

    # Contribution status
    contribution_status = Column(String(50), nullable=True, comment="Contribution payment status")
    last_contribution_date = Column(DateTime(timezone=True), nullable=True, comment="Last contribution payment date")
    arrear_count = Column(Integer, nullable=False, default=0, comment="Number of months in arrears")

    # Family dependency
    is_head_of_family = Column(Boolean, nullable=False, default=False, comment="Is head of family")
    family_head_nik = Column(String(16), nullable=True, comment="Family head NIK")
    family_members = Column(JSON, nullable=True, comment="Dependent family members")
    dependency_number = Column(Integer, nullable=True, comment="Dependency number in family")

    # Facility info
    faskes_tier_1 = Column(String(255), nullable=True, comment="First-tier facility (Puskesmas)")
    faskes_tier_2 = Column(String(255), nullable=True, comment="Second-tier facility (RS)")
    faskes_tier_3 = Column(String(255), nullable=True, comment="Third-tier facility (RS)")
    default_faskes = Column(String(255), nullable=True, comment="Default facility")

    # Verification
    is_verified = Column(Boolean, nullable=False, default=False, comment="Whether card is verified")
    verification_date = Column(DateTime(timezone=True), nullable=True, comment="Verification date")
    verification_source = Column(String(100), nullable=True, comment="Verification source")
    match_score = Column(Float, nullable=True, comment="Match score with provided data")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=True, comment="Error message")

    # Metadata
    api_response = Column(JSON, nullable=True, comment="Full API response")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])

    __table_args__ = (
        {"extend_existing": True, "comment": "BPJS card validation records"},
    )


class FaceRecognition(Base):
    """Face recognition verification model

    Stores face recognition verification attempts.
    """
    __tablename__ = "face_recognition_verifications"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(100), unique=True, nullable=False, index=True, comment="Verification ID")

    # Entity mapping
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True, comment="Patient ID")
    id_verification_id = Column(Integer, ForeignKey("id_verifications.id"), nullable=True, comment="Related ID verification")

    # Images
    source_image_url = Column(String(500), nullable=True, comment="Source image URL (from ID)")
    source_image_data = Column(Text, nullable=True, comment="Base64 source image data")
    captured_image_url = Column(String(500), nullable=True, comment="Captured image URL")
    captured_image_data = Column(Text, nullable=True, comment="Base64 captured image data")

    # Face detection
    face_detected = Column(Boolean, nullable=True, comment="Whether face was detected")
    face_count = Column(Integer, nullable=True, comment="Number of faces detected")
    face_coordinates = Column(JSON, nullable=True, comment="Face bounding boxes")
    face_landmarks = Column(JSON, nullable=True, comment="Face landmarks")

    # Recognition results
    match_score = Column(Float, nullable=False, comment="Match score (0-1)")
    match_confidence = Column(String(20), nullable=False, comment="Match confidence level")
    is_match = Column(Boolean, nullable=False, index=True, comment="Whether faces match")
    similarity_score = Column(Float, nullable=True, comment="Similarity score")

    # Liveness detection
    liveness_check = Column(Boolean, nullable=False, default=False, comment="Liveness check performed")
    liveness_score = Column(Float, nullable=True, comment="Liveness confidence score")
    is_live = Column(Boolean, nullable=True, comment="Whether image is live (not spoofed)")
    spoof_detection = Column(JSON, nullable=True, comment="Spoof detection details")

    # Quality metrics
    image_quality = Column(Float, nullable=True, comment="Image quality score")
    brightness = Column(Float, nullable=True, comment="Image brightness")
    sharpness = Column(Float, nullable=True, comment="Image sharpness")
    blur_detected = Column(Boolean, nullable=True, comment="Blur detected")
    lighting_condition = Column(String(20), nullable=True, comment="Lighting condition (good, fair, poor)")

    # Processing
    processing_time_ms = Column(Integer, nullable=True, comment="Processing time in milliseconds")
    model_version = Column(String(50), nullable=True, comment="Face recognition model version")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=True, comment="Error message")

    # Metadata
    verified_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])
    id_verification = relationship("IDVerification", foreign_keys=[id_verification_id])

    __table_args__ = (
        {"extend_existing": True, "comment": "Face recognition verification records"},
    )


class BiometricData(Base):
    """Biometric data storage model

    Stores biometric templates for fingerprint, iris, etc.
    """
    __tablename__ = "biometric_data"

    id = Column(Integer, primary_key=True, index=True)
    biometric_id = Column(String(100), unique=True, nullable=False, index=True, comment="Biometric ID")

    # Entity mapping
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    biometric_type = Column(String(50), nullable=False, index=True, comment="Biometric type (fingerprint, iris, face)")

    # Biometric data
    template_data = Column(JSON, nullable=False, comment="Biometric template data")
    template_format = Column(String(50), nullable=False, comment="Template format (ISO_19794_2, etc.)")
    template_version = Column(String(20), nullable=True, comment="Template version")
    quality_score = Column(Float, nullable=False, comment="Quality score (0-1)")

    # For fingerprint
    finger_position = Column(String(20), nullable=True, comment="Finger position (thumb, index, etc.)")
    hand = Column(String(10), nullable=True, comment="Hand (left, right)")
    image_data = Column(Text, nullable=True, comment="Base64 image data")

    # For iris
    eye_position = Column(String(10), nullable=True, comment="Eye position (left, right)")

    # Capture details
    capture_device = Column(String(100), nullable=True, comment="Capture device identifier")
    capture_date = Column(DateTime(timezone=True), nullable=False, comment="Capture date")
    capture_operator = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Operator who captured")

    # Verification
    is_verified = Column(Boolean, nullable=False, default=False, comment="Whether biometric is verified")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="Verification date")
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Verified by")

    # Status
    status = Column(String(50), nullable=False, index=True, default="active", comment="Status")
    is_primary = Column(Boolean, nullable=False, default=False, comment="Primary biometric for this type")

    # Security
    encrypted = Column(Boolean, nullable=False, default=True, comment="Whether data is encrypted")
    encryption_key_id = Column(String(100), nullable=True, comment="Encryption key identifier")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code from capture")
    error_message = Column(Text, nullable=True, comment="Error message from capture")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])

    __table_args__ = (
        {"extend_existing": True, "comment": "Biometric data storage"},
    )


class BiometricVerification(Base):
    """Biometric verification tracking model

    Tracks biometric verification attempts.
    """
    __tablename__ = "biometric_verifications"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(100), unique=True, nullable=False, index=True, comment="Verification ID")

    # Entity mapping
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True, comment="Patient ID")
    biometric_data_id = Column(Integer, ForeignKey("biometric_data.id"), nullable=False, comment="Biometric data ID")

    # Verification details
    verification_type = Column(String(50), nullable=False, comment="Verification type (fingerprint, iris, face)")
    captured_template = Column(JSON, nullable=False, comment="Captured template data")

    # Results
    match_score = Column(Float, nullable=False, comment="Match score (0-1)")
    match_confidence = Column(String(20), nullable=False, comment="Match confidence level")
    is_match = Column(Boolean, nullable=False, index=True, comment="Whether biometrics match")

    # Thresholds
    threshold_used = Column(Float, nullable=False, comment="Match threshold used")

    # Processing
    processing_time_ms = Column(Integer, nullable=True, comment="Processing time in milliseconds")
    matching_algorithm = Column(String(50), nullable=True, comment="Matching algorithm used")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=True, comment="Error message")

    # Metadata
    verified_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    patient = relationship("Patient", foreign_keys=[patient_id])
    biometric_data = relationship("BiometricData", foreign_keys=[biometric_data_id])

    __table_args__ = (
        {"extend_existing": True, "comment": "Biometric verification records"},
    )


class IdentificationConfig(Base):
    """Identification system configuration model

    Stores configuration for ID verification systems.
    """
    __tablename__ = "identification_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="Configuration key")

    # Configuration
    config_type = Column(String(50), nullable=False, index=True, comment="Configuration type (dukcapil, bpjs, face, fingerprint)")
    config_name = Column(String(255), nullable=False, comment="Configuration name")
    config_value = Column(JSON, nullable=False, comment="Configuration value")

    # API settings
    api_endpoint = Column(String(500), nullable=True, comment="API endpoint URL")
    auth_type = Column(String(50), nullable=True, comment="Authentication type")
    auth_credentials = Column(JSON, nullable=True, comment="Authentication credentials (encrypted)")

    # Rate limiting
    rate_limit = Column(Integer, nullable=True, comment="Rate limit (requests per minute)")
    rate_limit_window = Column(Integer, nullable=True, comment="Rate limit window in seconds")

    # Cache settings
    cache_ttl = Column(Integer, nullable=True, comment="Cache TTL in seconds")

    # Thresholds
    match_threshold = Column(Float, nullable=True, comment="Default match threshold")
    face_match_threshold = Column(Float, nullable=True, comment="Face match threshold")
    fingerprint_match_threshold = Column(Float, nullable=True, comment="Fingerprint match threshold")

    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Whether config is active")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Identification system configuration"},
    )
