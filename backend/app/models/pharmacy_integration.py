"""Pharmacy Integration Models for STORY-024-08

This module provides database models for:
- External pharmacy system connections
- Electronic prescription routing
- Medication dispensing integration
- Pharmacy inventory synchronization

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class PrescriptionStatus:
    """Prescription status constants"""
    PENDING = "pending"
    SENT_TO_PHARMACY = "sent_to_pharmacy"
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    PARTIALLY_DISPENSED = "partially_dispensed"
    DISPENSED = "dispensed"
    NOT_DISPENSED = "not_dispensed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    EXPIRED = "expired"


class DispenseStatus:
    """Dispense status constants"""
    PENDING = "pending"
    READY = "ready"
    DISPENSED = "dispensed"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class PharmacySystem(Base):
    """External pharmacy system registration model

    Stores connection details for external pharmacy systems
    and pharmacy management platforms.
    """
    __tablename__ = "pharmacy_systems"

    id = Column(Integer, primary_key=True, index=True)
    system_id = Column(String(100), unique=True, nullable=False, index=True, comment="Internal system ID")
    system_code = Column(String(100), unique=True, nullable=False, index=True, comment="System code")

    # System identification
    system_name = Column(String(255), nullable=False, comment="Pharmacy system name")
    system_type = Column(String(50), nullable=False, index=True, comment="System type (hospital, retail, mail_order)")
    organization = Column(String(255), nullable=True, comment="Organization name")
    pharmacy_id = Column(String(100), nullable=True, index=True, comment="Pharmacy ID")
    license_number = Column(String(100), nullable=True, comment="Pharmacy license number")

    # Contact information
    contact_name = Column(String(255), nullable=True, comment="Contact name")
    contact_email = Column(String(255), nullable=True, comment="Contact email")
    contact_phone = Column(String(50), nullable=True, comment="Contact phone")
    address = Column(String(500), nullable=True, comment="Physical address")

    # Connection settings
    protocol = Column(String(50), nullable=False, comment="Communication protocol")
    endpoint_url = Column(String(500), nullable=True, comment="Endpoint URL")
    auth_type = Column(String(50), nullable=True, comment="Authentication type")
    auth_credentials = Column(JSON, nullable=True, comment="Encrypted credentials")

    # Configuration
    ncpdp_config = Column(JSON, nullable=True, comment="NCPDP script configuration")
    edi_config = Column(JSON, nullable=True, comment="EDI configuration")
    mapping_config = Column(JSON, nullable=True, comment="Data mapping configuration")
    supported_formats = Column(JSON, nullable=True, comment="Supported formats (NCPDP, HL7, FHIR)")

    # Capabilities
    supports_e_prescribing = Column(Boolean, default=False, nullable=False, comment="Supports e-prescribing")
    supports_dispensing = Column(Boolean, default=False, nullable=False, comment="Supports dispensing integration")
    supports_inventory_sync = Column(Boolean, default=False, nullable=False, comment="Supports inventory sync")
    supports_refill_requests = Column(Boolean, default=False, nullable=False, comment="Supports refill requests")

    # Formulary
    formulary_id = Column(String(100), nullable=True, comment="Formulary ID")

    # Status
    status = Column(String(50), nullable=False, index=True, default="active", comment="Connection status")
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether system is active")
    is_primary = Column(Boolean, default=False, nullable=False, comment="Primary pharmacy")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Current error message")
    last_error_at = Column(DateTime(timezone=True), nullable=True, comment="Last error timestamp")

    # Testing
    test_mode = Column(Boolean, default=False, nullable=False, comment="Test mode flag")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    prescriptions = relationship("PrescriptionTransmission", back_populates="pharmacy_system", cascade="all, delete-orphan")

    __table_args__ = (
        {"extend_existing": True, "comment": "External pharmacy system connections"},
    )


class PrescriptionTransmission(Base):
    """Prescription transmission tracking model

    Tracks prescriptions sent to external pharmacy systems.
    """
    __tablename__ = "prescription_transmissions"

    id = Column(Integer, primary_key=True, index=True)
    transmission_id = Column(String(100), unique=True, nullable=False, index=True, comment="Transmission ID")
    prescription_number = Column(String(100), unique=True, nullable=False, index=True, comment="Prescription number")

    # Entity mapping
    pharmacy_system_id = Column(Integer, ForeignKey("pharmacy_systems.id"), nullable=False, index=True, comment="Pharmacy system ID")
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False, index=True, comment="SIMRS prescription ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    encounter_id = Column(Integer, ForeignKey("encounters.id"), nullable=True, index=True, comment="Encounter ID")

    # Prescriber information
    prescriber_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Prescriber ID")
    prescriber_npi = Column(String(50), nullable=True, comment="Prescriber NPI")
    prescriber_dea = Column(String(50), nullable=True, comment="Prescriber DEA number")

    # Patient information
    patient_name = Column(String(255), nullable=False, comment="Patient name")
    patient_dob = Column(DateTime(timezone=True), nullable=True, comment="Patient date of birth")
    patient_gender = Column(String(10), nullable=True, comment="Patient gender")
    patient_address = Column(JSON, nullable=True, comment="Patient address")

    # Insurance information
    primary_payer = Column(String(255), nullable=True, comment="Primary insurance payer")
    insurance_member_id = Column(String(100), nullable=True, comment="Insurance member ID")
    insurance_group_number = Column(String(100), nullable=True, comment="Insurance group number")

    # Medication details
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=True, index=True, comment="Medication ID")
    medication_name = Column(String(255), nullable=False, comment="Medication name")
    medication_code = Column(String(100), nullable=True, comment="Medication code (NDC, etc.)")
    generic_name = Column(String(255), nullable=True, comment="Generic name")
    dosage_form = Column(String(100), nullable=True, comment="Dosage form")
    strength = Column(String(100), nullable=True, comment="Medication strength")
    strength_unit = Column(String(50), nullable=True, comment="Strength unit")

    # Prescription details
    quantity = Column(Float, nullable=False, comment="Quantity prescribed")
    quantity_unit = Column(String(50), nullable=False, comment="Quantity unit")
    days_supply = Column(Integer, nullable=False, comment="Days supply")
    refills = Column(Integer, nullable=False, default=0, comment="Number of refills")
    refills_remaining = Column(Integer, nullable=False, default=0, comment="Refills remaining")

    # Sig/dosing instructions
    sig_text = Column(Text, nullable=False, comment="Sig instructions")
    dosage_instructions = Column(JSON, nullable=True, comment="Structured dosage instructions")
    route = Column(String(50), nullable=True, comment="Route of administration")
    frequency = Column(String(100), nullable=True, comment="Dosing frequency")

    # Clinical information
    diagnosis_code = Column(String(50), nullable=True, comment="Diagnosis code (ICD-10)")
    diagnosis_description = Column(String(255), nullable=True, comment="Diagnosis description")
    clinical_notes = Column(Text, nullable=True, comment="Clinical notes")

    # Transmission content
    prescription_data = Column(JSON, nullable=False, comment="Complete prescription data")
    ncpdp_script_content = Column(Text, nullable=True, comment="NCPDP script content")
    fhir_resource = Column(JSON, nullable=True, comment="FHIR MedicationRequest resource")
    hl7_message = Column(Text, nullable=True, comment="HL7 message content")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default=PrescriptionStatus.PENDING, comment="Prescription status")
    status_history = Column(JSON, nullable=True, comment="Status change history")

    # Transmission tracking
    sent_at = Column(DateTime(timezone=True), nullable=True, comment="Sent to pharmacy timestamp")
    received_at = Column(DateTime(timezone=True), nullable=True, comment="Received by pharmacy timestamp")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="Pharmacy acknowledgment timestamp")

    # Dispensing tracking
    dispensed_at = Column(DateTime(timezone=True), nullable=True, comment="Dispensed timestamp")
    quantity_dispensed = Column(Float, nullable=True, comment="Quantity actually dispensed")
    partial_dispense_count = Column(Integer, nullable=False, default=0, comment="Number of partial dispenses")

    # Pharmacy response
    pharmacy_response_code = Column(String(50), nullable=True, comment="Pharmacy response code")
    pharmacy_response_message = Column(Text, nullable=True, comment="Pharmacy response message")
    response_data = Column(JSON, nullable=True, comment="Complete response data")

    # Cancellation
    cancellation_reason = Column(Text, nullable=True, comment="Cancellation reason")
    cancelled_at = Column(DateTime(timezone=True), nullable=True, comment="Cancellation timestamp")
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Cancelled by")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=True, comment="Error message")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    pharmacy_system = relationship("PharmacySystem", back_populates="prescriptions")
    dispense_records = relationship("MedicationDispense", back_populates="prescription", cascade="all, delete-orphan")

    __table_args__ = (
        {"extend_existing": True, "comment": "Prescription transmission tracking"},
    )


class MedicationDispense(Base):
    """Medication dispense tracking model

    Tracks medication dispensing events from pharmacy systems.
    """
    __tablename__ = "medication_dispenses"

    id = Column(Integer, primary_key=True, index=True)
    dispense_id = Column(String(100), unique=True, nullable=False, index=True, comment="Dispense ID")

    # Entity mapping
    prescription_transmission_id = Column(Integer, ForeignKey("prescription_transmissions.id"), nullable=False, index=True, comment="Prescription transmission ID")
    pharmacy_system_id = Column(Integer, ForeignKey("pharmacy_systems.id"), nullable=False, index=True, comment="Pharmacy system ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=True, index=True, comment="Medication ID")

    # Dispense details
    dispense_number = Column(String(100), nullable=False, comment="Dispense number")
    dispense_date = Column(DateTime(timezone=True), nullable=False, comment="Dispense date")
    quantity_dispensed = Column(Float, nullable=False, comment="Quantity dispensed")
    days_supply = Column(Integer, nullable=False, comment="Days supply")
    refills_remaining = Column(Integer, nullable=False, comment="Refills remaining after dispense")

    # Medication information
    medication_name = Column(String(255), nullable=False, comment="Medication name")
    medication_code = Column(String(100), nullable=True, comment="Medication code")
    dosage_form = Column(String(100), nullable=True, comment="Dosage form")
    strength = Column(String(100), nullable=True, comment="Medication strength")
    strength_unit = Column(String(50), nullable=True, comment="Strength unit")

    # Dispensing details
    dispenser_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Dispenser ID")
    dispenser_name = Column(String(255), nullable=True, comment="Dispenser name")
    pharmacy_id = Column(String(100), nullable=True, comment="Pharmacy ID")

    # Pricing
    cost = Column(Float, nullable=True, comment="Medication cost")
    price = Column(Float, nullable=True, comment="Price charged")
    copay = Column(Float, nullable=True, comment="Patient copay amount")

    # Status
    status = Column(String(50), nullable=False, index=True, default=DispenseStatus.PENDING, comment="Dispense status")
    delivery_status = Column(String(50), nullable=True, comment="Delivery status")
    delivered_at = Column(DateTime(timezone=True), nullable=True, comment="Delivery timestamp")

    # Additional information
    lot_number = Column(String(100), nullable=True, comment="Lot number")
    expiration_date = Column(DateTime(timezone=True), nullable=True, comment="Expiration date")
    ndc = Column(String(100), nullable=True, comment="National Drug Code")
    dea_schedule = Column(String(10), nullable=True, comment="DEA schedule")

    # Notes
    dispense_notes = Column(Text, nullable=True, comment="Dispense notes")
    patient_counseling = Column(Text, nullable=True, comment="Patient counseling notes")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    prescription = relationship("PrescriptionTransmission", back_populates="dispense_records")

    __table_args__ = (
        {"extend_existing": True, "comment": "Medication dispense tracking"},
    )


class RefillRequest(Base):
    """Refill request model

    Tracks refill requests sent to pharmacies.
    """
    __tablename__ = "refill_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True, comment="Request ID")

    # Entity mapping
    prescription_transmission_id = Column(Integer, ForeignKey("prescription_transmissions.id"), nullable=False, index=True, comment="Original prescription transmission ID")
    pharmacy_system_id = Column(Integer, ForeignKey("pharmacy_systems.id"), nullable=False, index=True, comment="Pharmacy system ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True, comment="Patient ID")
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Requested by")

    # Request details
    refill_number = Column(Integer, nullable=False, comment="Refill number (1, 2, etc.)")
    quantity_requested = Column(Float, nullable=False, comment="Quantity requested")
    reason = Column(Text, nullable=True, comment="Reason for refill")

    # Status tracking
    status = Column(String(50), nullable=False, index=True, default="pending", comment="Request status")
    submitted_at = Column(DateTime(timezone=True), nullable=False, comment="Request submitted timestamp")
    responded_at = Column(DateTime(timezone=True), nullable=True, comment="Response timestamp")
    approved = Column(Boolean, nullable=True, comment="Refill approved")

    # Pharmacy response
    response_message = Column(Text, nullable=True, comment="Pharmacy response message")
    approval_expiration = Column(DateTime(timezone=True), nullable=True, comment="Approval expiration date")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Refill request tracking"},
    )


class PharmacyInventorySync(Base):
    """Pharmacy inventory synchronization model

    Tracks inventory synchronization events with pharmacy systems.
    """
    __tablename__ = "pharmacy_inventory_syncs"

    id = Column(Integer, primary_key=True, index=True)
    sync_id = Column(String(100), unique=True, nullable=False, index=True, comment="Sync ID")

    # Entity mapping
    pharmacy_system_id = Column(Integer, ForeignKey("pharmacy_systems.id"), nullable=False, index=True, comment="Pharmacy system ID")
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False, index=True, comment="Medication ID")

    # Sync details
    sync_type = Column(String(50), nullable=False, index=True, comment="Sync type (full, incremental, update)")
    direction = Column(String(20), nullable=False, comment="Direction (inbound, outbound)")

    # Inventory data
    quantity_on_hand = Column(Integer, nullable=True, comment="Quantity on hand")
    reorder_level = Column(Integer, nullable=True, comment="Reorder level")
    lot_numbers = Column(JSON, nullable=True, comment="Lot numbers and expiration dates")

    # Status
    sync_status = Column(String(50), nullable=False, index=True, comment="Sync status")
    synced_at = Column(DateTime(timezone=True), nullable=True, comment="Sync timestamp")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Error message")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Pharmacy inventory synchronization"},
    )


class DrugInteractionCheck(Base):
    """Drug interaction check model

    Stores drug interaction checks performed through pharmacy systems.
    """
    __tablename__ = "drug_interaction_checks"

    id = Column(Integer, primary_key=True, index=True)
    check_id = Column(String(100), unique=True, nullable=False, index=True, comment="Check ID")

    # Entity mapping
    pharmacy_system_id = Column(Integer, ForeignKey("pharmacy_systems.id"), nullable=False, index=True, comment="Pharmacy system ID")
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True, comment="Patient ID")
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=True, index=True, comment="Prescription ID")

    # Medications checked
    medication_ids = Column(JSON, nullable=False, comment="Medication IDs checked")
    medication_names = Column(JSON, nullable=False, comment="Medication names")

    # Check results
    interaction_count = Column(Integer, nullable=False, default=0, comment="Number of interactions found")
    interactions = Column(JSON, nullable=True, comment="Interaction details")
    severity_levels = Column(JSON, nullable=True, comment="Severity levels")

    # Summary
    has_contraindications = Column(Boolean, default=False, nullable=False, index=True, comment="Has contraindications")
    has_major_interactions = Column(Boolean, default=False, nullable=False, comment="Has major interactions")
    has_moderate_interactions = Column(Boolean, default=False, nullable=False, comment="Has moderate interactions")

    # Clinical decision support
    recommendation = Column(Text, nullable=True, comment="Clinical recommendation")
    requires_review = Column(Boolean, default=False, nullable=False, index=True, comment="Requires clinical review")
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Clinician who reviewed")

    # Metadata
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Drug interaction check records"},
    )
