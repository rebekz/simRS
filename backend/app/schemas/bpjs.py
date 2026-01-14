"""BPJS VClaim API schemas.

This module defines Pydantic schemas for BPJS VClaim API integration,
including configuration, requests, responses, and error handling.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any, Dict
from datetime import datetime, date


class BPJSConfig(BaseModel):
    """BPJS VClaim configuration schema."""

    cons_id: str = Field(..., description="Consumer ID from BPJS")
    secret_key: str = Field(..., description="Secret key from BPJS")
    user_key: str = Field(..., description="User key for BPJS API")
    api_url: str = Field(
        default="https://apijkn.bpjs-kesehatan.go.id/vclaim-rest",
        description="BPJS VClaim API base URL"
    )
    service_name: str = Field(
        default="SIMRS",
        description="Service name for BPJS integration"
    )

    @validator('api_url')
    def validate_api_url(cls, v):
        """Ensure API URL ends without trailing slash"""
        return v.rstrip('/')


class BPJSEligibilityRequest(BaseModel):
    """Schema for checking BPJS member eligibility."""

    card_number: Optional[str] = Field(
        None,
        min_length=13,
        max_length=13,
        description="BPJS card number (13 digits)"
    )
    nik: Optional[str] = Field(
        None,
        min_length=16,
        max_length=16,
        description="Indonesian ID number (16 digits)"
    )
    sep_date: date = Field(
        ...,
        description="SEP (Surat Eligibilitas Peserta) date"
    )

    @validator('card_number')
    def validate_card_number(cls, v, values):
        """Validate card number is numeric"""
        if v is not None and not v.isdigit():
            raise ValueError('Card number must contain only digits')
        return v

    @validator('nik')
    def validate_nik(cls, v):
        """Validate NIK is numeric"""
        if v is not None and not v.isdigit():
            raise ValueError('NIK must contain only digits')
        return v

    @validator('sep_date')
    def validate_sep_date(cls, v):
        """Validate SEP date is not in the future"""
        if v > date.today():
            raise ValueError('SEP date cannot be in the future')
        return v

    @validator('nik')
    def validate_nik_or_card_provided(cls, v, values):
        """Ensure either NIK or card number is provided"""
        if v is None and values.get('card_number') is None:
            raise ValueError('Either NIK or card number must be provided')
        return v


class BPJSPesertaInfo(BaseModel):
    """BPJS participant information from VClaim API."""

    nomorKartu: str = Field(..., description="BPJS card number")
    nama: str = Field(..., description="Participant name")
    noKTP: Optional[str] = Field(None, description="NIK (ID number)")
    mrNo: Optional[str] = Field(None, description="Medical record number")
    statusPeserta: Optional[Dict[str, Any]] = Field(None, description="Participant status")
    tglCetakKartu: Optional[str] = Field(None, description="Card print date")
    tglTAT: Optional[str] = Field(None, description="TAT date")
    tglTMT: Optional[str] = Field(None, description="TMT date")
    umur: Optional[Dict[str, Any]] = Field(None, description="Age information")
    peserta: Optional[Dict[str, Any]] = Field(None, description="Participant details")
    hakKelas: Optional[Dict[str, Any]] = Field(None, description="Class entitlement")
    jenisPeserta: Optional[str] = Field(None, description="Participant type")
    foto: Optional[str] = Field(None, description="Photo URL")
    provUmum: Optional[Dict[str, Any]] = Field(None, description="General practitioner info")


class BPJSEligibilityResponse(BaseModel):
    """Response schema for BPJS eligibility check."""

    metaData: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    response: Optional[Dict[str, Any]] = Field(None, description="Response data")
    peserta: Optional[BPJSPesertaInfo] = Field(None, description="Participant information")
    is_eligible: bool = Field(default=False, description="Eligibility status")
    message: str = Field(default="", description="Response message")


class BPJSSEPCreateRequest(BaseModel):
    """Schema for creating SEP (Surat Eligibilitas Peserta)."""

    noKartu: str = Field(..., min_length=13, max_length=13, description="BPJS card number")
    tglSEP: date = Field(..., description="SEP date")
    ppkPelayanan: str = Field(..., description="Healthcare facility code")
    jnsPelayanan: str = Field(..., description="Service type (RI/RAWAT INAP or RJ/RAWAT JALAN)")
    klsRawat: Optional[str] = Field(None, description="Treatment class")
    noMR: Optional[str] = Field(None, description="Medical record number")
    rujukan: Optional[Dict[str, Any]] = Field(None, description="Referral information")
    catatan: Optional[str] = Field(None, max_length=200, description="Additional notes")
    diagAwal: str = Field(..., min_length=3, max_length=3, description="Initial diagnosis code (ICD-10)")
    poliTujuan: Optional[str] = Field(None, description="Destination polyclinic")
    eksekutif: Optional[str] = Field(None, description="Executive service flag (0/1)")
    cob: Optional[Dict[str, Any]] = Field(None, description="COB information")
    katarak: Optional[str] = Field(None, description="Cataract flag")
    tujuanKun: Optional[str] = Field(None, description="Visit destination")
    dpjp: Optional[Dict[str, Any]] = Field(None, description="Doctor in charge")
    noTelp: Optional[str] = Field(None, description="Patient phone number")
    user: str = Field(..., description="User creating the SEP")

    @validator('noKartu', 'diagAwal', 'ppkPelayanan')
    def validate_alphanumeric(cls, v):
        """Validate alphanumeric fields"""
        if not v.replace('.', '').replace('-', '').replace('/', '').isalnum():
            raise ValueError('Field must contain only alphanumeric characters')
        return v

    @validator('jnsPelayanan')
    def validate_service_type(cls, v):
        """Validate service type"""
        valid_types = ['RI', 'RJ', 'RAWAT INAP', 'RAWAT JALAN']
        if v.upper() not in valid_types:
            raise ValueError(f'Service type must be one of: {", ".join(valid_types)}')
        return v.upper()


class BPJSSEPInfo(BaseModel):
    """SEP information from VClaim API."""

    sep: Optional[Dict[str, Any]] = Field(None, description="SEP details")


class BPJSSEPCreateResponse(BaseModel):
    """Response schema for SEP creation."""

    metaInfo: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    response: Optional[Dict[str, Any]] = Field(None, description="Response data")
    sep: Optional[Dict[str, Any]] = Field(None, description="Created SEP information")
    nsep: Optional[str] = Field(None, description="SEP number")
    message: str = Field(default="", description="Response message")


class BPJSSEPDeleteRequest(BaseModel):
    """Schema for deleting SEP."""

    sep_number: str = Field(..., description="SEP number to delete")
    user: str = Field(..., description="User requesting the deletion")


class BPJSSEPDeleteResponse(BaseModel):
    """Response schema for SEP deletion."""

    metaInfo: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    response: Optional[Dict[str, Any]] = Field(None, description="Response data")
    message: str = Field(default="", description="Response message")


class BPJSErrorResponse(BaseModel):
    """BPJS API error response schema."""

    metaData: Optional[Dict[str, Any]] = Field(None, description="Error metadata")
    response: Optional[Dict[str, Any]] = Field(None, description="Error response")
    code: str = Field(default="", description="Error code")
    message: str = Field(default="", description="Error message")
    details: Optional[str] = Field(None, description="Error details")
    is_error: bool = Field(default=True, description="Error flag")


class BPJSPolyclinicInfo(BaseModel):
    """Polyclinic information from BPJS."""

    kode: str = Field(..., description="Polyclinic code")
    nama: str = Field(..., description="Polyclinic name")


class BPJSFacilityInfo(BaseModel):
    """Healthcare facility information from BPJS."""

    kode: str = Field(..., description="Facility code")
    nama: str = Field(..., description="Facility name")


class BPJSDiagnosisInfo(BaseModel):
    """Diagnosis information from BPJS."""

    kode: str = Field(..., description="Diagnosis code (ICD-10)")
    nama: str = Field(..., description="Diagnosis name")


class BPJSDoctorInfo(BaseModel):
    """Doctor information from BPJS."""

    kode: str = Field(..., description="Doctor code")
    nama: str = Field(..., description="Doctor name")


class BPJSPoliclinicListResponse(BaseModel):
    """Response schema for polyclinic list."""

    metaInfo: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    list: Optional[List[BPJSPolyclinicInfo]] = Field(default_factory=list, description="Polyclinic list")


class BPJSFacilityListResponse(BaseModel):
    """Response schema for facility list."""

    metaInfo: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    list: Optional[List[BPJSFacilityInfo]] = Field(default_factory=list, description="Facility list")


class BPJSDiagnosisListResponse(BaseModel):
    """Response schema for diagnosis list."""

    metaInfo: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    list: Optional[List[BPJSDiagnosisInfo]] = Field(default_factory=list, description="Diagnosis list")


class BPJSDoctorListResponse(BaseModel):
    """Response schema for doctor list."""

    metaInfo: Optional[Dict[str, Any]] = Field(None, description="Response metadata")
    list: Optional[List[BPJSDoctorInfo]] = Field(default_factory=list, description="Doctor list")
