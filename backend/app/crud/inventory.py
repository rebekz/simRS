"""Pharmacy Inventory CRUD operations for STORY-024: Pharmacy Inventory Management

This module provides CRUD operations for drug master file, inventory tracking,
stock transactions, and purchase orders.
"""
from datetime import datetime, date, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy import select, and_, desc, func, case, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory import (
    Drug, DrugBatch, Supplier, StockTransaction, StockTransactionItem,
    PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem, NearExpiryAlert,
)
from app.schemas.inventory import (
    DrugCreate, DrugUpdate, DrugResponse,
    DrugBatchCreate, DrugBatchResponse,
    StockTransactionCreate, StockTransactionResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse,
    PurchaseOrderCreate, PurchaseOrderResponse,
    InventorySummary, InventoryAlert, StockLevelResponse,
    DrugSearchQuery, StockMovementQuery,
)


# =============================================================================
# Drug Master CRUD
# =============================================================================

async def get_drug(
    db: AsyncSession,
    drug_id: int,
) -> Optional[Drug]:
    """Get drug by ID."""
    stmt = select(Drug).where(Drug.id == drug_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_drug_by_code(
    db: AsyncSession,
    drug_code: str,
) -> Optional[Drug]:
    """Get drug by drug code."""
    stmt = select(Drug).where(Drug.drug_code == drug_code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_drugs(
    db: AsyncSession,
    search: Optional[str] = None,
    dosage_form: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Drug], int]:
    """
    List drugs with filtering and pagination.

    Returns:
        Tuple of (list of drugs, total count)
    """
    # Build conditions
    conditions = []

    if search:
        conditions.append(
            (Drug.generic_name.ilike(f"%{search}%")) |
            (Drug.drug_code.ilike(f"%{search}%"))
        )

    if dosage_form:
        conditions.append(Drug.dosage_form == dosage_form)

    if is_active is not None:
        conditions.append(Drug.is_active == is_active)

    # Count query
    count_stmt = select(func.count(Drug.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    # Data query
    offset = (page - 1) * page_size
    data_stmt = select(Drug)
    if conditions:
        data_stmt = data_stmt.where(and_(*conditions))
    data_stmt = data_stmt.order_by(Drug.generic_name).offset(offset).limit(page_size)
    data_result = await db.execute(data_stmt)
    drugs = list(data_result.scalars().all())

    return drugs, total


async def create_drug(
    db: AsyncSession,
    drug_data: DrugCreate,
    user_id: Optional[int] = None,
) -> Drug:
    """Create a new drug."""
    drug = Drug(
        **drug_data.model_dump(),
        created_by=user_id,
    )

    db.add(drug)
    await db.commit()
    await db.refresh(drug)

    return drug


async def update_drug(
    db: AsyncSession,
    drug_id: int,
    drug_data: DrugUpdate,
    user_id: Optional[int] = None,
) -> Optional[Drug]:
    """Update an existing drug."""
    drug = await get_drug(db, drug_id)
    if not drug:
        return None

    # Update fields
    update_data = drug_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(drug, field, value)

    drug.updated_by = user_id
    drug.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(drug)

    return drug


async def get_current_stock(
    db: AsyncSession,
    drug_id: int,
) -> int:
    """Get current stock level for a drug."""
    stmt = select(func.sum(DrugBatch.quantity)).where(
        and_(
            DrugBatch.drug_id == drug_id,
            DrugBatch.is_quarantined == False,
            DrugBatch.expiry_date >= date.today(),
        )
    )
    result = await db.execute(stmt)
    stock = result.scalar()
    return stock or 0


# =============================================================================
# Drug Batch CRUD
# =============================================================================

async def get_batches_by_drug(
    db: AsyncSession,
    drug_id: int,
    include_quarantined: bool = False,
) -> List[DrugBatch]:
    """Get all batches for a drug."""
    conditions = [DrugBatch.drug_id == drug_id]

    if not include_quarantined:
        conditions.append(DrugBatch.is_quarantined == False)

    stmt = select(DrugBatch).where(
        and_(*conditions)
    ).order_by(DrugBatch.expiry_date)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_fefo_batch(
    db: AsyncSession,
    drug_id: int,
    quantity: int,
) -> Optional[DrugBatch]:
    """
    Get First-Expired-First-Out (FEFO) batch for dispensing.

    Returns the batch with earliest expiry date that has sufficient quantity.
    """
    stmt = select(DrugBatch).where(
        and_(
            DrugBatch.drug_id == drug_id,
            DrugBatch.is_quarantined == False,
            DrugBatch.expiry_date > date.today(),
            DrugBatch.quantity >= quantity,
        )
    ).order_by(DrugBatch.expiry_date).limit(1)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_batch(
    db: AsyncSession,
    batch_data: DrugBatchCreate,
    user_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
) -> DrugBatch:
    """Create a new drug batch."""
    batch = DrugBatch(
        **batch_data.model_dump(),
        initial_quantity=batch_data.quantity,
        received_date=date.today(),
        received_by=user_id,
        supplier_id=supplier_id,
    )

    db.add(batch)
    await db.commit()
    await db.refresh(batch)

    return batch


# =============================================================================
# Near Expiry Alerting
# =============================================================================

async def get_near_expiry_batches(
    db: AsyncSession,
    days_threshold: int = 90,
) -> List[Dict[str, Any]]:
    """Get batches expiring within the threshold."""
    threshold_date = date.today() + timedelta(days=days_threshold)

    # Get drugs and batches near expiry
    stmt = select(
        Drug.id,
        Drug.generic_name,
        Drug.drug_code,
        DrugBatch.id.label('batch_id'),
        DrugBatch.batch_number,
        DrugBatch.expiry_date,
        DrugBatch.quantity,
        (DrugBatch.expiry_date - date.today()).label('days_to_expiry'),
    ).join(
        DrugBatch, Drug.id == DrugBatch.drug_id
    ).where(
        and_(
            Drug.is_active == True,
            DrugBatch.is_quarantined == False,
            DrugBatch.quantity > 0,
            DrugBatch.expiry_date <= threshold_date,
            DrugBatch.expiry_date > date.today(),
        )
    ).order_by(DrugBatch.expiry_date)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            'drug_id': row.id,
            'drug_name': row.generic_name,
            'drug_code': row.drug_code,
            'batch_id': row.batch_id,
            'batch_number': row.batch_number,
            'expiry_date': row.expiry_date,
            'quantity': row.quantity,
            'days_to_expiry': row.days_to_expiry,
        }
        for row in rows
    ]


async def get_expired_batches(
    db: AsyncSession,
) -> List[Dict[str, Any]]:
    """Get expired batches."""
    stmt = select(
        Drug.id,
        Drug.generic_name,
        Drug.drug_code,
        DrugBatch.id.label('batch_id'),
        DrugBatch.batch_number,
        DrugBatch.expiry_date,
        DrugBatch.quantity,
    ).join(
        DrugBatch, Drug.id == DrugBatch.drug_id
    ).where(
        and_(
            DrugBatch.expiry_date < date.today(),
            DrugBatch.quantity > 0,
        )
    ).order_by(DrugBatch.expiry_date)

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            'drug_id': row.id,
            'drug_name': row.generic_name,
            'drug_code': row.drug_code,
            'batch_id': row.batch_id,
            'batch_number': row.batch_number,
            'expiry_date': row.expiry_date,
            'quantity': row.quantity,
        }
        for row in rows
    ]


# =============================================================================
# Low Stock Alerts
# =============================================================================

async def get_low_stock_drugs(
    db: AsyncSession,
) -> List[Dict[str, Any]]:
    """Get drugs below minimum stock level."""
    stmt = select(
        Drug.id,
        Drug.generic_name,
        Drug.drug_code,
        Drug.min_stock_level,
        Drug.reorder_point,
        func.coalesce(func.sum(
            case(
                (and_(
                    DrugBatch.is_quarantined == False,
                    DrugBatch.expiry_date >= date.today(),
                ), DrugBatch.quantity),
                else_=0
            )
        ), 0).label('current_stock'),
    ).outerjoin(
        DrugBatch, Drug.id == DrugBatch.drug_id
    ).where(
        Drug.is_active == True
    ).group_by(
        Drug.id, Drug.generic_name, Drug.drug_code, Drug.min_stock_level, Drug.reorder_point
    ).having(
        func.coalesce(func.sum(
            case(
                (and_(
                    DrugBatch.is_quarantined == False,
                    DrugBatch.expiry_date >= date.today(),
                ), DrugBatch.quantity),
                else_=0
            )
        ), 0) < Drug.min_stock_level
    ).order_by('current_stock')

    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            'drug_id': row.id,
            'drug_name': row.generic_name,
            'drug_code': row.drug_code,
            'current_stock': row.current_stock,
            'min_stock_level': row.min_stock_level,
            'reorder_point': row.reorder_point,
            'is_below_reorder': row.current_stock < row.reorder_point,
        }
        for row in rows
    ]


# =============================================================================
# Stock Transaction CRUD
# =============================================================================

async def create_stock_transaction(
    db: AsyncSession,
    transaction_data: StockTransactionCreate,
    user_id: Optional[int] = None,
) -> StockTransaction:
    """Create a stock transaction and update inventory."""
    # Generate transaction number
    transaction_number = f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    transaction = StockTransaction(
        transaction_number=transaction_number,
        **transaction_data.model_dump(exclude={'items'}),
        created_by=user_id,
        status='confirmed',
    )

    db.add(transaction)
    await db.flush()  # Get the transaction ID

    total_cost = Decimal('0')

    # Process items
    for item_data in transaction_data.items:
        # Calculate quantity before
        current_stock = await get_current_stock(db, item_data.drug_id)

        # Get or create batch if provided
        batch_id = item_data.batch_id
        if item_data.batch_id:
            # Update batch quantity
            batch_stmt = select(DrugBatch).where(DrugBatch.id == item_data.batch_id)
            batch_result = await db.execute(batch_stmt)
            batch = batch_result.scalar_one_or_none()
            if batch:
                batch.quantity += item_data.quantity
                batch.updated_at = datetime.now(timezone.utc)

        # Create transaction item
        item_total = (item_data.unit_cost or Decimal('0')) * abs(item_data.quantity)
        total_cost += item_total

        transaction_item = StockTransactionItem(
            transaction_id=transaction.id,
            **item_data.model_dump(),
            quantity_before=current_stock,
            quantity_after=current_stock + item_data.quantity,
            total_cost=item_total,
        )
        db.add(transaction_item)

    transaction.total_cost = total_cost
    transaction.confirmed_by = user_id
    transaction.confirmed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(transaction)

    return transaction


async def list_stock_transactions(
    db: AsyncSession,
    query: StockMovementQuery,
) -> Tuple[List[StockTransaction], int]:
    """List stock transactions with filtering."""
    conditions = []

    if query.drug_id:
        conditions.append(
            StockTransaction.id.in_(
                select(StockTransactionItem.transaction_id).where(
                    StockTransactionItem.drug_id == query.drug_id
                )
            )
        )

    if query.transaction_type:
        conditions.append(StockTransaction.transaction_type == query.transaction_type)

    if query.date_from:
        conditions.append(StockTransaction.transaction_date >= query.date_from)

    if query.date_to:
        conditions.append(StockTransaction.transaction_date <= query.date_to)

    # Count
    count_stmt = select(func.count(StockTransaction.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    # Data
    offset = (query.page - 1) * query.page_size
    data_stmt = select(StockTransaction)
    if conditions:
        data_stmt = data_stmt.where(and_(*conditions))
    data_stmt = data_stmt.order_by(desc(StockTransaction.transaction_date)).offset(offset).limit(query.page_size)

    result = await db.execute(data_stmt)
    transactions = list(result.scalars().all())

    return transactions, total


# =============================================================================
# Supplier CRUD
# =============================================================================

async def get_supplier(
    db: AsyncSession,
    supplier_id: int,
) -> Optional[Supplier]:
    """Get supplier by ID."""
    stmt = select(Supplier).where(Supplier.id == supplier_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_suppliers(
    db: AsyncSession,
    is_active: Optional[bool] = None,
) -> List[Supplier]:
    """List all suppliers."""
    conditions = []

    if is_active is not None:
        conditions.append(Supplier.is_active == is_active)

    stmt = select(Supplier)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(Supplier.supplier_name)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_supplier(
    db: AsyncSession,
    supplier_data: SupplierCreate,
    user_id: Optional[int] = None,
) -> Supplier:
    """Create a new supplier."""
    supplier = Supplier(
        **supplier_data.model_dump(),
        created_by=user_id,
    )

    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)

    return supplier


# =============================================================================
# Inventory Summary
# =============================================================================

async def get_inventory_summary(
    db: AsyncSession,
) -> InventorySummary:
    """Get overall inventory summary."""
    # Total drugs
    total_drugs_stmt = select(func.count(Drug.id)).where(Drug.is_active == True)
    total_drugs = await db.scalar(total_drugs_stmt) or 0

    # Total items (sum of all batch quantities)
    total_items_stmt = select(func.coalesce(func.sum(DrugBatch.quantity), 0)).where(
        and_(
            DrugBatch.is_quarantined == False,
            DrugBatch.expiry_date >= date.today(),
        )
    )
    total_items = await db.scalar(total_items_stmt) or 0

    # Total value
    total_value_stmt = select(func.coalesce(func.sum(
        DrugBatch.quantity * DrugBatch.unit_cost
    ), 0)).where(
        and_(
            DrugBatch.is_quarantined == False,
            DrugBatch.expiry_date >= date.today(),
        )
    )
    total_value = await db.scalar(total_value_stmt) or Decimal('0')

    # Drugs below min stock
    low_stock = await get_low_stock_drugs(db)
    drugs_below_min = len(low_stock)

    # Drugs near expiry
    near_expiry = await get_near_expiry_batches(db, days_threshold=90)
    drugs_near_expiry = len(near_expiry)

    # Expired drugs
    expired = await get_expired_batches(db)
    drugs_expired = len(expired)

    # Out of stock
    drugs_out_of_stock = len([d for d in low_stock if d['current_stock'] == 0])

    # Purchase orders
    po_pending_stmt = select(func.count(PurchaseOrder.id)).where(
        PurchaseOrder.approval_status == 'pending'
    )
    purchase_orders_pending = await db.scalar(po_pending_stmt) or 0

    po_approved_stmt = select(func.count(PurchaseOrder.id)).where(
        and_(
            PurchaseOrder.approval_status == 'approved',
            PurchaseOrder.status.in_(['sent', 'partially_received'])
        )
    )
    purchase_orders_approved = await db.scalar(po_approved_stmt) or 0

    return InventorySummary(
        total_drugs=total_drugs,
        total_items=total_items,
        total_value=total_value,
        drugs_below_min=drugs_below_min,
        drugs_near_expiry=drugs_near_expiry,
        drugs_expired=drugs_expired,
        drugs_out_of_stock=drugs_out_of_stock,
        purchase_orders_pending=purchase_orders_pending,
        purchase_orders_approved=purchase_orders_approved,
    )


async def get_inventory_alerts(
    db: AsyncSession,
) -> List[InventoryAlert]:
    """Get all inventory alerts."""
    alerts = []

    # Low stock alerts
    low_stock = await get_low_stock_drugs(db)
    for drug in low_stock:
        if drug['current_stock'] == 0:
            alerts.append(InventoryAlert(
                alert_type="out_of_stock",
                drug_id=drug['drug_id'],
                drug_name=drug['drug_name'],
                drug_code=drug['drug_code'],
                current_stock=drug['current_stock'],
                message=f"{drug['drug_name']} is OUT OF STOCK",
                severity="critical",
            ))
        elif drug['current_stock'] < drug['reorder_point']:
            alerts.append(InventoryAlert(
                alert_type="low_stock",
                drug_id=drug['drug_id'],
                drug_name=drug['drug_name'],
                drug_code=drug['drug_code'],
                current_stock=drug['current_stock'],
                message=f"{drug['drug_name']} is below reorder point ({drug['current_stock']} < {drug['reorder_point']})",
                severity="warning",
            ))

    # Near expiry alerts
    near_expiry = await get_near_expiry_batches(db, days_threshold=90)
    for batch in near_expiry:
        severity = "critical" if batch['days_to_expiry'] <= 30 else "warning"
        alerts.append(InventoryAlert(
            alert_type="near_expiry",
            drug_id=batch['drug_id'],
            drug_name=batch['drug_name'],
            drug_code=batch['drug_code'],
            current_stock=batch['quantity'],
            message=f"{batch['drug_name']} batch {batch['batch_number']} expires in {batch['days_to_expiry']} days",
            severity=severity,
        ))

    # Expired alerts
    expired = await get_expired_batches(db)
    for batch in expired:
        alerts.append(InventoryAlert(
            alert_type="expired",
            drug_id=batch['drug_id'],
            drug_name=batch['drug_name'],
            drug_code=batch['drug_code'],
            current_stock=batch['quantity'],
            message=f"{batch['drug_name']} batch {batch['batch_number']} EXPIRED on {batch['expiry_date']}",
            severity="critical",
        ))

    return sorted(alerts, key=lambda x: x.severity, reverse=True)
