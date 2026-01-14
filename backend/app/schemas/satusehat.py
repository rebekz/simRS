"""SATUSEHAT FHIR R4 API schemas for STORY-033: Organization Registration.

This module defines Pydantic schemas for SATUSEHAT FHIR API integration,
including Organization registration, authentication, and FHIR resource models.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any, Dict
from datetime import datetime


# =============================================================================
# SATUSEHAT Configuration Schemas
# =============================================================================

class SATUSEHATConfig(BaseModel):
    """SATUSEHAT configuration schema."""

    client_id: str = Field(..., description="OAuth client ID from SATUSEHAT portal")
    client_secret: str = Field(..., description="OAuth client secret from SATUSEHAT portal")
    auth_url: str = Field(
        default="https://api-satusehat.kemkes.go.id/oauth2/v1",
        description="SATUSEHAT OAuth authorization server URL"
    )
    api_url: str = Field(
        default="https://api-satusehat.kemkes.go.id/fhir-r4/v1",
        description="SATUSEHAT FHIR R4 API base URL"
    )

    @validator('auth_url', 'api_url')
    def validate_url(cls, v):
        """Ensure URL ends without trailing slash"""
        return v.rstrip('/')


# =============================================================================
# OAuth Token Schemas
# =============================================================================

class SATUSEHATTokenResponse(BaseModel):
    """OAuth token response schema."""

    access_token: str = Field(..., description="Access token for API calls")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Token lifetime in seconds")
    scope: Optional[str] = Field(None, description="Granted scopes")
    obtained_at: datetime = Field(default_factory=datetime.now, description="When token was obtained")


# =============================================================================
# Organization Schemas (STORY-033)
# =============================================================================

class SATUSEHATOrganizationCreate(BaseModel):
    """Schema for creating Organization in SATUSEHAT."""

    identifier: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Facility identifier (e.g., hospital code from Kemenkes)"
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=250,
        description="Facility name"
    )
    org_type: List[str] = Field(
        ...,
        min_items=1,
        description="Organization type codes (e.g., 'prov', 'dept', 'team')"
    )
    telecom_phone: Optional[str] = Field(None, description="Primary phone number")
    telecom_email: Optional[str] = Field(None, description="Primary email address")
    address_line: List[str] = Field(
        default_factory=list,
        description="Address lines (street, city, state, postal code, country)"
    )
    address_city: Optional[str] = Field(None, description="City name")
    address_postal_code: Optional[str] = Field(None, description="Postal code")
    address_country: Optional[str] = Field(default="ID", description="Country code (ISO 3166)")
    part_of_id: Optional[str] = Field(None, description="Parent organization ID")

    @validator('identifier')
    def validate_identifier(cls, v):
        """Validate identifier is alphanumeric with allowed symbols"""
        if not v.replace('-', '').replace('_', '').replace('.', '').isalnum():
            raise ValueError('Identifier must contain only alphanumeric characters and -_.')
        return v

    @validator('org_type')
    def validate_org_type(cls, v):
        """Validate organization type codes"""
        valid_types = ['prov', 'dept', 'team', 'govt', 'ins', 'edu', 'reli', 'crs', 'bus', 'other']
        for t in v:
            if t not in valid_types:
                raise ValueError(f'Invalid organization type: {t}. Must be one of: {", ".join(valid_types)}')
        return v

    @validator('telecom_email')
    def validate_email(cls, v):
        """Validate email format"""
        if v and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class SATUSEHATOrganizationUpdate(BaseModel):
    """Schema for updating Organization in SATUSEHAT."""

    organization_id: str = Field(..., description="FHIR Organization resource ID")
    identifier: Optional[str] = Field(None, description="Facility identifier")
    name: Optional[str] = Field(None, min_length=1, max_length=250, description="Facility name")
    org_type: Optional[List[str]] = Field(None, description="Organization type codes")
    telecom_phone: Optional[str] = Field(None, description="Primary phone number")
    telecom_email: Optional[str] = Field(None, description="Primary email address")
    address_line: Optional[List[str]] = Field(None, description="Address lines")
    address_city: Optional[str] = Field(None, description="City name")
    address_postal_code: Optional[str] = Field(None, description="Postal code")
    address_country: Optional[str] = Field(None, description="Country code")


class SATUSEHATOrganizationResponse(BaseModel):
    """Schema for Organization response from SATUSEHAT."""

    resource_type: str = Field(default="Organization", description="FHIR resource type")
    id: str = Field(..., description="FHIR resource ID")
    identifier: List[Dict[str, Any]] = Field(default_factory=list, description="Facility identifiers")
    active: bool = Field(default=True, description="Whether organization is active")
    type: List[Dict[str, Any]] = Field(default_factory=list, description="Organization types")
    name: str = Field(..., description="Facility name")
    telecom: Optional[List[Dict[str, Any]]] = Field(None, description="Contact information")
    address: Optional[List[Dict[str, Any]]] = Field(None, description="Facility address")
    part_of: Optional[Dict[str, Any]] = Field(None, description="Parent organization reference")


class SATUSEHATOrganizationSearchResponse(BaseModel):
    """Schema for Organization search response (FHIR Bundle)."""

    resource_type: str = Field(default="Bundle", description="FHIR resource type")
    total: int = Field(..., description="Total number of matching resources")
    entry: Optional[List[Dict[str, Any]]] = Field(None, description="Search results")


# =============================================================================
# Connectivity Test Schemas
# =============================================================================

class SATUSEHATConnectivityTestResponse(BaseModel):
    """Schema for connectivity test response."""

    auth_url: str = Field(..., description="OAuth authorization server URL")
    api_url: str = Field(..., description="FHIR API base URL")
    authenticated: bool = Field(..., description="Whether authentication succeeded")
    api_accessible: bool = Field(..., description="Whether API is accessible")
    token_expires_at: Optional[str] = Field(None, description="Token expiration timestamp")
    auth_error: Optional[str] = Field(None, description="Authentication error message")
    api_error: Optional[str] = Field(None, description="API access error message")
    timestamp: str = Field(..., description="Test timestamp")


# =============================================================================
# Error Schemas
# =============================================================================

class SATUSEHATErrorResponse(BaseModel):
    """SATUSEHAT API error response schema."""

    resource_type: Optional[str] = Field(None, description="FHIR resource type (OperationOutcome)")
    issue: Optional[List[Dict[str, Any]]] = Field(None, description="List of issues")
    code: str = Field(default="", description="Error code")
    message: str = Field(default="", description="Error message")
    details: Optional[str] = Field(None, description="Error details")
    is_error: bool = Field(default=True, description="Error flag")


# =============================================================================
# Generic FHIR Resource Schemas
# =============================================================================

class FHIRIdentifier(BaseModel):
    """FHIR Identifier component."""

    use: Optional[str] = Field(None, description="usual | official | temp | secondary | old (if known)")
    type: Optional[Dict[str, Any]] = Field(None, description="Description of identifier")
    system: str = Field(..., description="The namespace for the identifier value")
    value: str = Field(..., description="The value that is unique")
    period: Optional[Dict[str, Any]] = Field(None, description="Time period when id is/was valid for use")
    assigner: Optional[Dict[str, Any]] = Field(None, description="Organization that issued id")


class FHIRCoding(BaseModel):
    """FHIR Coding component."""

    system: Optional[str] = Field(None, description="Identity of the terminology system")
    version: Optional[str] = Field(None, description="Version of the system")
    code: Optional[str] = Field(None, description="Symbol in syntax defined by the system")
    display: Optional[str] = Field(None, description="Representation defined by the system")
    user_selected: Optional[bool] = Field(None, description="If this coding was chosen directly by the user")


class FHIRCodeableConcept(BaseModel):
    """FHIR CodeableConcept component."""

    coding: Optional[List[FHIRCoding]] = Field(None, description="Code defined by a terminology system")
    text: Optional[str] = Field(None, description="Plain text representation of the concept")


class FHIRContactPoint(BaseModel):
    """FHIR ContactPoint component."""

    system: str = Field(..., description="phone | fax | email | pager | url | sms | other")
    value: str = Field(..., description="The actual contact point details")
    use: Optional[str] = Field(None, description="home | work | temp | old | mobile - purpose of this contact point")
    rank: Optional[int] = Field(None, description="Specify preferred order of use")
    period: Optional[Dict[str, Any]] = Field(None, description="Time period when the contact point was/is in use")


class FHIRAddress(BaseModel):
    """FHIR Address component."""

    use: Optional[str] = Field(None, description="home | work | temp | old | billing - purpose of this address")
    type: Optional[str] = Field(None, description="postal | physical | both")
    text: Optional[str] = Field(None, description="Text representation of the address")
    line: Optional[List[str]] = Field(None, description="Street name, number, direction & P.O. Box etc.")
    city: Optional[str] = Field(None, description="Name of city, town etc.")
    district: Optional[str] = Field(None, description="District name")
    state: Optional[str] = Field(None, description="Sub-unit of country")
    postal_code: Optional[str] = Field(None, description="Postal code for area")
    country: Optional[str] = Field(None, description="Country name")
    period: Optional[Dict[str, Any]] = Field(None, description="Time period when address was/is in use")


# =============================================================================
# Patient Schemas (STORY-034)
# =============================================================================

class FHIRHumanName(BaseModel):
    """FHIR HumanName component."""

    use: Optional[str] = Field(None, description="usual | official | temp | nickname | anonymous | old | maiden")
    text: Optional[str] = Field(None, description="Text representation of the full name")
    family: Optional[str] = Field(None, description="Family name (often called surname)")
    given: Optional[List[str]] = Field(None, description="Given names")
    prefix: Optional[List[str]] = Field(None, description="Parts that come before the name")
    suffix: Optional[List[str]] = Field(None, description="Parts that come after the name")
    period: Optional[Dict[str, Any]] = Field(None, description="Time period when name was/is in use")


class FHIRPatientCreate(BaseModel):
    """Schema for creating Patient in SATUSEHAT."""

    patient_id: int = Field(..., description="Internal patient ID")
    organization_id: Optional[str] = Field(None, description="SATUSEHAT Organization resource ID")
    force_update: bool = Field(default=False, description="Force update even if data unchanged")


class FHIRPatientResponse(BaseModel):
    """Schema for Patient response from SATUSEHAT."""

    resource_type: str = Field(default="Patient", description="FHIR resource type")
    id: str = Field(..., description="FHIR resource ID")
    identifier: List[Dict[str, Any]] = Field(default_factory=list, description="Patient identifiers")
    active: bool = Field(default=True, description="Whether patient record is active")
    name: Optional[List[Dict[str, Any]]] = Field(None, description="Patient names")
    telecom: Optional[List[Dict[str, Any]]] = Field(None, description="Contact information")
    gender: str = Field(..., description="male | female | other | unknown")
    birthDate: Optional[str] = Field(None, description="Patient birth date (ISO 8601)")
    address: Optional[List[Dict[str, Any]]] = Field(None, description="Patient addresses")
    maritalStatus: Optional[Dict[str, Any]] = Field(None, description="Marital status")
    managingOrganization: Optional[Dict[str, Any]] = Field(None, description="Managing organization reference")


class FHIRPatientSearchResponse(BaseModel):
    """Schema for Patient search response (FHIR Bundle)."""

    resource_type: str = Field(default="Bundle", description="FHIR resource type")
    total: int = Field(..., description="Total number of matching resources")
    entry: Optional[List[Dict[str, Any]]] = Field(None, description="Search results")


class PatientSyncResponse(BaseModel):
    """Schema for patient sync operation response."""

    success: bool = Field(..., description="Sync success status")
    message: str = Field(..., description="Sync response message")
    patient_id: int = Field(..., description="Internal patient ID")
    satusehat_patient_id: Optional[str] = Field(None, description="SATUSEHAT Patient resource ID")
    action: Optional[str] = Field(None, description="Action performed (create or update)")
    synced_at: Optional[datetime] = Field(default_factory=datetime.now, description="Sync timestamp")
    error: Optional[str] = Field(None, description="Error message if sync failed")


class PatientValidationResult(BaseModel):
    """Schema for patient validation result."""

    is_valid: bool = Field(..., description="Whether patient data is valid for sync")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")
    warnings: Optional[List[str]] = Field(None, description="List of validation warnings")
