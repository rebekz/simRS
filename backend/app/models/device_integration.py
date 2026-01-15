"""Device/Instrument Integration Models for STORY-024-05

This module provides database models for:
- Medical device registration and configuration
- Device communication protocols
- Device data capture and storage
- Lab analyzer integration

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class DeviceType:
    """Device type constants"""
    LAB_ANALYZER = "lab_analyzer"
    VITALS_MONITOR = "vitals_monitor"
    ECG_MACHINE = "ecg_machine"
    PULSE_OXIMETER = "pulse_oximeter"
    GLUCOSE_METER = "glucose_meter"
    INFUSION_PUMP = "infusion_pump"
    VENTILATOR = "ventilator"
    SCALE = "scale"
    THERMOMETER = "thermometer"
    BLOOD_PRESSURE = "blood_pressure"
    OTHER = "other"


class DeviceProtocol:
    """Device communication protocol constants"""
    HL7 = "HL7"
    ASTM = "ASTM"
    DICOM = "DICOM"
    TCP_IP = "TCP_IP"
    SERIAL = "SERIAL"
    BLE = "BLE"
    WIFI = "WIFI"
    HTTP_API = "HTTP_API"
    OTHER = "other"


class DeviceStatus:
    """Device status constants"""
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class Device(Base):
    """Medical device registration model

    Tracks medical devices connected to SIMRS with communication
    settings and data capture configuration.
    """
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, nullable=False, index=True, comment="Internal device ID")
    serial_number = Column(String(100), nullable=False, unique=True, index=True, comment="Device serial number")

    # Device identification
    device_name = Column(String(255), nullable=False, comment="Device name")
    device_type = Column(String(50), nullable=False, index=True, comment="Device type")
    manufacturer = Column(String(255), nullable=True, comment="Manufacturer")
    model = Column(String(255), nullable=True, comment="Model number")
    firmware_version = Column(String(100), nullable=True, comment="Firmware version")

    # Location
    location = Column(String(255), nullable=True, comment="Device location")
    department = Column(String(100), nullable=True, index=True, comment="Department")
    station = Column(String(100), nullable=True, comment="Station/Room")

    # Communication settings
    protocol = Column(String(50), nullable=False, comment="Communication protocol")
    connection_params = Column(JSON, nullable=True, comment="Connection parameters (host, port, etc.)")
    endpoint_url = Column(String(500), nullable=True, comment="Device endpoint URL")

    # Authentication
    auth_type = Column(String(50), nullable=True, comment="Authentication type")
    auth_credentials = Column(JSON, nullable=True, comment="Encrypted credentials")

    # Data capture settings
    auto_capture = Column(Boolean, default=False, nullable=False, comment="Enable automatic data capture")
    capture_interval_seconds = Column(Integer, nullable=True, comment="Data capture interval")
    data_format = Column(String(50), nullable=True, comment="Expected data format")
    mapping_config = Column(JSON, nullable=True, comment="Data field mapping configuration")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default=DeviceStatus.OFFLINE, comment="Device status")
    last_heartbeat_at = Column(DateTime(timezone=True), nullable=True, comment="Last device heartbeat")
    last_communication_at = Column(DateTime(timezone=True), nullable=True, comment="Last successful communication")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Current error message")
    error_count = Column(Integer, nullable=False, default=0, comment="Number of errors")
    last_error_at = Column(DateTime(timezone=True), nullable=True, comment="Last error timestamp")

    # Calibration and maintenance
    last_calibration_at = Column(DateTime(timezone=True), nullable=True, comment="Last calibration date")
    next_calibration_due = Column(DateTime(timezone=True), nullable=True, comment="Next calibration due date")

    # Metadata
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether device is active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    data_records = relationship("DeviceData", back_populates="device", cascade="all, delete-orphan")

    __table_args__ = (
        {"comment": "Medical device registration"},
    )


class DeviceData(Base):
    """Device data capture model

    Stores data captured from medical devices with parsed
    measurements and observations.
    """
    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(100), unique=True, nullable=False, index=True, comment="Record ID")

    # Entity mapping
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True, comment="Device ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True, comment="Patient ID")
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True, comment="Encounter ID")

    # Data capture
    data_type = Column(String(100), nullable=False, index=True, comment="Type of data captured")
    raw_data = Column(Text, nullable=False, comment="Raw data from device")
    parsed_data = Column(JSON, nullable=True, comment="Parsed data in structured format")

    # Measurements (common fields)
    measurement_type = Column(String(100), nullable=True, comment="Measurement type")
    measurement_value = Column(Float, nullable=True, comment="Measurement value")
    measurement_unit = Column(String(50), nullable=True, comment="Unit of measure")
    reference_range_low = Column(Float, nullable=True, comment="Reference range low")
    reference_range_high = Column(Float, nullable=True, comment="Reference range high")

    # Vitals specific fields
    heart_rate = Column(Integer, nullable=True, comment="Heart rate (bpm)")
    blood_pressure_systolic = Column(Integer, nullable=True, comment="Blood pressure systolic")
    blood_pressure_diastolic = Column(Integer, nullable=True, comment="Blood pressure diastolic")
    respiratory_rate = Column(Integer, nullable=True, comment="Respiratory rate")
    temperature = Column(Float, nullable=True, comment="Temperature (C)")
    spo2 = Column(Float, nullable=True, comment="SpO2 (%)")
    weight = Column(Float, nullable=True, comment="Weight (kg)")
    height = Column(Float, nullable=True, comment="Height (cm)")
    blood_glucose = Column(Float, nullable=True, comment="Blood glucose (mg/dL)")

    # Lab analyzer specific fields
    test_code = Column(String(50), nullable=True, index=True, comment="Lab test code")
    test_name = Column(String(255), nullable=True, comment="Lab test name")
    sample_id = Column(String(100), nullable=True, comment="Sample identifier")
    analyzer_id = Column(String(100), nullable=True, comment="Analyzer identifier")

    # Quality flags
    is_abnormal = Column(Boolean, default=False, nullable=False, comment="Abnormal value flag")
    is_critical = Column(Boolean, default=False, nullable=False, comment="Critical value flag")
    quality_flag = Column(String(50), nullable=True, comment="Data quality flag")

    # Processing status
    is_imported = Column(Boolean, default=False, nullable=False, index=True, comment="Imported to SIMRS")
    imported_at = Column(DateTime(timezone=True), nullable=True, comment="Import timestamp")
    import_error = Column(Text, nullable=True, comment="Import error message")

    # Timestamps
    measured_at = Column(DateTime(timezone=True), nullable=True, comment="When measurement was taken")
    received_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False, comment="When data was received")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    # Relationships
    device = relationship("Device", back_populates="data_records")

    __table_args__ = (
        {"comment": "Device data capture storage"},
    )


class DeviceCommand(Base):
    """Device command queue model

    Stores commands sent to devices with execution tracking.
    """
    __tablename__ = "device_commands"

    id = Column(Integer, primary_key=True, index=True)
    command_id = Column(String(100), unique=True, nullable=False, index=True, comment="Command ID")

    # Entity mapping
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True, comment="Device ID")

    # Command details
    command_type = Column(String(100), nullable=False, index=True, comment="Command type")
    command_data = Column(JSON, nullable=True, comment="Command parameters")

    # Execution tracking
    status = Column(String(50), nullable=False, index=True, default="pending", comment="Command status")
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="Command sent timestamp")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="Device acknowledgment")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Command completion")
    response_data = Column(JSON, nullable=True, comment="Device response")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")

    # Priority
    priority = Column(Integer, nullable=False, default=0, comment="Command priority (higher first)")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "Device command queue"},
    )


class DeviceAlert(Base):
    """Device alert model

    Stores alerts generated by devices (malfunction, abnormal readings, etc.).
    """
    __tablename__ = "device_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(100), unique=True, nullable=False, index=True, comment="Alert ID")

    # Entity mapping
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True, comment="Device ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True, comment="Patient ID")

    # Alert details
    alert_type = Column(String(100), nullable=False, index=True, comment="Alert type")
    alert_severity = Column(String(50), nullable=False, index=True, comment="Alert severity (low, medium, high, critical)")
    alert_message = Column(Text, nullable=False, comment="Alert message")
    alert_code = Column(String(50), nullable=True, comment="Device alert code")

    # Alert data
    alert_data = Column(JSON, nullable=True, comment="Additional alert data")

    # Notification
    is_notified = Column(Boolean, default=False, nullable=False, comment="Notification sent")
    notified_at = Column(DateTime(timezone=True), nullable=True, comment="Notification timestamp")

    # Acknowledgment
    is_acknowledged = Column(Boolean, default=False, nullable=False, comment="Alert acknowledged")
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="Acknowledgment timestamp")

    # Resolution
    is_resolved = Column(Boolean, default=False, nullable=False, index=True, comment="Alert resolved")
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="Resolution timestamp")
    resolution_notes = Column(Text, nullable=True, comment="Resolution notes")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "Device alert storage"},
    )


class DeviceCalibration(Base):
    """Device calibration record model

    Tracks device calibration history and results.
    """
    __tablename__ = "device_calibrations"

    id = Column(Integer, primary_key=True, index=True)

    # Entity mapping
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True, comment="Device ID")

    # Calibration details
    calibration_type = Column(String(100), nullable=False, comment="Calibration type")
    calibration_date = Column(DateTime(timezone=True), nullable=False, comment="Calibration date/time")
    performed_by = Column(String(255), nullable=True, comment="Performed by")
    calibration_results = Column(JSON, nullable=True, comment="Calibration results")

    # Standards and references
    reference_standard = Column(String(255), nullable=True, comment="Reference standard used")
    tolerance_met = Column(Boolean, nullable=True, comment="Whether tolerance was met")

    # Next calibration
    next_calibration_due = Column(DateTime(timezone=True), nullable=True, comment="Next calibration due date")

    # Notes
    notes = Column(Text, nullable=True, comment="Calibration notes")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "Device calibration records"},
    )
