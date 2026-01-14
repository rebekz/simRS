"""Medication List CRUD Operations for STORY-014

This module provides CRUD operations for:
- Patient medication tracking
- Drug interaction checking
- Medication reconciliation
- Duplicate therapy detection
"""
from typing import List, Optional, Tuple
from datetime import date, datetime
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.medication import (
    PatientMedication, DrugInteraction, CustomInteractionRule,
    MedicationReconciliation, MedicationReconciliationItem, MedicationAdministration
)
from app.models.patient import Patient
from app.models.user import User
from app.models.inventory import Drug
from app.schemas.medication import (
    MedicationStatus, InteractionSeverity, InteractionType,
    MedicationCreate, MedicationUpdate,
    DrugInteractionCheckRequest, DrugInteractionCheckResponse
)
import json


# =============================================================================
# Medication CRUD Operations
# =============================================================================

async def get_patient_medications(
    db: AsyncSession,
    patient_id: int,
    status: Optional[MedicationStatus] = None,
    include_past: bool = False,
) -> Tuple[List[PatientMedication], int]:
    """Get medications for a patient"""
    # Build query conditions
    conditions = [PatientMedication.patient_id == patient_id]

    if status:
        conditions.append(PatientMedication.status == status)
    elif not include_past:
        conditions.append(PatientMedication.status == MedicationStatus.ACTIVE)

    stmt = (
        select(PatientMedication)
        .options(
            selectinload(PatientMedication.drug),
            selectinload(PatientMedication.prescriber),
            selectinload(PatientMedication.encounter),
        )
        .where(and_(*conditions))
        .order_by(PatientMedication.created_at.desc())
    )

    result = await db.execute(stmt)
    medications = result.scalars().all()

    return list(medications), len(medications)


async def get_medication_by_id(
    db: AsyncSession,
    medication_id: int,
) -> Optional[PatientMedication]:
    """Get medication by ID"""
    stmt = (
        select(PatientMedication)
        .options(
            selectinload(PatientMedication.drug),
            selectinload(PatientMedication.prescriber),
            selectinload(PatientMedication.patient),
        )
        .where(PatientMedication.id == medication_id)
    )

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_patient_medication(
    db: AsyncSession,
    medication_data: MedicationCreate,
    patient_id: int,
    created_by: int,
) -> PatientMedication:
    """Create a new patient medication record"""
    # Get drug details
    drug_stmt = select(Drug).where(Drug.id == medication_data.drug_id)
    drug_result = await db.execute(drug_stmt)
    drug = drug_result.scalar_one_or_none()

    if not drug:
        raise ValueError(f"Drug with ID {medication_data.drug_id} not found")

    medication = PatientMedication(
        patient_id=patient_id,
        encounter_id=medication_data.encounter_id,
        drug_id=medication_data.drug_id,
        drug_name=medication_data.drug_name,
        generic_name=medication_data.generic_name,
        dosage=medication_data.dosage,
        dose_unit=medication_data.dose_unit,
        frequency=medication_data.frequency,
        route=medication_data.route.value if medication_data.route else None,
        indication=medication_data.indication,
        prescriber_id=medication_data.prescriber_id or created_by,
        prescription_date=medication_data.prescription_date or date.today(),
        status=medication_data.status,
        start_date=medication_data.start_date or date.today(),
        end_date=medication_data.end_date,
        notes=medication_data.notes,
        batch_number=medication_data.batch_number,
        manufacturer=medication_data.manufacturer or drug.manufacturer,
    )

    db.add(medication)
    await db.commit()
    await db.refresh(medication)

    # Load relationships
    await db.refresh(medication, ["drug", "prescriber"])

    return medication


async def update_patient_medication(
    db: AsyncSession,
    medication_id: int,
    medication_data: MedicationUpdate,
) -> Optional[PatientMedication]:
    """Update patient medication"""
    medication = await get_medication_by_id(db, medication_id)
    if not medication:
        return None

    if medication_data.dosage is not None:
        medication.dosage = medication_data.dosage
    if medication_data.dose_unit is not None:
        medication.dose_unit = medication_data.dose_unit
    if medication_data.frequency is not None:
        medication.frequency = medication_data.frequency
    if medication_data.route is not None:
        medication.route = medication_data.route.value
    if medication_data.indication is not None:
        medication.indication = medication_data.indication
    if medication_data.status is not None:
        medication.status = medication_data.status
        if medication_data.status != MedicationStatus.ACTIVE and medication_data.end_date is None:
            medication.end_date = date.today()
            medication.discontinuation_reason = medication_data.discontinuation_reason
    if medication_data.end_date is not None:
        medication.end_date = medication_data.end_date
    if medication_data.notes is not None:
        medication.notes = medication_data.notes

    await db.commit()
    await db.refresh(medication)

    return medication


async def stop_patient_medication(
    db: AsyncSession,
    medication_id: int,
    reason: str,
) -> Optional[PatientMedication]:
    """Stop a patient medication"""
    medication = await get_medication_by_id(db, medication_id)
    if not medication:
        return None

    medication.status = MedicationStatus.STOPPED
    medication.end_date = date.today()
    medication.discontinuation_reason = reason

    await db.commit()
    await db.refresh(medication)

    return medication


# =============================================================================
# Drug Interaction Checking
# =============================================================================

async def check_drug_interactions(
    db: AsyncSession,
    patient_id: int,
    drug_ids: List[int],
) -> DrugInteractionCheckResponse:
    """Check for drug interactions for a patient"""
    interactions = []
    severity_count = {
        InteractionSeverity.CONTRAINDICATED.value: 0,
        InteractionSeverity.SEVERE.value: 0,
        InteractionSeverity.MODERATE.value: 0,
        InteractionSeverity.MILD.value: 0,
    }

    # Check drug-drug interactions
    for drug_id in drug_ids:
        stmt = select(DrugInteraction).where(
            and_(
                DrugInteraction.drug_1_id == drug_id,
                DrugInteraction.drug_2_id.in_(drug_ids),
                DrugInteraction.interaction_type == InteractionType.DRUG_DRUG,
            )
        )
        result = await db.execute(stmt)
        dd_interactions = result.scalars().all()

        for interaction in dd_interactions:
            from app.schemas.medication import DrugInteraction as DrugInteractionSchema
            interactions.append(DrugInteractionSchema(
                id=interaction.id,
                interaction_type=interaction.interaction_type,
                severity=interaction.severity,
                drug_1_id=interaction.drug_1_id,
                drug_1_name=interaction.drug_1_name,
                drug_2_id=interaction.drug_2_id,
                drug_2_name=interaction.drug_2_name,
                description=interaction.description,
                recommendation=interaction.recommendation,
                references=json.loads(interaction.references) if interaction.references else None,
                requires_override=interaction.requires_override,
            ))
            severity_count[interaction.severity.value] += 1

    # Check custom rules
    for drug_id in drug_ids:
        stmt = select(CustomInteractionRule).where(
            and_(
                CustomInteractionRule.is_active == True,
                CustomInteractionRule.drug_ids.contains(str(drug_id)),
            )
        )
        result = await db.execute(stmt)
        custom_rules = result.scalars().all()

        for rule in custom_rules:
            # Check if all drugs in the rule are present
            rule_drugs = json.loads(rule.drug_ids)
            if all(d in drug_ids for d in rule_drugs):
                from app.schemas.medication import DrugInteraction as DrugInteractionSchema
                interactions.append(DrugInteractionSchema(
                    id=rule.id,
                    interaction_type=InteractionType.DRUG_DRUG,
                    severity=rule.severity,
                    drug_1_id=rule_drugs[0],
                    drug_1_name=json.loads(rule.drug_names)[0] if rule.drug_names else "Multiple",
                    drug_2_id=rule_drugs[1] if len(rule_drugs) > 1 else None,
                    drug_2_name=json.loads(rule.drug_names)[1] if rule.drug_names and len(rule.drug_names) > 1 else None,
                    description=rule.description,
                    recommendation=rule.action_required or "Review this medication combination",
                    requires_override=True,
                ))
                severity_count[rule.severity.value] += 1

    return DrugInteractionCheckResponse(
        patient_id=patient_id,
        has_interactions=len(interactions) > 0,
        interactions=interactions,
        total_interactions=len(interactions),
        by_severity={k: v for k, v in severity_count.items() if v > 0},
    )


async def check_duplicate_therapy(
    db: AsyncSession,
    drug_ids: List[int],
) -> List[dict]:
    """Check for duplicate therapies"""
    duplicates = []

    # Get drugs with their therapeutic classes
    stmt = select(Drug).where(Drug.id.in_(drug_ids))
    result = await db.execute(stmt)
    drugs = result.scalars().all()

    # Group by therapeutic class
    therapeutic_classes = {}
    for drug in drugs:
        if drug.therapeutic_class:
            if drug.therapeutic_class not in therapeutic_classes:
                therapeutic_classes[drug.therapeutic_class] = []
            therapeutic_classes[drug.therapeutic_class].append(drug)

    # Find duplicates (same therapeutic class, different drugs)
    for therapeutic_class, class_drugs in therapeutic_classes.items():
        if len(class_drugs) > 1:
            for i, drug1 in enumerate(class_drugs):
                for drug2 in class_drugs[i+1:]:
                    # Check if they have different generic names (different drugs)
                    if drug1.generic_name != drug2.generic_name:
                        duplicates.append({
                            "drug_1_id": drug1.id,
                            "drug_1_name": drug1.generic_name,
                            "drug_2_id": drug2.id,
                            "drug_2_name": drug2.generic_name,
                            "therapeutic_class": therapeutic_class,
                            "severity": "similar_therapy" if drug1.therapeutic_class else "exact_duplicate",
                            "recommendation": "Review for potential duplicate therapy. Consider consolidating to a single agent if appropriate.",
                        })

    return duplicates


# =============================================================================
# Medication Reconciliation
# =============================================================================

async def create_medication_reconciliation(
    db: AsyncSession,
    patient_id: int,
    encounter_id: int,
    source: str,
    medications: List[dict],
    reconciled_by: int,
    notes: Optional[str] = None,
) -> MedicationReconciliation:
    """Create a medication reconciliation record"""
    reconciliation = MedicationReconciliation(
        patient_id=patient_id,
        encounter_id=encounter_id,
        reconciliation_date=date.today(),
        source=source,
        total_medications=len(medications),
        discrepancies_found=sum(1 for m in medications if m.get("discrepancies")),
        medications_continued=sum(1 for m in medications if m.get("current_status") == "taking"),
        medications_modified=sum(1 for m in medications if m.get("current_status") == "changed_dose"),
        medications_stopped=sum(1 for m in medications if m.get("current_status") == "stopped"),
        medications_added=sum(1 for m in medications if m.get("current_status") == "not_taking"),
        reconciled_by=reconciled_by,
        notes=notes,
    )

    db.add(reconciliation)
    await db.flush()  # Get the ID before creating items

    # Create reconciliation items
    for med_data in medications:
        item = MedicationReconciliationItem(
            reconciliation_id=reconciliation.id,
            patient_medication_id=med_data.get("medication_id"),
            drug_name=med_data["drug_name"],
            current_status=med_data["current_status"],
            new_dosage=med_data.get("new_dosage"),
            new_frequency=med_data.get("new_frequency"),
            discrepancies=json.dumps(med_data.get("discrepancies", [])),
            notes=med_data.get("notes"),
        )
        db.add(item)

    await db.commit()
    await db.refresh(reconciliation)

    return reconciliation


async def get_medication_reconciliations(
    db: AsyncSession,
    patient_id: int,
    limit: int = 10,
) -> List[MedicationReconciliation]:
    """Get medication reconciliation history for a patient"""
    stmt = (
        select(MedicationReconciliation)
        .options(selectinload(MedicationReconciliation.reconciler))
        .where(MedicationReconciliation.patient_id == patient_id)
        .order_by(MedicationReconciliation.reconciliation_date.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


# =============================================================================
# Medication History
# =============================================================================

async def get_medication_history(
    db: AsyncSession,
    patient_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> Tuple[List[PatientMedication], int]:
    """Get complete medication history for a patient"""
    conditions = [PatientMedication.patient_id == patient_id]

    if date_from:
        conditions.append(PatientMedication.start_date >= date_from)
    if date_to:
        conditions.append(PatientMedication.start_date <= date_to)

    stmt = (
        select(PatientMedication)
        .options(
            selectinload(PatientMedication.drug),
            selectinload(PatientMedication.prescriber),
            selectinload(PatientMedication.encounter),
        )
        .where(and_(*conditions))
        .order_by(PatientMedication.start_date.desc())
    )

    result = await db.execute(stmt)
    medications = result.scalars().all()

    return list(medications), len(medications)
