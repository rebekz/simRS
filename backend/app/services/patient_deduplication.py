"""Patient Deduplication Service for STORY-006: New Patient Registration

This module provides services for:
- Patient duplicate detection
- Patient record merging
- Master patient record management

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.patient import Patient
from app.models.audit_log import AuditLog
from app.models.user import User


logger = logging.getLogger(__name__)


class PatientDeduplicationService(object):
    """Service for detecting and handling duplicate patient records"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_potential_duplicates(
        self,
        patient_data: Dict[str, any],
        threshold: float = 0.7,
    ) -> List[Dict[str, any]]:
        """Find potential duplicate patient records

        Args:
            patient_data: Patient data to check for duplicates
            threshold: Similarity threshold (0-1)

        Returns:
            List of potential duplicates with similarity scores
        """
        duplicates = []

        # Check by NIK (exact match)
        nik = patient_data.get("nik")
        if nik:
            query = select(Patient).where(
                and_(
                    Patient.nik == nik,
                    Patient.is_active == True
                )
            )
            result = await self.db.execute(query)
            patient = result.scalar_one_or_none()

            if patient:
                duplicates.append({
                    "patient_id": patient.id,
                    "mrn": patient.medical_record_number,
                    "full_name": patient.full_name,
                    "nik": patient.nik,
                    "similarity_score": 1.0,
                    "match_type": "nik_exact",
                })

        # Check by name + date of birth
        full_name = patient_data.get("full_name")
        dob = patient_data.get("date_of_birth")

        if full_name and dob:
            # Exact match
            query = select(Patient).where(
                and_(
                    Patient.full_name.ilike(full_name),
                    Patient.date_of_birth == dob,
                    Patient.is_active == True
                )
            )
            result = await self.db.execute(query)
            patients = result.scalars().all()

            for p in patients:
                if not any(d.get("patient_id") == p.id for d in duplicates):
                    duplicates.append({
                        "patient_id": p.id,
                        "mrn": p.medical_record_number,
                        "full_name": p.full_name,
                        "nik": p.nik,
                        "similarity_score": 1.0,
                        "match_type": "name_dob_exact",
                    })

            # Partial name match + same DOB
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                # Try matching first 2 name parts
                first_two = " ".join(name_parts[:2])
                query = select(Patient).where(
                    and_(
                        Patient.full_name.ilike("%{}%".format(first_two)),
                        Patient.date_of_birth == dob,
                        Patient.is_active == True
                    )
                )
                result = await self.db.execute(query)
                patients = result.scalars().all()

                for p in patients:
                    if not any(d.get("patient_id") == p.id for d in duplicates):
                        # Calculate similarity score
                        similarity = self._calculate_name_similarity(
                            full_name,
                            p.full_name
                        )

                        if similarity >= threshold:
                            duplicates.append({
                                "patient_id": p.id,
                                "mrn": p.medical_record_number,
                                "full_name": p.full_name,
                                "nik": p.nik,
                                "similarity_score": similarity,
                                "match_type": "name_dob_fuzzy",
                            })

        # Check by phone number
        phone = patient_data.get("phone")
        if phone and len(phone) >= 10:
            # Remove non-numeric characters
            clean_phone = "".join(c for c in phone if c.isdigit())

            query = select(Patient).where(
                and_(
                    Patient.phone.ilike("%{}%".format(clean_phone)),
                    Patient.is_active == True
                )
            )
            result = await self.db.execute(query)
            patients = result.scalars().all()

            for p in patients:
                if not any(d.get("patient_id") == p.id for d in duplicates):
                    duplicates.append({
                        "patient_id": p.id,
                        "mrn": p.medical_record_number,
                        "full_name": p.full_name,
                        "nik": p.nik,
                        "phone": p.phone,
                        "similarity_score": 0.6,  # Phone match is weaker
                        "match_type": "phone",
                    })

        return duplicates

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names using Jaro-Winkler distance

        Args:
            name1: First name
            name2: Second name

        Returns:
            Similarity score (0-1)
        """
        # Simple implementation - can be enhanced with proper Jaro-Winkler
        name1_lower = name1.lower().strip()
        name2_lower = name2.lower().strip()

        if name1_lower == name2_lower:
            return 1.0

        # Check if one name contains the other
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return 0.8

        # Calculate word overlap
        words1 = set(name1_lower.split())
        words2 = set(name2_lower.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    async def merge_patient_records(
        self,
        primary_mrn: str,
        duplicate_mrns: List[str],
        merge_reason: str,
        merged_by: int,
    ) -> Dict[str, any]:
        """Merge duplicate patient records into primary record

        Args:
            primary_mrn: Medical record number of primary record
            duplicate_mrns: List of duplicate MRNs to merge
            merge_reason: Reason for merge
            merged_by: User ID performing the merge

        Returns:
            Merge result with statistics

        Raises:
            ValueError: If primary or duplicate records not found
        """
        # Get primary patient
        query = select(Patient).where(Patient.medical_record_number == primary_mrn)
        result = await self.db.execute(query)
        primary_patient = result.scalar_one_or_none()

        if not primary_patient:
            raise ValueError("Primary patient not found: {}".format(primary_mrn))

        merged_count = 0
        failed_count = 0
        errors = []

        for dup_mrn in duplicate_mrns:
            try:
                # Get duplicate patient
                dup_query = select(Patient).where(Patient.medical_record_number == dup_mrn)
                dup_result = await self.db.execute(dup_query)
                duplicate_patient = dup_result.scalar_one_or_none()

                if not duplicate_patient:
                    errors.append("Duplicate not found: {}".format(dup_mrn))
                    failed_count += 1
                    continue

                # Transfer any relationships (encounters, etc.)
                await self._transfer_patient_relationships(
                    primary_patient.id,
                    duplicate_patient.id
                )

                # Deactivate duplicate
                duplicate_patient.is_active = False
                duplicate_patient.updated_at = datetime.utcnow()

                # Store reference to primary record
                if not duplicate_patient.additional_data:
                    from sqlalchemy import JSON
                    duplicate_patient.additional_data = {}

                duplicate_patient.additional_data["merged_into"] = primary_mrn
                duplicate_patient.additional_data["merge_reason"] = merge_reason
                duplicate_patient.additional_data["merge_date"] = datetime.utcnow().isoformat()

                merged_count += 1

                # Create audit log
                await self._create_merge_audit_log(
                    primary_patient,
                    duplicate_patient,
                    merge_reason,
                    merged_by
                )

            except Exception as e:
                logger.error("Error merging {}: {}".format(dup_mrn, e))
                errors.append("{}: {}".format(dup_mrn, str(e)))
                failed_count += 1

        logger.info(
            "Patient merge completed: {} (primary), {} merged, {} failed".format(
                primary_mrn, merged_count, failed_count
            )
        )

        return {
            "primary_mrn": primary_mrn,
            "merged_count": merged_count,
            "failed_count": failed_count,
            "errors": errors,
        }

    async def _transfer_patient_relationships(
        self,
        primary_patient_id: int,
        duplicate_patient_id: int,
    ):
        """Transfer relationships from duplicate to primary patient

        Args:
            primary_patient_id: Primary patient ID
            duplicate_patient_id: Duplicate patient ID
        """
        # Update encounters
        from app.models.encounter import Encounter

        encounter_query = select(Encounter).where(
            Encounter.patient_id == duplicate_patient_id
        )
        encounter_result = await self.db.execute(encounter_query)
        encounters = encounter_result.scalars().all()

        for encounter in encounters:
            encounter.patient_id = primary_patient_id

        # Update other relationships as needed
        # (clinical notes, prescriptions, etc.)

    async def _create_merge_audit_log(
        self,
        primary_patient: Patient,
        duplicate_patient: Patient,
        reason: str,
        merged_by: int,
    ):
        """Create audit log for patient merge

        Args:
            primary_patient: Primary patient record
            duplicate_patient: Duplicate patient record
            reason: Reason for merge
            merged_by: User ID performing merge
        """
        # Get user info
        query = select(User).where(User.id == merged_by)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        username = user.username if user else "system"

        audit_log = AuditLog(
            user_id=merged_by,
            username=username,
            action="MERGE",
            resource_type="Patient",
            resource_id=primary_patient.medical_record_number,
            request_path="/patients/{}/merge".format(primary_patient.medical_record_number),
            request_method="POST",
            success=True,
            additional_data={
                "primary_patient": primary_patient.full_name,
                "primary_mrn": primary_patient.medical_record_number,
                "duplicate_patient": duplicate_patient.full_name,
                "duplicate_mrn": duplicate_patient.medical_record_number,
                "reason": reason,
            },
        )

        self.db.add(audit_log)
        await self.db.flush()


class PatientMergeRequestService(object):
    """Service for managing patient merge requests"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_merge_request(
        self,
        primary_mrn: str,
        duplicate_mrns: List[str],
        reason: str,
        requested_by: int,
    ) -> Dict[str, any]:
        """Create a patient merge request

        Args:
            primary_mrn: Primary patient MRN
            duplicate_mrns: List of duplicate MRNs to merge
            reason: Reason for merge
            requested_by: User ID requesting merge

        Returns:
            Merge request details
        """
        # Validate patients exist
        for mrn in [primary_mrn] + duplicate_mrns:
            query = select(Patient).where(Patient.medical_record_number == mrn)
            result = await self.db.execute(query)
            patient = result.scalar_one_or_none()

            if not patient:
                raise ValueError("Patient not found: {}".format(mrn))

        # In production, this would create a merge request record
        # that requires approval before executing the merge

        return {
            "primary_mrn": primary_mrn,
            "duplicate_mrns": duplicate_mrns,
            "reason": reason,
            "status": "pending_approval",
            "created_at": datetime.utcnow().isoformat(),
        }


# Factory functions
def get_deduplication_service(db: AsyncSession) -> PatientDeduplicationService:
    """Get patient deduplication service"""
    return PatientDeduplicationService(db)


def get_merge_request_service(db: AsyncSession) -> PatientMergeRequestService:
    """Get patient merge request service"""
    return PatientMergeRequestService(db)
