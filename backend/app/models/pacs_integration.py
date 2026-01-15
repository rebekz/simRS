"""PACS (Picture Archiving and Communication System) Integration Models for STORY-024-04

This module provides database models for:
- DICOM study tracking and management
- DICOM series and instance storage
- PACS configuration and mapping
- DICOM worklist management

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class PACSStudyStatus:
    """PACS study status constants"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class DICOMModality:
    """DICOM modality constants"""
    CR = "CR"  # Computed Radiography
    CT = "CT"  # Computed Tomography
    MR = "MR"  # Magnetic Resonance
    US = "US"  # Ultrasound
    XR = "XR"  # X-Ray
    RF = "RF"  # Radiofluoroscopy
    MG = "MG"  # Mammography
    PT = "PT"  # Positron Emission Tomography
    NM = "NM"  # Nuclear Medicine
    XA = "XA"  # X-Ray Angiography


class PACSStudy(Base):
    """PACS study tracking model

    Tracks radiology studies sent to external PACS systems with
    DICOM metadata and status tracking.
    """
    __tablename__ = "pacs_studies"

    id = Column(Integer, primary_key=True, index=True)
    study_id = Column(String(100), unique=True, nullable=False, index=True, comment="Internal study ID")
    study_instance_uid = Column(String(100), nullable=False, unique=True, index=True, comment="DICOM Study Instance UID")
    accession_number = Column(String(100), nullable=False, unique=True, index=True, comment="Accession number")

    # Entity mapping
    radiology_order_id = Column(Integer, ForeignKey("radiology_orders.id"), nullable=False, index=True, comment="SIMRS radiology order ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True, comment="Encounter ID")

    # Study details
    study_description = Column(String(255), nullable=True, comment="Study description")
    study_date = Column(DateTime(timezone=True), nullable=True, comment="Study date/time")
    modality = Column(String(10), nullable=False, index=True, comment="DICOM modality (CT, MR, US, etc.)")
    body_part_examined = Column(String(100), nullable=True, comment="Body part examined")
    performing_physician = Column(String(255), nullable=True, comment="Performing physician")
    reading_physician = Column(String(255), nullable=True, comment="Reading physician")

    # DICOM identifiers
    patient_id_dicom = Column(String(100), nullable=False, index=True, comment="DICOM Patient ID")
    patient_name_dicom = Column(String(255), nullable=False, comment="DICOM Patient Name")
    patient_birth_date = Column(DateTime(timezone=True), nullable=True, comment="DICOM Patient Birth Date")
    patient_sex = Column(String(10), nullable=True, comment="DICOM Patient Sex")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default=PACSStudyStatus.SCHEDULED, comment="Study status")
    status_history = Column(JSON, nullable=True, comment="Status change history")

    # Transmission tracking
    sent_to_pacs_at = Column(DateTime(timezone=True), nullable=True, comment="Sent to PACS timestamp")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="PACS acknowledgment timestamp")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Study completion timestamp")

    # Image tracking
    series_count = Column(Integer, nullable=False, default=0, comment="Number of series in study")
    instance_count = Column(Integer, nullable=False, default=0, comment="Number of instances in study")
    has_images = Column(Boolean, default=False, nullable=False, comment="Images available in PACS")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")
    last_retry_at = Column(DateTime(timezone=True), nullable=True, comment="Last retry timestamp")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    series = relationship("DICOMSeries", back_populates="study", cascade="all, delete-orphan")

    __table_args__ = (
        {"comment": "PACS study tracking for radiology integration"},
    )


class DICOMSeries(Base):
    """DICOM series storage model

    Stores series information from PACS with instance tracking.
    """
    __tablename__ = "dicom_series"

    id = Column(Integer, primary_key=True, index=True)
    series_id = Column(String(100), unique=True, nullable=False, index=True, comment="Internal series ID")
    series_instance_uid = Column(String(100), nullable=False, unique=True, index=True, comment="DICOM Series Instance UID")
    series_number = Column(Integer, nullable=False, comment="Series number")

    # Entity mapping
    pacs_study_id = Column(Integer, ForeignKey("pacs_studies.id"), nullable=False, index=True, comment="PACS study ID")

    # Series details
    modality = Column(String(10), nullable=False, index=True, comment="DICOM modality")
    series_description = Column(String(255), nullable=True, comment="Series description")
    body_part_examined = Column(String(100), nullable=True, comment="Body part examined")
    view_position = Column(String(50), nullable=True, comment="View position")

    # Image details
    instance_count = Column(Integer, nullable=False, default=0, comment="Number of instances in series")

    # DICOM attributes
    scan_options = Column(String(255), nullable=True, comment="Scan options")
    sequence_name = Column(String(255), nullable=True, comment="Sequence name")
    operator_name = Column(String(255), nullable=True, comment="Operator name")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    # Relationships
    study = relationship("PACSStudy", back_populates="series")
    instances = relationship("DICOMInstance", back_populates="series", cascade="all, delete-orphan")

    __table_args__ = (
        {"comment": "DICOM series storage"},
    )


class DICOMInstance(Base):
    """DICOM instance storage model

    Stores individual DICOM instance (image) information from PACS.
    """
    __tablename__ = "dicom_instances"

    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(String(100), unique=True, nullable=False, index=True, comment="Internal instance ID")
    sop_instance_uid = Column(String(100), nullable=False, unique=True, index=True, comment="DICOM SOP Instance UID")
    instance_number = Column(Integer, nullable=False, comment="Instance number")

    # Entity mapping
    dicom_series_id = Column(Integer, ForeignKey("dicom_series.id"), nullable=False, index=True, comment="DICOM series ID")

    # Instance details
    instance_description = Column(String(255), nullable=True, comment="Instance description")
    image_type = Column(String(100), nullable=True, comment="Image type")
    view_position = Column(String(50), nullable=True, comment="View position")

    # Image attributes
    rows = Column(Integer, nullable=True, comment="Number of rows")
    columns = Column(Integer, nullable=True, comment="Number of columns")
    bits_allocated = Column(Integer, nullable=True, comment="Bits allocated")
    bits_stored = Column(Integer, nullable=True, comment="Bits stored")
    high_bit = Column(Integer, nullable=True, comment="High bit")
    pixel_representation = Column(Integer, nullable=True, comment="Pixel representation")

    # Location in PACS
    pacs_url = Column(String(500), nullable=True, comment="PACS URL for retrieval")
    file_path = Column(String(500), nullable=True, comment="File path in PACS")
    file_size = Column(Integer, nullable=True, comment="File size in bytes")

    # Content date/time
    content_date = Column(DateTime(timezone=True), nullable=True, comment="Content date")
    content_time = Column(String(20), nullable=True, comment="Content time")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    # Relationships
    series = relationship("DICOMSeries", back_populates="instances")

    __table_args__ = (
        {"comment": "DICOM instance storage"},
    )


class PACSWorklist(Base):
    """PACS worklist entry model

    Modality Worklist entries for radiology orders.
    """
    __tablename__ = "pacs_worklist"

    id = Column(Integer, primary_key=True, index=True)
    worklist_id = Column(String(100), unique=True, nullable=False, index=True, comment="Worklist entry ID")

    # Entity mapping
    radiology_order_id = Column(Integer, ForeignKey("radiology_orders.id"), nullable=False, index=True, comment="Radiology order ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")

    # Worklist details
    accession_number = Column(String(100), nullable=False, unique=True, index=True, comment="Accession number")
    requested_procedure_id = Column(String(100), nullable=False, comment="Requested procedure ID")
    study_instance_uid = Column(String(100), nullable=False, unique=True, index=True, comment="Study Instance UID")

    # Procedure information
    requested_procedure_description = Column(String(255), nullable=False, comment="Requested procedure description")
    scheduled_procedure_step_description = Column(String(255), nullable=False, comment="Scheduled procedure step description")
    modality = Column(String(10), nullable=False, index=True, comment="DICOM modality")

    # Scheduling
    scheduled_date_time = Column(DateTime(timezone=True), nullable=False, comment="Scheduled date/time")
    scheduled_station_name = Column(String(255), nullable=True, comment="Scheduled station name")
    scheduled_station_class = Column(String(255), nullable=True, comment="Scheduled station class")
    scheduled_location = Column(String(255), nullable=True, comment="Scheduled location")

    # Patient information
    patient_id_dicom = Column(String(100), nullable=False, comment="DICOM Patient ID")
    patient_name_dicom = Column(String(255), nullable=False, comment="DICOM Patient Name")
    patient_birth_date = Column(DateTime(timezone=True), nullable=True, comment="Patient birth date")
    patient_sex = Column(String(10), nullable=True, comment="Patient sex")
    patient_weight = Column(Float, nullable=True, comment="Patient weight (kg)")
    patient_height = Column(Float, nullable=True, comment="Patient height (cm)")

    # Ordering physician
    referring_physician_name = Column(String(255), nullable=True, comment="Referring physician name")
    ordering_physician_name = Column(String(255), nullable=True, comment="Ordering physician name")

    # Status
    status = Column(String(50), nullable=False, index=True, default=PACSStudyStatus.SCHEDULED, comment="Worklist status")
    performed = Column(Boolean, default=False, nullable=False, index=True, comment="Procedure performed")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "PACS modality worklist entries"},
    )


class PACSMapping(Base):
    """PACS configuration and mapping model

    Stores mappings between SIMRS codes and PACS/AE titles
    for modalities, stations, and physicians.
    """
    __tablename__ = "pacs_mappings"

    id = Column(Integer, primary_key=True, index=True)
    mapping_type = Column(String(50), nullable=False, index=True, comment="Mapping type (modality, station, physician)")
    simrs_code = Column(String(100), nullable=False, index=True, comment="SIMRS code")
    simrs_name = Column(String(255), nullable=False, comment="SIMRS name")
    pacs_code = Column(String(100), nullable=False, comment="PACS/AE title")
    pacs_name = Column(String(255), nullable=False, comment="PACS name")

    # Additional mapping data
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether mapping is active")
    mapping_config = Column(JSON, nullable=True, comment="Additional mapping configuration")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "PACS system code mappings"},
    )


class PACSConfiguration(Base):
    """PACS system configuration model

    Stores connection settings and preferences for PACS integration.
    """
    __tablename__ = "pacs_configurations"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="Configuration key")

    # Connection settings
    host = Column(String(255), nullable=True, comment="PACS system host")
    port = Column(Integer, nullable=True, comment="PACS system port (DICOM)")
    ae_title = Column(String(100), nullable=True, comment="Application Entity title")
    facility = Column(String(100), nullable=True, comment="Facility name")

    # DICOM settings
    calling_ae_title = Column(String(100), nullable=False, default="SIMRS_PACS", comment="Calling AE title")
    dicom_version = Column(String(20), nullable=False, default="DICOM_3.0", comment="DICOM version")

    # Processing settings
    timeout_seconds = Column(Integer, nullable=False, default=30, comment="Connection timeout")
    max_associations = Column(Integer, nullable=False, default=10, comment="Maximum concurrent associations")
    retry_attempts = Column(Integer, nullable=False, default=3, comment="Retry attempts on failure")
    retry_delay_seconds = Column(Integer, nullable=False, default=60, comment="Delay between retries")
    enable_auto_retry = Column(Boolean, default=False, nullable=False, comment="Enable automatic retry")

    # Image retrieval settings
    retrieve_timeout_seconds = Column(Integer, nullable=False, default=120, comment="Image retrieval timeout")
    max_retrieve_size = Column(Integer, nullable=False, default=1073741824, comment="Max retrieve size (1GB)")

    # Worklist settings
    enable_worklist = Column(Boolean, default=True, nullable=False, comment="Enable modality worklist")
    worklist_update_interval = Column(Integer, nullable=False, default=60, comment="Worklist update interval (seconds)")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether configuration is active")
    test_mode = Column(Boolean, default=False, nullable=False, comment="Test mode (don't send real DICOM)")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "PACS system configuration"},
    )
