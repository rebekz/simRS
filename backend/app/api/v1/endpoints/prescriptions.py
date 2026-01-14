"""Electronic Prescription API endpoints for STORY-017

This module provides API endpoints for:
- Prescription creation and management
- Drug search with auto-complete
- Interaction checking
- Prescription verification
- Pharmacy transmission
- Prescription printing
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_current_active_user, get_db
from app.models.user import User
from app.schemas.prescription import (
    PrescriptionResponse, PrescriptionCreate, PrescriptionUpdate,
    PrescriptionListResponse, PrescriptionItemResponse, PrescriptionItemUpdate,
    DrugSearchResponse, DrugSearchResult,
    PrescriptionInteractionCheck, PrescriptionPrintResponse,
    DoseCalculationRequest, DoseCalculationResponse,
    BPJSCoverageStatus, PrescriptionTransmissionRequest, PrescriptionTransmissionResponse,
    PrescriptionStatus,
)
from app.crud import prescription as crud
from app.crud.drug_interactions import check_duplicate_therapy


router = APIRouter()


# =============================================================================
# Drug Search Endpoints
# =============================================================================

@router.get("/prescriptions/drugs/search", response_model=DrugSearchResponse)
async def search_drugs(
    query: str = Query(..., min_length=2, description="Search query for drug name"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Search drugs by name or generic name with auto-complete"""
    results, total = await crud.search_drugs(
        db=db,
        query=query,
        page=page,
        page_size=page_size,
    )

    return DrugSearchResponse(
        query=query,
        results=results,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/prescriptions/drugs/{drug_id}/bpjs-coverage", response_model=BPJSCoverageStatus)
async def get_drug_bpjs_coverage(
    drug_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get BPJS coverage status for a drug"""
    coverage = await crud.get_bpjs_coverage_status(db=db, drug_id=drug_id)
    return BPJSCoverageStatus(**coverage)


@router.post("/prescriptions/calculate-dose", response_model=DoseCalculationResponse)
async def calculate_dose(
    request: DoseCalculationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Calculate dose based on patient parameters"""
    result = await crud.calculate_dose(
        db=db,
        drug_id=request.drug_id,
        patient_weight_kg=request.patient_weight_kg,
        patient_age_years=request.patient_age_years,
        target_dose_mg=request.target_dose_mg,
        concentration_mg_ml=request.concentration_mg_ml,
    )
    return DoseCalculationResponse(**result)


# =============================================================================
# Prescription Management Endpoints
# =============================================================================

@router.post("/prescriptions", response_model=PrescriptionResponse)
async def create_prescription(
    prescription: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new prescription"""
    # Check interactions first
    drug_ids = [item.drug_id for item in prescription.items]
    interaction_check = await crud.check_prescription_interactions(
        db=db,
        patient_id=prescription.patient_id,
        drug_ids=drug_ids,
    )

    # If contraindicated interactions found, prevent creation
    if interaction_check.contraindicated_count > 0 and not prescription.is_draft:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create prescription: {interaction_check.contraindicated_count} contraindicated interaction(s) found",
        )

    # Check for duplicate therapies
    duplicate_warnings = await check_duplicate_therapy(db=db, drug_ids=drug_ids)
    # Store warnings in notes for now
    if duplicate_warnings:
        warnings_str = f"Duplicate therapy warnings: {len(duplicate_warnings)} found"
        prescription.notes = f"{prescription.notes or ''} {warnings_str}".strip()

    db_prescription = await crud.create_prescription(
        db=db,
        prescription=prescription,
        prescriber_id=current_user.id,
    )

    # Build response with all details
    return await _build_prescription_response(db, db_prescription, interaction_check)


@router.get("/prescriptions", response_model=PrescriptionListResponse)
async def list_prescriptions(
    patient_id: Optional[int] = Query(None),
    encounter_id: Optional[int] = Query(None),
    status: Optional[PrescriptionStatus] = Query(None),
    prescriber_id: Optional[int] = Query(None),
    submitted_to_pharmacy: Optional[bool] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List prescriptions with filtering and pagination"""
    prescriptions, total = await crud.list_prescriptions(
        db=db,
        patient_id=patient_id,
        encounter_id=encounter_id,
        status=status,
        prescriber_id=prescriber_id,
        submitted_to_pharmacy=submitted_to_pharmacy,
        page=page,
        page_size=page_size,
    )

    # Build responses
    response_data = []
    for prescription in prescriptions:
        response_data.append(await _build_prescription_response(db, prescription))

    return PrescriptionListResponse(
        prescriptions=response_data,
        total=total,
        page=page,
        page_size=page_size,
        filters_applied={
            "patient_id": patient_id,
            "encounter_id": encounter_id,
            "status": status.value if status else None,
            "prescriber_id": prescriber_id,
            "submitted_to_pharmacy": submitted_to_pharmacy,
        },
    )


@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def get_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get prescription by ID"""
    prescription = await crud.get_prescription(db=db, prescription_id=prescription_id)
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    return await _build_prescription_response(db, prescription)


@router.put("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
async def update_prescription(
    prescription_id: int,
    prescription_update: PrescriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update prescription details (only draft prescriptions)"""
    prescription = await crud.update_prescription(
        db=db,
        prescription_id=prescription_id,
        prescription_update=prescription_update,
    )
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")

    return await _build_prescription_response(db, prescription)


@router.delete("/prescriptions/{prescription_id}")
async def delete_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a prescription (only draft prescriptions)"""
    success = await crud.delete_prescription(db=db, prescription_id=prescription_id)
    if not success:
        raise HTTPException(status_code=404, detail="Prescription not found")

    return {"message": "Prescription deleted successfully"}


@router.post("/prescriptions/{prescription_id}/submit", response_model=PrescriptionResponse)
async def submit_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Submit prescription to pharmacy for dispensing"""
    prescription = await crud.submit_prescription_to_pharmacy(db=db, prescription_id=prescription_id)
    return await _build_prescription_response(db, prescription)


# =============================================================================
# Prescription Item Endpoints
# =============================================================================

@router.put("/prescriptions/items/{item_id}", response_model=PrescriptionItemResponse)
async def update_prescription_item(
    item_id: int,
    item_update: PrescriptionItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a prescription item (only draft prescriptions)"""
    item = await crud.update_prescription_item(
        db=db,
        item_id=item_id,
        item_update=item_update,
    )
    if not item:
        raise HTTPException(status_code=404, detail="Prescription item not found")

    return _build_item_response(item)


# =============================================================================
# Interaction Checking Endpoints
# =============================================================================

@router.post("/prescriptions/check-interactions", response_model=PrescriptionInteractionCheck)
async def check_prescription_interactions(
    patient_id: int,
    drug_ids: List[int],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Check for drug interactions before creating prescription"""
    interaction_check = await crud.check_prescription_interactions(
        db=db,
        patient_id=patient_id,
        drug_ids=drug_ids,
    )

    return PrescriptionInteractionCheck(
        has_interactions=interaction_check.has_interactions,
        total_interactions=interaction_check.total_interactions,
        contraindicated_count=interaction_check.contraindicated_count,
        severe_count=interaction_check.severe_count,
        moderate_count=interaction_check.moderate_count,
        mild_count=interaction_check.mild_count,
        interactions=interaction_check.interactions,
        can_prescribe=interaction_check.can_prescribe,
        override_required=interaction_check.override_required,
        override_reason=interaction_check.override_reason,
    )


# =============================================================================
# Prescription Verification Endpoints
# =============================================================================

@router.post("/prescriptions/{prescription_id}/verify", response_model=PrescriptionResponse)
async def verify_prescription(
    prescription_id: int,
    issues_found: Optional[List[str]] = None,
    interactions_overridden: bool = False,
    override_reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Verify a prescription (pharmacist or supervisor review)"""
    # Determine verifier role
    verifier_role = "pharmacist" if "pharmacy" in current_user.role else "supervisor"

    prescription = await crud.verify_prescription(
        db=db,
        prescription_id=prescription_id,
        verifier_id=current_user.id,
        verifier_name=current_user.full_name,
        verifier_role=verifier_role,
        issues_found=issues_found,
        interactions_overridden=interactions_overridden,
        override_reason=override_reason,
    )

    return await _build_prescription_response(db, prescription)


# =============================================================================
# Pharmacy Transmission Endpoints
# =============================================================================

@router.post("/prescriptions/{prescription_id}/transmit", response_model=PrescriptionTransmissionResponse)
async def transmit_prescription(
    prescription_id: int,
    request: PrescriptionTransmissionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Transmit prescription to pharmacy"""
    # Override prescription_id from URL
    request.prescription_id = prescription_id

    transmission = await crud.create_prescription_transmission(
        db=db,
        prescription_id=prescription_id,
        target_pharmacy_id=request.target_pharmacy_id,
        priority=request.priority,
        notes=request.notes,
    )

    return PrescriptionTransmissionResponse(
        prescription_id=transmission.prescription_id,
        transmission_id=transmission.transmission_id,
        status=transmission.status,
        sent_at=transmission.sent_at,
        acknowledged_at=transmission.acknowledged_at,
        pharmacy_name=transmission.target_pharmacy_name,
        estimated_ready_time=transmission.estimated_ready_time,
    )


@router.post("/prescriptions/transmissions/{transmission_id}/acknowledge", response_model=PrescriptionTransmissionResponse)
async def acknowledge_transmission(
    transmission_id: str,
    pharmacy_name: str,
    estimated_ready_minutes: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Acknowledge prescription transmission from pharmacy (pharmacy endpoint)"""
    transmission = await crud.acknowledge_prescription_transmission(
        db=db,
        transmission_id=transmission_id,
        pharmacy_name=pharmacy_name,
        estimated_ready_minutes=estimated_ready_minutes,
    )

    return PrescriptionTransmissionResponse(
        prescription_id=transmission.prescription_id,
        transmission_id=transmission.transmission_id,
        status=transmission.status,
        sent_at=transmission.sent_at,
        acknowledged_at=transmission.acknowledged_at,
        pharmacy_name=transmission.target_pharmacy_name,
        estimated_ready_time=transmission.estimated_ready_time,
    )


# =============================================================================
# Prescription Print Endpoints
# =============================================================================

@router.post("/prescriptions/{prescription_id}/print", response_model=PrescriptionPrintResponse)
async def print_prescription(
    prescription_id: int,
    include_barcode: bool = True,
    include_diagnosis: bool = True,
    include_instructions: bool = True,
    copies: int = Query(default=1, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generate printable prescription document with barcode"""
    import secrets
    from datetime import timedelta

    # Generate secure token for document access
    secure_token = secrets.token_urlsafe(32)

    # Set expiry time (1 hour from now)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    # Build print URL
    print_url = f"/api/v1/prescriptions/{prescription_id}/print/{secure_token}"

    barcode_url = f"/api/v1/prescriptions/{prescription_id}/barcode" if include_barcode else None

    # Log the print event
    await crud.log_prescription_print(
        db=db,
        prescription_id=prescription_id,
        printed_by_id=current_user.id,
        printed_by_name=current_user.full_name,
        print_count=copies,
        included_barcode=include_barcode,
        included_diagnosis=include_diagnosis,
        included_instructions=include_instructions,
        document_url=print_url,
        document_expires_at=expires_at,
    )

    return PrescriptionPrintResponse(
        prescription_id=prescription_id,
        prescription_number="",  # Will be filled in response
        print_url=print_url,
        barcode_url=barcode_url,
        generated_at=datetime.utcnow(),
        expires_at=expires_at,
    )


# =============================================================================
# Helper Functions
# =============================================================================

async def _build_prescription_response(
    db: AsyncSession,
    prescription,
    interaction_check: Optional[PrescriptionInteractionCheck] = None,
) -> PrescriptionResponse:
    """Build full prescription response with all details"""
    # Get patient details
    patient_name = prescription.patient.name if prescription.patient else None
    patient_bpjs_number = prescription.patient.bpjs_number if prescription.patient else None

    # Get encounter details
    encounter_type = prescription.encounter.encounter_type if prescription.encounter else None

    # Get prescriber details
    prescriber_name = prescription.prescriber.full_name if prescription.prescriber else None
    prescriber_license = getattr(prescription.prescriber, 'license_number', None) if prescription.prescriber else None

    # Build items
    items = []
    narcotic_count = 0
    antibiotic_count = 0
    total_items_dispensed = 0

    for item in prescription.items:
        item_response = _build_item_response(item)
        items.append(item_response)

        if item_response.is_narcotic:
            narcotic_count += 1
        if item_response.is_antibiotic:
            antibiotic_count += 1
        if item_response.dispense_status.value in ["dispensed", "partial"]:
            total_items_dispensed += 1

    # Calculate if fully dispensed
    is_fully_dispensed = total_items_dispensed == len(items) and len(items) > 0

    # Build response
    return PrescriptionResponse(
        id=prescription.id,
        prescription_number=prescription.prescription_number,
        status=prescription.status,
        patient_id=prescription.patient_id,
        patient_name=patient_name,
        patient_bpjs_number=patient_bpjs_number,
        encounter_id=prescription.encounter_id,
        encounter_type=encounter_type,
        prescriber_id=prescription.prescriber_id,
        prescriber_name=prescriber_name,
        prescriber_license=prescriber_license,
        notes=prescription.notes,
        diagnosis=prescription.diagnosis,
        priority=prescription.priority,
        items=items,
        total_items=len(items),
        total_items_dispensed=total_items_dispensed,
        narcotic_count=narcotic_count,
        antibiotic_count=antibiotic_count,
        is_fully_dispensed=is_fully_dispensed,
        submitted_to_pharmacy=prescription.submitted_to_pharmacy,
        submitted_date=prescription.submitted_date,
        dispensed_date=prescription.dispensed_date,
        verified_by_id=prescription.verified_by_id,
        verified_by_name=prescription.verifier.full_name if prescription.verifier else None,
        verified_date=prescription.verified_date,
        barcode=prescription.barcode,
        barcode_url=f"/api/v1/prescriptions/{prescription.id}/barcode" if prescription.barcode else None,
        estimated_cost=prescription.estimated_cost,
        bpjs_coverage_estimate=prescription.bpjs_coverage_estimate,
        patient_cost_estimate=prescription.patient_cost_estimate,
        created_at=prescription.created_at,
        updated_at=prescription.updated_at,
    )


def _build_item_response(item) -> PrescriptionItemResponse:
    """Build prescription item response"""
    from app.schemas.medication import Route

    # Get dispenser name
    dispenser_name = item.dispenser.full_name if item.dispenser else None

    # Calculate days supply from duration
    days_supply = item.duration_days

    return PrescriptionItemResponse(
        id=item.id,
        prescription_id=item.prescription_id,
        item_type=item.item_type,
        drug_id=item.drug_id,
        drug_name=item.drug_name,
        generic_name=item.generic_name,
        dosage=item.dosage,
        dose_unit=item.dose_unit,
        frequency=item.frequency,
        route=Route(item.route),
        duration_days=item.duration_days,
        quantity=item.quantity,
        indication=item.indication,
        compound_name=item.compound_name,
        compound_components=item.compound_components,
        special_instructions=item.special_instructions,
        is_prn=item.is_prn,
        dispense_status=item.dispense_status,
        quantity_dispensed=item.quantity_dispensed,
        dispensed_date=item.dispensed_date,
        dispenser_id=item.dispenser_id,
        dispenser_name=dispenser_name,
        bpjs_code=None,  # Would load from drug
        bpjs_covered=True,  # Would check from drug
        is_narcotic=False,  # Would check from drug
        is_antibiotic=False,  # Would check from drug
        days_supply=days_supply,
        refills_allowed=item.refills_allowed,
        refills_used=item.refills_used,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
