"""Patient Portal Radiology Results Schemas

Pydantic schemas for viewing radiology/imaging results through patient portal.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class RadiologyStatus(str, Enum):
    """Status of radiology exam"""
    ORDERED = "ordered"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ModalityType(str, Enum):
    """Imaging modality types"""
    CT = "CT"
    MRI = "MRI"
    XRAY = "XRAY"
    US = "US"
    FLUOROSCOPY = "FLUOROSCOPY"
    MAMMOGRAPHY = "MAMMOGRAPHY"
    NUCLEAR_MEDICINE = "NUCLEAR_MEDICINE"
    PET = "PET"


class RadiologyResultListItem(BaseModel):
    """Radiology result for list view"""
    id: int
    order_number: str
    procedure_name: str
    modality: str
    body_part: Optional[str] = None
    exam_date: date
    status: str
    has_critical_findings: bool
    has_report: bool
    ordered_by: str

    model_config = ConfigDict(from_attributes=True)


class RadiologyResultsListResponse(BaseModel):
    """Response for patient's radiology results"""
    recent_results: List[RadiologyResultListItem]
    historical_results: List[RadiologyResultListItem]
    total_recent: int
    total_historical: int
    pending_count: int
    critical_alerts: int


class RadiologyResultDetail(BaseModel):
    """Detailed radiology result information"""
    id: int
    order_number: str
    accession_number: Optional[str] = None

    # Procedure details
    procedure_code: str
    procedure_name: str
    modality: str
    body_part: Optional[str] = None
    view_position: Optional[str] = None

    # Status
    status: str
    priority: str

    # Clinical information
    clinical_indication: Optional[str] = None
    clinical_history: Optional[str] = None

    # Safety
    contrast_required: bool
    contrast_type: Optional[str] = None
    radiation_dose_msv: Optional[int] = None

    # Report
    preliminary_report: Optional[str] = None
    preliminary_report_at: Optional[datetime] = None
    final_report: Optional[str] = None
    final_report_at: Optional[datetime] = None
    findings: Optional[str] = None
    impression: Optional[str] = None

    # Critical findings
    critical_findings: bool
    critical_findings_notified: bool

    # Imaging info
    image_count: Optional[int] = None
    series_count: Optional[int] = None

    # Timestamps
    ordered_at: datetime
    scheduled_at: Optional[datetime] = None
    procedure_completed_at: Optional[datetime] = None

    # Providers
    ordered_by_name: str
    radiologist_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ImagingStudyInfo(BaseModel):
    """Information about imaging study for patient"""
    study_uid: Optional[str] = None
    modality: str
    body_part: Optional[str] = None
    series_count: Optional[int] = None
    image_count: Optional[int] = None
    radiation_dose_msv: Optional[int] = None
    contrast_used: bool
    contrast_volume_ml: Optional[int] = None


class RadiologyExamExplanation(BaseModel):
    """Patient-friendly explanation of a radiology exam"""
    modality: str
    description: str
    what_it_is: str
    why_its_done: str
    how_to_prepare: Optional[str] = None
    what_to_expect: str
    duration: str
    risks: str
    results_timing: str


class CriticalFindingAlert(BaseModel):
    """Critical finding alert notification"""
    radiology_order_id: int
    procedure_name: str
    critical_finding: str
    alert_time: datetime
    notified: bool = False


class ImageMetadata(BaseModel):
    """Metadata for imaging study images"""
    series_number: int
    image_number: int
    modality: str
    body_part: Optional[str] = None
    view_position: Optional[str] = None
    slice_thickness: Optional[float] = None
    kvp: Optional[int] = None
    mas: Optional[int] = None
