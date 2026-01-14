"""Billing and Invoicing API endpoints

This module provides REST API endpoints for billing, invoicing, payments,
and financial reporting. All endpoints require authentication and appropriate permissions.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.db.session import get_db
from app.core.deps import get_current_user, require_permission, get_request_info
from app.models.user import User
from app.crud.audit_log import create_audit_log

router = APIRouter()


# =============================================================================
# INVOICE MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/invoices", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_invoice(
    invoice_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "create"))
):
    """
    Generate a new invoice for a patient.

    Args:
        invoice_data: Invoice creation data including patient_id, items, etc.
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:create permission

    Returns:
        Created invoice details

    Raises:
        HTTPException 400: If validation error
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement invoice generation logic
        # 1. Validate patient exists
        # 2. Calculate totals from items
        # 3. Apply billing rules
        # 4. Generate invoice number
        # 5. Create invoice record
        # 6. Create invoice items

        await create_audit_log(
            db=db,
            action="INVOICE_CREATED",
            resource_type="Invoice",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "id": 1,
            "invoice_number": "INV-2026-0001",
            "patient_id": invoice_data.get("patient_id"),
            "status": "draft",
            "subtotal": Decimal("0.00"),
            "tax": Decimal("0.00"),
            "discount": Decimal("0.00"),
            "total": Decimal("0.00"),
            "created_at": datetime.now(),
            "message": "Invoice generated successfully"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="INVOICE_CREATE_FAILED",
            resource_type="Invoice",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/invoices", response_model=dict, status_code=status.HTTP_200_OK)
async def list_invoices(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status (draft, pending, approved, rejected, paid, partial)"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    date_from: Optional[date] = Query(None, description="Filter by date from"),
    date_to: Optional[date] = Query(None, description="Filter by date to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "read"))
):
    """
    List invoices with pagination and filters.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Filter by invoice status
        patient_id: Filter by patient ID
        date_from: Filter by start date
        date_to: Filter by end date
        db: Database session
        current_user: Authenticated user with billing:read permission

    Returns:
        Paginated list of invoices
    """
    # TODO: Implement invoice listing with filters
    return {
        "items": [],
        "total": 0,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": 0
    }


@router.get("/invoices/{invoice_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "read"))
):
    """
    Get invoice by ID.

    Args:
        invoice_id: Invoice ID
        db: Database session
        current_user: Authenticated user with billing:read permission

    Returns:
        Invoice details with items

    Raises:
        HTTPException 404: If invoice not found
    """
    # TODO: Implement invoice retrieval
    return {
        "id": invoice_id,
        "invoice_number": "INV-2026-0001",
        "patient_id": 1,
        "patient_name": "John Doe",
        "status": "pending",
        "subtotal": Decimal("100.00"),
        "tax": Decimal("10.00"),
        "discount": Decimal("0.00"),
        "total": Decimal("110.00"),
        "paid_amount": Decimal("0.00"),
        "balance_due": Decimal("110.00"),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "items": []
    }


@router.put("/invoices/{invoice_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def update_invoice(
    invoice_id: int,
    invoice_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "update"))
):
    """
    Update invoice details.

    Args:
        invoice_id: Invoice ID
        invoice_data: Invoice update data
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:update permission

    Returns:
        Updated invoice details

    Raises:
        HTTPException 404: If invoice not found
        HTTPException 400: If validation error or invoice already approved
    """
    request_info = await get_request_info(request)

    # TODO: Implement invoice update
    # Only allow updates on draft/pending invoices

    await create_audit_log(
        db=db,
        action="INVOICE_UPDATED",
        resource_type="Invoice",
        resource_id=str(invoice_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": invoice_id,
        "message": "Invoice updated successfully"
    }


@router.delete("/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "delete"))
):
    """
    Delete an invoice (only draft or pending invoices).

    Args:
        invoice_id: Invoice ID
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:delete permission

    Raises:
        HTTPException 404: If invoice not found
        HTTPException 400: If invoice already approved/paid
    """
    request_info = await get_request_info(request)

    # TODO: Implement invoice deletion (soft delete)

    await create_audit_log(
        db=db,
        action="INVOICE_DELETED",
        resource_type="Invoice",
        resource_id=str(invoice_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


@router.get("/invoices/patient/{patient_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_patient_invoices(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "read"))
):
    """
    Get all invoices for a specific patient.

    Args:
        patient_id: Patient ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        status: Filter by status
        db: Database session
        current_user: Authenticated user with billing:read permission

    Returns:
        List of patient invoices
    """
    # TODO: Implement patient invoices retrieval
    return {
        "patient_id": patient_id,
        "items": [],
        "total": 0,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": 0
    }


@router.post("/invoices/{invoice_id}/approve", response_model=dict, status_code=status.HTTP_200_OK)
async def approve_invoice(
    invoice_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "approve"))
):
    """
    Approve an invoice for payment.

    Args:
        invoice_id: Invoice ID
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:approve permission

    Returns:
        Updated invoice status

    Raises:
        HTTPException 404: If invoice not found
        HTTPException 400: If invoice not in pending status
    """
    request_info = await get_request_info(request)

    # TODO: Implement invoice approval

    await create_audit_log(
        db=db,
        action="INVOICE_APPROVED",
        resource_type="Invoice",
        resource_id=str(invoice_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": invoice_id,
        "status": "approved",
        "message": "Invoice approved successfully"
    }


@router.post("/invoices/{invoice_id}/reject", response_model=dict, status_code=status.HTTP_200_OK)
async def reject_invoice(
    invoice_id: int,
    rejection_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "approve"))
):
    """
    Reject an invoice.

    Args:
        invoice_id: Invoice ID
        rejection_data: Rejection reason
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:approve permission

    Returns:
        Updated invoice status

    Raises:
        HTTPException 404: If invoice not found
    """
    request_info = await get_request_info(request)

    # TODO: Implement invoice rejection

    await create_audit_log(
        db=db,
        action="INVOICE_REJECTED",
        resource_type="Invoice",
        resource_id=str(invoice_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": invoice_id,
        "status": "rejected",
        "rejection_reason": rejection_data.get("reason", "No reason provided"),
        "message": "Invoice rejected successfully"
    }


# =============================================================================
# INVOICE ITEMS ENDPOINTS
# =============================================================================

@router.post("/invoices/{invoice_id}/items", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_invoice_item(
    invoice_id: int,
    item_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "create"))
):
    """
    Add an item to an invoice.

    Args:
        invoice_id: Invoice ID
        item_data: Item details (description, quantity, unit_price, etc.)
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:create permission

    Returns:
        Created invoice item

    Raises:
        HTTPException 404: If invoice not found
        HTTPException 400: If invoice already approved
    """
    request_info = await get_request_info(request)

    # TODO: Implement invoice item creation

    await create_audit_log(
        db=db,
        action="INVOICE_ITEM_ADDED",
        resource_type="InvoiceItem",
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": 1,
        "invoice_id": invoice_id,
        "description": item_data.get("description"),
        "quantity": item_data.get("quantity", 1),
        "unit_price": item_data.get("unit_price"),
        "total": Decimal("0.00"),
        "message": "Item added successfully"
    }


@router.put("/invoices/items/{item_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def update_invoice_item(
    item_id: int,
    item_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "update"))
):
    """
    Update an invoice item.

    Args:
        item_id: Invoice item ID
        item_data: Updated item data
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:update permission

    Returns:
        Updated invoice item

    Raises:
        HTTPException 404: If item not found
        HTTPException 400: If invoice already approved
    """
    request_info = await get_request_info(request)

    # TODO: Implement invoice item update

    await create_audit_log(
        db=db,
        action="INVOICE_ITEM_UPDATED",
        resource_type="InvoiceItem",
        resource_id=str(item_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": item_id,
        "message": "Item updated successfully"
    }


@router.delete("/invoices/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_invoice_item(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "delete"))
):
    """
    Remove an item from an invoice.

    Args:
        item_id: Invoice item ID
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:delete permission

    Raises:
        HTTPException 404: If item not found
        HTTPException 400: If invoice already approved
    """
    request_info = await get_request_info(request)

    # TODO: Implement invoice item deletion

    await create_audit_log(
        db=db,
        action="INVOICE_ITEM_REMOVED",
        resource_type="InvoiceItem",
        resource_id=str(item_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


# =============================================================================
# PAYMENTS ENDPOINTS
# =============================================================================

@router.post("/payments", response_model=dict, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payment_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "create"))
):
    """
    Process a payment for an invoice.

    Args:
        payment_data: Payment details (invoice_id, amount, payment_method, etc.)
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing:create permission

    Returns:
        Payment confirmation

    Raises:
        HTTPException 404: If invoice not found
        HTTPException 400: If payment amount exceeds balance
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement payment processing
        # 1. Validate invoice exists and is approved
        # 2. Validate payment amount
        # 3. Process payment based on method (cash, card, insurance, BPJS)
        # 4. Update invoice status if fully paid
        # 5. Generate receipt

        await create_audit_log(
            db=db,
            action="PAYMENT_PROCESSED",
            resource_type="Payment",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "id": 1,
            "invoice_id": payment_data.get("invoice_id"),
            "amount": payment_data.get("amount"),
            "payment_method": payment_data.get("payment_method"),
            "payment_date": datetime.now(),
            "receipt_number": "RCPT-2026-0001",
            "status": "completed",
            "message": "Payment processed successfully"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="PAYMENT_FAILED",
            resource_type="Payment",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/payments/invoice/{invoice_id}", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_invoice_payments(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "read"))
):
    """
    Get all payments for a specific invoice.

    Args:
        invoice_id: Invoice ID
        db: Database session
        current_user: Authenticated user with billing:read permission

    Returns:
        List of payments for the invoice
    """
    # TODO: Implement invoice payments retrieval
    return [
        {
            "id": 1,
            "invoice_id": invoice_id,
            "amount": Decimal("100.00"),
            "payment_method": "cash",
            "payment_date": datetime.now(),
            "receipt_number": "RCPT-2026-0001",
            "status": "completed"
        }
    ]


# =============================================================================
# REPORTING ENDPOINTS
# =============================================================================

@router.get("/reports/revenue", response_model=dict, status_code=status.HTTP_200_OK)
async def get_revenue_report(
    date_from: date = Query(..., description="Start date"),
    date_to: date = Query(..., description="End date"),
    group_by: Optional[str] = Query("day", description="Group by: day, week, month"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "read"))
):
    """
    Generate revenue report for a date range.

    Args:
        date_from: Start date
        date_to: End date
        group_by: Grouping period (day, week, month)
        db: Database session
        current_user: Authenticated user with billing:read permission

    Returns:
        Revenue report with breakdown by period
    """
    # TODO: Implement revenue report generation
    return {
        "date_from": date_from,
        "date_to": date_to,
        "group_by": group_by,
        "total_revenue": Decimal("0.00"),
        "total_payments": 0,
        "average_payment": Decimal("0.00"),
        "breakdown": []
    }


@router.get("/reports/aging", response_model=dict, status_code=status.HTTP_200_OK)
async def get_aging_report(
    as_of_date: Optional[date] = Query(None, description="As of date (default: today)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "read"))
):
    """
    Generate accounts receivable aging report.

    Args:
        as_of_date: Report date (default: today)
        db: Database session
        current_user: Authenticated user with billing:read permission

    Returns:
        Aging report with buckets (0-30, 31-60, 61-90, 90+ days)
    """
    # TODO: Implement aging report generation
    report_date = as_of_date or date.today()

    return {
        "as_of_date": report_date,
        "total_outstanding": Decimal("0.00"),
        "aging_buckets": {
            "current": {"amount": Decimal("0.00"), "count": 0, "days": "0-30"},
            "overdue_31_60": {"amount": Decimal("0.00"), "count": 0, "days": "31-60"},
            "overdue_61_90": {"amount": Decimal("0.00"), "count": 0, "days": "61-90"},
            "overdue_90_plus": {"amount": Decimal("0.00"), "count": 0, "days": "90+"}
        }
    }


@router.get("/reports/payer-summary", response_model=dict, status_code=status.HTTP_200_OK)
async def get_payer_summary_report(
    date_from: date = Query(..., description="Start date"),
    date_to: date = Query(..., description="End date"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing", "read"))
):
    """
    Generate payer summary report (BPJS, Insurance, Cash, etc.).

    Args:
        date_from: Start date
        date_to: End date
        db: Database session
        current_user: Authenticated user with billing:read permission

    Returns:
        Payer summary with breakdown by payment type
    """
    # TODO: Implement payer summary report generation
    return {
        "date_from": date_from,
        "date_to": date_to,
        "total_amount": Decimal("0.00"),
        "payers": [
            {
                "payer_type": "cash",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            {
                "payer_type": "bpjs",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            {
                "payer_type": "insurance",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            }
        ]
    }


# =============================================================================
# BILLING RULES ENDPOINTS (ADMIN)
# =============================================================================

@router.get("/rules", response_model=List[dict], status_code=status.HTTP_200_OK)
async def list_billing_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: bool = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing_admin", "read"))
):
    """
    List billing rules with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        db: Database session
        current_user: Authenticated user with billing_admin:read permission

    Returns:
        List of billing rules
    """
    # TODO: Implement billing rules listing
    return []


@router.post("/rules", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_billing_rule(
    rule_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing_admin", "create"))
):
    """
    Create a new billing rule.

    Args:
        rule_data: Billing rule details (name, type, conditions, actions, etc.)
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing_admin:create permission

    Returns:
        Created billing rule

    Raises:
        HTTPException 400: If validation error
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement billing rule creation

        await create_audit_log(
            db=db,
            action="BILLING_RULE_CREATED",
            resource_type="BillingRule",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "id": 1,
            "name": rule_data.get("name"),
            "rule_type": rule_data.get("rule_type"),
            "is_active": True,
            "created_at": datetime.now(),
            "message": "Billing rule created successfully"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="BILLING_RULE_CREATE_FAILED",
            resource_type="BillingRule",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=False,
            failure_reason=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/rules/{rule_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def update_billing_rule(
    rule_id: int,
    rule_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing_admin", "update"))
):
    """
    Update a billing rule.

    Args:
        rule_id: Billing rule ID
        rule_data: Updated rule data
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing_admin:update permission

    Returns:
        Updated billing rule

    Raises:
        HTTPException 404: If rule not found
    """
    request_info = await get_request_info(request)

    # TODO: Implement billing rule update

    await create_audit_log(
        db=db,
        action="BILLING_RULE_UPDATED",
        resource_type="BillingRule",
        resource_id=str(rule_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": rule_id,
        "message": "Billing rule updated successfully"
    }


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_billing_rule(
    rule_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("billing_admin", "delete"))
):
    """
    Delete a billing rule.

    Args:
        rule_id: Billing rule ID
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with billing_admin:delete permission

    Raises:
        HTTPException 404: If rule not found
    """
    request_info = await get_request_info(request)

    # TODO: Implement billing rule deletion (soft delete)

    await create_audit_log(
        db=db,
        action="BILLING_RULE_DELETED",
        resource_type="BillingRule",
        resource_id=str(rule_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )
