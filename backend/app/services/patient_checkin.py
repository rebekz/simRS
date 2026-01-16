"""Patient Check-in Service for STORY-007: Returning Patient Check-in

This module provides services for:
- Fast patient lookup with multiple search methods
- Patient summary view (last visit, diagnoses, allergies)
- Quick check-in workflow
- Insurance status verification
- Patient information updates during check-in

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func

from app.models.patient import Patient
from app.models.encounter import Encounter, Diagnosis
from app.models.allergy import Allergy
from app.models.queue import QueueTicket, QueueDepartment, QueueStatus, QueuePriority
from app.models.user import User
from app.models.audit_log import AuditLog


logger = logging.getLogger(__name__)


class PatientNotFoundError(Exception):
    """Patient not found error"""
    pass


class CheckinValidationError(Exception):
    """Check-in validation error"""
    pass


class PatientCheckinService(object):
    """Service for patient check-in operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def lookup_patient(
        self,
        search_term: Optional[str] = None,
        mrn: Optional[str] = None,
        nik: Optional[str] = None,
        bpjs_number: Optional[str] = None,
        phone: Optional[str] = None,
        name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        limit: int = 20,
    ) -> List[Dict[str, any]]:
        """Fast patient lookup with multiple search methods

        Args:
            search_term: General search term (searches name, MRN, phone, NIK)
            mrn: Medical record number (exact match)
            nik: NIK (exact match)
            bpjs_number: BPJS card number (exact match)
            phone: Phone number (partial match)
            name: Patient name (partial match)
            date_of_birth: Date of birth (exact match)
            limit: Maximum results to return

        Returns:
            List of patient dictionaries with summary info

        Target: Lookup time <10 seconds (typically <2 seconds with proper indexing)
        """
        query = select(Patient).where(Patient.is_active == True)

        # Build search conditions
        conditions = []

        if search_term:
            # General search - multiple fields
            search_pattern = "%{}%".format(search_term)
            conditions.append(
                or_(
                    Patient.medical_record_number.ilike(search_pattern),
                    Patient.nik.ilike(search_pattern),
                    Patient.bpjs_card_number.ilike(search_pattern),
                    Patient.phone.ilike(search_pattern),
                    Patient.full_name.ilike(search_pattern),
                )
            )
        else:
            # Specific searches - exact matches where possible
            if mrn:
                conditions.append(Patient.medical_record_number == mrn)
            if nik:
                conditions.append(Patient.nik == nik)
            if bpjs_number:
                conditions.append(Patient.bpjs_card_number == bpjs_number)
            if phone:
                conditions.append(Patient.phone.ilike("%{}%".format(phone)))
            if name:
                conditions.append(Patient.full_name.ilike("%{}%".format(name)))
            if date_of_birth:
                conditions.append(Patient.date_of_birth == date_of_birth)

        if conditions:
            query = query.where(and_(*conditions))

        # Order by most recently updated/created
        query = query.order_by(Patient.updated_at.desc()).limit(limit)

        result = await self.db.execute(query)
        patients = result.scalars().all()

        # Get last visit info for each patient
        patient_summaries = []
        for p in patients:
            last_visit = await self._get_last_visit_info(p.id)
            patient_summaries.append({
                "id": p.id,
                "mrn": p.medical_record_number,
                "nik": p.nik,
                "full_name": p.full_name,
                "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
                "gender": p.gender.value if p.gender else None,
                "phone": p.phone,
                "email": p.email,
                "address": p.address,
                "city": p.city,
                "blood_type": p.blood_type.value if p.blood_type else None,
                "bpjs_card_number": p.bpjs_card_number,
                "last_visit": last_visit,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            })

        return patient_summaries

    async def get_patient_summary(
        self,
        patient_id: int,
    ) -> Dict[str, any]:
        """Get comprehensive patient summary for check-in

        Args:
            patient_id: Patient ID

        Returns:
            Patient summary with demographics, last visit, diagnoses, allergies

        Raises:
            PatientNotFoundError: If patient not found
        """
        # Get patient
        patient = await self._get_patient_by_id(patient_id)

        if not patient:
            raise PatientNotFoundError("Patient not found")

        # Get last visit info
        last_visit = await self._get_last_visit_info(patient_id)

        # Get recent diagnoses (from last visit)
        recent_diagnoses = await self._get_recent_diagnoses(patient_id)

        # Get allergies
        allergies = await self._get_patient_allergies(patient_id)

        # Get insurance info
        insurance = await self._get_patient_insurance(patient_id)

        return {
            "patient": {
                "id": patient.id,
                "mrn": patient.medical_record_number,
                "nik": patient.nik,
                "full_name": patient.full_name,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "gender": patient.gender.value if patient.gender else None,
                "phone": patient.phone,
                "email": patient.email,
                "address": patient.address,
                "city": patient.city,
                "province": patient.province,
                "postal_code": patient.postal_code,
                "blood_type": patient.blood_type.value if patient.blood_type else None,
                "bpjs_card_number": patient.bpjs_card_number,
                "photo_url": patient.photo_url,
                "updated_at": patient.updated_at.isoformat() if patient.updated_at else None,
            },
            "last_visit": last_visit,
            "recent_diagnoses": recent_diagnoses,
            "allergies": allergies,
            "insurance": insurance,
        }

    async def quick_checkin(
        self,
        patient_id: int,
        department: QueueDepartment,
        encounter_type: str,
        chief_complaint: Optional[str] = None,
        poli_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        appointment_id: Optional[int] = None,
        priority: QueuePriority = QueuePriority.NORMAL,
        checked_in_by: int = None,
    ) -> Dict[str, any]:
        """Quick check-in workflow (single click after patient lookup)

        Args:
            patient_id: Patient ID
            department: Department to check into
            encounter_type: Type of encounter (outpatient, emergency, etc.)
            chief_complaint: Patient's chief complaint
            poli_id: Polyclinic ID (for POLI department)
            doctor_id: Doctor ID (if specific doctor)
            appointment_id: Appointment ID (if pre-booked)
            priority: Queue priority
            checked_in_by: User ID performing check-in

        Returns:
            Check-in result with encounter and queue ticket info

        Raises:
            PatientNotFoundError: If patient not found
            CheckinValidationError: If validation fails
        """
        # Get patient
        patient = await self._get_patient_by_id(patient_id)

        if not patient:
            raise PatientNotFoundError("Patient not found")

        # Verify insurance status if BPJS patient
        if patient.bpjs_card_number:
            insurance_valid = await self._verify_insurance_status(patient_id)
            if not insurance_valid["is_active"]:
                logger.warning("Patient {} has inactive insurance".format(patient_id))

        # Create encounter
        encounter = Encounter(
            patient_id=patient_id,
            encounter_type=encounter_type,
            encounter_date=date.today(),
            department=department.value,
            doctor_id=doctor_id,
            chief_complaint=chief_complaint,
            status="active",
            is_urgent=(priority == QueuePriority.URGENT),
        )

        self.db.add(encounter)
        await self.db.flush()

        # Generate queue number
        ticket_number = await self._generate_queue_number(department)

        # Calculate queue position
        queue_position = await self._get_next_queue_position(department)

        # Calculate estimated wait time
        estimated_wait = await self._calculate_wait_time(department, queue_position)

        # Create queue ticket
        queue_ticket = QueueTicket(
            ticket_number=ticket_number,
            department=department,
            date=date.today(),
            patient_id=patient_id,
            priority=priority,
            status=QueueStatus.WAITING,
            poli_id=poli_id,
            doctor_id=doctor_id,
            appointment_id=appointment_id,
            queue_position=queue_position,
            people_ahead=max(0, queue_position - 1),
            estimated_wait_minutes=estimated_wait,
        )

        self.db.add(queue_ticket)
        await self.db.flush()

        # Create audit log
        await self._create_checkin_audit_log(
            patient,
            encounter,
            queue_ticket,
            checked_in_by
        )

        logger.info(
            "Patient check-in: {} - {} - Ticket: {}".format(
                patient.medical_record_number,
                patient.full_name,
                ticket_number
            )
        )

        return {
            "encounter_id": encounter.id,
            "ticket_id": queue_ticket.id,
            "ticket_number": ticket_number,
            "queue_position": queue_position,
            "people_ahead": max(0, queue_position - 1),
            "estimated_wait_minutes": estimated_wait,
            "department": department.value,
            "message": "Patient checked in successfully",
        }

    async def update_patient_during_checkin(
        self,
        patient_id: int,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        province: Optional[str] = None,
        postal_code: Optional[str] = None,
        bpjs_card_number: Optional[str] = None,
        updated_by: int = None,
    ) -> Dict[str, any]:
        """Update patient information during check-in

        Args:
            patient_id: Patient ID
            phone: Updated phone number
            email: Updated email
            address: Updated address
            city: Updated city
            province: Updated province
            postal_code: Updated postal code
            bpjs_card_number: Updated BPJS card number
            updated_by: User ID making updates

        Returns:
            Updated patient info

        Raises:
            PatientNotFoundError: If patient not found
        """
        patient = await self._get_patient_by_id(patient_id)

        if not patient:
            raise PatientNotFoundError("Patient not found")

        # Track changes for highlighting
        changes = {}

        # Update fields
        if phone and phone != patient.phone:
            changes["phone"] = {"old": patient.phone, "new": phone}
            patient.phone = phone

        if email and email != patient.email:
            changes["email"] = {"old": patient.email, "new": email}
            patient.email = email

        if address and address != patient.address:
            changes["address"] = {"old": patient.address, "new": address}
            patient.address = address

        if city and city != patient.city:
            changes["city"] = {"old": patient.city, "new": city}
            patient.city = city

        if province and province != patient.province:
            changes["province"] = {"old": patient.province, "new": province}
            patient.province = province

        if postal_code and postal_code != patient.postal_code:
            changes["postal_code"] = {"old": patient.postal_code, "new": postal_code}
            patient.postal_code = postal_code

        if bpjs_card_number and bpjs_card_number != patient.bpjs_card_number:
            changes["bpjs_card_number"] = {
                "old": patient.bpjs_card_number,
                "new": bpjs_card_number
            }
            patient.bpjs_card_number = bpjs_card_number

        patient.updated_at = datetime.utcnow()

        await self.db.flush()

        logger.info(
            "Patient updated during check-in: {} - {}".format(
                patient.medical_record_number,
                patient.full_name
            )
        )

        return {
            "patient_id": patient.id,
            "mrn": patient.medical_record_number,
            "full_name": patient.full_name,
            "changes": changes,
            "updated_at": patient.updated_at.isoformat() if patient.updated_at else None,
        }

    async def verify_insurance_status(
        self,
        patient_id: int,
    ) -> Dict[str, any]:
        """Verify current insurance status for patient

        Args:
            patient_id: Patient ID

        Returns:
            Insurance status information
        """
        patient = await self._get_patient_by_id(patient_id)

        if not patient:
            raise PatientNotFoundError("Patient not found")

        # Get insurance info
        from app.models.patient import PatientInsurance

        query = select(PatientInsurance).where(
            and_(
                PatientInsurance.patient_id == patient_id,
                PatientInsurance.is_active == True
            )
        ).order_by(PatientInsurance.created_at.desc())

        result = await self.db.execute(query)
        insurance = result.scalar_one_or_none()

        if not insurance:
            return {
                "has_insurance": False,
                "is_active": False,
                "insurance_type": None,
                "provider_name": None,
                "policy_number": None,
                "expiry_date": None,
                "is_valid": False,
            }

        # Check if expired
        is_expired = False
        if insurance.expiry_date:
            is_expired = insurance.expiry_date < date.today()

        return {
            "has_insurance": True,
            "is_active": insurance.is_active,
            "insurance_type": insurance.insurance_type.value if insurance.insurance_type else None,
            "provider_name": insurance.provider_name,
            "policy_number": insurance.policy_number,
            "insurance_number": insurance.insurance_number,
            "expiry_date": insurance.expiry_date.isoformat() if insurance.expiry_date else None,
            "is_valid": insurance.is_active and not is_expired,
            "is_expired": is_expired,
        }

    # ==============================================================================
    # Private Helper Methods
    # ==============================================================================

    async def _get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID

        Args:
            patient_id: Patient ID

        Returns:
            Patient instance or None
        """
        query = select(Patient).where(
            and_(
                Patient.id == patient_id,
                Patient.is_active == True
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_last_visit_info(self, patient_id: int) -> Optional[Dict[str, any]]:
        """Get last visit information for patient

        Args:
            patient_id: Patient ID

        Returns:
            Last visit info or None
        """
        query = select(Encounter).where(
            and_(
                Encounter.patient_id == patient_id,
                Encounter.status.in_(["active", "completed"])
            )
        ).order_by(Encounter.encounter_date.desc(), Encounter.start_time.desc())

        result = await self.db.execute(query)
        last_visit = result.scalar_one_or_none()

        if not last_visit:
            return None

        return {
            "encounter_id": last_visit.id,
            "encounter_date": last_visit.encounter_date.isoformat() if last_visit.encounter_date else None,
            "encounter_type": last_visit.encounter_type,
            "department": last_visit.department,
            "doctor_id": last_visit.doctor_id,
            "chief_complaint": last_visit.chief_complaint,
            "status": last_visit.status,
        }

    async def _get_recent_diagnoses(
        self,
        patient_id: int,
        limit: int = 10,
    ) -> List[Dict[str, any]]:
        """Get recent diagnoses for patient

        Args:
            patient_id: Patient ID
            limit: Maximum diagnoses to return

        Returns:
            List of recent diagnoses
        """
        # Get most recent encounter
        query = select(Encounter).where(
            and_(
                Encounter.patient_id == patient_id,
                Encounter.status == "completed"
            )
        ).order_by(Encounter.encounter_date.desc()).limit(1)

        result = await self.db.execute(query)
        last_encounter = result.scalar_one_or_none()

        if not last_encounter:
            return []

        # Get diagnoses from last encounter
        diag_query = select(Diagnosis).where(
            Diagnosis.encounter_id == last_encounter.id
        ).order_by(Diagnosis.diagnosis_type)

        diag_result = await self.db.execute(diag_query)
        diagnoses = diag_result.scalars().all()

        return [
            {
                "icd_10_code": d.icd_10_code,
                "diagnosis_name": d.diagnosis_name,
                "diagnosis_type": d.diagnosis_type,
                "is_chronic": d.is_chronic,
            }
            for d in diagnoses
        ]

    async def _get_patient_allergies(
        self,
        patient_id: int,
    ) -> List[Dict[str, any]]:
        """Get patient allergies

        Args:
            patient_id: Patient ID

        Returns:
            List of allergies
        """
        query = select(Allergy).where(
            and_(
                Allergy.patient_id == patient_id,
                Allergy.is_active == True
            )
        ).order_by(Allergy.severity.desc())

        result = await self.db.execute(query)
        allergies = result.scalars().all()

        return [
            {
                "allergen": a.allergen,
                "allergy_type": a.allergy_type.value if a.allergy_type else None,
                "severity": a.severity.value if a.severity else None,
                "reaction": a.reaction,
                "onset_date": a.onset_date.isoformat() if a.onset_date else None,
            }
            for a in allergies
        ]

    async def _get_patient_insurance(
        self,
        patient_id: int,
    ) -> Optional[Dict[str, any]]:
        """Get patient insurance information

        Args:
            patient_id: Patient ID

        Returns:
            Insurance info or None
        """
        from app.models.patient import PatientInsurance

        query = select(PatientInsurance).where(
            and_(
                PatientInsurance.patient_id == patient_id,
                PatientInsurance.is_active == True
            )
        ).order_by(PatientInsurance.created_at.desc())

        result = await self.db.execute(query)
        insurance = result.scalar_one_or_none()

        if not insurance:
            return None

        return {
            "insurance_type": insurance.insurance_type.value if insurance.insurance_type else None,
            "insurance_number": insurance.insurance_number,
            "provider_name": insurance.provider_name,
            "policy_number": insurance.policy_number,
            "expiry_date": insurance.expiry_date.isoformat() if insurance.expiry_date else None,
            "is_active": insurance.is_active,
        }

    async def _generate_queue_number(
        self,
        department: QueueDepartment,
    ) -> str:
        """Generate queue number for department

        Args:
            department: Department to generate number for

        Returns:
            Queue number (e.g., "A-001", "F-045")

        Format: {Department Prefix}-{Daily Sequence}
        Prefixes:
        - POLI: P
        - FARMASI: F
        - LAB: L
        - RADIOLOGI: R
        - KASIR: K
        - EMERGENCY: E
        """
        # Get department prefix
        prefixes = {
            QueueDepartment.POLI: "P",
            QueueDepartment.FARMASI: "F",
            QueueDepartment.LAB: "L",
            QueueDepartment.RADIOLOGI: "R",
            QueueDepartment.KASIR: "K",
            QueueDepartment.IGD: "E",
        }

        prefix = prefixes.get(department, "X")

        # Get next sequence for today
        today = date.today()

        query = select(func.count()).select_from(QueueTicket).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today
            )
        )

        result = await self.db.execute(query)
        count = result.scalar() or 0

        sequence = count + 1

        return "{0}-{1:03d}".format(prefix, sequence)

    async def _get_next_queue_position(
        self,
        department: QueueDepartment,
    ) -> int:
        """Get next queue position for department

        Args:
            department: Department to check

        Returns:
            Next queue position (1-indexed)
        """
        today = date.today()

        query = select(func.count()).select_from(QueueTicket).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today,
                QueueTicket.status == QueueStatus.WAITING
            )
        )

        result = await self.db.execute(query)
        waiting_count = result.scalar() or 0

        return waiting_count + 1

    async def _calculate_wait_time(
        self,
        department: QueueDepartment,
        queue_position: int,
    ) -> int:
        """Calculate estimated wait time

        Args:
            department: Department
            queue_position: Position in queue

        Returns:
            Estimated wait time in minutes

        Simple heuristic: 5 minutes per person ahead
        Can be enhanced with historical service time data
        """
        people_ahead = max(0, queue_position - 1)

        # Base time per patient (varies by department)
        service_times = {
            QueueDepartment.POLI: 10,      # 10 minutes per patient
            QueueDepartment.FARMASI: 5,    # 5 minutes per prescription
            QueueDepartment.LAB: 3,        # 3 minutes per sample
            QueueDepartment.RADIOLOGI: 15, # 15 minutes per imaging
            QueueDepartment.KASIR: 3,      # 3 minutes per payment
            QueueDepartment.IGD: 5,        # 5 minutes per triage
        }

        service_time = service_times.get(department, 5)

        return people_ahead * service_time

    async def _verify_insurance_status(
        self,
        patient_id: int,
    ) -> Dict[str, any]:
        """Verify insurance status (internal method)

        Args:
            patient_id: Patient ID

        Returns:
            Insurance status with is_active flag
        """
        status = await self.verify_insurance_status(patient_id)
        return status

    async def _create_checkin_audit_log(
        self,
        patient: Patient,
        encounter: Encounter,
        queue_ticket: QueueTicket,
        checked_in_by: int,
    ):
        """Create audit log for patient check-in

        Args:
            patient: Patient being checked in
            encounter: Encounter created
            queue_ticket: Queue ticket created
            checked_in_by: User ID performing check-in
        """
        # Get user info
        if checked_in_by:
            query = select(User).where(User.id == checked_in_by)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            username = user.username if user else "system"
        else:
            username = "system"

        audit_log = AuditLog(
            user_id=checked_in_by,
            username=username,
            action="CREATE",
            resource_type="PatientCheckin",
            resource_id=patient.medical_record_number,
            request_path="/patient-registration/checkin",
            request_method="POST",
            success=True,
            additional_data={
                "patient_name": patient.full_name,
                "mrn": patient.medical_record_number,
                "encounter_id": encounter.id,
                "ticket_number": queue_ticket.ticket_number,
                "department": queue_ticket.department.value,
            },
        )

        self.db.add(audit_log)
        await self.db.flush()


# Factory function
def get_patient_checkin_service(db: AsyncSession) -> PatientCheckinService:
    """Get patient check-in service"""
    return PatientCheckinService(db)
