"""SATUSEHAT FHIR R4 API endpoints for STORY-033 & STORY-034.

This module provides REST API endpoints for:
- SATUSEHAT facility/organization registration (STORY-033)
- Patient demographics sync (STORY-034)
- OAuth token management and testing
- Connectivity verification
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.patient import Patient
from app.schemas.satusehat import (
    SATUSEHATOrganizationCreate,
    SATUSEHATOrganizationUpdate,
    SATUSEHATOrganizationResponse,
    SATUSEHATOrganizationSearchResponse,
    SATUSEHATConnectivityTestResponse,
    FHIRPatientCreate,
    FHIRPatientResponse,
    FHIRPatientSearchResponse,
    PatientSyncResponse,
    PatientValidationResult,
    FHIREncounterCreate,
    FHIREncounterResponse,
    EncounterSyncResponse,
    EncounterValidationResult,
)
from app.services.satusehat import (
    SATUSEHATClient,
    SATUSEHATError,
    SATUSEHATAuthError,
    get_satusehat_client,
)
from app.services.patient_sync import (
    sync_patient_to_satusehat,
    get_patient_from_satusehat,
    search_patient_by_identifier,
    trigger_patient_sync_on_create,
    trigger_patient_sync_on_update,
    validate_patient_for_sync,
)
from app.services.encounter_sync import (
    sync_encounter_to_satusehat,
    get_encounter_from_satusehat,
    trigger_encounter_sync_on_create,
    trigger_encounter_sync_on_update,
    trigger_encounter_sync_on_completion,
    validate_encounter_for_sync,
)
from app.models.encounter import Encounter


router = APIRouter()


# =============================================================================
# Organization Registration Endpoints (STORY-033)
# =============================================================================

@router.post("/organization", response_model=SATUSEHATOrganizationResponse)
async def create_organization(
    organization: SATUSEHATOrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a healthcare organization/facility with SATUSEHAT.

    This endpoint creates a new FHIR Organization resource in SATUSEHAT,
    registering the healthcare facility for national health data exchange.

    Args:
        organization: Organization registration data
        current_user: Authenticated user (admin only)
        db: Database session

    Returns:
        Created FHIR Organization resource

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 502: If SATUSEHAT API error
    """
    # Verify user has permission (admin only)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can register organizations with SATUSEHAT"
        )

    try:
        async with SATUSEHATClient() as client:
            # Build telecom list
            telecom = []
            if organization.telecom_phone:
                telecom.append({
                    "system": "phone",
                    "value": organization.telecom_phone,
                    "use": "work",
                })
            if organization.telecom_email:
                telecom.append({
                    "system": "email",
                    "value": organization.telecom_email,
                    "use": "work",
                })

            # Build address
            address = None
            if organization.address_line or organization.address_city:
                address = {
                    "use": "work",
                    "type": "physical",
                }
                if organization.address_line:
                    address["line"] = organization.address_line
                if organization.address_city:
                    address["city"] = organization.address_city
                if organization.address_postal_code:
                    address["postalCode"] = organization.address_postal_code
                if organization.address_country:
                    address["country"] = organization.address_country

            # Create organization
            result = await client.create_organization(
                identifier=organization.identifier,
                name=organization.name,
                org_type=organization.org_type,
                telecom=telecom if telecom else None,
                address=address,
                part_of=organization.part_of_id,
            )

            return SATUSEHATOrganizationResponse(**result)

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT authentication error: {e.message}"
        )
    except SATUSEHATError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create organization: {str(e)}"
        )


@router.put("/organization/{organization_id}", response_model=SATUSEHATOrganizationResponse)
async def update_organization(
    organization_id: str,
    organization: SATUSEHATOrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing organization in SATUSEHAT.

    This endpoint updates a registered FHIR Organization resource in SATUSEHAT.

    Args:
        organization_id: FHIR Organization resource ID
        organization: Organization update data
        current_user: Authenticated user (admin only)
        db: Database session

    Returns:
        Updated FHIR Organization resource

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 404: If organization not found
        HTTPException 502: If SATUSEHAT API error
    """
    # Verify user has permission (admin only)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can update organizations in SATUSEHAT"
        )

    try:
        async with SATUSEHATClient() as client:
            # Build telecom list
            telecom = None
            if organization.telecom_phone or organization.telecom_email:
                telecom = []
                if organization.telecom_phone:
                    telecom.append({
                        "system": "phone",
                        "value": organization.telecom_phone,
                        "use": "work",
                    })
                if organization.telecom_email:
                    telecom.append({
                        "system": "email",
                        "value": organization.telecom_email,
                        "use": "work",
                    })

            # Build address
            address = None
            if organization.address_line or organization.address_city:
                address = {
                    "use": "work",
                    "type": "physical",
                }
                if organization.address_line:
                    address["line"] = organization.address_line
                if organization.address_city:
                    address["city"] = organization.address_city
                if organization.address_postal_code:
                    address["postalCode"] = organization.address_postal_code
                if organization.address_country:
                    address["country"] = organization.address_country

            # Update organization
            result = await client.update_organization(
                organization_id=organization_id,
                identifier=organization.identifier,
                name=organization.name,
                org_type=organization.org_type,
                telecom=telecom,
                address=address,
            )

            return SATUSEHATOrganizationResponse(**result)

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT authentication error: {e.message}"
        )
    except SATUSEHATError as e:
        if "not found" in str(e.message).lower():
            raise HTTPException(
                status_code=404,
                detail=f"Organization {organization_id} not found in SATUSEHAT"
            )
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update organization: {str(e)}"
        )


@router.get("/organization/{organization_id}", response_model=SATUSEHATOrganizationResponse)
async def get_organization(
    organization_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve an organization from SATUSEHAT.

    This endpoint fetches a registered FHIR Organization resource from SATUSEHAT.

    Args:
        organization_id: FHIR Organization resource ID
        current_user: Authenticated user
        db: Database session

    Returns:
        FHIR Organization resource

    Raises:
        HTTPException 404: If organization not found
        HTTPException 502: If SATUSEHAT API error
    """
    try:
        async with SATUSEHATClient() as client:
            result = await client.get_organization(organization_id)
            return SATUSEHATOrganizationResponse(**result)

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT authentication error: {e.message}"
        )
    except SATUSEHATError as e:
        if "not found" in str(e.message).lower():
            raise HTTPException(
                status_code=404,
                detail=f"Organization {organization_id} not found in SATUSEHAT"
            )
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve organization: {str(e)}"
        )


@router.get("/organization", response_model=SATUSEHATOrganizationSearchResponse)
async def search_organization(
    identifier: str = Query(..., description="Facility identifier (e.g., hospital code)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for organization by facility identifier in SATUSEHAT.

    This endpoint searches for a registered FHIR Organization resource
    using the official facility identifier.

    Args:
        identifier: Facility identifier from Kemenkes
        current_user: Authenticated user
        db: Database session

    Returns:
        FHIR Bundle with search results

    Raises:
        HTTPException 502: If SATUSEHAT API error
    """
    try:
        async with SATUSEHATClient() as client:
            result = await client.search_organization_by_identifier(identifier)
            return SATUSEHATOrganizationSearchResponse(**result)

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT authentication error: {e.message}"
        )
    except SATUSEHATError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT API error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search organization: {str(e)}"
        )


# =============================================================================
# Connectivity and Authentication Endpoints
# =============================================================================

@router.get("/test-connectivity", response_model=SATUSEHATConnectivityTestResponse)
async def test_satusehat_connectivity(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Test connectivity to SATUSEHAT services.

    This endpoint verifies OAuth authentication and basic API access
    to ensure SATUSEHAT integration is properly configured.

    Args:
        current_user: Authenticated user (admin only)
        db: Database session

    Returns:
        Connectivity test results

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 500: If test fails unexpectedly
    """
    # Verify user has permission (admin only)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can test SATUSEHAT connectivity"
        )

    try:
        async with SATUSEHATClient() as client:
            result = await client.test_connectivity()
            return SATUSEHATConnectivityTestResponse(**result)

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=500,
            detail=f"SATUSEHAT authentication failed: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connectivity test failed: {str(e)}"
        )


@router.get("/token-info")
async def get_token_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current SATUSEHAT OAuth token information.

    This endpoint returns information about the current access token
    including expiration time.

    Args:
        current_user: Authenticated user (admin only)
        db: Database session

    Returns:
        Token information

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 502: If token retrieval fails
    """
    # Verify user has permission (admin only)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin users can view token information"
        )

    try:
        async with SATUSEHATClient() as client:
            # Force token refresh to get current token info
            token = await client._get_valid_token()

            return {
                "token_type": "Bearer",
                "expires_at": client._token_expires_at.isoformat() if client._token_expires_at else None,
                "is_valid": bool(client._access_token and client._token_expires_at),
                "expires_in_seconds": (
                    int((client._token_expires_at - datetime.now()).total_seconds())
                    if client._token_expires_at else None
                ),
            }

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to get token: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve token information: {str(e)}"
        )


# =============================================================================
# Patient Sync Endpoints (STORY-034)
# =============================================================================

@router.post("/patients/sync/{patient_id}", response_model=PatientSyncResponse)
async def sync_patient_to_satusehat_endpoint(
    patient_id: int,
    organization_id: Optional[str] = Query(None, description="SATUSEHAT Organization resource ID"),
    force_update: bool = Query(default=False, description="Force update even if data unchanged"),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync a patient's demographics to SATUSEHAT.

    This endpoint manually triggers a sync of patient data to SATUSEHAT
    for national health data exchange.

    Args:
        patient_id: Internal patient ID to sync
        organization_id: SATUSEHAT Organization resource ID
        force_update: Force update even if data unchanged
        background_tasks: FastAPI background tasks
        current_user: Authenticated user (admin/nurse/doctor)
        db: Database session

    Returns:
        Sync result

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 404: If patient not found
        HTTPException 502: If SATUSEHAT API error
    """
    # Verify user has permission
    if current_user.role not in ["admin", "nurse", "doctor"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin, nurse, and doctor roles can sync patient data"
        )

    # Verify patient exists
    from sqlalchemy import select
    patient_result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = patient_result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found"
        )

    # Validate patient data
    is_valid, errors = validate_patient_for_sync(patient)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Patient data validation failed: {', '.join(errors)}"
        )

    # Perform sync
    try:
        async with SATUSEHATClient() as client:
            result = await sync_patient_to_satusehat(
                db,
                patient_id,
                client,
                organization_id,
                force_update
            )

        return PatientSyncResponse(
            success=result["success"],
            message=result["message"],
            patient_id=patient_id,
            satusehat_patient_id=result.get("satusehat_patient_id"),
            action=result.get("action"),
            synced_at=datetime.now() if result["success"] else None,
            error=result.get("error"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync patient: {str(e)}"
        )


@router.get("/patients/satusehat/{satusehat_patient_id}", response_model=FHIRPatientResponse)
async def get_satusehat_patient(
    satusehat_patient_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a patient from SATUSEHAT.

    This endpoint fetches a patient's FHIR resource from SATUSEHAT.

    Args:
        satusehat_patient_id: SATUSEHAT Patient resource ID
        current_user: Authenticated user
        db: Database session

    Returns:
        FHIR Patient resource

    Raises:
        HTTPException 404: If patient not found
        HTTPException 502: If SATUSEHAT API error
    """
    try:
        async with SATUSEHATClient() as client:
            result = await get_patient_from_satusehat(client, satusehat_patient_id)

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Patient {satusehat_patient_id} not found in SATUSEHAT"
                )

            return FHIRPatientResponse(**result)

    except HTTPException:
        raise

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT authentication error: {e.message}"
        )

    except SATUSEHATError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT API error: {e.message}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve patient: {str(e)}"
        )


@router.get("/patients/search", response_model=FHIRPatientSearchResponse)
async def search_satusehat_patient(
    identifier_system: str = Query(..., description="Identifier system URL"),
    identifier_value: str = Query(..., description="Identifier value"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for a patient by identifier in SATUSEHAT.

    This endpoint searches for a patient using their identifier
    (NIK, MRN, BPJS card number, etc.) in SATUSEHAT.

    Args:
        identifier_system: Identifier system URL
        identifier_value: Identifier value
        current_user: Authenticated user
        db: Database session

    Returns:
        FHIR Bundle with search results

    Raises:
        HTTPException 502: If SATUSEHAT API error
    """
    try:
        async with SATUSEHATClient() as client:
            result = await search_patient_by_identifier(
                client,
                identifier_system,
                identifier_value
            )
            return FHIRPatientSearchResponse(**result)

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT authentication error: {e.message}"
        )

    except SATUSEHATError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT API error: {e.message}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search patient: {str(e)}"
        )


@router.get("/patients/{patient_id}/validate", response_model=PatientValidationResult)
async def validate_patient_for_satusehat(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate patient data for SATUSEHAT sync.

    This endpoint checks if a patient's data meets SATUSEHAT requirements
    before attempting to sync.

    Args:
        patient_id: Internal patient ID to validate
        current_user: Authenticated user
        db: Database session

    Returns:
        Validation result

    Raises:
        HTTPException 404: If patient not found
    """
    # Get patient
    from sqlalchemy import select
    patient_result = await db.execute(select(Patient).filter(Patient.id == patient_id))
    patient = patient_result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {patient_id} not found"
        )

    # Validate patient data
    is_valid, errors = validate_patient_for_sync(patient)

    # Add warnings
    warnings = []
    if not patient.bpjs_card_number:
        warnings.append("BPJS card number not provided - patient may not be linked to BPJS")

    return PatientValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings if warnings else None,
    )


# =============================================================================
# Encounter Sync Endpoints (STORY-035)
# =============================================================================

@router.post("/encounters/sync/{encounter_id}", response_model=EncounterSyncResponse)
async def sync_encounter_to_satusehat_endpoint(
    encounter_id: int,
    organization_id: Optional[str] = Query(None, description="SATUSEHAT Organization resource ID"),
    force_update: bool = Query(default=False, description="Force update even if data unchanged"),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Sync an encounter to SATUSEHAT.

    This endpoint manually triggers a sync of encounter data to SATUSEHAT
    for national health data exchange.

    Args:
        encounter_id: Internal encounter ID to sync
        organization_id: SATUSEHAT Organization resource ID
        force_update: Force update even if data unchanged
        background_tasks: FastAPI background tasks
        current_user: Authenticated user (admin/nurse/doctor)
        db: Database session

    Returns:
        Sync result

    Raises:
        HTTPException 403: If user lacks permission
        HTTPException 404: If encounter not found
        HTTPException 502: If SATUSEHAT API error
    """
    # Verify user has permission
    if current_user.role not in ["admin", "nurse", "doctor"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin, nurse, and doctor roles can sync encounter data"
        )

    # Verify encounter exists and get related data
    from sqlalchemy import select
    encounter_result = await db.execute(select(Encounter).filter(Encounter.id == encounter_id))
    encounter = encounter_result.scalar_one_or_none()

    if not encounter:
        raise HTTPException(
            status_code=404,
            detail=f"Encounter {encounter_id} not found"
        )

    # Get patient
    patient_result = await db.execute(select(Patient).filter(Patient.id == encounter.patient_id))
    patient = patient_result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {encounter.patient_id} not found"
        )

    # Validate encounter data
    is_valid, errors = validate_encounter_for_sync(encounter, patient)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Encounter data validation failed: {', '.join(errors)}"
        )

    # Perform sync
    try:
        async with SATUSEHATClient() as client:
            result = await sync_encounter_to_satusehat(
                db,
                encounter_id,
                client,
                organization_id,
                force_update
            )

        return EncounterSyncResponse(
            success=result["success"],
            message=result["message"],
            encounter_id=encounter_id,
            satusehat_encounter_id=result.get("satusehat_encounter_id"),
            action=result.get("action"),
            synced_at=datetime.now() if result["success"] else None,
            error=result.get("error"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync encounter: {str(e)}"
        )


@router.get("/encounters/satusehat/{satusehat_encounter_id}", response_model=FHIREncounterResponse)
async def get_satusehat_encounter(
    satusehat_encounter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve an encounter from SATUSEHAT.

    This endpoint fetches an encounter's FHIR resource from SATUSEHAT.

    Args:
        satusehat_encounter_id: SATUSEHAT Encounter resource ID
        current_user: Authenticated user
        db: Database session

    Returns:
        FHIR Encounter resource

    Raises:
        HTTPException 404: If encounter not found
        HTTPException 502: If SATUSEHAT API error
    """
    try:
        async with SATUSEHATClient() as client:
            result = await get_encounter_from_satusehat(client, satusehat_encounter_id)

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Encounter {satusehat_encounter_id} not found in SATUSEHAT"
                )

            return FHIREncounterResponse(**result)

    except HTTPException:
        raise

    except SATUSEHATAuthError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT authentication error: {e.message}"
        )

    except SATUSEHATError as e:
        raise HTTPException(
            status_code=502,
            detail=f"SATUSEHAT API error: {e.message}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve encounter: {str(e)}"
        )


@router.get("/encounters/{encounter_id}/validate", response_model=EncounterValidationResult)
async def validate_encounter_for_satusehat(
    encounter_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validate encounter data for SATUSEHAT sync.

    This endpoint checks if an encounter's data meets SATUSEHAT requirements
    before attempting to sync.

    Args:
        encounter_id: Internal encounter ID to validate
        current_user: Authenticated user
        db: Database session

    Returns:
        Validation result

    Raises:
        HTTPException 404: If encounter not found
    """
    # Get encounter
    from sqlalchemy import select
    encounter_result = await db.execute(select(Encounter).filter(Encounter.id == encounter_id))
    encounter = encounter_result.scalar_one_or_none()

    if not encounter:
        raise HTTPException(
            status_code=404,
            detail=f"Encounter {encounter_id} not found"
        )

    # Get patient
    patient_result = await db.execute(select(Patient).filter(Patient.id == encounter.patient_id))
    patient = patient_result.scalar_one_or_none()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"Patient {encounter.patient_id} not found"
        )

    # Validate encounter data
    is_valid, errors = validate_encounter_for_sync(encounter, patient)

    # Add warnings
    warnings = []
    if not encounter.doctor_id:
        warnings.append("No doctor assigned - encounter may be incomplete")
    if not encounter.bpjs_sep_number:
        warnings.append("BPJS SEP number not provided - insurance claim may not be linked")

    return EncounterValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings if warnings else None,
    )
