"""Analytics Dashboard API Endpoints for EPIC-017

This module provides API endpoints for:
- KPI management and calculation
- Dashboard data retrieval
- Hospital KPIs and metrics
- Scheduled report management

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.analytics import get_analytics_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class KPICreateRequest(BaseModel):
    """Request to create KPI"""
    kpi_code: str = Field(..., description="KPI code")
    kpi_name: str = Field(..., description="KPI name")
    kpi_category: str = Field(..., description="KPI category")
    calculation_method: str = Field(..., description="Calculation method (sql, formula)")
    description: Optional[str] = Field(None, description="KPI description")
    sql_query: Optional[str] = Field(None, description="SQL query for calculation")
    formula: Optional[str] = Field(None, description="Calculation formula")
    data_source: Optional[str] = Field(None, description="Data source table")
    unit: Optional[str] = Field(None, description="Unit of measure")
    decimal_places: int = Field(2, description="Decimal places")
    format_type: str = Field("number", description="Format type (number, percentage, currency)")
    target_value: Optional[float] = Field(None, description="Target value")
    target_min: Optional[float] = Field(None, description="Minimum acceptable value")
    target_max: Optional[float] = Field(None, description="Maximum acceptable value")
    aggregation_type: str = Field("sum", description="Aggregation type")
    aggregation_period: str = Field("daily", description="Aggregation period")
    chart_type: Optional[str] = Field(None, description="Recommended chart type")


class DashboardRequest(BaseModel):
    """Request to create dashboard"""
    dashboard_code: str = Field(..., description="Dashboard code")
    dashboard_name: str = Field(..., description="Dashboard name")
    dashboard_type: str = Field(..., description="Dashboard type")
    description: Optional[str] = Field(None, description="Dashboard description")
    layout_config: dict = Field(..., description="Layout configuration")
    refresh_interval: int = Field(300, description="Refresh interval (seconds)")
    is_public: bool = Field(False, description="Whether dashboard is public")


# =============================================================================
# KPI Management Endpoints
# =============================================================================

@router.post("/kpis", status_code=status.HTTP_201_CREATED)
async def create_kpi(
    request: KPICreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new KPI (admin only)"""
    try:
        service = get_analytics_service(db)

        result = await service.create_kpi(
            kpi_code=request.kpi_code,
            kpi_name=request.kpi_name,
            kpi_category=request.kpi_category,
            calculation_method=request.calculation_method,
            description=request.description,
            sql_query=request.sql_query,
            formula=request.formula,
            data_source=request.data_source,
            unit=request.unit,
            decimal_places=request.decimal_places,
            format_type=request.format_type,
            target_value=request.target_value,
            target_min=request.target_min,
            target_max=request.target_max,
            aggregation_type=request.aggregation_type,
            aggregation_period=request.aggregation_period,
            chart_type=request.chart_type
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
        logger.error("Error creating KPI: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create KPI"
        )


@router.get("/kpis/values")
async def get_kpi_values(
    kpi_codes: str = Query(..., description="Comma-separated KPI codes"),
    period_start: Optional[str] = Query(None, description="Period start (YYYY-MM-DD)"),
    period_end: Optional[str] = Query(None, description="Period end (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get KPI values for specified codes and period"""
    try:
        service = get_analytics_service(db)

        # Parse KPI codes
        codes = [c.strip() for c in kpi_codes.split(",")]

        # Parse dates
        start = None
        end = None
        if period_start:
            start = datetime.combine(date.fromisoformat(period_start), datetime.min.time())
        if period_end:
            end = datetime.combine(date.fromisoformat(period_end), datetime.max.time())

        # Default to today if not specified
        if not start:
            start = datetime.combine(date.today(), datetime.min.time())
        if not end:
            end = datetime.combine(date.today(), datetime.max.time())

        result = await service.get_kpi_values(codes, start, end)

        return {
            "period_start": start.isoformat(),
            "period_end": end.isoformat(),
            "values": result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting KPI values: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get KPI values"
        )


# =============================================================================
# Dashboard Endpoints
# =============================================================================

@router.get("/dashboards/{dashboard_code}")
async def get_dashboard(
    dashboard_code: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard data by code"""
    try:
        service = get_analytics_service(db)

        result = await service.get_dashboard(dashboard_code, current_user.id)

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
        logger.error("Error getting dashboard: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard"
        )


@router.get("/dashboards")
async def list_dashboards(
    dashboard_type: Optional[str] = Query(None, description="Filter by dashboard type"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List available dashboards"""
    try:
        from app.models.analytics import Dashboard
        from sqlalchemy import select, and_

        # Build filters
        filters = [Dashboard.is_active == True]

        if dashboard_type:
            filters.append(Dashboard.dashboard_type == dashboard_type)
        if is_public is not None:
            filters.append(Dashboard.is_public == is_public)

        # Get dashboards
        query = select(Dashboard)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(Dashboard.display_order)

        result = await db.execute(query)
        dashboards = result.scalars().all()

        # Build response
        dashboard_list = [
            {
                "dashboard_code": d.dashboard_code,
                "dashboard_name": d.dashboard_name,
                "dashboard_type": d.dashboard_type,
                "description": d.description,
                "is_public": d.is_public,
                "refresh_interval": d.refresh_interval
            }
            for d in dashboards
        ]

        return {
            "dashboards": dashboard_list
        }

    except Exception as e:
        logger.error("Error listing dashboards: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list dashboards"
        )


# =============================================================================
# Hospital KPIs Endpoints
# =============================================================================

@router.get("/hospital/kpis")
async def get_hospital_kpis(
    period_start: Optional[str] = Query(None, description="Period start (YYYY-MM-DD)"),
    period_end: Optional[str] = Query(None, description="Period end (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get hospital KPIs for executive dashboard"""
    try:
        service = get_analytics_service(db)

        # Parse dates
        start = None
        end = None
        if period_start:
            start = datetime.combine(date.fromisoformat(period_start), datetime.min.time())
        if period_end:
            end = datetime.combine(date.fromisoformat(period_end), datetime.max.time())

        result = await service.get_hospital_kpis(start, end)

        return result

    except Exception as e:
        logger.error("Error getting hospital KPIs: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get hospital KPIs"
        )


# =============================================================================
# Executive Dashboard Endpoints
# =============================================================================

@router.get("/executive/overview")
async def get_executive_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get executive overview with key hospital metrics"""
    try:
        service = get_analytics_service(db)

        # Get today's KPIs
        today = date.today()
        period_start = datetime.combine(today, datetime.min.time())
        period_end = datetime.combine(today, datetime.max.time())

        kpi_data = await service.get_hospital_kpis(period_start, period_end)

        # Add additional executive summary data
        from app.models.patient import Patient
        from app.models.encounter import Encounter
        from sqlalchemy import select, func

        # Total patients
        patient_query = select(func.count(Patient.id))
        patient_result = await db.execute(patient_query)
        total_patients = patient_result.scalar() or 0

        # Active encounters
        encounter_query = select(func.count(Encounter.id)).where(
            Encounter.status == "active"
        )
        encounter_result = await db.execute(encounter_query)
        active_encounters = encounter_result.scalar() or 0

        return {
            "overview_date": today.isoformat(),
            "summary": {
                "total_patients": total_patients,
                "active_encounters": active_encounters
            },
            "kpis": kpi_data.get("kpis", {}),
            "generated_at": kpi_data.get("generated_at")
        }

    except Exception as e:
        logger.error("Error getting executive overview: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get executive overview"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_analytics_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics system statistics"""
    try:
        from app.models.analytics import KPI, Dashboard, DashboardWidget
        from sqlalchemy import select, func

        # Get KPI counts by category
        category_query = select(
            KPI.kpi_category,
            func.count(KPI.id).label("count")
        ).group_by(KPI.kpi_category)

        category_result = await db.execute(category_query)
        category_counts = {row[0]: row[1] for row in category_result.all()}

        # Get total counts
        kpi_query = select(func.count(KPI.id))
        kpi_result = await db.execute(kpi_query)
        total_kpis = kpi_result.scalar() or 0

        dashboard_query = select(func.count(Dashboard.id))
        dashboard_result = await db.execute(dashboard_query)
        total_dashboards = dashboard_result.scalar() or 0

        widget_query = select(func.count(DashboardWidget.id))
        widget_result = await db.execute(widget_query)
        total_widgets = widget_result.scalar() or 0

        return {
            "total_kpis": total_kpis,
            "total_dashboards": total_dashboards,
            "total_widgets": total_widgets,
            "category_counts": category_counts,
            "summary": {
                "financial": category_counts.get("financial", 0),
                "operational": category_counts.get("operational", 0),
                "clinical": category_counts.get("clinical", 0),
                "patient": category_counts.get("patient", 0),
                "quality": category_counts.get("quality", 0)
            }
        }

    except Exception as e:
        logger.error("Error getting analytics statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
