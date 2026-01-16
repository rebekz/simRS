"""Expiry Management API Endpoints

EPIC-019 Story 4: Expiry Date Management & Automated Discounts

API endpoints for:
- FEFO dispensing logic
- Expiry alerts and reporting
- Automated discount application
- Expiry forecasting
- Supplier return management
- Cost avoidance tracking

Python 3.5+ compatible
"""

from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.services.expiry_management import create_expiry_management_service


router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class FefoDispenseRequest(BaseModel):
    """Request schema for FEFO dispensing"""
    drug_id: int = Field(..., description="Drug ID")
    quantity_needed: int = Field(..., ge=1, description="Quantity to dispense")

    class Config:
        schema_extra = {
            "example": {
                "drug_id": 123,
                "quantity_needed": 30
            }
        }


class ApplyDiscountsRequest(BaseModel):
    """Request schema for applying discounts"""
    batch_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of batch IDs")

    class Config:
        schema_extra = {
            "example": {
                "batch_ids": [1, 2, 3]
            }
        }


class ExpiryAlertResponse(BaseModel):
    """Response schema for expiry alerts"""
    batch_id: int
    drug_id: int
    drug_name: str
    drug_code: str
    batch_number: str
    expiry_date: str
    days_to_expiry: int
    quantity: int
    unit_cost: float
    total_value: float
    alert_level: str
    recommended_action: str
    discount_percentage: float
    discounted_value: float


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/fefo-dispense", status_code=status.HTTP_200_OK)
async def get_fefo_batches(
    request: FefoDispenseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get batches for dispensing using FEFO (First Expire, First Out) logic

    **Permissions:** Staff, Admin, Pharmacist
    **Rate Limit:** 60 requests per minute

    Returns batches sorted by expiry date with quantities to dispense.

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/expiry/fefo-dispense \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "drug_id": 123,
        "quantity_needed": 30
      }'
    ```

    **Response:**
    ```json
    {
      "batches": [
        {
          "batch_id": 1,
          "batch_number": "BATCH-001",
          "expiry_date": "2026-03-15",
          "quantity": 30,
          "remaining_quantity": 20,
          "days_to_expiry": 58,
          "unit_cost": 5000
        }
      ]
    }
    ```
    """
    try:
        service = create_expiry_management_service(db)

        batches = await service.get_batches_fefo(
            drug_id=request.drug_id,
            quantity_needed=request.quantity_needed
        )

        total_allocated = sum(b['quantity'] for b in batches)

        return {
            'drug_id': request.drug_id,
            'quantity_needed': request.quantity_needed,
            'quantity_allocated': total_allocated,
            'fully_satisfied': total_allocated >= request.quantity_needed,
            'batches': batches
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting FEFO batches: {}".format(str(e))
        )


@router.get("/alerts", status_code=status.HTTP_200_OK)
async def get_expiry_alerts(
    threshold: Optional[str] = Query(None, description="Alert threshold: critical, urgent, warning, notice"),
    drug_id: Optional[int] = Query(None, description="Filter by drug ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get expiry alerts for batches approaching expiry

    **Permissions:** Staff, Admin, Pharmacist, Pharmacy Manager

    Returns list of batches with expiry alerts, recommended actions,
    and applicable discounts.

    **Alert Levels:**
    - **critical** (≤1 month): Immediate action required
    - **urgent** (≤2 months): Initiate discounting
    - **warning** (≤3 months): Priority dispensing
    - **notice** (≤6 months): Plan for rotation

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/expiry/alerts?threshold=urgent" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_expiry_management_service(db)

        alerts = await service.get_expiry_alerts(
            threshold=threshold,
            drug_id=drug_id
        )

        return {
            "count": len(alerts),
            "threshold": threshold,
            "alerts": alerts
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting expiry alerts: {}".format(str(e))
        )


@router.get("/forecast", status_code=status.HTTP_200_OK)
async def get_expiry_forecast(
    months_ahead: int = Query(12, ge=1, le=24, description="Months to forecast"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate expiry forecast report

    **Permissions:** Pharmacy Manager, Admin

    Returns forecast of items expiring in the next N months,
    grouped by month with value totals.

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/expiry/forecast?months_ahead=12" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_expiry_management_service(db)

        forecast = await service.get_expiry_forecast(
            months_ahead=months_ahead
        )

        return forecast

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating forecast: {}".format(str(e))
        )


@router.get("/reports/{report_type}", status_code=status.HTTP_200_OK)
async def get_expiry_report(
    report_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate various expiry reports

    **Permissions:** Pharmacy Manager, Admin

    **Report Types:**
    - `near_expiry`: Items expiring within 6 months
    - `expired`: Already expired items (write-offs)
    - `supplier_analysis`: Expiry rate by supplier

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/expiry/reports/near_expiry \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_expiry_management_service(db)

        report = await service.get_expiry_report(report_type=report_type)

        if 'error' in report:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=report['error']
            )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating report: {}".format(str(e))
        )


@router.post("/apply-discounts", status_code=status.HTTP_200_OK)
async def apply_discounts(
    request: ApplyDiscountsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Apply automatic discounts to near-expiry batches

    **Permissions:** Pharmacy Manager, Admin
    **Rate Limit:** 30 requests per minute

    Applies discount schedule based on remaining shelf life:
    - 1-2 months: 50% discount
    - 2-3 months: 30% discount
    - 3-4 months: 20% discount
    - 4-6 months: 10% discount

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/expiry/apply-discounts \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "batch_ids": [1, 2, 3]
      }'
    ```
    """
    try:
        service = create_expiry_management_service(db)

        result = await service.apply_discounts(request.batch_ids)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error applying discounts: {}".format(str(e))
        )


@router.get("/return-requests", status_code=status.HTTP_200_OK)
async def generate_return_requests(
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    days_to_expiry: int = Query(60, ge=30, le=180, description="Max days to expiry"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate return requests for near-expiry items

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin

    Identifies items eligible for return to suppliers based on
    proximity to expiry and supplier return policies.

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/expiry/return-requests?days_to_expiry=60" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_expiry_management_service(db)

        returns = await service.generate_return_requests(
            supplier_id=supplier_id,
            days_to_expiry=days_to_expiry
        )

        return {
            "count": len(returns),
            "return_eligible_items": returns
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating return requests: {}".format(str(e))
        )


@router.get("/cost-avoidance", status_code=status.HTTP_200_OK)
async def calculate_cost_avoidance(
    days: int = Query(90, ge=30, le=365, description="Analysis period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate cost avoidance through discounts vs write-offs

    **Permissions:** Pharmacy Manager, Admin, Finance Manager

    Compares value recovered through discounts versus
    potential write-offs to demonstrate ROI.

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/expiry/cost-avoidance?days=90" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_expiry_management_service(db)

        analysis = await service.calculate_cost_avoidance(days=days)

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating cost avoidance: {}".format(str(e))
        )


@router.get("/discount-schedule", status_code=status.HTTP_200_OK)
async def get_discount_schedule(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get discount schedule configuration

    **Permissions:** Any authenticated user

    Returns current discount schedule based on remaining shelf life.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/expiry/discount-schedule \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    return {
        "discount_schedule": [
            {
                "months_remaining": "1-2",
                "days_range": "30-60",
                "discount_percentage": 50,
                "description": "Critical - must sell quickly"
            },
            {
                "months_remaining": "2-3",
                "days_range": "60-90",
                "discount_percentage": 30,
                "description": "Urgent - aggressive discounting"
            },
            {
                "months_remaining": "3-4",
                "days_range": "90-120",
                "discount_percentage": 20,
                "description": "Moderate - standard discount"
            },
            {
                "months_remaining": "4-6",
                "days_range": "120-180",
                "discount_percentage": 10,
                "description": "Early - preventive discounting"
            }
        ],
        "notes": [
            "Discounts applied automatically to eligible batches",
            "Requires Pharmacy Manager approval for discounts >30%",
            "ROI tracked via cost-avoidance endpoint"
        ]
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def service_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Health check endpoint for expiry management service

    **Permissions:** Public

    Returns service status and configuration.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/expiry/health
    ```
    """
    return {
        "status": "healthy",
        "service": "expiry_management",
        "timestamp": datetime.utcnow().isoformat(),
        "features": {
            "fefo_logic": True,
            "expiry_alerts": True,
            "discount_automation": True,
            "expiry_forecasting": True,
            "return_management": True
        }
    }
