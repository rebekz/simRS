"""PACS (Picture Archiving and Communication System) Integration Service for STORY-024-04

This module provides services for:
- DICOM worklist management (MWL)
- DICOM image storage and retrieval (C-STORE, C-MOVE, C-FIND)
- Study and series tracking
- PACS configuration and mapping

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.pacs_integration import (
    PACSStudy, DICOMSeries, DICOMInstance, PACSWorklist, PACSMapping, PACSConfiguration,
    PACSStudyStatus, DICOMModality
)
from app.models.hl7 import HL7Message, HL7MessageStatus


logger = logging.getLogger(__name__)


class DICOMUidGenerator(object):
    """Generates DICOM UIDs (Unique Identifiers)"""

    # DICOM UID root (example - should be registered with http://www.dicomstandard.org/)
    UID_ROOT = "1.2.840.10008.1.2.3"

    def __init__(self):
        self._counter = 0

    def generate_study_uid(self) -> str:
        """Generate Study Instance UID"""
        self._counter += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return "{}.{}.{}.{}.{}".format(
            self.UID_ROOT,
            timestamp,
            self._counter,
            "1",
            "1"
        )

    def generate_series_uid(self, study_uid: str, series_number: int) -> str:
        """Generate Series Instance UID"""
        return "{}.{}".format(study_uid, series_number)

    def generate_sop_uid(self, series_uid: str, instance_number: int) -> str:
        """Generate SOP Instance UID"""
        return "{}.{}".format(series_uid, instance_number)


class DICOMWorklistBuilder(object):
    """Builds DICOM Modality Worklist entries"""

    def __init__(self):
        self.uid_generator = DICOMUidGenerator()

    def build_worklist_entry(
        self,
        radiology_order: Any,
        patient_data: Dict[str, Any],
        config: PACSConfiguration
    ) -> Dict[str, Any]:
        """Build DICOM worklist entry

        Args:
            radiology_order: Radiology order model
            patient_data: Patient demographic data
            config: PACS configuration

        Returns:
            Dict with worklist entry data
        """
        try:
            # Generate DICOM UIDs
            study_instance_uid = self.uid_generator.generate_study_uid()
            accession_number = "ACC-{}".format(radiology_order.id)

            # Build worklist entry
            worklist_entry = {
                "accession_number": accession_number,
                "study_instance_uid": study_instance_uid,
                "requested_procedure_id": "RP-{}".format(radiology_order.id),
                "requested_procedure_description": radiology_order.procedure_name or "Radiology Procedure",
                "scheduled_procedure_step_description": radiology_order.procedure_name or "Radiology Procedure",
                "modality": self._map_modality(radiology_order.modality),
                "scheduled_date_time": radiology_order.scheduled_at.isoformat() if radiology_order.scheduled_at else None,
                "patient_id_dicom": str(patient_data.get("id", "")),
                "patient_name_dicom": self._format_patient_name(patient_data),
                "patient_birth_date": patient_data.get("date_of_birth"),
                "patient_sex": self._map_sex(patient_data.get("gender")),
                "referring_physician_name": radiology_order.referring_physician,
            }

            return worklist_entry

        except Exception as e:
            logger.error("Error building worklist entry: {}".format(e))
            raise ValueError("Failed to build worklist entry: {}".format(str(e)))

    def _map_modality(self, modality: str) -> str:
        """Map SIMRS modality to DICOM modality"""
        modality_map = {
            "ct": DICOMModality.CT,
            "mr": DICOMModality.MR,
            "us": DICOMModality.US,
            "xray": DICOMModality.XR,
            "mammography": DICOMModality.MG,
            "fluoroscopy": DICOMModality.RF,
            "nuclear": DICOMModality.NM,
            "pet": DICOMModality.PT,
        }
        return modality_map.get(modality.lower(), DICOMModality.CR)

    def _format_patient_name(self, patient_data: Dict[str, Any]) -> str:
        """Format patient name for DICOM (Last^First^Middle^Title)"""
        return "{}^{}^{}^{}".format(
            patient_data.get("last_name", ""),
            patient_data.get("first_name", ""),
            patient_data.get("middle_name", ""),
            patient_data.get("title", "")
        )

    def _map_sex(self, sex: str) -> str:
        """Map SIMRS sex to DICOM sex (M/F/O)"""
        if not sex:
            return "O"
        sex_lower = sex.lower()
        if sex_lower in ["male", "m", "laki-laki"]:
            return "M"
        elif sex_lower in ["female", "f", "perempuan"]:
            return "F"
        else:
            return "O"


class DICOMImageProcessor(object):
    """Processes DICOM image data from PACS"""

    def __init__(self):
        pass

    def process_study_metadata(
        self,
        study_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process DICOM study metadata

        Args:
            study_metadata: Raw study metadata from PACS

        Returns:
            Dict with processed study data
        """
        try:
            processed = {
                "study_instance_uid": study_metadata.get("study_instance_uid", ""),
                "accession_number": study_metadata.get("accession_number", ""),
                "study_description": study_metadata.get("study_description", ""),
                "study_date": self._parse_dicom_datetime(study_metadata.get("study_date")),
                "modality": study_metadata.get("modality", ""),
                "body_part_examined": study_metadata.get("body_part_examined", ""),
                "performing_physician": study_metadata.get("performing_physician", ""),
                "series_count": len(study_metadata.get("series", [])),
            }

            return processed

        except Exception as e:
            logger.error("Error processing study metadata: {}".format(e))
            raise ValueError("Failed to process study metadata: {}".format(str(e)))

    def process_series_metadata(
        self,
        series_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process DICOM series metadata

        Args:
            series_metadata: Raw series metadata from PACS

        Returns:
            Dict with processed series data
        """
        try:
            processed = {
                "series_instance_uid": series_metadata.get("series_instance_uid", ""),
                "series_number": series_metadata.get("series_number", 0),
                "modality": series_metadata.get("modality", ""),
                "series_description": series_metadata.get("series_description", ""),
                "body_part_examined": series_metadata.get("body_part_examined", ""),
                "instance_count": len(series_metadata.get("instances", [])),
            }

            return processed

        except Exception as e:
            logger.error("Error processing series metadata: {}".format(e))
            raise ValueError("Failed to process series metadata: {}".format(str(e)))

    def _parse_dicom_datetime(self, datetime_str: str) -> Optional[str]:
        """Parse DICOM datetime format (YYYYMMDDHHMMSS)"""
        if not datetime_str or len(datetime_str) < 8:
            return None
        try:
            # DICOM date format: YYYYMMDD
            year = int(datetime_str[0:4])
            month = int(datetime_str[4:6])
            day = int(datetime_str[6:8])

            # Optional time
            hour = 0
            minute = 0
            if len(datetime_str) >= 12:
                hour = int(datetime_str[8:10])
                minute = int(datetime_str[10:12])

            return datetime(year, month, day, hour, minute).isoformat()
        except Exception:
            return None


class PACSIntegrationService(object):
    """Service for PACS integration"""

    def __init__(self, db):
        self.db = db
        self.uid_generator = DICOMUidGenerator()
        self.worklist_builder = DICOMWorklistBuilder()
        self.image_processor = DICOMImageProcessor()

    # ==========================================================================
    # Worklist Management
    # ==========================================================================

    async def create_worklist_entry(
        self,
        radiology_order_id: int
    ) -> Dict[str, Any]:
        """Create PACS worklist entry for radiology order

        Args:
            radiology_order_id: Radiology order ID

        Returns:
            Dict with worklist entry details
        """
        try:
            # Get radiology order
            from app.models.radiology_orders import RadiologyOrder
            query = select(RadiologyOrder).where(RadiologyOrder.id == radiology_order_id)
            result = await self.db.execute(query)
            order = result.scalar_one_or_none()

            if not order:
                raise ValueError("Radiology order {} not found".format(radiology_order_id))

            # Get patient data
            from app.models.patient import Patient
            patient_query = select(Patient).where(Patient.id == order.patient_id)
            patient_result = await self.db.execute(patient_query)
            patient = patient_result.scalar_one_or_none()

            if not patient:
                raise ValueError("Patient {} not found".format(order.patient_id))

            # Get PACS configuration
            config = await self._get_pacs_config()
            if not config or not config.is_active:
                raise ValueError("PACS configuration not found or inactive")

            # Build worklist entry
            patient_data = {
                "id": patient.id,
                "first_name": patient.first_name,
                "middle_name": patient.middle_name,
                "last_name": patient.last_name,
                "title": patient.title,
                "gender": patient.gender,
                "date_of_birth": patient.date_of_birth
            }

            worklist_data = self.worklist_builder.build_worklist_entry(
                order, patient_data, config
            )

            # Create worklist entry
            worklist = PACSWorklist(
                worklist_id="WL-{}".format(order.id),
                radiology_order_id=radiology_order_id,
                patient_id=order.patient_id,
                accession_number=worklist_data["accession_number"],
                requested_procedure_id=worklist_data["requested_procedure_id"],
                study_instance_uid=worklist_data["study_instance_uid"],
                requested_procedure_description=worklist_data["requested_procedure_description"],
                scheduled_procedure_step_description=worklist_data["scheduled_procedure_step_description"],
                modality=worklist_data["modality"],
                scheduled_date_time=datetime.utcnow(),
                patient_id_dicom=worklist_data["patient_id_dicom"],
                patient_name_dicom=worklist_data["patient_name_dicom"],
                patient_birth_date=worklist_data["patient_birth_date"],
                patient_sex=worklist_data["patient_sex"],
                referring_physician_name=worklist_data["referring_physician_name"],
                status=PACSStudyStatus.SCHEDULED
            )

            self.db.add(worklist)
            await self.db.commit()

            logger.info("Created worklist entry for order: {}".format(radiology_order_id))

            return {
                "worklist_id": worklist.worklist_id,
                "accession_number": worklist.accession_number,
                "study_instance_uid": worklist.study_instance_uid,
                "status": worklist.status,
                "scheduled_date_time": worklist.scheduled_date_time.isoformat()
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error creating worklist entry: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create worklist entry: {}".format(str(e)))

    async def get_worklist_entries(
        self,
        modality: Optional[str] = None,
        date: Optional[str] = None,
        performed: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get worklist entries with filtering

        Args:
            modality: Filter by modality
            date: Filter by date (YYYY-MM-DD)
            performed: Filter by performed status

        Returns:
            List of worklist entries
        """
        try:
            # Build filters
            filters = []

            if modality:
                filters.append(PACSWorklist.modality == modality.upper())
            if date:
                filters.append(func.date(PACSWorklist.scheduled_date_time) == date)
            if performed is not None:
                filters.append(PACSWorklist.performed == performed)

            # Get worklist entries
            query = select(PACSWorklist)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(PACSWorklist.scheduled_date_time.asc())

            result = await self.db.execute(query)
            worklist_entries = result.scalars().all()

            # Build response
            entries = [
                {
                    "worklist_id": w.worklist_id,
                    "accession_number": w.accession_number,
                    "study_instance_uid": w.study_instance_uid,
                    "modality": w.modality,
                    "scheduled_date_time": w.scheduled_date_time.isoformat(),
                    "patient_id_dicom": w.patient_id_dicom,
                    "patient_name_dicom": w.patient_name_dicom,
                    "requested_procedure_description": w.requested_procedure_description,
                    "status": w.status,
                    "performed": w.performed
                }
                for w in worklist_entries
            ]

            return entries

        except Exception as e:
            logger.error("Error getting worklist entries: {}".format(e))
            raise ValueError("Failed to get worklist entries: {}".format(str(e)))

    # ==========================================================================
    # Study Tracking
    # ==========================================================================

    async def create_study(
        self,
        radiology_order_id: int,
        study_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create PACS study tracking record

        Args:
            radiology_order_id: Radiology order ID
            study_metadata: Study metadata from PACS

        Returns:
            Dict with study details
        """
        try:
            # Get radiology order
            from app.models.radiology_orders import RadiologyOrder
            query = select(RadiologyOrder).where(RadiologyOrder.id == radiology_order_id)
            result = await self.db.execute(query)
            order = result.scalar_one_or_none()

            if not order:
                raise ValueError("Radiology order {} not found".format(radiology_order_id))

            # Get worklist entry
            worklist_query = select(PACSWorklist).where(
                PACSWorklist.radiology_order_id == radiology_order_id
            )
            worklist_result = await self.db.execute(worklist_query)
            worklist = worklist_result.scalar_one_or_none()

            # Process study metadata
            processed_metadata = self.image_processor.process_study_metadata(study_metadata)

            # Create study
            study = PACSStudy(
                study_id="STUDY-{}".format(radiology_order_id),
                study_instance_uid=processed_metadata["study_instance_uid"],
                accession_number=processed_metadata.get("accession_number") or (worklist.accession_number if worklist else "ACC-{}".format(radiology_order_id)),
                radiology_order_id=radiology_order_id,
                patient_id=order.patient_id,
                encounter_id=order.encounter_id,
                study_description=processed_metadata.get("study_description"),
                study_date=self._parse_datetime(processed_metadata.get("study_date")),
                modality=processed_metadata.get("modality"),
                body_part_examined=processed_metadata.get("body_part_examined"),
                performing_physician=processed_metadata.get("performing_physician"),
                patient_id_dicom=str(order.patient_id),
                patient_name_dicom=worklist.patient_name_dicom if worklist else "",
                status=PACSStudyStatus.IN_PROGRESS,
                series_count=processed_metadata.get("series_count", 0)
            )

            self.db.add(study)
            await self.db.commit()

            logger.info("Created PACS study for order: {}".format(radiology_order_id))

            return {
                "study_id": study.study_id,
                "accession_number": study.accession_number,
                "study_instance_uid": study.study_instance_uid,
                "status": study.status,
                "series_count": study.series_count
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error creating study: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create study: {}".format(str(e)))

    async def get_study_status(
        self,
        study_id: str
    ) -> Dict[str, Any]:
        """Get PACS study status

        Args:
            study_id: Study identifier

        Returns:
            Dict with study status details
        """
        try:
            query = select(PACSStudy).options(
                selectinload(PACSStudy.series)
            ).where(PACSStudy.study_id == study_id)

            result = await self.db.execute(query)
            study = result.scalar_one_or_none()

            if not study:
                raise ValueError("Study {} not found".format(study_id))

            # Get series summary
            series_summary = []
            for series in study.series:
                series_summary.append({
                    "series_id": series.series_id,
                    "series_instance_uid": series.series_instance_uid,
                    "modality": series.modality,
                    "series_description": series.series_description,
                    "instance_count": series.instance_count
                })

            return {
                "study_id": study.study_id,
                "accession_number": study.accession_number,
                "study_instance_uid": study.study_instance_uid,
                "status": study.status,
                "modality": study.modality,
                "study_description": study.study_description,
                "study_date": study.study_date.isoformat() if study.study_date else None,
                "series_count": study.series_count,
                "instance_count": study.instance_count,
                "has_images": study.has_images,
                "series": series_summary
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error getting study status: {}".format(e))
            raise ValueError("Failed to get study status: {}".format(str(e)))

    # ==========================================================================
    # Configuration and Mapping
    # ==========================================================================

    async def _get_pacs_config(self) -> Optional[PACSConfiguration]:
        """Get active PACS configuration"""
        query = select(PACSConfiguration).where(
            and_(
                PACSConfiguration.is_active == True,
                PACSConfiguration.config_key == "default"
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_mapping(
        self,
        mapping_type: str,
        simrs_code: str,
        simrs_name: str,
        pacs_code: str,
        pacs_name: str
    ) -> Dict[str, Any]:
        """Create PACS code mapping

        Args:
            mapping_type: Mapping type (modality, station, physician)
            simrs_code: SIMRS code
            simrs_name: SIMRS name
            pacs_code: PACS/AE title
            pacs_name: PACS name

        Returns:
            Dict with mapping details
        """
        try:
            mapping = PACSMapping(
                mapping_type=mapping_type,
                simrs_code=simrs_code,
                simrs_name=simrs_name,
                pacs_code=pacs_code,
                pacs_name=pacs_name,
                is_active=True
            )

            self.db.add(mapping)
            await self.db.commit()

            return {
                "mapping_id": mapping.id,
                "message": "PACS mapping created successfully"
            }

        except Exception as e:
            logger.error("Error creating PACS mapping: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create PACS mapping: {}".format(str(e)))

    def _parse_datetime(self, datetime_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string"""
        if not datetime_str:
            return None
        try:
            return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        except Exception:
            return None


def get_pacs_integration_service(db):
    """Get or create PACS integration service instance

    Args:
        db: Database session

    Returns:
        PACSIntegrationService instance
    """
    return PACSIntegrationService(db)
