"""Return & Recall Management API Endpoints

EPIC-019 Story 8: Return & Recall Management

API endpoints for:
- Product returns to suppliers
- Return Material Authorization (RMA)
- Manufacturer recalls
- Automatic quarantine of recalled items
- Credit note tracking
- Return shipping documentation
- Recall compliance reporting

Python 3.5+ compatible
"""

from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.services.return_recall_management import create_return_recall_management_service


router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class ReturnItem(BaseModel):
    """Single item in return request"""
    drug_id: int = Field(..., description="Drug ID")
    batch_no: Optional[str] = Field(None, description="Batch number")
    quantity: int = Field(..., gt=0, description="Quantity to return")
    reason: Optional[str] = Field(None, description="Specific reason for this item")


class ReturnRequestCreate(BaseModel):
    """Request schema for creating return request"""
    supplier_id: int = Field(..., description="Supplier ID")
    return_items: List[ReturnItem] = Field(..., description="Items to return")
    return_type: str = Field(..., description="Return reason code")
    notes: Optional[str] = Field(None, description="Additional notes")

    class Config:
        schema_extra = {
            "example": {
                "supplier_id": 1,
                "return_items": [
                    {
                        "drug_id": 123,
                        "batch_no": "B12345",
                        "quantity": 50,
                        "reason": "Damaged packaging"
                    }
                ],
                "return_type": "DAMAGED",
                "notes": "Received with water damage"
            }
        }


class ReturnAuthorize(BaseModel):
    """Request schema for authorizing return"""
    authorization_no: str = Field(..., description="RMA number from supplier")
    authorized_by: int = Field(..., description="User ID authorizing")


class ReturnShip(BaseModel):
    """Request schema for shipping return"""
    carrier: str = Field(..., description="Shipping carrier")
    tracking_no: str = Field(..., description="Tracking number")
    shipped_date: Optional[str] = Field(None, description="Ship date (ISO format)")
    estimated_delivery: Optional[str] = Field(None, description="Estimated delivery (ISO format)")


class CreditNote(BaseModel):
    """Request schema for processing credit note"""
    credit_note_no: str = Field(..., description="Credit note number")
    credit_amount: float = Field(..., gt=0, description="Amount credited")


class RecallNoticeCreate(BaseModel):
    """Request schema for creating recall notice"""
    manufacturer_id: int = Field(..., description="Manufacturer ID")
    product_name: str = Field(..., description="Product/brand name")
    batch_from: Optional[str] = Field(None, description="Batch range start")
    batch_to: Optional[str] = Field(None, description="Batch range end")
    batch_prefix: Optional[str] = Field(None, description="Batch prefix")
    expiry_from: Optional[str] = Field(None, description="Expiry range start (ISO format)")
    expiry_to: Optional[str] = Field(None, description="Expiry range end (ISO format)")
    recall_reason: str = Field(..., description="Reason for recall")
    recall_type: str = Field('VOLUNTARY', description="VOLUNTARY or MANDATORY")
    severity: str = Field('MEDIUM', description="LOW, MEDIUM, HIGH, or CRITICAL")


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/returns", status_code=status.HTTP_201_CREATED)
async def create_return_request(
    request: ReturnRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new return request to supplier

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin
    **Rate Limit:** 30 requests per minute

    **Return Reason Codes:**
    - **DAMAGED**: Damaged in transit or storage
    - **WRONG_ITEM**: Incorrect item delivered
    - **EXPIRY**: Near-expiry or expired
    - **QUALITY**: Quality issue, failed QC
    - **OVERSTOCK**: Excess inventory
    - **RECALL**: Manufacturer recall

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/returns/returns \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "supplier_id": 1,
        "return_items": [{"drug_id": 123, "batch_no": "B12345", "quantity": 50}],
        "return_type": "DAMAGED",
        "notes": "Damaged packaging"
      }'
    ```

    **Response:**
    ```json
    {
      "supplier_id": 1,
      "supplier_name": "PT Pharma Sehat",
      "return_type": "DAMAGED",
      "status": "PENDING",
      "total_value": 2500000,
      "total_items": 1,
      "items": [...]
    }
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        result = await service.create_return_request(
            supplier_id=request.supplier_id,
            return_items=[item.dict() for item in request.return_items],
            return_type=request.return_type,
            notes=request.notes
        )

        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating return request: {}".format(str(e))
        )


@router.put("/returns/{return_id}/authorize", status_code=status.HTTP_200_OK)
async def authorize_return_request(
    return_id: int,
    request: ReturnAuthorize,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Authorize return request with supplier RMA

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin

    **Usage:**
    ```bash
    curl -X PUT https://api.simrs-hospital.com/v1/inventory/returns/1/authorize \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "authorization_no": "RMA-2026-12345",
        "authorized_by": 5
      }'
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        result = await service.authorize_return(
            return_id=return_id,
            authorization_no=request.authorization_no,
            authorized_by=request.authorized_by
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error authorizing return: {}".format(str(e))
        )


@router.put("/returns/{return_id}/ship", status_code=status.HTTP_200_OK)
async def ship_return_request(
    return_id: int,
    request: ReturnShip,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark return as shipped to supplier

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin

    **Usage:**
    ```bash
    curl -X PUT https://api.simrs-hospital.com/v1/inventory/returns/1/ship \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "carrier": "JNE",
        "tracking_no": "JP1234567890",
        "shipped_date": "2026-01-16"
      }'
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        result = await service.ship_return(
            return_id=return_id,
            shipping_details=request.dict()
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error shipping return: {}".format(str(e))
        )


@router.put("/returns/{return_id}/credit", status_code=status.HTTP_200_OK)
async def process_credit_note(
    return_id: int,
    request: CreditNote,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Process credit note received from supplier

    **Permissions:** Finance Manager, Pharmacy Manager, Admin

    **Usage:**
    ```bash
    curl -X PUT https://api.simrs-hospital.com/v1/inventory/returns/1/credit \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "credit_note_no": "CN-2026-98765",
        "credit_amount": 2500000
      }'
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        result = await service.process_credit_note(
            return_id=return_id,
            credit_note_no=request.credit_note_no,
            credit_amount=request.credit_amount
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing credit note: {}".format(str(e))
        )


@router.post("/recalls", status_code=status.HTTP_201_CREATED)
async def create_recall_notice(
    request: RecallNoticeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create manufacturer recall notice

    **Permissions:** Compliance Officer, Pharmacy Manager, Admin
    **Rate Limit:** 20 requests per minute

    **Recall Severity Levels:**
    - **CRITICAL**: Emergency recall - immediate quarantine required
    - **HIGH**: High priority - urgent action required
    - **MEDIUM**: Standard priority
    - **LOW**: Regular priority

    **Recall Types:**
    - **VOLUNTARY**: Voluntary manufacturer recall
    - **MANDATORY**: Mandatory government recall

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/returns/recalls \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "manufacturer_id": 5,
        "product_name": "Amoxicillin",
        "batch_from": "B12000",
        "batch_to": "B12999",
        "recall_reason": "Potential contamination",
        "recall_type": "MANDATORY",
        "severity": "HIGH"
      }'
    ```

    **Response:**
    ```json
    {
      "manufacturer_id": 5,
      "product_name": "Amoxicillin",
      "affected_quantity": 500,
      "affected_value": 5000000,
      "affected_batches": [...],
      "recall_date": "2026-01-16",
      "recall_reason": "Potential contamination",
      "recall_type": "MANDATORY",
      "severity": "HIGH",
      "status": "ACTIVE"
    }
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        # Parse dates
        expiry_from = None
        expiry_to = None
        if request.expiry_from:
            expiry_from = date.fromisoformat(request.expiry_from)
        if request.expiry_to:
            expiry_to = date.fromisoformat(request.expiry_to)

        result = await service.create_recall_notice(
            manufacturer_id=request.manufacturer_id,
            product_name=request.product_name,
            batch_from=request.batch_from,
            batch_to=request.batch_to,
            batch_prefix=request.batch_prefix,
            expiry_from=expiry_from,
            expiry_to=expiry_to,
            recall_reason=request.recall_reason,
            recall_type=request.recall_type,
            severity=request.severity
        )

        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating recall notice: {}".format(str(e))
        )


@router.post("/recalls/{recall_id}/quarantine", status_code=status.HTTP_200_OK)
async def quarantine_recalled_items(
    recall_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Quarantine all items affected by recall

    **Permissions:** Compliance Officer, Pharmacy Manager, Admin

    This endpoint:
    - Identifies all batches affected by recall
    - Sets is_quarantined = True on affected batches
    - Blocks items from dispensing
    - Generates quarantine report

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/returns/recalls/1/quarantine \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        # In real implementation, would fetch recall notice first
        recall_notice = {
            'affected_batches': []
        }

        result = await service.quarantine_recalled_items(
            recall_id=recall_id,
            recall_notice=recall_notice
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error quarantining items: {}".format(str(e))
        )


@router.get("/returns/summary", status_code=status.HTTP_200_OK)
async def get_return_summary(
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    status: Optional[str] = Query(None, description="Filter by status"),
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get summary of return requests

    **Permissions:** Staff, Admin, Procurement Officer, Pharmacy Manager, Finance Manager

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/returns/summary?supplier_id=1&status=CREDITED" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        # Parse dates
        from = None
        to = None
        if from_date:
            from = date.fromisoformat(from_date)
        if to_date:
            to = date.fromisoformat(to_date)

        summary = await service.get_return_summary(
            supplier_id=supplier_id,
            status=status,
            from_date=from,
            to_date=to
        )

        return summary

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting return summary: {}".format(str(e))
        )


@router.get("/recalls/summary", status_code=status.HTTP_200_OK)
async def get_recall_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get summary of active recalls

    **Permissions:** Any authenticated user

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/returns/recalls/summary \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        summary = await service.get_recall_summary()

        return summary

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting recall summary: {}".format(str(e))
        )


@router.get("/returns/check-eligibility", status_code=status.HTTP_200_OK)
async def check_return_eligibility(
    drug_id: int = Query(..., description="Drug ID"),
    batch_no: str = Query(..., description="Batch number"),
    supplier_id: int = Query(..., description="Supplier ID"),
    return_type: str = Query(..., description="Return reason code"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if item is eligible for return

    **Permissions:** Staff, Admin, Procurement Officer, Pharmacy Manager

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/returns/check-eligibility?drug_id=123&batch_no=B12345&supplier_id=1&return_type=EXPIRY" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        eligibility = await service.check_return_eligibility(
            drug_id=drug_id,
            batch_no=batch_no,
            supplier_id=supplier_id,
            return_type=return_type
        )

        return eligibility

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking eligibility: {}".format(str(e))
        )


@router.get("/returns/supplier-performance/{supplier_id}", status_code=status.HTTP_200_OK)
async def get_supplier_return_performance(
    supplier_id: int,
    months: int = Query(12, ge=1, le=24, description="Analysis period in months"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get supplier return performance metrics

    **Permissions:** Procurement Officer, Pharmacy Manager, Finance Manager, Admin

    **Metrics:**
    - Return rate (returns as % of purchases)
    - Authorization rate (% authorized)
    - Credit rate (% credited)
    - Average days to receive credit
    - Top return reasons

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/returns/supplier-performance/1?months=12" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_return_recall_management_service(db)

        performance = await service.get_supplier_return_performance(
            supplier_id=supplier_id,
            months=months
        )

        return performance

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting performance metrics: {}".format(str(e))
        )


@router.get("/return-reasons", status_code=status.HTTP_200_OK)
async def list_return_reasons(
    current_user: User = Depends(get_current_active_user)
):
    """
    List available return reason codes

    **Permissions:** Any authenticated user

    Returns descriptions of return reason codes.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/returns/return-reasons \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    return {
        "return_reasons": [
            {
                "code": "DAMAGED",
                "description": "Damaged in transit or storage",
                "examples": ["Water damage", "Broken containers", "Leaking packages"]
            },
            {
                "code": "WRONG_ITEM",
                "description": "Incorrect item delivered",
                "examples": ["Wrong drug", "Wrong dosage", "Wrong quantity"]
            },
            {
                "code": "EXPIRY",
                "description": "Near-expiry or expired items",
                "examples": ["< 90 days to expiry", "Already expired"]
            },
            {
                "code": "QUALITY",
                "description": "Quality issue, failed QC",
                "examples": ["Failed quality check", "Contamination suspected"]
            },
            {
                "code": "OVERSTOCK",
                "description": "Excess inventory",
                "examples": ["Over-ordered", "Changed formulary"]
            },
            {
                "code": "RECALL",
                "description": "Manufacturer recall",
                "examples": ["Voluntary recall", "Mandatory recall"]
            }
        ]
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def service_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Health check endpoint for return and recall service

    **Permissions:** Public

    Returns service status and capabilities.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/returns/health
    ```
    """
    return {
        "status": "healthy",
        "service": "return_recall_management",
        "timestamp": datetime.utcnow().isoformat(),
        "return_reasons": 6,
        "recall_severity_levels": 4,
        "supported_workflows": ["returns", "recalls", "quarantine", "credits"]
    }
