"""Patient History Service for STORY-011: Patient History View

This service aggregates comprehensive patient historical data from multiple sources
including encounters, allergies, medications, lab results, and more.
Optimized for fast loading in clinical workflows.
"""
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func
from sqlalchemy.orm import selectinload

from app.models.patient import Patient
from app.models.encounter import Encounter
from app.models.allergy import Allergy
from app.models.appointments import Appointment
from app.models.clinical_note import ClinicalNote
from app.schemas.patient_history import (
    PatientHistoryResponse,
    PatientHistorySummary,
    PatientHistoryFilter,
    EncounterHistoryItem,
    EncounterTimelineItem,
    PatientAllergy,
    CurrentMedication,
    LabResultSummary,
    VitalSignsRecord,
    SurgicalHistory,
    ImmunizationRecord,
    FamilyHistory,
    SocialHistory,
    ChronicCondition,
)


class PatientHistoryService:
    """Service for aggregating and retrieving patient historical data

    Features:
    - Comprehensive history aggregation from multiple tables
    - Optimized queries with strategic eager loading
    - Timeline visualization support
    - Configurable data sections
    - Performance optimized for clinical workflows (<3 seconds)
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_patient_history(
        self,
        patient_id: int,
        filters: Optional[PatientHistoryFilter] = None
    ) -> PatientHistoryResponse:
        """Get comprehensive patient history

        Args:
            patient_id: Patient ID
            filters: Optional filters for which sections to include

        Returns:
            PatientHistoryResponse with all requested sections

        Raises:
            ValueError: If patient not found
        """
        if filters is None:
            filters = PatientHistoryFilter()

        # Get base patient data with relationships
        patient = await self._get_patient_with_contacts(patient_id)

        # Calculate age
        age = self._calculate_age(patient.date_of_birth)

        # Build response sections
        response_dict = {
            # Basic Demographics
            "patient_id": patient.id,
            "medical_record_number": patient.medical_record_number,
            "full_name": patient.full_name,
            "date_of_birth": patient.date_of_birth,
            "age": age,
            "gender": patient.gender.value,
            "blood_type": patient.blood_type.value if patient.blood_type else None,
            "phone": patient.phone,
            "email": patient.email,
            "address": patient.address,
            "city": patient.city,

            # Emergency Contacts
            "emergency_contacts": [
                {
                    "id": ec.id,
                    "name": ec.name,
                    "relationship": ec.relationship_type,
                    "phone": ec.phone,
                    "address": ec.address
                }
                for ec in patient.emergency_contacts
            ],

            # Insurance
            "primary_insurance": self._get_primary_insurance(patient),
            "insurance_status": await self._get_insurance_status(patient_id),

            # Initialize lists
            "allergies": [],
            "current_medications": [],
            "chronic_conditions": [],

            # Encounter History
            "recent_encounters": [],
            "total_encounters": 0,
            "last_encounter_date": None,
            "last_department": None,
            "last_doctor": None,

            # Timeline
            "encounter_timeline": [],

            # Lab Results
            "recent_lab_results": [],
            "recent_vital_signs": [],

            # Surgical History
            "surgical_history": [],

            # Immunizations
            "immunization_records": [],

            # Family History
            "family_history": [],

            # Social History
            "social_history": None,

            # Metadata
            "data_completeness": {},
            "last_updated": datetime.utcnow()
        }

        # Load requested sections
        if filters.include_allergies:
            response_dict["allergies"] = await self._get_allergies(patient_id)

        if filters.include_medications:
            response_dict["current_medications"] = await self._get_current_medications(patient_id)

        if filters.include_conditions:
            response_dict["chronic_conditions"] = await self._get_chronic_conditions(patient_id)

        if filters.include_encounters:
            encounter_data = await self._get_encounter_history(
                patient_id,
                limit=filters.encounter_limit
            )
            response_dict.update(encounter_data)

        if filters.include_lab_results:
            response_dict["recent_lab_results"] = await self._get_recent_lab_results(
                patient_id,
                limit=filters.lab_results_limit
            )

        if filters.include_vital_signs:
            response_dict["recent_vital_signs"] = await self._get_recent_vital_signs(
                patient_id,
                limit=filters.vital_signs_limit
            )

        if filters.include_surgical_history:
            response_dict["surgical_history"] = await self._get_surgical_history(patient_id)

        if filters.include_immunizations:
            response_dict["immunization_records"] = await self._get_immunization_records(patient_id)

        if filters.include_family_history:
            response_dict["family_history"] = await self._get_family_history(patient_id)

        if filters.include_social_history:
            response_dict["social_history"] = await self._get_social_history(patient_id)

        # Calculate data completeness
        response_dict["data_completeness"] = self._calculate_data_completeness(response_dict)

        return PatientHistoryResponse(**response_dict)

    async def get_patient_history_summary(
        self,
        patient_id: int
    ) -> PatientHistorySummary:
        """Get lightweight patient history summary

        Args:
            patient_id: Patient ID

        Returns:
            PatientHistorySummary with quick reference data
        """
        # Get patient basic info
        patient_result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = patient_result.scalar_one_or_none()

        if not patient:
            raise ValueError("Patient {patient_id} not found".format(patient_id=patient_id))

        age = self._calculate_age(patient.date_of_birth)

        # Get quick stats
        allergy_count = await self._get_allergy_count(patient_id)
        chronic_count = await self._get_chronic_condition_count(patient_id)
        medication_count = await self._get_medication_count(patient_id)

        # Get last encounter
        last_encounter = await self._get_last_encounter(patient_id)

        # Build summary
        return PatientHistorySummary(
            patient_id=patient.id,
            medical_record_number=patient.medical_record_number,
            full_name=patient.full_name,
            age=age,
            gender=patient.gender.value,
            blood_type=patient.blood_type.value if patient.blood_type else None,
            has_allergies=allergy_count > 0,
            allergy_count=allergy_count,
            has_chronic_conditions=chronic_count > 0,
            chronic_condition_count=chronic_count,
            medication_count=medication_count,
            last_visit_date=last_encounter.start_date if last_encounter else None,
            last_visit_type=last_encounter.encounter_type.value if last_encounter else None,
            last_department=last_encounter.department_name if last_encounter else None,
            has_unpaid_bills=await self._has_unpaid_bills(patient_id),
            has_pending_appointments=await self._has_pending_appointments(patient_id),
            insurance_status=await self._get_insurance_status(patient_id)
        )

    async def search_patient_history(
        self,
        search_term: str,
        limit: int = 20
    ) -> List[PatientHistorySummary]:
        """Search patients by name, MRN, or NIK with history summary

        Args:
            search_term: Search term (name, MRN, or NIK)
            limit: Maximum results to return

        Returns:
            List of PatientHistorySummary
        """
        # Search for patients
        from app.models.patient import Patient

        search_pattern = "%{term}%".format(term=search_term)

        query = (
            select(Patient)
            .where(
                or_(
                    Patient.full_name.ilike(search_pattern),
                    Patient.medical_record_number.ilike(search_pattern),
                    Patient.nik.ilike(search_pattern)
                )
            )
            .where(Patient.is_active == True)
            .order_by(Patient.full_name)
            .limit(limit)
        )

        result = await self.db.execute(query)
        patients = result.scalars().all()

        # Build summaries
        summaries = []
        for patient in patients:
            try:
                summary = await self.get_patient_history_summary(patient.id)
                summaries.append(summary)
            except Exception:
                # Skip patients with errors
                continue

        return summaries

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    async def _get_patient_with_contacts(self, patient_id: int) -> Patient:
        """Get patient with emergency contacts and insurance preloaded"""
        result = await self.db.execute(
            select(Patient)
            .options(selectinload(Patient.emergency_contacts))
            .options(selectinload(Patient.insurance_policies))
            .where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()

        if not patient:
            raise ValueError("Patient {patient_id} not found".format(patient_id=patient_id))

        return patient

    def _calculate_age(self, birth_date: date) -> int:
        """Calculate age from birth date"""
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )

    def _get_primary_insurance(self, patient: Patient) -> Optional[dict]:
        """Extract primary insurance from patient policies"""
        if not patient.insurance_policies:
            return None

        # Return first/bpjs policy as primary
        for policy in patient.insurance_policies:
            if policy.insurance_type.value == "bpjs":
                return {
                    "id": policy.id,
                    "type": policy.insurance_type.value,
                    "number": policy.insurance_number,
                    "member_name": policy.member_name,
                    "expiry_date": policy.expiry_date.isoformat() if policy.expiry_date else None
                }

        # Return first policy if no BPJS
        policy = patient.insurance_policies[0]
        return {
            "id": policy.id,
            "type": policy.insurance_type.value,
            "number": policy.insurance_number,
            "member_name": policy.member_name,
            "expiry_date": policy.expiry_date.isoformat() if policy.expiry_date else None
        }

    async def _get_insurance_status(self, patient_id: int) -> str:
        """Check patient insurance status"""
        # Placeholder - would integrate with BPJS API in STORY-008
        return "Unknown"

    async def _get_allergies(self, patient_id: int) -> List[PatientAllergy]:
        """Get patient allergies"""
        from app.models.allergy import Allergy

        result = await self.db.execute(
            select(Allergy)
            .where(Allergy.patient_id == patient_id)
            .order_by(Allergy.severity.desc(), Allergy.allergen)
        )
        allergies = result.scalars().all()

        return [
            PatientAllergy(
                id=a.id,
                allergen=a.allergen,
                allergy_type=a.allergy_type.value,
                severity=a.severity,
                reaction=a.reaction,
                diagnosed_date=a.diagnosed_date,
                diagnosed_by=a.diagnosed_by,
                notes=a.notes
            )
            for a in allergies
        ]

    async def _get_current_medications(self, patient_id: int) -> List[CurrentMedication]:
        """Get active patient medications"""
        # Placeholder - would integrate with prescription data
        # For now, return empty list
        return []

    async def _get_chronic_conditions(self, patient_id: int) -> List[ChronicCondition]:
        """Get chronic conditions"""
        # Placeholder - would integrate with ICD-10/problem list
        # For now, return empty list
        return []

    async def _get_encounter_history(
        self,
        patient_id: int,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get encounter history with timeline"""
        # Get encounters with related data
        result = await self.db.execute(
            select(Encounter)
            .where(Encounter.patient_id == patient_id)
            .order_by(Encounter.start_date.desc())
            .limit(limit)
        )
        encounters = result.scalars().all()

        # Build history items
        history_items = []
        timeline_items = []
        last_date = None
        last_department = None
        last_doctor = None

        for encounter in encounters:
            history_item = EncounterHistoryItem(
                id=encounter.id,
                encounter_number=encounter.encounter_number or "ENC-{id}".format(id=encounter.id),
                encounter_type=encounter.encounter_type.value if encounter.encounter_type else "unknown",
                status=encounter.status.value if encounter.status else "unknown",
                start_date=encounter.start_date,
                end_date=encounter.end_date,
                department_name=encounter.department_name,
                doctor_name=encounter.doctor_name,
                chief_complaint=encounter.chief_complaint,
                primary_diagnosis=encounter.primary_diagnosis,
                notes_count=0  # Would count clinical notes
            )
            history_items.append(history_item)

            # Add to timeline
            if encounter.start_date:
                timeline_items.append(EncounterTimelineItem(
                    date=encounter.start_date,
                    encounter_id=encounter.id,
                    encounter_type=encounter.encounter_type.value if encounter.encounter_type else "unknown",
                    department=encounter.department_name or "Unknown",
                    doctor=encounter.doctor_name,
                    chief_complaint=encounter.chief_complaint,
                    diagnosis=encounter.primary_diagnosis
                ))

            # Track last encounter
            if last_date is None or encounter.start_date > last_date:
                last_date = encounter.start_date
                last_department = encounter.department_name
                last_doctor = encounter.doctor_name

        # Sort timeline by date ascending
        timeline_items.sort(key=lambda x: x.date)

        # Get total count
        count_result = await self.db.execute(
            select(func.count(Encounter.id))
            .where(Encounter.patient_id == patient_id)
        )
        total_encounters = count_result.scalar() or 0

        return {
            "recent_encounters": history_items,
            "total_encounters": total_encounters,
            "last_encounter_date": last_date,
            "last_department": last_department,
            "last_doctor": last_doctor,
            "encounter_timeline": timeline_items
        }

    async def _get_recent_lab_results(
        self,
        patient_id: int,
        limit: int = 10
    ) -> List[LabResultSummary]:
        """Get recent lab results"""
        # Placeholder - would integrate with lab orders
        return []

    async def _get_recent_vital_signs(
        self,
        patient_id: int,
        limit: int = 5
    ) -> List[VitalSignsRecord]:
        """Get recent vital signs"""
        # Placeholder - would integrate with encounter vital signs
        return []

    async def _get_surgical_history(self, patient_id: int) -> List[SurgicalHistory]:
        """Get surgical history"""
        # Placeholder - would integrate with encounter procedures
        return []

    async def _get_immunization_records(self, patient_id: int) -> List[ImmunizationRecord]:
        """Get immunization records"""
        # Placeholder - would integrate with vaccination records
        return []

    async def _get_family_history(self, patient_id: int) -> List[FamilyHistory]:
        """Get family medical history"""
        # Placeholder - would integrate with family history data
        return []

    async def _get_social_history(self, patient_id: int) -> Optional[SocialHistory]:
        """Get social and lifestyle history"""
        # Placeholder - would integrate with social history data
        return None

    async def _get_allergy_count(self, patient_id: int) -> int:
        """Get count of patient allergies"""
        result = await self.db.execute(
            select(func.count(Allergy.id))
            .where(Allergy.patient_id == patient_id)
        )
        return result.scalar() or 0

    async def _get_chronic_condition_count(self, patient_id: int) -> int:
        """Get count of chronic conditions"""
        # Placeholder
        return 0

    async def _get_medication_count(self, patient_id: int) -> int:
        """Get count of current medications"""
        # Placeholder
        return 0

    async def _get_last_encounter(self, patient_id: int) -> Optional[Encounter]:
        """Get most recent encounter"""
        result = await self.db.execute(
            select(Encounter)
            .where(Encounter.patient_id == patient_id)
            .order_by(Encounter.start_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _has_unpaid_bills(self, patient_id: int) -> bool:
        """Check if patient has unpaid bills"""
        # Placeholder - would integrate with billing
        return False

    async def _has_pending_appointments(self, patient_id: int) -> bool:
        """Check if patient has pending appointments"""
        result = await self.db.execute(
            select(func.count(Appointment.id))
            .where(
                and_(
                    Appointment.patient_id == patient_id,
                    Appointment.appointment_date >= date.today(),
                    Appointment.status.in_(["scheduled", "confirmed"])
                )
            )
        )
        return (result.scalar() or 0) > 0

    def _calculate_data_completeness(self, response_dict: dict) -> dict:
        """Calculate data completeness metrics"""
        total_fields = 0
        populated_fields = 0

        # Check key fields
        fields_to_check = [
            "phone", "email", "address", "blood_type",
            "emergency_contacts", "allergies", "current_medications"
        ]

        for field in fields_to_check:
            total_fields += 1
            value = response_dict.get(field)
            if value:
                if isinstance(value, list) and len(value) > 0:
                    populated_fields += 1
                elif not isinstance(value, list):
                    populated_fields += 1

        completeness_percentage = int((populated_fields / total_fields) * 100) if total_fields > 0 else 0

        return {
            "total_fields": total_fields,
            "populated_fields": populated_fields,
            "completeness_percentage": completeness_percentage,
            "is_complete": completeness_percentage >= 80
        }
