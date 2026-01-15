"""Training Management Models for STORY-038

This module provides database models for:
- Training modules and materials
- Training assignments and progress tracking
- Training completion and certification
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base
from enum import Enum


class TrainingCategory(str, Enum):
    """Training module categories"""
    SYSTEM_USAGE = "system_usage"
    PATIENT_REGISTRATION = "patient_registration"
    CLINICAL_WORKFLOWS = "clinical_workflows"
    BILLING = "billing"
    SAFETY_COMPLIANCE = "safety_compliance"


class TrainingStatus(str, Enum):
    """Training assignment status"""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    EXPIRED = "expired"


class DifficultyLevel(str, Enum):
    """Training module difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TrainingModule(Base):
    """Training module model for managing training content"""
    __tablename__ = "training_modules"

    id = Column(Integer, primary_key=True, index=True)

    # Basic information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(TrainingCategory), nullable=False, index=True)
    difficulty_level = Column(SQLEnum(DifficultyLevel), nullable=False, index=True)

    # Content details
    content_type = Column(String(50), nullable=False)  # document, video, interactive
    content_url = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Configuration
    is_active = Column(Boolean, server_default="true", nullable=False, index=True)
    is_mandatory = Column(Boolean, server_default="false", nullable=False)
    required_for_roles = Column(JSON, nullable=True)  # List of roles that must complete this

    # Ordering and versioning
    order_index = Column(Integer, server_default="0", nullable=False)
    version = Column(String(20), nullable=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    assignments = relationship("TrainingAssignment", back_populates="module", cascade="all, delete-orphan")
    materials = relationship("TrainingMaterial", back_populates="module", cascade="all, delete-orphan")
    completions = relationship("TrainingCompletion", back_populates="module", cascade="all, delete-orphan")


class TrainingAssignment(Base):
    """Training assignment model for tracking user training assignments"""
    __tablename__ = "training_assignments"

    id = Column(Integer, primary_key=True, index=True)

    # Assignment details
    module_id = Column(Integer, ForeignKey("training_modules.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Due dates and completion
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completion_percentage = Column(Integer, server_default="0", nullable=False)

    # Status tracking
    status = Column(SQLEnum(TrainingStatus), nullable=False, default=TrainingStatus.ASSIGNED, index=True)

    # Performance metrics
    score = Column(Integer, nullable=True)  # 0-100
    passed = Column(Boolean, nullable=True)
    attempts = Column(Integer, server_default="0", nullable=False)

    # Progress tracking
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    progress_data = Column(JSON, nullable=True)  # Stores detailed progress information

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    module = relationship("TrainingModule", back_populates="assignments")
    user = relationship("User", foreign_keys=[user_id], backref="training_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])
    progress_records = relationship("TrainingProgress", back_populates="assignment", cascade="all, delete-orphan")


class TrainingProgress(Base):
    """Training progress model for tracking lesson-by-lesson progress"""
    __tablename__ = "training_progress"

    id = Column(Integer, primary_key=True, index=True)

    # Reference to assignment
    assignment_id = Column(Integer, ForeignKey("training_assignments.id", ondelete="CASCADE"), nullable=False, index=True)

    # Lesson details
    lesson_number = Column(Integer, nullable=False)
    lesson_title = Column(String(255), nullable=False)

    # Completion status
    completed = Column(Boolean, server_default="false", nullable=False)
    time_spent_minutes = Column(Integer, server_default="0", nullable=False)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    assignment = relationship("TrainingAssignment", back_populates="progress_records")


class TrainingMaterial(Base):
    """Training material model for managing module resources"""
    __tablename__ = "training_materials"

    id = Column(Integer, primary_key=True, index=True)

    # Reference to module
    module_id = Column(Integer, ForeignKey("training_modules.id"), nullable=False, index=True)

    # Material information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    material_type = Column(String(50), nullable=False)  # pdf, video, document, slide, etc.

    # File details
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # Size in bytes
    content_preview = Column(Text, nullable=True)  # Preview or excerpt

    # Ordering and tracking
    display_order = Column(Integer, server_default="0", nullable=False)
    download_count = Column(Integer, server_default="0", nullable=False)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    module = relationship("TrainingModule", back_populates="materials")


class TrainingCompletion(Base):
    """Training completion model for tracking certifications and feedback"""
    __tablename__ = "training_completions"

    id = Column(Integer, primary_key=True, index=True)

    # Reference to user and module
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("training_modules.id"), nullable=False, index=True)

    # Completion details
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Admin who verified completion

    # Performance
    score = Column(Integer, nullable=True)  # 0-100
    certificate_issued = Column(Boolean, server_default="false", nullable=False)
    certificate_url = Column(String(500), nullable=True)

    # User feedback
    feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 stars

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    module = relationship("TrainingModule", back_populates="completions")
    user = relationship("User", foreign_keys=[user_id], backref="training_completions")
    verifier = relationship("User", foreign_keys=[completed_by])
