"""Patient Registration Service for STORY-006: New Patient Registration

This module provides services for:
- Patient registration with MRN generation
- Patient search and deduplication
- Patient data validation
- Medical record number management

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.models.patient import Patient, EmergencyContact, PatientInsurance
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.system_alerts import SystemAlert, AlertSeverity, AlertStatus


logger = logging.getLogger(__name__)


# MRN Configuration
MRN_PREFIX = "RM"
MRN_FORMAT = "{prefix}{year:04d}{sequence:06d}"
MRN_SEQUENCE_START = 1


class PatientValidationError(Exception):
    """Patient validation error"""
    pass


class DuplicatePatientError(Exception):
    """Duplicate patient detected"""
    def __init__(self, message: str, existing_patient: Dict = None):
        self.message = message
        self.existing_patient = existing_patient or {}
        super(DuplicatePatientError, self).__init__(message)


class PatientRegistrationService(object):
    """Service for patient registration and management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_patient(
        self,
        patient_data: Dict[str, any],
        emergency_contacts: List[Dict[str, any]] = None,
        insurance_policies: List[Dict[str, any]] = None,
        created_by: int = None,
        check_duplicates: bool = True,
    ) -> Patient:
        """Register a new patient with auto-generated MRN

        Args:
            patient_data: Patient demographic and medical information
            emergency_contacts: List of emergency contacts
            insurance_policies: List of insurance policies
            created_by: User ID registering the patient
            check_duplicates: Whether to check for duplicate patients

        Returns:
            Created Patient instance

        Raises:
            PatientValidationError: If validation fails
            DuplicatePatientError: If duplicate patient detected
        """
        # Validate patient data
        await self._validate_patient_data(patient_data)

        # Check for duplicates if requested
        if check_duplicates:
            duplicate = await self._check_duplicate_patient(patient_data)
            if duplicate:
                raise DuplicatePatientError(
                    "Patient with this NIK or similar details already exists",
                    existing_patient=duplicate
                )

        # Generate MRN
        mrn = await self._generate_medical_record_number()

        # Create patient record
        patient = Patient(
            medical_record_number=mrn,
            nik=patient_data.get("nik"),
            full_name=patient_data.get("full_name"),
            date_of_birth=patient_data.get("date_of_birth"),
            gender=patient_data.get("gender"),
            phone=patient_data.get("phone"),
            email=patient_data.get("email"),
            address=patient_data.get("address"),
            city=patient_data.get("city"),
            province=patient_data.get("province"),
            postal_code=patient_data.get("postal_code"),
            blood_type=patient_data.get("blood_type"),
            marital_status=patient_data.get("marital_status"),
            religion=patient_data.get("religion"),
            occupation=patient_data.get("occupation"),
            photo_url=patient_data.get("photo_url"),
            country=patient_data.get("country", "Indonesia"),
            bpjs_card_number=patient_data.get("bpjs_card_number"),
            satusehat_patient_id=patient_data.get("satusehat_patient_id"),
            is_active=True,
        )

        self.db.add(patient)
        await self.db.flush()

        # Add emergency contacts
        if emergency_contacts:
            for contact_data in emergency_contacts:
                contact = EmergencyContact(
                    patient_id=patient.id,
                    name=contact_data.get("name"),
                    relationship_type=contact_data.get("relationship_type"),
                    phone=contact_data.get("phone"),
                    address=contact_data.get("address"),
                )
                self.db.add(contact)

        # Add insurance policies
        if insurance_policies:
            for policy_data in insurance_policies:
                policy = PatientInsurance(
                    patient_id=patient.id,
                    insurance_type=policy_data.get("insurance_type"),
                    insurance_number=policy_data.get("insurance_number"),
                    provider_name=policy_data.get("provider_name"),
                    policy_number=policy_data.get("policy_number"),
                    expiry_date=policy_data.get("expiry_date"),
                )
                self.db.add(policy)

        # Create audit log
        await self._create_registration_audit_log(patient, created_by)

        logger.info("Patient registered: {} - {}".format(mrn, patient.full_name))

        return patient

    async def search_patients(
        self,
        search_term: Optional[str] = None,
        nik: Optional[str] = None,
        mrn: Optional[str] = None,
        phone: Optional[str] = None,
        name: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        limit: int = 20,
    ) -> List[Dict[str, any]]:
        """Search for patients by various criteria

        Args:
            search_term: General search term (searches name, MRN, phone)
            nik: NIK to search
            mrn: Medical record number to search
            phone: Phone number to search
            name: Patient name to search (partial match)
            date_of_birth: Date of birth filter
            limit: Maximum results to return

        Returns:
            List of patient dictionaries
        """
        query = select(Patient).where(Patient.is_active == True)

        # Build search conditions
        conditions = []

        if search_term:
            # Search multiple fields
            search_pattern = "%{}%".format(search_term)
            conditions.append(
                or_(
                    Patient.full_name.ilike(search_pattern),
                    Patient.medical_record_number.ilike(search_pattern),
                    Patient.phone.ilike(search_pattern),
                    Patient.nik.ilike(search_pattern),
                )
            )
        else:
            # Specific field searches
            if nik:
                conditions.append(Patient.nik == nik)
            if mrn:
                conditions.append(Patient.medical_record_number == mrn)
            if phone:
                conditions.append(Patient.phone.ilike("%{}%".format(phone)))
            if name:
                conditions.append(Patient.full_name.ilike("%{}%".format(name)))
            if date_of_birth:
                conditions.append(Patient.date_of_birth == date_of_birth)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(Patient.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        patients = result.scalars().all()

        return [
            {
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
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in patients
        ]

    async def get_patient_by_mrn(self, mrn: str) -> Optional[Patient]:
        """Get patient by medical record number

        Args:
            mrn: Medical record number

        Returns:
            Patient instance or None
        """
        query = select(Patient).where(
            and_(
                Patient.medical_record_number == mrn,
                Patient.is_active == True
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_patient_by_nik(self, nik: str) -> Optional[Patient]:
        """Get patient by NIK

        Args:
            nik: Indonesian National ID number

        Returns:
            Patient instance or None
        """
        query = select(Patient).where(
            and_(
                Patient.nik == nik,
                Patient.is_active == True
            )
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_patient(
        self,
        mrn: str,
        patient_data: Dict[str, any],
        updated_by: int = None,
    ) -> Patient:
        """Update patient information

        Args:
            mrn: Medical record number
            patient_data: Updated patient data
            updated_by: User ID making the update

        Returns:
            Updated Patient instance

        Raises:
            ValueError: If patient not found
        """
        patient = await self.get_patient_by_mrn(mrn)

        if not patient:
            raise ValueError("Patient not found: {}".format(mrn))

        # Update allowed fields
        updatable_fields = [
            "full_name", "phone", "email", "address", "city", "province",
            "postal_code", "blood_type", "marital_status", "religion",
            "occupation", "photo_url", "bpjs_card_number", "satusehat_patient_id",
        ]

        for field in updatable_fields:
            if field in patient_data:
                setattr(patient, field, patient_data[field])

        patient.updated_at = datetime.utcnow()

        await self.db.flush()

        # Create audit log
        await self._create_update_audit_log(patient, updated_by)

        logger.info("Patient updated: {} - {}".format(mrn, patient.full_name))

        return patient

    async def deactivate_patient(
        self,
        mrn: str,
        reason: str = None,
        deactivated_by: int = None,
    ) -> bool:
        """Deactivate a patient record

        Args:
            mrn: Medical record number
            reason: Reason for deactivation
            deactivated_by: User ID deactivating the record

        Returns:
            True if successful

        Raises:
            ValueError: If patient not found
        """
        patient = await self.get_patient_by_mrn(mrn)

        if not patient:
            raise ValueError("Patient not found: {}".format(mrn))

        patient.is_active = False
        patient.updated_at = datetime.utcnow()

        await self.db.flush()

        # Create audit log
        await self._create_deactivation_audit_log(patient, reason, deactivated_by)

        logger.info("Patient deactivated: {} - {}".format(mrn, patient.full_name))

        return True

    async def get_patient_statistics(self) -> Dict[str, any]:
        """Get patient registration statistics

        Returns:
            Dict with statistics
        """
        # Total patients
        total_query = select(func.count()).where(Patient.is_active == True)
        total_result = await self.db.execute(total_query)
        total_patients = total_result.scalar() or 0

        # New registrations this month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        new_query = select(func.count()).where(
            and_(
                Patient.is_active == True,
                Patient.created_at >= month_start
            )
        )
        new_result = await self.db.execute(new_query)
        new_this_month = new_result.scalar() or 0

        # By gender
        gender_query = select(
            Patient.gender,
            func.count().label("count")
        ).where(Patient.is_active == True).group_by(Patient.gender)

        gender_result = await self.db.execute(gender_query)
        by_gender = {row.gender.value: row.count for row in gender_result}

        # By age group
        today = date.today()
        age_groups = {
            "0-18": 0,
            "19-35": 0,
            "36-50": 0,
            "51-65": 0,
            "65+": 0,
        }

        patients_query = select(Patient).where(Patient.is_active == True)
        patients_result = await self.db.execute(patients_query)
        all_patients = patients_result.scalars().all()

        for p in all_patients:
            if p.date_of_birth:
                age = (today - p.date_of_birth).days // 365
                if age <= 18:
                    age_groups["0-18"] += 1
                elif age <= 35:
                    age_groups["19-35"] += 1
                elif age <= 50:
                    age_groups["36-50"] += 1
                elif age <= 65:
                    age_groups["51-65"] += 1
                else:
                    age_groups["65+"] += 1

        return {
            "total_patients": total_patients,
            "new_this_month": new_this_month,
            "by_gender": by_gender,
            "by_age_group": age_groups,
        }

    # ==========================================================================
    # Private Helper Methods
    # ==========================================================================

    async def _validate_patient_data(self, patient_data: Dict[str, any]):
        """Validate patient data

        Args:
            patient_data: Patient data to validate

        Raises:
            PatientValidationError: If validation fails
        """
        errors = []

        # Required fields
        required_fields = ["full_name", "date_of_birth", "gender"]
        for field in required_fields:
            if not patient_data.get(field):
                errors.append("{} is required".format(field))

        # Validate NIK format if provided
        nik = patient_data.get("nik")
        if nik and not nik.isdigit():
            errors.append("NIK must be numeric")
        if nik and len(nik) != 16:
            errors.append("NIK must be 16 digits")

        # Validate date of birth
        dob = patient_data.get("date_of_birth")
        if dob:
            if isinstance(dob, str):
                try:
                    from datetime import datetime
                    dob = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    errors.append("Invalid date of birth format. Use YYYY-MM-DD")

            if dob and dob > date.today():
                errors.append("Date of birth cannot be in the future")

        if errors:
            raise PatientValidationError("; ".join(errors))

    async def _check_duplicate_patient(
        self,
        patient_data: Dict[str, any],
    ) -> Optional[Dict[str, any]]:
        """Check for duplicate patient

        Args:
            patient_data: Patient data to check

        Returns:
            Duplicate patient info if found, None otherwise
        """
        # Check by NIK
        nik = patient_data.get("nik")
        if nik:
            existing = await self.get_patient_by_nik(nik)
            if existing:
                return {
                    "mrn": existing.medical_record_number,
                    "full_name": existing.full_name,
                    "nik": existing.nik,
                    "match_type": "nik",
                }

        # Check by name + date of birth
        full_name = patient_data.get("full_name")
        dob = patient_data.get("date_of_birth")

        if full_name and dob:
            query = select(Patient).where(
                and_(
                    Patient.full_name.ilike(full_name),
                    Patient.date_of_birth == dob,
                    Patient.is_active == True
                )
            )

            result = await self.db.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                return {
                    "mrn": existing.medical_record_number,
                    "full_name": existing.full_name,
                    "nik": existing.nik,
                    "match_type": "name_dob",
                }

        return None

    async def _generate_medical_record_number(self) -> str:
        """Generate a new medical record number

        Returns:
            Generated MRN
        """
        year = datetime.utcnow().year

        # Get next sequence number
        sequence = await self._get_next_mrn_sequence(year)

        mrn = MRN_FORMAT.format(
            prefix=MRN_PREFIX,
            year=year,
            sequence=sequence,
        )

        return mrn

    async def _get_next_mrn_sequence(self, year: int) -> int:
        """Get next MRN sequence number for the year

        Args:
            year: Year to get sequence for

        Returns:
            Next sequence number
        """
        # Find the last MRN for this year
        pattern = "{}{}%".format(MRN_PREFIX, year)
        query = select(Patient).where(
            Patient.medical_record_number.like(pattern)
        ).order_by(Patient.medical_record_number.desc())

        result = await self.db.execute(query)
        last_patient = result.scalar_one_or_none()

        if last_patient:
            # Extract sequence from last MRN
            last_mrn = last_patient.medical_record_number
            # Format: RM + YYYY (4) + sequence (6) = 12 characters total
            sequence_str = last_mrn[-6:]
            try:
                last_sequence = int(sequence_str)
                return last_sequence + 1
            except ValueError:
                pass

        return MRN_SEQUENCE_START

    async def _create_registration_audit_log(
        self,
        patient: Patient,
        created_by: int,
    ):
        """Create audit log for patient registration

        Args:
            patient: Patient that was registered
            created_by: User ID who registered the patient
        """
        # Get user info
        if created_by:
            query = select(User).where(User.id == created_by)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            username = user.username if user else "system"
        else:
            username = "system"

        audit_log = AuditLog(
            user_id=created_by,
            username=username,
            action="CREATE",
            resource_type="Patient",
            resource_id=patient.medical_record_number,
            request_path="/patients/",
            request_method="POST",
            success=True,
            additional_data={
                "patient_name": patient.full_name,
                "mrn": patient.medical_record_number,
                "nik": patient.nik,
            },
        )

        self.db.add(audit_log)
        await self.db.flush()

    async def _create_update_audit_log(
        self,
        patient: Patient,
        updated_by: int,
    ):
        """Create audit log for patient update

        Args:
            patient: Patient that was updated
            updated_by: User ID who updated the patient
        """
        # Get user info
        if updated_by:
            query = select(User).where(User.id == updated_by)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            username = user.username if user else "system"
        else:
            username = "system"

        audit_log = AuditLog(
            user_id=updated_by,
            username=username,
            action="UPDATE",
            resource_type="Patient",
            resource_id=patient.medical_record_number,
            request_path="/patients/{}".format(patient.medical_record_number),
            request_method="PUT",
            success=True,
            additional_data={
                "patient_name": patient.full_name,
                "mrn": patient.medical_record_number,
            },
        )

        self.db.add(audit_log)
        await self.db.flush()

    async def _create_deactivation_audit_log(
        self,
        patient: Patient,
        reason: str,
        deactivated_by: int,
    ):
        """Create audit log for patient deactivation

        Args:
            patient: Patient that was deactivated
            reason: Reason for deactivation
            deactivated_by: User ID who deactivated the patient
        """
        # Get user info
        if deactivated_by:
            query = select(User).where(User.id == deactivated_by)
            result = await self.db.execute(query)
            user = result.scalar_one_or_none()
            username = user.username if user else "system"
        else:
            username = "system"

        audit_log = AuditLog(
            user_id=deactivated_by,
            username=username,
            action="DELETE",
            resource_type="Patient",
            resource_id=patient.medical_record_number,
            request_path="/patients/{}".format(patient.medical_record_number),
            request_method="DELETE",
            success=True,
            failure_reason="Deactivated: {}".format(reason),
            additional_data={
                "patient_name": patient.full_name,
                "mrn": patient.medical_record_number,
                "reason": reason,
            },
        )

        self.db.add(audit_log)
        await self.db.flush()


# Factory function
def get_patient_registration_service(db: AsyncSession) -> PatientRegistrationService:
    """Get patient registration service"""
    return PatientRegistrationService(db)
