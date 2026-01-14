"""Condition sync service for SATUSEHAT FHIR R4 integration (STORY-036).

This module provides functions to sync diagnosis/condition data with SATUSEHAT,
converting internal diagnosis data to FHIR Condition format.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.satusehat import SATUSEHATClient, SATUSEHATError
from app.models.encounter import Diagnosis, Encounter
from app.models.patient import Patient

logger = logging.getLogger(__name__)


# =============================================================================
# FHIR Condition Resource Builder
# =============================================================================

def build_fhir_condition_resource(
    diagnosis: Diagnosis,
    encounter: Encounter,
    patient: Patient,
) -> Dict[str, Any]:
    """
    Build FHIR Condition resource from internal diagnosis model.

    Args:
        diagnosis: Diagnosis model instance
        encounter: Associated Encounter model instance
        patient: Associated Patient model instance

    Returns:
        FHIR Condition resource dictionary
    """
    # Map diagnosis type to FHIR category
    category_mapping = {
        "primary": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                "code": "encounter-diagnosis",
                "display": "Encounter Diagnosis",
            }]
        },
        "secondary": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                "code": "problem-list-item",
                "display": "Problem List Item",
            }]
        },
        "admission": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                "code": "admission-diagnosis",
                "display": "Admission Diagnosis",
            }]
        },
        "discharge": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                "code": "discharge-diagnosis",
                "display": "Discharge Diagnosis",
            }]
        },
    }

    # Get category based on diagnosis type
    category = category_mapping.get(
        diagnosis.diagnosis_type.lower(),
        category_mapping["primary"]
    )

    # Build clinical status (assume active for new diagnoses)
    # Could be enhanced to check encounter status
    clinical_status = "active"
    if encounter.status == "completed":
        clinical_status = "resolved"

    # Build verification status (assume confirmed)
    verification_status = "confirmed"

    # Build severity (optional - could be added based on diagnosis data)
    severity = None
    if diagnosis.is_chronic:
        severity = {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "24484000",
                "display": "Severe",
            }]
        }

    # Build FHIR Condition resource
    fhir_condition = {
        "resourceType": "Condition",
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": clinical_status,
                "display": clinical_status.title(),
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": verification_status,
                "display": "Confirmed",
            }]
        },
        "category": [category],
        "code": {
            "coding": [{
                "system": "http://hl7.org/fhir/sid/icd-10",
                "code": diagnosis.icd_10_code,
                "display": diagnosis.diagnosis_name,
            }],
            "text": diagnosis.diagnosis_name,
        },
        "subject": {
            "reference": f"Patient/{patient.satusehat_patient_id or patient.id}",
            "display": patient.full_name,
        },
        "encounter": {
            "reference": f"Encounter/{encounter.satusehat_encounter_id or encounter.id}",
            "display": f"Encounter {encounter.id}",
        },
    }

    # Add severity if present
    if severity:
        fhir_condition["severity"] = severity

    # Add notes if present
    if diagnosis.notes:
        fhir_condition["note"] = [{
            "text": diagnosis.notes,
        }]

    # Add onset date (use encounter date)
    if encounter.encounter_date:
        fhir_condition["onsetDateTime"] = encounter.encounter_date.isoformat()

    # Add recorded date (use diagnosis created_at)
    if diagnosis.created_at:
        fhir_condition["recordedDate"] = diagnosis.created_at.isoformat()

    # Add internal diagnosis ID as extension
    if "extension" not in fhir_condition:
        fhir_condition["extension"] = []

    fhir_condition["extension"].append({
        "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/conditionInternalId",
        "valueString": str(diagnosis.id),
    })

    return fhir_condition


# =============================================================================
# Condition Sync Operations
# =============================================================================

async def sync_condition_to_satusehat(
    db: AsyncSession,
    diagnosis_id: int,
    satusehat_client: SATUSEHATClient,
    force_update: bool = False,
) -> Dict[str, Any]:
    """
    Sync a diagnosis/condition to SATUSEHAT.

    Args:
        db: Database session
        diagnosis_id: Diagnosis ID to sync
        satusehat_client: SATUSEHAT API client
        force_update: Force update even if data unchanged

    Returns:
        Sync result dictionary

    Raises:
        ValueError: If diagnosis not found
        SATUSEHATError: If sync fails
    """
    try:
        # Get diagnosis with related data
        diagnosis_result = await db.execute(
            select(Diagnosis).filter(Diagnosis.id == diagnosis_id)
        )
        diagnosis = diagnosis_result.scalar_one_or_none()

        if not diagnosis:
            return {
                "success": False,
                "message": f"Diagnosis {diagnosis_id} not found",
                "diagnosis_id": diagnosis_id,
            }

        # Get encounter
        encounter_result = await db.execute(
            select(Encounter).filter(Encounter.id == diagnosis.encounter_id)
        )
        encounter = encounter_result.scalar_one_or_none()

        if not encounter:
            return {
                "success": False,
                "message": f"Encounter {diagnosis.encounter_id} not found",
                "diagnosis_id": diagnosis_id,
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
                "diagnosis_id": diagnosis_id,
            }

        # Validate patient has SATUSEHAT ID
        if not patient.satusehat_patient_id:
            return {
                "success": False,
                "message": "Patient must be synced to SATUSEHAT first",
                "diagnosis_id": diagnosis_id,
            }

        # Build FHIR Condition resource
        fhir_condition = build_fhir_condition_resource(
            diagnosis,
            encounter,
            patient
        )

        # Check if diagnosis already has SATUSEHAT ID
        if diagnosis.satusehat_condition_id and not force_update:
            # Update existing condition
            logger.info(f"Updating existing SATUSEHAT condition: {diagnosis.satusehat_condition_id}")
            result = await satusehat_client._make_fhir_request(
                "PUT",
                "Condition",
                resource_id=diagnosis.satusehat_condition_id,
                data=fhir_condition,
            )
            action = "update"
        else:
            # Create new condition
            logger.info(f"Creating new SATUSEHAT condition for: {diagnosis_id}")
            result = await satusehat_client._make_fhir_request(
                "POST",
                "Condition",
                data=fhir_condition,
            )
            action = "create"

            # Store SATUSEHAT condition ID
            diagnosis.satusehat_condition_id = result.get("id")
            await db.commit()

        logger.info(f"Diagnosis {diagnosis_id} synced to SATUSEHAT (ID: {result.get('id')})")

        return {
            "success": True,
            "message": "Diagnosis synced successfully",
            "diagnosis_id": diagnosis_id,
            "satusehat_condition_id": result.get("id"),
            "action": action,
            "fhir_resource": result,
        }

    except SATUSEHATError as e:
        logger.error(f"Failed to sync diagnosis {diagnosis_id} to SATUSEHAT: {e}")
        return {
            "success": False,
            "message": f"Failed to sync diagnosis: {e.message}",
            "diagnosis_id": diagnosis_id,
            "error": str(e),
        }

    except Exception as e:
        logger.exception(f"Unexpected error syncing diagnosis {diagnosis_id} to SATUSEHAT")
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "diagnosis_id": diagnosis_id,
            "error": str(e),
        }


async def sync_all_conditions_for_encounter(
    db: AsyncSession,
    encounter_id: int,
    satusehat_client: SATUSEHATClient,
) -> Dict[str, Any]:
    """
    Sync all diagnoses for an encounter to SATUSEHAT.

    Args:
        db: Database session
        encounter_id: Encounter ID
        satusehat_client: SATUSEHAT API client

    Returns:
        Sync result summary
    """
    # Get all diagnoses for encounter
    diagnoses_result = await db.execute(
        select(Diagnosis).filter(Diagnosis.encounter_id == encounter_id)
    )
    diagnoses = diagnoses_result.scalars().all()

    success_count = 0
    failure_count = 0
    results = []

    for diagnosis in diagnoses:
        result = await sync_condition_to_satusehat(db, diagnosis.id, satusehat_client)
        results.append(result)

        if result["success"]:
            success_count += 1
        else:
            failure_count += 1

    return {
        "total_diagnoses": len(diagnoses),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }


async def get_condition_from_satusehat(
    satusehat_client: SATUSEHATClient,
    satusehat_condition_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve condition from SATUSEHAT.

    Args:
        satusehat_client: SATUSEHAT API client
        satusehat_condition_id: SATUSEHAT Condition resource ID

    Returns:
        FHIR Condition resource or None if not found

    Raises:
        SATUSEHATError: If retrieval fails
    """
    try:
        result = await satusehat_client._make_fhir_request(
            "GET",
            "Condition",
            resource_id=satusehat_condition_id,
        )
        return result

    except SATUSEHATError as e:
        if "not found" in str(e.message).lower():
            return None
        raise


# =============================================================================
# Auto-sync Triggers
# =============================================================================

async def trigger_condition_sync_on_create(
    db: AsyncSession,
    diagnosis_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Trigger SATUSEHAT sync when diagnosis is created.

    This should be called after a diagnosis is created to automatically
    sync the condition data to SATUSEHAT.

    Args:
        db: Database session
        diagnosis_id: Diagnosis ID that was created

    Returns:
        Sync result or None if sync failed
    """
    try:
        async with SATUSEHATClient() as client:
            return await sync_condition_to_satusehat(db, diagnosis_id, client)

    except Exception as e:
        logger.exception(f"Failed to trigger condition sync for diagnosis {diagnosis_id}")
        return None


# =============================================================================
# Condition Data Validation
# =============================================================================

def validate_condition_for_sync(
    diagnosis: Diagnosis,
    encounter: Encounter,
    patient: Patient,
) -> tuple[bool, List[str]]:
    """
    Validate condition data for SATUSEHAT sync.

    Args:
        diagnosis: Diagnosis model instance
        encounter: Associated Encounter model instance
        patient: Associated Patient model instance

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    if not diagnosis.icd_10_code:
        errors.append("ICD-10 code is required")

    if not diagnosis.diagnosis_name:
        errors.append("Diagnosis name is required")

    # Validate ICD-10 code format (basic validation)
    if diagnosis.icd_10_code:
        # ICD-10 codes are typically A00-Z99 format
        if not diagnosis.icd_10_code[0].isalpha() or len(diagnosis.icd_10_code) < 3:
            errors.append("ICD-10 code format appears invalid (expected format: A00-Z99)")

    # Check patient has SATUSEHAT ID
    if not patient.satusehat_patient_id:
        errors.append("Patient must be synced to SATUSEHAT first")

    # Check encounter has SATUSEHAT ID
    if not encounter.satusehat_encounter_id:
        errors.append("Encounter must be synced to SATUSEHAT first")

    # Validate diagnosis type
    valid_types = ["primary", "secondary", "admission", "discharge"]
    if diagnosis.diagnosis_type.lower() not in valid_types:
        errors.append(f"Invalid diagnosis type. Must be one of: {', '.join(valid_types)}")

    return len(errors) == 0, errors
