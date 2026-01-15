"""Message Transformation API Endpoints for STORY-024-10

This module provides API endpoints for:
- HL7 to FHIR transformation
- FHIR to HL7 transformation
- Transformation history and statistics

Python 3.5+ compatible
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.transformation import get_transformation_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class HL7ToFHIRRequest(BaseModel):
    """Request to transform HL7 to FHIR"""
    message_type: str = Field(..., description="Message type (ADT, ORM, ORU)")
    hl7_message: dict = Field(..., description="Parsed HL7 message")
    config: Optional[dict] = Field(None, description="Optional transformation config")


class FHIRToHL7Request(BaseModel):
    """Request to transform FHIR to HL7"""
    resource_type: str = Field(..., description="FHIR resource type (Patient, etc.)")
    fhir_resource: dict = Field(..., description="FHIR resource")
    config: Optional[dict] = Field(None, description="Optional transformation config")


# =============================================================================
# HL7 to FHIR Transformation Endpoints
# =============================================================================

@router.post("/hl7-to-fhir/adt/patient", status_code=status.HTTP_200_OK)
async def transform_hl7_adt_to_fhir_patient(
    request: HL7ToFHIRRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Transform HL7 ADT message to FHIR Patient resource"""
    try:
        service = get_transformation_service(db)

        result = await service.transform_hl7_adt_to_fhir_patient(
            hl7_message=request.hl7_message,
            config=request.config
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error transforming HL7 ADT to FHIR Patient: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transform message"
        )


@router.post("/hl7-to-fhir/orm/servicerequest", status_code=status.HTTP_200_OK)
async def transform_hl7_orm_to_fhir_service_request(
    request: HL7ToFHIRRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Transform HL7 ORM message to FHIR ServiceRequest resource"""
    try:
        service = get_transformation_service(db)

        result = await service.transform_hl7_orm_to_fhir_service_request(
            hl7_message=request.hl7_message,
            config=request.config
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error transforming HL7 ORM to FHIR ServiceRequest: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transform message"
        )


@router.post("/hl7-to-fhir/oru/observation", status_code=status.HTTP_200_OK)
async def transform_hl7_oru_to_fhir_observation(
    request: HL7ToFHIRRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Transform HL7 ORU message to FHIR Observation resources"""
    try:
        service = get_transformation_service(db)

        result = await service.transform_hl7_oru_to_fhir_observation(
            hl7_message=request.hl7_message,
            config=request.config
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error transforming HL7 ORU to FHIR Observation: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transform message"
        )


# =============================================================================
# FHIR to HL7 Transformation Endpoints
# =============================================================================

@router.post("/fhir-to-hl7/patient/adt", status_code=status.HTTP_200_OK)
async def transform_fhir_patient_to_hl7_adt(
    request: FHIRToHL7Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Transform FHIR Patient resource to HL7 ADT message"""
    try:
        service = get_transformation_service(db)

        result = await service.transform_fhir_patient_to_hl7_adt(
            fhir_resource=request.fhir_resource,
            config=request.config
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error transforming FHIR Patient to HL7 ADT: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transform message"
        )


# =============================================================================
# Transformation History Endpoints
# =============================================================================

@router.get("/history")
async def get_transformation_history(
    transformation_type: Optional[str] = Query(None, description="Filter by transformation type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get transformation history"""
    try:
        service = get_transformation_service(db)

        history = await service.get_transformation_history(
            limit=limit,
            transformation_type=transformation_type
        )

        return {
            "transformations": history,
            "count": len(history)
        }

    except Exception as e:
        logger.error("Error getting transformation history: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transformation history"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_transformation_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get transformation statistics"""
    try:
        from app.models.transformation import TransformationLog
        from sqlalchemy import select, func

        # Get total counts by direction
        hl7_to_fhir_query = select(func.count(TransformationLog.id)).where(
            TransformationLog.source_format == "HL7"
        )
        hl7_to_fhir_result = await db.execute(hl7_to_fhir_query)
        total_hl7_to_fhir = hl7_to_fhir_result.scalar() or 0

        fhir_to_hl7_query = select(func.count(TransformationLog.id)).where(
            TransformationLog.source_format == "FHIR"
        )
        fhir_to_hl7_result = await db.execute(fhir_to_hl7_query)
        total_fhir_to_hl7 = fhir_to_hl7_result.scalar() or 0

        # Get transformation type breakdown
        type_query = select(
            TransformationLog.transformation_type,
            func.count(TransformationLog.id).label("count")
        ).group_by(TransformationLog.transformation_type)

        type_result = await db.execute(type_query)
        type_counts = {row[0]: row[1] for row in type_result.all()}

        # Get average processing time
        time_query = select(func.avg(TransformationLog.processing_time_ms)).where(
            TransformationLog.processing_time_ms.isnot(None)
        )
        time_result = await db.execute(time_query)
        avg_time = time_result.scalar() or 0

        return {
            "total_transformations": total_hl7_to_fhir + total_fhir_to_hl7,
            "hl7_to_fhir": total_hl7_to_fhir,
            "fhir_to_hl7": total_fhir_to_hl7,
            "transformation_type_counts": type_counts,
            "average_processing_time_ms": float(avg_time)
        }

    except Exception as e:
        logger.error("Error getting transformation statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
