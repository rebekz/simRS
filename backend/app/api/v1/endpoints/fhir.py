"""FHIR R4 Server API Endpoints for STORY-024-02

This module provides FHIR R4 compliant API endpoints for:
- Resource read operations (GET /{resourceType}/{id})
- Resource search operations (GET /{resourceType}?parameter=value)
- Resource metadata endpoint

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.services.fhir_server import get_fhir_server_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# FHIR API Endpoints
# =============================================================================

@router.get("/metadata")
async def get_fhir_metadata():
    """FHIR Capability Statement

    Returns the FHIR Capability Statement describing server capabilities.
    """
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": datetime.utcnow().isoformat(),
        "kind": "instance",
        "implementation": {
            "description": "SIMRS FHIR R4 Server",
            "url": "https://simrs-hospital.com/fhir"
        },
        "fhirVersion": "4.0.1",
        "format": ["application/fhir+json"],
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {
                        "type": "Patient",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {"name": "identifier", "type": "token"},
                            {"name": "name", "type": "string"},
                            {"name": "birthdate", "type": "date"},
                            {"name": "gender", "type": "token"}
                        ]
                    },
                    {
                        "type": "Encounter",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"}
                        ],
                        "searchParam": [
                            {"name": "patient", "type": "reference"},
                            {"name": "date", "type": "date"},
                            {"name": "status", "type": "token"}
                        ]
                    }
                ]
            }
        ]
    }


@router.get("/{resource_type}/{resource_id}")
async def read_fhir_resource(
    resource_type: str,
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Read FHIR resource by ID

    FHIR read operation: GET /{resourceType}/{id}

    Args:
        resource_type: FHIR resource type (e.g., Patient, Encounter)
        resource_id: Resource ID (with or without type prefix)
        current_user: Authenticated user
        db: Database session

    Returns:
        FHIR resource in JSON format
    """
    try:
        service = get_fhir_server_service(db)

        result = await service.read_resource(
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=current_user.id
        )

        # Return FHIR JSON response
        return JSONResponse(
            content=result,
            status_code=status.HTTP_200_OK,
            media_type="application/fhir+json"
        )

    except ValueError as e:
        # Check if resource not found
        if "not found" in str(e).lower():
            operation_outcome = {
                "resourceType": "OperationOutcome",
                "issue": [
                    {
                        "severity": "error",
                        "code": "not-found",
                        "diagnostics": str(e)
                    }
                ]
            }
            return JSONResponse(
                content=operation_outcome,
                status_code=status.HTTP_404_NOT_FOUND,
                media_type="application/fhir+json"
            )

        # Other errors
        operation_outcome = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "invalid",
                    "diagnostics": str(e)
                }
            ]
        }
        return JSONResponse(
            content=operation_outcome,
            status_code=status.HTTP_400_BAD_REQUEST,
            media_type="application/fhir+json"
        )

    except Exception as e:
        logger.error("Error reading FHIR resource: {}".format(e))
        operation_outcome = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "exception",
                    "diagnostics": "Internal server error"
                }
            ]
        }
        return JSONResponse(
            content=operation_outcome,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/fhir+json"
        )


@router.get("/{resource_type}")
async def search_fhir_resources(
    resource_type: str,
    identifier: Optional[str] = Query(None, description="Resource identifier"),
    name: Optional[str] = Query(None, description="Patient name (contains)"),
    birthdate: Optional[str] = Query(None, description="Birth date (YYYY-MM-DD)"),
    gender: Optional[str] = Query(None, description="Gender (male|female|other|unknown)"),
    patient: Optional[str] = Query(None, description="Patient reference (e.g., Patient/123)"),
    date: Optional[str] = Query(None, description="Encounter date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Encounter status"),
    _count: int = Query(20, ge=1, le=100, description="Number of results per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search FHIR resources

    FHIR search operation: GET /{resourceType}?parameter=value

    Args:
        resource_type: FHIR resource type
        identifier: Resource identifier
        name: Patient name (for Patient resource)
        birthdate: Birth date (for Patient resource)
        gender: Gender (for Patient resource)
        patient: Patient reference (for Encounter resource)
        date: Encounter date (for Encounter resource)
        status: Encounter status (for Encounter resource)
        _count: Page size
        current_user: Authenticated user
        db: Database session

    Returns:
        FHIR Bundle containing search results
    """
    try:
        service = get_fhir_server_service(db)

        # Build parameters dict from query params
        parameters = {}

        if identifier:
            parameters["identifier"] = identifier
        if name:
            parameters["name"] = name
        if birthdate:
            parameters["birthdate"] = birthdate
        if gender:
            parameters["gender"] = gender
        if patient:
            parameters["patient"] = patient
        if date:
            parameters["date"] = date
        if status:
            parameters["status"] = status
        if _count:
            parameters["_count"] = _count

        result = await service.search_resources(
            resource_type=resource_type,
            parameters=parameters,
            user_id=current_user.id
        )

        # Return FHIR Bundle response
        return JSONResponse(
            content=result,
            status_code=status.HTTP_200_OK,
            media_type="application/fhir+json"
        )

    except ValueError as e:
        operation_outcome = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "invalid",
                    "diagnostics": str(e)
                }
            ]
        }
        return JSONResponse(
            content=operation_outcome,
            status_code=status.HTTP_400_BAD_REQUEST,
            media_type="application/fhir+json"
        )

    except Exception as e:
        logger.error("Error searching FHIR resources: {}".format(e))
        operation_outcome = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "exception",
                    "diagnostics": "Internal server error"
                }
            ]
        }
        return JSONResponse(
            content=operation_outcome,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/fhir+json"
        )


@router.post("/{resource_type}")
async def create_fhir_resource(
    resource_type: str,
    resource_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create FHIR resource

    FHIR create operation: POST /{resourceType}

    Args:
        resource_type: FHIR resource type
        resource_data: Resource data from request body
        current_user: Authenticated user
        db: Database session

    Returns:
        Created FHIR resource with location header
    """
    try:
        service = get_fhir_server_service(db)

        result = await service.create_resource(
            resource_type=resource_type,
            resource_data=resource_data,
            user_id=current_user.id
        )

        # Return created resource
        return JSONResponse(
            content=result,
            status_code=status.HTTP_201_CREATED,
            media_type="application/fhir+json",
            headers={
                "Location": "/fhir/{}/{}".format(resource_type, result.get("id"))
            }
        )

    except ValueError as e:
        operation_outcome = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "invalid",
                    "diagnostics": str(e)
                }
            ]
        }
        return JSONResponse(
            content=operation_outcome,
            status_code=status.HTTP_400_BAD_REQUEST,
            media_type="application/fhir+json"
        )

    except Exception as e:
        logger.error("Error creating FHIR resource: {}".format(e))
        operation_outcome = {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": "error",
                    "code": "exception",
                    "diagnostics": "Internal server error"
                }
            ]
        }
        return JSONResponse(
            content=operation_outcome,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            media_type="application/fhir+json"
        )
