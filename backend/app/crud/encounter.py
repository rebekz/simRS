"""Encounter CRUD operations for STORY-011: Patient History View

This module provides async CRUD operations for encounters, diagnoses, and treatments.
"""
from typing import List, Optional, Tuple, Dict, Any
from datetime import date
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.encounter import Encounter, Diagnosis, Treatment
from app.models.patient import Patient
from app.schemas.encounter import (
    EncounterCreate,
    EncounterUpdate,
    DiagnosisCreate,
    TreatmentCreate
)


async def get_encounter_by_id(db: AsyncSession, encounter_id: int) -> Optional[Encounter]:
    """Get encounter by ID with diagnoses and treatments"""
    result = await db.execute(
        select(Encounter)
        .options(selectinload(Encounter.diagnoses), selectinload(Encounter.treatments))
        .where(Encounter.id == encounter_id)
    )
    return result.scalars().first()


async def get_encounters_by_patient(
    db: AsyncSession,
    patient_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> Tuple[List[Encounter], int]:
    """Get encounters by patient ID with pagination"""
    query = select(Encounter).options(selectinload(Encounter.diagnoses), selectinload(Encounter.treatments))

    if status:
        query = query.where(Encounter.status == status)

    # Get total count
    count_query = select(func.count(Encounter.id)).where(Encounter.patient_id == patient_id)
    if status:
        count_query = count_query.where(Encounter.status == status)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.where(Encounter.patient_id == patient_id).order_by(desc(Encounter.encounter_date), desc(Encounter.start_time))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    encounters = result.scalars().all()

    return list(encounters), total


async def create_encounter(db: AsyncSession, encounter_in: EncounterCreate) -> Encounter:
    """Create a new encounter with diagnoses and treatments"""
    # Verify patient exists
    patient_result = await db.execute(select(Patient).where(Patient.id == encounter_in.patient_id))
    patient = patient_result.scalars().first()
    if not patient:
        raise ValueError(f"Patient with ID {encounter_in.patient_id} not found")

    # Create encounter
    encounter_data = encounter_in.model_dump(exclude={'diagnoses', 'treatments'})
    encounter = Encounter(**encounter_data)
    db.add(encounter)
    await db.flush()  # Get the ID before adding related objects

    # Add diagnoses
    if encounter_in.diagnoses:
        for diagnosis_in in encounter_in.diagnoses:
            diagnosis = Diagnosis(
                encounter_id=encounter.id,
                **diagnosis_in.model_dump()
            )
            db.add(diagnosis)

    # Add treatments
    if encounter_in.treatments:
        for treatment_in in encounter_in.treatments:
            treatment = Treatment(
                encounter_id=encounter.id,
                **treatment_in.model_dump()
            )
            db.add(treatment)

    await db.commit()
    await db.refresh(encounter)

    # Load relationships
    encounter = await get_encounter_by_id(db, encounter.id)
    return encounter


async def update_encounter(
    db: AsyncSession,
    encounter_id: int,
    encounter_in: EncounterUpdate
) -> Optional[Encounter]:
    """Update an existing encounter"""
    encounter = await get_encounter_by_id(db, encounter_id)
    if not encounter:
        return None

    # Update encounter fields
    update_data = encounter_in.model_dump(exclude_unset=True, exclude={'diagnoses', 'treatments'})

    for field, value in update_data.items():
        setattr(encounter, field, value)

    # Handle diagnoses update
    if encounter_in.diagnoses is not None:
        # Remove existing diagnoses
        for diagnosis in encounter.diagnoses:
            await db.delete(diagnosis)

        # Add new diagnoses
        for diagnosis_in in encounter_in.diagnoses:
            diagnosis = Diagnosis(
                encounter_id=encounter.id,
                **diagnosis_in.model_dump()
            )
            db.add(diagnosis)

    # Handle treatments update
    if encounter_in.treatments is not None:
        # Remove existing treatments
        for treatment in encounter.treatments:
            await db.delete(treatment)

        # Add new treatments
        for treatment_in in encounter_in.treatments:
            treatment = Treatment(
                encounter_id=encounter.id,
                **treatment_in.model_dump()
            )
            db.add(treatment)

    await db.commit()
    await db.refresh(encounter)

    # Reload with relationships
    encounter = await get_encounter_by_id(db, encounter_id)
    return encounter


async def get_patient_history(db: AsyncSession, patient_id: int) -> Dict[str, Any]:
    """Get comprehensive patient history"""
    # Get patient info
    patient_result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = patient_result.scalars().first()
    if not patient:
        raise ValueError(f"Patient with ID {patient_id} not found")

    # Get all encounters with diagnoses and treatments
    encounters, total = await get_encounters_by_patient(db, patient_id, skip=0, limit=1000)

    # Collect all diagnoses
    all_diagnoses = []
    chronic_conditions = []

    for encounter in encounters:
        for diagnosis in encounter.diagnoses:
            diag_data = {
                "id": diagnosis.id,
                "encounter_id": diagnosis.encounter_id,
                "icd_10_code": diagnosis.icd_10_code,
                "diagnosis_name": diagnosis.diagnosis_name,
                "diagnosis_type": diagnosis.diagnosis_type,
                "is_chronic": diagnosis.is_chronic,
                "notes": diagnosis.notes,
                "created_at": diagnosis.created_at,
                "updated_at": diagnosis.updated_at,
                "encounter_date": encounter.encounter_date,
                "encounter_type": encounter.encounter_type
            }
            all_diagnoses.append(diag_data)
            if diagnosis.is_chronic:
                chronic_conditions.append(diag_data)

    # Collect all treatments (active and all)
    active_treatments = []
    all_treatments = []

    for encounter in encounters:
        for treatment in encounter.treatments:
            treatment_data = {
                "id": treatment.id,
                "encounter_id": treatment.encounter_id,
                "treatment_type": treatment.treatment_type,
                "treatment_name": treatment.treatment_name,
                "dosage": treatment.dosage,
                "frequency": treatment.frequency,
                "duration": treatment.duration,
                "notes": treatment.notes,
                "is_active": treatment.is_active,
                "created_at": treatment.created_at,
                "updated_at": treatment.updated_at,
                "encounter_date": encounter.encounter_date,
                "encounter_type": encounter.encounter_type
            }
            all_treatments.append(treatment_data)
            if treatment.is_active:
                active_treatments.append(treatment_data)

    # Get last visit info
    last_visit_date = None
    last_department = None
    last_doctor_id = None

    if encounters:
        last_encounter = encounters[0]  # Already sorted by date desc
        last_visit_date = last_encounter.encounter_date
        last_department = last_encounter.department
        last_doctor_id = last_encounter.doctor_id

    return {
        "patient_id": patient.id,
        "medical_record_number": patient.medical_record_number,
        "full_name": patient.full_name,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender.value,
        "total_encounters": total,
        "encounters": encounters,
        "all_diagnoses": all_diagnoses,
        "chronic_conditions": chronic_conditions,
        "active_treatments": active_treatments,
        "all_treatments": all_treatments,
        "last_visit_date": last_visit_date,
        "last_department": last_department,
        "last_doctor_id": last_doctor_id,
        "total_diagnoses": len(all_diagnoses),
        "total_treatments": len(all_treatments),
        "chronic_condition_count": len(chronic_conditions)
    }


async def count_encounters(db: AsyncSession, patient_id: Optional[int] = None) -> int:
    """Count encounters, optionally filtered by patient"""
    query = select(func.count(Encounter.id))
    if patient_id:
        query = query.where(Encounter.patient_id == patient_id)

    result = await db.execute(query)
    return result.scalar()
