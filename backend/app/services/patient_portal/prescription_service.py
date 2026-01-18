"""Prescription Refill Service

Service for managing prescription refill requests through patient portal.
Handles eligibility checking, refill requests, and status tracking.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import secrets

from app.models.refill_request import (
    PrescriptionRefillRequest,
    PrescriptionRefillItem,
    RefillRequestStatus,
)
from app.models.prescription import Prescription, PrescriptionItem
from app.models.patient import Patient
from app.models.inventory import Drug
from app.models.dispensing import Dispense
from app.schemas.dispensing import DispenseStatus
from app.schemas.patient_portal.prescriptions import (
    RefillRequestCreate,
    RefillEligibility,
    RefillEligibilityCheck,
    MedicationInfo,
    PrescriptionItem as PrescriptionItemResponse,
    RefillRequestResponse,
)


class PrescriptionRefillService:
    """Service for handling prescription refill requests"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_prescriptions(
        self, patient_id: int
    ) -> Dict[str, List[PrescriptionItemResponse]]:
        """Get patient's active and past prescriptions

        Returns prescriptions grouped into active and past, with refill eligibility.
        """
        # Get all prescriptions for this patient
        result = await self.db.execute(
            select(Prescription)
            .options(
                selectinload(Prescription.items).selectinload(PrescriptionItem.drug),
                selectinload(Prescription.prescriber),
            )
            .where(Prescription.patient_id == patient_id)
            .order_by(desc(Prescription.prescription_date))
        )
        prescriptions = result.scalars().all()

        active_prescriptions = []
        past_prescriptions = []

        for rx in prescriptions:
            # Check if prescription is still valid (not expired, not fully used)
            is_active = await self._is_prescription_active(rx)
            can_refill, refills_remaining = await self._check_refill_eligibility(rx)

            # Build medication info for each item
            medications = []
            for item in rx.items:
                drug = item.drug
                medication_info = MedicationInfo(
                    drug_id=drug.id,
                    drug_name=drug.name,
                    generic_name=drug.generic_name or "",
                    dosage=item.dosage or "",
                    dose_unit=item.dose_unit or "",
                    frequency=item.frequency or "",
                    route=item.route or "",
                    duration_days=item.duration_days,
                    quantity=item.quantity,
                    quantity_dispensed=item.quantity_dispensed or 0,
                    refills_allowed=item.refills_allowed or 0,
                    refills_used=item.refills_used or 0,
                    refills_remaining=max(0, (item.refills_allowed or 0) - (item.refills_used or 0)),
                    instructions=item.instructions,
                    warnings=self._get_medication_warnings(drug),
                )
                medications.append(medication_info)

            prescription_item = PrescriptionItemResponse(
                id=rx.id,
                prescription_number=rx.prescription_number,
                prescription_date=rx.prescription_date,
                prescriber_name=rx.prescriber.full_name if rx.prescriber else "Unknown",
                diagnosis=rx.diagnosis,
                status=rx.status,
                medications=medications,
                is_fully_dispensed=all(
                    m.quantity_dispensed >= m.quantity for m in medications
                ),
                can_refill=can_refill,
                refills_remaining=refills_remaining,
                expires_at=rx.valid_until,
            )

            if is_active:
                active_prescriptions.append(prescription_item)
            else:
                past_prescriptions.append(prescription_item)

        return {
            "active_prescriptions": active_prescriptions,
            "past_prescriptions": past_prescriptions,
        }

    async def check_refill_eligibility(
        self, patient_id: int, prescription_item_ids: List[int]
    ) -> List[RefillEligibilityCheck]:
        """Check if specific prescription items are eligible for refill

        Returns eligibility status for each requested item.
        """
        eligibility_results = []

        # Get prescription items
        result = await self.db.execute(
            select(PrescriptionItem)
            .options(
                selectinload(PrescriptionItem.drug),
                selectinload(PrescriptionItem.prescription),
            )
            .where(
                and_(
                    PrescriptionItem.id.in_(prescription_item_ids),
                    PrescriptionItem.prescription.has(patient_id=patient_id),
                )
            )
        )
        items = result.scalars().all()

        for item in items:
            eligibility_status, message, next_refill_date = await self._check_item_eligibility(item)

            eligibility_results.append(
                RefillEligibilityCheck(
                    prescription_item_id=item.id,
                    drug_name=item.drug.name,
                    eligible=eligibility_status == RefillEligibility.ELIGIBLE,
                    eligibility_status=eligibility_status,
                    refills_remaining=max(0, (item.refills_allowed or 0) - (item.refills_used or 0)),
                    next_refill_date=next_refill_date,
                    message=message,
                )
            )

        return eligibility_results

    async def create_refill_request(
        self, patient_id: int, request: RefillRequestCreate
    ) -> RefillRequestResponse:
        """Create a new prescription refill request

        Validates eligibility, creates request with items, generates request number.
        """
        # Validate patient exists
        patient_result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = patient_result.scalar_one_or_none()
        if not patient:
            raise ValueError("Patient not found")

        # Check eligibility for all items
        prescription_item_ids = [item.prescription_item_id for item in request.items]
        eligibility_checks = await self.check_refill_eligibility(
            patient_id, prescription_item_ids
        )

        # Ensure all items are eligible
        ineligible_items = [check for check in eligibility_checks if not check.eligible]
        if ineligible_items:
            error_msg = "; ".join(
                [f"{check.drug_name}: {check.message}" for check in ineligible_items]
            )
            raise ValueError(f"Some medications are not eligible for refill: {error_msg}")

        # Generate unique request number
        request_number = await self._generate_request_number()

        # Create refill request
        refill_request = PrescriptionRefillRequest(
            request_number=request_number,
            patient_id=patient_id,
            status="pending",
            notes=request.notes,
            preferred_pickup_date=request.preferred_pickup_date,
            items=[item.model_dump() for item in request.items],
            expires_at=datetime.utcnow() + timedelta(days=30),  # Expires in 30 days
        )

        self.db.add(refill_request)
        await self.db.flush()

        # Create individual refill items
        for item_request in request.items:
            # Get prescription item details
            item_result = await self.db.execute(
                select(PrescriptionItem).where(
                    PrescriptionItem.id == item_request.prescription_item_id
                )
            )
            prescription_item = item_result.scalar_one()

            refill_item = PrescriptionRefillItem(
                refill_request_id=refill_request.id,
                prescription_id=item_request.prescription_id,
                prescription_item_id=item_request.prescription_item_id,
                drug_id=item_request.drug_id,
                drug_name=item_request.drug_name,
                quantity_requested=item_request.quantity_requested,
                status="pending",
            )
            self.db.add(refill_item)

        await self.db.commit()
        await self.db.refresh(refill_request)

        return RefillRequestResponse(
            request_id=refill_request.id,
            status=refill_request.status.value,
            message="Refill request submitted successfully. You will be notified when it is reviewed.",
            estimated_processing_time="1-2 business days",
            items_count=len(request.items),
        )

    async def get_refill_requests(self, patient_id: int) -> Dict[str, Any]:
        """Get all refill requests for a patient, grouped by status"""
        result = await self.db.execute(
            select(PrescriptionRefillRequest)
            .options(selectinload(PrescriptionRefillRequest.items))
            .where(PrescriptionRefillRequest.patient_id == patient_id)
            .order_by(desc(PrescriptionRefillRequest.created_at))
        )
        requests = result.scalars().all()

        # Count by status
        status_counts = {
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "ready_for_pickup": 0,
            "completed": 0,
        }

        request_details = []
        for req in requests:
            status_counts[req.status.value] = status_counts.get(req.status.value, 0) + 1

            request_details.append(
                {
                    "id": req.id,
                    "request_number": req.request_number,
                    "patient_id": req.patient_id,
                    "items": req.items,
                    "notes": req.notes,
                    "preferred_pickup_date": req.preferred_pickup_date,
                    "status": req.status.value,
                    "rejection_reason": req.rejection_reason,
                    "created_at": req.created_at,
                    "updated_at": req.updated_at,
                    "processed_at": req.reviewed_at,
                    "approved_by": None,  # Would need to join User table
                    "ready_for_pickup_at": req.ready_for_pickup_at,
                }
            )

        return {
            "requests": request_details,
            "total": len(requests),
            **status_counts,
        }

    async def _is_prescription_active(self, prescription: Prescription) -> bool:
        """Check if prescription is still active (not expired, has refills)"""
        # Check if expired
        if prescription.valid_until and prescription.valid_until < date.today():
            return False

        # Check if any items have refills remaining
        for item in prescription.items:
            refills_remaining = (item.refills_allowed or 0) - (item.refills_used or 0)
            if refills_remaining > 0:
                return True

        return False

    async def _check_refill_eligibility(
        self, prescription: Prescription
    ) -> tuple[bool, int]:
        """Check if prescription has refills remaining

        Returns (can_refill, refills_remaining)
        """
        total_refills_allowed = sum(item.refills_allowed or 0 for item in prescription.items)
        total_refills_used = sum(item.refills_used or 0 for item in prescription.items)
        refills_remaining = max(0, total_refills_allowed - total_refills_used)

        return (refills_remaining > 0, refills_remaining)

    async def _check_item_eligibility(
        self, item: PrescriptionItem
    ) -> tuple[str, str, Optional[date]]:
        """Check eligibility for a single prescription item

        Returns (eligibility_status, message, next_refill_date)
        """
        # Check refills remaining
        refills_remaining = (item.refills_allowed or 0) - (item.refills_used or 0)
        if refills_remaining <= 0:
            return (
                RefillEligibility.MAX_REFILLS_REACHED,
                "No refills remaining for this medication",
                None,
            )

        # Check prescription expiration
        prescription = item.prescription
        if prescription.valid_until and prescription.valid_until < date.today():
            return (
                RefillEligibility.EXPIRED,
                f"Prescription expired on {prescription.valid_until}",
                None,
            )

        # Check if last dispense was too recent (minimum 21 days between refills)
        last_dispense_result = await self.db.execute(
            select(Dispense)
            .where(
                and_(
                    Dispense.prescription_item_id == item.id,
                    Dispense.status == DispenseStatus.COMPLETED,
                )
            )
            .order_by(desc(Dispense.dispensed_at))
            .limit(1)
        )
        last_dispense = last_dispense_result.scalar_one_or_none()

        if last_dispense and last_dispense.dispensed_at:
            days_since_last_dispense = (date.today() - last_dispense.dispensed_at.date()).days
            min_days = 21  # Minimum days between refills
            if days_since_last_dispense < min_days:
                next_refill_date = last_dispense.dispensed_at.date() + timedelta(days=min_days)
                return (
                    RefillEligibility.TOO_SOON,
                    f"Refill available in {min_days - days_since_last_dispense} days",
                    next_refill_date,
                )

        # All checks passed
        return (RefillEligibility.ELIGIBLE, "Eligible for refill", None)

    async def _generate_request_number(self) -> str:
        """Generate unique refill request number"""
        today = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = secrets.token_hex(3).upper()  # 6 character random string
        return f"REFILL-{today}-{random_suffix}"

    def _get_medication_warnings(self, drug: Drug) -> Optional[List[str]]:
        """Get warnings for a medication"""
        warnings = []

        if drug.is_narcotic:
            warnings.append("Controlled substance - additional regulations apply")

        if drug.requires_prescription:
            warnings.append("Requires valid prescription")

        # Add any black box warnings
        if drug.contraindications:
            warnings.append(f"Contraindications: {drug.contraindications}")

        return warnings if warnings else None
