"""Patient Portal Prescription Refill Endpoints

API endpoints for patients to view prescriptions and request refills.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.deps import get_db, get_current_portal_patient
from app.models.patient_portal import PatientPortalUser
from app.schemas.patient_portal.prescriptions import (
    PrescriptionListResponse,
    PrescriptionItem,
    RefillRequestCreate,
    RefillRequestResponse,
    RefillRequestListResponse,
    RefillEligibilityCheck,
    MedicationDetail,
)
from app.services.patient_portal.prescription_service import PrescriptionRefillService

router = APIRouter()


@router.get("/prescriptions", response_model=PrescriptionListResponse)
async def get_my_prescriptions(
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get patient's active and past prescriptions

    Returns all prescriptions with medication details and refill eligibility.
    """
    service = PrescriptionRefillService(db)
    prescriptions = await service.get_active_prescriptions(current_user.patient_id)

    return PrescriptionListResponse(
        active_prescriptions=prescriptions["active_prescriptions"],
        past_prescriptions=prescriptions["past_prescriptions"],
        total_active=len(prescriptions["active_prescriptions"]),
        total_past=len(prescriptions["past_prescriptions"]),
    )


@router.post("/prescriptions/check-eligibility", response_model=List[RefillEligibilityCheck])
async def check_refill_eligibility(
    prescription_item_ids: List[int],
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Check if specific prescription items are eligible for refill

    Use this before submitting a refill request to validate eligibility.
    """
    if not prescription_item_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one prescription item ID must be provided",
        )

    service = PrescriptionRefillService(db)
    eligibility_checks = await service.check_refill_eligibility(
        current_user.patient_id, prescription_item_ids
    )

    return eligibility_checks


@router.post("/prescriptions/refill-requests", response_model=RefillRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_refill_request(
    request: RefillRequestCreate,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Submit a new prescription refill request

    Creates refill request for specified medications.
    System will validate eligibility before creating request.

    Request will be reviewed by a pharmacist or prescriber.
    Patient will be notified of approval/rejection.
    """
    try:
        service = PrescriptionRefillService(db)
        response = await service.create_refill_request(current_user.patient_id, request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create refill request: {str(e)}",
        )


@router.get("/prescriptions/refill-requests", response_model=RefillRequestListResponse)
async def get_my_refill_requests(
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get all refill requests for the current patient

    Returns requests grouped by status (pending, approved, rejected, etc.)
    """
    service = PrescriptionRefillService(db)
    requests = await service.get_refill_requests(current_user.patient_id)

    return RefillRequestListResponse(**requests)


@router.get("/prescriptions/medications/{drug_id}", response_model=MedicationDetail)
async def get_medication_details(
    drug_id: int,
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific medication

    Includes indications, contraindications, warnings, and usage instructions.
    """
    from sqlalchemy import select
    from app.models.inventory import Drug

    result = await db.execute(select(Drug).where(Drug.id == drug_id))
    drug = result.scalar_one_or_none()

    if not drug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )

    # Parse text fields into lists where applicable
    def parse_text_list(text: str | None) -> list[str]:
        if not text:
            return []
        return [line.strip() for line in text.split("\n") if line.strip()]

    return MedicationDetail(
        drug_id=drug.id,
        drug_name=drug.generic_name,
        generic_name=drug.generic_name,
        dosage_form=drug.dosage_form,
        strength=drug.strength,
        manufacturer=drug.manufacturer,
        description=drug.description,
        indications=parse_text_list(drug.indications),
        contraindications=parse_text_list(drug.contraindications),
        warnings=parse_text_list(drug.warnings),
        side_effects=[],  # Not tracked in current Drug model
        drug_interactions=[],  # Not tracked in current Drug model
        instructions_for_use=None,  # Not tracked in current Drug model
        storage_requirements=drug.storage_conditions,
    )


@router.get("/prescriptions/check-interactions")
async def check_drug_interactions(
    drug_ids: List[int],
    current_user: PatientPortalUser = Depends(get_current_portal_patient),
    db: AsyncSession = Depends(get_db),
):
    """Check for potential drug interactions between medications

    Returns severity levels and interaction descriptions.
    """
    from sqlalchemy import select, and_
    from app.models.drugs import Drug, DrugInteraction
    from app.schemas.patient_portal.prescriptions import DrugInteractionWarning

    if len(drug_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 drugs must be provided to check interactions",
        )

    # Get drug names
    result = await db.execute(select(Drug).where(Drug.id.in_(drug_ids)))
    drugs = result.scalars().all()
    drug_map = {drug.id: drug.name for drug in drugs}

    # Check for interactions between pairs
    interactions = []
    for i, drug_id_1 in enumerate(drug_ids):
        for drug_id_2 in drug_ids[i + 1 :]:
            result = await db.execute(
                select(DrugInteraction).where(
                    and_(
                        DrugInteraction.drug_id_1 == drug_id_1,
                        DrugInteraction.drug_id_2 == drug_id_2,
                    )
                )
            )
            interaction = result.scalar_one_or_none()

            if interaction:
                interactions.append(
                    DrugInteractionWarning(
                        severity=interaction.severity,
                        description=interaction.description,
                        interacting_drugs=[
                            drug_map[drug_id_1],
                            drug_map[drug_id_2],
                        ],
                    )
                )

    return {"interactions": interactions, "total": len(interactions)}
