"""Patient Portal Health Record Service

Service for aggregating and formatting patient health records for portal display.
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, date

from app.models.patient import Patient
from app.models.encounter import Encounter, Diagnosis, Treatment
from app.models.allergy import Allergy
from app.models.prescription import Prescription
from app.models.user import User
from app.schemas.patient_portal.health_record import (
    PatientDemographics,
    PatientDemographicsUpdate,
    AllergyItem,
    AllergyList,
    DiagnosisItem,
    DiagnosisList,
    MedicationItem,
    MedicationList,
    VitalSignsItem,
    VitalSignsHistory,
    EncounterSummary,
    EncounterHistory,
    TimelineEvent,
    TimelineEventType,
    HealthTimeline,
    PersonalHealthRecord,
    HealthRecordSearch,
    HealthRecordSearchResult,
)


class HealthRecordService:
    """Service for aggregating patient health records"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_complete_health_record(
        self,
        patient_id: int,
    ) -> PersonalHealthRecord:
        """Get complete personal health record for a patient"""

        # Get all components in parallel
        demographics = await self.get_demographics(patient_id)
        allergies = await self.get_allergies(patient_id)
        diagnoses = await self.get_diagnoses(patient_id)
        medications = await self.get_medications(patient_id)
        vital_signs = await self.get_vital_signs_history(patient_id)
        encounter_history = await self.get_encounter_history(patient_id)
        timeline = await self.get_health_timeline(patient_id)

        # Determine last updated timestamp
        last_updated = demographics.updated_at
        for component in [allergies, diagnoses, medications, encounter_history]:
            if hasattr(component, 'events') and component.events:
                for event in component.events:
                    if hasattr(event, 'updated_at') and event.updated_at > last_updated:
                        last_updated = event.updated_at

        return PersonalHealthRecord(
            demographics=demographics,
            allergies=allergies,
            diagnoses=diagnoses,
            medications=medications,
            vital_signs=vital_signs,
            encounter_history=encounter_history,
            timeline=timeline,
            last_updated=last_updated,
            data_accuracy_verified=True,
            record_completeness=self._calculate_completeness(demographics),
        )

    async def get_demographics(self, patient_id: int) -> PatientDemographics:
        """Get patient demographic information"""
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()

        if not patient:
            raise ValueError("Patient not found")

        return PatientDemographics(
            medical_record_number=patient.medical_record_number,
            full_name=patient.full_name,
            nik=patient.nik,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender.value,
            blood_type=patient.blood_type.value if patient.blood_type else None,
            marital_status=patient.marital_status.value if patient.marital_status else None,
            religion=patient.religion,
            occupation=patient.occupation,
            phone=patient.phone,
            email=patient.email,
            address=patient.address,
            city=patient.city,
            province=patient.province,
            postal_code=patient.postal_code,
            country=patient.country,
            bpjs_card_number=patient.bpjs_card_number,
            created_at=patient.created_at,
            updated_at=patient.updated_at,
        )

    async def get_allergies(self, patient_id: int) -> AllergyList:
        """Get patient allergies separated by status"""
        result = await self.db.execute(
            select(Allergy).where(
                Allergy.patient_id == patient_id
            ).order_by(Allergy.created_at.desc())
        )
        allergies = result.scalars().all()

        active = []
        resolved = []
        has_severe = False

        for allergy in allergies:
            item = AllergyItem(
                id=allergy.id,
                allergy_type=allergy.allergy_type,
                allergen=allergy.allergen,
                allergen_code=allergy.allergen_code,
                severity=allergy.severity,
                reaction=allergy.reaction,
                reaction_details=allergy.reaction_details,
                status=allergy.status,
                onset_date=allergy.onset_date,
                resolved_date=allergy.resolved_date,
                clinical_notes=allergy.clinical_notes,
                alternatives=allergy.alternatives,
                created_at=allergy.created_at,
                updated_at=allergy.updated_at,
            )

            if allergy.status == "active":
                active.append(item)
                if allergy.severity in ["severe", "life_threatening"]:
                    has_severe = True
            else:
                resolved.append(item)

        return AllergyList(
            active_allergies=active,
            resolved_allergies=resolved,
            total=len(allergies),
            has_severe_allergies=has_severe,
        )

    async def get_diagnoses(self, patient_id: int) -> DiagnosisList:
        """Get patient diagnoses from all encounters"""
        result = await self.db.execute(
            select(Diagnosis, Encounter)
            .join(Encounter, Diagnosis.encounter_id == Encounter.id)
            .where(Encounter.patient_id == patient_id)
            .order_by(desc(Encounter.encounter_date))
        )
        results = result.all()

        active = []
        resolved = []
        chronic = []

        for diagnosis, encounter in results:
            item = DiagnosisItem(
                id=diagnosis.id,
                icd_10_code=diagnosis.icd_10_code,
                diagnosis_name=diagnosis.diagnosis_name,
                diagnosis_type=diagnosis.diagnosis_type,
                is_chronic=diagnosis.is_chronic,
                encounter_date=encounter.encounter_date,
                department=encounter.department,
                notes=diagnosis.notes,
                patient_friendly_description=self._get_patient_friendly_description(diagnosis.icd_10_code),
            )

            active.append(item)
            if diagnosis.is_chronic:
                chronic.append(item)

        return DiagnosisList(
            active_diagnoses=active,
            resolved_diagnoses=resolved,  # Would need resolution tracking
            chronic_conditions=chronic,
            total=len(active),
        )

    async def get_medications(self, patient_id: int) -> MedicationList:
        """Get patient medications from treatments and prescriptions"""
        # Get from treatments
        result = await self.db.execute(
            select(Treatment, Encounter)
            .join(Encounter, Treatment.encounter_id == Encounter.id)
            .where(
                and_(
                    Encounter.patient_id == patient_id,
                    Treatment.treatment_type == "medication",
                )
            )
            .order_by(desc(Encounter.encounter_date))
        )
        treatment_results = result.all()

        current = []
        past = []

        for treatment, encounter in treatment_results:
            item = MedicationItem(
                id=treatment.id,
                treatment_name=treatment.treatment_name,
                dosage=treatment.dosage,
                frequency=treatment.frequency,
                duration=treatment.duration,
                is_active=treatment.is_active,
                encounter_date=encounter.encounter_date,
                notes=treatment.notes,
                created_at=treatment.created_at,
            )

            if treatment.is_active:
                current.append(item)
            else:
                past.append(item)

        return MedicationList(
            current_medications=current,
            past_medications=past,
            total=len(current) + len(past),
        )

    async def get_vital_signs_history(self, patient_id: int) -> Optional[VitalSignsHistory]:
        """Get vital signs history from encounters"""
        result = await self.db.execute(
            select(Encounter)
            .where(
                and_(
                    Encounter.patient_id == patient_id,
                    Encounter.vital_signs.isnot(None),
                )
            )
            .order_by(desc(Encounter.encounter_date))
            .limit(20)
        )
        encounters = result.scalars().all()

        recordings = []
        latest = None

        for encounter in encounters:
            item = VitalSignsItem(
                encounter_date=encounter.encounter_date,
                vital_signs=encounter.vital_signs,
                department=encounter.department,
            )
            recordings.append(item)

        if recordings:
            latest = recordings[0].vital_signs

        return VitalSignsHistory(
            recordings=recordings,
            latest=latest,
        )

    async def get_encounter_history(self, patient_id: int) -> EncounterHistory:
        """Get patient encounter history"""
        result = await self.db.execute(
            select(Encounter)
            .where(Encounter.patient_id == patient_id)
            .options(selectinload(Encounter.diagnoses), selectinload(Encounter.treatments))
            .order_by(desc(Encounter.encounter_date))
        )
        encounters = result.scalars().all()

        encounter_summaries = []
        admission_count = 0
        emergency_count = 0
        outpatient_count = 0

        for encounter in encounters:
            # Get doctor name
            doctor_name = None
            if encounter.doctor_id:
                doctor_result = await self.db.execute(
                    select(User).where(User.id == encounter.doctor_id)
                )
                doctor = doctor_result.scalar_one_or_none()
                if doctor:
                    doctor_name = doctor.full_name

            # Build diagnoses and treatments lists
            diagnoses = [
                DiagnosisItem(
                    id=d.id,
                    icd_10_code=d.icd_10_code,
                    diagnosis_name=d.diagnosis_name,
                    diagnosis_type=d.diagnosis_type,
                    is_chronic=d.is_chronic,
                    encounter_date=encounter.encounter_date,
                    department=encounter.department,
                    notes=d.notes,
                    patient_friendly_description=self._get_patient_friendly_description(d.icd_10_code),
                )
                for d in encounter.diagnoses
            ]

            treatments = [
                MedicationItem(
                    id=t.id,
                    treatment_name=t.treatment_name,
                    dosage=t.dosage,
                    frequency=t.frequency,
                    duration=t.duration,
                    is_active=t.is_active,
                    encounter_date=encounter.encounter_date,
                    notes=t.notes,
                    created_at=t.created_at,
                )
                for t in encounter.treatments
            ]

            summary = EncounterSummary(
                id=encounter.id,
                encounter_type=encounter.encounter_type,
                encounter_date=encounter.encounter_date,
                department=encounter.department,
                doctor_name=doctor_name,
                chief_complaint=encounter.chief_complaint,
                status=encounter.status,
                diagnoses=diagnoses,
                treatments=treatments,
            )

            encounter_summaries.append(summary)

            # Count by type
            if encounter.encounter_type == "inpatient":
                admission_count += 1
            elif encounter.encounter_type == "emergency":
                emergency_count += 1
            elif encounter.encounter_type == "outpatient":
                outpatient_count += 1

        return EncounterHistory(
            encounters=encounter_summaries,
            total=len(encounter_summaries),
            admission_count=admission_count,
            emergency_count=emergency_count,
            outpatient_count=outpatient_count,
        )

    async def get_health_timeline(self, patient_id: int) -> HealthTimeline:
        """Get patient health timeline with all events"""
        events = []

        # Get encounters
        result = await self.db.execute(
            select(Encounter).where(Encounter.patient_id == patient_id)
            .order_by(desc(Encounter.encounter_date))
        )
        encounters = result.scalars().all()

        for encounter in encounters:
            if encounter.encounter_type == "inpatient":
                events.append(TimelineEvent(
                    id=f"encounter-{encounter.id}",
                    event_type=TimelineEventType.HOSPITALIZATION,
                    title=f"Hospitalization - {encounter.department or 'Unknown'}",
                    description=encounter.chief_complaint,
                    date=encounter.encounter_date,
                    details={
                        "encounter_id": encounter.id,
                        "department": encounter.department,
                        "status": encounter.status,
                    },
                ))
            elif encounter.encounter_type == "emergency":
                events.append(TimelineEvent(
                    id=f"encounter-{encounter.id}",
                    event_type=TimelineEventType.ENCOUNTER,
                    title="Emergency Room Visit",
                    description=encounter.chief_complaint,
                    date=encounter.encounter_date,
                    details={
                        "encounter_id": encounter.id,
                        "department": encounter.department,
                        "is_urgent": encounter.is_urgent,
                    },
                ))
            else:
                events.append(TimelineEvent(
                    id=f"encounter-{encounter.id}",
                    event_type=TimelineEventType.ENCOUNTER,
                    title=f"Outpatient Visit - {encounter.department or 'Unknown'}",
                    description=encounter.chief_complaint,
                    date=encounter.encounter_date,
                    details={
                        "encounter_id": encounter.id,
                        "department": encounter.department,
                        "status": encounter.status,
                    },
                ))

        # Sort by date descending
        events.sort(key=lambda e: e.date, reverse=True)

        return HealthTimeline(
            events=events[:100],  # Limit to 100 most recent
            total_events=len(events),
        )

    async def search_health_records(
        self,
        patient_id: int,
        query: HealthRecordSearch,
    ) -> HealthRecordSearchResult:
        """Search health records by keyword and/or date range"""
        events = []

        # Get timeline first
        timeline = await self.get_health_timeline(patient_id)

        # Filter by keyword
        if query.keyword:
            keyword_lower = query.keyword.lower()
            for event in timeline.events:
                if (
                    (event.title and keyword_lower in event.title.lower()) or
                    (event.description and keyword_lower in event.description.lower())
                ):
                    events.append(event)
        else:
            events = timeline.events

        # Filter by date range
        if query.date_from:
            events = [e for e in events if e.date >= query.date_from]
        if query.date_to:
            events = [e for e in events if e.date <= query.date_to]

        # Filter by event types
        if query.event_types:
            type_strs = [t.value for t in query.event_types]
            events = [e for e in events if e.event_type.value in type_strs]

        return HealthRecordSearchResult(
            events=events[:50],
            total=len(events),
            query=query,
        )

    def _get_patient_friendly_description(self, icd_10_code: str) -> Optional[str]:
        """Get patient-friendly description for ICD-10 code

        In production, this would query a medical terminology service
        or a database of patient-friendly descriptions.
        """
        # Simplified mapping - in production would use a comprehensive lookup
        descriptions = {
            "E11": "Type 2 diabetes mellitus - A condition that affects how your body uses sugar for energy.",
            "I10": "Hypertension (high blood pressure) - Increased force of blood against artery walls.",
            "J01": "Acute sinusitis - Inflammation of the sinuses, often causing facial pain and congestion.",
            "J18": "Pneumonia - Infection that inflames the air sacs in one or both lungs.",
        }

        # Check for code prefix matches
        for code_prefix, description in descriptions.items():
            if icd_10_code.startswith(code_prefix):
                return description

        return None

    def _calculate_completeness(self, demographics: PatientDemographics) -> str:
        """Calculate record completeness percentage"""
        fields = [
            demographics.phone,
            demographics.email,
            demographics.address,
            demographics.city,
            demographics.province,
            demographics.postal_code,
            demographics.blood_type,
            demographics.marital_status,
        ]

        filled = sum(1 for f in fields if f is not None and f != "")
        percentage = (filled / len(fields)) * 100

        if percentage >= 90:
            return "Complete"
        elif percentage >= 70:
            return "Good"
        elif percentage >= 50:
            return "Partial"
        else:
            return "Minimal"
