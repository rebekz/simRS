"""Payment Processing API endpoints

This module provides REST API endpoints for payment processing, refunds,
allocations, deposits, receipts, and financial reporting. All endpoints require
authentication and appropriate permissions.
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
# PAYMENT PROCESSING ENDPOINTS
# =============================================================================

@router.post("/process", response_model=dict, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payment_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "create"))
):
    """
    Process a payment for a patient or invoice.

    Args:
        payment_data: Payment details including amount, payment_method, patient_id, etc.
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:create permission

    Returns:
        Payment transaction details with receipt number

    Raises:
        HTTPException 400: If validation error or payment fails
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement payment processing logic
        # 1. Validate patient and invoice (if provided)
        # 2. Validate payment amount
        # 3. Process payment based on method (cash, card, insurance, BPJS, e-wallet)
        # 4. Create payment transaction record
        # 5. Generate receipt
        # 6. Update invoice payment status if applicable
        # 7. Trigger receipt generation in background

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
            "transaction_number": "TXN-2026-0001",
            "patient_id": payment_data.get("patient_id"),
            "invoice_id": payment_data.get("invoice_id"),
            "amount": payment_data.get("amount"),
            "payment_method": payment_data.get("payment_method"),
            "status": "completed",
            "receipt_number": "RCPT-2026-0001",
            "transaction_date": datetime.now(),
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


@router.get("/transactions", response_model=dict, status_code=status.HTTP_200_OK)
async def list_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status (pending, completed, failed, refunded)"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    date_from: Optional[date] = Query(None, description="Filter by date from"),
    date_to: Optional[date] = Query(None, description="Filter by date to"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    List payment transactions with pagination and filters.

    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        status: Filter by transaction status
        payment_method: Filter by payment method
        patient_id: Filter by patient ID
        date_from: Filter by start date
        date_to: Filter by end date
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        Paginated list of payment transactions
    """
    # TODO: Implement transaction listing with filters
    return {
        "items": [],
        "total": 0,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": 0
    }


@router.get("/transactions/{transaction_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    Get payment transaction by ID.

    Args:
        transaction_id: Transaction ID
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        Transaction details with allocations and refunds

    Raises:
        HTTPException 404: If transaction not found
    """
    # TODO: Implement transaction retrieval
    return {
        "id": transaction_id,
        "transaction_number": "TXN-2026-0001",
        "patient_id": 1,
        "patient_name": "John Doe",
        "invoice_id": 1,
        "amount": Decimal("100.00"),
        "payment_method": "cash",
        "status": "completed",
        "receipt_number": "RCPT-2026-0001",
        "transaction_date": datetime.now(),
        "allocated_amount": Decimal("100.00"),
        "refundable_amount": Decimal("0.00"),
        "allocations": [],
        "refunds": []
    }


@router.post("/refund", response_model=dict, status_code=status.HTTP_201_CREATED)
async def request_refund(
    refund_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "create"))
):
    """
    Request a refund for a payment transaction.

    Args:
        refund_data: Refund details including transaction_id, amount, reason
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:create permission

    Returns:
        Refund request details

    Raises:
        HTTPException 400: If validation error or refund not allowed
        HTTPException 404: If transaction not found
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement refund request logic
        # 1. Validate transaction exists and is eligible for refund
        # 2. Check refundable amount
        # 3. Create refund record with status 'pending'
        # 4. Notify finance team for approval

        await create_audit_log(
            db=db,
            action="REFUND_REQUESTED",
            resource_type="Refund",
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
            "transaction_id": refund_data.get("transaction_id"),
            "amount": refund_data.get("amount"),
            "reason": refund_data.get("reason"),
            "status": "pending_approval",
            "requested_by": current_user.username,
            "requested_at": datetime.now(),
            "message": "Refund request submitted successfully"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="REFUND_REQUEST_FAILED",
            resource_type="Refund",
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


@router.post("/refund/{refund_id}/approve", response_model=dict, status_code=status.HTTP_200_OK)
async def approve_refund(
    refund_id: int,
    approval_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "approve"))
):
    """
    Approve a refund request.

    Args:
        refund_id: Refund ID
        approval_data: Approval details including notes
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:approve permission

    Returns:
        Updated refund details

    Raises:
        HTTPException 404: If refund not found
        HTTPException 400: If refund not in pending status
    """
    request_info = await get_request_info(request)

    # TODO: Implement refund approval logic
    # 1. Validate refund exists and is pending
    # 2. Update refund status to 'approved'
    # 3. Create approval record

    await create_audit_log(
        db=db,
        action="REFUND_APPROVED",
        resource_type="Refund",
        resource_id=str(refund_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": refund_id,
        "status": "approved",
        "approved_by": current_user.username,
        "approved_at": datetime.now(),
        "approval_notes": approval_data.get("notes"),
        "message": "Refund approved successfully"
    }


@router.post("/refund/{refund_id}/process", response_model=dict, status_code=status.HTTP_200_OK)
async def process_refund(
    refund_id: int,
    processing_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "update"))
):
    """
    Process an approved refund.

    Args:
        refund_id: Refund ID
        processing_data: Processing details including refund_method, reference
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:update permission

    Returns:
        Processed refund details

    Raises:
        HTTPException 404: If refund not found
        HTTPException 400: If refund not approved
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement refund processing logic
        # 1. Validate refund is approved
        # 2. Process refund based on method (original payment, cash, bank transfer)
        # 3. Update refund status to 'processed'
        # 4. Update original transaction refunded amount
        # 5. Reverse allocations if necessary
        # 6. Generate refund receipt

        await create_audit_log(
            db=db,
            action="REFUND_PROCESSED",
            resource_type="Refund",
            resource_id=str(refund_id),
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "id": refund_id,
            "status": "processed",
            "processed_by": current_user.username,
            "processed_at": datetime.now(),
            "refund_method": processing_data.get("refund_method"),
            "reference_number": processing_data.get("reference"),
            "refund_receipt_number": "REF-RCPT-2026-0001",
            "message": "Refund processed successfully"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="REFUND_PROCESS_FAILED",
            resource_type="Refund",
            resource_id=str(refund_id),
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


@router.post("/settle", response_model=dict, status_code=status.HTTP_200_OK)
async def settle_payment(
    settlement_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "update"))
):
    """
    Mark a payment transaction as settled.

    Args:
        settlement_data: Settlement details including transaction_id, settlement_date
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:update permission

    Returns:
        Updated transaction details

    Raises:
        HTTPException 404: If transaction not found
        HTTPException 400: If transaction already settled
    """
    request_info = await get_request_info(request)

    # TODO: Implement payment settlement logic
    # 1. Validate transaction exists and is completed
    # 2. Update transaction status to 'settled'
    # 3. Record settlement date and reference

    await create_audit_log(
        db=db,
        action="PAYMENT_SETTLED",
        resource_type="Payment",
        resource_id=str(settlement_data.get("transaction_id")),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": settlement_data.get("transaction_id"),
        "status": "settled",
        "settled_by": current_user.username,
        "settled_at": datetime.now(),
        "settlement_date": settlement_data.get("settlement_date"),
        "message": "Payment settled successfully"
    }


# =============================================================================
# ALLOCATION ENDPOINTS
# =============================================================================

@router.post("/allocate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def allocate_payment(
    allocation_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "create"))
):
    """
    Allocate a payment to one or more invoices.

    Args:
        allocation_data: Allocation details including payment_id, allocations list
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:create permission

    Returns:
        Allocation details

    Raises:
        HTTPException 400: If validation error or insufficient funds
        HTTPException 404: If payment or invoice not found
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement payment allocation logic
        # 1. Validate payment exists and has sufficient unallocated amount
        # 2. Validate invoices exist and are approved
        # 3. Create allocation records
        # 4. Update invoice payment status
        # 5. Update payment allocated amount

        await create_audit_log(
            db=db,
            action="PAYMENT_ALLOCATED",
            resource_type="PaymentAllocation",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "payment_id": allocation_data.get("payment_id"),
            "total_allocated": allocation_data.get("total_amount"),
            "remaining": Decimal("0.00"),
            "allocations": [],
            "message": "Payment allocated successfully"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="PAYMENT_ALLOCATION_FAILED",
            resource_type="PaymentAllocation",
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


@router.get("/allocations/{payment_id}", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_payment_allocations(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    Get all allocations for a specific payment.

    Args:
        payment_id: Payment ID
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        List of allocations for the payment
    """
    # TODO: Implement allocation retrieval
    return [
        {
            "id": 1,
            "payment_id": payment_id,
            "invoice_id": 1,
            "invoice_number": "INV-2026-0001",
            "allocated_amount": Decimal("100.00"),
            "allocated_at": datetime.now()
        }
    ]


# =============================================================================
# DEPOSITS ENDPOINTS
# =============================================================================

@router.get("/deposits/patient/{patient_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_patient_deposits(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    Get all deposits for a specific patient.

    Args:
        patient_id: Patient ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        Paginated list of patient deposits
    """
    # TODO: Implement patient deposits retrieval
    return {
        "patient_id": patient_id,
        "items": [],
        "total": 0,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": 0
    }


@router.post("/deposits", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit_data: dict,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "create"))
):
    """
    Create a new patient deposit.

    Args:
        deposit_data: Deposit details including patient_id, amount, payment_method
        background_tasks: FastAPI background tasks
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:create permission

    Returns:
        Created deposit details

    Raises:
        HTTPException 400: If validation error
        HTTPException 404: If patient not found
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement deposit creation logic
        # 1. Validate patient exists
        # 2. Create deposit record
        # 3. Process payment
        # 4. Generate receipt

        await create_audit_log(
            db=db,
            action="DEPOSIT_CREATED",
            resource_type="Deposit",
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
            "patient_id": deposit_data.get("patient_id"),
            "amount": deposit_data.get("amount"),
            "payment_method": deposit_data.get("payment_method"),
            "balance": deposit_data.get("amount"),
            "deposit_number": "DEP-2026-0001",
            "receipt_number": "RCPT-2026-0001",
            "created_at": datetime.now(),
            "message": "Deposit created successfully"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="DEPOSIT_CREATE_FAILED",
            resource_type="Deposit",
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


@router.post("/deposits/use", response_model=dict, status_code=status.HTTP_200_OK)
async def use_deposit(
    usage_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "create"))
):
    """
    Use patient deposit for invoice payment.

    Args:
        usage_data: Usage details including patient_id, invoice_id, amount
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:create permission

    Returns:
        Usage details with remaining balance

    Raises:
        HTTPException 400: If insufficient deposit balance
        HTTPException 404: If patient or invoice not found
    """
    request_info = await get_request_info(request)

    try:
        # TODO: Implement deposit usage logic
        # 1. Validate patient has sufficient deposit balance
        # 2. Create deposit usage record
        # 3. Update deposit balance
        # 4. Create payment transaction
        # 5. Allocate to invoice
        # 6. Update invoice payment status

        await create_audit_log(
            db=db,
            action="DEPOSIT_USED",
            resource_type="DepositUsage",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return {
            "patient_id": usage_data.get("patient_id"),
            "invoice_id": usage_data.get("invoice_id"),
            "amount_used": usage_data.get("amount"),
            "remaining_balance": Decimal("0.00"),
            "payment_transaction_id": 1,
            "message": "Deposit used successfully"
        }
    except ValueError as e:
        await create_audit_log(
            db=db,
            action="DEPOSIT_USAGE_FAILED",
            resource_type="DepositUsage",
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


@router.get("/deposits/balance/{patient_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_deposit_balance(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    Get deposit balance for a patient.

    Args:
        patient_id: Patient ID
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        Deposit balance information

    Raises:
        HTTPException 404: If patient not found
    """
    # TODO: Implement deposit balance retrieval
    return {
        "patient_id": patient_id,
        "total_deposited": Decimal("0.00"),
        "total_used": Decimal("0.00"),
        "current_balance": Decimal("0.00"),
        "last_deposit": None,
        "last_usage": None
    }


# =============================================================================
# RECEIPTS ENDPOINTS
# =============================================================================

@router.get("/receipt/{transaction_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_receipt(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    Get receipt for a payment transaction.

    Args:
        transaction_id: Transaction ID
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        Receipt details

    Raises:
        HTTPException 404: If transaction or receipt not found
    """
    # TODO: Implement receipt retrieval
    return {
        "id": 1,
        "transaction_id": transaction_id,
        "receipt_number": "RCPT-2026-0001",
        "patient": {
            "id": 1,
            "name": "John Doe",
            "medical_record_number": "MRN-2026-0001"
        },
        "payment": {
            "amount": Decimal("100.00"),
            "payment_method": "cash",
            "payment_date": datetime.now()
        },
        "invoice": {
            "id": 1,
            "invoice_number": "INV-2026-0001"
        },
        "issued_by": current_user.username,
        "issued_at": datetime.now()
    }


@router.post("/receipt/{transaction_id}/regenerate", response_model=dict, status_code=status.HTTP_200_OK)
async def regenerate_receipt(
    transaction_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "update"))
):
    """
    Regenerate a receipt for a payment transaction.

    Args:
        transaction_id: Transaction ID
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with payments:update permission

    Returns:
        New receipt details

    Raises:
        HTTPException 404: If transaction not found
    """
    request_info = await get_request_info(request)

    # TODO: Implement receipt regeneration logic
    # 1. Validate transaction exists
    # 2. Generate new receipt number
    # 3. Create new receipt record
    # 4. Void old receipt if necessary

    await create_audit_log(
        db=db,
        action="RECEIPT_REGENERATED",
        resource_type="Receipt",
        resource_id=str(transaction_id),
        username=current_user.username,
        user_id=current_user.id,
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )

    return {
        "id": 2,
        "transaction_id": transaction_id,
        "receipt_number": "RCPT-2026-0002",
        "regenerated_by": current_user.username,
        "regenerated_at": datetime.now(),
        "message": "Receipt regenerated successfully"
    }


# =============================================================================
# REPORTING ENDPOINTS
# =============================================================================

@router.get("/reports/reconciliation", response_model=dict, status_code=status.HTTP_200_OK)
async def get_reconciliation_report(
    report_date: date = Query(..., description="Report date (default: today)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    Generate daily reconciliation report.

    Args:
        report_date: Report date
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        Daily reconciliation report with payment method breakdown
    """
    # TODO: Implement reconciliation report generation
    return {
        "report_date": report_date,
        "total_payments": Decimal("0.00"),
        "total_transactions": 0,
        "payment_methods": [
            {
                "method": "cash",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            {
                "method": "card",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            {
                "method": "transfer",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            {
                "method": "bpjs",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            {
                "method": "insurance",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            }
        ],
        "deposits": {
            "total_deposited": Decimal("0.00"),
            "total_used": Decimal("0.00"),
            "net_change": Decimal("0.00")
        },
        "refunds": {
            "total_refunded": Decimal("0.00"),
            "count": 0
        },
        "generated_at": datetime.now()
    }


@router.get("/reports/accounts-receivable", response_model=dict, status_code=status.HTTP_200_OK)
async def get_accounts_receivable_report(
    as_of_date: Optional[date] = Query(None, description="As of date (default: today)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    Generate accounts receivable report.

    Args:
        as_of_date: Report date (default: today)
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        Accounts receivable report with aging buckets
    """
    # TODO: Implement accounts receivable report generation
    report_date = as_of_date or date.today()

    return {
        "as_of_date": report_date,
        "total_receivable": Decimal("0.00"),
        "aging_buckets": {
            "current": {
                "days": "0-30",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            "overdue_31_60": {
                "days": "31-60",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            "overdue_61_90": {
                "days": "61-90",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            },
            "overdue_90_plus": {
                "days": "90+",
                "amount": Decimal("0.00"),
                "count": 0,
                "percentage": 0.0
            }
        },
        "top_outstanding": [],
        "generated_at": datetime.now()
    }


@router.get("/reports/settlement", response_model=dict, status_code=status.HTTP_200_OK)
async def get_settlement_report(
    date_from: date = Query(..., description="Start date"),
    date_to: date = Query(..., description="End date"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("payments", "read"))
):
    """
    Generate settlement report for a date range.

    Args:
        date_from: Start date
        date_to: End date
        payment_method: Filter by payment method
        db: Database session
        current_user: Authenticated user with payments:read permission

    Returns:
        Settlement report with transaction details
    """
    # TODO: Implement settlement report generation
    return {
        "date_from": date_from,
        "date_to": date_to,
        "payment_method": payment_method,
        "total_transactions": 0,
        "total_amount": Decimal("0.00"),
        "settled_amount": Decimal("0.00"),
        "pending_amount": Decimal("0.00"),
        "transactions": [],
        "summary": {
            "by_payment_method": [],
            "by_status": []
        },
        "generated_at": datetime.now()
    }
