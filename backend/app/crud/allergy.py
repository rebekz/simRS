"""Allergy CRUD operations for STORY-013: Allergy Tracking

This module provides CRUD operations for allergy tracking and alerting.
"""
from datetime import datetime, timezone, date
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.allergy import Allergy
from app.models.patient import Patient


async def get_allergy_by_id(
    db: AsyncSession,
    allergy_id: int,
) -> Optional[Allergy]:
    """Get allergy by ID."""
    stmt = select(Allergy).where(Allergy.id == allergy_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_patient_allergies(
    db: AsyncSession,
    patient_id: int,
    status_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    limit: int = 100,
) -> List[Allergy]:
    """
    Get all allergies for a patient with optional filters.

    Args:
        db: Database session
        patient_id: Patient ID
        status_filter: Filter by status (active, resolved, unconfirmed)
        severity_filter: Filter by severity
        type_filter: Filter by allergy type
        limit: Maximum results

    Returns:
        List of allergies ordered by severity (descending) and date (descending)
    """
    stmt = select(Allergy).where(Allergy.patient_id == patient_id)

    if status_filter:
        stmt = stmt.where(Allergy.status == status_filter)

    if severity_filter:
        stmt = stmt.where(Allergy.severity == severity_filter)

    if type_filter:
        stmt = stmt.where(Allergy.allergy_type == type_filter)

    # Order by severity (life_threatening first) and then by creation date
    severity_order = {
        'life_threatening': 0,
        'severe': 1,
        'moderate': 2,
        'mild': 3,
    }

    # Note: This is a simplified ordering. For production, consider using CASE in SQL
    stmt = stmt.order_by(desc(Allergy.created_at)).limit(limit)

    result = await db.execute(stmt)
    allergies = result.scalars().all()

    # Sort by severity in Python (more flexible)
    sorted_allergies = sorted(
        allergies,
        key=lambda a: (severity_order.get(a.severity, 99), a.created_at or datetime.min),
        reverse=True
    )

    return sorted_allergies


async def create_allergy(
    db: AsyncSession,
    patient_id: int,
    allergy_type: str,
    allergen: str,
    severity: str,
    reaction: str,
    recorded_by: int,
    allergen_code: Optional[str] = None,
    reaction_details: Optional[Dict[str, Any]] = None,
    status: str = "active",
    onset_date: Optional[date] = None,
    resolved_date: Optional[date] = None,
    source: str = "patient_reported",
    source_notes: Optional[str] = None,
    clinical_notes: Optional[str] = None,
    alternatives: Optional[List[str]] = None,
    verified_by: Optional[int] = None,
) -> Allergy:
    """Create a new allergy for a patient."""
    # Verify patient exists
    patient_stmt = select(Patient).where(Patient.id == patient_id)
    patient_result = await db.execute(patient_stmt)
    if not patient_result.scalar_one_or_none():
        raise ValueError(f"Patient with ID {patient_id} not found")

    allergy = Allergy(
        patient_id=patient_id,
        allergy_type=allergy_type,
        allergen=allergen,
        allergen_code=allergen_code,
        severity=severity,
        reaction=reaction,
        reaction_details=reaction_details,
        status=status,
        onset_date=onset_date,
        resolved_date=resolved_date,
        source=source,
        source_notes=source_notes,
        clinical_notes=clinical_notes,
        alternatives=alternatives,
        recorded_by=recorded_by,
        verified_by=verified_by,
        verified_at=datetime.now(timezone.utc) if verified_by else None,
    )

    db.add(allergy)
    await db.commit()
    await db.refresh(allergy)
    return allergy


async def update_allergy(
    db: AsyncSession,
    allergy_id: int,
    allergy_type: Optional[str] = None,
    allergen: Optional[str] = None,
    allergen_code: Optional[str] = None,
    severity: Optional[str] = None,
    reaction: Optional[str] = None,
    reaction_details: Optional[Dict[str, Any]] = None,
    status: Optional[str] = None,
    onset_date: Optional[date] = None,
    resolved_date: Optional[date] = None,
    source: Optional[str] = None,
    source_notes: Optional[str] = None,
    clinical_notes: Optional[str] = None,
    alternatives: Optional[List[str]] = None,
    verified_by: Optional[int] = None,
) -> Optional[Allergy]:
    """Update an allergy."""
    stmt = select(Allergy).where(Allergy.id == allergy_id)
    result = await db.execute(stmt)
    allergy = result.scalar_one_or_none()

    if not allergy:
        return None

    if allergy_type is not None:
        allergy.allergy_type = allergy_type
    if allergen is not None:
        allergy.allergen = allergen
    if allergen_code is not None:
        allergy.allergen_code = allergen_code
    if severity is not None:
        allergy.severity = severity
    if reaction is not None:
        allergy.reaction = reaction
    if reaction_details is not None:
        allergy.reaction_details = reaction_details
    if status is not None:
        allergy.status = status
    if onset_date is not None:
        allergy.onset_date = onset_date
    if resolved_date is not None:
        allergy.resolved_date = resolved_date
    if source is not None:
        allergy.source = source
    if source_notes is not None:
        allergy.source_notes = source_notes
    if clinical_notes is not None:
        allergy.clinical_notes = clinical_notes
    if alternatives is not None:
        allergy.alternatives = alternatives
    if verified_by is not None:
        allergy.verified_by = verified_by
        allergy.verified_at = datetime.now(timezone.utc)

    allergy.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(allergy)
    return allergy


async def delete_allergy(
    db: AsyncSession,
    allergy_id: int,
) -> bool:
    """Delete an allergy (hard delete - allergies are critical data)."""
    stmt = select(Allergy).where(Allergy.id == allergy_id)
    result = await db.execute(stmt)
    allergy = result.scalar_one_or_none()

    if allergy:
        await db.delete(allergy)
        await db.commit()
        return True
    return False


async def check_allergies_against_medications(
    db: AsyncSession,
    patient_id: int,
    medications: List[str],
) -> tuple[List[Dict[str, Any]], bool]:
    """
    Check if medications interact with patient allergies.

    Args:
        db: Database session
        patient_id: Patient ID
        medications: List of medication names or codes to check

    Returns:
        Tuple of (list of warnings, can_prescribe flag)
    """
    allergies = await get_patient_allergies(
        db=db,
        patient_id=patient_id,
        status_filter="active",
    )

    warnings = []
    can_prescribe = True

    for allergy in allergies:
        for medication in medications:
            # Simple matching: check if allergen is in medication name or vice versa
            # In production, this would use drug databases (RxNorm, drug interaction APIs)
            medication_lower = medication.lower()
            allergen_lower = allergy.allergen.lower()

            if (
                allergen_lower in medication_lower or
                medication_lower in allergen_lower or
                (allergy.allergen_code and allergy.allergen_code.lower() in medication_lower)
            ):
                is_contraindicated = allergy.severity in ['severe', 'life_threatening']
                if is_contraindicated:
                    can_prescribe = False

                warnings.append({
                    "allergy_id": allergy.id,
                    "allergen": allergy.allergen,
                    "allergy_type": allergy.allergy_type,
                    "severity": allergy.severity,
                    "reaction": allergy.reaction,
                    "matched_medication": medication,
                    "is_contraindicated": is_contraindicated,
                })

    return warnings, can_prescribe


async def get_patient_allergy_summary(
    db: AsyncSession,
    patient_id: int,
) -> Dict[str, Any]:
    """
    Get allergy summary for a patient.

    Returns comprehensive statistics and alerts for clinical display.
    """
    allergies = await get_patient_allergies(db, patient_id, limit=1000)

    # Check if patient has NKA (No Known Allergies)
    # This would be a separate table/flag in production
    no_known_allergies = len(allergies) == 0

    # Count by various dimensions
    active_allergies = sum(1 for a in allergies if a.status == "active")
    severe_allergies = sum(
        1 for a in allergies
        if a.status == "active" and a.severity in ["moderate", "severe", "life_threatening"]
    )
    drug_allergies = sum(1 for a in allergies if a.allergy_type == "drug" and a.status == "active")
    food_allergies = sum(1 for a in allergies if a.allergy_type == "food" and a.status == "active")
    environmental_allergies = sum(
        1 for a in allergies if a.allergy_type == "environmental" and a.status == "active"
    )

    # Determine if alert is required
    requires_alert = severe_allergies > 0
    alert_message = None
    if requires_alert:
        life_threatening = sum(
            1 for a in allergies
            if a.severity == "life_threatening" and a.status == "active"
        )
        if life_threatening > 0:
            alert_message = f"PERINGATAN: {life_threatening} alergi yang mengancam jiwa"
        else:
            alert_message = f"PERINGATAN: {severe_allergies} alergi parah"

    return {
        "patient_id": patient_id,
        "has_allergies": len(allergies) > 0,
        "no_known_allergies": no_known_allergies,
        "total_allergies": len(allergies),
        "active_allergies": active_allergies,
        "severe_allergies": severe_allergies,
        "drug_allergies": drug_allergies,
        "food_allergies": food_allergies,
        "environmental_allergies": environmental_allergies,
        "requires_alert": requires_alert,
        "alert_message": alert_message,
    }
