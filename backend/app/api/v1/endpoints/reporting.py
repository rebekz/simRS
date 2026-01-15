"""Reporting & Analytics API Endpoints for EPIC-013

This module provides API endpoints for:
- Report management (create, list, get, update, delete)
- Report execution
- Metric retrieval
- Dashboard data

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.reporting import get_reporting_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class ReportCreateRequest(BaseModel):
    """Request to create a report"""
    name: str = Field(..., min_length=1, max_length=255, description="Report name")
    code: str = Field(..., min_length=1, max_length=100, description="Unique report code")
    description: Optional[str] = Field(None, description="Report description")
    report_type: str = Field(..., description="Type of report")
    category: Optional[str] = Field(None, description="Report category")
    config: Optional[dict] = Field(None, description="Report configuration")
    output_formats: Optional[List[str]] = Field(None, description="Supported output formats")
    default_output_format: str = Field("pdf", description="Default output format")
    required_role: Optional[str] = Field(None, description="Required role to access")


class ReportUpdateRequest(BaseModel):
    """Request to update a report"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    config: Optional[dict] = None
    output_formats: Optional[List[str]] = None
    default_output_format: Optional[str] = None
    required_role: Optional[str] = None
    is_active: Optional[bool] = None


class ReportResponse(BaseModel):
    """Response for report details"""
    report_id: int
    name: str
    code: str
    description: Optional[str] = None
    report_type: str
    category: Optional[str] = None
    is_active: bool
    is_system: bool
    is_scheduled: bool
    output_formats: Optional[List[str]] = None
    default_output_format: str
    required_role: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ReportListResponse(BaseModel):
    """Response for report list"""
    reports: List[ReportResponse]
    total_count: int
    page: int
    per_page: int
    total_pages: int


class ReportExecutionRequest(BaseModel):
    """Request to execute a report"""
    parameters: Optional[dict] = Field(None, description="Report parameters")
    output_format: str = Field("json", description="Output format")


class ReportExecutionResponse(BaseModel):
    """Response for report execution"""
    execution_id: int
    report_id: int
    report_name: str
    status: str
    duration_seconds: Optional[int] = None
    row_count: Optional[int] = None
    data: Optional[dict] = None
    executed_at: Optional[str] = None


class MetricsResponse(BaseModel):
    """Response for metrics"""
    metric_date: str
    total_inpatients: int
    outpatient_visits: int
    emergency_visits: int
    total_patients: int
    bed_occupancy_rate: Optional[float] = None
    average_wait_time_minutes: Optional[float] = None


class DashboardResponse(BaseModel):
    """Response for dashboard data"""
    daily_census: dict
    bed_occupancy: dict
    patient_wait_times: dict
    revenue_summary: dict
    clinical_quality: dict


# =============================================================================
# Report Management Endpoints
# =============================================================================

@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    request: ReportCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new report (admin only)"""
    try:
        service = get_reporting_service(db)

        result = await service.create_report(
            name=request.name,
            code=request.code,
            report_type=request.report_type,
            description=request.description,
            config=request.config,
            output_formats=request.output_formats,
            default_output_format=request.default_output_format,
            required_role=request.required_role,
            created_by=current_user.id
        )

        # Get full report details
        report_details = await service.get_report(result["report_id"])

        return ReportResponse(**report_details)

    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating report: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report"
        )


@router.get("/reports", response_model=ReportListResponse)
async def list_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List reports with filtering"""
    try:
        service = get_reporting_service(db)

        result = await service.list_reports(
            report_type=report_type,
            category=category,
            is_active=is_active,
            page=page,
            per_page=per_page
        )

        return ReportListResponse(
            reports=[ReportResponse(**r) for r in result["reports"]],
            total_count=result["total_count"],
            page=page,
            per_page=per_page,
            total_pages=result["total_pages"]
        )

    except Exception as e:
        logger.error("Error listing reports: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list reports"
        )


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get report by ID"""
    try:
        service = get_reporting_service(db)

        result = await service.get_report(report_id)

        return ReportResponse(**result)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting report: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get report"
        )


@router.post("/reports/{report_id}/execute", response_model=ReportExecutionResponse)
async def execute_report(
    report_id: int,
    request: ReportExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a report"""
    try:
        service = get_reporting_service(db)

        result = await service.execute_report(
            report_id=report_id,
            parameters=request.parameters,
            output_format=request.output_format,
            triggered_by=current_user.id
        )

        return ReportExecutionResponse(**result)

    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error executing report: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute report"
        )


# =============================================================================
# Pre-defined Report Endpoints
# =============================================================================

@router.get("/reports/daily-census")
async def get_daily_census(
    report_date: Optional[str] = Query(None, description="Report date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get daily census report"""
    try:
        service = get_reporting_service(db)

        # Use today if no date provided
        if not report_date:
            report_date = datetime.utcnow().date().isoformat()

        data = await service._generate_daily_census({"report_date": report_date})

        return data

    except Exception as e:
        logger.error("Error generating daily census: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate daily census report"
        )


@router.get("/reports/bed-occupancy")
async def get_bed_occupancy(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bed occupancy report"""
    try:
        service = get_reporting_service(db)

        data = await service._generate_bed_occupancy({})

        return data

    except Exception as e:
        logger.error("Error generating bed occupancy: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate bed occupancy report"
        )


@router.get("/reports/patient-wait-times")
async def get_patient_wait_times(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get patient wait times report"""
    try:
        service = get_reporting_service(db)

        data = await service._generate_patient_wait_times({})

        return data

    except Exception as e:
        logger.error("Error generating patient wait times: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate patient wait times report"
        )


@router.get("/reports/revenue-summary")
async def get_revenue_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue summary report"""
    try:
        service = get_reporting_service(db)

        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = datetime.utcnow()
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")

        data = await service._generate_revenue_summary({
            "start_date": start_date,
            "end_date": end_date
        })

        return data

    except Exception as e:
        logger.error("Error generating revenue summary: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate revenue summary report"
        )


@router.get("/reports/bpjs-analytics")
async def get_bpjs_claim_analytics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get BPJS claim analytics report"""
    try:
        service = get_reporting_service(db)

        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = datetime.utcnow()
            start_date = today.replace(day=1).strftime("%Y-%m-%d")
            end_date = today.strftime("%Y-%m-%d")

        data = await service._generate_bpjs_claim_analytics({
            "start_date": start_date,
            "end_date": end_date
        })

        return data

    except Exception as e:
        logger.error("Error generating BPJS claim analytics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate BPJS claim analytics report"
        )


@router.get("/reports/clinical-quality")
async def get_clinical_quality_summary(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get clinical quality summary report"""
    try:
        service = get_reporting_service(db)

        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end = datetime.utcnow()
            start = end - timedelta(days=30)
            start_date = start.strftime("%Y-%m-%d")
            end_date = end.strftime("%Y-%m-%d")

        data = await service._generate_clinical_quality_summary({
            "start_date": start_date,
            "end_date": end_date
        })

        return data

    except Exception as e:
        logger.error("Error generating clinical quality summary: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate clinical quality summary report"
        )


# =============================================================================
# Dashboard Endpoints
# =============================================================================

@router.get("/dashboard")
async def get_dashboard_data(
    report_date: Optional[str] = Query(None, description="Report date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get executive dashboard data"""
    try:
        service = get_reporting_service(db)

        # Use today if no date provided
        if not report_date:
            report_date = datetime.utcnow().date().isoformat()

        # Get today's date for revenue and clinical quality
        today = datetime.utcnow()
        month_start = today.replace(day=1).strftime("%Y-%m-%d")
        today_str = today.strftime("%Y-%m-%d")

        # Gather all dashboard data
        daily_census = await service._generate_daily_census({"report_date": report_date})
        bed_occupancy = await service._generate_bed_occupancy({})
        wait_times = await service._generate_patient_wait_times({})
        revenue_summary = await service._generate_revenue_summary({
            "start_date": month_start,
            "end_date": today_str
        })
        clinical_quality = await service._generate_clinical_quality_summary({
            "start_date": month_start,
            "end_date": today_str
        })

        return DashboardResponse(
            daily_census=daily_census,
            bed_occupancy=bed_occupancy,
            patient_wait_times=wait_times,
            revenue_summary=revenue_summary,
            clinical_quality=clinical_quality
        )

    except Exception as e:
        logger.error("Error generating dashboard data: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate dashboard data"
        )


# =============================================================================
# Metric Aggregation Endpoints (Admin)
# =============================================================================

@router.post("/metrics/aggregate-daily")
async def aggregate_daily_metrics(
    metric_date: Optional[str] = Query(None, description="Metric date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Aggregate and store daily metrics (admin only)"""
    try:
        service = get_reporting_service(db)

        # Use yesterday if no date provided
        if not metric_date:
            metric_date_obj = datetime.utcnow() - timedelta(days=1)
        else:
            metric_date_obj = datetime.strptime(metric_date, "%Y-%m-%d")

        result = await service.aggregate_daily_metrics(metric_date_obj)

        return result

    except Exception as e:
        logger.error("Error aggregating daily metrics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to aggregate daily metrics"
        )
