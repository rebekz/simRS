"""Billing and Invoicing CRUD Operations

This module provides CRUD operations for:
- Invoice management and lifecycle
- Invoice item management
- Billing rules and calculations
- Invoice approval workflow
- Payment processing
- Billing reports and analytics

Supports Indonesian healthcare billing requirements including:
- BPJS INA-CBG (Indonesian Case Base Groups)
- Fee-for-service billing
- Tax calculations (PPN)
- Discount management
- Multi-payer support
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func as sql_func, update, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from decimal import Decimal
import json

# Models would be imported when they exist
# from app.models.billing import (
#     Invoice, InvoiceItem, BillingRule, InvoiceApproval,
#     Payment, PaymentAllocation, InvoiceStatus, PaymentStatus,
#     PaymentMethod, BillingRuleType, PayerType
# )
# from app.schemas.billing import (
#     InvoiceCreate, InvoiceUpdate, InvoiceItemCreate,
#     BillingRuleCreate, PaymentCreate
# )


# =============================================================================
# Invoice Management - Basic CRUD
# =============================================================================

async def get_invoice(
    db: AsyncSession,
    invoice_id: int,
) -> Optional[Any]:
    """
    Get invoice by ID with all relationships.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        Invoice object or None
    """
    # Placeholder - would use actual Invoice model
    # stmt = (
    #     select(Invoice)
    #     .options(
    #         selectinload(Invoice.items),
    #         selectinload(Invoice.patient),
    #         selectinload(Invoice.encounter),
    #         selectinload(Invoice.approvals),
    #         selectinload(Invoice.payments)
    #     )
    #     .where(Invoice.id == invoice_id)
    # )
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


async def get_invoice_by_number(
    db: AsyncSession,
    invoice_number: str,
) -> Optional[Any]:
    """
    Get invoice by invoice number.

    Args:
        db: Database session
        invoice_number: Unique invoice number

    Returns:
        Invoice object or None
    """
    # stmt = select(Invoice).where(Invoice.invoice_number == invoice_number)
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


async def get_invoices(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    encounter_id: Optional[int] = None,
    status: Optional[str] = None,
    payer_type: Optional[str] = None,
    invoice_date_from: Optional[date] = None,
    invoice_date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    List invoices with filtering and pagination.

    Args:
        db: Database session
        patient_id: Filter by patient
        encounter_id: Filter by encounter
        status: Filter by status (draft, pending, approved, paid, cancelled)
        payer_type: Filter by payer type (bpjs, commercial, self_pay)
        invoice_date_from: Filter by invoice date start
        invoice_date_to: Filter by invoice date end
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (list of invoices, total count)
    """
    # conditions = []
    # if patient_id:
    #     conditions.append(Invoice.patient_id == patient_id)
    # if encounter_id:
    #     conditions.append(Invoice.encounter_id == encounter_id)
    # if status:
    #     conditions.append(Invoice.status == status)
    # if payer_type:
    #     conditions.append(Invoice.payer_type == payer_type)
    # if invoice_date_from:
    #     conditions.append(Invoice.invoice_date >= invoice_date_from)
    # if invoice_date_to:
    #     conditions.append(Invoice.invoice_date <= invoice_date_to)

    # stmt = select(Invoice)
    # if conditions:
    #     stmt = stmt.where(and_(*conditions))

    # count_stmt = select(sql_func.count(Invoice.id))
    # if conditions:
    #     count_stmt = count_stmt.where(and_(*conditions))

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.options(selectinload(Invoice.items))
    # stmt = stmt.order_by(Invoice.created_at.desc())
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # invoices = result.scalars().all()

    # return list(invoices), total
    return [], 0


async def create_invoice(
    db: AsyncSession,
    invoice_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Create a new invoice.

    Args:
        db: Database session
        invoice_data: Invoice creation data
        created_by_id: User ID creating the invoice

    Returns:
        Created invoice object
    """
    # Generate invoice number
    invoice_number = await generate_invoice_number(db)

    # db_invoice = Invoice(
    #     invoice_number=invoice_number,
    #     patient_id=invoice_data.get('patient_id'),
    #     encounter_id=invoice_data.get('encounter_id'),
    #     payer_type=invoice_data.get('payer_type', 'self_pay'),
    #     insurance_id=invoice_data.get('insurance_id'),
    #     invoice_date=invoice_data.get('invoice_date', date.today()),
    #     due_date=invoice_data.get('due_date'),
    #     status='draft',
    #     notes=invoice_data.get('notes'),
    #     created_by_id=created_by_id,
    # )

    # db.add(db_invoice)
    # await db.flush()

    # # Add invoice items if provided
    # if 'items' in invoice_data:
    #     for item_data in invoice_data['items']:
    #         await add_invoice_item(db, db_invoice.id, item_data)

    # # Calculate totals
    # await calculate_invoice_totals(db, db_invoice.id)

    # await db.commit()
    # await db.refresh(db_invoice)

    # return db_invoice
    return None


async def update_invoice(
    db: AsyncSession,
    invoice_id: int,
    invoice_update: Dict[str, Any],
) -> Optional[Any]:
    """
    Update an existing invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID
        invoice_update: Update data

    Returns:
        Updated invoice or None
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     return None

    # # Only allow updates to draft invoices
    # if invoice.status != 'draft':
    #     raise ValueError("Can only update draft invoices")

    # for field, value in invoice_update.items():
    #     if field == 'items':
    #         continue  # Handle items separately
    #     if hasattr(invoice, field) and value is not None:
    #         setattr(invoice, field, value)

    # await db.commit()
    # await db.refresh(invoice)

    # return invoice
    return None


async def delete_invoice(
    db: AsyncSession,
    invoice_id: int,
) -> bool:
    """
    Delete a draft invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        True if deleted, False otherwise
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     return False

    # if invoice.status != 'draft':
    #     raise ValueError("Can only delete draft invoices")

    # await db.delete(invoice)
    # await db.commit()

    # return True
    return False


# =============================================================================
# Invoice Management - Patient and Encounter Queries
# =============================================================================

async def get_patient_invoices(
    db: AsyncSession,
    patient_id: int,
    status: Optional[str] = None,
    unpaid_only: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get all invoices for a specific patient.

    Args:
        db: Database session
        patient_id: Patient ID
        status: Optional status filter
        unpaid_only: Only show unpaid invoices
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (invoices, total count)
    """
    return await get_invoices(
        db=db,
        patient_id=patient_id,
        status=status,
        page=page,
        page_size=page_size,
    )


async def get_encounter_invoices(
    db: AsyncSession,
    encounter_id: int,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get all invoices for a specific encounter.

    Args:
        db: Database session
        encounter_id: Encounter ID
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (invoices, total count)
    """
    return await get_invoices(
        db=db,
        encounter_id=encounter_id,
        page=page,
        page_size=page_size,
    )


# =============================================================================
# Invoice Management - Status Queries
# =============================================================================

async def get_pending_invoices(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get invoices pending approval.

    Args:
        db: Database session
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (invoices, total count)
    """
    return await get_invoices(
        db=db,
        status='pending_approval',
        page=page,
        page_size=page_size,
    )


async def get_overdue_invoices(
    db: AsyncSession,
    as_of_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get overdue unpaid invoices.

    Args:
        db: Database session
        as_of_date: Check overdue as of this date (default: today)
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (invoices, total count)
    """
    # check_date = as_of_date or date.today()

    # stmt = select(Invoice).where(
    #     and_(
    #         Invoice.status.in_(['approved', 'partial_payment']),
    #         Invoice.due_date < check_date
    #     )
    # )

    # count_stmt = select(sql_func.count(Invoice.id)).where(
    #     and_(
    #         Invoice.status.in_(['approved', 'partial_payment']),
    #         Invoice.due_date < check_date
    #     )
    # )

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.options(selectinload(Invoice.items))
    # stmt = stmt.order_by(Invoice.due_date.asc())
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # invoices = result.scalars().all()

    # return list(invoices), total
    return [], 0


async def get_unpaid_invoices(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get unpaid invoices.

    Args:
        db: Database session
        patient_id: Optional patient filter
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (invoices, total count)
    """
    return await get_invoices(
        db=db,
        patient_id=patient_id,
        status='approved',
        page=page,
        page_size=page_size,
    )


async def get_paid_invoices(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get fully paid invoices.

    Args:
        db: Database session
        patient_id: Optional patient filter
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (invoices, total count)
    """
    return await get_invoices(
        db=db,
        patient_id=patient_id,
        status='paid',
        page=page,
        page_size=page_size,
    )


# =============================================================================
# Invoice Number and Totals
# =============================================================================

async def generate_invoice_number(db: AsyncSession) -> str:
    """
    Generate a unique invoice number.
    Format: INV-YYYY-XXXXX (sequential per year)

    Args:
        db: Database session

    Returns:
        Unique invoice number
    """
    # year = datetime.now().year
    # pattern = f"INV-{year}-%"

    # stmt = select(sql_func.max(Invoice.invoice_number)).filter(
    #     Invoice.invoice_number.like(pattern)
    # )
    # result = await db.execute(stmt)
    # last_number = result.scalar()

    # if last_number:
    #     last_sequence = int(last_number.split('-')[-1])
    #     new_sequence = last_sequence + 1
    # else:
    #     new_sequence = 1

    # return f"INV-{year}-{new_sequence:05d}"
    return f"INV-{datetime.now().year}-00001"


async def calculate_invoice_totals(
    db: AsyncSession,
    invoice_id: int,
) -> Dict[str, Decimal]:
    """
    Recalculate invoice totals from items.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        Dictionary with totals (subtotal, tax, discount, total)
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # # Get all invoice items
    # stmt = select(InvoiceItem).where(InvoiceItem.invoice_id == invoice_id)
    # result = await db.execute(stmt)
    # items = result.scalars().all()

    # # Calculate subtotal
    # subtotal = Decimal('0.00')
    # for item in items:
    #     item_total = item.quantity * item.unit_price
    #     subtotal += item_total

    # # Calculate tax
    # tax_rate = invoice.tax_rate or Decimal('0.11')  # Default 11% PPN
    # tax_amount = subtotal * tax_rate

    # # Calculate discount
    # discount_amount = Decimal('0.00')
    # if invoice.discount_type == 'percentage':
    #     discount_amount = subtotal * (invoice.discount_value or Decimal('0')) / Decimal('100')
    # elif invoice.discount_type == 'fixed':
    #     discount_amount = invoice.discount_value or Decimal('0')

    # # Calculate total
    # total = subtotal + tax_amount - discount_amount

    # # Update invoice
    # invoice.subtotal = subtotal
    # invoice.tax_amount = tax_amount
    # invoice.discount_amount = discount_amount
    # invoice.total_amount = total
    # invoice.balance_due = total - (invoice.amount_paid or Decimal('0'))

    # await db.commit()

    # return {
    #     'subtotal': subtotal,
    #     'tax_amount': tax_amount,
    #     'discount_amount': discount_amount,
    #     'total': total,
    #     'balance_due': invoice.balance_due
    # }

    return {
        'subtotal': Decimal('0.00'),
        'tax_amount': Decimal('0.00'),
        'discount_amount': Decimal('0.00'),
        'total': Decimal('0.00'),
        'balance_due': Decimal('0.00'),
    }


# =============================================================================
# Billing Rules and Calculations
# =============================================================================

async def get_billing_rule(
    db: AsyncSession,
    rule_id: int,
) -> Optional[Any]:
    """
    Get billing rule by ID.

    Args:
        db: Database session
        rule_id: Rule ID

    Returns:
        Billing rule or None
    """
    # stmt = select(BillingRule).where(BillingRule.id == rule_id)
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None


async def get_billing_rules(
    db: AsyncSession,
    rule_type: Optional[str] = None,
    is_active: bool = True,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get billing rules with filtering.

    Args:
        db: Database session
        rule_type: Filter by rule type
        is_active: Only active rules
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (rules, total count)
    """
    # conditions = [BillingRule.is_active == is_active]

    # if rule_type:
    #     conditions.append(BillingRule.rule_type == rule_type)

    # stmt = select(BillingRule).where(and_(*conditions))
    # count_stmt = select(sql_func.count(BillingRule.id)).where(and_(*conditions))

    # count_result = await db.execute(count_stmt)
    # total = count_result.scalar_one()

    # stmt = stmt.order_by(BillingRule.created_at.desc())
    # stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    # result = await db.execute(stmt)
    # rules = result.scalars().all()

    # return list(rules), total
    return [], 0


async def create_billing_rule(
    db: AsyncSession,
    rule_data: Dict[str, Any],
) -> Any:
    """
    Create a new billing rule.

    Args:
        db: Database session
        rule_data: Rule creation data

    Returns:
        Created billing rule
    """
    # db_rule = BillingRule(
    #     rule_name=rule_data['rule_name'],
    #     rule_type=rule_data['rule_type'],
    #     description=rule_data.get('description'),
    #     conditions=rule_data.get('conditions', {}),
    #     actions=rule_data.get('actions', {}),
    #     priority=rule_data.get('priority', 0),
    #     is_active=rule_data.get('is_active', True),
    #     effective_from=rule_data.get('effective_from'),
    #     effective_to=rule_data.get('effective_to'),
    # )

    # db.add(db_rule)
    # await db.commit()
    # await db.refresh(db_rule)

    # return db_rule
    return None


async def apply_billing_rules(
    db: AsyncSession,
    invoice_id: int,
) -> Dict[str, Any]:
    """
    Apply applicable billing rules to an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        Dictionary with applied rules and adjustments
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # # Get applicable rules
    # applicable_rules = await get_applicable_rules(db, invoice)

    # applied_rules = []
    # adjustments = Decimal('0.00')

    # for rule in applicable_rules:
    #     # Apply rule logic
    #     rule_result = await _apply_single_rule(db, invoice, rule)
    #     if rule_result['applied']:
    #         applied_rules.append(rule_result)
    #         adjustments += rule_result.get('adjustment', Decimal('0.00'))

    # # Recalculate totals with adjustments
    # await calculate_invoice_totals(db, invoice_id)

    # return {
    #     'applied_rules': applied_rules,
    #     'total_adjustment': adjustments,
    #     'rules_count': len(applied_rules)
    # }

    return {
        'applied_rules': [],
        'total_adjustment': Decimal('0.00'),
        'rules_count': 0
    }


async def apply_billing_rules_to_invoice(
    db: AsyncSession,
    invoice_id: int,
    rule_ids: List[int],
) -> Dict[str, Any]:
    """
    Apply specific billing rules to an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID
        rule_ids: List of rule IDs to apply

    Returns:
        Dictionary with applied rules and adjustments
    """
    return await apply_billing_rules(db, invoice_id)


async def get_applicable_rules(
    db: AsyncSession,
    invoice: Any,
) -> List[Any]:
    """
    Get billing rules applicable to an invoice.

    Args:
        db: Database session
        invoice: Invoice object

    Returns:
        List of applicable billing rules
    """
    # Get all active rules and filter by conditions
    # stmt = select(BillingRule).where(
    #     and_(
    #         BillingRule.is_active == True,
    #         or_(
    #             BillingRule.effective_from.is_(None),
    #             BillingRule.effective_from <= date.today()
    #         ),
    #         or_(
    #             BillingRule.effective_to.is_(None),
    #             BillingRule.effective_to >= date.today()
    #         )
    #     )
    # ).order_by(BillingRule.priority.desc())

    # result = await db.execute(stmt)
    # rules = result.scalars().all()

    # # Filter rules based on conditions
    # applicable = []
    # for rule in rules:
    #     if await _evaluate_rule_conditions(db, invoice, rule):
    #         applicable.append(rule)

    # return applicable
    return []


async def calculate_tax(
    db: AsyncSession,
    invoice_id: int,
) -> Decimal:
    """
    Calculate tax for an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        Tax amount
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # tax_rate = invoice.tax_rate or Decimal('0.11')  # 11% PPN Indonesia
    # return invoice.subtotal * tax_rate
    return Decimal('0.00')


async def apply_discount(
    db: AsyncSession,
    invoice_id: int,
    discount_type: str,
    discount_value: Decimal,
    reason: Optional[str] = None,
) -> Dict[str, Decimal]:
    """
    Apply discount to an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID
        discount_type: Type ('percentage' or 'fixed')
        discount_value: Discount value
        reason: Discount reason

    Returns:
        Updated totals
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # invoice.discount_type = discount_type
    # invoice.discount_value = discount_value
    # invoice.discount_reason = reason

    # # Recalculate totals
    # totals = await calculate_invoice_totals(db, invoice_id)

    # await db.commit()

    # return totals
    return await calculate_invoice_totals(db, invoice_id)


# =============================================================================
# BPJS and Fee-for-Service Calculations
# =============================================================================

async def calculate_bpjs_ina_cbg(
    db: AsyncSession,
    invoice_id: int,
    cbg_code: str,
) -> Dict[str, Any]:
    """
    Calculate BPJS INA-CBG (Indonesian Case Base Groups) billing.

    Args:
        db: Database session
        invoice_id: Invoice ID
        cbg_code: INA-CBG procedure code

    Returns:
        Dictionary with CBG calculation details
    """
    # Look up CBG rate
    # cbg_rate = await _get_cbg_rate(db, cbg_code)

    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # # BPJS pays the CBG rate regardless of actual charges
    # invoice.billing_type = 'bpjs_ina_cbg'
    # invoice.cbg_code = cbg_code
    # invoice.cbg_rate = cbg_rate

    # # Update total
    # invoice.total_amount = cbg_rate
    # invoice.balance_due = cbg_rate - (invoice.amount_paid or Decimal('0'))

    # await db.commit()

    # return {
    #     'cbg_code': cbg_code,
    #     'cbg_rate': cbg_rate,
    #     'description': 'BPJS INA-CBG Package Rate',
    #     'patient_responsibility': Decimal('0.00'),  # Full coverage
    # }

    return {
        'cbg_code': cbg_code,
        'cbg_rate': Decimal('0.00'),
        'description': 'BPJS INA-CBG Package Rate',
        'patient_responsibility': Decimal('0.00'),
    }


async def calculate_fee_for_service(
    db: AsyncSession,
    invoice_id: int,
) -> Dict[str, Any]:
    """
    Calculate fee-for-service billing (itemized charges).

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        Dictionary with fee-for-service details
    """
    # Calculate from actual items
    totals = await calculate_invoice_totals(db, invoice_id)

    # invoice = await get_invoice(db, invoice_id)
    # if invoice:
    #     invoice.billing_type = 'fee_for_service'
    #     await db.commit()

    return {
        'billing_type': 'fee_for_service',
        'subtotal': totals['subtotal'],
        'tax': totals['tax_amount'],
        'discount': totals['discount_amount'],
        'total': totals['total'],
        'item_count': 0,  # Would count actual items
    }


# =============================================================================
# Invoice Items
# =============================================================================

async def add_invoice_item(
    db: AsyncSession,
    invoice_id: int,
    item_data: Dict[str, Any],
) -> Any:
    """
    Add an item to an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID
        item_data: Item data (description, quantity, unit_price, etc.)

    Returns:
        Created invoice item
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # if invoice.status != 'draft':
    #     raise ValueError("Can only add items to draft invoices")

    # db_item = InvoiceItem(
    #     invoice_id=invoice_id,
    #     item_type=item_data.get('item_type', 'service'),
    #     description=item_data['description'],
    #     quantity=item_data.get('quantity', 1),
    #     unit_price=item_data['unit_price'],
    #     service_code=item_data.get('service_code'),
    #     service_date=item_data.get('service_date'),
    #     provider_id=item_data.get('provider_id'),
    # )

    # db.add(db_item)
    # await db.flush()

    # # Recalculate invoice totals
    # await calculate_invoice_totals(db, invoice_id)

    # await db.commit()
    # await db.refresh(db_item)

    # return db_item
    return None


async def update_invoice_item(
    db: AsyncSession,
    item_id: int,
    item_update: Dict[str, Any],
) -> Optional[Any]:
    """
    Update an invoice item.

    Args:
        db: Database session
        item_id: Item ID
        item_update: Update data

    Returns:
        Updated item or None
    """
    # stmt = select(InvoiceItem).where(InvoiceItem.id == item_id)
    # result = await db.execute(stmt)
    # item = result.scalar_one_or_none()

    # if not item:
    #     return None

    # # Check if invoice is still draft
    # invoice = await get_invoice(db, item.invoice_id)
    # if invoice.status != 'draft':
    #     raise ValueError("Can only update items in draft invoices")

    # for field, value in item_update.items():
    #     if hasattr(item, field) and value is not None:
    #         setattr(item, field, value)

    # await db.commit()
    # await db.refresh(item)

    # # Recalculate invoice totals
    # await calculate_invoice_totals(db, item.invoice_id)

    # return item
    return None


async def remove_invoice_item(
    db: AsyncSession,
    item_id: int,
) -> bool:
    """
    Remove an invoice item.

    Args:
        db: Database session
        item_id: Item ID

    Returns:
        True if removed
    """
    # stmt = select(InvoiceItem).where(InvoiceItem.id == item_id)
    # result = await db.execute(stmt)
    # item = result.scalar_one_or_none()

    # if not item:
    #     return False

    # invoice_id = item.invoice_id

    # # Check if invoice is still draft
    # invoice = await get_invoice(db, invoice_id)
    # if invoice.status != 'draft':
    #     raise ValueError("Can only remove items from draft invoices")

    # await db.delete(item)
    # await db.commit()

    # # Recalculate invoice totals
    # await calculate_invoice_totals(db, invoice_id)

    # return True
    return False


async def get_invoice_items(
    db: AsyncSession,
    invoice_id: int,
) -> List[Any]:
    """
    Get all items for an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        List of invoice items
    """
    # stmt = select(InvoiceItem).where(
    #     InvoiceItem.invoice_id == invoice_id
    # ).order_by(InvoiceItem.created_at)

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def recalculate_invoice_totals(
    db: AsyncSession,
    invoice_id: int,
) -> Dict[str, Decimal]:
    """
    Recalculate invoice totals from items.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        Updated totals
    """
    return await calculate_invoice_totals(db, invoice_id)


# =============================================================================
# Invoice Approvals
# =============================================================================

async def submit_for_approval(
    db: AsyncSession,
    invoice_id: int,
    submitted_by_id: int,
    notes: Optional[str] = None,
) -> Any:
    """
    Submit invoice for approval.

    Args:
        db: Database session
        invoice_id: Invoice ID
        submitted_by_id: User submitting
        notes: Optional notes

    Returns:
        Updated invoice
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # if invoice.status != 'draft':
    #     raise ValueError("Can only submit draft invoices for approval")

    # invoice.status = 'pending_approval'
    # invoice.submitted_for_approval_at = datetime.utcnow()

    # # Create approval record
    # approval = InvoiceApproval(
    #     invoice_id=invoice_id,
    #     action='submitted',
    #     actor_id=submitted_by_id,
    #     notes=notes,
    #     action_date=datetime.utcnow(),
    # )

    # db.add(approval)
    # await db.commit()
    # await db.refresh(invoice)

    # return invoice
    return None


async def approve_invoice(
    db: AsyncSession,
    invoice_id: int,
    approved_by_id: int,
    approver_name: str,
    notes: Optional[str] = None,
) -> Any:
    """
    Approve an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID
        approved_by_id: Approver user ID
        approver_name: Approver name
        notes: Optional notes

    Returns:
        Updated invoice
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # if invoice.status != 'pending_approval':
    #     raise ValueError("Invoice is not pending approval")

    # invoice.status = 'approved'
    # invoice.approved_at = datetime.utcnow()
    # invoice.approved_by_id = approved_by_id

    # # Create approval record
    # approval = InvoiceApproval(
    #     invoice_id=invoice_id,
    #     action='approved',
    #     actor_id=approved_by_id,
    #     actor_name=approver_name,
    #     notes=notes,
    #     action_date=datetime.utcnow(),
    # )

    # db.add(approval)
    # await db.commit()
    # await db.refresh(invoice)

    # return invoice
    return None


async def reject_invoice(
    db: AsyncSession,
    invoice_id: int,
    rejected_by_id: int,
    rejecter_name: str,
    reason: str,
) -> Any:
    """
    Reject an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID
        rejected_by_id: Rejecter user ID
        rejecter_name: Rejecter name
        reason: Rejection reason

    Returns:
        Updated invoice
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # if invoice.status != 'pending_approval':
    #     raise ValueError("Invoice is not pending approval")

    # invoice.status = 'rejected'
    # invoice.rejected_at = datetime.utcnow()
    # invoice.rejection_reason = reason

    # # Create approval record
    # approval = InvoiceApproval(
    #     invoice_id=invoice_id,
    #     action='rejected',
    #     actor_id=rejected_by_id,
    #     actor_name=rejecter_name,
    #     notes=reason,
    #     action_date=datetime.utcnow(),
    # )

    # db.add(approval)
    # await db.commit()
    # await db.refresh(invoice)

    # return invoice
    return None


async def get_pending_approvals(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Any], int]:
    """
    Get invoices pending approval.

    Args:
        db: Database session
        page: Page number
        page_size: Items per page

    Returns:
        Tuple of (invoices, total count)
    """
    return await get_pending_invoices(db, page, page_size)


async def get_approval_history(
    db: AsyncSession,
    invoice_id: int,
) -> List[Any]:
    """
    Get approval history for an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        List of approval actions
    """
    # stmt = select(InvoiceApproval).where(
    #     InvoiceApproval.invoice_id == invoice_id
    # ).order_by(InvoiceApproval.action_date.desc())

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


# =============================================================================
# Payments
# =============================================================================

async def create_payment(
    db: AsyncSession,
    payment_data: Dict[str, Any],
    created_by_id: int,
) -> Any:
    """
    Create a payment record.

    Args:
        db: Database session
        payment_data: Payment data
        created_by_id: User creating payment

    Returns:
        Created payment
    """
    # Generate payment reference
    # payment_ref = await _generate_payment_reference(db)

    # db_payment = Payment(
    #     payment_reference=payment_ref,
    #     patient_id=payment_data['patient_id'],
    #     payment_method=payment_data['payment_method'],
    #     amount=payment_data['amount'],
    #     payment_date=payment_data.get('payment_date', datetime.utcnow()),
    #     reference_number=payment_data.get('reference_number'),
    #     notes=payment_data.get('notes'),
    #     status='pending',
    #     created_by_id=created_by_id,
    # )

    # db.add(db_payment)
    # await db.commit()
    # await db.refresh(db_payment)

    # # If invoice_id provided, apply payment
    # if 'invoice_id' in payment_data:
    #     await apply_payment_to_invoice(
    #         db=db,
    #         payment_id=db_payment.id,
    #         invoice_id=payment_data['invoice_id'],
    #         amount=payment_data['amount']
    #     )

    # return db_payment
    return None


async def get_invoice_payments(
    db: AsyncSession,
    invoice_id: int,
) -> List[Any]:
    """
    Get all payments for an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        List of payments
    """
    # stmt = select(Payment).join(
    #     PaymentAllocation,
    #     Payment.id == PaymentAllocation.payment_id
    # ).where(
    #     PaymentAllocation.invoice_id == invoice_id
    # ).order_by(Payment.payment_date.desc())

    # result = await db.execute(stmt)
    # return list(result.scalars().all())
    return []


async def process_payment(
    db: AsyncSession,
    payment_id: int,
) -> Any:
    """
    Process a pending payment.

    Args:
        db: Database session
        payment_id: Payment ID

    Returns:
        Updated payment
    """
    # payment = await get_payment(db, payment_id)
    # if not payment:
    #     raise ValueError("Payment not found")

    # if payment.status != 'pending':
    #     raise ValueError("Payment is not in pending status")

    # # Simulate payment processing
    # payment.status = 'completed'
    # payment.processed_at = datetime.utcnow()

    # await db.commit()
    # await db.refresh(payment)

    # return payment
    return None


async def apply_payment_to_invoice(
    db: AsyncSession,
    payment_id: int,
    invoice_id: int,
    amount: Decimal,
) -> Any:
    """
    Apply payment to an invoice.

    Args:
        db: Database session
        payment_id: Payment ID
        invoice_id: Invoice ID
        amount: Amount to apply

    Returns:
        Payment allocation record
    """
    # payment = await get_payment(db, payment_id)
    # invoice = await get_invoice(db, invoice_id)

    # if not payment or not invoice:
    #     raise ValueError("Payment or invoice not found")

    # # Create allocation
    # allocation = PaymentAllocation(
    #     payment_id=payment_id,
    #     invoice_id=invoice_id,
    #     amount=amount,
    #     allocated_at=datetime.utcnow(),
    # )

    # db.add(allocation)

    # # Update invoice
    # invoice.amount_paid = (invoice.amount_paid or Decimal('0')) + amount
    # invoice.balance_due = invoice.total_amount - invoice.amount_paid

    # # Update invoice status if fully paid
    # if invoice.balance_due <= 0:
    #     invoice.status = 'paid'
    #     invoice.paid_in_full_at = datetime.utcnow()
    # elif invoice.amount_paid > 0:
    #     invoice.status = 'partial_payment'

    # await db.commit()
    # await db.refresh(allocation)

    # return allocation
    return None


async def get_payment_status(
    db: AsyncSession,
    invoice_id: int,
) -> Dict[str, Any]:
    """
    Get payment status for an invoice.

    Args:
        db: Database session
        invoice_id: Invoice ID

    Returns:
        Payment status details
    """
    # invoice = await get_invoice(db, invoice_id)
    # if not invoice:
    #     raise ValueError("Invoice not found")

    # payments = await get_invoice_payments(db, invoice_id)
    # total_paid = sum(p.amount for p in payments)

    # return {
    #     'invoice_id': invoice_id,
    #     'total_amount': invoice.total_amount,
    #     'amount_paid': total_paid,
    #     'balance_due': invoice.total_amount - total_paid,
    #     'status': invoice.status,
    #     'payment_count': len(payments),
    #     'last_payment_date': payments[0].payment_date if payments else None,
    # }

    return {
        'invoice_id': invoice_id,
        'total_amount': Decimal('0.00'),
        'amount_paid': Decimal('0.00'),
        'balance_due': Decimal('0.00'),
        'status': 'unknown',
        'payment_count': 0,
        'last_payment_date': None,
    }


# =============================================================================
# Reporting
# =============================================================================

async def get_revenue_report(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    payer_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate revenue report for a date range.

    Args:
        db: Database session
        start_date: Report start date
        end_date: Report end date
        department_id: Optional department filter
        payer_type: Optional payer type filter

    Returns:
        Revenue report data
    """
    # stmt = select(
    #     sql_func.date(Invoice.invoice_date).label('date'),
    #     sql_func.sum(Invoice.total_amount).label('total_billed'),
    #     sql_func.sum(Invoice.amount_paid).label('total_collected'),
    #     sql_func.count(Invoice.id).label('invoice_count'),
    # ).where(
    #     and_(
    #         Invoice.invoice_date >= start_date,
    #         Invoice.invoice_date <= end_date,
    #     )
    # )

    # if department_id:
    #     stmt = stmt.where(Invoice.department_id == department_id)
    # if payer_type:
    #     stmt = stmt.where(Invoice.payer_type == payer_type)

    # stmt = stmt.group_by(sql_func.date(Invoice.invoice_date))
    # stmt = stmt.order_by(sql_func.date(Invoice.invoice_date))

    # result = await db.execute(stmt)
    # daily_data = result.all()

    # # Calculate totals
    # total_billed = sum(row.total_billed or Decimal('0') for row in daily_data)
    # total_collected = sum(row.total_collected or Decimal('0') for row in daily_data)
    # total_invoices = sum(row.invoice_count for row in daily_data)
    # collection_rate = (total_collected / total_billed * 100) if total_billed > 0 else Decimal('0')

    # return {
    #     'start_date': start_date,
    #     'end_date': end_date,
    #     'total_billed': total_billed,
    #     'total_collected': total_collected,
    #     'total_invoices': total_invoices,
    #     'collection_rate': collection_rate,
    #     'outstanding': total_billed - total_collected,
    #     'daily_breakdown': [
    #         {
    #             'date': str(row.date),
    #             'billed': row.total_billed,
    #             'collected': row.total_collected,
    #             'count': row.invoice_count,
    #         }
    #         for row in daily_data
    #     ],
    # }

    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_billed': Decimal('0.00'),
        'total_collected': Decimal('0.00'),
        'total_invoices': 0,
        'collection_rate': Decimal('0.00'),
        'outstanding': Decimal('0.00'),
        'daily_breakdown': [],
    }


async def get_aging_report(
    db: AsyncSession,
    as_of_date: Optional[date] = None,
    patient_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate accounts receivable aging report.

    Args:
        db: Database session
        as_of_date: Report date (default: today)
        patient_id: Optional patient filter

    Returns:
        Aging report data
    """
    # report_date = as_of_date or date.today()

    # # Define aging buckets
    # buckets = {
    #     '0_30': 0,
    #     '31_60': 0,
    #     '61_90': 0,
    #     '91_plus': 0,
    # }

    # stmt = select(Invoice).where(
    #     and_(
    #         Invoice.status.in_(['approved', 'partial_payment']),
    #         Invoice.balance_due > 0
    #     )
    # )

    # if patient_id:
    #     stmt = stmt.where(Invoice.patient_id == patient_id)

    # result = await db.execute(stmt)
    # invoices = result.scalars().all()

    # aging_details = []
    # total_outstanding = Decimal('0.00')

    # for invoice in invoices:
    #     days_overdue = (report_date - invoice.due_date).days

    #     if days_overdue <= 30:
    #         bucket = '0_30'
    #     elif days_overdue <= 60:
    #         bucket = '31_60'
    #     elif days_overdue <= 90:
    #         bucket = '61_90'
    #     else:
    #         bucket = '91_plus'

    #     buckets[bucket] += invoice.balance_due
    #     total_outstanding += invoice.balance_due

    #     aging_details.append({
    #         'invoice_id': invoice.id,
    #         'invoice_number': invoice.invoice_number,
    #         'patient_id': invoice.patient_id,
    #         'due_date': invoice.due_date,
    #         'days_overdue': days_overdue,
    #         'balance_due': invoice.balance_due,
    #         'bucket': bucket,
    #     })

    # return {
    #     'as_of_date': report_date,
    #     'total_outstanding': total_outstanding,
    #     'aging_buckets': buckets,
    #     'invoice_count': len(invoices),
    #     'details': aging_details,
    # }

    return {
        'as_of_date': as_of_date or date.today(),
        'total_outstanding': Decimal('0.00'),
        'aging_buckets': {
            '0_30': Decimal('0.00'),
            '31_60': Decimal('0.00'),
            '61_90': Decimal('0.00'),
            '91_plus': Decimal('0.00'),
        },
        'invoice_count': 0,
        'details': [],
    }


async def get_payer_summary(
    db: AsyncSession,
    start_date: date,
    end_date: date,
) -> List[Dict[str, Any]]:
    """
    Generate summary by payer type.

    Args:
        db: Database session
        start_date: Start date
        end_date: End date

    Returns:
        List of payer summaries
    """
    # stmt = select(
    #     Invoice.payer_type,
    #     sql_func.count(Invoice.id).label('invoice_count'),
    #     sql_func.sum(Invoice.total_amount).label('total_billed'),
    #     sql_func.sum(Invoice.amount_paid).label('total_collected'),
    # ).where(
    #     and_(
    #         Invoice.invoice_date >= start_date,
    #         Invoice.invoice_date <= end_date,
    #     )
    # ).group_by(Invoice.payer_type)

    # result = await db.execute(stmt)
    # rows = result.all()

    # return [
    #     {
    #         'payer_type': row.payer_type,
    #         'invoice_count': row.invoice_count,
    #         'total_billed': row.total_billed or Decimal('0'),
    #         'total_collected': row.total_collected or Decimal('0'),
    #         'outstanding': (row.total_billed or Decimal('0')) - (row.total_collected or Decimal('0')),
    #     }
    #     for row in rows
    # ]

    return []


# =============================================================================
# Helper Functions
# =============================================================================

async def _apply_single_rule(
    db: AsyncSession,
    invoice: Any,
    rule: Any,
) -> Dict[str, Any]:
    """Apply a single billing rule to an invoice."""
    # Implementation would evaluate rule conditions and apply actions
    return {
        'rule_id': 0,
        'rule_name': 'placeholder',
        'applied': False,
        'adjustment': Decimal('0.00'),
    }


async def _evaluate_rule_conditions(
    db: AsyncSession,
    invoice: Any,
    rule: Any,
) -> bool:
    """Evaluate if rule conditions match invoice."""
    # Implementation would check rule conditions against invoice
    return False


async def _get_cbg_rate(
    db: AsyncSession,
    cbg_code: str,
) -> Decimal:
    """Look up CBG rate for a code."""
    # Implementation would query CBG rate table
    return Decimal('0.00')


async def _generate_payment_reference(db: AsyncSession) -> str:
    """Generate unique payment reference number."""
    # Format: PAY-YYYY-XXXXX
    year = datetime.now().year
    return f"PAY-{year}-00001"


async def get_payment(
    db: AsyncSession,
    payment_id: int,
) -> Optional[Any]:
    """Get payment by ID."""
    # stmt = select(Payment).where(Payment.id == payment_id)
    # result = await db.execute(stmt)
    # return result.scalar_one_or_none()
    return None
