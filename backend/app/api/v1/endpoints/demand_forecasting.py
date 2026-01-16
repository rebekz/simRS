"""Demand Forecasting API Endpoints

EPIC-019 Story 1: Demand Forecasting & Predictive Ordering

API endpoints for:
- Generating demand forecasts
- Purchase order suggestions
- Forecast accuracy reports
- Batch forecasting for multiple drugs
- Forecast algorithm comparison

Python 3.5+ compatible
"""

from datetime import date, datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.api.deps import get_db, get_current_active_user
from app.models.users import User
from app.services.demand_forecasting import create_demand_forecasting_service


router = APIRouter()


# =============================================================================
# Request/Response Schemas
# =============================================================================

class ForecastRequest(BaseModel):
    """Request schema for demand forecast"""
    drug_id: int = Field(..., description="Drug ID")
    forecast_horizon: int = Field(30, ge=7, le=90, description="Forecast horizon in days")
    algorithm: Optional[str] = Field(None, description="Algorithm: simple_moving_average, exponential_smoothing, linear_regression")
    historical_days: int = Field(365, ge=30, le=1095, description="Days of historical data")

    class Config:
        schema_extra = {
            "example": {
                "drug_id": 123,
                "forecast_horizon": 30,
                "algorithm": None,
                "historical_days": 365
            }
        }


class PurchaseSuggestionRequest(BaseModel):
    """Request schema for purchase suggestions"""
    drug_id: int = Field(..., description="Drug ID")
    forecast_horizon: int = Field(30, ge=7, le=90, description="Forecast horizon in days")
    algorithm: Optional[str] = Field(None, description="Forecasting algorithm")

    class Config:
        schema_extra = {
            "example": {
                "drug_id": 123,
                "forecast_horizon": 30
            }
        }


class BatchForecastRequest(BaseModel):
    """Request schema for batch forecasting"""
    drug_ids: List[int] = Field(..., min_items=1, max_items=100, description="List of drug IDs")
    forecast_horizon: int = Field(30, ge=7, le=90, description="Forecast horizon in days")

    class Config:
        schema_extra = {
            "example": {
                "drug_ids": [123, 124, 125],
                "forecast_horizon": 30
            }
        }


class ForecastResponse(BaseModel):
    """Response schema for forecast"""
    drug_id: int
    algorithm: str
    forecast_horizon: int
    forecast: List[dict]
    confidence_intervals: List[dict]
    mape: Optional[float] = None


class PurchaseSuggestionResponse(BaseModel):
    """Response schema for purchase suggestion"""
    drug_id: int
    drug_name: str
    drug_code: str
    forecast_summary: dict
    current_stock: int
    open_orders: int
    suggested_order_quantity: int
    budget_impact: dict
    reorder_point: int
    lead_time_days: int
    is_critical: bool


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/forecast", response_model=ForecastResponse, status_code=status.HTTP_200_OK)
async def generate_forecast(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate demand forecast for a drug

    **Permissions:** Staff, Admin, Procurement Officer
    **Rate Limit:** 60 requests per minute

    Generates demand forecast using selected or auto-detected algorithm.
    Includes confidence intervals (80%, 90%, 95%).

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/forecasting/forecast \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "drug_id": 123,
        "forecast_horizon": 30,
        "algorithm": "simple_moving_average"
      }'
    ```
    """
    try:
        service = create_demand_forecasting_service(db)

        result = await service.generate_forecast(
            drug_id=request.drug_id,
            forecast_horizon=request.forecast_horizon,
            algorithm=request.algorithm,
            historical_days=request.historical_days
        )

        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        return ForecastResponse(
            drug_id=result['drug_id'],
            algorithm=result['algorithm'],
            forecast_horizon=request.forecast_horizon,
            forecast=result['forecast'],
            confidence_intervals=result.get('confidence_intervals', []),
            mape=result.get('mape')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating forecast: {}".format(str(e))
        )


@router.post("/purchase-suggestions", response_model=PurchaseSuggestionResponse, status_code=status.HTTP_200_OK)
async def generate_purchase_suggestion(
    request: PurchaseSuggestionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate purchase order suggestion based on forecast

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin
    **Rate Limit:** 30 requests per minute

    Analyzes forecasted demand, current stock, and open orders
    to suggest optimal purchase quantities with budget impact.

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/forecasting/purchase-suggestions \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "drug_id": 123,
        "forecast_horizon": 30
      }'
    ```
    """
    try:
        service = create_demand_forecasting_service(db)

        result = await service.generate_purchase_suggestions(
            drug_id=request.drug_id,
            forecast_horizon=request.forecast_horizon,
            algorithm=request.algorithm
        )

        if 'error' in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result['error']
            )

        return PurchaseSuggestionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating purchase suggestion: {}".format(str(e))
        )


@router.post("/batch-forecast", status_code=status.HTTP_200_OK)
async def batch_generate_forecasts(
    request: BatchForecastRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate forecasts for multiple drugs in batch

    **Permissions:** Procurement Officer, Pharmacy Manager, Admin
    **Rate Limit:** 10 requests per minute

    Efficiently generates forecasts for multiple drugs.
    Useful for nightly batch jobs or periodic re-forecasting.

    **Usage:**
    ```bash
    curl -X POST https://api.simrs-hospital.com/v1/inventory/forecasting/batch-forecast \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -d '{
        "drug_ids": [123, 124, 125],
        "forecast_horizon": 30
      }'
    ```
    """
    try:
        service = create_demand_forecasting_service(db)

        results = await service.batch_forecast(
            drug_ids=request.drug_ids,
            forecast_horizon=request.forecast_horizon
        )

        return {
            "count": len(results),
            "forecasts": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating batch forecasts: {}".format(str(e))
        )


@router.get("/accuracy/{drug_id}", status_code=status.HTTP_200_OK)
async def get_forecast_accuracy(
    drug_id: int,
    algorithm: Optional[str] = Query(None, description="Algorithm to evaluate"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get forecast accuracy report for a drug

    **Permissions:** Staff, Admin, Procurement Officer

    Evaluates forecast accuracy by comparing predictions against actuals
    from the last 30 days. Provides MAPE, MAD, RMSE, and bias metrics.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/forecasting/accuracy/123 \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    try:
        service = create_demand_forecasting_service(db)

        result = await service.get_forecast_accuracy_report(
            drug_id=drug_id,
            algorithm=algorithm
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
            detail="Error getting accuracy report: {}".format(str(e))
        )


@router.get("/algorithms", status_code=status.HTTP_200_OK)
async def list_algorithms(
    current_user: User = Depends(get_current_active_user)
):
    """
    List available forecasting algorithms

    **Permissions:** Any authenticated user

    Returns list of available forecasting algorithms with descriptions.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/forecasting/algorithms \\
      -H "Authorization: Bearer YOUR_TOKEN"
    ```
    """
    return {
        "algorithms": [
            {
                "name": "simple_moving_average",
                "description": "Best for stable demand with low variability",
                "parameters": {
                    "window": "Moving average window size (default: 30 days)"
                }
            },
            {
                "name": "exponential_smoothing",
                "description": "Best for trending items with moderate variability",
                "parameters": {
                    "alpha": "Smoothing parameter 0-1 (default: 0.3)"
                }
            },
            {
                "name": "linear_regression",
                "description": "Best for items with strong trends or seasonality",
                "parameters": {
                    "trend": "Linear trend coefficient"
                }
            }
        ]
    }


@router.get("/health", status_code=status.HTTP_200_OK)
async def service_health(
    db: AsyncSession = Depends(get_db)
):
    """
    Health check endpoint for forecasting service

    **Permissions:** Public

    Returns service status and availability.

    **Usage:**
    ```bash
    curl -X GET https://api.simrs-hospital.com/v1/inventory/forecasting/health
    ```
    """
    return {
        "status": "healthy",
        "service": "demand_forecasting",
        "timestamp": datetime.utcnow().isoformat(),
        "algorithms_available": 3
    }
