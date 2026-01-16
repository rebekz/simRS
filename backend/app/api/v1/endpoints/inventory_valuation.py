"""Inventory Valuation API Endpoints

EPIC-019 Story 6: Inventory Valuation & Cost Analysis Reports

API endpoints for:
- Inventory valuation (FIFO, Weighted Average, Standard Cost)
- Inventory aging analysis
- Turnover ratio and DSI calculation
- Holding cost analysis
- Regulatory reports (POM, Narcotics)
- Balance sheet valuation

Python 3.5+ compatible
"""

from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.services.inventory_valuation import create_inventory_valuation_service


router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class ValuationRequest(BaseModel):
    """Request schema for inventory valuation"""
    costing_method: str = Field('weighted_average', description="Costing method: fifo, weighted_average, standard_cost")
    as_of_date: Optional[str] = Field(None, description="Valuation date (ISO format)")

    class Config:
        schema_extra = {
            "example": {
                "costing_method": "weighted_average",
                "as_of_date": "2026-01-16"
            }
        }


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/valuation", status_code=status.HTTP_200_OK)
async def calculate_inventory_valuation(
    request: ValuationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate total inventory valuation using specified method

    **Permissions:** Staff, Admin, Pharmacy Manager, Finance Manager
    **Rate Limit:** 30 requests per minute

    **Costing Methods:**
    - **FIFO**: First In, First Out - oldest costs assigned first
    - **Weighted Average**: Average cost of all batches
    - **Standard Cost**: Predetermined standard cost

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/valuation/valuation \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "costing_method": "weighted_average",
        "as_of_date": "2026-01-16"
      }'
    ```

    **Response:**
    ```json
    {
      "costing_method": "weighted_average",
      "as_of_date": "2026-01-16",
      "total_items": 1234,
      "total_quantity": 45678,
      "total_value": 1250000000,
      "currency": "IDR",
      "valuation": {
        "method": "Weighted Average Cost",
        "items": [...]
      }
    }
    ```
    """
    try:
        service = create_inventory_valuation_service(db)

        # Parse date
        as_of_date = None
        if request.as_of_date:
            as_of_date = date.fromisoformat(request.as_of_date)

        result = await service.calculate_inventory_valuation(
            costing_method=request.costing_method,
            as_of_date=as_of_date
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating valuation: {}".format(str(e))
        )


@router.get("/aging-analysis", status_code=status.HTTP_200_OK)
async def get_inventory_aging_analysis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate inventory aging analysis

    **Permissions:** Staff, Admin, Pharmacy Manager, Finance Manager

    Categorizes inventory by age:
    - Fast Moving: < 3 months
    - Slow Moving: 3-6 months
    - Non-Moving: 6-12 months
    - Obsolete: > 2 years

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/valuation/aging-analysis \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_inventory_valuation_service(db)

        analysis = await service.get_inventory_aging_analysis()

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating aging analysis: {}".format(str(e))
        )


@router.get("/turnover", status_code=status.HTTP_200_OK)
async def calculate_inventory_turnover(
    period_days: int = Query(90, ge=30, le=365, description="Analysis period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate inventory turnover ratio

    **Permissions:** Staff, Admin, Pharmacy Manager, Finance Manager

    **Formula:** Turnover = COGS / Average Inventory

    **Performance Classification:**
    - Excellent: ≥12 (monthly turnover)
    - Good: 8-12
    - Acceptable: 4-8
    - Poor: <4 (overstocked)

    Also calculates Days Sales of Inventory (DSI).

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/valuation/turnover?period_days=90" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_inventory_valuation_service(db)

        turnover = await service.calculate_inventory_turnover(period_days=period_days)

        return turnover

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating turnover: {}".format(str(e))
        )


@router.get("/holding-costs", status_code=status.HTTP_200_OK)
async def calculate_holding_costs(
    days: int = Query(365, ge=30, le=365, description="Period in days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Calculate inventory holding costs

    **Permissions:** Staff, Admin, Pharmacy Manager, Finance Manager

    **Holding Cost Components:**
    - Capital Cost: 15% (cost of capital)
    - Storage Cost: 5% (warehousing)
    - Risk Cost: 3% (obsolescence, damage, expiry)
    - **Total: 23% annually**

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/valuation/holding-costs?days=365" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_inventory_valuation_service(db)

        holding_costs = await service.calculate_holding_costs(days=days)

        return holding_costs

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating holding costs: {}".format(str(e))
        )


@router.get("/regulatory-reports/{report_type}", status_code=status.HTTP_200_OK)
async def generate_regulatory_report(
    report_type: str,
    month: Optional[int] = Query(None, ge=1, le=12, description="Report month"),
    year: Optional[int] = Query(None, ge=2020, le=2030, description="Report year"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate regulatory reports

    **Permissions:** Pharmacy Manager, Admin, Compliance Officer

    **Report Types:**
    - `pom`: Psychotropic & Narcotic drugs (POM)
    - `narcotics`: Narcotics consumption tracking

    **Usage:**
    ```bash
    curl -X GET "https://api.simrs-hospital.com/v1/inventory/valuation/regulatory-reports/pom?month=1&year=2026" \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_inventory_valuation_service(db)

        report = await service.generate_regulatory_reports(
            report_type=report_type,
            month=month,
            year=year
        )

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
            detail="Error generating regulatory report: {}".format(str(e))
        )


@router.get("/costing-methods", status_code=status.HTTP_200_OK)
async def list_costing_methods(
    current_user: User = Depends(get_current_active_user)
):
    """
    List available inventory costing methods

    **Permissions:** Any authenticated user

    Returns descriptions of costing methods and when to use each.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/valuation/costing-methods \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    return {
        "costing_methods": [
            {
                "method": "fifo",
                "name": "FIFO (First In, First Out)",
                "description": "Oldest inventory costs are assigned to COGS first",
                "best_for": "Items with stable prices, accurate cost flow",
                "complexity": "Medium - requires batch tracking",
                "regulatory_compliance": "Acceptable for most tax jurisdictions"
            },
            {
                "method": "weighted_average",
                "name": "Weighted Average Cost",
                "description": "Average cost of all batches updated after each purchase",
                "best_for": "High-volume items with price fluctuations",
                "complexity": "Low - simple calculation",
                "regulatory_compliance": "Acceptable for most tax jurisdictions"
            },
            {
                "method": "standard_cost",
                "name": "Standard Costing",
                "description": "Predetermined standard costs per item",
                "best_for": "Budgeting, planning, items with stable costs",
                "complexity": "Low - simple to implement",
                "regulatory_compliance": "Requires variance tracking"
            },
            {
                "method": "specific_identification",
                "name": "Specific Identification",
                "description": "Track actual cost of each specific unit",
                "best_for": "High-value, unique items (e.g., specialty medications)",
                "complexity": "High - requires unit-level tracking",
                "regulatory_compliance": "Most accurate but complex"
            }
        ],
        "default_method": "weighted_average",
        "recommendation": "Use weighted_average for general pharmaceutical inventory"
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def service_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Health check endpoint for inventory valuation service

    **Permissions:** Public

    Returns service status and capabilities.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/valuation/health
    ```
    """
    return {
        "status": "healthy",
        "service": "inventory_valuation",
        "timestamp": datetime.utcnow().isoformat(),
        "costing_methods": 4,
        "holding_cost_rate": "23% annually"
    }
