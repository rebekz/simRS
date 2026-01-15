"""FHIR R4 Resource Models for STORY-024-02

This module provides FHIR R4 resource models that map to existing
SIMRS database models for healthcare data exchange.

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base


class FHIRResourceType:
    """FHIR resource type constants"""
    PATIENT = "Patient"
    ENCOUNTER = "Encounter"
    CONDITION = "Condition"
    OBSERVATION = "Observation"
    SERVICEREQUEST = "ServiceRequest"
    MEDICATIONREQUEST = "MedicationRequest"
    MEDICATIONADMINISTRATION = "MedicationAdministration"
    DIAGNOSTICREPORT = "DiagnosticReport"
    PRACTITIONER = "Practitioner"
    ORGANIZATION = "Organization"
    LOCATION = "Location"
    IMMUNIZATION = "Immunization"
    DOCUMENTREFERENCE = "DocumentReference"


class FHIRResource(Base):
    """FHIR resource storage model

    Stores FHIR resources with version tracking and audit trail.
    Maps to SIMRS entities for data synchronization.
    """
    __tablename__ = "fhir_resources"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False, index=True, comment="FHIR resource type")
    resource_id = Column(String(100), nullable=False, index=True, comment="FHIR resource identifier")
    version_id = Column(String(100), nullable=False, index=True, comment="FHIR version identifier")

    # Entity mapping
    simrs_entity_type = Column(String(100), nullable=True, comment="SIMRS entity type (patient, encounter, etc.)")
    simrs_entity_id = Column(Integer, nullable=True, index=True, comment="SIMRS entity ID")

    # Resource content
    resource_json = Column(JSON, nullable=False, comment="FHIR resource as JSON")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Access control
    is_public = Column(Boolean, default=False, nullable=False, comment="Whether resource is publicly accessible")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, index=True, comment="Patient ID for compartment access")

    __table_args__ = (
        {"comment": "FHIR R4 resources for healthcare data exchange"},
    )


class FHIRSearchParameter(Base):
    """FHIR search parameter configuration model"""
    __tablename__ = "fhir_search_parameters"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False, index=True, comment="Resource type")
    parameter_name = Column(String(100), nullable=False, index=True, comment="Parameter name")
    parameter_type = Column(String(50), nullable=False, comment="Parameter type (string, token, reference, date, number)")

    # Mapping to SIMRS fields
    entity_field = Column(String(100), nullable=True, comment="SIMRS entity field name")
    json_path = Column(String(500), nullable=True, comment="JSON path for parameter extraction")

    # Configuration
    is_multi_valued = Column(Boolean, default=False, nullable=False, comment="Whether parameter supports multiple values")
    modifiers = Column(JSON, nullable=True, comment="Supported modifiers (contains, exact, etc.)")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    __table_args__ = (
        {"comment": "FHIR search parameter definitions"},
    )


class FHIRAuditEvent(Base):
    """FHIR access audit logging model"""
    __tablename__ = "fhir_audit_events"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False, index=True, comment="Resource type accessed")
    resource_id = Column(String(100), nullable=True, index=True, comment="Resource ID accessed")

    # Request details
    operation = Column(String(20), nullable=False, comment="FHIR operation (read, create, update, delete, search)")
    request_method = Column(String(10), nullable=False, comment="HTTP method")
    request_url = Column(Text, nullable=False, comment="Full request URL")

    # Authentication
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True, comment="User who made request")
    access_token = Column(String(500), nullable=True, comment="OAuth access token (hashed)")

    # Response details
    response_status = Column(Integer, nullable=False, comment="HTTP response status code")
    operation_outcome = Column(JSON, nullable=True, comment="FHIR OperationOutcome for errors")

    # Timing
    request_timestamp = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    response_duration_ms = Column(Integer, nullable=True, comment="Response duration in milliseconds")

    __table_args__ = (
        {"comment": "FHIR API access audit log"},
    )
