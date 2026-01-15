"""Patient Portal Lab Results Schemas

Pydantic schemas for viewing laboratory results through patient portal.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum


class LabResultStatus(str, Enum):
    """Status of lab result"""
    PENDING = "pending"
    COLLECTED = "collected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AbnormalFlag(str, Enum):
    """Abnormal result flag"""
    HIGH = "high"
    LOW = "low"
    ABNORMAL = "abnormal"
    NORMAL = "normal"
    CRITICAL = "critical"


class TestResultItem(BaseModel):
    """Individual test result within a lab order"""
    test_name: str
    result_value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None
    is_abnormal: bool = False
    is_critical: bool = False

    model_config = ConfigDict(from_attributes=True)


class LabResultDetail(BaseModel):
    """Detailed lab result information"""
    id: int
    order_number: str
    test_name: str
    test_code: str
    loinc_code: Optional[str] = None
    status: str
    priority: str

    # Clinical information
    clinical_indication: Optional[str] = None
    specimen_type: Optional[str] = None

    # Results
    results: List[TestResultItem]
    results_interpretation: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[bool] = None

    # Test explanation (patient-friendly)
    test_description: Optional[str] = None
    what_it_measures: Optional[str] = None
    what_results_mean: Optional[str] = None

    # Timestamps
    ordered_at: datetime
    specimen_collected_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Ordering provider
    ordered_by_name: str

    model_config = ConfigDict(from_attributes=True)


class LabResultListItem(BaseModel):
    """Lab result for list view"""
    id: int
    order_number: str
    test_name: str
    test_date: date
    status: str
    has_abnormal_results: bool
    has_critical_results: bool
    ordered_by: str

    model_config = ConfigDict(from_attributes=True)


class LabResultsListResponse(BaseModel):
    """Response for patient's lab results"""
    recent_results: List[LabResultListItem]
    historical_results: List[LabResultListItem]
    total_recent: int
    total_historical: int
    pending_count: int
    critical_alerts: int


class TestHistoryPoint(BaseModel):
    """Single data point for test history/trending"""
    date: date
    value: float
    is_abnormal: bool
    reference_range: Optional[str] = None


class TestHistoryResponse(BaseModel):
    """Test history for trending visualization"""
    test_code: str
    test_name: str
    unit: str
    history: List[TestHistoryPoint]
    trend: Optional[str] = None  # "improving", "worsening", "stable"
    normal_range: Optional[str] = None


class LabResultExportRequest(BaseModel):
    """Request to export lab results"""
    result_ids: List[int]
    format: str = Field("pdf", pattern="^(pdf|csv)$")
    include_interpretation: bool = True
    include_reference_ranges: bool = True


class LabResultDocument(BaseModel):
    """Lab result document for download"""
    document_id: str
    download_url: str
    expires_at: datetime
    format: str


class CriticalValueAlert(BaseModel):
    """Critical value alert notification"""
    lab_order_id: int
    test_name: str
    critical_value: str
    normal_range: str
    alert_time: datetime
    notified: bool = False


class LabTestExplanation(BaseModel):
    """Patient-friendly explanation of a lab test"""
    test_code: str
    test_name: str
    loinc_code: Optional[str] = None
    description: str
    what_it_measures: str
    why_its_done: str
    how_to_prepare: Optional[str] = None
    what_results_mean: str
    normal_range: str
    abnormal_values_mean: str
    next_steps_if_abnormal: str
    educational_links: List[str] = []
