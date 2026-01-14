"""Patient sync service for SATUSEHAT FHIR R4 integration (STORY-034).

This module provides functions to sync patient demographics with SATUSEHAT,
converting internal patient data to FHIR Patient format and handling sync retries.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.satusehat import SATUSEHATClient, SATUSEHATError
from app.models.patient import Patient

logger = logging.getLogger(__name__)


# =============================================================================
# FHIR Patient Resource Builder
# =============================================================================

def build_fhir_patient_resource(
    patient: Patient,
    organization_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build FHIR Patient resource from internal patient model.

    Args:
        patient: Patient model instance
        organization_id: SATUSEHAT Organization resource ID (managing organization)

    Returns:
        FHIR Patient resource dictionary
    """
    # Build identifier list (NIK is primary, MRN is secondary)
    identifiers = []

    # NIK (Indonesian ID) - primary official identifier
    if patient.nik:
        identifiers.append({
            "use": "official",
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "NN",
                    "display": "National unique individual identifier"
                }]
            },
            "system": "https://fhir.kemkes.go.id/id/nik",
            "value": patient.nik,
        })

    # Medical Record Number (MRN)
    if patient.medical_record_number:
        identifiers.append({
            "use": "usual",
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "MR",
                    "display": "Medical record number"
                }]
            },
            "system": f"https://fhir.kemkes.go.id/id/mrn-{organization_id or 'default'}",
            "value": patient.medical_record_number,
        })

    # BPJS card number
    if patient.bpjs_card_number:
        identifiers.append({
            "use": "official",
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "NI",
                    "display": "National unique individual identifier"
                }]
            },
            "system": "https://fhir.kemkes.go.id/id/bpjs",
            "value": patient.bpjs_card_number,
        })

    # Build name (Indonesian format: given names + family name)
    name = {
        "use": "official",
        "text": patient.full_name,
    }

    if patient.full_name:
        # Split into given names and family name
        # In Indonesian naming, usually last word is family name
        name_parts = patient.full_name.split()
        if len(name_parts) > 1:
            name["given"] = name_parts[:-1]
            name["family"] = name_parts[-1]
        else:
            name["given"] = name_parts
            name["family"] = ""  # No family name

    # Build telecom (contact)
    telecom = []

    if patient.phone:
        telecom.append({
            "system": "phone",
            "value": patient.phone,
            "use": "mobile",
        })

    if patient.email:
        telecom.append({
            "system": "email",
            "value": patient.email,
            "use": "home",
        })

    # Build gender
    gender_map = {
        "male": "male",
        "female": "female",
        "other": "other",
        "unknown": "unknown",
    }
    gender = gender_map.get(patient.gender.lower() if patient.gender else "unknown", "unknown")

    # Build birthDate
    birth_date = None
    if patient.date_of_birth:
        birth_date = patient.date_of_birth.isoformat()

    # Build address
    address = None
    if patient.address or patient.city or patient.province:
        address = {
            "use": "home",
            "type": "both",
        }
        if patient.address:
            address["line"] = [patient.address]
        if patient.city:
            address["city"] = patient.city
        if patient.province:
            address["state"] = patient.province
        if patient.postal_code:
            address["postalCode"] = patient.postal_code
        if patient.country:
            address["country"] = patient.country

    # Build marital status
    marital_status = None
    if patient.marital_status:
        marital_status_code = {
            "single": "U",  # Unmarried
            "married": "M",
            "widowed": "W",
            "divorced": "D",
            "separated": "L",
        }.get(patient.marital_status.lower(), "UNK")

        marital_status = {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                "code": marital_status_code,
            }]
        }

    # Build FHIR Patient resource
    fhir_patient = {
        "resourceType": "Patient",
        "identifier": identifiers,
        "active": True,  # Patient records are always active
        "name": [name],
        "gender": gender,
    }

    if birth_date:
        fhir_patient["birthDate"] = birth_date

    if telecom:
        fhir_patient["telecom"] = telecom

    if address:
        fhir_patient["address"] = [address]

    if marital_status:
        fhir_patient["maritalStatus"] = marital_status

    # Add managing organization reference if provided
    if organization_id:
        fhir_patient["managingOrganization"] = {
            "reference": f"Organization/{organization_id}",
            "display": "Healthcare Facility",
        }

    # Add internal patient ID as extension
    fhir_patient["extension"] = [
        {
            "url": "https://fhir.kemkes.go.id/r4/StructureDefinition/patientInternalId",
            "valueString": str(patient.id),
        }
    ]

    return fhir_patient


# =============================================================================
# Patient Sync Operations
# =============================================================================

async def sync_patient_to_satusehat(
    db: AsyncSession,
    patient_id: int,
    satusehat_client: SATUSEHATClient,
    organization_id: Optional[str] = None,
    force_update: bool = False,
) -> Dict[str, Any]:
    """
    Sync a patient's demographics to SATUSEHAT.

    Args:
        db: Database session
        patient_id: Patient ID to sync
        satusehat_client: SATUSEHAT API client
        organization_id: SATUSEHAT Organization resource ID
        force_update: Force update even if data unchanged

    Returns:
        Sync result dictionary

    Raises:
        ValueError: If patient not found
        SATUSEHATError: If sync fails
    """
    try:
        # Get patient
        patient_result = await db.execute(select(Patient).filter(Patient.id == patient_id))
        patient = patient_result.scalar_one_or_none()

        if not patient:
            return {
                "success": False,
                "message": f"Patient {patient_id} not found",
                "patient_id": patient_id,
            }

        # Build FHIR Patient resource
        fhir_patient = build_fhir_patient_resource(patient, organization_id)

        # Check if patient already has SATUSEHAT ID
        if patient.satusehat_patient_id and not force_update:
            # Update existing patient
            logger.info(f"Updating existing SATUSEHAT patient: {patient.satusehat_patient_id}")
            result = await satusehat_client._make_fhir_request(
                "PUT",
                "Patient",
                resource_id=patient.satusehat_patient_id,
                data=fhir_patient,
            )
            action = "update"
        else:
            # Create new patient
            logger.info(f"Creating new SATUSEHAT patient for: {patient.medical_record_number}")
            result = await satusehat_client._make_fhir_request(
                "POST",
                "Patient",
                data=fhir_patient,
            )
            action = "create"

            # Store SATUSEHAT patient ID
            patient.satusehat_patient_id = result.get("id")
            await db.commit()

        logger.info(f"Patient {patient_id} synced to SATUSEHAT (ID: {result.get('id')})")

        return {
            "success": True,
            "message": "Patient synced successfully",
            "patient_id": patient_id,
            "satusehat_patient_id": result.get("id"),
            "action": action,
            "fhir_resource": result,
        }

    except SATUSEHATError as e:
        logger.error(f"Failed to sync patient {patient_id} to SATUSEHAT: {e}")
        return {
            "success": False,
            "message": f"Failed to sync patient: {e.message}",
            "patient_id": patient_id,
            "error": str(e),
        }

    except Exception as e:
        logger.exception(f"Unexpected error syncing patient {patient_id} to SATUSEHAT")
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}",
            "patient_id": patient_id,
            "error": str(e),
        }


async def get_patient_from_satusehat(
    satusehat_client: SATUSEHATClient,
    satusehat_patient_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve patient from SATUSEHAT.

    Args:
        satusehat_client: SATUSEHAT API client
        satusehat_patient_id: SATUSEHAT Patient resource ID

    Returns:
        FHIR Patient resource or None if not found

    Raises:
        SATUSEHATError: If retrieval fails
    """
    try:
        result = await satusehat_client._make_fhir_request(
            "GET",
            "Patient",
            resource_id=satusehat_patient_id,
        )
        return result

    except SATUSEHATError as e:
        if "not found" in str(e.message).lower():
            return None
        raise


async def search_patient_by_identifier(
    satusehat_client: SATUSEHATClient,
    identifier_system: str,
    identifier_value: str,
) -> Dict[str, Any]:
    """
    Search for patient by identifier in SATUSEHAT.

    Args:
        satusehat_client: SATUSEHAT API client
        identifier_system: Identifier system URL
        identifier_value: Identifier value

    Returns:
        FHIR Bundle with search results

    Raises:
        SATUSEHATError: If search fails
    """
    params = {
        "identifier": f"{identifier_system}|{identifier_value}"
    }

    result = await satusehat_client._make_fhir_request(
        "GET",
        "Patient",
        params=params,
    )

    return result


# =============================================================================
# Auto-sync Triggers
# =============================================================================

async def trigger_patient_sync_on_create(
    db: AsyncSession,
    patient_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Trigger SATUSEHAT sync when patient is created.

    This should be called after a patient is created to automatically
    sync the demographics to SATUSEHAT.

    Args:
        db: Database session
        patient_id: Patient ID that was created

    Returns:
        Sync result or None if sync failed
    """
    try:
        async with SATUSEHATClient() as client:
            return await sync_patient_to_satusehat(db, patient_id, client)

    except Exception as e:
        logger.exception(f"Failed to trigger patient sync for patient {patient_id}")
        return None


async def trigger_patient_sync_on_update(
    db: AsyncSession,
    patient_id: int,
) -> Optional[Dict[str, Any]]:
    """
    Trigger SATUSEHAT sync when patient demographics are updated.

    This should be called after a patient's demographics are updated
    to automatically sync the changes to SATUSEHAT.

    Args:
        db: Database session
        patient_id: Patient ID that was updated

    Returns:
        Sync result or None if sync failed
    """
    try:
        async with SATUSEHATClient() as client:
            return await sync_patient_to_satusehat(db, patient_id, client, force_update=True)

    except Exception as e:
        logger.exception(f"Failed to trigger patient sync for patient {patient_id}")
        return None


# =============================================================================
# Batch Sync Operations
# =============================================================================

async def sync_all_patients_to_satusehat(
    db: AsyncSession,
    satusehat_client: SATUSEHATClient,
    organization_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Sync all patients to SATUSEHAT (batch operation).

    Args:
        db: Database session
        satusehat_client: SATUSEHAT API client
        organization_id: SATUSEHAT Organization resource ID
        limit: Maximum number of patients to sync

    Returns:
        Sync result summary
    """
    # Get all patients
    query = select(Patient)
    if limit:
        query = query.limit(limit)

    patients_result = await db.execute(query)
    patients = patients_result.scalars().all()

    success_count = 0
    failure_count = 0
    results = []

    for patient in patients:
        result = await sync_patient_to_satusehat(
            db,
            patient.id,
            satusehat_client,
            organization_id
        )
        results.append(result)

        if result["success"]:
            success_count += 1
        else:
            failure_count += 1

    return {
        "total_patients": len(patients),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }


# =============================================================================
# Patient Data Validation
# =============================================================================

def validate_patient_for_sync(patient: Patient) -> tuple[bool, List[str]]:
    """
    Validate patient data for SATUSEHAT sync.

    Args:
        patient: Patient model instance

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    if not patient.full_name:
        errors.append("Full name is required")

    if not patient.date_of_birth:
        errors.append("Date of birth is required")

    if not patient.gender:
        errors.append("Gender is required")

    # Check at least one identifier
    if not patient.nik and not patient.medical_record_number:
        errors.append("At least one identifier (NIK or MRN) is required")

    # Validate NIK format if provided
    if patient.nik and (len(patient.nik) != 16 or not patient.nik.isdigit()):
        errors.append("NIK must be 16 digits")

    # Validate phone format if provided
    if patient.phone and not patient.phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
        errors.append("Phone number contains invalid characters")

    return len(errors) == 0, errors
