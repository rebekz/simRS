"""Electronic Prescription CRUD Operations for STORY-017

This module provides CRUD operations for:
- Prescription creation and management
- Prescription item management
- Drug search with auto-complete
- Interaction checking integration
- BPJS coverage status
- Prescription verification
- Pharmacy transmission
"""
from typing import List, Optional, Tuple, Dict
from datetime import datetime, date
from sqlalchemy import select, and_, or_, func as sql_func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import json
import uuid

from app.models.prescription import (
    Prescription, PrescriptionItem, BasicPrescriptionTransmission,
    PrescriptionVerificationLog, PrescriptionPrintLog
)
from app.models.medication import PatientMedication
from app.models.inventory import Drug
from app.models.user import User
from app.schemas.prescription import (
    PrescriptionCreate, PrescriptionUpdate, PrescriptionStatus,
    PrescriptionItemType, DispenseStatus,
    PrescriptionItemCreate, PrescriptionItemUpdate,
    DrugSearchResult
)
from app.schemas.medication import DrugInteractionCheckResponse, DrugInteraction


# =============================================================================
# Prescription CRUD
# =============================================================================

async def get_prescription(
    db: AsyncSession,
    prescription_id: int,
) -> Optional[Prescription]:
    """Get prescription by ID with all relationships"""
    stmt = (
        select(Prescription)
        .options(
            selectinload(Prescription.items),
            selectinload(Prescription.patient),
            selectinload(Prescription.prescriber),
            selectinload(Prescription.verifier)
        )
        .where(Prescription.id == prescription_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_prescriptions(
    db: AsyncSession,
    patient_id: Optional[int] = None,
    encounter_id: Optional[int] = None,
    status: Optional[PrescriptionStatus] = None,
    prescriber_id: Optional[int] = None,
    submitted_to_pharmacy: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[Prescription], int]:
    """List prescriptions with filtering and pagination"""
    conditions = []

    if patient_id:
        conditions.append(Prescription.patient_id == patient_id)
    if encounter_id:
        conditions.append(Prescription.encounter_id == encounter_id)
    if status:
        conditions.append(Prescription.status == status)
    if prescriber_id:
        conditions.append(Prescription.prescriber_id == prescriber_id)
    if submitted_to_pharmacy is not None:
        conditions.append(Prescription.submitted_to_pharmacy == submitted_to_pharmacy)

    # Build query
    stmt = select(Prescription)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Get total count
    count_stmt = select(sql_func.count(Prescription.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Apply pagination and ordering
    stmt = stmt.options(selectinload(Prescription.items))
    stmt = stmt.order_by(Prescription.created_at.desc())
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    prescriptions = result.scalars().all()

    return list(prescriptions), total


async def create_prescription(
    db: AsyncSession,
    prescription: PrescriptionCreate,
    prescriber_id: int,
) -> Prescription:
    """Create a new prescription with items"""
    # Generate prescription number
    prescription_number = await _generate_prescription_number(db)

    # Generate barcode
    barcode = await _generate_prescription_barcode(db, prescription_number)

    # Create prescription
    db_prescription = Prescription(
        prescription_number=prescription_number,
        barcode=barcode,
        patient_id=prescription.patient_id,
        encounter_id=prescription.encounter_id,
        prescriber_id=prescriber_id,
        priority=prescription.priority,
        diagnosis=prescription.diagnosis,
        notes=prescription.notes,
        status=PrescriptionStatus.DRAFT if prescription.is_draft else PrescriptionStatus.ACTIVE,
    )

    db.add(db_prescription)
    await db.flush()  # Get the ID before adding items

    # Add prescription items
    narcotic_count = 0
    antibiotic_count = 0

    for item_data in prescription.items:
        db_item = await _create_prescription_item(db, db_prescription.id, item_data)

        # Count special drugs
        drug_stmt = select(Drug).where(Drug.id == item_data.drug_id)
        drug_result = await db.execute(drug_stmt)
        drug = drug_result.scalar_one_or_none()

        if drug:
            if drug.is_narcotic:
                narcotic_count += 1
            if drug.is_antibiotic:
                antibiotic_count += 1

    await db.commit()
    await db.refresh(db_prescription)

    return db_prescription


async def update_prescription(
    db: AsyncSession,
    prescription_id: int,
    prescription_update: PrescriptionUpdate,
) -> Optional[Prescription]:
    """Update prescription details"""
    prescription = await get_prescription(db, prescription_id)
    if not prescription:
        return None

    # Only allow updates to draft prescriptions
    if prescription.status != PrescriptionStatus.DRAFT:
        raise ValueError("Can only update draft prescriptions")

    if prescription_update.notes is not None:
        prescription.notes = prescription_update.notes
    if prescription_update.diagnosis is not None:
        prescription.diagnosis = prescription_update.diagnosis
    if prescription_update.priority is not None:
        prescription.priority = prescription_update.priority
    if prescription_update.status is not None:
        prescription.status = prescription_update.status

    await db.commit()
    await db.refresh(prescription)

    return prescription


async def delete_prescription(
    db: AsyncSession,
    prescription_id: int,
) -> bool:
    """Delete a prescription (only draft status)"""
    prescription = await get_prescription(db, prescription_id)
    if not prescription:
        return False

    # Only allow deletion of draft prescriptions
    if prescription.status != PrescriptionStatus.DRAFT:
        raise ValueError("Can only delete draft prescriptions")

    await db.delete(prescription)
    await db.commit()

    return True


async def submit_prescription_to_pharmacy(
    db: AsyncSession,
    prescription_id: int,
) -> Prescription:
    """Submit prescription to pharmacy for dispensing"""
    prescription = await get_prescription(db, prescription_id)
    if not prescription:
        raise ValueError("Prescription not found")

    # Update prescription status
    prescription.status = PrescriptionStatus.ACTIVE
    prescription.submitted_to_pharmacy = True
    prescription.submitted_date = datetime.utcnow()

    await db.commit()
    await db.refresh(prescription)

    # Create pharmacy transmission record
    await create_prescription_transmission(
        db,
        prescription_id=prescription_id,
        target_pharmacy_id=None,  # Default hospital pharmacy
    )

    return prescription


# =============================================================================
# Prescription Item CRUD
# =============================================================================

async def _create_prescription_item(
    db: AsyncSession,
    prescription_id: int,
    item_data: PrescriptionItemCreate,
) -> PrescriptionItem:
    """Create a prescription item (internal function)"""
    # Get drug details
    drug_stmt = select(Drug).where(Drug.id == item_data.drug_id)
    drug_result = await db.execute(drug_stmt)
    drug = drug_result.scalar_one_or_none()

    if not drug:
        raise ValueError(f"Drug with ID {item_data.drug_id} not found")

    # Prepare compound components JSON
    compound_components_json = None
    if item_data.item_type == PrescriptionItemType.COMPOUND and item_data.compound_components:
        compound_components_json = [comp.model_dump() for comp in item_data.compound_components]

    # Create prescription item
    db_item = PrescriptionItem(
        prescription_id=prescription_id,
        item_type=item_data.item_type,
        drug_id=item_data.drug_id,
        drug_name=drug.name,
        generic_name=drug.generic_name,
        dosage=item_data.dosage,
        dose_unit=item_data.dose_unit,
        frequency=item_data.frequency,
        route=item_data.route.value,
        duration_days=item_data.duration_days,
        quantity=item_data.quantity,
        compound_name=item_data.compound_name,
        compound_components=compound_components_json,
        indication=item_data.indication,
        special_instructions=item_data.special_instructions,
        is_prn=item_data.is_prn,
    )

    db.add(db_item)
    await db.flush()

    return db_item


async def update_prescription_item(
    db: AsyncSession,
    item_id: int,
    item_update: PrescriptionItemUpdate,
) -> Optional[PrescriptionItem]:
    """Update a prescription item"""
    stmt = select(PrescriptionItem).where(PrescriptionItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()

    if not item:
        return None

    # Check if prescription is still draft
    prescription = await get_prescription(db, item.prescription_id)
    if prescription.status != PrescriptionStatus.DRAFT:
        raise ValueError("Can only update items in draft prescriptions")

    if item_update.dosage is not None:
        item.dosage = item_update.dosage
    if item_update.dose_unit is not None:
        item.dose_unit = item_update.dose_unit
    if item_update.frequency is not None:
        item.frequency = item_update.frequency
    if item_update.route is not None:
        item.route = item_update.route.value
    if item_update.duration_days is not None:
        item.duration_days = item_update.duration_days
    if item_update.quantity is not None:
        item.quantity = item_update.quantity
    if item_update.indication is not None:
        item.indication = item_update.indication
    if item_update.special_instructions is not None:
        item.special_instructions = item_update.special_instructions

    await db.commit()
    await db.refresh(item)

    return item


# =============================================================================
# Drug Search
# =============================================================================

async def search_drugs(
    db: AsyncSession,
    query: str,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[DrugSearchResult], int]:
    """Search drugs by name or generic name with auto-complete"""
    # Build search query - search in both name and generic_name
    search_pattern = f"%{query}%"

    stmt = select(Drug).where(
        or_(
            Drug.name.ilike(search_pattern),
            Drug.generic_name.ilike(search_pattern),
        )
    )

    # Get total count
    count_stmt = select(sql_func.count(Drug.id)).where(
        or_(
            Drug.name.ilike(search_pattern),
            Drug.generic_name.ilike(search_pattern),
        )
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()

    # Apply pagination and ordering
    stmt = stmt.order_by(Drug.name)
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    drugs = result.scalars().all()

    # Convert to search results
    search_results = [
        DrugSearchResult(
            id=drug.id,
            name=drug.name,
            generic_name=drug.generic_name,
            dosage_form=drug.dosage_form,
            strength=drug.strength,
            bpjs_code=drug.bpjs_code,
            is_narcotic=drug.is_narcotic or False,
            is_antibiotic=drug.is_antibiotic or False,
            requires_prescription=drug.requires_prescription or True,
            stock_available=drug.stock_quantity,
            therapeutic_class=drug.therapeutic_class,
        )
        for drug in drugs
    ]

    return search_results, total


# =============================================================================
# Drug Interaction Checking
# =============================================================================

async def check_prescription_interactions(
    db: AsyncSession,
    patient_id: int,
    drug_ids: List[int],
) -> DrugInteractionCheckResponse:
    """Check for drug interactions in a prescription"""
    from app.crud.drug_interactions import check_drug_interactions

    # Use the existing interaction check from medication module
    interaction_response = await check_drug_interactions(
        db=db,
        patient_id=patient_id,
        drug_ids=drug_ids,
    )

    # Determine if prescription can proceed
    contraindicated_count = interaction_response.by_severity.get("contraindicated", 0)
    can_prescribe = contraindicated_count == 0
    override_required = contraindicated_count > 0 or interaction_response.by_severity.get("severe", 0) > 0

    override_reason = None
    if override_required:
        if contraindicated_count > 0:
            override_reason = f"{contraindicated_count} contraindicated interaction(s) found"
        else:
            override_reason = "Severe interactions found - requires override"

    return DrugInteractionCheckResponse(
        has_interactions=interaction_response.has_interactions,
        total_interactions=interaction_response.total_interactions,
        contraindicated_count=interaction_response.by_severity.get("contraindicated", 0),
        severe_count=interaction_response.by_severity.get("severe", 0),
        moderate_count=interaction_response.by_severity.get("moderate", 0),
        mild_count=interaction_response.by_severity.get("mild", 0),
        interactions=interaction_response.interactions,
        can_prescribe=can_prescribe,
        override_required=override_required,
        override_reason=override_reason,
    )


# =============================================================================
# Prescription Verification
# =============================================================================

async def verify_prescription(
    db: AsyncSession,
    prescription_id: int,
    verifier_id: int,
    verifier_name: str,
    verifier_role: str,
    issues_found: Optional[List[str]] = None,
    interactions_overridden: bool = False,
    override_reason: Optional[str] = None,
) -> Prescription:
    """Verify a prescription (pharmacist or supervisor review)"""
    prescription = await get_prescription(db, prescription_id)
    if not prescription:
        raise ValueError("Prescription not found")

    # Mark as verified
    prescription.verified_by_id = verifier_id
    prescription.verified_date = datetime.utcnow()

    # Create verification log
    verification_log = PrescriptionVerificationLog(
        prescription_id=prescription_id,
        action="verified" if not issues_found else "flagged",
        verifier_id=verifier_id,
        verifier_name=verifier_name,
        verifier_role=verifier_role,
        issues_found=issues_found or [],
        requires_intervention=bool(issues_found),
        interactions_overridden=interactions_overridden,
        override_reason=override_reason,
    )

    db.add(verification_log)
    await db.commit()
    await db.refresh(prescription)

    return prescription


# =============================================================================
# Pharmacy Transmission
# =============================================================================

async def create_prescription_transmission(
    db: AsyncSession,
    prescription_id: int,
    target_pharmacy_id: Optional[int] = None,
    priority: str = "routine",
    notes: Optional[str] = None,
) -> BasicPrescriptionTransmission:
    """Create a pharmacy transmission record"""
    # Generate transmission ID
    transmission_id = f"TX-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    transmission = BasicPrescriptionTransmission(
        prescription_id=prescription_id,
        transmission_id=transmission_id,
        target_pharmacy_id=target_pharmacy_id,
        status="queued",
        sent_at=datetime.utcnow(),
        notes=notes,
    )

    db.add(transmission)
    await db.commit()
    await db.refresh(transmission)

    return transmission


async def acknowledge_prescription_transmission(
    db: AsyncSession,
    transmission_id: str,
    pharmacy_name: str,
    estimated_ready_minutes: Optional[int] = None,
) -> BasicPrescriptionTransmission:
    """Acknowledge prescription transmission from pharmacy"""
    stmt = select(BasicPrescriptionTransmission).where(
        BasicPrescriptionTransmission.transmission_id == transmission_id
    )
    result = await db.execute(stmt)
    transmission = result.scalar_one_or_none()

    if not transmission:
        raise ValueError("Transmission not found")

    transmission.status = "acknowledged"
    transmission.acknowledged_at = datetime.utcnow()
    transmission.target_pharmacy_name = pharmacy_name

    if estimated_ready_minutes:
        from datetime import timedelta
        transmission.estimated_ready_time = datetime.utcnow() + timedelta(minutes=estimated_ready_minutes)

    await db.commit()
    await db.refresh(transmission)

    return transmission


# =============================================================================
# Prescription Print Log
# =============================================================================

async def log_prescription_print(
    db: AsyncSession,
    prescription_id: int,
    printed_by_id: int,
    printed_by_name: str,
    print_count: int = 1,
    included_barcode: bool = True,
    included_diagnosis: bool = True,
    included_instructions: bool = True,
    document_url: Optional[str] = None,
    document_expires_at: Optional[datetime] = None,
) -> PrescriptionPrintLog:
    """Log a prescription print event"""
    print_log = PrescriptionPrintLog(
        prescription_id=prescription_id,
        printed_by_id=printed_by_id,
        printed_by_name=printed_by_name,
        print_count=print_count,
        included_barcode=included_barcode,
        included_diagnosis=included_diagnosis,
        included_instructions=included_instructions,
        document_url=document_url,
        document_expires_at=document_expires_at,
    )

    db.add(print_log)
    await db.commit()
    await db.refresh(print_log)

    return print_log


# =============================================================================
# Helper Functions
# =============================================================================

async def _generate_prescription_number(db: AsyncSession) -> str:
    """Generate a unique prescription number"""
    # Format: RX-YYYY-XXXXXX
    year = datetime.utcnow().strftime("%Y")

    # Get count of prescriptions this year
    stmt = select(sql_func.count(Prescription.id)).where(
        sql_func.extract('year', Prescription.created_at) == int(year)
    )
    result = await db.execute(stmt)
    count = result.scalar_one() + 1

    # Format with leading zeros
    number = f"RX-{year}-{count:06d}"

    # Check for uniqueness (unlikely collision)
    existing_stmt = select(Prescription).where(Prescription.prescription_number == number)
    existing_result = await db.execute(existing_stmt)
    if existing_result.scalar_one_or_none():
        # Collision - try again with timestamp
        return f"RX-{year}-{uuid.uuid4().hex[:6].upper()}"

    return number


async def _generate_prescription_barcode(db: AsyncSession, prescription_number: str) -> str:
    """Generate a barcode for the prescription"""
    # Simple barcode generation using prescription number + timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{prescription_number}-{timestamp}"


# =============================================================================
# BPJS Coverage Status
# =============================================================================

async def get_bpjs_coverage_status(
    db: AsyncSession,
    drug_id: int,
) -> Dict:
    """Get BPJS coverage status for a drug"""
    drug_stmt = select(Drug).where(Drug.id == drug_id)
    drug_result = await db.execute(drug_stmt)
    drug = drug_result.scalar_one_or_none()

    if not drug:
        raise ValueError("Drug not found")

    # Determine coverage based on BPJS code
    is_covered = drug.bpjs_code is not None and drug.bpjs_code != ""

    coverage_type = "full" if is_covered else "not_covered"
    restrictions = []
    prior_auth_required = False

    # Add restrictions for certain drug classes
    if drug.is_narcotic:
        restrictions.append("Narcotic - additional documentation required")
        prior_auth_required = True

    if drug.is_antibiotic:
        restrictions.append("Antibiotic - may require prior authorization for certain types")

    return {
        "drug_name": drug.name,
        "generic_name": drug.generic_name,
        "bpjs_code": drug.bpjs_code,
        "is_covered": is_covered,
        "coverage_type": coverage_type,
        "restrictions": restrictions if restrictions else None,
        "prior_auth_required": prior_auth_required,
        "patient_cost_estimate": 0.0 if is_covered else None,
    }


# =============================================================================
# Dose Calculation Helper
# =============================================================================

async def calculate_dose(
    db: AsyncSession,
    drug_id: int,
    patient_weight_kg: Optional[float] = None,
    patient_age_years: Optional[int] = None,
    target_dose_mg: Optional[float] = None,
    concentration_mg_ml: Optional[float] = None,
) -> Dict:
    """Calculate dose based on patient parameters"""
    drug_stmt = select(Drug).where(Drug.id == drug_id)
    drug_result = await db.execute(drug_stmt)
    drug = drug_result.scalar_one_or_none()

    if not drug:
        raise ValueError("Drug not found")

    warnings = []
    max_dose_exceeded = False
    calculated_dose = None
    calculated_quantity = None
    instructions = None

    # Simple dose calculation example
    if target_dose_mg and patient_weight_kg:
        # Weight-based dosing
        calculated_dose = f"{target_dose_mg} mg/kg"

        total_dose_mg = target_dose_mg * patient_weight_kg

        if concentration_mg_ml:
            volume_ml = total_dose_mg / concentration_mg_ml
            calculated_quantity = int(volume_ml) + 1  # Round up with buffer
            instructions = f"Berikan {volume_ml:.1f} ml ({total_dose_mg:.1f} mg)"

            # Check for max dose
            if total_dose_mg > 1000:  # Example threshold
                warnings.append("Dose exceeds typical maximum - verify calculation")
                max_dose_exceeded = True

    return {
        "drug_name": drug.name,
        "calculated_dose": calculated_dose,
        "calculated_quantity": calculated_quantity,
        "concentration": f"{concentration_mg_ml} mg/ml" if concentration_mg_ml else None,
        "instructions": instructions,
        "warnings": warnings,
        "max_dose_exceeded": max_dose_exceeded,
    }
