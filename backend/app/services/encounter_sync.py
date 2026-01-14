"""Encounter sync service for SATUSEHAT FHIR R4 integration (STORY-035).

This module provides functions to sync encounter data with SATUSEHAT,
converting internal encounter data to FHIR Encounter format.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.satusehat import SATUSEHATClient, SATUSEHATError
from app.models.encounter import Encounter
from app.models.patient import Patient
from app.models.user import User

logger = logging.getLogger(__name__)


# =============================================================================
# FHIR Encounter Resource Builder
# =============================================================================

def build_fhir_encounter_resource(
    encounter: Encounter,
    patient: Patient,
    doctor: Optional[User] = None,
    organization_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build FHIR Encounter resource from internal encounter model.

    Args:
        encounter: Encounter model instance
        patient: Patient model instance
        doctor: Doctor user instance
        organization_id: SATUSEHAT Organization resource ID

    Returns:
        FHIR Encounter resource dictionary
    """
    # Map encounter type to FHIR class system
    encounter_class_mapping = {
        "outpatient": "amb",
        "inpatient": "imp",
        "emergency": "emer",
        "telephone": "amb",
        "home_visit": "home",
    }

    encounter_class = encounter_class_mapping.get(
        encounter.encounter_type.lower(),
        "amb"  # Default to ambulatory
    )

    # Map encounter status to FHIR status
    status_mapping = {
        "active": "in_progress",
        "completed": "finished",
        "cancelled": "cancelled",
        "scheduled": "planned",
    }

    fhir_status = status_mapping.get(
        encounter.status.lower(),
        "in_progress"
    )

    # Build FHIR Encounter resource
    fhir_encounter = {
        "resourceType": "Encounter",
        "status": fhir_status,
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": encounter_class,
            "display": _get_class_display(encounter_class),
        },
        "subject": {
            "reference": f"Patient/{patient.satusehat_patient_id or patient.id}",
            "display": patient.full_name,
        },
    }

    # Add period (start and end time)
    period = {}
    if encounter.start_time:
        period["start"] = encounter.start_time.isoformat()

    if encounter.end_time:
        period["end"] = encounter.end_time.isoformat()

    if period:
        fhir_encounter["period"] = period

    # Add participant references
    participants = []

    # Add doctor as participant
    if doctor:
        participants.append({
            "type": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                    "code": "ATND",
                    "display": "attender",
                }]
            }],
            "individual": {
                "reference": f"Practitioner/{doctor.id}",
                "display": doctor.full_name,
            }
        })

    if participants:
        fhir_encounter["participant"] = participants

    # Add managing organization
    if organization_id:
        fhir_encounter["serviceProvider"] = {
            "reference": f"Organization/{organization_id}",
            "display": "Healthcare Facility",
        }

    # Add department/location
    if encounter.department:
        fhir_encounter["location"] = [{
            "location": {
                "display": encounter.department,
            }
        }]

    # Add priority if urgent
    if encounter.is_urgent:
        fhir_encounter["priority"] = {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                "code": "URG",
                "display": "urgent",
            }]
        }

    # Add reason for visit (chief complaint)
    if encounter.chief_complaint:
        fhir_encounter["reasonCode"] = [{
            "text": encounter.chief_complaint,
        }]

    # Add internal encounter ID as extension
    if "extension" not in fhir_encounter:
        fhir_encounter["extension"] = []

    fhir_encounter["extension"].append({
        "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/encounterInternalId",
        "valueString": str(encounter.id),
    })

    # Add BPJS SEP number if available
    if encounter.bpjs_sep_number:
        fhir_encounter["identifier"] = [{
            "use": "official",
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "VN",
                    "display": "Visit number",
                }]
            },
            "system": "https://fhir.kemkes.go.id/id/bpjs-sep",
            "value": encounter.bpjs_sep_number,
        }]

    return fhir_encounter


def _get_class_display(encounter_class: str) -> str:
    """Get display name for encounter class."""
    display_names = {
        "amb": "Ambulatory",
        "imp": "Inpatient",
        "emer": "Emergency",
        "home": "Home Visit",
    }
    return display_names.get(encounter_class, "Ambulatory")


# =============================================================================
# Encounter Sync Operations
# =============================================================================

async def sync_encounter_to_satusehat(
    db: AsyncSession,
    encounter_id: int,
    satusehat_client: SATUSEHATClient,
    organization_id: Optional[str] = None,
    force_update: bool = False,
) -> Dict[str, Any]:
    """
    Sync an encounter to SATUSEHAT.

    Args:
        db: Database session
        encounter_id: Encounter ID to sync
        satusehat_client: SATUSEHAT API client
        organization_id: SATUSEHAT Organization resource ID
        force_update: Force update even if data unchanged

    Returns:
        Sync result dictionary

    Raises:
        ValueError: If encounter not found
        SATUSEHATError: If sync fails
    """
    try:
        # Get encounter with related data
        encounter_result = await db.execute(
            select(Encounter)
            .filter(Encounter.id == encounter_id)
        )
        encounter = encounter_result.scalar_one_or_none()

        if not encounter:
            return {
                "success": False,
                "message": f"Encounter {encounter_id} not found",
                "encounter_id": encounter_id,
            }

        # Get patient
        patient_result = await db.execute(
            select(Patient).filter(Patient.id == encounter.patient_id)
        )
        patient = patient_result.scalar_one_or_none()

        if not patient:
            return {
                "success": False,
                "message": f"Patient {encounter.patient_id} not found",
                "encounter_id": encounter_id,
            }

        # Get doctor if present
        doctor = None
        if encounter.doctor_id:
            doctor_result = await db.execute(
                select(User).filter(User.id == encounter.doctor_id)
            )
            doctor = doctor_result.scalar_one_or_none()

        # Build FHIR Encounter resource
        fhir_encounter = build_fhir_encounter_resource(
            encounter,
            patient,
            doctor,
            organization_id
        )

        # Check if encounter already has SATUSEHAT ID
        if encounter.satusehat_encounter_id and not force_update:
            # Update existing encounter
            logger.info(f"Updating existing SATUSEHAT encounter: {encounter.satusehat_encounter_id}")
            result = await satusehat_client._make_fhir_request(
                "PUT",
                "Encounter",
                resource_id=encounter.satusehat_encounter_id,
                data=fhir_encounter,
            )
            action = "update"
        else:
            # Create new encounter
            logger.info(f"Creating new SATUSEHAT encounter for: {encounter_id}")
            result = await satusehat_client._make_fhir_request(
                "POST",
                "Encounter",
                data=fhir_encounter,
            )
            action = "create"

            # Store SATUSEHAT encounter ID
            encounter.satusehat_encounter_id = result.get("id")
            await db.commit()

        logger.info(f"Encounter {encounter_id} synced to SATUSEHAT (ID: {result.get('id')})")

        return {
            "success": True,
            "message": "Encounter synced successfully",
            "encounter_id": encounter_id,
            "satusehat_encounter_id": result.get("id"),
            "action": action,
            "fhir_resource": result,
        }

    except SATUSEHATError as e:
        logger.error(f"Failed to sync encounter {encounter_id} to SATUSEHAT: {e}")
        return {
            "success": False,
            "message": f"Failed to sync encounter: {e.message}",
            "encounter_id": encounter_id,
            "error": str(e),
        }

    except Exception as e:
        logger.exception(f"Unexpected error syncing encounter {encounter_id} to SATUSEHAT")
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "encounter_id": encounter_id,
            "error": str(e),
        }


async def get_encounter_from_satusehat(
    satusehat_client: SATUSEHATClient,
    satusehat_encounter_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve encounter from SATUSEHAT.

    Args:
        satusehat_client: SATUSEHAT API client
        satusehat_encounter_id: SATUSEHAT Encounter resource ID

    Returns:
        FHIR Encounter resource or None if not found

    Raises:
        SATUSEHATError: If retrieval fails
    """
    try:
        result = await satusehat_client._make_fhir_request(
            "GET",
            "Encounter",
            resource_id=satusehat_encounter_id,
        )
        return result

    except SATUSEHATError as e:
        if "not found" in str(e.message).lower():
            return None
        raise


# =============================================================================
# Auto-sync Triggers
# =============================================================================

async def trigger_encounter_sync_on_create(
    db: AsyncSession,
    encounter_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Trigger SATUSEHAT sync when encounter is created.

    This should be called after an encounter is created to automatically
    sync the encounter data to SATUSEHAT.

    Args:
        db: Database session
        encounter_id: Encounter ID that was created

    Returns:
        Sync result or None if sync failed
    """
    try:
        async with SATUSEHATClient() as client:
            return await sync_encounter_to_satusehat(db, encounter_id, client)

    except Exception as e:
        logger.exception(f"Failed to trigger encounter sync for encounter {encounter_id}")
        return None


async def trigger_encounter_sync_on_update(
    db: AsyncSession,
    encounter_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Trigger SATUSEHAT sync when encounter is updated.

    This should be called after an encounter's data is updated
    to automatically sync the changes to SATUSEHAT.

    Args:
        db: Database session
        encounter_id: Encounter ID that was updated

    Returns:
        Sync result or None if sync failed
    """
    try:
        async with SATUSEHATClient() as client:
            return await sync_encounter_to_satusehat(db, encounter_id, client, force_update=True)

    except Exception as e:
        logger.exception(f"Failed to trigger encounter sync for encounter {encounter_id}")
        return None


async def trigger_encounter_sync_on_completion(
    db: AsyncSession,
    encounter_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Trigger SATUSEHAT sync when encounter is completed.

    This should be called when an encounter is marked as completed
    to sync the final state to SATUSEHAT.

    Args:
        db: Database session
        encounter_id: Encounter ID that was completed

    Returns:
        Sync result or None if sync failed
    """
    try:
        async with SATUSEHATClient() as client:
            return await sync_encounter_to_satusehat(db, encounter_id, client, force_update=True)

    except Exception as e:
        logger.exception(f"Failed to trigger encounter sync for encounter {encounter_id}")
        return None


# =============================================================================
# Encounter Data Validation
# =============================================================================

def validate_encounter_for_sync(encounter: Encounter, patient: Patient) -> tuple[bool, List[str]]:
    """
    Validate encounter data for SATUSEHAT sync.

    Args:
        encounter: Encounter model instance
        patient: Patient model instance

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    if not encounter.encounter_type:
        errors.append("Encounter type is required")

    if not encounter.encounter_date:
        errors.append("Encounter date is required")

    if not encounter.start_time:
        errors.append("Start time is required")

    # Check patient has SATUSEHAT ID
    if not patient.satusehat_patient_id:
        errors.append("Patient must be synced to SATUSEHAT first")

    # Validate encounter type
    valid_types = ["outpatient", "inpatient", "emergency", "telephone", "home_visit"]
    if encounter.encounter_type.lower() not in valid_types:
        errors.append(f"Invalid encounter type. Must be one of: {', '.join(valid_types)}")

    # Validate status
    valid_statuses = ["active", "completed", "cancelled", "scheduled"]
    if encounter.status.lower() not in valid_statuses:
        errors.append(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    return len(errors) == 0, errors
