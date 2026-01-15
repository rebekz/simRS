"""Message Transformation Models for STORY-024-10

This module provides database models for:
- HL7 to FHIR transformation rules
- Field mappings between formats
- Terminology mappings
- Transformation logs and history

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


class TransformationDirection:
    """Transformation direction constants"""
    HL7_TO_FHIR = "hl7_to_fhir"
    FHIR_TO_HL7 = "fhir_to_hl7"
    HL7_TO_HL7 = "hl7_to_hl7"
    FHIR_TO_FHIR = "fhir_to_fhir"


class TransformationStatus:
    """Transformation status constants"""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"


class MappingType:
    """Mapping type constants"""
    DIRECT = "direct"
    LOOKUP = "lookup"
    CONCATENATION = "concatenation"
    CONDITIONAL = "conditional"
    CUSTOM = "custom"
    DEFAULT_VALUE = "default_value"


class TransformationRule(Base):
    """Transformation rule model

    Defines high-level transformation rules between message formats.
    """
    __tablename__ = "transformation_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(100), unique=True, nullable=False, index=True, comment="Rule ID")
    rule_name = Column(String(255), nullable=False, comment="Rule name")
    rule_code = Column(String(100), unique=True, nullable=False, index=True, comment="Rule code")

    # Transformation type
    source_format = Column(String(20), nullable=False, index=True, comment="Source format (HL7, FHIR)")
    target_format = Column(String(20), nullable=False, index=True, comment="Target format (HL7, FHIR)")
    transformation_type = Column(String(50), nullable=False, index=True, comment="Transformation type (ADT, ORM, ORU, etc.)")
    direction = Column(String(20), nullable=False, index=True, comment="Transformation direction")

    # Configuration
    transformation_config = Column(JSON, nullable=False, comment="Transformation configuration")
    pre_processing_script = Column(Text, nullable=True, comment="Pre-processing script")
    post_processing_script = Column(Text, nullable=True, comment="Post-processing script")

    # Validation
    validation_rules = Column(JSON, nullable=True, comment="Validation rules")
    required_fields = Column(JSON, nullable=True, comment="Required fields list")

    # Status
    status = Column(String(50), nullable=False, index=True, default=TransformationStatus.DRAFT, comment="Rule status")
    version = Column(Integer, nullable=False, default=1, comment="Rule version")
    is_published = Column(Boolean, nullable=False, default=False, comment="Whether rule is published")

    # Testing
    test_data = Column(JSON, nullable=True, comment="Test data for validation")
    expected_output = Column(JSON, nullable=True, comment="Expected output for testing")

    # Metadata
    description = Column(Text, nullable=True, comment="Rule description")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True, comment="Published timestamp")
    published_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Published by")

    # Relationships
    field_mappings = relationship("FieldMapping", back_populates="transformation_rule", cascade="all, delete-orphan")
    transformation_logs = relationship("TransformationLog", back_populates="rule", cascade="all, delete-orphan")

    __table_args__ = (
        {"comment": "Transformation rule definitions"},
    )


class FieldMapping(Base):
    """Field mapping model

    Defines individual field mappings between source and target.
    """
    __tablename__ = "field_mappings"

    id = Column(Integer, primary_key=True, index=True)
    mapping_id = Column(String(100), unique=True, nullable=False, index=True, comment="Mapping ID")

    # Rule association
    transformation_rule_id = Column(Integer, ForeignKey("transformation_rules.id"), nullable=False, index=True, comment="Transformation rule ID")

    # Field paths
    source_path = Column(String(500), nullable=False, comment="Source field path (e.g., PID.5.1)")
    source_path_description = Column(String(255), nullable=True, comment="Source path description")
    target_path = Column(String(500), nullable=False, comment="Target field path (e.g., Patient.name[0].family)")
    target_path_description = Column(String(255), nullable=True, comment="Target path description")

    # Mapping configuration
    mapping_type = Column(String(50), nullable=False, index=True, comment="Mapping type (direct, lookup, conditional, etc.)")
    transformation_config = Column(JSON, nullable=True, comment="Transformation configuration")
    data_type_mapping = Column(String(50), nullable=True, comment="Data type conversion (string, integer, date, etc.)")

    # Default and custom logic
    default_value = Column(String(500), nullable=True, comment="Default value if source is empty")
    custom_function = Column(Text, nullable=True, comment="Custom transformation function")
    lookup_table = Column(String(100), nullable=True, comment="Lookup table name")

    # Conditional mapping
    condition = Column(JSON, nullable=True, comment="Conditional mapping logic")
    priority = Column(Integer, nullable=False, default=0, comment="Mapping priority (higher wins)")

    # Validation
    is_required = Column(Boolean, nullable=False, default=False, comment="Whether field is required")
    validation_pattern = Column(String(255), nullable=True, comment="Validation regex pattern")
    value_set = Column(JSON, nullable=True, comment="Allowed values set")

    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Whether mapping is active")

    # Metadata
    description = Column(Text, nullable=True, comment="Mapping description")
    notes = Column(Text, nullable=True, comment="Mapping notes")
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    # Relationships
    transformation_rule = relationship("TransformationRule", back_populates="field_mappings")

    __table_args__ = (
        {"comment": "Field mapping definitions"},
    )


class TerminologyMapping(Base):
    """Terminology mapping model

    Maps codes between different code systems.
    """
    __tablename__ = "terminology_mappings"

    id = Column(Integer, primary_key=True, index=True)
    mapping_id = Column(String(100), unique=True, nullable=False, index=True, comment="Mapping ID")

    # Code systems
    source_code_system = Column(String(100), nullable=False, index=True, comment="Source code system (ICD-9, LOINC, etc.)")
    source_code = Column(String(100), nullable=False, index=True, comment="Source code")
    source_display = Column(String(500), nullable=True, comment="Source display text")
    source_version = Column(String(20), nullable=True, comment="Source code system version")

    # Target code systems
    target_code_system = Column(String(100), nullable=False, index=True, comment="Target code system (ICD-10, SNOMED, etc.)")
    target_code = Column(String(100), nullable=False, index=True, comment="Target code")
    target_display = Column(String(500), nullable=True, comment="Target display text")
    target_version = Column(String(20), nullable=True, comment="Target code system version")

    # Mapping attributes
    equivalence = Column(String(20), nullable=False, comment="Mapping equivalence (equivalent, wider, narrower, etc.)")
    mapping_type = Column(String(50), nullable=True, comment="Mapping type (direct, grouped, complex)")
    mapping_relationship = Column(String(50), nullable=True, comment="Mapping relationship")

    # Additional info
    mapping_notes = Column(Text, nullable=True, comment="Mapping notes")
    mapping_status = Column(String(50), nullable=False, index=True, default="active", comment="Mapping status")
    effective_date = Column(DateTime(timezone=True), nullable=True, comment="Effective date")
    expiration_date = Column(DateTime(timezone=True), nullable=True, comment="Expiration date")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "Terminology mapping records"},
    )


class LookupTable(Base):
    """Lookup table model

    Stores lookup tables for field value mappings.
    """
    __tablename__ = "lookup_tables"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(String(100), unique=True, nullable=False, index=True, comment="Table ID")
    table_name = Column(String(255), nullable=False, comment="Table name")
    table_code = Column(String(100), unique=True, nullable=False, index=True, comment="Table code")

    # Configuration
    table_type = Column(String(50), nullable=False, index=True, comment="Table type (gender, marital_status, etc.)")
    table_description = Column(Text, nullable=True, comment="Table description")

    # Mappings
    lookup_mappings = Column(JSON, nullable=False, comment="Lookup mappings (source -> target)")

    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Whether table is active")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "Lookup tables for value mapping"},
    )


class TransformationLog(Base):
    """Transformation log model

    Logs all transformation executions for audit and debugging.
    """
    __tablename__ = "transformation_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(100), unique=True, nullable=False, index=True, comment="Log ID")

    # Rule association
    rule_id = Column(Integer, ForeignKey("transformation_rules.id"), nullable=True, index=True, comment="Transformation rule ID")

    # Message info
    message_id = Column(String(100), nullable=True, index=True, comment="Original message ID")
    correlation_id = Column(String(100), nullable=True, index=True, comment="Correlation ID")

    # Transformation details
    source_format = Column(String(20), nullable=False, index=True, comment="Source format")
    target_format = Column(String(20), nullable=False, index=True, comment="Target format")
    transformation_type = Column(String(50), nullable=True, comment="Transformation type")

    # Message content
    input_message = Column(JSON, nullable=False, comment="Input message content")
    output_message = Column(JSON, nullable=False, comment="Output message content")
    input_raw = Column(Text, nullable=True, comment="Raw input message")
    output_raw = Column(Text, nullable=True, comment="Raw output message")

    # Status
    status = Column(String(50), nullable=False, index=True, comment="Transformation status (success, error, partial)")
    has_warnings = Column(Boolean, nullable=False, default=False, comment="Whether transformation has warnings")
    has_errors = Column(Boolean, nullable=False, default=False, comment="Whether transformation has errors")

    # Performance
    processing_time_ms = Column(Integer, nullable=True, comment="Processing time in milliseconds")
    field_count = Column(Integer, nullable=True, comment="Number of fields transformed")

    # Errors and warnings
    errors = Column(JSON, nullable=True, comment="Transformation errors")
    warnings = Column(JSON, nullable=True, comment="Transformation warnings")
    missing_fields = Column(JSON, nullable=True, comment="List of missing required fields")

    # Validation
    validation_passed = Column(Boolean, nullable=True, comment="Whether validation passed")
    validation_errors = Column(JSON, nullable=True, comment="Validation errors")

    # Metadata
    transformed_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    transformed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Transformed by (manual)")

    # Relationships
    rule = relationship("TransformationRule", back_populates="transformation_logs")

    __table_args__ = (
        {"comment": "Transformation execution logs"},
    )


class TransformationTest(Base):
    """Transformation test model

    Stores test cases for transformation rules.
    """
    __tablename__ = "transformation_tests"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String(100), unique=True, nullable=False, index=True, comment="Test ID")

    # Rule association
    rule_id = Column(Integer, ForeignKey("transformation_rules.id"), nullable=False, index=True, comment="Transformation rule ID")

    # Test details
    test_name = Column(String(255), nullable=False, comment="Test name")
    test_description = Column(Text, nullable=True, comment="Test description")

    # Test data
    input_data = Column(JSON, nullable=False, comment="Test input data")
    expected_output = Column(JSON, nullable=False, comment="Expected output")

    # Test results
    last_run_at = Column(DateTime(timezone=True), nullable=True, comment="Last test run timestamp")
    last_run_status = Column(String(50), nullable=True, comment="Last test run status (passed, failed)")
    last_run_output = Column(JSON, nullable=True, comment="Last test run output")
    diff_details = Column(JSON, nullable=True, comment="Difference details")

    # Metadata
    is_active = Column(Boolean, nullable=False, default=True, comment="Whether test is active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "Transformation test cases"},
    )
