"""Training Management Schemas for STORY-038

This module provides Pydantic schemas for training management operations including:
- Training module CRUD operations
- Training assignment management
- Training progress tracking
- Training materials repository
- Training completion reporting
- Training statistics and analytics
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


# =============================================================================
# Enums
# =============================================================================

class ModuleStatus(str, Enum):
    """Status of training modules"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AssignmentStatus(str, Enum):
    """Status of training assignments"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class ProgressStatus(str, Enum):
    """Status of training progress"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class MaterialType(str, Enum):
    """Type of training materials"""
    DOCUMENT = "document"
    VIDEO = "video"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    PRESENTATION = "presentation"
    MANUAL = "manual"
    GUIDE = "guide"


class CompletionStatus(str, Enum):
    """Overall completion status"""
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    OVERDUE = "overdue"
    EXEMPT = "exempt"


# =============================================================================
# Training Module Schemas
# =============================================================================

class TrainingModuleBase(BaseModel):
    """Base schema for training module"""
    title: str = Field(..., min_length=1, max_length=255, description="Module title")
    code: str = Field(..., min_length=1, max_length=50, description="Unique module code")
    description: Optional[str] = Field(None, max_length=1000, description="Module description")
    category: Optional[str] = Field(None, max_length=100, description="Training category")
    duration_hours: float = Field(..., ge=0, description="Expected duration in hours")
    is_mandatory: bool = Field(default=False, description="Whether training is mandatory")
    valid_for_months: Optional[int] = Field(None, ge=0, description="Validity period in months")
    required_role: Optional[str] = Field(None, max_length=50, description="Required role for this training")
    department_id: Optional[int] = Field(None, description="Department-specific training")
    pass_score: float = Field(default=80.0, ge=0, le=100, description="Minimum passing score")
    max_attempts: int = Field(default=3, ge=1, description="Maximum quiz attempts")
    sort_order: int = Field(default=0, description="Display order")
    prerequisites: Optional[List[int]] = Field(default_factory=list, description="Required module IDs")

    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate module code format"""
        if not v or not v.strip():
            raise ValueError('Module code cannot be empty')
        return v.upper().strip()

    @field_validator('duration_hours')
    @classmethod
    def validate_duration(cls, v: float) -> float:
        """Validate duration is reasonable"""
        if v > 100:
            raise ValueError('Duration cannot exceed 100 hours')
        return round(v, 2)


class TrainingModuleCreate(TrainingModuleBase):
    """Schema for creating a training module"""
    status: ModuleStatus = Field(default=ModuleStatus.DRAFT, description="Module status")
    created_by: int = Field(..., description="Creator user ID")


class TrainingModuleUpdate(BaseModel):
    """Schema for updating a training module"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    duration_hours: Optional[float] = Field(None, ge=0)
    is_mandatory: Optional[bool] = None
    valid_for_months: Optional[int] = Field(None, ge=0)
    required_role: Optional[str] = Field(None, max_length=50)
    department_id: Optional[int] = None
    pass_score: Optional[float] = Field(None, ge=0, le=100)
    max_attempts: Optional[int] = Field(None, ge=1)
    sort_order: Optional[int] = None
    prerequisites: Optional[List[int]] = None
    status: Optional[ModuleStatus] = None


class TrainingModuleResponse(TrainingModuleBase):
    """Schema for training module response"""
    id: int
    status: ModuleStatus
    created_by: int
    created_by_name: Optional[str] = None
    material_count: int = 0
    enrolled_count: int = 0
    completed_count: int = 0
    average_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingModuleListResponse(BaseModel):
    """Schema for training module list response"""
    modules: List[TrainingModuleResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


# =============================================================================
# Training Assignment Schemas
# =============================================================================

class TrainingAssignmentBase(BaseModel):
    """Base schema for training assignment"""
    module_id: int = Field(..., description="Training module ID")
    user_id: int = Field(..., description="Assigned user ID")
    assigned_by: int = Field(..., description="Assigner user ID")
    due_date: Optional[date] = Field(None, description="Assignment due date")
    priority: str = Field(default="medium", description="Assignment priority: low, medium, high")
    notes: Optional[str] = Field(None, max_length=500, description="Assignment notes")
    is_mandatory: bool = Field(default=False, description="Whether assignment is mandatory")

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        """Validate priority value"""
        valid_priorities = ['low', 'medium', 'high']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class TrainingAssignmentCreate(TrainingAssignmentBase):
    """Schema for creating a training assignment"""
    pass


class TrainingAssignmentUpdate(BaseModel):
    """Schema for updating a training assignment"""
    due_date: Optional[date] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    is_mandatory: Optional[bool] = None
    status: Optional[AssignmentStatus] = None


class TrainingAssignmentResponse(TrainingAssignmentBase):
    """Schema for training assignment response"""
    id: int
    status: AssignmentStatus
    progress_percentage: float = 0.0
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    attempts: int = 0
    module_title: Optional[str] = None
    module_code: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    assigned_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TrainingAssignmentListResponse(BaseModel):
    """Schema for training assignment list response"""
    assignments: List[TrainingAssignmentResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class BulkAssignmentCreate(BaseModel):
    """Schema for bulk creating training assignments"""
    module_id: int
    user_ids: List[int] = Field(..., min_length=1, description="List of user IDs to assign")
    assigned_by: int
    due_date: Optional[date] = None
    priority: str = "medium"
    notes: Optional[str] = None
    is_mandatory: bool = False


class BulkAssignmentResponse(BaseModel):
    """Schema for bulk assignment response"""
    total: int
    succeeded: int
    failed: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Training Progress Schemas
# =============================================================================

class TrainingProgressBase(BaseModel):
    """Base schema for training progress"""
    module_id: int = Field(..., description="Training module ID")
    user_id: int = Field(..., description="User ID")
    status: ProgressStatus = Field(default=ProgressStatus.NOT_STARTED)
    current_material_id: Optional[int] = Field(None, description="Current material being viewed")
    percentage_complete: float = Field(default=0.0, ge=0, le=100)

    @field_validator('percentage_complete')
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        """Validate percentage is properly formatted"""
        return round(v, 2)


class TrainingProgressCreate(TrainingProgressBase):
    """Schema for creating training progress"""
    pass


class TrainingProgressResponse(TrainingProgressBase):
    """Schema for training progress response"""
    id: int
    time_spent_minutes: int = 0
    last_accessed: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    quiz_score: Optional[float] = None
    quiz_attempts: int = 0
    certificate_issued: bool = False
    certificate_url: Optional[str] = None
    module_title: Optional[str] = None
    user_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProgressDetail(BaseModel):
    """Detailed progress information for a user"""
    progress: TrainingProgressResponse
    materials_completed: int
    total_materials: int
    materials_remaining: List[int] = Field(default_factory=list)
    next_material_id: Optional[int] = None
    can_complete: bool = False
    estimated_remaining_minutes: Optional[int] = None


class TrainingProgressListResponse(BaseModel):
    """Schema for training progress list response"""
    progress_items: List[TrainingProgressResponse]
    total: int
    page: int
    page_size: int


# =============================================================================
# Training Material Schemas
# =============================================================================

class TrainingMaterialBase(BaseModel):
    """Base schema for training material"""
    module_id: int = Field(..., description="Parent training module ID")
    title: str = Field(..., min_length=1, max_length=255, description="Material title")
    material_type: MaterialType = Field(..., description="Type of material")
    description: Optional[str] = Field(None, max_length=1000, description="Material description")
    file_url: Optional[str] = Field(None, max_length=500, description="URL to material file")
    content: Optional[str] = Field(None, description="Text content for documents/guides")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Expected duration in minutes")
    sort_order: int = Field(default=0, description="Display order within module")
    is_downloadable: bool = Field(default=False, description="Whether material can be downloaded")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty"""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class TrainingMaterialCreate(TrainingMaterialBase):
    """Schema for creating training material"""
    created_by: int = Field(..., description="Creator user ID")


class TrainingMaterialUpdate(BaseModel):
    """Schema for updating training material"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    file_url: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    sort_order: Optional[int] = None
    is_downloadable: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class TrainingMaterialResponse(TrainingMaterialBase):
    """Schema for training material response"""
    id: int
    created_by: int
    created_by_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    view_count: int = 0
    download_count: int = 0
    module_title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaterialListResponse(BaseModel):
    """Schema for material list response"""
    materials: List[TrainingMaterialResponse]
    total: int
    module_id: int
    module_title: Optional[str] = None


# =============================================================================
# Training Completion Schemas
# =============================================================================

class TrainingCompletionResponse(BaseModel):
    """Schema for individual training completion record"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    module_id: int
    module_title: Optional[str] = None
    module_code: Optional[str] = None
    status: CompletionStatus
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    attempts: int = 0
    certificate_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    due_date: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


class CompletionSummary(BaseModel):
    """Summary of training completion"""
    total_assigned: int = 0
    total_completed: int = 0
    total_in_progress: int = 0
    total_overdue: int = 0
    total_exempt: int = 0
    completion_rate: float = 0.0
    average_score: Optional[float] = None
    mandatory_completed: int = 0
    mandatory_total: int = 0
    mandatory_completion_rate: float = 0.0


class CompletionReport(BaseModel):
    """Comprehensive training completion report"""
    summary: CompletionSummary
    completions: List[TrainingCompletionResponse]
    by_department: Dict[str, CompletionSummary] = Field(default_factory=dict)
    by_role: Dict[str, CompletionSummary] = Field(default_factory=dict)
    by_module: Dict[str, CompletionSummary] = Field(default_factory=dict)
    overdue_users: List[Dict[str, Any]] = Field(default_factory=list)
    report_generated_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Training Statistics Schemas
# =============================================================================

class UserTrainingStats(BaseModel):
    """Statistics for a single user's training"""
    user_id: int
    user_name: Optional[str] = None
    total_assigned: int = 0
    total_completed: int = 0
    total_in_progress: int = 0
    total_overdue: int = 0
    completion_rate: float = 0.0
    average_score: Optional[float] = None
    total_time_spent_minutes: int = 0
    certificates_earned: int = 0
    mandatory_completed: int = 0
    mandatory_total: int = 0
    last_activity: Optional[datetime] = None


class ModuleStats(BaseModel):
    """Statistics for a single training module"""
    module_id: int
    module_title: Optional[str] = None
    module_code: Optional[str] = None
    total_assigned: int = 0
    total_completed: int = 0
    total_in_progress: int = 0
    completion_rate: float = 0.0
    average_score: Optional[float] = None
    average_time_to_complete_minutes: Optional[float] = None
    pass_rate: float = 0.0
    average_attempts: float = 0.0
    last_enrollment: Optional[datetime] = None


class OverallTrainingStats(BaseModel):
    """Overall training statistics across all modules and users"""
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    total_modules: int = 0
    active_modules: int = 0
    total_users_assigned: int = 0
    total_enrollments: int = 0
    total_completions: int = 0
    overall_completion_rate: float = 0.0
    overall_pass_rate: float = 0.0
    average_completion_time_hours: Optional[float] = None
    top_performing_modules: List[ModuleStats] = Field(default_factory=list)
    modules_need_attention: List[ModuleStats] = Field(default_factory=list)
    user_rankings: List[UserTrainingStats] = Field(default_factory=list)
    department_stats: Dict[str, CompletionSummary] = Field(default_factory=dict)
    recent_completions: List[TrainingCompletionResponse] = Field(default_factory=list)


# =============================================================================
# Training Quiz Schemas (Additional)
# =============================================================================

class QuizQuestionBase(BaseModel):
    """Base schema for quiz questions"""
    question: str = Field(..., min_length=5, max_length=500)
    question_type: str = Field(default="multiple_choice", description="Type: multiple_choice, true_false, short_answer")
    options: Optional[List[str]] = Field(None, description="Answer options for multiple choice")
    correct_answer: str = Field(..., description="Correct answer")
    points: int = Field(default=1, ge=0, description="Points for correct answer")
    explanation: Optional[str] = Field(None, description="Explanation of the answer")
    order: int = Field(default=0, description="Display order")


class QuizQuestionCreate(QuizQuestionBase):
    """Schema for creating quiz question"""
    material_id: int = Field(..., description="Parent material ID")


class QuizQuestionResponse(QuizQuestionBase):
    """Schema for quiz question response"""
    id: int
    material_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuizAttemptBase(BaseModel):
    """Base schema for quiz attempt"""
    progress_id: int = Field(..., description="Training progress ID")
    answers: Dict[int, str] = Field(..., description="Question ID to answer mapping")
    time_spent_seconds: int = Field(default=0, ge=0)


class QuizAttemptCreate(QuizAttemptBase):
    """Schema for creating quiz attempt"""
    pass


class QuizAttemptResponse(BaseModel):
    """Schema for quiz attempt response"""
    id: int
    progress_id: int
    score: float
    percentage: float
    passed: bool
    answers: Dict[int, str]
    correct_answers: int
    total_questions: int
    time_spent_seconds: int
    attempted_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Training Certificate Schemas
# =============================================================================

class CertificateGenerate(BaseModel):
    """Schema for generating training certificate"""
    progress_id: int = Field(..., description="Training progress ID")
    include_verification_code: bool = Field(default=True)


class CertificateResponse(BaseModel):
    """Schema for certificate response"""
    id: int
    progress_id: int
    user_id: int
    user_name: Optional[str] = None
    module_id: int
    module_title: Optional[str] = None
    certificate_url: Optional[str] = None
    verification_code: Optional[str] = None
    issued_at: datetime
    expires_at: Optional[datetime] = None
    is_valid: bool = True

    model_config = ConfigDict(from_attributes=True)


class CertificateVerify(BaseModel):
    """Schema for certificate verification"""
    verification_code: str = Field(..., min_length=1, max_length=100)


class CertificateVerificationResponse(BaseModel):
    """Schema for certificate verification response"""
    is_valid: bool
    certificate: Optional[CertificateResponse] = None
    verification_message: str
    verified_at: datetime = Field(default_factory=datetime.now)


# =============================================================================
# Training Reminder Schemas
# =============================================================================

class TrainingReminderCreate(BaseModel):
    """Schema for creating training reminders"""
    assignment_ids: List[int] = Field(..., min_length=1, description="Assignment IDs to send reminders for")
    reminder_type: str = Field(default="email", description="Type: email, sms, notification")
    custom_message: Optional[str] = Field(None, max_length=500, description="Custom reminder message")
    send_by: int = Field(..., description="User ID sending the reminder")


class TrainingReminderResponse(BaseModel):
    """Schema for training reminder response"""
    total: int
    sent: int
    failed: int
    failed_ids: List[int] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    sent_at: datetime = Field(default_factory=datetime.now)
