"""Patient Portal Vaccination Records Schemas

Pydantic schemas for vaccination records and immunization history management.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import date, datetime
from typing import List, Optional, Literal


class VaccinationRecord(BaseModel):
    """Complete vaccination record with all administration details.

    Attributes:
        id: Unique identifier for the vaccination record
        vaccine_name: Name of the vaccine administered
        vaccine_type: Type or category of vaccine (e.g., "viral", "bacterial", "toxoid")
        date_administered: Date when the vaccine was administered
        dose_number: Current dose number in the series (e.g., 1 of 3)
        total_doses: Total number of doses required for complete regimen
        batch_number: Manufacturer's batch number for traceability
        expiration_date: Expiration date of the vaccine batch
        administering_facility: Healthcare facility where administered
        administering_doctor: Name of the healthcare provider who administered
        site: Injection site (e.g., "left_arm", "right_arm", "left_thigh", "right_thigh")
        adverse_events: List of any adverse events or reactions observed
        next_due_date: Date when the next dose is due (if applicable)
        status: Current status of the vaccination
        notes: Additional clinical notes or observations
        created_at: Timestamp when record was created
    """

    id: int

    vaccine_name: str = Field(..., min_length=1, max_length=255, description="Name of the vaccine administered")

    vaccine_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type/category of vaccine (e.g., viral, bacterial, toxoid, mRNA)"
    )

    date_administered: date = Field(..., description="Date when vaccine was administered")

    dose_number: int = Field(..., ge=1, le=10, description="Current dose number in the series")

    total_doses: int = Field(..., ge=1, le=10, description="Total number of doses required")

    batch_number: Optional[str] = Field(None, max_length=100, description="Manufacturer batch number for traceability")

    expiration_date: Optional[date] = Field(None, description="Vaccine batch expiration date")

    administering_facility: Optional[str] = Field(None, max_length=255, description="Healthcare facility name")

    administering_doctor: Optional[str] = Field(None, max_length=255, description="Administering healthcare provider")

    site: Optional[Literal["left_arm", "right_arm", "left_thigh", "right_thigh", "other"]] = Field(
        None,
        description="Injection site location"
    )

    adverse_events: List[str] = Field(
        default_factory=list,
        description="List of any adverse events or reactions"
    )

    next_due_date: Optional[date] = Field(None, description="Next dose due date")

    status: Literal["scheduled", "administered", "missed", "overdue"] = Field(
        ...,
        description="Current vaccination status"
    )

    notes: Optional[str] = Field(None, max_length=2000, description="Additional clinical notes")

    created_at: datetime = Field(..., description="Record creation timestamp")

    @field_validator("date_administered")
    @classmethod
    def validate_date_administered(cls, v: date) -> date:
        """Ensure administered date is not in the future."""
        if v > date.today():
            raise ValueError("Administration date cannot be in the future")
        return v

    @field_validator("expiration_date")
    @classmethod
    def validate_expiration_date(cls, v: Optional[date], info) -> Optional[date]:
        """Ensure vaccine was not expired when administered."""
        if v is not None and "date_administered" in info.data:
            if v < info.data["date_administered"]:
                raise ValueError("Vaccine was expired at time of administration")
        return v

    @field_validator("next_due_date")
    @classmethod
    def validate_next_due_date(cls, v: Optional[date], info) -> Optional[date]:
        """Ensure next due date is after administration date."""
        if v is not None and "date_administered" in info.data:
            if v <= info.data["date_administered"]:
                raise ValueError("Next due date must be after administration date")
        return v

    @field_validator("dose_number", "total_doses")
    @classmethod
    def validate_dose_numbers(cls, v: int, info) -> int:
        """Ensure dose numbers are valid."""
        if "dose_number" in info.data and "total_doses" in info.data:
            if info.data["dose_number"] > info.data["total_doses"]:
                raise ValueError("Dose number cannot exceed total doses")
        return v

    model_config = ConfigDict(from_attributes=True)


class VaccinationStatus(BaseModel):
    """Summary statistics for patient's vaccination status.

    Provides an overview of vaccination completeness and pending items.

    Attributes:
        total_vaccinations: Total number of vaccination records
        complete_regimens: Number of completed vaccination regimens
        incomplete_regimens: Number of ongoing/incomplete regimens
        overdue_vaccinations: Count of vaccinations that are overdue
        upcoming_vaccinations: Count of scheduled upcoming vaccinations
    """

    total_vaccinations: int = Field(..., ge=0, description="Total vaccination records")

    complete_regimens: int = Field(..., ge=0, description="Number of completed vaccination series")

    incomplete_regimens: int = Field(..., ge=0, description="Number of incomplete vaccination series")

    overdue_vaccinations: int = Field(..., ge=0, description="Count of overdue vaccinations")

    upcoming_vaccinations: int = Field(..., ge=0, description="Count of scheduled upcoming doses")

    model_config = ConfigDict(from_attributes=True)


class VaccinationSummary(BaseModel):
    """Comprehensive vaccination summary for a patient.

    Aggregates vaccination data into categorized lists for easy display.

    Attributes:
        patient_id: Unique patient identifier
        vaccination_status: Overall vaccination status statistics
        recent_vaccinations: List of recently administered vaccinations
        upcoming_vaccinations: List of scheduled upcoming vaccinations
        overdue_vaccinations: List of overdue vaccinations requiring attention
    """

    patient_id: int = Field(..., description="Patient unique identifier")

    vaccination_status: VaccinationStatus = Field(
        ...,
        description="Overall vaccination status statistics"
    )

    recent_vaccinations: List[VaccinationRecord] = Field(
        default_factory=list,
        description="Recently administered vaccinations (last 12 months)"
    )

    upcoming_vaccinations: List[VaccinationRecord] = Field(
        default_factory=list,
        description="Scheduled upcoming vaccinations"
    )

    overdue_vaccinations: List[VaccinationRecord] = Field(
        default_factory=list,
        description="Overdue vaccinations requiring attention"
    )

    model_config = ConfigDict(from_attributes=True)


class VaccinationCertificateRequest(BaseModel):
    """Request schema for generating vaccination certificate.

    Used when patients request official vaccination documentation.

    Attributes:
        vaccination_id: ID of the vaccination record for certificate
        include_qr_code: Whether to include a QR code on the certificate
    """

    vaccination_id: int = Field(..., gt=0, description="Vaccination record ID")

    include_qr_code: bool = Field(
        default=True,
        description="Include QR code for verification"
    )

    @field_validator("vaccination_id")
    @classmethod
    def validate_vaccination_id(cls, v: int) -> int:
        """Ensure vaccination ID is positive."""
        if v <= 0:
            raise ValueError("Vaccination ID must be positive")
        return v

    model_config = ConfigDict(from_attributes=True)


class VaccinationCertificate(BaseModel):
    """Vaccination certificate details.

    Contains information about the generated vaccination certificate document.

    Attributes:
        certificate_url: URL to download the certificate document
        qr_code_url: URL to the QR code image (if generated)
        issued_at: Timestamp when certificate was issued
        expires_at: Optional expiration date of the certificate
    """

    certificate_url: str = Field(..., description="URL to download certificate PDF/document")

    qr_code_url: Optional[str] = Field(None, description="URL to QR code image for verification")

    issued_at: datetime = Field(..., description="Certificate issuance timestamp")

    expires_at: Optional[datetime] = Field(None, description="Certificate expiration date")

    @field_validator("certificate_url", "qr_code_url")
    @classmethod
    def validate_urls(cls, v: Optional[str]) -> Optional[str]:
        """Ensure URLs are properly formatted if provided."""
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Ensure expiration is after issuance."""
        if v is not None and "issued_at" in info.data:
            if v <= info.data["issued_at"]:
                raise ValueError("Expiration must be after issuance date")
        return v

    model_config = ConfigDict(from_attributes=True)


class VaccinationListResponse(BaseModel):
    """Paginated response for vaccination records list.

    Returns a list of vaccination records with pagination metadata.

    Attributes:
        total: Total number of vaccination records
        vaccinations: List of vaccination records
    """

    total: int = Field(..., ge=0, description="Total number of vaccination records")

    vaccinations: List[VaccinationRecord] = Field(
        default_factory=list,
        description="List of vaccination records"
    )

    model_config = ConfigDict(from_attributes=True)


class VaccinationDetailResponse(BaseModel):
    """Detailed response for a single vaccination record.

    Provides complete vaccination details along with certificate availability.

    Attributes:
        vaccination: Complete vaccination record details
        certificate_url: URL to download vaccination certificate (if available)
        can_download_certificate: Whether certificate is available for download
    """

    vaccination: VaccinationRecord = Field(..., description="Complete vaccination record")

    certificate_url: Optional[str] = Field(
        None,
        description="URL to download vaccination certificate if available"
    )

    can_download_certificate: bool = Field(
        ...,
        description="Whether certificate can be downloaded for this vaccination"
    )

    @field_validator("certificate_url")
    @classmethod
    def validate_certificate_url(cls, v: Optional[str]) -> Optional[str]:
        """Ensure certificate URL is valid if provided."""
        if v is not None and not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Certificate URL must start with http:// or https://")
        return v

    model_config = ConfigDict(from_attributes=True)
