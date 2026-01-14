"""Lab Orders CRUD Operations

This module provides CRUD operations for laboratory test orders including:
- Order creation and management
- Order status tracking
- Queue management for lab department
- Result tracking integration
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, and_, or_, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

# Temporarily using dict for order_data until models are created
# TODO: Import from app.models.lab_orders when models are available
# from app.models.lab_orders import LabOrder


class LabOrderStatus:
    """Lab order status constants"""
    DRAFT = "draft"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class LabOrderPriority:
    """Lab order priority constants"""
    ROUTINE = "routine"
    URGENT = "urgent"
    STAT = "stat"  # Immediate/emergency


# =============================================================================
# Lab Order CRUD
# =============================================================================

async def get_lab_order(
    db: AsyncSession,
    order_id: int,
) -> Optional[Dict[str, Any]]:
    """Get lab order by ID with all relationships

    Args:
        db: Async database session
        order_id: Lab order ID

    Returns:
        Lab order dict or None if not found
    """
    # TODO: Replace with actual model query when LabOrder model exists
    # stmt = select(LabOrder).options(
    #     selectinload(LabOrder.patient),
    #     selectinload(LabOrder.encounter),
    #     selectinload(LabOrder.ordering_provider),
    #     selectinload(LabOrder.procedure_codes),
    # ).where(LabOrder.id == order_id)
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()

    # Placeholder until model exists
    return None


async def get_lab_orders(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    encounter_id: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """List lab orders with pagination and filtering

    Args:
        db: Async database session
        patient_id: Filter by patient ID (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status (optional)
        encounter_id: Filter by encounter ID (optional)

    Returns:
        Tuple of (lab orders list, total count)
    """
    # TODO: Replace with actual model query when LabOrder model exists
    # conditions = []
    #
    # if patient_id:
    #     conditions.append(LabOrder.patient_id == patient_id)
    # if status:
    #     conditions.append(LabOrder.status == status)
    # if encounter_id:
    #     conditions.append(LabOrder.encounter_id == encounter_id)
    #
    # # Get total count
    # count_stmt = select(sql_func.count(LabOrder.id))
    # if conditions:
    #     count_stmt = count_stmt.where(and_(*conditions))
    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()
    #
    # # Build query
    # stmt = select(LabOrder)
    # if conditions:
    #     stmt = stmt.where(and_(*conditions))
    #
    # stmt = stmt.order_by(LabOrder.created_at.desc())
    # stmt = stmt.offset(skip).limit(limit)
    #
    # result = await db.execute(stmt)
    # orders = result.scalars().all()
    #
    # return list(orders), total

    # Placeholder until model exists
    return [], 0


async def get_lab_orders_by_encounter(
    db: AsyncSession,
    encounter_id: int,
) -> List[Dict[str, Any]]:
    """Get all lab orders for a specific encounter

    Args:
        db: Async database session
        encounter_id: Encounter ID

    Returns:
        List of lab orders for the encounter
    """
    # TODO: Replace with actual model query when LabOrder model exists
    # stmt = select(LabOrder).where(
    #     LabOrder.encounter_id == encounter_id
    # ).order_by(LabOrder.created_at.desc())
    #
    # result = await db.execute(stmt)
    # orders = result.scalars().all()
    #
    # return list(orders)

    # Placeholder until model exists
    return []


async def create_lab_order(
    db: AsyncSession,
    order_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create new lab order with auto-generated order number

    Args:
        db: Async database session
        order_data: Dictionary containing order details:
            - patient_id: Required
            - encounter_id: Optional
            - ordering_provider_id: Required
            - department_id: Required (lab department)
            - priority: Default 'routine'
            - diagnosis: Optional clinical diagnosis
            - clinical_indication: Optional reason for order
            - procedure_codes: List of procedure/test codes to order
            - notes: Optional additional notes
            - specimen_type: Optional (blood, urine, etc)
            - fasting_required: Optional boolean
            - urgent: Optional boolean (deprecated, use priority)

    Returns:
        Created lab order

    Raises:
        HTTPException: If patient or provider not found, or validation fails
    """
    # TODO: Replace with actual model when LabOrder model exists
    # # Generate order number
    # order_number = await _generate_lab_order_number(db)
    #
    # # Create lab order
    # db_order = LabOrder(
    #     order_number=order_number,
    #     patient_id=order_data["patient_id"],
    #     encounter_id=order_data.get("encounter_id"),
    #     ordering_provider_id=order_data["ordering_provider_id"],
    #     department_id=order_data["department_id"],
    #     priority=order_data.get("priority", LabOrderPriority.ROUTINE),
    #     diagnosis=order_data.get("diagnosis"),
    #     clinical_indication=order_data.get("clinical_indication"),
    #     specimen_type=order_data.get("specimen_type"),
    #     fasting_required=order_data.get("fasting_required", False),
    #     notes=order_data.get("notes"),
    #     status=LabOrderStatus.PENDING,
    # )
    #
    # db.add(db_order)
    # await db.flush()  # Get ID before adding procedure codes
    #
    # # Add procedure codes
    # for code_data in order_data.get("procedure_codes", []):
    #     await _add_lab_procedure_code(db, db_order.id, code_data)
    #
    # await db.commit()
    # await db.refresh(db_order)
    #
    # return db_order

    # Placeholder until model exists
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Lab order model not yet implemented"
    )


async def update_lab_order(
    db: AsyncSession,
    order_id: int,
    update_data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Update lab order details

    Args:
        db: Async database session
        order_id: Lab order ID
        update_data: Dictionary containing fields to update:
            - diagnosis
            - clinical_indication
            - specimen_type
            - fasting_required
            - notes
            - priority
            - procedure_codes (replaces existing codes)

    Returns:
        Updated lab order or None if not found

    Raises:
        ValueError: If order is not in draft/pending status
    """
    # TODO: Replace with actual model when LabOrder model exists
    # order = await get_lab_order(db, order_id)
    # if not order:
    #     return None
    #
    # # Only allow updates to draft or pending orders
    # if order.status not in [LabOrderStatus.DRAFT, LabOrderStatus.PENDING]:
    #     raise ValueError("Can only update draft or pending orders")
    #
    # # Update fields
    # if "diagnosis" in update_data:
    #     order.diagnosis = update_data["diagnosis"]
    # if "clinical_indication" in update_data:
    #     order.clinical_indication = update_data["clinical_indication"]
    # if "specimen_type" in update_data:
    #     order.specimen_type = update_data["specimen_type"]
    # if "fasting_required" in update_data:
    #     order.fasting_required = update_data["fasting_required"]
    # if "notes" in update_data:
    #     order.notes = update_data["notes"]
    # if "priority" in update_data:
    #     order.priority = update_data["priority"]
    #
    # # Update procedure codes if provided
    # if "procedure_codes" in update_data:
    #     # Remove existing procedure codes
    #     # Add new procedure codes
    #     for code_data in update_data["procedure_codes"]:
    #         await _add_lab_procedure_code(db, order_id, code_data)
    #
    # order.updated_at = datetime.now(timezone.utc)
    # await db.commit()
    # await db.refresh(order)
    #
    # return order

    # Placeholder until model exists
    return None


async def update_lab_order_status(
    db: AsyncSession,
    order_id: int,
    status: str,
) -> Optional[Dict[str, Any]]:
    """Update lab order status only

    Args:
        db: Async database session
        order_id: Lab order ID
        status: New status (draft, pending, in_progress, completed, cancelled, on_hold)

    Returns:
        Updated lab order or None if not found

    Raises:
        ValueError: If status transition is invalid
    """
    # TODO: Replace with actual model when LabOrder model exists
    # order = await get_lab_order(db, order_id)
    # if not order:
    #     return None
    #
    # # Validate status transition
    # valid_transitions = {
    #     LabOrderStatus.DRAFT: [LabOrderStatus.PENDING, LabOrderStatus.CANCELLED],
    #     LabOrderStatus.PENDING: [LabOrderStatus.IN_PROGRESS, LabOrderStatus.CANCELLED, LabOrderStatus.ON_HOLD],
    #     LabOrderStatus.IN_PROGRESS: [LabOrderStatus.COMPLETED, LabOrderStatus.CANCELLED, LabOrderStatus.ON_HOLD],
    #     LabOrderStatus.ON_HOLD: [LabOrderStatus.PENDING, LabOrderStatus.CANCELLED],
    #     LabOrderStatus.COMPLETED: [],  # Terminal state
    #     LabOrderStatus.CANCELLED: [],  # Terminal state
    # }
    #
    # if status not in valid_transitions.get(order.status, []):
    #     raise ValueError(f"Cannot transition from {order.status} to {status}")
    #
    # order.status = status
    #
    # # Set timestamps based on status
    # if status == LabOrderStatus.IN_PROGRESS:
    #     order.started_at = datetime.now(timezone.utc)
    # elif status == LabOrderStatus.COMPLETED:
    #     order.completed_at = datetime.now(timezone.utc)
    # elif status == LabOrderStatus.CANCELLED:
    #     order.cancelled_at = datetime.now(timezone.utc)
    #
    # order.updated_at = datetime.now(timezone.utc)
    # await db.commit()
    # await db.refresh(order)
    #
    # return order

    # Placeholder until model exists
    return None


async def cancel_lab_order(
    db: AsyncSession,
    order_id: int,
    reason: str,
    cancelled_by_id: int,
) -> Optional[Dict[str, Any]]:
    """Cancel lab order with reason

    Args:
        db: Async database session
        order_id: Lab order ID
        reason: Reason for cancellation
        cancelled_by_id: User ID who cancelled the order

    Returns:
        Cancelled lab order or None if not found

    Raises:
        ValueError: If order is already completed or cancelled
    """
    # TODO: Replace with actual model when LabOrder model exists
    # order = await get_lab_order(db, order_id)
    # if not order:
    #     return None
    #
    # # Check if order can be cancelled
    # if order.status in [LabOrderStatus.COMPLETED, LabOrderStatus.CANCELLED]:
    #     raise ValueError(f"Cannot cancel order with status: {order.status}")
    #
    # order.status = LabOrderStatus.CANCELLED
    # order.cancellation_reason = reason
    # order.cancelled_by_id = cancelled_by_id
    # order.cancelled_at = datetime.now(timezone.utc)
    # order.updated_at = datetime.now(timezone.utc)
    #
    # await db.commit()
    # await db.refresh(order)
    #
    # return order

    # Placeholder until model exists
    return None


async def get_pending_orders(
    db: AsyncSession,
    department_id: int,
    priority: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Get pending lab orders for queue management

    Args:
        db: Async database session
        department_id: Department ID (lab department)
        priority: Optional filter by priority
        limit: Maximum number of orders to return

    Returns:
        List of pending lab orders ordered by priority and creation time
    """
    # TODO: Replace with actual model query when LabOrder model exists
    # conditions = [
    #     LabOrder.department_id == department_id,
    #     LabOrder.status == LabOrderStatus.PENDING,
    # ]
    #
    # if priority:
    #     conditions.append(LabOrder.priority == priority)
    #
    # # Order by priority (stat first, then urgent, then routine)
    # # Use CASE for custom ordering
    # priority_order = sql_func.case(
    #     (LabOrder.priority == LabOrderPriority.STAT, 1),
    #     (LabOrder.priority == LabOrderPriority.URGENT, 2),
    #     (LabOrder.priority == LabOrderPriority.ROUTINE, 3),
    #     else_=4
    # )
    #
    # stmt = (
    #     select(LabOrder)
    #     .where(and_(*conditions))
    #     .order_by(priority_order, LabOrder.created_at)
    #     .limit(limit)
    # )
    #
    # result = await db.execute(stmt)
    # orders = result.scalars().all()
    #
    # return list(orders)

    # Placeholder until model exists
    return []


# =============================================================================
# Helper Functions
# =============================================================================

async def _generate_lab_order_number(db: AsyncSession) -> str:
    """Generate a unique lab order number

    Format: LAB-YYYY-XXXXXX
    """
    # TODO: Implement when LabOrder model exists
    # year = datetime.now().strftime("%Y")
    #
    # # Get count of orders this year
    # stmt = select(sql_func.count(LabOrder.id)).where(
    #     sql_func.extract('year', LabOrder.created_at) == int(year)
    # )
    # result = await db.execute(stmt)
    # count = result.scalar_one() + 1
    #
    # # Format with leading zeros
    # number = f"LAB-{year}-{count:06d}"
    #
    # # Check for uniqueness
    # existing_stmt = select(LabOrder).where(LabOrder.order_number == number)
    # existing_result = await db.execute(existing_stmt)
    # if existing_result.scalar_one_or_none():
    #     # Collision - use timestamp
    #     import uuid
    #     return f"LAB-{year}-{uuid.uuid4().hex[:6].upper()}"
    #
    # return number

    # Placeholder until model exists
    year = datetime.now().strftime('%Y')
    return "LAB-{}-000001".format(year)


async def _add_lab_procedure_code(
    db: AsyncSession,
    order_id: int,
    code_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Add procedure code to lab order (internal function)

    Args:
        db: Async database session
        order_id: Lab order ID
        code_data: Procedure code data

    Returns:
        Created order procedure
    """
    # TODO: Implement when LabOrder model exists
    # from app.crud.procedure_codes import get_procedure_code
    #
    # # Verify procedure code exists
    # procedure = await get_procedure_code(db, code_data["procedure_code_id"])
    # if not procedure:
    #     raise ValueError(f"Procedure code {code_data['procedure_code_id']} not found")
    #
    # # Create order procedure
    # order_procedure = LabOrderProcedure(
    #     lab_order_id=order_id,
    #     procedure_code_id=code_data["procedure_code_id"],
    #     procedure_name=procedure["name"],
    #     procedure_code=procedure["code"],
    #     clinical_notes=code_data.get("clinical_notes"),
    # )
    #
    # db.add(order_procedure)
    # await db.flush()
    #
    # return order_procedure

    # Placeholder until model exists
    return {}
