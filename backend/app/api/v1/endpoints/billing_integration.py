"""Billing System Integration API Endpoints for STORY-024-07

This module provides API endpoints for:
- External billing system management
- Claims submission and tracking
- Payment reconciliation
- Remittance advice processing

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
from app.services.billing_integration import get_billing_integration_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class BillingSystemRegisterRequest(BaseModel):
    """Request to register billing system"""
    system_code: str = Field(..., description="System code")
    system_name: str = Field(..., description="System name")
    system_type: str = Field(..., description="System type (clearinghouse, insurance, payer)")
    protocol: str = Field(..., description="Communication protocol")
    organization: Optional[str] = Field(None, description="Organization name")
    payer_id: Optional[str] = Field(None, description="Payer ID")
    contact_name: Optional[str] = Field(None, description="Contact name")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    endpoint_url: Optional[str] = Field(None, description="Endpoint URL")
    auth_type: Optional[str] = Field(None, description="Authentication type")
    is_bpjs: bool = Field(False, description="Is BPJS system")
    bpjs_sep_type: Optional[str] = Field(None, description="BPJS SEP type")
    test_mode: bool = Field(False, description="Test mode")


class ClaimSubmitRequest(BaseModel):
    """Request to submit claim"""
    invoice_id: int = Field(..., description="Invoice ID")
    billing_system_id: int = Field(..., description="Billing system ID")
    claim_type: str = Field(..., description="Claim type (institutional, professional)")
    patient_id: int = Field(..., description="Patient ID")
    encounter_id: Optional[int] = Field(None, description="Encounter ID")
    claim_amount: float = Field(..., description="Total claim amount")
    service_start_date: datetime = Field(..., description="Service start date")
    service_end_date: datetime = Field(..., description="Service end date")
    principal_diagnosis: Optional[str] = Field(None, description="Principal diagnosis code")
    principal_diagnosis_desc: Optional[str] = Field(None, description="Principal diagnosis description")
    procedures: Optional[dict] = Field(None, description="Procedures and charges")


class PaymentProcessRequest(BaseModel):
    """Request to process payment"""
    claim_submission_id: int = Field(..., description="Claim submission ID")
    patient_id: int = Field(..., description="Patient ID")
    payment_amount: float = Field(..., description="Payment amount")
    payment_date: datetime = Field(..., description="Payment date")
    payment_method: Optional[str] = Field(None, description="Payment method")
    payment_reference: Optional[str] = Field(None, description="Payment reference")
    payer_name: Optional[str] = Field(None, description="Payer name")
    payer_id: Optional[str] = Field(None, description="Payer ID")
    check_number: Optional[str] = Field(None, description="Check number")


# =============================================================================
# Billing System Management Endpoints
# =============================================================================

@router.post("/systems", status_code=status.HTTP_201_CREATED)
async def register_billing_system(
    request: BillingSystemRegisterRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Register external billing system (admin only)"""
    try:
        service = get_billing_integration_service(db)

        result = await service.register_billing_system(
            system_code=request.system_code,
            system_name=request.system_name,
            system_type=request.system_type,
            protocol=request.protocol,
            organization=request.organization,
            payer_id=request.payer_id,
            contact_name=request.contact_name,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            endpoint_url=request.endpoint_url,
            auth_type=request.auth_type,
            is_bpjs=request.is_bpjs,
            bpjs_sep_type=request.bpjs_sep_type,
            test_mode=request.test_mode
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
        logger.error("Error registering billing system: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register billing system"
        )


@router.get("/systems")
async def list_billing_systems(
    system_type: Optional[str] = Query(None, description="Filter by system type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List billing systems"""
    try:
        from app.models.billing_integration import BillingSystem
        from sqlalchemy import select, and_

        # Build filters
        filters = []
        if system_type:
            filters.append(BillingSystem.system_type == system_type)
        if is_active is not None:
            filters.append(BillingSystem.is_active == is_active)

        # Get systems
        query = select(BillingSystem)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(BillingSystem.system_name)

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
                "payer_id": s.payer_id,
                "protocol": s.protocol,
                "status": s.status,
                "is_active": s.is_active,
                "is_bpjs": s.is_bpjs
            }
            for s in systems
        ]

        return {
            "systems": system_list
        }

    except Exception as e:
        logger.error("Error listing billing systems: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list billing systems"
        )


# =============================================================================
# Claim Submission Endpoints
# =============================================================================

@router.post("/claims/submit", status_code=status.HTTP_201_CREATED)
async def submit_claim(
    request: ClaimSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit claim to billing system"""
    try:
        service = get_billing_integration_service(db)

        # Build claim data
        claim_data = {
            "patient_id": request.patient_id,
            "encounter_id": request.encounter_id,
            "claim_type": request.claim_type,
            "claim_amount": request.claim_amount,
            "service_start_date": request.service_start_date,
            "service_end_date": request.service_end_date,
            "principal_diagnosis": request.principal_diagnosis,
            "principal_diagnosis_desc": request.principal_diagnosis_desc,
            "procedures": request.procedures
        }

        result = await service.submit_claim(
            invoice_id=request.invoice_id,
            billing_system_id=request.billing_system_id,
            claim_data=claim_data,
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
        logger.error("Error submitting claim: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit claim"
        )


@router.get("/claims/{claim_number}")
async def get_claim_status(
    claim_number: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get claim status by claim number"""
    try:
        service = get_billing_integration_service(db)

        result = await service.get_claim_status(claim_number)

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
        logger.error("Error getting claim status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get claim status"
        )


@router.get("/claims")
async def list_claims(
    billing_system_id: Optional[int] = Query(None, description="Filter by billing system"),
    patient_id: Optional[int] = Query(None, description="Filter by patient"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List claims with filtering"""
    try:
        from app.models.billing_integration import ClaimSubmission
        from sqlalchemy import select, func, and_

        # Build filters
        filters = []
        if billing_system_id:
            filters.append(ClaimSubmission.billing_system_id == billing_system_id)
        if patient_id:
            filters.append(ClaimSubmission.patient_id == patient_id)
        if status:
            filters.append(ClaimSubmission.status == status)
        if start_date:
            filters.append(ClaimSubmission.created_at >= start_date)
        if end_date:
            filters.append(ClaimSubmission.created_at <= end_date)

        # Get total count
        count_query = select(func.count(ClaimSubmission.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get claims with pagination
        offset = (page - 1) * per_page
        query = select(ClaimSubmission)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(ClaimSubmission.created_at.desc()).limit(per_page).offset(offset)

        result = await db.execute(query)
        claims = result.scalars().all()

        # Build response
        claim_list = [
            {
                "submission_id": c.submission_id,
                "claim_number": c.claim_number,
                "patient_id": c.patient_id,
                "claim_type": c.claim_type,
                "claim_amount": c.claim_amount,
                "approved_amount": c.approved_amount,
                "status": c.status,
                "submitted_at": c.submitted_at.isoformat() if c.submitted_at else None,
                "processed_at": c.processed_at.isoformat() if c.processed_at else None
            }
            for c in claims
        ]

        return {
            "claims": claim_list,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
        }

    except Exception as e:
        logger.error("Error listing claims: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list claims"
        )


# =============================================================================
# Payment Processing Endpoints
# =============================================================================

@router.post("/payments/process", status_code=status.HTTP_201_CREATED)
async def process_payment(
    request: PaymentProcessRequest,
    billing_system_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process payment from billing system"""
    try:
        service = get_billing_integration_service(db)

        payment_data = {
            "claim_submission_id": request.claim_submission_id,
            "patient_id": request.patient_id,
            "payment_amount": request.payment_amount,
            "payment_date": request.payment_date,
            "payment_method": request.payment_method,
            "payment_reference": request.payment_reference,
            "payer_name": request.payer_name,
            "payer_id": request.payer_id,
            "check_number": request.check_number
        }

        result = await service.process_payment(
            payment_data=payment_data,
            billing_system_id=billing_system_id
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
        logger.error("Error processing payment: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process payment"
        )


@router.post("/remittance")
async def process_remittance_advice(
    billing_system_id: int,
    x835_content: str = Query(..., description="EDI 835 content"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process electronic remittance advice (X835)"""
    try:
        service = get_billing_integration_service(db)

        result = await service.process_remittance_advice(
            x835_content=x835_content,
            billing_system_id=billing_system_id
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error processing remittance advice: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process remittance advice"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_billing_integration_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get billing integration statistics"""
    try:
        from app.models.billing_integration import BillingSystem, ClaimSubmission, ClaimPayment
        from sqlalchemy import select, func

        # Get total counts
        system_query = select(func.count(BillingSystem.id)).where(BillingSystem.is_active == True)
        system_result = await db.execute(system_query)
        total_systems = system_result.scalar() or 0

        claim_query = select(func.count(ClaimSubmission.id))
        claim_result = await db.execute(claim_query)
        total_claims = claim_result.scalar() or 0

        payment_query = select(func.count(ClaimPayment.id))
        payment_result = await db.execute(payment_query)
        total_payments = payment_result.scalar() or 0

        # Get claim status breakdown
        status_query = select(
            ClaimSubmission.status,
            func.count(ClaimSubmission.id).label("count")
        ).group_by(ClaimSubmission.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # Get total claim amounts
        amount_query = select(
            func.sum(ClaimSubmission.claim_amount).label("total_claimed"),
            func.sum(ClaimSubmission.approved_amount).label("total_approved"),
            func.sum(ClaimSubmission.insurance_payment_amount).label("total_paid")
        )
        amount_result = await db.execute(amount_query)
        amount_row = amount_result.first()

        return {
            "total_systems": total_systems,
            "total_claims": total_claims,
            "total_payments": total_payments,
            "status_counts": status_counts,
            "amounts": {
                "total_claimed": float(amount_row[0]) if amount_row[0] else 0,
                "total_approved": float(amount_row[1]) if amount_row[1] else 0,
                "total_paid": float(amount_row[2]) if amount_row[2] else 0
            },
            "summary": {
                "submitted": status_counts.get("submitted", 0),
                "approved": status_counts.get("approved", 0),
                "paid": status_counts.get("paid", 0),
                "rejected": status_counts.get("rejected", 0),
                "denied": status_counts.get("denied", 0)
            }
        }

    except Exception as e:
        logger.error("Error getting billing integration statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
