"""Bed Management System Models for STORY-020

This module provides SQLAlchemy models for:
- Room and ward management
- Bed inventory and status tracking
- Bed assignment and transfer workflow
- Room status management
- Bed request workflow
- Real-time bed dashboard
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, DateTime, Date, Text, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


# =============================================================================
# Room and Bed Models
# =============================================================================

class Room(Base):
    """Room model for managing hospital rooms"""
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)

    # Room identification
    # TODO: ward_id = Column(Integer, ForeignKey("wards.id"), nullable=False, index=True) - Ward model not yet defined
    ward_id = Column(Integer, nullable=True, index=True, comment="Ward ID (reference to Ward model when implemented)")
    room_number = Column(String(50), nullable=False, index=True)
    room_class = Column(
        SQLEnum("vvip", "vip", "1", "2", "3", name="roomclass"),
        nullable=False
    )
    gender_type = Column(
        SQLEnum("male", "female", "mixed", name="gendertype"),
        nullable=False
    )

    # Room configuration
    total_beds = Column(Integer, nullable=False, default=1)
    floor = Column(Integer, nullable=False, default=1)
    description = Column(Text, nullable=True)

    # Room status
    status = Column(
        SQLEnum("clean", "soiled", "maintenance", "isolation", name="roomstatus"),
        nullable=False,
        default="clean"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    beds = relationship("Bed", back_populates="room", cascade="all, delete-orphan")
    status_history = relationship("RoomStatusHistory", back_populates="room", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_rooms_ward_class', 'ward_id', 'room_class'),
        Index('ix_rooms_ward_number', 'ward_id', 'room_number'),
    )


class Bed(Base):
    """Bed model for managing individual hospital beds"""
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True, index=True)

    # Bed identification
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    bed_number = Column(String(50), nullable=False)
    bed_type = Column(String(50), nullable=False, default="standard")  # standard, icu, pediatric, isolation

    # Denormalized fields for quick queries (updated via triggers or app logic)
    room_number = Column(String(50), nullable=False)  # Denormalized from room
    ward_id = Column(Integer, nullable=False)  # Denormalized from room
    room_class = Column(String(10), nullable=False)  # Denormalized from room
    gender_type = Column(String(10), nullable=False)  # Denormalized from room
    floor = Column(Integer, nullable=False)  # Denormalized from room

    # Bed status
    status = Column(
        SQLEnum("available", "occupied", "maintenance", "reserved", name="bedstatus"),
        nullable=False,
        default="available"
    )

    # Current patient assignment (if occupied)
    current_patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
    admission_date = Column(DateTime(timezone=True), nullable=True)
    expected_discharge_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    room = relationship("Room", back_populates="beds")
    assignments = relationship("BedAssignment", back_populates="bed", cascade="all, delete-orphan")
    transfers_from = relationship("BedTransfer", foreign_keys="BedTransfer.from_bed_id", back_populates="from_bed")
    transfers_to = relationship("BedTransfer", foreign_keys="BedTransfer.to_bed_id", back_populates="to_bed")

    # Indexes
    __table_args__ = (
        Index('ix_beds_room_bed', 'room_id', 'bed_number'),
        Index('ix_beds_status', 'status'),
        Index('ix_beds_ward_status', 'ward_id', 'status'),
    )


# =============================================================================
# Bed Assignment and Transfer Models
# =============================================================================

class BedAssignment(Base):
    """Bed assignment model tracking patient to bed assignments"""
    __tablename__ = "bed_assignments"

    id = Column(Integer, primary_key=True, index=True)

    # Patient and bed
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False, index=True)
    admission_id = Column(Integer, ForeignKey("encounters.id"), nullable=True)

    # Assignment details
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expected_discharge_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    assign_for_isolation = Column(Boolean, nullable=False, default=False)

    # Discharge details
    discharged_at = Column(DateTime(timezone=True), nullable=True)
    discharged_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    discharge_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    bed = relationship("Bed", back_populates="assignments")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    discharged_by = relationship("User", foreign_keys=[discharged_by_id])

    # Indexes
    __table_args__ = (
        Index('ix_bed_assignments_patient', 'patient_id'),
        Index('ix_bed_assignments_bed', 'bed_id'),
        Index('ix_bed_assignments_active', 'bed_id', 'discharged_at'),
    )


class BedTransfer(Base):
    """Bed transfer model tracking patient transfers between beds"""
    __tablename__ = "bed_transfers"

    id = Column(Integer, primary_key=True, index=True)

    # Patient and beds
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    from_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)
    to_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)

    # Transfer details
    reason = Column(Text, nullable=False)
    transfer_notes = Column(Text, nullable=True)
    transferred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    transferred_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    from_bed = relationship("Bed", foreign_keys=[from_bed_id], back_populates="transfers_from")
    to_bed = relationship("Bed", foreign_keys=[to_bed_id], back_populates="transfers_to")
    transferred_by = relationship("User")

    # Indexes
    __table_args__ = (
        Index('ix_bed_transfers_patient', 'patient_id'),
        Index('ix_bed_transfers_date', 'transferred_at'),
    )


# =============================================================================
# Bed Request Workflow Models
# =============================================================================

class BedRequest(Base):
    """Bed request model for bed request workflow"""
    __tablename__ = "bed_requests"

    id = Column(Integer, primary_key=True, index=True)

    # Patient and request details
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    priority = Column(String(20), nullable=False, default="routine")  # routine, urgent, emergency

    # Request preferences
    requested_room_class = Column(String(10), nullable=True)  # vvip, vip, 1, 2, 3
    # TODO: requested_ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True) - Ward model not yet defined
    requested_ward_id = Column(Integer, nullable=True, comment="Requested Ward ID (reference to Ward model when implemented)")
    gender_preference = Column(String(10), nullable=True)  # male, female, mixed
    medical_requirements = Column(Text, nullable=True)
    expected_admission_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Request status and workflow
    status = Column(
        SQLEnum("pending", "approved", "assigned", "cancelled", "completed", name="bedrequeststatus"),
        nullable=False,
        default="pending"
    )

    # Assignment details (filled when bed is assigned)
    assigned_bed_id = Column(Integer, ForeignKey("beds.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Approval details
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Cancellation details
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    assigned_bed = relationship("Bed")
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    assigned_by_user = relationship("User", foreign_keys=[assigned_by_id])
    cancelled_by = relationship("User", foreign_keys=[cancelled_by_id])

    # Indexes
    __table_args__ = (
        Index('ix_bed_requests_status', 'status'),
        Index('ix_bed_requests_priority', 'priority'),
        Index('ix_bed_requests_patient', 'patient_id'),
    )


# =============================================================================
# Room Status Management Models
# =============================================================================

class RoomStatusHistory(Base):
    """Room status history model tracking room status changes"""
    __tablename__ = "room_status_history"

    id = Column(Integer, primary_key=True, index=True)

    # Room and status
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    status = Column(
        SQLEnum("clean", "soiled", "maintenance", "isolation", name="roomstatus"),
        nullable=False
    )
    previous_status = Column(String(20), nullable=True)

    # Status change details
    notes = Column(Text, nullable=True)
    clean_required = Column(Boolean, nullable=False, default=False)
    maintenance_reason = Column(Text, nullable=True)

    # Timestamps and user
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    room = relationship("Room", back_populates="status_history")
    updated_by = relationship("User")

    # Indexes
    __table_args__ = (
        Index('ix_room_status_history_room', 'room_id'),
        Index('ix_room_status_history_date', 'updated_at'),
    )
