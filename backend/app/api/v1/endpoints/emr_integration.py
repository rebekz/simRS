"""EMR/EHR Integration API Endpoints for STORY-024-06

This module provides API endpoints for:
- External EMR/EHR system management
- CCD document exchange
- Patient data queries
- Referral and consultation workflows

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.emr_integration import get_emr_integration_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class ExternalSystemRegisterRequest(BaseModel):
    """Request to register external system"""
    system_code: str = Field(..., description="System code")
    system_name: str = Field(..., description="System name")
    system_type: str = Field(..., description="System type (EHR, EMR, HIE)")
    protocol: str = Field(..., description="Exchange protocol")
    organization: Optional[str] = Field(None, description="Organization name")
    facility_type: Optional[str] = Field(None, description="Facility type")
    address: Optional[str] = Field(None, description="Physical address")
    city: Optional[str] = Field(None, description="City")
    province: Optional[str] = Field(None, description="Province")
    country: Optional[str] = Field("Indonesia", description="Country")
    postal_code: Optional[str] = Field(None, description="Postal code")
    endpoint_url: Optional[str] = Field(None, description="Endpoint URL")
    auth_type: Optional[str] = Field(None, description="Authentication type")


class CCDSendRequest(BaseModel):
    """Request to send CCD document"""
    patient_id: int = Field(..., description="Patient ID")
    external_system_id: int = Field(..., description="External system ID")
    include_sections: Optional[List[str]] = Field(None, description="Sections to include")


class PatientDataQueryRequest(BaseModel):
    """Request to query patient data"""
    patient_id: int = Field(..., description="Patient ID")
    external_system_id: int = Field(..., description="External system ID")
    query_criteria: dict = Field(..., description="Query criteria")


class ReferralCreateRequest(BaseModel):
    """Request to create referral"""
    patient_id: int = Field(..., description="Patient ID")
    referral_type: str = Field(..., description="Referral type")
    priority: str = Field(..., description="Priority (routine, urgent, emergent)")
    reason: str = Field(..., description="Reason for referral")
    external_system_id: Optional[int] = Field(None, description="External system ID")
    encounter_id: Optional[int] = Field(None, description="Encounter ID")
    referring_provider_id: Optional[int] = Field(None, description="Referring provider")
    referred_to_provider: Optional[str] = Field(None, description="Referred to provider")
    referred_to_facility: Optional[str] = Field(None, description="Referred to facility")
    diagnosis: Optional[str] = Field(None, description="Primary diagnosis")
    clinical_summary: Optional[str] = Field(None, description="Clinical summary")
    attachments: Optional[dict] = Field(None, description="Attached documents")


# =============================================================================
# External System Management Endpoints
# =============================================================================

@router.post("/systems", status_code=status.HTTP_201_CREATED)
async def register_external_system(
    request: ExternalSystemRegisterRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Register external EMR/EHR system (admin only)"""
    try:
        service = get_emr_integration_service(db)

        result = await service.register_external_system(
            system_code=request.system_code,
            system_name=request.system_name,
            system_type=request.system_type,
            protocol=request.protocol,
            organization=request.organization,
            facility_type=request.facility_type,
            address=request.address,
            city=request.city,
            province=request.province,
            country=request.country,
            postal_code=request.postal_code,
            endpoint_url=request.endpoint_url,
            auth_type=request.auth_type
        )

        return result

    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error registering external system: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register external system"
        )


@router.get("/systems")
async def list_external_systems(
    system_type: Optional[str] = Query(None, description="Filter by system type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List external EMR/EHR systems"""
    try:
        from app.models.emr_integration import ExternalSystem
        from sqlalchemy import select, and_

        # Build filters
        filters = []
        if system_type:
            filters.append(ExternalSystem.system_type == system_type)
        if is_active is not None:
            filters.append(ExternalSystem.is_active == is_active)

        # Get systems
        query = select(ExternalSystem)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(ExternalSystem.system_name)

        result = await db.execute(query)
        systems = result.scalars().all()

        # Build response
        system_list = [
            {
                "system_id": s.system_id,
                "system_code": s.system_code,
                "system_name": s.system_name,
                "system_type": s.system_type,
                "organization": s.organization,
                "facility_type": s.facility_type,
                "protocol": s.protocol,
                "status": s.status,
                "is_active": s.is_active,
                "last_tested_at": s.last_tested_at.isoformat() if s.last_tested_at else None
            }
            for s in systems
        ]

        return {
            "systems": system_list
        }

    except Exception as e:
        logger.error("Error listing external systems: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list external systems"
        )


# =============================================================================
# CCD Document Exchange Endpoints
# =============================================================================

@router.post("/ccd/send", status_code=status.HTTP_201_CREATED)
async def send_ccd_document(
    request: CCDSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send CCD document to external system"""
    try:
        service = get_emr_integration_service(db)

        result = await service.send_ccd(
            patient_id=request.patient_id,
            external_system_id=request.external_system_id,
            include_sections=request.include_sections,
            initiated_by=current_user.id
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error sending CCD: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send CCD document"
        )


@router.get("/ccd/documents")
async def list_ccd_documents(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    external_system_id: Optional[int] = Query(None, description="Filter by external system"),
    direction: Optional[str] = Query(None, description="Filter by direction (sent, received)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List CCD documents with filtering"""
    try:
        from app.models.emr_integration import CCDDocument
        from sqlalchemy import select, func, and_

        # Build filters
        filters = []
        if patient_id:
            filters.append(CDDocument.patient_id == patient_id)
        if external_system_id:
            filters.append(CDDocument.external_system_id == external_system_id)
        if direction:
            filters.append(CDDocument.direction == direction)

        # Get total count
        count_query = select(func.count(CDDocument.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get documents with pagination
        offset = (page - 1) * per_page
        query = select(CDDocument)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(CDDocument.created_at.desc()).limit(per_page).offset(offset)

        result = await db.execute(query)
        documents = result.scalars().all()

        # Build response
        document_list = [
            {
                "document_id": d.document_id,
                "patient_id": d.patient_id,
                "document_type": d.document_type,
                "document_format": d.document_format,
                "document_date": d.document_date.isoformat(),
                "direction": d.direction,
                "is_valid": d.is_valid,
                "created_at": d.created_at.isoformat()
            }
            for d in documents
        ]

        return {
            "documents": document_list,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
        }

    except Exception as e:
        logger.error("Error listing CCD documents: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list CCD documents"
        )


# =============================================================================
# Patient Data Query Endpoints
# =============================================================================

@router.post("/query", status_code=status.HTTP_201_CREATED)
async def query_patient_data(
    request: PatientDataQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Query patient data from external system"""
    try:
        service = get_emr_integration_service(db)

        result = await service.query_patient_data(
            patient_id=request.patient_id,
            external_system_id=request.external_system_id,
            query_criteria=request.query_criteria,
            submitted_by=current_user.id
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error querying patient data: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query patient data"
        )


# =============================================================================
# Referral Management Endpoints
# =============================================================================

@router.post("/referrals", status_code=status.HTTP_201_CREATED)
async def create_referral(
    request: ReferralCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create patient referral"""
    try:
        service = get_emr_integration_service(db)

        result = await service.create_referral(
            patient_id=request.patient_id,
            referral_type=request.referral_type,
            priority=request.priority,
            reason=request.reason,
            external_system_id=request.external_system_id,
            encounter_id=request.encounter_id,
            referring_provider_id=request.referring_provider_id,
            referred_to_provider=request.referred_to_provider,
            referred_to_facility=request.referred_to_facility,
            diagnosis=request.diagnosis,
            clinical_summary=request.clinical_summary,
            attachments=request.attachments
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating referral: {}".format(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create referral"
        )


@router.get("/referrals")
async def list_referrals(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List referrals with filtering"""
    try:
        from app.models.emr_integration import Referral
        from sqlalchemy import select, func, and_

        # Build filters
        filters = []
        if patient_id:
            filters.append(Referral.patient_id == patient_id)
        if status:
            filters.append(Referral.status == status)
        if priority:
            filters.append(Referral.priority == priority)

        # Get total count
        count_query = select(func.count(Referral.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get referrals with pagination
        offset = (page - 1) * per_page
        query = select(Referral)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(Referral.referral_date.desc()).limit(per_page).offset(offset)

        result = await db.execute(query)
        referrals = result.scalars().all()

        # Build response
        referral_list = [
            {
                "referral_id": r.referral_id,
                "patient_id": r.patient_id,
                "referral_type": r.referral_type,
                "priority": r.priority,
                "reason": r.reason,
                "referred_to_facility": r.referred_to_facility,
                "status": r.status,
                "referral_date": r.referral_date.isoformat()
            }
            for r in referrals
        ]

        return {
            "referrals": referral_list,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
        }

    except Exception as e:
        logger.error("Error listing referrals: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list referrals"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_emr_integration_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get EMR integration statistics"""
    try:
        from app.models.emr_integration import ExternalSystem, DataExchange, Referral, CCDDocument
        from sqlalchemy import select, func

        # Get total counts
        system_query = select(func.count(ExternalSystem.id)).where(ExternalSystem.is_active == True)
        system_result = await db.execute(system_query)
        total_systems = system_result.scalar() or 0

        exchange_query = select(func.count(DataExchange.id))
        exchange_result = await db.execute(exchange_query)
        total_exchanges = exchange_result.scalar() or 0

        referral_query = select(func.count(Referral.id))
        referral_result = await db.execute(referral_query)
        total_referrals = referral_result.scalar() or 0

        ccd_query = select(func.count(CCDocument.id))
        ccd_result = await db.execute(ccd_query)
        total_ccds = ccd_result.scalar() or 0

        # Get exchange status breakdown
        status_query = select(
            DataExchange.status,
            func.count(DataExchange.id).label("count")
        ).group_by(DataExchange.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # Get system type breakdown
        type_query = select(
            ExternalSystem.system_type,
            func.count(ExternalSystem.id).label("count")
        ).where(ExternalSystem.is_active == True).group_by(ExternalSystem.system_type)

        type_result = await db.execute(type_query)
        type_counts = {row[0]: row[1] for row in type_result.all()}

        return {
            "total_systems": total_systems,
            "total_exchanges": total_exchanges,
            "total_referrals": total_referrals,
            "total_ccds": total_ccds,
            "status_counts": status_counts,
            "type_counts": type_counts,
            "summary": {
                "active_connections": total_systems,
                "completed_exchanges": status_counts.get("completed", 0),
                "pending_referrals": status_counts.get("pending", 0)
            }
        }

    except Exception as e:
        logger.error("Error getting EMR integration statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
