"""Supplier Performance API Endpoints

EPIC-019 Story 5: Supplier Performance Tracking & Scoring

API endpoints for:
- Supplier performance scoring
- Multi-dimensional evaluation (Delivery, Quality, Price, Service)
- Supplier rankings
- Performance trend analysis
- Component score breakdowns

Python 3.5+ compatible
"""

from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.services.supplier_performance import create_supplier_performance_service


router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class SupplierScoreRequest(BaseModel):
    """Request schema for supplier score calculation"""
    supplier_id: int = Field(..., description="Supplier ID")
    start_date: Optional[str] = Field(None, description="Start date (ISO format)")
    end_date: Optional[str] = Field(None, description="End date (ISO format)")

    class Config:
        schema_extra = {
            "example": {
                "supplier_id": 1,
                "start_date": "2025-10-01",
                "end_date": "2025-12-31"
            }
        }


class ScoreResponse(BaseModel):
    """Response schema for supplier score"""
    supplier_id: int
    supplier_name: str
    total_score: float
    performance_level: str
    component_scores: dict
    recommendations: List[str]


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/score", response_model=ScoreResponse, status_code=status.HTTP_200_OK)
async def calculate_supplier_score(
    request: SupplierScoreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate comprehensive performance score for a supplier

    **Permissions:** Staff, Admin, Procurement Officer, Pharmacy Manager
    **Rate Limit:** 60 requests per minute

    Calculates weighted score across 4 dimensions:
    - Delivery (40%): On-time rate, fulfillment, lead time
    - Quality (30%): Damage rate, wrong items, expiry, documentation
    - Price (20%): E-Katalog comparison, stability, discounts
    - Service (10%): Responsiveness, communication, problem resolution

    **Performance Levels:**
    - Excellent: 90-100
    - Good: 75-89
    - Acceptable: 60-74
    - Poor: 40-59
    - Unacceptable: <40

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/suppliers/score \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "supplier_id": 1,
        "start_date": "2025-10-01",
        "end_date": "2025-12-31"
      }'
    ```

    **Response:**
    ```json
    {
      "supplier_id": 1,
      "supplier_name": "PT Pharma Sehat",
      "total_score": 87.5,
      "performance_level": "good",
      "component_scores": {
        "delivery": {
          "score": 92.5,
          "components": {
            "on_time_delivery_rate": {"value": 95.0, "weight": 60},
            "complete_fulfillment_rate": {"value": 90.0, "weight": 30},
            "lead_time_adherence": {"value": 85.0, "weight": 10}
          }
        },
        "quality": {"score": 85.0},
        "price": {"score": 82.0},
        "service": {"score": 75.0}
      },
      "recommendations": [
        "Good performance overall - consider preferred designation"
      ]
    }
    ```
    """
    try:
        service = create_supplier_performance_service(db)

        # Parse dates
        start_date = None
        end_date = None
        if request.start_date:
            start_date = date.fromisoformat(request.start_date)
        if request.end_date:
            end_date = date.fromisoformat(request.end_date)

        result = await service.calculate_supplier_score(
            supplier_id=request.supplier_id,
            start_date=start_date,
            end_date=end_date
        )

        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        return ScoreResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating supplier score: {}".format(str(e))
        )


@router.get("/rankings", status_code=status.HTTP_200_OK)
async def get_supplier_rankings(
    limit: int = Query(10, ge=1, le=50, description="Number of top suppliers"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get supplier performance rankings

    **Permissions:** Staff, Admin, Procurement Officer, Pharmacy Manager

    Returns ranked list of suppliers based on comprehensive
    performance scores. Includes top and bottom performers.

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/suppliers/rankings?limit=10" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_supplier_performance_service(db)

        rankings = await service.get_supplier_rankings(limit=limit)

        return rankings

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting rankings: {}".format(str(e))
        )


@router.get("/trends/{supplier_id}", status_code=status.HTTP_200_OK)
async def get_performance_trends(
    supplier_id: int,
    months: int = Query(6, ge=3, le=12, description="Number of months to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get performance trends for a supplier

    **Permissions:** Staff, Admin, Procurement Officer, Pharmacy Manager

    Returns monthly performance data to identify trends
    (improving, stable, declining).

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/suppliers/trends/1?months=6" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_supplier_performance_service(db)

        trends = await service.get_performance_trends(
            supplier_id=supplier_id,
            months=months
        )

        return trends

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting trends: {}".format(str(e))
        )


@router.get("/batch-scores", status_code=status.HTTP_200_OK)
async def batch_calculate_scores(
    supplier_ids: Optional[str] = Query(None, description="Comma-separated supplier IDs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate scores for multiple suppliers in batch

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin
    **Rate Limit:** 10 requests per minute

    Efficiently calculates scores for multiple suppliers.
    Useful for periodic re-evaluation of all suppliers.

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/suppliers/batch-scores?supplier_ids=1,2,3" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_supplier_performance_service(db)

        # Parse supplier IDs
        supplier_id_list = None
        if supplier_ids:
            supplier_id_list = [int(s.strip()) for s in supplier_ids.split(',')]

        scores = await service.batch_calculate_scores(supplier_ids=supplier_id_list)

        return {
            "count": len(scores),
            "scores": scores
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating batch scores: {}".format(str(e))
        )


@router.get("/scoring-methodology", status_code=status.HTTP_200_OK)
async def explain_scoring_methodology(
    current_user: User = Depends(get_current_active_user)
):
    """
    Explain supplier scoring methodology

    **Permissions:** Any authenticated user

    Returns detailed explanation of scoring algorithm and
    component weights.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/suppliers/scoring-methodology \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    return {
        "scoring_methodology": {
            "overview": "Multi-dimensional weighted scoring system",
            "formula": "Total Score = (Delivery × 0.40) + (Quality × 0.30) + (Price × 0.20) + (Service × 0.10)",
            "dimensions": [
                {
                    "name": "Delivery",
                    "weight": "40%",
                    "description": "On-time delivery, fulfillment rate, lead time adherence",
                    "components": [
                        {
                            "name": "On-time Delivery Rate",
                            "weight": "60%",
                            "description": "Orders delivered on or before expected date"
                        },
                        {
                            "name": "Complete Fulfillment Rate",
                            "weight": "30%",
                            "description": "Orders with complete quantity delivered"
                        },
                        {
                            "name": "Lead Time Adherence",
                            "weight": "10%",
                            "description": "Actual lead time vs expected lead time"
                        }
                    ]
                },
                {
                    "name": "Quality",
                    "weight": "30%",
                    "description": "Damage rate, wrong items, expiry, documentation",
                    "components": [
                        {
                            "name": "Damage Rate",
                            "weight": "40%",
                            "description": "Quarantined/damaged items received"
                        },
                        {
                            "name": "Wrong Item Rate",
                            "weight": "30%",
                            "description": "Incorrect items shipped"
                        },
                        {
                            "name": "Expiry Rate",
                            "weight": "20%",
                            "description": "Items with short remaining shelf life"
                        },
                        {
                            "name": "Documentation",
                            "weight": "10%",
                            "description": "Quality of delivery documentation"
                        }
                    ]
                },
                {
                    "name": "Price",
                    "weight": "20%",
                    "description": "E-Katalog comparison, price stability, volume discounts",
                    "components": [
                        {
                            "name": "E-Katalog Comparison",
                            "weight": "60%",
                            "description": "Price vs government E-Katalog reference"
                        },
                        {
                            "name": "Price Stability",
                            "weight": "20%",
                            "description": "Consistency of pricing over time"
                        },
                        {
                            "name": "Volume Discounts",
                            "weight": "20%",
                            "description": "Discount terms for bulk orders"
                        }
                    ]
                },
                {
                    "name": "Service",
                    "weight": "10%",
                    "description": "Responsiveness, communication, problem resolution",
                    "components": [
                        {"name": "Responsiveness", "description": "Response time to inquiries"},
                        {"name": "Communication", "description": "Quality of communication"},
                        {"name": "Problem Resolution", "description": "Handling of issues and complaints"}
                    ]
                }
            ],
            "performance_levels": {
                "excellent": {"range": "90-100", "description": "Outstanding performance"},
                "good": {"range": "75-89", "description": "Above average performance"},
                "acceptable": {"range": "60-74", "description": "Meets minimum requirements"},
                "poor": {"range": "40-59", "description": "Below standard - improvement needed"},
                "unacceptable": {"range": "0-39", "description": "Fails to meet standards - replacement recommended"}
            },
            "recalculation": "Monthly scores recommended",
            "data_collection": "Automated from POs, receipts, and manual surveys"
        }
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def service_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Health check endpoint for supplier performance service

    **Permissions:** Public

    Returns service status and capabilities.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/suppliers/health
    ```
    """
    return {
        "status": "healthy",
        "service": "supplier_performance_tracking",
        "timestamp": datetime.utcnow().isoformat(),
        "dimensions": 4,
        "scoring_frequency": "Monthly recommended"
    }
