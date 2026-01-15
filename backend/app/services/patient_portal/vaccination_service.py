"""Vaccination Service

Service for managing vaccination records and immunization history through patient portal.
Handles vaccination summaries, details, status tracking, and certificate generation.
STORY-050: Vaccination Records & Immunization History
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
import secrets
import uuid

from app.models.patient import Patient
from app.schemas.patient_portal.vaccinations import (
    VaccinationRecord,
    VaccinationStatus,
    VaccinationSummary,
    VaccinationListResponse,
    VaccinationDetailResponse,
    VaccinationCertificate,
)


class VaccinationService:
    """Service for handling vaccination records and certificates"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_vaccination_summary(
        self, patient_id: int
    ) -> VaccinationSummary:
        """Get complete vaccination summary for patient

        Returns summary with status, recent, upcoming, and overdue vaccinations.
        """
        # Get all vaccinations for this patient
        vaccinations = await self._get_all_vaccinations(patient_id)

        # Categorize vaccinations
        recent_vaccinations = []
        upcoming_vaccinations = []
        overdue_vaccinations = []

        today = date.today()
        one_year_ago = today - timedelta(days=365)

        complete_regimens = 0
        incomplete_regimens = 0

        for v in vaccinations:
            # Check if regimen is complete
            if v.dose_number >= v.total_doses:
                complete_regimens += 1
                # Add to recent if administered within last year
                if v.date_administered and v.date_administered >= one_year_ago:
                    recent_vaccinations.append(v)
            else:
                incomplete_regimens += 1

                # Check if scheduled, upcoming, or overdue
                if v.next_due_date:
                    if v.next_due_date < today:
                        overdue_vaccinations.append(v)
                    elif v.next_due_date <= today + timedelta(days=30):
                        upcoming_vaccinations.append(v)
                elif v.status == "scheduled":
                    upcoming_vaccinations.append(v)

        # Create vaccination status
        vaccination_status = VaccinationStatus(
            total_vaccinations=len(vaccinations),
            complete_regimens=complete_regimens,
            incomplete_regimens=incomplete_regimens,
            overdue_vaccinations=len(overdue_vaccinations),
            upcoming_vaccinations=len(upcoming_vaccinations),
        )

        return VaccinationSummary(
            patient_id=patient_id,
            vaccination_status=vaccination_status,
            recent_vaccinations=recent_vaccinations[:10],  # Limit to 10 most recent
            upcoming_vaccinations=upcoming_vaccinations[:10],
            overdue_vaccinations=overdue_vaccinations[:10],
        )

    async def list_vaccinations(
        self,
        patient_id: int,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> VaccinationListResponse:
        """List vaccinations with optional filtering

        Returns paginated list of vaccinations.
        """
        # Build query
        query = select(VaccinationRecord).where(
            VaccinationRecord.patient_id == patient_id
        )

        # Apply status filter if provided
        if status:
            query = query.where(VaccinationRecord.status == status)

        # Order by administration date (most recent first)
        query = query.order_by(desc(VaccinationRecord.date_administered))

        # Execute query with pagination
        result = await self.db.execute(query)
        all_vaccinations = result.scalars().all()

        # Apply pagination
        total = len(all_vaccinations)
        vaccinations = all_vaccinations[offset:offset + limit]

        return VaccinationListResponse(
            total=total,
            vaccinations=vaccinations,
        )

    async def get_vaccination_detail(
        self,
        patient_id: int,
        vaccination_id: int,
    ) -> VaccinationDetailResponse:
        """Get detailed information about specific vaccination

        Returns detail with certificate availability.
        """
        # Get vaccination record
        vaccination = await self._get_vaccination_by_id(vaccination_id)

        if not vaccination or vaccination.patient_id != patient_id:
            raise ValueError("Vaccination record not found")

        # Check if certificate can be generated
        can_download = vaccination.status == "administered" and vaccination.dose_number >= vaccination.total_doses

        # Generate certificate URL if available
        certificate_url = None
        if can_download:
            certificate_url = f"/api/v1/portal/vaccinations/{vaccination_id}/certificate"

        return VaccinationDetailResponse(
            vaccination=vaccination,
            certificate_url=certificate_url,
            can_download_certificate=can_download,
        )

    async def get_vaccination_status(
        self,
        patient_id: int,
    ) -> VaccinationStatus:
        """Get vaccination status statistics

        Returns counts and status information.
        """
        vaccinations = await self._get_all_vaccinations(patient_id)

        complete_regimens = 0
        incomplete_regimens = 0
        overdue_count = 0
        upcoming_count = 0

        today = date.today()

        for v in vaccinations:
            if v.dose_number >= v.total_doses:
                complete_regimens += 1
            else:
                incomplete_regimens += 1

            if v.next_due_date:
                if v.next_due_date < today:
                    overdue_count += 1
                elif v.next_due_date <= today + timedelta(days=30):
                    upcoming_count += 1

        return VaccinationStatus(
            total_vaccinations=len(vaccinations),
            complete_regimens=complete_regimens,
            incomplete_regimens=incomplete_regimens,
            overdue_vaccinations=overdue_count,
            upcoming_vaccinations=upcoming_count,
        )

    async def generate_vaccination_certificate(
        self,
        patient_id: int,
        vaccination_id: int,
    ) -> VaccinationCertificate:
        """Generate vaccination certificate

        Returns certificate URLs for download.
        """
        # Get vaccination record
        vaccination = await self._get_vaccination_by_id(vaccination_id)

        if not vaccination or vaccination.patient_id != patient_id:
            raise ValueError("Vaccination record not found")

        # Verify vaccination is complete
        if vaccination.status != "administered" or vaccination.dose_number < vaccination.total_doses:
            raise ValueError("Cannot generate certificate for incomplete vaccination")

        # Get patient information
        patient = await self._get_patient(patient_id)
        if not patient:
            raise ValueError("Patient not found")

        # Generate certificate (mock implementation)
        certificate_id = str(uuid.uuid4())
        issued_at = datetime.utcnow()

        # Generate URLs
        base_url = "/api/v1/portal/vaccinations/certificates"
        certificate_url = f"{base_url}/{certificate_id}.pdf"
        qr_code_url = f"{base_url}/{certificate_id}/qrcode.png"
        verification_url = f"{base_url}/{certificate_id}/verify"

        return VaccinationCertificate(
            certificate_url=certificate_url,
            qr_code_url=qr_code_url,
            issued_at=issued_at,
            expires_at=None,  # Certificates typically don't expire
        )

    # Private helper methods

    async def _get_all_vaccinations(
        self, patient_id: int
    ) -> List[VaccinationRecord]:
        """Get all vaccination records for a patient"""
        # Mock implementation - in production, query database
        # For now, return empty list as placeholder
        return []

    async def _get_vaccination_by_id(
        self, vaccination_id: int
    ) -> Optional[VaccinationRecord]:
        """Get vaccination record by ID"""
        # Mock implementation - in production, query database
        # For now, return None
        return None

    async def _get_patient(
        self, patient_id: int
    ) -> Optional[Patient]:
        """Get patient by ID"""
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()
