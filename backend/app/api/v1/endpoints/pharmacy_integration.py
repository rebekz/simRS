"""Pharmacy Integration API Endpoints for STORY-024-08

This module provides API endpoints for:
- External pharmacy system management
- Electronic prescription transmission
- Medication dispensing tracking
- Refill request management
- Drug interaction checking
- Pharmacy inventory synchronization

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import User
from app.core.deps import get_current_user, get_current_admin_user
from app.services.pharmacy_integration import get_pharmacy_integration_service


logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class PharmacySystemRegisterRequest(BaseModel):
    """Request to register pharmacy system"""
    system_code: str = Field(..., description="System code")
    system_name: str = Field(..., description="System name")
    system_type: str = Field(..., description="System type (hospital, retail, mail_order)")
    protocol: str = Field(..., description="Communication protocol")
    organization: Optional[str] = Field(None, description="Organization name")
    pharmacy_id: Optional[str] = Field(None, description="Pharmacy ID")
    license_number: Optional[str] = Field(None, description="Pharmacy license number")
    contact_name: Optional[str] = Field(None, description="Contact name")
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone")
    address: Optional[str] = Field(None, description="Physical address")
    endpoint_url: Optional[str] = Field(None, description="Endpoint URL")
    auth_type: Optional[str] = Field(None, description="Authentication type")
    is_primary: bool = Field(False, description="Is primary pharmacy")
    test_mode: bool = Field(False, description="Test mode")


class PrescriptionTransmitRequest(BaseModel):
    """Request to transmit prescription"""
    prescription_id: int = Field(..., description="Prescription ID")
    pharmacy_system_id: int = Field(..., description="Pharmacy system ID")
    patient_id: int = Field(..., description="Patient ID")
    encounter_id: Optional[int] = Field(None, description="Encounter ID")
    prescriber_id: Optional[int] = Field(None, description="Prescriber ID")
    medication_id: Optional[int] = Field(None, description="Medication ID")
    medication_name: str = Field(..., description="Medication name")
    medication_code: Optional[str] = Field(None, description="Medication code")
    generic_name: Optional[str] = Field(None, description="Generic name")
    dosage_form: Optional[str] = Field(None, description="Dosage form")
    strength: Optional[str] = Field(None, description="Medication strength")
    strength_unit: Optional[str] = Field(None, description="Strength unit")
    quantity: float = Field(..., description="Quantity prescribed")
    quantity_unit: str = Field(..., description="Quantity unit")
    days_supply: int = Field(..., description="Days supply")
    refills: int = Field(0, description="Number of refills")
    sig_text: str = Field(..., description="Sig instructions")
    route: Optional[str] = Field(None, description="Route of administration")
    frequency: Optional[str] = Field(None, description="Dosing frequency")
    diagnosis_code: Optional[str] = Field(None, description="Diagnosis code")
    diagnosis_description: Optional[str] = Field(None, description="Diagnosis description")
    clinical_notes: Optional[str] = Field(None, description="Clinical notes")


class MedicationDispenseRequest(BaseModel):
    """Request to record medication dispense"""
    prescription_transmission_id: int = Field(..., description="Prescription transmission ID")
    pharmacy_system_id: int = Field(..., description="Pharmacy system ID")
    patient_id: int = Field(..., description="Patient ID")
    medication_id: Optional[int] = Field(None, description="Medication ID")
    dispense_number: str = Field(..., description="Dispense number")
    dispense_date: datetime = Field(..., description="Dispense date")
    quantity_dispensed: float = Field(..., description="Quantity dispensed")
    days_supply: int = Field(..., description="Days supply")
    refills_remaining: int = Field(..., description="Refills remaining")
    medication_name: str = Field(..., description="Medication name")
    medication_code: Optional[str] = Field(None, description="Medication code")
    dosage_form: Optional[str] = Field(None, description="Dosage form")
    strength: Optional[str] = Field(None, description="Medication strength")
    strength_unit: Optional[str] = Field(None, description="Strength unit")
    dispenser_id: Optional[int] = Field(None, description="Dispenser ID")
    dispenser_name: Optional[str] = Field(None, description="Dispenser name")
    pharmacy_id: Optional[str] = Field(None, description="Pharmacy ID")
    cost: Optional[float] = Field(None, description="Medication cost")
    price: Optional[float] = Field(None, description="Price charged")
    copay: Optional[float] = Field(None, description="Patient copay")
    lot_number: Optional[str] = Field(None, description="Lot number")
    expiration_date: Optional[datetime] = Field(None, description="Expiration date")
    ndc: Optional[str] = Field(None, description="National Drug Code")
    dea_schedule: Optional[str] = Field(None, description="DEA schedule")
    dispense_notes: Optional[str] = Field(None, description="Dispense notes")
    patient_counseling: Optional[str] = Field(None, description="Patient counseling notes")


class RefillRequestRequest(BaseModel):
    """Request to request prescription refill"""
    prescription_transmission_id: int = Field(..., description="Prescription transmission ID")
    pharmacy_system_id: int = Field(..., description="Pharmacy system ID")
    patient_id: int = Field(..., description="Patient ID")
    requested_by: int = Field(..., description="User ID requesting refill")
    refill_number: int = Field(..., description="Refill number (1, 2, etc.)")
    quantity_requested: float = Field(..., description="Quantity requested")
    reason: Optional[str] = Field(None, description="Reason for refill")


class DrugInteractionCheckRequest(BaseModel):
    """Request to check drug interactions"""
    medication_ids: List[int] = Field(..., description="Medication IDs to check")
    patient_id: int = Field(..., description="Patient ID")
    pharmacy_system_id: int = Field(..., description="Pharmacy system ID")
    prescription_id: Optional[int] = Field(None, description="Prescription ID")


# =============================================================================
# Pharmacy System Management Endpoints
# =============================================================================

@router.post("/systems", status_code=status.HTTP_201_CREATED)
async def register_pharmacy_system(
    request: PharmacySystemRegisterRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Register external pharmacy system (admin only)"""
    try:
        service = get_pharmacy_integration_service(db)

        result = await service.register_pharmacy_system(
            system_code=request.system_code,
            system_name=request.system_name,
            system_type=request.system_type,
            protocol=request.protocol,
            organization=request.organization,
            pharmacy_id=request.pharmacy_id,
            license_number=request.license_number,
            contact_name=request.contact_name,
            contact_email=request.contact_email,
            contact_phone=request.contact_phone,
            address=request.address,
            endpoint_url=request.endpoint_url,
            auth_type=request.auth_type,
            is_primary=request.is_primary,
            test_mode=request.test_mode,
            created_by=current_user.id
        )

        return result

    except ValueError as e:
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error registering pharmacy system: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register pharmacy system"
        )


@router.get("/systems")
async def list_pharmacy_systems(
    system_type: Optional[str] = Query(None, description="Filter by system type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List pharmacy systems"""
    try:
        from app.models.pharmacy_integration import PharmacySystem
        from sqlalchemy import select, and_

        # Build filters
        filters = []
        if system_type:
            filters.append(PharmacySystem.system_type == system_type)
        if is_active is not None:
            filters.append(PharmacySystem.is_active == is_active)

        # Get systems
        query = select(PharmacySystem)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(PharmacySystem.system_name)

        result = await db.execute(query)
        systems = result.scalars().all()

        # Build response
        system_list = [
            {
                "system_id": s.system_id,
                "system_code": s.system_code,
                "system_name": s.system_name,
                "system_type": s.system_type,
                "organization": s.organization,
                "pharmacy_id": s.pharmacy_id,
                "protocol": s.protocol,
                "status": s.status,
                "is_active": s.is_active,
                "is_primary": s.is_primary,
                "supports_e_prescribing": s.supports_e_prescribing,
                "supports_dispensing": s.supports_dispensing,
                "supports_inventory_sync": s.supports_inventory_sync
            }
            for s in systems
        ]

        return {
            "systems": system_list
        }

    except Exception as e:
        logger.error("Error listing pharmacy systems: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list pharmacy systems"
        )


# =============================================================================
# Prescription Transmission Endpoints
# =============================================================================

@router.post("/prescriptions/transmit", status_code=status.HTTP_201_CREATED)
async def transmit_prescription(
    request: PrescriptionTransmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Transmit prescription to pharmacy system"""
    try:
        service = get_pharmacy_integration_service(db)

        # Build prescription data
        prescription_data = {
            "patient_id": request.patient_id,
            "encounter_id": request.encounter_id,
            "prescriber_id": request.prescriber_id,
            "medication_id": request.medication_id,
            "medication_name": request.medication_name,
            "medication_code": request.medication_code,
            "generic_name": request.generic_name,
            "dosage_form": request.dosage_form,
            "strength": request.strength,
            "strength_unit": request.strength_unit,
            "quantity": request.quantity,
            "quantity_unit": request.quantity_unit,
            "days_supply": request.days_supply,
            "refills": request.refills,
            "sig_text": request.sig_text,
            "route": request.route,
            "frequency": request.frequency,
            "diagnosis_code": request.diagnosis_code,
            "diagnosis_description": request.diagnosis_description,
            "clinical_notes": request.clinical_notes
        }

        result = await service.transmit_prescription(
            prescription_id=request.prescription_id,
            pharmacy_system_id=request.pharmacy_system_id,
            prescription_data=prescription_data,
            transmitted_by=current_user.id
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error transmitting prescription: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transmit prescription"
        )


@router.get("/prescriptions/{prescription_number}")
async def get_prescription_status(
    prescription_number: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get prescription transmission status by prescription number"""
    try:
        service = get_pharmacy_integration_service(db)

        result = await service.get_prescription_status(prescription_number)

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error getting prescription status: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get prescription status"
        )


@router.get("/prescriptions")
async def list_prescriptions(
    pharmacy_system_id: Optional[int] = Query(None, description="Filter by pharmacy system"),
    patient_id: Optional[int] = Query(None, description="Filter by patient"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List prescription transmissions with filtering"""
    try:
        from app.models.pharmacy_integration import PrescriptionTransmission
        from sqlalchemy import select, func, and_

        # Build filters
        filters = []
        if pharmacy_system_id:
            filters.append(PrescriptionTransmission.pharmacy_system_id == pharmacy_system_id)
        if patient_id:
            filters.append(PrescriptionTransmission.patient_id == patient_id)
        if status:
            filters.append(PrescriptionTransmission.status == status)
        if start_date:
            filters.append(PrescriptionTransmission.created_at >= start_date)
        if end_date:
            filters.append(PrescriptionTransmission.created_at <= end_date)

        # Get total count
        count_query = select(func.count(PrescriptionTransmission.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Get prescriptions with pagination
        offset = (page - 1) * per_page
        query = select(PrescriptionTransmission)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(PrescriptionTransmission.created_at.desc()).limit(per_page).offset(offset)

        result = await db.execute(query)
        prescriptions = result.scalars().all()

        # Build response
        prescription_list = [
            {
                "transmission_id": p.transmission_id,
                "prescription_number": p.prescription_number,
                "patient_id": p.patient_id,
                "patient_name": p.patient_name,
                "medication_name": p.medication_name,
                "quantity": p.quantity,
                "quantity_unit": p.quantity_unit,
                "refills_remaining": p.refills_remaining,
                "status": p.status,
                "sent_at": p.sent_at.isoformat() if p.sent_at else None,
                "dispensed_at": p.dispensed_at.isoformat() if p.dispensed_at else None
            }
            for p in prescriptions
        ]

        return {
            "prescriptions": prescription_list,
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
        }

    except Exception as e:
        logger.error("Error listing prescriptions: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list prescriptions"
        )


# =============================================================================
# Medication Dispense Endpoints
# =============================================================================

@router.post("/dispenses", status_code=status.HTTP_201_CREATED)
async def record_dispense(
    request: MedicationDispenseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record medication dispense from pharmacy"""
    try:
        service = get_pharmacy_integration_service(db)

        # Build dispense data
        dispense_data = {
            "patient_id": request.patient_id,
            "medication_id": request.medication_id,
            "dispense_number": request.dispense_number,
            "dispense_date": request.dispense_date,
            "quantity_dispensed": request.quantity_dispensed,
            "days_supply": request.days_supply,
            "refills_remaining": request.refills_remaining,
            "medication_name": request.medication_name,
            "medication_code": request.medication_code,
            "dosage_form": request.dosage_form,
            "strength": request.strength,
            "strength_unit": request.strength_unit,
            "dispenser_id": request.dispenser_id,
            "dispenser_name": request.dispenser_name,
            "pharmacy_id": request.pharmacy_id,
            "cost": request.cost,
            "price": request.price,
            "copay": request.copay,
            "lot_number": request.lot_number,
            "expiration_date": request.expiration_date,
            "ndc": request.ndc,
            "dea_schedule": request.dea_schedule,
            "dispense_notes": request.dispense_notes,
            "patient_counseling": request.patient_counseling
        }

        result = await service.record_dispense(
            prescription_transmission_id=request.prescription_transmission_id,
            dispense_data=dispense_data
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error recording dispense: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record dispense"
        )


# =============================================================================
# Refill Request Endpoints
# =============================================================================

@router.post("/refills", status_code=status.HTTP_201_CREATED)
async def request_refill(
    request: RefillRequestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Request prescription refill"""
    try:
        service = get_pharmacy_integration_service(db)

        # Build refill data
        refill_data = {
            "patient_id": request.patient_id,
            "requested_by": request.requested_by,
            "refill_number": request.refill_number,
            "quantity_requested": request.quantity_requested,
            "reason": request.reason
        }

        result = await service.request_refill(
            prescription_transmission_id=request.prescription_transmission_id,
            refill_data=refill_data
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower() or "no refills" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error requesting refill: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request refill"
        )


# =============================================================================
# Drug Interaction Check Endpoints
# =============================================================================

@router.post("/drug-interactions/check", status_code=status.HTTP_201_CREATED)
async def check_drug_interactions(
    request: DrugInteractionCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check drug interactions through pharmacy system"""
    try:
        service = get_pharmacy_integration_service(db)

        result = await service.check_drug_interactions(
            medication_ids=request.medication_ids,
            patient_id=request.patient_id,
            pharmacy_system_id=request.pharmacy_system_id,
            prescription_id=request.prescription_id
        )

        return result

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error checking drug interactions: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check drug interactions"
        )


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_pharmacy_integration_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pharmacy integration statistics"""
    try:
        from app.models.pharmacy_integration import (
            PharmacySystem, PrescriptionTransmission,
            MedicationDispense, RefillRequest
        )
        from sqlalchemy import select, func

        # Get total counts
        system_query = select(func.count(PharmacySystem.id)).where(
            PharmacySystem.is_active == True
        )
        system_result = await db.execute(system_query)
        total_systems = system_result.scalar() or 0

        prescription_query = select(func.count(PrescriptionTransmission.id))
        prescription_result = await db.execute(prescription_query)
        total_prescriptions = prescription_result.scalar() or 0

        dispense_query = select(func.count(MedicationDispense.id))
        dispense_result = await db.execute(dispense_query)
        total_dispenses = dispense_result.scalar() or 0

        refill_query = select(func.count(RefillRequest.id))
        refill_result = await db.execute(refill_query)
        total_refills = refill_result.scalar() or 0

        # Get prescription status breakdown
        status_query = select(
            PrescriptionTransmission.status,
            func.count(PrescriptionTransmission.id).label("count")
        ).group_by(PrescriptionTransmission.status)

        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}

        # Get dispense status breakdown
        dispense_status_query = select(
            MedicationDispense.status,
            func.count(MedicationDispense.id).label("count")
        ).group_by(MedicationDispense.status)

        dispense_status_result = await db.execute(dispense_status_query)
        dispense_status_counts = {row[0]: row[1] for row in dispense_status_result.all()}

        return {
            "total_systems": total_systems,
            "total_prescriptions": total_prescriptions,
            "total_dispenses": total_dispenses,
            "total_refills": total_refills,
            "prescription_status_counts": status_counts,
            "dispense_status_counts": dispense_status_counts,
            "summary": {
                "pending": status_counts.get("pending", 0),
                "sent_to_pharmacy": status_counts.get("sent_to_pharmacy", 0),
                "dispensed": status_counts.get("dispensed", 0),
                "partially_dispensed": status_counts.get("partially_dispensed", 0),
                "cancelled": status_counts.get("cancelled", 0)
            }
        }

    except Exception as e:
        logger.error("Error getting pharmacy integration statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
