"""Pharmacy Inventory API endpoints for STORY-024

This module provides API endpoints for drug master file, inventory tracking,
stock transactions, and purchase orders.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.inventory import (
    DrugCreate, DrugUpdate, DrugResponse, DrugListResponse,
    DrugBatchCreate, DrugBatchResponse,
    StockTransactionCreate, StockTransactionResponse,
    SupplierCreate, SupplierUpdate, SupplierResponse,
    PurchaseOrderCreate, PurchaseOrderResponse,
    InventorySummary, InventoryAlert, StockLevelResponse,
    DrugSearchQuery, StockMovementQuery,
)
from app.crud import inventory as crud_inventory


router = APIRouter()


# =============================================================================
# Drug Master Endpoints
# =============================================================================

@router.post("/inventory/drugs", response_model=DrugResponse)
async def create_drug(
    drug_data: DrugCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DrugResponse:
    """Create a new drug in the master file."""
    # Check if drug code already exists
    existing = await crud_inventory.get_drug_by_code(db, drug_data.drug_code)
    if existing:
        raise HTTPException(status_code=400, detail="Drug code already exists")

    drug = await crud_inventory.create_drug(db, drug_data, current_user.id)

    return DrugResponse(
        id=drug.id,
        drug_code=drug.drug_code,
        generic_name=drug.generic_name,
        brand_names=drug.brand_names,
        dosage_form=drug.dosage_form,
        strength=drug.strength,
        route=drug.route,
        bpjs_code=drug.bpjs_code,
        ekatalog_code=drug.ekatalog_code,
        manufacturer=drug.manufacturer,
        country_of_origin=drug.country_of_origin,
        min_stock_level=drug.min_stock_level,
        max_stock_level=drug.max_stock_level,
        reorder_point=drug.reorder_point,
        lead_time_days=drug.lead_time_days,
        purchase_price=drug.purchase_price,
        selling_price=drug.selling_price,
        bpjs_price=drug.bpjs_price,
        is_narcotic=drug.is_narcotic,
        is_antibiotic=drug.is_antibiotic,
        requires_prescription=drug.requires_prescription,
        requires_cold_chain=drug.requires_cold_chain,
        storage_conditions=drug.storage_conditions,
        shelf_life_months=drug.shelf_life_months,
        atc_code=drug.atc_code,
        therapeutic_class=drug.therapeutic_class,
        description=drug.description,
        is_active=drug.is_active,
        current_stock=0,
        is_below_min_stock=False,
        is_near_expiry=False,
        created_at=drug.created_at,
        updated_at=drug.updated_at,
    )


@router.get("/inventory/drugs", response_model=DrugListResponse)
async def list_drugs(
    search: Optional[str] = Query(None),
    dosage_form: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DrugListResponse:
    """List drugs with filtering and pagination."""
    drugs, total = await crud_inventory.list_drugs(
        db=db,
        search=search,
        dosage_form=dosage_form,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )

    # Get current stock for each drug
    drug_responses = []
    for drug in drugs:
        current_stock = await crud_inventory.get_current_stock(db, drug.id)
        drug_responses.append(DrugResponse(
            id=drug.id,
            drug_code=drug.drug_code,
            generic_name=drug.generic_name,
            brand_names=drug.brand_names,
            dosage_form=drug.dosage_form,
            strength=drug.strength,
            route=drug.route,
            bpjs_code=drug.bpjs_code,
            ekatalog_code=drug.ekatalog_code,
            manufacturer=drug.manufacturer,
            country_of_origin=drug.country_of_origin,
            min_stock_level=drug.min_stock_level,
            max_stock_level=drug.max_stock_level,
            reorder_point=drug.reorder_point,
            lead_time_days=drug.lead_time_days,
            purchase_price=drug.purchase_price,
            selling_price=drug.selling_price,
            bpjs_price=drug.bpjs_price,
            is_narcotic=drug.is_narcotic,
            is_antibiotic=drug.is_antibiotic,
            requires_prescription=drug.requires_prescription,
            requires_cold_chain=drug.requires_cold_chain,
            storage_conditions=drug.storage_conditions,
            shelf_life_months=drug.shelf_life_months,
            atc_code=drug.atc_code,
            therapeutic_class=drug.therapeutic_class,
            description=drug.description,
            is_active=drug.is_active,
            current_stock=current_stock,
            is_below_min_stock=current_stock < drug.min_stock_level,
            is_near_expiry=False,  # TODO: implement
            created_at=drug.created_at,
            updated_at=drug.updated_at,
        ))

    return DrugListResponse(
        drugs=drug_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/inventory/drugs/{drug_id}", response_model=DrugResponse)
async def get_drug(
    drug_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DrugResponse:
    """Get drug by ID."""
    drug = await crud_inventory.get_drug(db, drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    current_stock = await crud_inventory.get_current_stock(db, drug.id)

    return DrugResponse(
        id=drug.id,
        drug_code=drug.drug_code,
        generic_name=drug.generic_name,
        brand_names=drug.brand_names,
        dosage_form=drug.dosage_form,
        strength=drug.strength,
        route=drug.route,
        bpjs_code=drug.bpjs_code,
        ekatalog_code=drug.ekatalog_code,
        manufacturer=drug.manufacturer,
        country_of_origin=drug.country_of_origin,
        min_stock_level=drug.min_stock_level,
        max_stock_level=drug.max_stock_level,
        reorder_point=drug.reorder_point,
        lead_time_days=drug.lead_time_days,
        purchase_price=drug.purchase_price,
        selling_price=drug.selling_price,
        bpjs_price=drug.bpjs_price,
        is_narcotic=drug.is_narcotic,
        is_antibiotic=drug.is_antibiotic,
        requires_prescription=drug.requires_prescription,
        requires_cold_chain=drug.requires_cold_chain,
        storage_conditions=drug.storage_conditions,
        shelf_life_months=drug.shelf_life_months,
        atc_code=drug.atc_code,
        therapeutic_class=drug.therapeutic_class,
        description=drug.description,
        is_active=drug.is_active,
        current_stock=current_stock,
        is_below_min_stock=current_stock < drug.min_stock_level,
        is_near_expiry=False,
        created_at=drug.created_at,
        updated_at=drug.updated_at,
    )


@router.put("/inventory/drugs/{drug_id}", response_model=DrugResponse)
async def update_drug(
    drug_id: int,
    drug_data: DrugUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DrugResponse:
    """Update an existing drug."""
    drug = await crud_inventory.update_drug(db, drug_id, drug_data, current_user.id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    current_stock = await crud_inventory.get_current_stock(db, drug.id)

    return DrugResponse(
        id=drug.id,
        drug_code=drug.drug_code,
        generic_name=drug.generic_name,
        brand_names=drug.brand_names,
        dosage_form=drug.dosage_form,
        strength=drug.strength,
        route=drug.route,
        bpjs_code=drug.bpjs_code,
        ekatalog_code=drug.ekatalog_code,
        manufacturer=drug.manufacturer,
        country_of_origin=drug.country_of_origin,
        min_stock_level=drug.min_stock_level,
        max_stock_level=drug.max_stock_level,
        reorder_point=drug.reorder_point,
        lead_time_days=drug.lead_time_days,
        purchase_price=drug.purchase_price,
        selling_price=drug.selling_price,
        bpjs_price=drug.bpjs_price,
        is_narcotic=drug.is_narcotic,
        is_antibiotic=drug.is_antibiotic,
        requires_prescription=drug.requires_prescription,
        requires_cold_chain=drug.requires_cold_chain,
        storage_conditions=drug.storage_conditions,
        shelf_life_months=drug.shelf_life_months,
        atc_code=drug.atc_code,
        therapeutic_class=drug.therapeutic_class,
        description=drug.description,
        is_active=drug.is_active,
        current_stock=current_stock,
        is_below_min_stock=current_stock < drug.min_stock_level,
        is_near_expiry=False,
        created_at=drug.created_at,
        updated_at=drug.updated_at,
    )


# =============================================================================
# Drug Batch Endpoints
# =============================================================================

@router.post("/inventory/batches", response_model=DrugBatchResponse)
async def create_batch(
    batch_data: DrugBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DrugBatchResponse:
    """Create a new drug batch."""
    # Verify drug exists
    drug = await crud_inventory.get_drug(db, batch_data.drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found")

    batch = await crud_inventory.create_batch(db, batch_data, current_user.id)

    days_to_expiry = (batch.expiry_date - date.today()).days if batch.expiry_date else None
    is_expired = batch.expiry_date < date.today() if batch.expiry_date else False
    is_near_expiry = days_to_expiry is not None and days_to_expiry <= 90

    return DrugBatchResponse(
        id=batch.id,
        drug_id=batch.drug_id,
        batch_number=batch.batch_number,
        manufacturing_date=batch.manufacturing_date,
        expiry_date=batch.expiry_date,
        quantity=batch.quantity,
        initial_quantity=batch.initial_quantity,
        bin_location=batch.bin_location,
        is_quarantined=batch.is_quarantined,
        days_to_expiry=days_to_expiry,
        is_expired=is_expired,
        is_near_expiry=is_near_expiry,
    )


@router.get("/inventory/drugs/{drug_id}/batches", response_model=List[DrugBatchResponse])
async def get_drug_batches(
    drug_id: int,
    include_quarantined: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DrugBatchResponse]:
    """Get all batches for a drug."""
    batches = await crud_inventory.get_batches_by_drug(db, drug_id, include_quarantined)

    batch_responses = []
    for batch in batches:
        days_to_expiry = (batch.expiry_date - date.today()).days if batch.expiry_date else None
        is_expired = batch.expiry_date < date.today() if batch.expiry_date else False
        is_near_expiry = days_to_expiry is not None and days_to_expiry <= 90

        batch_responses.append(DrugBatchResponse(
            id=batch.id,
            drug_id=batch.drug_id,
            batch_number=batch.batch_number,
            manufacturing_date=batch.manufacturing_date,
            expiry_date=batch.expiry_date,
            quantity=batch.quantity,
            initial_quantity=batch.initial_quantity,
            bin_location=batch.bin_location,
            is_quarantined=batch.is_quarantined,
            days_to_expiry=days_to_expiry,
            is_expired=is_expired,
            is_near_expiry=is_near_expiry,
        ))

    return batch_responses


# =============================================================================
# Stock Transaction Endpoints
# =============================================================================

@router.post("/inventory/transactions", response_model=StockTransactionResponse)
async def create_stock_transaction(
    transaction_data: StockTransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StockTransactionResponse:
    """Create a stock transaction."""
    transaction = await crud_inventory.create_stock_transaction(
        db, transaction_data, current_user.id
    )

    # Get batch responses
    batch_responses = []
    for item in transaction.items:
        if item.batch:
            days_to_expiry = (item.batch.expiry_date - date.today()).days if item.batch.expiry_date else None
            batch_responses.append(DrugBatchResponse(
                id=item.batch.id,
                drug_id=item.batch.drug_id,
                batch_number=item.batch.batch_number,
                manufacturing_date=item.batch.manufacturing_date,
                expiry_date=item.batch.expiry_date,
                quantity=item.batch.quantity,
                initial_quantity=item.batch.initial_quantity,
                bin_location=item.batch.bin_location,
                is_quarantined=item.batch.is_quarantined,
                days_to_expiry=days_to_expiry,
                is_expired=item.batch.expiry_date < date.today() if item.batch.expiry_date else False,
                is_near_expiry=days_to_expiry is not None and days_to_expiry <= 90,
            ))

    return StockTransactionResponse(
        id=transaction.id,
        transaction_number=transaction.transaction_number,
        transaction_type=transaction.transaction_type,
        transaction_date=transaction.transaction_date,
        reference_number=transaction.reference_number,
        status=transaction.status,
        total_cost=transaction.total_cost,
        items=batch_responses,
        created_at=transaction.created_at,
    )


@router.get("/inventory/transactions", response_model=List[StockTransactionResponse])
async def list_stock_transactions(
    drug_id: Optional[int] = Query(None),
    transaction_type: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[StockTransactionResponse]:
    """List stock transactions with filtering."""
    from datetime import datetime

    query = StockMovementQuery(
        drug_id=drug_id,
        transaction_type=transaction_type,
        date_from=datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None,
        date_to=datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None,
        page=page,
        page_size=page_size,
    )

    transactions, total = await crud_inventory.list_stock_transactions(db, query)

    # Build responses
    responses = []
    for transaction in transactions:
        responses.append(StockTransactionResponse(
            id=transaction.id,
            transaction_number=transaction.transaction_number,
            transaction_type=transaction.transaction_type,
            transaction_date=transaction.transaction_date,
            reference_number=transaction.reference_number,
            status=transaction.status,
            total_cost=transaction.total_cost,
            items=[],  # TODO: populate
            created_at=transaction.created_at,
        ))

    return responses


# =============================================================================
# Supplier Endpoints
# =============================================================================

@router.post("/inventory/suppliers", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SupplierResponse:
    """Create a new supplier."""
    # TODO: Check if supplier code exists
    supplier = await crud_inventory.create_supplier(db, supplier_data, current_user.id)

    return SupplierResponse(
        id=supplier.id,
        supplier_code=supplier.supplier_code,
        supplier_name=supplier.supplier_name,
        contact_person=supplier.contact_person,
        phone=supplier.phone,
        email=supplier.email,
        address=supplier.address,
        is_bpjs_supplier=supplier.is_bpjs_supplier,
        bpjs_facility_code=supplier.bpjs_facility_code,
        payment_terms=supplier.payment_terms,
        credit_limit=supplier.credit_limit,
        is_active=supplier.is_active,
        created_at=supplier.created_at,
        updated_at=supplier.updated_at,
    )


@router.get("/inventory/suppliers", response_model=List[SupplierResponse])
async def list_suppliers(
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SupplierResponse]:
    """List all suppliers."""
    suppliers = await crud_inventory.list_suppliers(db, is_active)

    return [
        SupplierResponse(
            id=s.id,
            supplier_code=s.supplier_code,
            supplier_name=s.supplier_name,
            contact_person=s.contact_person,
            phone=s.phone,
            email=s.email,
            address=s.address,
            is_bpjs_supplier=s.is_bpjs_supplier,
            bpjs_facility_code=s.bpjs_facility_code,
            payment_terms=s.payment_terms,
            credit_limit=s.credit_limit,
            is_active=s.is_active,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in suppliers
    ]


# =============================================================================
# Inventory Summary and Alerts
# =============================================================================

@router.get("/inventory/summary", response_model=InventorySummary)
async def get_inventory_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InventorySummary:
    """Get overall inventory summary."""
    summary = await crud_inventory.get_inventory_summary(db)
    return summary


@router.get("/inventory/alerts", response_model=List[InventoryAlert])
async def get_inventory_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[InventoryAlert]:
    """Get all inventory alerts."""
    alerts = await crud_inventory.get_inventory_alerts(db)
    return alerts


@router.get("/inventory/stock-levels", response_model=List[StockLevelResponse])
async def get_stock_levels(
    only_alerts: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[StockLevelResponse]:
    """Get stock levels for all drugs."""
    # Get all active drugs
    drugs, _ = await crud_inventory.list_drugs(db, is_active=True, page=1, page_size=1000)

    stock_levels = []
    for drug in drugs:
        current_stock = await crud_inventory.get_current_stock(db, drug.id)
        is_below_min = current_stock < drug.min_stock_level

        # Skip if only alerts and not below min
        if only_alerts and not is_below_min:
            continue

        # Get batches
        batches = await crud_inventory.get_batches_by_drug(db, drug.id)
        batch_responses = []
        for batch in batches:
            days_to_expiry = (batch.expiry_date - date.today()).days if batch.expiry_date else None
            batch_responses.append(DrugBatchResponse(
                id=batch.id,
                drug_id=batch.drug_id,
                batch_number=batch.batch_number,
                manufacturing_date=batch.manufacturing_date,
                expiry_date=batch.expiry_date,
                quantity=batch.quantity,
                initial_quantity=batch.initial_quantity,
                bin_location=batch.bin_location,
                is_quarantined=batch.is_quarantined,
                days_to_expiry=days_to_expiry,
                is_expired=batch.expiry_date < date.today() if batch.expiry_date else False,
                is_near_expiry=days_to_expiry is not None and days_to_expiry <= 90,
            ))

        total_value = current_stock * drug.purchase_price if drug.purchase_price else None

        stock_levels.append(StockLevelResponse(
            drug_id=drug.id,
            drug_name=drug.generic_name,
            drug_code=drug.drug_code,
            generic_name=drug.generic_name,
            dosage_form=drug.dosage_form,
            current_stock=current_stock,
            min_stock_level=drug.min_stock_level,
            max_stock_level=drug.max_stock_level,
            reorder_point=drug.reorder_point,
            is_below_min=is_below_min,
            batches=batch_responses,
            last_purchase_price=drug.purchase_price,
            total_value=total_value,
        ))

    # Sort by is_below_min and current_stock
    stock_levels.sort(key=lambda x: (not x.is_below_min, x.current_stock))

    return stock_levels
