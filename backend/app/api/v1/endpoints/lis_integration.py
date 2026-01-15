"""LIS (Laboratory Information System) Integration API Endpoints for STORY-024-03

This module provides API endpoints for:
- LIS order management
- LIS result processing
- Order status tracking
- LIS configuration and mapping

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.lis_integration import get_lis_integration_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class LISOrderSendRequest(BaseModel):
    """Request to send order to LIS"""
    lis_order_id: int = Field(..., description="LIS order ID")


class LISOrderResponse(BaseModel):
    """Response for LIS order details"""
    order_id: str
    lis_order_number: Optional[str] = None
    status: str
    sent_at: Optional[str] = None
    completed_at: Optional[str] = None
    results_received: int
    critical_value: bool


class LISResultProcessRequest(BaseModel):
    """Request to process LIS result"""
    message: str = Field(..., description="Raw HL7 ORU^R01 message")


class TestMappingCreateRequest(BaseModel):
    """Request to create test mapping"""
    simrs_code: str = Field(..., description="SIMRS test code")
    simrs_name: str = Field(..., description="SIMRS test name")
    lis_code: str = Field(..., description="LIS test code")
    lis_name: str = Field(..., description="LIS test name")


# =============================================================================
# LIS Order Endpoints
# =============================================================================

@router.post("/orders/send", status_code=status.HTTP_202_ACCEPTED)
async def send_lis_order(
    request: LISOrderSendRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send lab order to LIS system"""
    try:
        service = get_lis_integration_service(db)

        result = await service.send_order_to_lis(
            lis_order_id=request.lis_order_id
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
        logger.error("Error sending LIS order: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send order to LIS"
        )


@router.get("/orders/{order_id}")
async def get_lis_order_status(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get LIS order status by order ID"""
    try:
        service = get_lis_integration_service(db)

        result = await service.get_order_status(order_id)

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
        logger.error("Error getting LIS order status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order status"
        )


@router.get("/orders")
async def list_lis_orders(
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List LIS orders with filtering"""
    try:
        service = get_lis_integration_service(db)

        result = await service.list_orders(
            patient_id=patient_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )

        return result

    except Exception as e:
        logger.error("Error listing LIS orders: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list orders"
        )


# =============================================================================
# LIS Result Processing Endpoints
# =============================================================================

@router.post("/results")
async def process_lis_result(
    request: LISResultProcessRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Process lab result received from LIS"""
    try:
        service = get_lis_integration_service(db)

        result = await service.process_lis_result(
            raw_message=request.message
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
        logger.error("Error processing LIS result: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process result"
        )


# =============================================================================
# LIS Configuration Endpoints (Admin)
# =============================================================================

@router.post("/mappings/tests", status_code=status.HTTP_201_CREATED)
async def create_test_mapping(
    request: TestMappingCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create test code mapping (admin only)"""
    try:
        service = get_lis_integration_service(db)

        result = await service.create_test_mapping(
            simrs_code=request.simrs_code,
            simrs_name=request.simrs_name,
            lis_code=request.lis_code,
            lis_name=request.lis_name
        )

        return result

    except Exception as e:
        logger.error("Error creating test mapping: {}".format(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test mapping"
        )


# =============================================================================
# LIS Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_lis_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get LIS integration statistics"""
    try:
        from app.models.lis_integration import LISOrder, LISOrderStatus
        from sqlalchemy import select, func

        # Get order counts by status
        status_query = select(
            LISOrder.status,
            func.count(LISOrder.id).label("count")
        ).group_by(LISOrder.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # Get total orders
        total_query = select(func.count(LISOrder.id))
        total_result = await db.execute(total_query)
        total_orders = total_result.scalar() or 0

        # Get total results
        results_query = select(func.count(LISResult.id))
        results_result = await db.execute(results_query)
        total_results = results_result.scalar() or 0

        # Get critical values count
        critical_query = select(func.count(LISResult.id)).where(
            LISResult.critical_flag == True
        )
        critical_result = await db.execute(critical_query)
        critical_count = critical_result.scalar() or 0

        return {
            "total_orders": total_orders,
            "total_results": total_results,
            "critical_values": critical_count,
            "status_counts": status_counts,
            "summary": {
                "pending": status_counts.get(LISOrderStatus.PENDING, 0),
                "sent": status_counts.get(LISOrderStatus.SENT, 0),
                "in_progress": status_counts.get(LISOrderStatus.IN_PROGRESS, 0),
                "completed": status_counts.get(LISOrderStatus.COMPLETED, 0),
                "error": status_counts.get(LISOrderStatus.ERROR, 0),
            }
        }

    except Exception as e:
        logger.error("Error getting LIS statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
