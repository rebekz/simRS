"""Patient Record Linking Service

Service for linking portal accounts to existing patient records.
"""
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime, date

from app.models.patient import Patient
from app.models.patient_portal import PatientPortalUser
from app.core.security import verify_password


class PatientLinkingService:
    """Service for linking portal accounts to patient records"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_patient_by_nik(
        self,
        nik: str,
        date_of_birth: Optional[date] = None,
    ) -> Optional[Patient]:
        """Find patient by NIK with optional DOB verification"""
        query = select(Patient).where(Patient.nik == nik)

        if date_of_birth:
            query = query.where(Patient.date_of_birth == date_of_birth)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_patient_by_mrn(
        self,
        mrn: str,
        date_of_birth: Optional[date] = None,
    ) -> Optional[Patient]:
        """Find patient by medical record number with optional DOB verification"""
        query = select(Patient).where(Patient.medical_record_number == mrn)

        if date_of_birth:
            query = query.where(Patient.date_of_birth == date_of_birth)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def find_patient_by_bpjs(
        self,
        bpjs_card_number: str,
        date_of_birth: date,
    ) -> Optional[Patient]:
        """Find patient by BPJS card number (requires DOB for verification)"""
        result = await self.db.execute(
            select(Patient).where(
                and_(
                    Patient.bpjs_card_number == bpjs_card_number,
                    Patient.date_of_birth == date_of_birth,
                )
            )
        )
        return result.scalar_one_or_none()

    async def search_patients(
        self,
        search_type: str,
        nik: Optional[str] = None,
        bpjs_card_number: Optional[str] = None,
        include_inactive: bool = False,
    ) -> Tuple[bool, list[Patient], str]:
        """Search for existing patients

        Returns:
            Tuple of (found, patients_list, message)
        """
        patients = []

        if search_type == "nik" and nik:
            result = await self.db.execute(
                select(Patient).where(Patient.nik == nik)
            )
            patient = result.scalar_one_or_none()
            if patient:
                patients = [patient]

        elif search_type == "bpjs" and bpjs_card_number:
            result = await self.db.execute(
                select(Patient).where(Patient.bpjs_card_number == bpjs_card_number)
            )
            patient = result.scalar_one_or_none()
            if patient:
                patients = [patient]

        if not patients:
            return False, [], "No patient found with the provided information"

        # Filter inactive if needed
        if not include_inactive:
            active_patients = [p for p in patients if p.is_active]
            if not active_patients:
                return True, [], "Patient found but account is inactive"
            patients = active_patients

        return True, patients, f"Found {len(patients)} patient(s)"

    async def link_portal_user_to_patient(
        self,
        portal_user_id: int,
        patient_id: int,
    ) -> Tuple[bool, str]:
        """Link portal user to patient record

        Returns:
            Tuple of (success, message)
        """
        # Get portal user
        result = await self.db.execute(
            select(PatientPortalUser).where(PatientPortalUser.id == portal_user_id)
        )
        portal_user = result.scalar_one_or_none()

        if not portal_user:
            return False, "Portal user not found"

        # Check if already linked
        if portal_user.patient_id and portal_user.patient_id != patient_id:
            return False, "Portal user is already linked to a different patient record"

        # Get patient
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()

        if not patient:
            return False, "Patient not found"

        # Link
        portal_user.patient_id = patient_id
        await self.db.commit()

        return True, f"Successfully linked to patient record {patient.medical_record_number}"

    async def verify_patient_link_eligibility(
        self,
        portal_user_id: int,
        patient_id: int,
    ) -> Tuple[bool, str]:
        """Verify if a patient can be linked to a portal user

        Checks for existing links and data consistency.
        """
        # Get portal user
        result = await self.db.execute(
            select(PatientPortalUser).where(PatientPortalUser.id == portal_user_id)
        )
        portal_user = result.scalar_one_or_none()

        if not portal_user:
            return False, "Portal user not found"

        # Get patient
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()

        if not patient:
            return False, "Patient not found"

        # Check if patient already has a portal account
        result = await self.db.execute(
            select(PatientPortalUser).where(
                and_(
                    PatientPortalUser.patient_id == patient_id,
                    PatientPortalUser.id != portal_user_id,
                    PatientPortalUser.is_active == True,
                )
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return False, f"Patient already has an active portal account (email: {existing.email})"

        return True, "Patient is eligible for linking"

    async def create_new_patient_and_link(
        self,
        portal_user_id: int,
        patient_data: dict,
    ) -> Tuple[bool, str, Optional[Patient]]:
        """Create a new patient record and link to portal user

        Args:
            portal_user_id: ID of the portal user
            patient_data: Dictionary of patient data

        Returns:
            Tuple of (success, message, patient)
        """
        from app.models.patient import (
            Patient,
            Gender,
            MaritalStatus,
            BloodType,
            InsuranceType,
        )

        # Get portal user
        result = await self.db.execute(
            select(PatientPortalUser).where(PatientPortalUser.id == portal_user_id)
        )
        portal_user = result.scalar_one_or_none()

        if not portal_user:
            return False, "Portal user not found", None

        # Check if already linked
        if portal_user.patient_id:
            return False, "Portal user is already linked to a patient record", None

        # Check for duplicate NIK
        if patient_data.get("nik"):
            result = await self.db.execute(
                select(Patient).where(Patient.nik == patient_data["nik"])
            )
            existing = result.scalar_one_or_none()
            if existing:
                return False, f"Patient with NIK {patient_data['nik']} already exists (MRN: {existing.medical_record_number})", None

        # Generate MRN
        from app.services.patient import generate_medical_record_number
        mrn = await generate_medical_record_number(self.db)

        # Create patient
        patient = Patient(
            medical_record_number=mrn,
            nik=patient_data.get("nik"),
            full_name=patient_data.get("full_name"),
            date_of_birth=patient_data.get("date_of_birth"),
            gender=Gender(patient_data.get("gender", "male")),
            phone=patient_data.get("phone") or portal_user.phone,
            email=patient_data.get("email") or portal_user.email,
            address=patient_data.get("address"),
            city=patient_data.get("city"),
            province=patient_data.get("province"),
            postal_code=patient_data.get("postal_code"),
            country=patient_data.get("country", "Indonesia"),
            blood_type=BloodType(patient_data.get("blood_type", "none")) if patient_data.get("blood_type") else None,
            marital_status=MaritalStatus(patient_data["marital_status"]) if patient_data.get("marital_status") else None,
            religion=patient_data.get("religion"),
            occupation=patient_data.get("occupation"),
            bpjs_card_number=patient_data.get("bpjs_card_number"),
            is_active=True,
        )

        self.db.add(patient)
        await self.flush()

        # Link to portal user
        portal_user.patient_id = patient.id
        await self.db.commit()

        return True, f"New patient record created with MRN {mrn}", patient

    async def unlink_patient_from_portal(
        self,
        portal_user_id: int,
    ) -> Tuple[bool, str]:
        """Unlink patient from portal user (admin operation)

        Returns:
            Tuple of (success, message)
        """
        result = await self.db.execute(
            select(PatientPortalUser).where(PatientPortalUser.id == portal_user_id)
        )
        portal_user = result.scalar_one_or_none()

        if not portal_user:
            return False, "Portal user not found"

        if not portal_user.patient_id:
            return False, "Portal user is not linked to any patient"

        patient_id = portal_user.patient_id
        portal_user.patient_id = None
        await self.db.commit()

        return True, f"Unlinked from patient ID {patient_id}"
