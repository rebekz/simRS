"""Lab Order API endpoints for Lab/Radiology Ordering

This module provides API endpoints for:
- Lab order creation and management
- Lab test ordering with procedure codes
- Order status tracking and updates
- Pending queue management for lab departments
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_current_active_user, get_db
from app.models.user import User, UserRole
from app.schemas.lab_orders import (
    LabOrderCreate,
    LabOrderResponse,
    LabOrderUpdate,
    LabOrderStatusUpdate,
    LabOrderListResponse,
    LabOrderItemResponse,
    LabOrderStatus,
)


router = APIRouter()


# =============================================================================
# Lab Order Management Endpoints
# =============================================================================

@router.post("/lab/orders", response_model=LabOrderResponse)
async def create_lab_order(
    order_data: LabOrderCreate,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LabOrderResponse:
    """Create a new lab order.

    Args:
        order_data: Lab order details including tests, patient, encounter info
        background_tasks: FastAPI background tasks for async operations
        db: Database session
        current_user: Authenticated user (doctor/nurse)

    Returns:
        LabOrderResponse: Created lab order with details

    Raises:
        HTTPException 400: Invalid data or business rule violation
        HTTPException 403: Insufficient permissions
        HTTPException 404: Patient or encounter not found
    """
    try:
        from app.crud import lab_orders as crud_lab

        # Create lab order
        order = await crud_lab.create_lab_order(
            db=db,
            patient_id=order_data.patient_id,
            encounter_id=order_data.encounter_id,
            ordering_physician_id=current_user.id,
            department_id=order_data.department_id,
            priority=order_data.priority,
            diagnosis=order_data.diagnosis,
            clinical_indication=order_data.clinical_indication,
            test_items=order_data.test_items,
            notes=order_data.notes,
            fasting_required=order_data.fasting_required,
            special_instructions=order_data.special_instructions,
        )

        # Trigger background tasks if needed (e.g., notification to lab)
        if background_tasks and order:
            from app.services.lab_notification import notify_lab_department
            background_tasks.add_task(
                notify_lab_department,
                db,
                order.id,
                order.department_id,
            )

        return await _build_lab_order_response(db, order)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/lab/orders/{order_id}", response_model=LabOrderResponse)
async def get_lab_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LabOrderResponse:
    """Get a single lab order by ID.

    Args:
        order_id: Lab order ID
        db: Database session
        current_user: Authenticated user

    Returns:
        LabOrderResponse: Lab order details

    Raises:
        HTTPException 404: Order not found
    """
    from app.crud import lab_orders as crud_lab

    order = await crud_lab.get_lab_order(db=db, order_id=order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Lab order not found")

    return await _build_lab_order_response(db, order)


@router.get("/lab/orders/patient/{patient_id}", response_model=LabOrderListResponse)
async def get_patient_lab_orders(
    patient_id: int,
    status: Optional[LabOrderStatus] = Query(None, description="Filter by status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LabOrderListResponse:
    """Get all lab orders for a specific patient.

    Args:
        patient_id: Patient ID
        status: Optional status filter
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session
        current_user: Authenticated user

    Returns:
        LabOrderListResponse: Paginated list of lab orders
    """
    from app.crud import lab_orders as crud_lab

    orders, total = await crud_lab.get_patient_lab_orders(
        db=db,
        patient_id=patient_id,
        status=status,
        limit=limit,
        offset=offset,
    )

    response_data = []
    for order in orders:
        response_data.append(await _build_lab_order_response(db, order))

    return LabOrderListResponse(
        orders=response_data,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/lab/orders/encounter/{encounter_id}", response_model=LabOrderListResponse)
async def get_encounter_lab_orders(
    encounter_id: int,
    status: Optional[LabOrderStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LabOrderListResponse:
    """Get all lab orders for a specific encounter.

    Args:
        encounter_id: Encounter ID
        status: Optional status filter
        db: Database session
        current_user: Authenticated user

    Returns:
        LabOrderListResponse: List of lab orders for the encounter
    """
    from app.crud import lab_orders as crud_lab

    orders = await crud_lab.get_encounter_lab_orders(
        db=db,
        encounter_id=encounter_id,
        status=status,
    )

    response_data = []
    for order in orders:
        response_data.append(await _build_lab_order_response(db, order))

    return LabOrderListResponse(
        orders=response_data,
        total=len(orders),
        limit=100,
        offset=0,
    )


@router.put("/lab/orders/{order_id}", response_model=LabOrderResponse)
async def update_lab_order(
    order_id: int,
    order_update: LabOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LabOrderResponse:
    """Update a lab order.

    Only draft orders or orders pending approval can be modified.
    Completed orders cannot be modified.

    Args:
        order_id: Lab order ID
        order_update: Updated order data
        db: Database session
        current_user: Authenticated user

    Returns:
        LabOrderResponse: Updated lab order

    Raises:
        HTTPException 400: Cannot modify completed order
        HTTPException 403: Insufficient permissions
        HTTPException 404: Order not found
    """
    from app.crud import lab_orders as crud_lab

    try:
        order = await crud_lab.update_lab_order(
            db=db,
            order_id=order_id,
            order_update=order_update,
            updated_by_id=current_user.id,
        )

        if not order:
            raise HTTPException(status_code=404, detail="Lab order not found")

        return await _build_lab_order_response(db, order)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/lab/orders/{order_id}/status", response_model=LabOrderResponse)
async def update_lab_order_status(
    order_id: int,
    status_update: LabOrderStatusUpdate,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LabOrderResponse:
    """Update lab order status.

    Status transitions:
    - draft -> pending_approval
    - pending_approval -> approved | rejected
    - approved -> in_progress | cancelled
    - in_progress -> completed | cancelled

    Args:
        order_id: Lab order ID
        status_update: New status and optional notes
        background_tasks: FastAPI background tasks for notifications
        db: Database session
        current_user: Authenticated user

    Returns:
        LabOrderResponse: Updated lab order

    Raises:
        HTTPException 400: Invalid status transition
        HTTPException 403: Insufficient permissions
        HTTPException 404: Order not found
    """
    from app.crud import lab_orders as crud_lab

    try:
        order = await crud_lab.update_order_status(
            db=db,
            order_id=order_id,
            new_status=status_update.status,
            updated_by_id=current_user.id,
            notes=status_update.notes,
            rejection_reason=status_update.rejection_reason,
        )

        if not order:
            raise HTTPException(status_code=404, detail="Lab order not found")

        # Trigger notifications for status changes
        if background_tasks:
            from app.services.lab_notification import notify_order_status_change
            background_tasks.add_task(
                notify_order_status_change,
                db,
                order.id,
                status_update.status,
            )

        return await _build_lab_order_response(db, order)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/lab/orders/{order_id}", response_model=dict)
async def cancel_lab_order(
    order_id: int,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Cancel a lab order.

    Only draft, pending_approval, or approved orders can be cancelled.
    In-progress or completed orders cannot be cancelled.

    Args:
        order_id: Lab order ID
        reason: Optional cancellation reason
        db: Database session
        current_user: Authenticated user

    Returns:
        dict: Cancellation confirmation

    Raises:
        HTTPException 400: Cannot cancel order
        HTTPException 403: Insufficient permissions
        HTTPException 404: Order not found
    """
    from app.crud import lab_orders as crud_lab

    try:
        success = await crud_lab.cancel_lab_order(
            db=db,
            order_id=order_id,
            cancelled_by_id=current_user.id,
            cancellation_reason=reason,
        )

        if not success:
            raise HTTPException(status_code=404, detail="Lab order not found")

        return {
            "message": "Lab order cancelled successfully",
            "order_id": order_id,
            "cancelled": True,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/lab/orders/pending/{department_id}", response_model=LabOrderListResponse)
async def get_pending_lab_orders(
    department_id: int,
    priority: Optional[str] = Query(None, description="Filter by priority: routine, urgent, stat"),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LabOrderListResponse:
    """Get pending lab orders for a department (lab queue view).

    Used by lab staff to view and process incoming orders.
    Orders are sorted by priority (stat > urgent > routine) and creation time.

    Args:
        department_id: Department ID (lab department)
        priority: Optional priority filter
        limit: Maximum number of results
        db: Database session
        current_user: Authenticated user (lab staff)

    Returns:
        LabOrderListResponse: Paginated list of pending orders

    Raises:
        HTTPException 403: Not authorized to view lab queue
    """
    # Verify user has access to this department
    if current_user.role not in [UserRole.LAB_STAFF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Only lab staff can view pending lab orders",
        )

    from app.crud import lab_orders as crud_lab

    orders = await crud_lab.get_pending_lab_orders(
        db=db,
        department_id=department_id,
        priority=priority,
        limit=limit,
    )

    response_data = []
    for order in orders:
        response_data.append(await _build_lab_order_response(db, order))

    return LabOrderListResponse(
        orders=response_data,
        total=len(orders),
        limit=limit,
        offset=0,
    )


# =============================================================================
# Helper Functions
# =============================================================================

async def _build_lab_order_response(
    db: AsyncSession,
    order,
) -> LabOrderResponse:
    """Build full lab order response with all details.

    Args:
        db: Database session
        order: Lab order model instance

    Returns:
        LabOrderResponse: Complete order response
    """
    # Get patient details
    patient_name = order.patient.name if order.patient else None
    patient_bpjs_number = order.patient.bpjs_number if order.patient else None

    # Get encounter details
    encounter_type = order.encounter.encounter_type if order.encounter else None

    # Get ordering physician details
    physician_name = order.ordering_physician.full_name if order.ordering_physician else None
    physician_license = getattr(order.ordering_physician, 'license_number', None) if order.ordering_physician else None

    # Build test items
    test_items = []
    for item in order.test_items:
        test_items.append(LabOrderItemResponse(
            id=item.id,
            procedure_code_id=item.procedure_code_id,
            procedure_code=item.procedure_code.code if item.procedure_code else None,
            procedure_name=item.procedure_code.name if item.procedure_code else None,
            specimen_type=item.specimen_type,
            specimen_collection_instructions=item.specimen_collection_instructions,
            status=item.status,
        ))

    # Get approver details
    approved_by_name = order.approved_by.full_name if order.approved_by else None
    approved_date = order.approved_date

    # Get processor details
    processed_by_name = order.processed_by.full_name if order.processed_by else None
    processed_date = order.processed_date

    return LabOrderResponse(
        id=order.id,
        order_number=order.order_number,
        patient_id=order.patient_id,
        patient_name=patient_name,
        patient_bpjs_number=patient_bpjs_number,
        encounter_id=order.encounter_id,
        encounter_type=encounter_type,
        ordering_physician_id=order.ordering_physician_id,
        ordering_physician_name=physician_name,
        ordering_physician_license=physician_license,
        department_id=order.department_id,
        status=order.status,
        priority=order.priority,
        diagnosis=order.diagnosis,
        clinical_indication=order.clinical_indication,
        test_items=test_items,
        notes=order.notes,
        fasting_required=order.fasting_required,
        special_instructions=order.special_instructions,
        specimen_collection_status=order.specimen_collection_status,
        specimen_collected_at=order.specimen_collected_at,
        specimen_collected_by_id=order.specimen_collected_by_id,
        approved_by_id=order.approved_by_id,
        approved_by_name=approved_by_name,
        approved_date=approved_date,
        processed_by_id=order.processed_by_id,
        processed_by_name=processed_by_name,
        processed_date=processed_date,
        results_available=order.results_available,
        results_url=order.results_url,
        cancellation_reason=order.cancellation_reason,
        cancelled_by_id=order.cancelled_by_id,
        cancelled_at=order.cancelled_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )
