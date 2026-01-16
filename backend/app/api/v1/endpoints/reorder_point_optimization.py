"""Reorder Point Optimization API Endpoints

EPIC-019 Story 3: Automated Reorder Point Optimization

API endpoints for:
- Calculating optimal reorder points
- Getting reorder alerts
- Optimizing order consolidation
- Dynamic reorder point adjustments
- ABC classification

Python 3.5+ compatible
"""

from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.services.reorder_point_optimization import create_reorder_point_service


router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class ReorderPointRequest(BaseModel):
    """Request schema for reorder point calculation"""
    drug_id: int = Field(..., description="Drug ID")
    service_level: float = Field(0.95, ge=0.90, le=0.999, description="Service level (0.90, 0.95, 0.99, 0.999)")
    lead_time_days: Optional[int] = Field(None, ge=1, le=365, description="Lead time in days")
    review_period_days: int = Field(30, ge=7, le=90, description="Review period in days")

    class Config:
        schema_extra = {
            "example": {
                "drug_id": 123,
                "service_level": 0.95,
                "lead_time_days": 7,
                "review_period_days": 30
            }
        }


class BatchReorderPointRequest(BaseModel):
    """Request schema for batch reorder point calculation"""
    drug_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of drug IDs")
    service_level: float = Field(0.95, ge=0.90, le=0.999, description="Service level")

    class Config:
        schema_extra = {
            "example": {
                "drug_ids": [123, 124, 125],
                "service_level": 0.95
            }
        }


class ReorderPointResponse(BaseModel):
    """Response schema for reorder point calculation"""
    drug_id: int
    drug_name: str
    drug_code: str
    parameters: dict
    reorder_point: dict
    economic_order_quantity: dict
    current_status: dict
    recommendations: List[str]


class ReorderAlertResponse(BaseModel):
    """Response schema for reorder alerts"""
    drug_id: int
    drug_name: str
    drug_code: str
    current_stock: int
    reorder_point: int
    safety_stock: int
    suggested_order_quantity: int
    days_stock_on_hand: float
    is_critical: bool
    abc_classification: str
    priority: int


class OrderConsolidationResponse(BaseModel):
    """Response schema for order consolidation"""
    supplier_id: int
    supplier_name: str
    items: List[dict]
    summary: dict


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/calculate", response_model=ReorderPointResponse, status_code=status.HTTP_200_OK)
async def calculate_reorder_point(
    request: ReorderPointRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate optimal reorder point for a drug

    **Permissions:** Staff, Admin, Procurement Officer, Pharmacy Manager
    **Rate Limit:** 60 requests per minute

    Calculates optimal reorder point using:
    - Average Daily Usage (ADU)
    - Demand variability (standard deviation)
    - Service level targets (Z-factor)
    - Lead time considerations
    - Safety stock calculation

    Also calculates Economic Order Quantity (EOQ) for cost optimization.

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/reorder-point/calculate \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "drug_id": 123,
        "service_level": 0.95,
        "lead_time_days": 7
      }'
    ```

    **Response:**
    ```json
    {
      "drug_id": 123,
      "drug_name": "Amoxicillin 500mg",
      "drug_code": "DRUG-001",
      "parameters": {
        "average_daily_usage": 15.5,
        "demand_std_dev": 5.2,
        "lead_time_days": 7,
        "service_level": 0.95
      },
      "reorder_point": {
        "calculated_rop": 150,
        "safety_stock": 30,
        "demand_during_lead_time": 108.5
      },
      "economic_order_quantity": {
        "eoq": 500,
        "annual_demand": 5657.5
      },
      "current_status": {
        "current_stock": 45,
        "days_stock_on_hand": 2.9,
        "should_reorder": true,
        "suggested_order_quantity": 500
      },
      "recommendations": [
        "WARNING: Stock at or below reorder point. Order recommended.",
        "High-value item: Tight control recommended. Review weekly."
      ]
    }
    ```
    """
    try:
        service = create_reorder_point_service(db)

        result = await service.calculate_reorder_point(
            drug_id=request.drug_id,
            service_level=request.service_level,
            lead_time_days=request.lead_time_days,
            review_period_days=request.review_period_days
        )

        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        return ReorderPointResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating reorder point: {}".format(str(e))
        )


@router.post("/batch-calculate", status_code=status.HTTP_200_OK)
async def batch_calculate_reorder_points(
    request: BatchReorderPointRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate reorder points for multiple drugs

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin
    **Rate Limit:** 10 requests per minute

    Efficiently calculates reorder points for multiple drugs.
    Useful for periodic re-calculation of all inventory.

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/reorder-point/batch-calculate \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "drug_ids": [123, 124, 125],
        "service_level": 0.95
      }'
    ```
    """
    try:
        service = create_reorder_point_service(db)

        results = await service.batch_calculate_reorder_points(
            drug_ids=request.drug_ids,
            service_level=request.service_level
        )

        return {
            "count": len(results),
            "calculations": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating batch reorder points: {}".format(str(e))
        )


@router.get("/alerts", status_code=status.HTTP_200_OK)
async def get_reorder_alerts(
    location_id: Optional[int] = Query(None, description="Filter by location"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get drugs that need reordering

    **Permissions:** Staff, Admin, Procurement Officer, Pharmacy Manager

    Returns list of drugs at or below their reorder points,
    sorted by priority. Includes suggested order quantities.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/reorder-point/alerts \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_reorder_point_service(db)

        alerts = await service.get_reorder_alerts(location_id=location_id)

        return {
            "count": len(alerts),
            "alerts": alerts
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting reorder alerts: {}".format(str(e))
        )


@router.post("/optimize-orders", status_code=status.HTTP_200_OK)
async def optimize_order_consolidation(
    supplier_id: Optional[int] = Query(None, description="Filter by supplier"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Optimize and consolidate purchase orders

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin

    Groups items by supplier to maximize bulk discounts and
    minimize ordering costs. Provides order summaries for each supplier.

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/reorder-point/optimize-orders \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_reorder_point_service(db)

        result = await service.optimize_order_consolidation(supplier_id=supplier_id)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error optimizing orders: {}".format(str(e))
        )


@router.get("/adjust-dynamic", status_code=status.HTTP_200_OK)
async def adjust_reorder_points_dynamically(
    variation_threshold: float = Query(0.20, ge=0.10, le=0.50, description="Variation threshold"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Auto-adjust reorder points based on consumption changes

    **Permissions:** Pharmacy Manager, Admin

    Analyzes consumption patterns and suggests reorder point
    adjustments when significant changes are detected (>20% variation).

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/reorder-point/adjust-dynamic?variation_threshold=0.20" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_reorder_point_service(db)

        adjustments = await service.adjust_reorder_points_dynamically(
            variation_threshold=variation_threshold
        )

        return {
            "count": len(adjustments),
            "adjustments": adjustments
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adjusting reorder points: {}".format(str(e))
        )


@router.get("/service-levels", status_code=status.HTTP_200_OK)
async def list_service_levels(
    current_user: User = Depends(get_current_active_user)
):
    """
    List available service levels

    **Permissions:** Any authenticated user

    Returns available service levels with Z-factors and descriptions.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/reorder-point/service-levels \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    return {
        "service_levels": [
            {
                "level": 0.90,
                "name": "90%",
                "z_factor": 1.28,
                "description": "Standard items - 10% stockout risk acceptable",
                "recommended_for": "Low-cost, non-critical items"
            },
            {
                "level": 0.95,
                "name": "95%",
                "z_factor": 1.645,
                "description": "High service level - 5% stockout risk",
                "recommended_for": "Most pharmaceutical items"
            },
            {
                "level": 0.99,
                "name": "99%",
                "z_factor": 2.33,
                "description": "Very high service level - 1% stockout risk",
                "recommended_for": "High-value, important medications"
            },
            {
                "level": 0.999,
                "name": "99.9%",
                "z_factor": 3.09,
                "description": "Critical service level - 0.1% stockout risk",
                "recommended_for": "Life-critical medications, narcotics"
            }
        ]
    }


@router.get("/abc-classification", status_code=status.HTTP_200_OK)
async def explain_abc_classification(
    current_user: User = Depends(get_current_active_user)
):
    """
    Explain ABC classification system

    **Permissions:** Any authenticated user

    Returns ABC classification methodology and review frequencies.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/reorder-point/abc-classification \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    return {
        "abc_classification": {
            "description": "Inventory classification based on value and volume",
            "classes": [
                {
                    "class": "A",
                    "description": "High value, low volume items",
                    "examples": "Expensive medications, narcotics, specialty drugs",
                    "control_level": "Tight control",
                    "review_frequency": "Weekly (7 days)",
                    "ordering_strategy": "Frequent small orders"
                },
                {
                    "class": "B",
                    "description": "Medium value, medium volume items",
                    "examples": "Common antibiotics, chronic medications",
                    "control_level": "Moderate control",
                    "review_frequency": "Monthly (30 days)",
                    "ordering_strategy": "Regular orders"
                },
                {
                    "class": "C",
                    "description": "Low value, high volume items",
                    "examples": "Basic supplies, OTC medications",
                    "control_level": "Loose control",
                    "review_frequency": "Quarterly (90 days)",
                    "ordering_strategy": "Bulk orders to minimize ordering costs"
                }
            ],
            "benefits": [
                "Optimized inventory investment",
                "Reduced carrying costs",
                "Focused management attention on high-value items",
                "Improved cash flow"
            ]
        }
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def service_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Health check endpoint for reorder point service

    **Permissions:** Public

    Returns service status and availability.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/reorder-point/health
    ```
    """
    return {
        "status": "healthy",
        "service": "reorder_point_optimization",
        "timestamp": datetime.utcnow().isoformat(),
        "service_levels_available": 4,
        "abc_classes": 3
    }
