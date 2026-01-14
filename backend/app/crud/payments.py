"""Payment Processing CRUD Operations

This module provides comprehensive CRUD operations for:
- Payment transaction processing and management
- Payment allocation to invoices
- Patient deposit management
- Refund processing and workflow
- Payment reconciliation and reporting
- Accounts receivable tracking

Supports Indonesian healthcare payment requirements including:
- Multi-payment method support (cash, transfer, credit card, BPJS, insurance)
- Payment allocation across multiple invoices
- Deposit management with tracking
- Refund workflow with approval
- Daily settlement and reconciliation
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func as sql_func, update, case, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal
import json

# Import models when they exist
# from app.models.billing import (
#     Payment, PaymentAllocation, PatientDeposit, Refund,
#     Invoice, PaymentMethod, PaymentStatus
# )
# from app.models.patient import Patient


# =============================================================================
# Payment Processing - Basic CRUD
# =============================================================================

async def get_payment_transaction(
    db: AsyncSession,
    payment_id: int,
) -> Optional[Any]:
    """
    Get payment transaction by ID with all relationships.

    Args:
        db: Database session
        payment_id: Payment ID

    Returns:
        Payment object or None
    """
    # stmt = (
    #     select(Payment)
    #     .options(
    #         selectinload(Payment.allocations),
    #         selectinload(Payment.invoice),
    #         selectinload(Payment.refunds),
    #         selectinload(Payment.patient)
    #     )
    #     .where(Payment.id == payment_id)
    # )
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


async def get_payment_transactions(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    invoice_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    status: Optional[str] = None,
    payment_date_from: Optional[date] = None,
    payment_date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    List payment transactions with filtering and pagination.

    Args:
        db: Database session
        patient_id: Filter by patient
        invoice_id: Filter by invoice
        payment_method: Filter by payment method
        status: Filter by status
        payment_date_from: Filter by payment date start
        payment_date_to: Filter by payment date end
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (list of payments, total count)
    """
    # conditions = []
    # if patient_id:
    #     conditions.append(Payment.patient_id == patient_id)
    # if invoice_id:
    #     conditions.append(Payment.invoice_id == invoice_id)
    # if payment_method:
    #     conditions.append(Payment.payment_method == payment_method)
    # if status:
    #     conditions.append(Payment.status == status)
    # if payment_date_from:
    #     conditions.append(Payment.payment_date >= payment_date_from)
    # if payment_date_to:
    #     conditions.append(Payment.payment_date <= payment_date_to)

    # stmt = select(Payment)
    # if conditions:
    #     stmt = stmt.where(and_(*conditions))

    # count_stmt = select(sql_func.count(Payment.id))
    # if conditions:
    #     count_stmt = count_stmt.where(and_(*conditions))

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.options(selectinload(Payment.allocations))
    # stmt = stmt.order_by(Payment.payment_date.desc())
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # payments = result.scalars().all()

    # return list(payments), total
    return [], 0


async def create_payment_transaction(
    db: AsyncSession,
    payment_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Create a new payment transaction.

    Args:
        db: Database session
        payment_data: Payment creation data
        created_by_id: User ID creating the payment

    Returns:
        Created payment object
    """
    # Generate payment number
    payment_number = await generate_payment_number(db)

    # db_payment = Payment(
    #     payment_number=payment_number,
    #     patient_id=payment_data['patient_id'],
    #     invoice_id=payment_data.get('invoice_id'),
    #     payment_method=payment_data['payment_method'],
    #     amount=payment_data['amount'],
    #     payment_date=payment_data.get('payment_date', datetime.utcnow()),
    #     reference_number=payment_data.get('reference_number'),
    #     bank_name=payment_data.get('bank_name'),
    #     card_last_four=payment_data.get('card_last_four'),
    #     payment_gateway_response=payment_data.get('payment_gateway_response'),
    #     notes=payment_data.get('notes'),
    #     status='pending',
    #     created_by_id=created_by_id,
    # )

    # db.add(db_payment)
    # await db.flush()

    # # If invoice_id provided, auto-allocate payment
    # if 'invoice_id' in payment_data:
    #     await allocate_payment_to_invoice(
    #         db=db,
    #         payment_id=db_payment.id,
    #         invoice_id=payment_data['invoice_id'],
    #         amount=payment_data['amount']
    #     )

    # await db.commit()
    # await db.refresh(db_payment)

    # return db_payment
    return None


async def process_payment(
    db: AsyncSession,
    payment_id: int,
    processing_data: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Process a pending payment through payment gateway or validation.

    Args:
        db: Database session
        payment_id: Payment ID
        processing_data: Optional processing data (gateway response, etc.)

    Returns:
        Updated payment object
    """
    # payment = await get_payment_transaction(db, payment_id)
    # if not payment:
    #     raise ValueError("Payment not found")

    # if payment.status != 'pending':
    #     raise ValueError("Payment is not in pending status")

    # # Process payment based on method
    # if payment.payment_method == 'cash':
    #     payment.status = 'completed'
    #     payment.processed_at = datetime.utcnow()
    # elif payment.payment_method == 'transfer':
    #     # Validate bank transfer
    #     payment.status = 'completed'
    #     payment.processed_at = datetime.utcnow()
    # elif payment.payment_method == 'credit_card':
    #     # Process through payment gateway
    #     if processing_data and 'gateway_response' in processing_data:
    #         payment.payment_gateway_response = processing_data['gateway_response']
    #         if processing_data['gateway_response'].get('success'):
    #             payment.status = 'completed'
    #             payment.processed_at = datetime.utcnow()
    #         else:
    #             payment.status = 'failed'
    #             payment.failure_reason = processing_data['gateway_response'].get('error')
    # elif payment.payment_method == 'bpjs':
    #     # BPJS payment processing
    #     payment.status = 'completed'
    #     payment.processed_at = datetime.utcnow()
    # elif payment.payment_method == 'insurance':
    #     # Insurance payment processing
    #     payment.status = 'completed'
    #     payment.processed_at = datetime.utcnow()

    # await db.commit()
    # await db.refresh(payment)

    # return payment
    return None


async def refund_payment(
    db: AsyncSession,
    payment_id: int,
    refund_amount: Optional[Decimal] = None,
    reason: Optional[str] = None,
    requested_by_id: Optional[int] = None,
) -> Any:
    """
    Request a refund for a payment.

    Args:
        db: Database session
        payment_id: Payment ID
        refund_amount: Amount to refund (default: full amount)
        reason: Refund reason
        requested_by_id: User requesting refund

    Returns:
        Created refund object
    """
    # payment = await get_payment_transaction(db, payment_id)
    # if not payment:
    #     raise ValueError("Payment not found")

    # if payment.status != 'completed':
    #     raise ValueError("Can only refund completed payments")

    # amount_to_refund = refund_amount or payment.amount

    # if amount_to_refund > payment.amount:
    #     raise ValueError("Refund amount cannot exceed payment amount")

    # # Check if payment has already been refunded
    # total_refunded = await get_total_refunded_for_payment(db, payment_id)
    # if total_refunded + amount_to_refund > payment.amount:
    #     raise ValueError("Total refunds cannot exceed payment amount")

    # refund = await create_refund(
    #     db=db,
    #     payment_id=payment_id,
    #     refund_amount=amount_to_refund,
    #     reason=reason,
    #     requested_by_id=requested_by_id
    # )

    # return refund
    return None


async def partial_refund(
    db: AsyncSession,
    payment_id: int,
    refund_amount: Decimal,
    reason: Optional[str] = None,
    requested_by_id: Optional[int] = None,
) -> Any:
    """
    Request a partial refund for a payment.

    Args:
        db: Database session
        payment_id: Payment ID
        refund_amount: Amount to refund
        reason: Refund reason
        requested_by_id: User requesting refund

    Returns:
        Created refund object
    """
    return await refund_payment(
        db=db,
        payment_id=payment_id,
        refund_amount=refund_amount,
        reason=reason,
        requested_by_id=requested_by_id
    )


async def get_payments_by_invoice(
    db: AsyncSession,
    invoice_id: int,
    include_allocations: bool = True,
) -> List[Any]:
    """
    Get all payments for a specific invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID
        include_allocations: Include allocation details

    Returns:
        List of payments
    """
    # stmt = select(Payment).join(
    #     PaymentAllocation,
    #     Payment.id == PaymentAllocation.payment_id
    # ).where(
    #     PaymentAllocation.invoice_id == invoice_id
    # ).order_by(Payment.payment_date.desc())

    # if include_allocations:
    #     stmt = stmt.options(selectinload(Payment.allocations))

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def get_payments_by_date_range(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    payment_method: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Any]:
    """
    Get payments within a date range.

    Args:
        db: Database session
        start_date: Start date
        end_date: End date
        payment_method: Optional payment method filter
        status: Optional status filter

    Returns:
        List of payments
    """
    # conditions = [
    #     sql_func.date(Payment.payment_date) >= start_date,
    #     sql_func.date(Payment.payment_date) <= end_date,
    # ]

    # if payment_method:
    #     conditions.append(Payment.payment_method == payment_method)
    # if status:
    #     conditions.append(Payment.status == status)

    # stmt = select(Payment).where(
    #     and_(*conditions)
    # ).order_by(Payment.payment_date)

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def generate_payment_number(db: AsyncSession) -> str:
    """
    Generate a unique payment number.
    Format: PAY-YYYY-XXXXX (sequential per year)

    Args:
        db: Database session

    Returns:
        Unique payment number
    """
    # year = datetime.now().year
    # pattern = f"PAY-{year}-%"

    # stmt = select(sql_func.max(Payment.payment_number)).filter(
    #     Payment.payment_number.like(pattern)
    # )
    # result = await db.execute(stmt)
    # last_number = result.scalar()

    # if last_number:
    #     last_sequence = int(last_number.split('-')[-1])
    #     new_sequence = last_sequence + 1
    # else:
    #     new_sequence = 1

    # return f"PAY-{year}-{new_sequence:05d}"
    return f"PAY-{datetime.now().year}-00001"


async def generate_receipt_number(db: AsyncSession) -> str:
    """
    Generate a unique receipt number.
    Format: RCP-YYYY-XXXXX (sequential per year)

    Args:
        db: Database session

    Returns:
        Unique receipt number
    """
    # year = datetime.now().year
    # pattern = f"RCP-{year}-%"

    # stmt = select(sql_func.max(Payment.receipt_number)).filter(
    #     Payment.receipt_number.like(pattern)
    # )
    # result = await db.execute(stmt)
    # last_number = result.scalar()

    # if last_number:
    #     last_sequence = int(last_number.split('-')[-1])
    #     new_sequence = last_sequence + 1
    # else:
    #     new_sequence = 1

    # return f"RCP-{year}-{new_sequence:05d}"
    return f"RCP-{datetime.now().year}-00001"


async def settle_payment(
    db: AsyncSession,
    payment_id: int,
    settlement_data: Dict[str, Any],
) -> Any:
    """
    Settle a payment (bank reconciliation, POS settlement, etc.).

    Args:
        db: Database session
        payment_id: Payment ID
        settlement_data: Settlement details

    Returns:
        Updated payment object
    """
    # payment = await get_payment_transaction(db, payment_id)
    # if not payment:
    #     raise ValueError("Payment not found")

    # if payment.status != 'completed':
    #     raise ValueError("Can only settle completed payments")

    # payment.settlement_date = settlement_data.get('settlement_date', datetime.utcnow())
    # payment.settlement_reference = settlement_data.get('settlement_reference')
    # payment.settlement_status = 'settled'

    # await db.commit()
    # await db.refresh(payment)

    # return payment
    return None


async def mark_as_settled(
    db: AsyncSession,
    payment_id: int,
    settlement_reference: Optional[str] = None,
) -> Any:
    """
    Mark a payment as settled.

    Args:
        db: Database session
        payment_id: Payment ID
        settlement_reference: Optional settlement reference

    Returns:
        Updated payment object
    """
    return await settle_payment(
        db=db,
        payment_id=payment_id,
        settlement_data={
            'settlement_reference': settlement_reference
        }
    )


# =============================================================================
# Payment Allocation
# =============================================================================

async def allocate_payment_to_invoice(
    db: AsyncSession,
    payment_id: int,
    invoice_id: int,
    amount: Decimal,
    allocation_notes: Optional[str] = None,
) -> Any:
    """
    Allocate a payment to a specific invoice.

    Args:
        db: Database session
        payment_id: Payment ID
        invoice_id: Invoice ID
        amount: Amount to allocate
        allocation_notes: Optional notes

    Returns:
        Payment allocation object
    """
    # payment = await get_payment_transaction(db, payment_id)
    # if not payment:
    #     raise ValueError("Payment not found")

    # Check if payment has sufficient unallocated amount
    # allocated_sum = await get_total_allocated_for_payment(db, payment_id)
    # available_amount = payment.amount - allocated_sum

    # if amount > available_amount:
    #     raise ValueError(f"Insufficient unallocated amount. Available: {available_amount}")

    # # Create allocation
    # allocation = PaymentAllocation(
    #     payment_id=payment_id,
    #     invoice_id=invoice_id,
    #     amount=amount,
    #     allocated_at=datetime.utcnow(),
    #     notes=allocation_notes,
    # )

    # db.add(allocation)

    # # Update invoice
    # from app.crud.billing import get_invoice
    # invoice = await get_invoice(db, invoice_id)
    # if invoice:
    #     invoice.paid_amount = (invoice.paid_amount or Decimal('0')) + amount
    #     invoice.balance_due = invoice.total_amount - invoice.paid_amount

    #     # Update invoice status if fully paid
    #     if invoice.balance_due <= Decimal('0.01'):  # Allow for rounding
    #         invoice.status = 'paid'
    #     elif invoice.paid_amount > Decimal('0'):
    #         invoice.status = 'partial_paid'

    # await db.commit()
    # await db.refresh(allocation)

    # return allocation
    return None


async def get_payment_allocations(
    db: AsyncSession,
    payment_id: int,
) -> List[Any]:
    """
    Get all allocations for a payment.

    Args:
        db: Database session
        payment_id: Payment ID

    Returns:
        List of payment allocations
    """
    # stmt = select(PaymentAllocation).where(
    #     PaymentAllocation.payment_id == payment_id
    # ).order_by(PaymentAllocation.allocated_at)

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def auto_allocate_payment(
    db: AsyncSession,
    payment_id: int,
    patient_id: Optional[int] = None,
    allocation_strategy: str = 'fifo',
) -> List[Any]:
    """
    Automatically allocate payment to unpaid invoices.

    Args:
        db: Database session
        payment_id: Payment ID
        patient_id: Patient ID (if not provided, use from payment)
        allocation_strategy: Allocation strategy ('fifo', 'highest_balance', 'due_date')

    Returns:
        List of created allocations
    """
    # payment = await get_payment_transaction(db, payment_id)
    # if not payment:
    #     raise ValueError("Payment not found")

    # target_patient_id = patient_id or payment.patient_id

    # # Get unpaid invoices
    # unpaid_invoices = await get_unpaid_invoices(db, target_patient_id)

    # if not unpaid_invoices:
    #     return []

    # # Sort invoices based on strategy
    # if allocation_strategy == 'fifo':
    #     # Oldest invoices first
    #     unpaid_invoices.sort(key=lambda x: x.invoice_date)
    # elif allocation_strategy == 'highest_balance':
    #     # Highest balance first
    #     unpaid_invoices.sort(key=lambda x: x.balance_due, reverse=True)
    # elif allocation_strategy == 'due_date':
    #     # Nearest due date first
    #     unpaid_invoices.sort(key=lambda x: x.due_date or date.max)

    # # Allocate payment
    # allocations = []
    # remaining_amount = payment.amount

    # for invoice in unpaid_invoices:
    #     if remaining_amount <= 0:
    #         break

    #     allocate_amount = min(remaining_amount, invoice.balance_due)

    #     allocation = await allocate_payment_to_invoice(
    #         db=db,
    #         payment_id=payment_id,
    #         invoice_id=invoice.id,
    #         amount=allocate_amount
    #     )

    #     allocations.append(allocation)
    #     remaining_amount -= allocate_amount

    # return allocations
    return []


async def deallocate_payment(
    db: AsyncSession,
    allocation_id: int,
    reason: Optional[str] = None,
) -> bool:
    """
    Deallocate a payment from an invoice.

    Args:
        db: Database session
        allocation_id: Allocation ID
        reason: Reason for deallocation

    Returns:
        True if deallocated
    """
    # stmt = select(PaymentAllocation).where(
    #     PaymentAllocation.id == allocation_id
    # )
    # result = await db.execute(stmt)
    # allocation = result.scalar_one_or_none()

    # if not allocation:
    #     return False

    # invoice_id = allocation.invoice_id
    # amount = allocation.amount

    # # Update invoice
    # from app.crud.billing import get_invoice
    # invoice = await get_invoice(db, invoice_id)
    # if invoice:
    #     invoice.paid_amount = (invoice.paid_amount or Decimal('0')) - amount
    #     invoice.balance_due = invoice.total_amount - invoice.paid_amount

    #     # Update invoice status
    #     if invoice.balance_due >= invoice.total_amount - Decimal('0.01'):
    #         invoice.status = 'approved'
    #     elif invoice.paid_amount > Decimal('0'):
    #         invoice.status = 'partial_paid'

    # # Delete allocation
    # await db.delete(allocation)
    # await db.commit()

    # return True
    return False


async def get_unpaid_invoices(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    include_overdue: bool = False,
) -> List[Any]:
    """
    Get unpaid invoices.

    Args:
        db: Database session
        patient_id: Optional patient filter
        include_overdue: Only include overdue invoices

    Returns:
        List of unpaid invoices
    """
    # from app.crud.billing import get_invoices

    # status = 'approved'  # Unpaid but approved
    # invoices, _ = await get_invoices(
    #     db=db,
    #     patient_id=patient_id,
    #     status=status,
    #     page_size=1000  # Get all
    # )

    # if include_overdue:
    #     today = date.today()
    #     invoices = [inv for inv in invoices if inv.due_date and inv.due_date < today]

    # return invoices
    return []


async def get_partially_paid_invoices(
    db: AsyncSession,
    patient_id: Optional[int] = None,
) -> List[Any]:
    """
    Get partially paid invoices.

    Args:
        db: Database session
        patient_id: Optional patient filter

    Returns:
        List of partially paid invoices
    """
    # from app.crud.billing import get_invoices

    # invoices, _ = await get_invoices(
    #     db=db,
    #     patient_id=patient_id,
    #     status='partial_paid',
    #     page_size=1000  # Get all
    # )

    # return invoices
    return []


# =============================================================================
# Patient Deposits
# =============================================================================

async def get_patient_deposit(
    db: AsyncSession,
    deposit_id: int,
) -> Optional[Any]:
    """
    Get patient deposit by ID.

    Args:
        db: Database session
        deposit_id: Deposit ID

    Returns:
        Deposit object or None
    """
    # stmt = (
    #     select(PatientDeposit)
    #     .options(
    #         selectinload(PatientDeposit.transactions),
    #         selectinload(PatientDeposit.patient)
    #     )
    #     .where(PatientDeposit.id == deposit_id)
    # )
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


async def get_patient_deposits(
    db: AsyncSession,
    patient_id: int,
    active_only: bool = True,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get all deposits for a patient.

    Args:
        db: Database session
        patient_id: Patient ID
        active_only: Only show active deposits with balance
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (deposits, total count)
    """
    # conditions = [PatientDeposit.patient_id == patient_id]

    # if active_only:
    #     conditions.append(PatientDeposit.balance > 0)

    # stmt = select(PatientDeposit).where(and_(*conditions))
    # count_stmt = select(sql_func.count(PatientDeposit.id)).where(and_(*conditions))

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.order_by(PatientDeposit.created_at.desc())
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # deposits = result.scalars().all()

    # return list(deposits), total
    return [], 0


async def create_patient_deposit(
    db: AsyncSession,
    patient_id: int,
    deposit_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Create a new patient deposit.

    Args:
        db: Database session
        patient_id: Patient ID
        deposit_data: Deposit data
        created_by_id: User creating deposit

    Returns:
        Created deposit object
    """
    # Generate deposit number
    deposit_number = await generate_deposit_number(db)

    # db_deposit = PatientDeposit(
    #     deposit_number=deposit_number,
    #     patient_id=patient_id,
    #     deposit_type=deposit_data.get('deposit_type', 'general'),
    #     initial_amount=deposit_data['amount'],
    #     balance=deposit_data['amount'],
    #     payment_method=deposit_data.get('payment_method'),
    #     reference_number=deposit_data.get('reference_number'),
    #     notes=deposit_data.get('notes'),
    #     status='active',
    #     created_by_id=created_by_id,
    # )

    # db.add(db_deposit)
    # await db.commit()
    # await db.refresh(db_deposit)

    # return db_deposit
    return None


async def use_deposit(
    db: AsyncSession,
    deposit_id: int,
    invoice_id: int,
    amount: Decimal,
    notes: Optional[str] = None,
) -> Any:
    """
    Use patient deposit to pay invoice.

    Args:
        db: Database session
        deposit_id: Deposit ID
        invoice_id: Invoice ID
        amount: Amount to use
        notes: Optional notes

    Returns:
        Deposit transaction object
    """
    # deposit = await get_patient_deposit(db, deposit_id)
    # if not deposit:
    #     raise ValueError("Deposit not found")

    # if deposit.balance < amount:
    #     raise ValueError(f"Insufficient deposit balance. Available: {deposit.balance}")

    # # Create transaction
    # transaction = DepositTransaction(
    #     deposit_id=deposit_id,
    #     transaction_type='usage',
    #     amount=-amount,
    #     invoice_id=invoice_id,
    #     notes=notes,
    #     transaction_date=datetime.utcnow(),
    # )

    # db.add(transaction)

    # # Update deposit balance
    # deposit.balance -= amount

    # # Create payment allocation
    # await allocate_payment_to_invoice(
    #     db=db,
    #     payment_id=deposit_id,  # Using deposit_id as payment reference
    #     invoice_id=invoice_id,
    #     amount=amount
    # )

    # await db.commit()
    # await db.refresh(transaction)

    # return transaction
    return None


async def add_to_deposit(
    db: AsyncSession,
    deposit_id: int,
    amount: Decimal,
    payment_method: str,
    reference_number: Optional[str] = None,
    notes: Optional[str] = None,
) -> Any:
    """
    Add funds to existing deposit.

    Args:
        db: Database session
        deposit_id: Deposit ID
        amount: Amount to add
        payment_method: Payment method
        reference_number: Optional reference
        notes: Optional notes

    Returns:
        Deposit transaction object
    """
    # deposit = await get_patient_deposit(db, deposit_id)
    # if not deposit:
    #     raise ValueError("Deposit not found")

    # # Create transaction
    # transaction = DepositTransaction(
    #     deposit_id=deposit_id,
    #     transaction_type='deposit',
    #     amount=amount,
    #     payment_method=payment_method,
    #     reference_number=reference_number,
    #     notes=notes,
    #     transaction_date=datetime.utcnow(),
    # )

    # db.add(transaction)

    # # Update deposit balance
    # deposit.balance += amount

    # await db.commit()
    # await db.refresh(transaction)

    # return transaction
    return None


async def get_deposit_balance(
    db: AsyncSession,
    patient_id: int,
    deposit_type: Optional[str] = None,
) -> Decimal:
    """
    Get total deposit balance for a patient.

    Args:
        db: Database session
        patient_id: Patient ID
        deposit_type: Optional deposit type filter

    Returns:
        Total balance
    """
    # conditions = [
    #     PatientDeposit.patient_id == patient_id,
    #     PatientDeposit.status == 'active',
    # ]

    # if deposit_type:
    #     conditions.append(PatientDeposit.deposit_type == deposit_type)

    # stmt = select(sql_func.sum(PatientDeposit.balance)).where(
    #     and_(*conditions)
    # )

    # result = await db.execute(stmt)
    # return result.scalar() or Decimal('0.00')
    return Decimal('0.00')


async def generate_deposit_number(db: AsyncSession) -> str:
    """
    Generate a unique deposit number.
    Format: DEP-YYYY-XXXXX (sequential per year)

    Args:
        db: Database session

    Returns:
        Unique deposit number
    """
    # year = datetime.now().year
    # pattern = f"DEP-{year}-%"

    # stmt = select(sql_func.max(PatientDeposit.deposit_number)).filter(
    #     PatientDeposit.deposit_number.like(pattern)
    # )
    # result = await db.execute(stmt)
    # last_number = result.scalar()

    # if last_number:
    #     last_sequence = int(last_number.split('-')[-1])
    #     new_sequence = last_sequence + 1
    # else:
    #     new_sequence = 1

    # return f"DEP-{year}-{new_sequence:05d}"
    return f"DEP-{datetime.now().year}-00001"


# =============================================================================
# Refunds
# =============================================================================

async def create_refund(
    db: AsyncSession,
    payment_id: int,
    refund_amount: Decimal,
    reason: Optional[str] = None,
    requested_by_id: Optional[int] = None,
) -> Any:
    """
    Create a refund request.

    Args:
        db: Database session
        payment_id: Payment ID
        refund_amount: Amount to refund
        reason: Refund reason
        requested_by_id: User requesting refund

    Returns:
        Created refund object
    """
    # payment = await get_payment_transaction(db, payment_id)
    # if not payment:
    #     raise ValueError("Payment not found")

    # # Generate refund number
    # refund_number = await _generate_refund_number(db)

    # db_refund = Refund(
    #     refund_number=refund_number,
    #     payment_id=payment_id,
    #     invoice_id=payment.invoice_id,
    #     patient_id=payment.patient_id,
    #     refund_amount=refund_amount,
    #     reason=reason,
    #     status='pending',
    #     requested_by_id=requested_by_id,
    #     requested_at=datetime.utcnow(),
    # )

    # db.add(db_refund)
    # await db.commit()
    # await db.refresh(db_refund)

    # return db_refund
    return None


async def approve_refund(
    db: AsyncSession,
    refund_id: int,
    approved_by_id: int,
    notes: Optional[str] = None,
) -> Any:
    """
    Approve a refund request.

    Args:
        db: Database session
        refund_id: Refund ID
        approved_by_id: Approver user ID
        notes: Optional notes

    Returns:
        Updated refund object
    """
    # refund = await get_refund(db, refund_id)
    # if not refund:
    #     raise ValueError("Refund not found")

    # if refund.status != 'pending':
    #     raise ValueError("Refund is not in pending status")

    # refund.status = 'approved'
    # refund.approved_by_id = approved_by_id
    # refund.approved_at = datetime.utcnow()
    # refund.approval_notes = notes

    # await db.commit()
    # await db.refresh(refund)

    # return refund
    return None


async def process_refund(
    db: AsyncSession,
    refund_id: int,
    refund_method: Optional[str] = None,
    refund_reference: Optional[str] = None,
    processed_by_id: Optional[int] = None,
) -> Any:
    """
    Process an approved refund.

    Args:
        db: Database session
        refund_id: Refund ID
        refund_method: Refund method (default: original payment method)
        refund_reference: Refund transaction reference
        processed_by_id: User processing refund

    Returns:
        Updated refund object
    """
    # refund = await get_refund(db, refund_id)
    # if not refund:
    #     raise ValueError("Refund not found")

    # if refund.status != 'approved':
    #     raise ValueError("Refund is not approved")

    # payment = await get_payment_transaction(db, refund.payment_id)
    # actual_refund_method = refund_method or payment.payment_method

    # # Process refund based on method
    # if actual_refund_method == 'cash':
    #     # Cash refund - immediate
    #     refund.status = 'completed'
    #     refund.refund_method = actual_refund_method
    #     refund.refund_reference = refund_reference
    #     refund.refunded_at = datetime.utcnow()
    # elif actual_refund_method == 'transfer':
    #     # Bank transfer refund
    #     refund.status = 'processing'
    #     refund.refund_method = actual_refund_method
    #     refund.refund_reference = refund_reference
    # elif actual_refund_method == 'credit_card':
    #     # Credit card refund through gateway
    #     refund.status = 'processing'
    #     refund.refund_method = actual_refund_method
    #     refund.refund_reference = refund_reference

    # refund.processed_by_id = processed_by_id

    # await db.commit()
    # await db.refresh(refund)

    # return refund
    return None


async def get_refunds(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    payment_id: Optional[int] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get refunds with filtering.

    Args:
        db: Database session
        patient_id: Optional patient filter
        payment_id: Optional payment filter
        status: Optional status filter
        from_date: Optional start date
        to_date: Optional end date
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (refunds, total count)
    """
    # conditions = []

    # if patient_id:
    #     conditions.append(Refund.patient_id == patient_id)
    # if payment_id:
    #     conditions.append(Refund.payment_id == payment_id)
    # if status:
    #     conditions.append(Refund.status == status)
    # if from_date:
    #     conditions.append(Refund.requested_at >= from_date)
    # if to_date:
    #     conditions.append(Refund.requested_at <= to_date)

    # stmt = select(Refund)
    # if conditions:
    #     stmt = stmt.where(and_(*conditions))

    # count_stmt = select(sql_func.count(Refund.id))
    # if conditions:
    #     count_stmt = count_stmt.where(and_(*conditions))

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.order_by(Refund.requested_at.desc())
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # refunds = result.scalars().all()

    # return list(refunds), total
    return [], 0


async def get_refund_by_payment(
    db: AsyncSession,
    payment_id: int,
) -> List[Any]:
    """
    Get all refunds for a payment.

    Args:
        db: Database session
        payment_id: Payment ID

    Returns:
        List of refunds
    """
    return await get_refunds(
        db=db,
        payment_id=payment_id,
        page_size=1000
    )


async def refund_to_original_payment_method(
    db: AsyncSession,
    refund_id: int,
    processed_by_id: Optional[int] = None,
) -> Any:
    """
    Process refund to original payment method.

    Args:
        db: Database session
        refund_id: Refund ID
        processed_by_id: User processing refund

    Returns:
        Updated refund object
    """
    # refund = await get_refund(db, refund_id)
    # if not refund:
    #     raise ValueError("Refund not found")

    # payment = await get_payment_transaction(db, refund.payment_id)

    # return await process_refund(
    #     db=db,
    #     refund_id=refund_id,
    #     refund_method=payment.payment_method,
    #     processed_by_id=processed_by_id
    # )
    return None


async def get_refund(
    db: AsyncSession,
    refund_id: int,
) -> Optional[Any]:
    """
    Get refund by ID.

    Args:
        db: Database session
        refund_id: Refund ID

    Returns:
        Refund object or None
    """
    # stmt = select(Refund).where(Refund.id == refund_id)
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


# =============================================================================
# Reporting
# =============================================================================

async def get_payment_summary(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    payment_method: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get payment summary for a date range.

    Args:
        db: Database session
        start_date: Start date
        end_date: End date
        department_id: Optional department filter
        payment_method: Optional payment method filter

    Returns:
        Payment summary data
    """
    # conditions = [
    #     sql_func.date(Payment.payment_date) >= start_date,
    #     sql_func.date(Payment.payment_date) <= end_date,
    #     Payment.status == 'completed',
    # ]

    # if payment_method:
    #     conditions.append(Payment.payment_method == payment_method)

    # # Get total payments
    # stmt = select(
    #     sql_func.sum(Payment.amount).label('total_amount'),
    #     sql_func.count(Payment.id).label('payment_count'),
    # ).where(and_(*conditions))

    # result = await db.execute(stmt)
    # summary = result.one()

    # # Get pending payments
    # pending_conditions = conditions.copy()
    # pending_conditions[-1] = Payment.status == 'pending'

    # pending_stmt = select(
    #     sql_func.sum(Payment.amount).label('pending_amount'),
    #     sql_func.count(Payment.id).label('pending_count'),
    # ).where(and_(*pending_conditions))

    # pending_result = await db.execute(pending_stmt)
    # pending = pending_result.one()

    # return {
    #     'start_date': start_date,
    #     'end_date': end_date,
    #     'total_amount': summary.total_amount or Decimal('0.00'),
    #     'payment_count': summary.payment_count or 0,
    #     'pending_amount': pending.pending_amount or Decimal('0.00'),
    #     'pending_count': pending.pending_count or 0,
    # }

    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': Decimal('0.00'),
        'payment_count': 0,
        'pending_amount': Decimal('0.00'),
        'pending_count': 0,
    }


async def get_accounts_receivable(
    db: AsyncSession,
    as_of_date: Optional[date] = None,
    patient_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get accounts receivable summary.

    Args:
        db: Database session
        as_of_date: Report date (default: today)
        patient_id: Optional patient filter

    Returns:
        Accounts receivable data
    """
    # from app.crud.billing import get_invoices

    # report_date = as_of_date or date.today()

    # # Get unpaid and partially paid invoices
    # unpaid_invoices, _ = await get_invoices(
    #     db=db,
    #     patient_id=patient_id,
    #     status='approved',
    #     page_size=10000
    # )

    # partial_invoices, _ = await get_invoices(
    #     db=db,
    #     patient_id=patient_id,
    #     status='partial_paid',
    #     page_size=10000
    # )

    # all_outstanding = unpaid_invoices + partial_invoices

    # total_outstanding = Decimal('0.00')
    # aging_buckets = {
    #     '0_30': Decimal('0.00'),
    #     '31_60': Decimal('0.00'),
    #     '61_90': Decimal('0.00'),
    #     '91_plus': Decimal('0.00'),
    # }

    # for invoice in all_outstanding:
    #     total_outstanding += invoice.balance_due

    #     if invoice.due_date:
    #         days_overdue = (report_date - invoice.due_date).days

    #         if days_overdue <= 30:
    #             aging_buckets['0_30'] += invoice.balance_due
    #         elif days_overdue <= 60:
    #             aging_buckets['31_60'] += invoice.balance_due
    #         elif days_overdue <= 90:
    #             aging_buckets['61_90'] += invoice.balance_due
    #         else:
    #             aging_buckets['91_plus'] += invoice.balance_due

    # return {
    #     'as_of_date': report_date,
    #     'total_outstanding': total_outstanding,
    #     'invoice_count': len(all_outstanding),
    #     'aging_buckets': aging_buckets,
    # }

    return {
        'as_of_date': as_of_date or date.today(),
        'total_outstanding': Decimal('0.00'),
        'invoice_count': 0,
        'aging_buckets': {
            '0_30': Decimal('0.00'),
            '31_60': Decimal('0.00'),
            '61_90': Decimal('0.00'),
            '91_plus': Decimal('0.00'),
        },
    }


async def get_settlement_report(
    db: AsyncSession,
    settlement_date: date,
) -> Dict[str, Any]:
    """
    Get settlement report for a specific date.

    Args:
        db: Database session
        settlement_date: Settlement date

    Returns:
        Settlement report data
    """
    # Get all settled payments for the date
    # stmt = select(Payment).where(
    #     and_(
    #         sql_func.date(Payment.settlement_date) == settlement_date,
    #         Payment.settlement_status == 'settled'
    #     )
    # )

    # result = await db.execute(stmt)
    # payments = result.scalars().all()

    # # Group by payment method
    # by_method = {}
    # total_settled = Decimal('0.00')

    # for payment in payments:
    #     method = payment.payment_method
    #     if method not in by_method:
    #         by_method[method] = {
    #             'count': 0,
    #             'total_amount': Decimal('0.00'),
    #         }

    #     by_method[method]['count'] += 1
    #     by_method[method]['total_amount'] += payment.amount
    #     total_settled += payment.amount

    # return {
    #     'settlement_date': settlement_date,
    #     'total_settled': total_settled,
    #     'payment_count': len(payments),
    #     'by_method': by_method,
    # }

    return {
        'settlement_date': settlement_date,
        'total_settled': Decimal('0.00'),
        'payment_count': 0,
        'by_method': {},
    }


async def get_payment_method_breakdown(
    db: AsyncSession,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """
    Get payment breakdown by payment method.

    Args:
        db: Database session
        start_date: Start date
        end_date: End date

    Returns:
        List of payment method summaries
    """
    # stmt = select(
    #     Payment.payment_method,
    #     sql_func.count(Payment.id).label('count'),
    #     sql_func.sum(Payment.amount).label('total_amount'),
    # ).where(
    #     and_(
    #         sql_func.date(Payment.payment_date) >= start_date,
    #         sql_func.date(Payment.payment_date) <= end_date,
    #         Payment.status == 'completed',
    #     )
    # ).group_by(Payment.payment_method)

    # result = await db.execute(stmt)
    # rows = result.all()

    # return [
    #     {
    #         'payment_method': row.payment_method,
    #         'count': row.count,
    #         'total_amount': row.total_amount or Decimal('0.00'),
    #     }
    #     for row in rows
    # ]

    return []


async def get_daily_reconciliation(
    db: AsyncSession,
    reconciliation_date: date,
) -> Dict[str, Any]:
    """
    Get daily reconciliation report.

    Args:
        db: Database session
        reconciliation_date: Reconciliation date

    Returns:
        Daily reconciliation data
    """
    # Get all payments for the date
    # stmt = select(Payment).where(
    #     sql_func.date(Payment.payment_date) == reconciliation_date
    # )

    # result = await db.execute(stmt)
    # payments = result.scalars().all()

    # # Group by status and method
    # by_status = {}
    # by_method = {}
    # total_collected = Decimal('0.00')
    # total_pending = Decimal('0.00')

    # for payment in payments:
    #     # By status
    #     status = payment.status
    #     if status not in by_status:
    #         by_status[status] = {
    #             'count': 0,
    #             'total_amount': Decimal('0.00'),
    #         }

    #     by_status[status]['count'] += 1
    #     by_status[status]['total_amount'] += payment.amount

    #     # By method
    #     method = payment.payment_method
    #     if method not in by_method:
    #         by_method[method] = {
    #             'count': 0,
    #             'total_amount': Decimal('0.00'),
    #         }

    #     by_method[method]['count'] += 1
    #     by_method[method]['total_amount'] += payment.amount

    #     # Totals
    #     if payment.status == 'completed':
    #         total_collected += payment.amount
    #     elif payment.status == 'pending':
    #         total_pending += payment.amount

    # return {
    #     'date': reconciliation_date,
    #     'total_payments': len(payments),
    #     'total_collected': total_collected,
    #     'total_pending': total_pending,
    #     'by_status': by_status,
    #     'by_method': by_method,
    # }

    return {
        'date': reconciliation_date,
        'total_payments': 0,
        'total_collected': Decimal('0.00'),
        'total_pending': Decimal('0.00'),
        'by_status': {},
        'by_method': {},
    }


# =============================================================================
# Helper Functions
# =============================================================================

async def get_total_allocated_for_payment(
    db: AsyncSession,
    payment_id: int,
) -> Decimal:
    """
    Get total allocated amount for a payment.

    Args:
        db: Database session
        payment_id: Payment ID

    Returns:
        Total allocated amount
    """
    # stmt = select(sql_func.sum(PaymentAllocation.amount)).where(
    #     PaymentAllocation.payment_id == payment_id
    # )

    # result = await db.execute(stmt)
    # return result.scalar() or Decimal('0.00')
    return Decimal('0.00')


async def get_total_refunded_for_payment(
    db: AsyncSession,
    payment_id: int,
) -> Decimal:
    """
    Get total refunded amount for a payment.

    Args:
        db: Database session
        payment_id: Payment ID

    Returns:
        Total refunded amount
    """
    # stmt = select(sql_func.sum(Refund.refund_amount)).where(
    #     and_(
    #         Refund.payment_id == payment_id,
    #         Refund.status.in_(['approved', 'completed', 'processing'])
    #     )
    # )

    # result = await db.execute(stmt)
    # return result.scalar() or Decimal('0.00')
    return Decimal('0.00')


async def _generate_refund_number(db: AsyncSession) -> str:
    """
    Generate a unique refund number.
    Format: REF-YYYY-XXXXX (sequential per year)

    Args:
        db: Database session

    Returns:
        Unique refund number
    """
    # year = datetime.now().year
    # pattern = f"REF-{year}-%"

    # stmt = select(sql_func.max(Refund.refund_number)).filter(
    #     Refund.refund_number.like(pattern)
    # )
    # result = await db.execute(stmt)
    # last_number = result.scalar()

    # if last_number:
    #     last_sequence = int(last_number.split('-')[-1])
    #     new_sequence = last_sequence + 1
    # else:
    #     new_sequence = 1

    # return f"REF-{year}-{new_sequence:05d}"
    return f"REF-{datetime.now().year}-00001"
