"""FHIR R4 Server Service for STORY-024-02

This module provides services for:
- FHIR resource CRUD operations
- Mapping between FHIR resources and SIMRS entities
- FHIR search operations
- FHIR validation and OperationOutcome generation

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.fhir import FHIRResource, FHIRAuditEvent, FHIRResourceType
from app.models.patient import Patient
from app.models.encounter import Encounter
from app.models.user import User


logger = logging.getLogger(__name__)


class FHIRValidator(object):
    """FHIR resource validator"""

    @staticmethod
    def validate_resource_type(resource_type: str) -> bool:
        """Validate FHIR resource type"""
        valid_types = [
            FHIRResourceType.PATIENT,
            FHIRResourceType.ENCOUNTER,
            FHIRResourceType.CONDITION,
            FHIRResourceType.OBSERVATION,
            FHIRResourceType.SERVICEREQUEST,
            FHIRResourceType.MEDICATIONREQUEST,
            FHIRResourceType.DIAGNOSTICREPORT,
            FHIRResourceType.PRACTITIONER,
            FHIRResourceType.ORGANIZATION,
            FHIRResourceType.LOCATION,
            FHIRResourceType.IMMUNIZATION,
            FHIRResourceType.DOCUMENTREFERENCE
        ]
        return resource_type in valid_types

    @staticmethod
    def create_operation_outcome(severity: str, code: str, diagnostics: str) -> Dict[str, Any]:
        """Create FHIR OperationOutcome resource"""
        return {
            "resourceType": "OperationOutcome",
            "issue": [
                {
                    "severity": severity,
                    "code": code,
                    "diagnostics": diagnostics
                }
            ]
        }


class FHIRMapper(object):
    """Maps SIMRS entities to FHIR resources"""

    def patient_to_fhir(self, patient: Patient) -> Dict[str, Any]:
        """Convert SIMRS Patient to FHIR Patient resource

        Args:
            patient: SIMRS Patient model

        Returns:
            FHIR Patient resource as dict
        """
        resource = {
            "resourceType": "Patient",
            "id": "Patient-{}".format(patient.id),
            "identifier": [
                {
                    "use": "usual",
                    "system": "https://simrs-hospital.com/patient-id",
                    "value": str(patient.id)
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": patient.last_name or "",
                    "given": [patient.first_name or ""] + ([patient.middle_name] if patient.middle_name else [])
                }
            ],
            "telecom": [],
            "gender": self._map_gender(patient.gender),
            "birthDate": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "address": [],
            "active": not patient.is_deceased if hasattr(patient, 'is_deceased') else True
        }

        # Add phone numbers
        if patient.phone:
            resource["telecom"].append({
                "system": "phone",
                "value": patient.phone,
                "use": "mobile"
            })

        # Add email
        if patient.email:
            resource["telecom"].append({
                "system": "email",
                "value": patient.email,
                "use": "home"
            })

        # Add address
        if patient.address:
            resource["address"].append({
                "use": "home",
                "text": patient.address,
                "city": patient.city,
                "state": patient.province,
                "postalCode": patient.postal_code,
                "country": "IDN"
            })

        # Add BPJS identifier if available
        if patient.bpjs_number:
            resource["identifier"].append({
                "use": "official",
                "system": "https://bpjs-kesehatan.go.id/peserta",
                "value": patient.bpjs_number
            })

        return resource

    def encounter_to_fhir(self, encounter: Encounter) -> Dict[str, Any]:
        """Convert SIMRS Encounter to FHIR Encounter resource

        Args:
            encounter: SIMRS Encounter model

        Returns:
            FHIR Encounter resource as dict
        """
        resource = {
            "resourceType": "Encounter",
            "id": "Encounter-{}".format(encounter.id),
            "status": self._map_encounter_status(encounter.status),
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": self._map_encounter_class(encounter.encounter_type),
                "display": encounter.encounter_type
            },
            "subject": {
                "reference": "Patient/{}".format(encounter.patient_id),
                "display": "Patient {}".format(encounter.patient_id)
            },
            "period": {
                "start": encounter.created_at.isoformat() if encounter.created_at else None
            }
        }

        # Add location if available
        if encounter.department_id:
            resource["location"] = [{
                "location": {
                    "reference": "Location/{}".format(encounter.department_id)
                }
            }]

        return resource

    def _map_gender(self, gender: Optional[str]) -> str:
        """Map SIMRS gender to FHIR"""
        if not gender:
            return "unknown"

        gender_map = {
            "male": "male",
            "female": "female",
            "other": "other"
        }
        return gender_map.get(gender.lower(), "unknown")

    def _map_encounter_status(self, status: Optional[str]) -> str:
        """Map SIMRS encounter status to FHIR"""
        if not status:
            return "unknown"

        status_map = {
            "planned": "planned",
            "in_progress": "in-progress",
            "on_hold": "onhold",
            "completed": "completed",
            "cancelled": "cancelled",
            "discontinued": "discontinued"
        }
        return status_map.get(status.lower(), "unknown")

    def _map_encounter_class(self, encounter_type: Optional[str]) -> str:
        """Map encounter type to FHIR encounter class"""
        if not encounter_type:
            return "AMB"

        type_map = {
            "inpatient": "IMP",
            "outpatient": "AMB",
            "emergency": "EMER",
            "virtual": "VR"
        }
        return type_map.get(encounter_type.lower(), "AMB")


class FHIRServerService(object):
    """Service for FHIR R4 server operations"""

    def __init__(self, db):
        self.db = db
        self.mapper = FHIRMapper()
        self.validator = FHIRValidator()

    # ==========================================================================
    # Resource CRUD Operations
    # ==========================================================================

    async def read_resource(
        self,
        resource_type: str,
        resource_id: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Read FHIR resource by ID

        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID (with or without type prefix)
            user_id: User ID for audit logging

        Returns:
            FHIR resource as dict
        """
        try:
            # Validate resource type
            if not self.validator.validate_resource_type(resource_type):
                raise ValueError("Unknown or unsupported resource type: {}".format(resource_type))

            # Extract numeric ID if prefixed
            if resource_id.startswith("{}-".format(resource_type)):
                numeric_id = resource_id.split("-", 1)[1]
            else:
                numeric_id = resource_id

            # Get resource from appropriate SIMRS table
            if resource_type == FHIRResourceType.PATIENT:
                return await self._read_patient(numeric_id, user_id)
            elif resource_type == FHIRResourceType.ENCOUNTER:
                return await self._read_encounter(numeric_id, user_id)
            else:
                raise ValueError("Resource type {} not yet implemented".format(resource_type))

        except ValueError:
            await self._audit_access(
                resource_type, resource_id, "read", "GET", None, 404, user_id, str(ValueError)
            )
            raise
        except Exception as e:
            logger.error("Error reading FHIR resource: {}".format(e))
            await self._audit_access(
                resource_type, resource_id, "read", "GET", None, 500, user_id, str(e)
            )
            raise ValueError("Failed to read resource: {}".format(str(e)))

    async def _read_patient(
        self,
        patient_id: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Read Patient resource from SIMRS

        Args:
            patient_id: Patient ID
            user_id: User ID for audit

        Returns:
            FHIR Patient resource
        """
        try:
            query = select(Patient).where(Patient.id == int(patient_id))
            result = await self.db.execute(query)
            patient = result.scalar_one_or_none()

            if not patient:
                raise ValueError("Patient {} not found".format(patient_id))

            # Convert to FHIR
            fhir_resource = self.mapper.patient_to_fhir(patient)

            # Audit access
            await self._audit_access(
                FHIRResourceType.PATIENT,
                fhir_resource["id"],
                "read",
                "GET",
                None,
                200,
                user_id
            )

            return fhir_resource

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error reading patient: {}".format(e))
            raise ValueError("Failed to read patient: {}".format(str(e)))

    async def _read_encounter(
        self,
        encounter_id: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Read Encounter resource from SIMRS

        Args:
            encounter_id: Encounter ID
            user_id: User ID for audit

        Returns:
            FHIR Encounter resource
        """
        try:
            query = select(Encounter).where(Encounter.id == int(encounter_id))
            result = await self.db.execute(query)
            encounter = result.scalar_one_or_none()

            if not encounter:
                raise ValueError("Encounter {} not found".format(encounter_id))

            # Convert to FHIR
            fhir_resource = self.mapper.encounter_to_fhir(encounter)

            # Audit access
            await self._audit_access(
                FHIRResourceType.ENCOUNTER,
                fhir_resource["id"],
                "read",
                "GET",
                None,
                200,
                user_id
            )

            return fhir_resource

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error reading encounter: {}".format(e))
            raise ValueError("Failed to read encounter: {}".format(str(e)))

    async def search_resources(
        self,
        resource_type: str,
        parameters: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search FHIR resources by parameters

        Args:
            resource_type: FHIR resource type
            parameters: Search parameters
            user_id: User ID for audit

        Returns:
            FHIR Bundle with search results
        """
        try:
            # Validate resource type
            if not self.validator.validate_resource_type(resource_type):
                raise ValueError("Unknown or unsupported resource type: {}".format(resource_type))

            # Perform search based on resource type
            if resource_type == FHIRResourceType.PATIENT:
                results = await self._search_patients(parameters)
            elif resource_type == FHIRResourceType.ENCOUNTER:
                results = await self._search_encounters(parameters)
            else:
                raise ValueError("Search for resource type {} not yet implemented".format(resource_type))

            # Build FHIR Bundle response
            bundle = {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": len(results),
                "entry": [
                    {
                        "resource": result
                    }
                    for result in results
                ]
            }

            # Audit access
            await self._audit_access(
                resource_type,
                None,
                "search",
                "GET",
                None,
                200,
                user_id
            )

            return bundle

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error searching resources: {}".format(e))
            raise ValueError("Failed to search resources: {}".format(str(e)))

    async def _search_patients(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Patient resources

        Args:
            parameters: Search parameters

        Returns:
            List of FHIR Patient resources
        """
        try:
            query = select(Patient)
            filters = []

            # Filter by name
            if "name" in parameters:
                name_filter = "%{}%".format(parameters["name"])
                filters.append(
                    or_(
                        Patient.first_name.ilike(name_filter),
                        Patient.last_name.ilike(name_filter)
                    )
                )

            # Filter by identifier
            if "identifier" in parameters:
                try:
                    # Try to parse as patient ID
                    patient_id = int(parameters["identifier"])
                    filters.append(Patient.id == patient_id)
                except ValueError:
                    # Search by BPJS number
                    filters.append(Patient.bpjs_number == parameters["identifier"])

            # Filter by birthdate
            if "birthdate" in parameters:
                filters.append(
                    func.date(Patient.date_of_birth) == parameters["birthdate"]
                )

            # Filter by gender
            if "gender" in parameters:
                filters.append(Patient.gender == parameters["gender"])

            # Apply filters
            if filters:
                query = query.where(and_(*filters))

            # Limit results
            count = int(parameters.get("_count", 20))
            if count > 100:
                count = 100

            query = query.limit(count)

            # Execute query
            result = await self.db.execute(query)
            patients = result.scalars().all()

            # Convert to FHIR resources
            return [self.mapper.patient_to_fhir(p) for p in patients]

        except Exception as e:
            logger.error("Error searching patients: {}".format(e))
            raise

    async def _search_encounters(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Encounter resources

        Args:
            parameters: Search parameters

        Returns:
            List of FHIR Encounter resources
        """
        try:
            query = select(Encounter)
            filters = []

            # Filter by patient
            if "patient" in parameters:
                # Parse patient reference (e.g., "Patient/123")
                patient_ref = parameters["patient"]
                if patient_ref.startswith("Patient/"):
                    patient_id = int(patient_ref.split("/", 1)[1])
                    filters.append(Encounter.patient_id == patient_id)

            # Filter by status
            if "status" in parameters:
                filters.append(Encounter.status == parameters["status"])

            # Filter by date
            if "date" in parameters:
                filters.append(
                    func.date(Encounter.created_at) == parameters["date"]
                )

            # Apply filters
            if filters:
                query = query.where(and_(*filters))

            # Limit results
            count = int(parameters.get("_count", 20))
            if count > 100:
                count = 100

            query = query.limit(count)

            # Execute query
            result = await self.db.execute(query)
            encounters = result.scalars().all()

            # Convert to FHIR resources
            return [self.mapper.encounter_to_fhir(e) for e in encounters]

        except Exception as e:
            logger.error("Error searching encounters: {}".format(e))
            raise

    async def create_resource(
        self,
        resource_type: str,
        resource_data: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create new FHIR resource

        Args:
            resource_type: FHIR resource type
            resource_data: Resource data as dict
            user_id: User ID for audit

        Returns:
            Created FHIR resource
        """
        try:
            # Validate resource type
            if not self.validator.validate_resource_type(resource_type):
                raise ValueError("Unknown or unsupported resource type: {}".format(resource_type))

            # Validate resource matches type
            if resource_data.get("resourceType") != resource_type:
                raise ValueError("Resource type mismatch")

            # For now, return not implemented for create operations
            # In production, this would create the corresponding SIMRS entity
            raise ValueError("Create operation not yet implemented for resource type: {}".format(resource_type))

        except ValueError:
            await self._audit_access(
                resource_type,
                None,
                "create",
                "POST",
                None,
                501,
                user_id,
                "Not implemented"
            )
            raise
        except Exception as e:
            logger.error("Error creating resource: {}".format(e))
            await self._audit_access(
                resource_type,
                None,
                "create",
                "POST",
                None,
                500,
                user_id,
                str(e)
            )
            raise ValueError("Failed to create resource: {}".format(str(e)))

    async def _audit_access(
        self,
        resource_type: str,
        resource_id: Optional[str],
        operation: str,
        method: str,
        url: Optional[str],
        status_code: int,
        user_id: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Audit FHIR API access

        Args:
            resource_type: Resource type accessed
            resource_id: Resource ID accessed
            operation: FHIR operation
            method: HTTP method
            url: Request URL
            status_code: HTTP status code
            user_id: User who made request
            error_message: Error message if any
        """
        try:
            audit_event = FHIRAuditEvent(
                resource_type=resource_type,
                resource_id=resource_id,
                operation=operation,
                request_method=method,
                request_url=url or "/fhir/{}{}".format(
                    resource_type,
                    "/{}".format(resource_id) if resource_id else ""
                ),
                user_id=user_id,
                response_status=status_code,
                operation_outcome=self.validator.create_operation_outcome(
                    "error" if status_code >= 400 else "information",
                    "processing" if status_code >= 400 else "success",
                    error_message or "Operation completed"
                ) if error_message or status_code >= 400 else None
            )

            self.db.add(audit_event)
            self.db.flush()

        except Exception as e:
            logger.error("Error auditing FHIR access: {}".format(e))
            # Don't raise - audit logging shouldn't break the API


def get_fhir_server_service(db):
    """Get or create FHIR server service instance

    Args:
        db: Database session

    Returns:
        FHIRServerService instance
    """
    return FHIRServerService(db)
