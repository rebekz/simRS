"""SATUSEHAT FHIR R4 API endpoints for STORY-033: Organization Registration.

This module provides REST API endpoints for:
- SATUSEHAT facility/organization registration
- OAuth token management and testing
- Connectivity verification
- Organization CRUD operations
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.satusehat import (
    SATUSEHATOrganizationCreate,
    SATUSEHATOrganizationUpdate,
    SATUSEHATOrganizationResponse,
    SATUSEHATOrganizationSearchResponse,
    SATUSEHATConnectivityTestResponse,
)
from app.services.satusehat import (
    SATUSEHATClient,
    SATUSEHATError,
    SATUSEHATAuthError,
    get_satusehat_client,
)


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
