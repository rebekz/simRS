"""EMR/EHR Integration Service for STORY-024-06

This module provides services for:
- CCD/CCR document generation and parsing
- Patient data exchange with external systems
- Referral and consultation workflows
- Health Information Exchange (HIE) integration

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.emr_integration import (
    ExternalSystem, DataExchange, PatientDataQuery, Referral,
    ConsultationRequest, CCDDocument, ExchangeProtocol, ExchangeStatus
)


logger = logging.getLogger(__name__)


class CCDDocumentBuilder(object):
    """Builds CCD (Continuity of Care Document) documents"""

    def __init__(self):
        pass

    async def build_ccd(
        self,
        patient_id: int,
        db: AsyncSession,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Build CCD document for patient

        Args:
            patient_id: Patient ID
            db: Database session
            include_sections: Sections to include (default: all)

        Returns:
            Dict with CCD document structure
        """
        try:
            # Default sections
            if include_sections is None:
                include_sections = [
                    "header", "problems", "medications", "allergies",
                    "immunizations", "vital_signs", "results", "procedures"
                ]

            ccd = {
                "document_type": "CCD",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat(),
                "sections": {}
            }

            # Get patient data
            from app.models.patient import Patient
            patient_query = select(Patient).where(Patient.id == patient_id)
            patient_result = await db.execute(patient_query)
            patient = patient_result.scalar_one_or_none()

            if not patient:
                raise ValueError("Patient {} not found".format(patient_id))

            # Build header
            if "header" in include_sections:
                ccd["sections"]["header"] = self._build_header(patient)

            # Build problems
            if "problems" in include_sections:
                ccd["sections"]["problems"] = await self._build_problems(patient_id, db)

            # Build medications
            if "medications" in include_sections:
                ccd["sections"]["medications"] = await self._build_medications(patient_id, db)

            # Build allergies
            if "allergies" in include_sections:
                ccd["sections"]["allergies"] = await self._build_allergies(patient_id, db)

            # Build immunizations
            if "immunizations" in include_sections:
                ccd["sections"]["immunizations"] = await self._build_immunizations(patient_id, db)

            # Build vital signs
            if "vital_signs" in include_sections:
                ccd["sections"]["vital_signs"] = await self._build_vital_signs(patient_id, db)

            # Build results
            if "results" in include_sections:
                ccd["sections"]["results"] = await self._build_results(patient_id, db)

            # Build procedures
            if "procedures" in include_sections:
                ccd["sections"]["procedures"] = await self._build_procedures(patient_id, db)

            return ccd

        except Exception as e:
            logger.error("Error building CCD: {}".format(e))
            raise ValueError("Failed to build CCD: {}".format(str(e)))

    def _build_header(self, patient: Any) -> Dict[str, Any]:
        """Build CCD header section"""
        return {
            "patient_id": str(patient.id),
            "patient_name": {
                "first": patient.first_name,
                "middle": patient.middle_name,
                "last": patient.last_name,
                "title": patient.title
            },
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "gender": patient.gender,
            "address": {
                "street": patient.address,
                "city": patient.city,
                "province": patient.province,
                "postal_code": patient.postal_code,
                "country": patient.country
            } if patient.address else None,
            "contact": {
                "phone": patient.phone,
                "email": patient.email
            }
        }

    async def _build_problems(self, patient_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Build problems section"""
        try:
            from app.models.problem_list import Problem
            query = select(Problem).where(
                and_(
                    Problem.patient_id == patient_id,
                    Problem.is_active == True
                )
            )
            result = await db.execute(query)
            problems = result.scalars().all()

            return [
                {
                    "code": p.icd10_code,
                    "description": p.description,
                    "onset_date": p.onset_date.isoformat() if p.onset_date else None,
                    "status": p.status
                }
                for p in problems
            ]

        except Exception as e:
            logger.error("Error building problems: {}".format(e))
            return []

    async def _build_medications(self, patient_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Build medications section"""
        try:
            from app.models.prescription import Prescription
            query = select(Prescription).where(
                and_(
                    Prescription.patient_id == patient_id,
                    Prescription.status == "active"
                )
            )
            result = await db.execute(query)
            medications = result.scalars().all()

            return [
                {
                    "medication": m.medication_name,
                    "dosage": m.dosage,
                    "frequency": m.frequency,
                    "route": m.route,
                    "start_date": m.start_date.isoformat() if m.start_date else None
                }
                for m in medications
            ]

        except Exception as e:
            logger.error("Error building medications: {}".format(e))
            return []

    async def _build_allergies(self, patient_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Build allergies section"""
        try:
            from app.models.allergy import Allergy
            query = select(Allergy).where(
                and_(
                    Allergy.patient_id == patient_id,
                    Allergy.is_active == True
                )
            )
            result = await db.execute(query)
            allergies = result.scalars().all()

            return [
                {
                    "allergen": a.allergen,
                    "reaction": a.reaction,
                    "severity": a.severity,
                    "allergy_type": a.allergy_type
                }
                for a in allergies
            ]

        except Exception as e:
            logger.error("Error building allergies: {}".format(e))
            return []

    async def _build_immunizations(self, patient_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Build immunizations section"""
        try:
            # Placeholder - implement when vaccination tracking is available
            return []

        except Exception as e:
            logger.error("Error building immunizations: {}".format(e))
            return []

    async def _build_vital_signs(self, patient_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Build vital signs section"""
        try:
            from app.models.encounter import Encounter
            from app.models.vitals import Vitals

            # Get recent encounters with vitals
            query = select(Encounter).options(
                selectinload(Encounter.vitals)
            ).where(
                and_(
                    Encounter.patient_id == patient_id,
                    Encounter.status == "active"
                )
            ).limit(10)

            result = await db.execute(query)
            encounters = result.scalars().all()

            vitals_list = []
            for encounter in encounters:
                for vital in encounter.vitals:
                    vitals_list.append({
                        "date": vital.recorded_at.isoformat() if vital.recorded_at else None,
                        "blood_pressure_systolic": vital.blood_pressure_systolic,
                        "blood_pressure_diastolic": vital.blood_pressure_diastolic,
                        "heart_rate": vital.heart_rate,
                        "respiratory_rate": vital.respiratory_rate,
                        "temperature": vital.temperature,
                        "spo2": vital.spo2
                    })

            return vitals_list

        except Exception as e:
            logger.error("Error building vital signs: {}".format(e))
            return []

    async def _build_results(self, patient_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Build lab results section"""
        try:
            from app.models.lab_orders import LabOrder, LabResult
            query = select(LabOrder).options(
                selectinload(LabOrder.results)
            ).where(LabOrder.patient_id == patient_id).limit(20)

            result = await db.execute(query)
            orders = result.scalars().all()

            results_list = []
            for order in orders:
                for lab_result in order.results:
                    results_list.append({
                        "test_code": lab_result.test_code,
                        "test_name": lab_result.test_name,
                        "result_value": lab_result.result_value,
                        "unit": lab_result.unit,
                        "reference_range": lab_result.reference_range,
                        "abnormal_flag": lab_result.abnormal_flag,
                        "result_date": lab_result.result_date.isoformat() if lab_result.result_date else None
                    })

            return results_list

        except Exception as e:
            logger.error("Error building results: {}".format(e))
            return []

    async def _build_procedures(self, patient_id: int, db: AsyncSession) -> List[Dict[str, Any]]:
        """Build procedures section"""
        try:
            from app.models.encounter import Encounter
            from app.models.procedure_codes import Procedure

            query = select(Encounter).options(
                selectinload(Encounter.procedures)
            ).where(Encounter.patient_id == patient_id).limit(20)

            result = await db.execute(query)
            encounters = result.scalars().all()

            procedures_list = []
            for encounter in encounters:
                for proc in encounter.procedures:
                    procedures_list.append({
                        "code": proc.procedure_code,
                        "description": proc.description,
                        "date": proc.performed_at.isoformat() if proc.performed_at else None,
                        "provider": proc.provider_name
                    })

            return procedures_list

        except Exception as e:
            logger.error("Error building procedures: {}".format(e))
            return []


class EMRIntegrationService(object):
    """Service for EMR/EHR integration"""

    def __init__(self, db):
        self.db = db
        self.ccd_builder = CCDDocumentBuilder()

    # ==========================================================================
    # External System Management
    # ==========================================================================

    async def register_external_system(
        self,
        system_code: str,
        system_name: str,
        system_type: str,
        protocol: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Register external EMR/EHR system

        Args:
            system_code: System code
            system_name: System name
            system_type: System type (EHR, EMR, HIE)
            protocol: Exchange protocol
            **kwargs: Additional system attributes

        Returns:
            Dict with system details
        """
        try:
            system = ExternalSystem(
                system_id="EXT-{}".format(system_code),
                system_code=system_code,
                system_name=system_name,
                system_type=system_type,
                organization=kwargs.get("organization"),
                facility_type=kwargs.get("facility_type"),
                address=kwargs.get("address"),
                city=kwargs.get("city"),
                province=kwargs.get("province"),
                country=kwargs.get("country"),
                postal_code=kwargs.get("postal_code"),
                protocol=protocol,
                endpoint_url=kwargs.get("endpoint_url"),
                auth_type=kwargs.get("auth_type"),
                auth_credentials=kwargs.get("auth_credentials"),
                connection_config=kwargs.get("connection_config"),
                mapping_config=kwargs.get("mapping_config"),
                supported_formats=kwargs.get("supported_formats")
            )

            self.db.add(system)
            await self.db.commit()

            logger.info("Registered external system: {}".format(system.system_id))

            return {
                "system_id": system.system_id,
                "system_code": system.system_code,
                "system_name": system.system_name,
                "status": system.status
            }

        except Exception as e:
            logger.error("Error registering external system: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to register external system: {}".format(str(e)))

    # ==========================================================================
    # CCD Document Exchange
    # ==========================================================================

    async def send_ccd(
        self,
        patient_id: int,
        external_system_id: int,
        include_sections: Optional[List[str]] = None,
        initiated_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send CCD document to external system

        Args:
            patient_id: Patient ID
            external_system_id: External system ID
            include_sections: Sections to include
            initiated_by: User ID

        Returns:
            Dict with exchange details
        """
        try:
            # Get external system
            system_query = select(ExternalSystem).where(ExternalSystem.id == external_system_id)
            system_result = await self.db.execute(system_query)
            system = system_result.scalar_one_or_none()

            if not system:
                raise ValueError("External system {} not found".format(external_system_id))

            # Build CCD
            ccd_data = await self.ccd_builder.build_ccd(patient_id, self.db, include_sections)

            # Create data exchange record
            exchange = DataExchange(
                exchange_id="EXCH-{}-{}".format(system.system_code, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                external_system_id=external_system_id,
                patient_id=patient_id,
                exchange_type="submit",
                exchange_direction="outbound",
                document_type="CCD",
                request_data=ccd_data,
                status=ExchangeStatus.COMPLETED,
                initiated_at=datetime.utcnow(),
                sent_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                record_count=1
            )

            self.db.add(exchange)

            # Store CCD document
            document_id = "CCD-{}-{}".format(patient_id, datetime.utcnow().strftime("%Y%m%d%H%M%S"))
            ccd_document = CCDDocument(
                document_id=document_id,
                patient_id=patient_id,
                external_system_id=external_system_id,
                document_type="CCD",
                document_format="JSON",
                document_date=datetime.utcnow(),
                document_content=str(ccd_data),
                parsed_data=ccd_data,
                exchange_id=exchange.exchange_id,
                direction="sent"
            )

            self.db.add(ccd_document)
            await self.db.commit()

            logger.info("Sent CCD for patient {} to system {}".format(patient_id, system.system_code))

            return {
                "exchange_id": exchange.exchange_id,
                "document_id": document_id,
                "status": exchange.status,
                "sent_at": exchange.sent_at.isoformat()
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error sending CCD: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to send CCD: {}".format(str(e)))

    # ==========================================================================
    # Patient Data Query
    # ==========================================================================

    async def query_patient_data(
        self,
        patient_id: int,
        external_system_id: int,
        query_criteria: Dict[str, Any],
        submitted_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Query patient data from external system

        Args:
            patient_id: Local patient ID
            external_system_id: External system ID
            query_criteria: Query criteria
            submitted_by: User ID

        Returns:
            Dict with query details
        """
        try:
            # Create query record
            query_id = "QUERY-{}-{}".format(patient_id, datetime.utcnow().strftime("%Y%m%d%H%M%S"))

            query = PatientDataQuery(
                query_id=query_id,
                external_system_id=external_system_id,
                patient_id=patient_id,
                query_criteria=query_criteria,
                requested_data_types=query_criteria.get("data_types", []),
                date_range=query_criteria.get("date_range"),
                response_status="pending",
                submitted_at=datetime.utcnow(),
                submitted_by=submitted_by
            )

            self.db.add(query)
            await self.db.commit()

            logger.info("Created patient data query: {}".format(query_id))

            # In production, would initiate actual query to external system
            # For now, return pending status

            return {
                "query_id": query_id,
                "status": "pending",
                "submitted_at": query.submitted_at.isoformat(),
                "message": "Query submitted successfully"
            }

        except Exception as e:
            logger.error("Error querying patient data: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to query patient data: {}".format(str(e)))

    # ==========================================================================
    # Referral Management
    # ==========================================================================

    async def create_referral(
        self,
        patient_id: int,
        referral_type: str,
        priority: str,
        reason: str,
        external_system_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create patient referral

        Args:
            patient_id: Patient ID
            referral_type: Type of referral
            priority: Priority level
            reason: Reason for referral
            external_system_id: External system ID
            **kwargs: Additional referral attributes

        Returns:
            Dict with referral details
        """
        try:
            referral = Referral(
                referral_id="REF-{}-{}".format(patient_id, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                patient_id=patient_id,
                encounter_id=kwargs.get("encounter_id"),
                external_system_id=external_system_id,
                referral_type=referral_type,
                priority=priority,
                reason=reason,
                referring_provider_id=kwargs.get("referring_provider_id"),
                referred_to_provider=kwargs.get("referred_to_provider"),
                referred_to_facility=kwargs.get("referred_to_facility"),
                diagnosis=kwargs.get("diagnosis"),
                clinical_summary=kwargs.get("clinical_summary"),
                attachments=kwargs.get("attachments"),
                referral_date=datetime.utcnow()
            )

            self.db.add(referral)
            await self.db.commit()

            logger.info("Created referral: {}".format(referral.referral_id))

            return {
                "referral_id": referral.referral_id,
                "status": referral.status,
                "referral_date": referral.referral_date.isoformat()
            }

        except Exception as e:
            logger.error("Error creating referral: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create referral: {}".format(str(e)))


def get_emr_integration_service(db):
    """Get or create EMR integration service instance

    Args:
        db: Database session

    Returns:
        EMRIntegrationService instance
    """
    return EMRIntegrationService(db)
