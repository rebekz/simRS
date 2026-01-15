"""Message Transformation Service for STORY-024-10

This module provides services for:
- HL7 to FHIR transformation
- FHIR to HL7 transformation
- Field mapping and configuration
- Terminology mapping

Python 3.5+ compatible
"""

import logging
import json
import copy
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transformation import (
    TransformationRule, FieldMapping, TerminologyMapping,
    LookupTable, TransformationLog, TransformationTest,
    TransformationDirection, TransformationStatus, MappingType
)


logger = logging.getLogger(__name__)


# =============================================================================
# Service Factory
# =============================================================================

_transformation_service_instance = None


def get_transformation_service(db: AsyncSession):
    """Get or create transformation service instance"""
    global _transformation_service_instance
    if _transformation_service_instance is None:
        _transformation_service_instance = TransformationService(db)
    else:
        _transformation_service_instance.db = db
    return _transformation_service_instance


# =============================================================================
# HL7 to FHIR Transformer
# =============================================================================

class HL7ToFHIRTransformer(object):
    """HL7 to FHIR message transformer

    Transforms HL7 v2.x messages to FHIR R4 resources.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def transform_adt_to_patient(
        self,
        hl7_message: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform HL7 ADT message to FHIR Patient resource

        Args:
            hl7_message: Parsed HL7 message
            config: Optional transformation config

        Returns:
            FHIR Patient resource
        """
        log_id = "HL7-FHIR-{}".format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))
        start_time = datetime.utcnow()

        try:
            # Extract MSH segment
            msh = hl7_message.get("MSH", {})
            pid = hl7_message.get("PID", {})
            pv1 = hl7_message.get("PV1", {})

            # Build FHIR Patient resource
            patient_resource = {
                "resourceType": "Patient",
                "id": self._generate_id(),
                "identifier": self._transform_identifiers(pid),
                "name": self._transform_names(pid),
                "telecom": self._transform_telecom(pid),
                "gender": self._transform_gender(pid),
                "birthDate": self._transform_birth_date(pid),
                "address": self._transform_address(pid),
                "maritalStatus": self._transform_marital_status(pid),
                "contact": self._transform_contact(pid),
                "communication": self._transform_communication(pid)
            }

            # Add extension fields if present
            if pid.get("PD1"):
                patient_resource["extension"] = self._transform_pd1_extensions(pid.get("PD1"))

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log transformation
            await self._log_transformation(
                log_id,
                hl7_message,
                patient_resource,
                "ADT^A04",
                TransformationDirection.HL7_TO_FHIR,
                processing_time
            )

            return patient_resource

        except Exception as e:
            logger.error("Error transforming ADT to Patient: {}".format(e))
            raise

    async def transform_orm_to_service_request(
        self,
        hl7_message: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform HL7 ORM message to FHIR ServiceRequest resource

        Args:
            hl7_message: Parsed HL7 message
            config: Optional transformation config

        Returns:
            FHIR ServiceRequest resource
        """
        log_id = "HL7-FHIR-{}".format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))
        start_time = datetime.utcnow()

        try:
            # Extract segments
            msh = hl7_message.get("MSH", {})
            pid = hl7_message.get("PID", {})
            pv1 = hl7_message.get("PV1", {})
            orc = hl7_message.get("ORC", {})
            obr = hl7_message.get("OBR", {})
            rxo = hl7_message.get("RXO", {})  # Pharmacy order segment

            # Build FHIR ServiceRequest resource
            service_request = {
                "resourceType": "ServiceRequest",
                "id": self._generate_id(),
                "identifier": self._transform_order_identifiers(orc, obr),
                "status": self._transform_order_status(orc),
                "intent": "order",
                "category": self._transform_order_category(obr),
                "priority": self._transform_order_priority(obr),
                "code": self._transform_order_code(obr),
                "orderDetail": self._transform_order_detail(rxo) if rxo else [],
                "subject": self._build_patient_reference(pid),
                "encounter": self._build_encounter_reference(pv1),
                "occurrenceDateTime": self._transform_order_date(obr),
                "authoredOn": self._transform_authored_on(orc),
                "requester": self._build_requester_reference(pv1),
                "performer": self._build_performer_reference(pv1),
                "reasonCode": self._transform_reason_code(obr),
                "supportingInfo": self._transform_supporting_info(obr),
                "note": self._transform_order_notes(orc, obr)
            }

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log transformation
            await self._log_transformation(
                log_id,
                hl7_message,
                service_request,
                "ORM^O01",
                TransformationDirection.HL7_TO_FHIR,
                processing_time
            )

            return service_request

        except Exception as e:
            logger.error("Error transforming ORM to ServiceRequest: {}".format(e))
            raise

    async def transform_oru_to_observation(
        self,
        hl7_message: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform HL7 ORU message to FHIR Observation resources

        Args:
            hl7_message: Parsed HL7 message
            config: Optional transformation config

        Returns:
            Bundle of FHIR Observation resources
        """
        log_id = "HL7-FHIR-{}".format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))
        start_time = datetime.utcnow()

        try:
            msh = hl7_message.get("MSH", {})
            pid = hl7_message.get("PID", {})
            obr = hl7_message.get("OBR", {})
            obx_segments = hl7_message.get("OBX", [])

            # Build FHIR Bundle with multiple observations
            observations = []

            for obx in obx_segments:
                observation = {
                    "resourceType": "Observation",
                    "id": self._generate_id(),
                    "identifier": self._transform_observation_identifiers(obr, obx),
                    "status": self._transform_observation_status(obx),
                    "category": self._transform_observation_category(obr),
                    "code": self._transform_observation_code(obx),
                    "subject": self._build_patient_reference(pid),
                    "encounter": self._build_encounter_reference(hl7_message.get("PV1", {})),
                    "effectiveDateTime": self._transform_observation_datetime(obx),
                    "issued": self._transform_observation_issued(obr),
                    "valueQuantity": self._transform_observation_value(obx),
                    "interpretation": self._transform_observation_interpretation(obx),
                    "referenceRange": self._transform_reference_range(obx),
                    "note": self._transform_observation_notes(obx)
                }
                observations.append(observation)

            # Create diagnostic report if applicable
            diagnostic_report = None
            if obr:
                diagnostic_report = {
                    "resourceType": "DiagnosticReport",
                    "id": self._generate_id(),
                    "status": "final",
                    "code": self._transform_report_code(obr),
                    "subject": self._build_patient_reference(pid),
                    "encounter": self._build_encounter_reference(hl7_message.get("PV1", {})),
                    "effectiveDateTime": self._transform_report_datetime(obr),
                    "issued": self._transform_report_issued(obr),
                    "result": [
                        {"reference": "Observation/{}".format(obs["id"])}
                        for obs in observations
                    ]
                }

            bundle = {
                "resourceType": "Bundle",
                "type": "collection",
                "entry": []
            }

            for obs in observations:
                bundle["entry"].append({"resource": obs})

            if diagnostic_report:
                bundle["entry"].append({"resource": diagnostic_report})

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log transformation
            await self._log_transformation(
                log_id,
                hl7_message,
                bundle,
                "ORU^R01",
                TransformationDirection.HL7_TO_FHIR,
                processing_time
            )

            return bundle

        except Exception as e:
            logger.error("Error transforming ORU to Observation: {}".format(e))
            raise

    def _generate_id(self) -> str:
        """Generate unique resource ID"""
        import uuid
        return str(uuid.uuid4())

    def _transform_identifiers(self, pid: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform PID identifiers to FHIR identifiers"""
        identifiers = []

        # Patient ID (PID-3)
        if pid.get("patient_identifier_list"):
            for cx in pid["patient_identifier_list"]:
                identifier = {
                    "use": "usual",
                    "system": cx.get("assigning_authority", "urn:oid:2.16.840.1.113883.2.4.3.11"),
                    "value": cx.get("id_number", "")
                }
                if cx.get("identifier_type_code"):
                    identifier["type"] = {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": cx["identifier_type_code"]}]}
                identifiers.append(identifier)

        # Alternative IDs (PID-2)
        if pid.get("patient_id"):
            identifiers.append({
                "use": "old",
                "system": "urn:oid:2.16.840.1.113883.2.4.3.11",
                "value": pid["patient_id"]
            })

        return identifiers

    def _transform_names(self, pid: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform PID names to FHIR names"""
        names = []

        if pid.get("patient_name"):
            for xpn in pid["patient_name"]:
                name = {
                    "use": "official",
                    "family": xpn.get("family_name", ""),
                    "given": [xpn.get("given_name", "")] if xpn.get("given_name") else []
                }
                if xpn.get("name_type_code"):
                    name["use"] = self._map_name_type_code(xpn["name_type_code"])
                names.append(name)

        return names

    def _map_name_type_code(self, code: str) -> str:
        """Map HL7 name type code to FHIR name use"""
        mapping = {
            "L": "usual",
            "F": "official",
            "M": "maiden",
            "D": "nickname",
            "S": "official"
        }
        return mapping.get(code, "official")

    def _transform_telecom(self, pid: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform PID telecom to FHIR telecom"""
        telecom = []

        # Phone numbers (PID-13)
        if pid.get("phone_home"):
            telecom.append({"system": "phone", "value": pid["phone_home"], "use": "home"})
        if pid.get("phone_business"):
            telecom.append({"system": "phone", "value": pid["phone_business"], "use": "work"})

        # Email (PID-14)
        if pid.get("email"):
            telecom.append({"system": "email", "value": pid["email"]})

        return telecom

    def _transform_gender(self, pid: Dict[str, Any]) -> str:
        """Transform HL7 gender to FHIR gender"""
        hl7_gender = pid.get("administrative_sex", "")
        mapping = {
            "M": "male",
            "F": "female",
            "O": "other",
            "U": "unknown"
        }
        return mapping.get(hl7_gender, "unknown")

    def _transform_birth_date(self, pid: Dict[str, Any]) -> Optional[str]:
        """Transform HL7 birth date to FHIR birthDate"""
        dob = pid.get("date_of_birth")
        if dob:
            return dob.strftime("%Y-%m-%d")
        return None

    def _transform_address(self, pid: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform PID address to FHIR address"""
        addresses = []

        if pid.get("patient_address"):
            for xad in pid["patient_address"]:
                address = {
                    "use": self._map_address_type(xad.get("address_type", "")),
                    "line": [xad.get("street_address", "").strip()],
                    "city": xad.get("city", ""),
                    "district": xad.get("state_or_province", ""),
                    "state": xad.get("state_or_province", ""),
                    "postalCode": xad.get("zip_or_postal_code", ""),
                    "country": xad.get("country", "")
                }
                addresses.append(address)

        return addresses

    def _map_address_type(self, hl7_type: str) -> str:
        """Map HL7 address type to FHIR address use"""
        mapping = {
            "H": "home",
            "W": "work",
            "C": "temp",
            "BA": "old"
        }
        return mapping.get(hl7_type, "home")

    def _transform_marital_status(self, pid: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform HL7 marital status to FHIR maritalStatus"""
        marital_code = pid.get("marital_status")
        if marital_code:
            # Map HL7 marital status to FHIR
            mapping = {
                "S": "D",  # Never married -> Divorced (approximate)
                "M": "M",  # Married
                "D": "D",  # Divorced
                "W": "W",  # Widowed
                "A": "L",  # Separated -> Legally separated
                "P": "P",  # Domestic partner
                "U": "UNK"  # Unknown
            }
            fhir_code = mapping.get(marital_code, "UNK")

            return {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                    "code": fhir_code
                }]
            }
        return None

    def _transform_contact(self, pid: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform PID next of kin to FHIR contact"""
        contacts = []

        if pid.get("next_of_kin"):
            for nk1 in pid["next_of_kin"]:
                contact = {
                    "relationship": [{"text": nk1.get("relationship", "")}],
                    "name": {
                        "family": nk1.get("name", "")
                    },
                    "telecom": []
                }

                if nk1.get("phone_number"):
                    contact["telecom"].append({
                        "system": "phone",
                        "value": nk1["phone_number"]
                    })

                contacts.append(contact)

        return contacts

    def _transform_communication(self, pid: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform PID language to FHIR communication"""
        communications = []

        if pid.get("primary_language"):
            communications.append({
                "language": {
                    "coding": [{
                        "system": "urn:ietf:bcp:47",
                        "code": pid["primary_language"]
                    }]
                }
            })

        return communications

    def _transform_order_identifiers(
        self,
        orc: Dict[str, Any],
        obr: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Transform ORC/OBR identifiers to FHIR identifiers"""
        identifiers = []

        # Filler order number (ORC-4)
        if orc.get("filler_order_number"):
            identifiers.append({
                "system": "urn:oid:2.16.840.1.113883.2.4.3.11",
                "value": orc["filler_order_number"]
            })

        # Placer order number (ORC-3)
        if orc.get("placer_order_number"):
            identifiers.append({
                "system": "http://hospital.org/order-numbers",
                "value": orc["placer_order_number"]
            })

        return identifiers

    def _transform_order_status(self, orc: Dict[str, Any]) -> str:
        """Transform HL7 order status to FHIR status"""
        order_status = orc.get("order_status", "")
        mapping = {
            "CA": "completed",
            "CM": "in-progress",
            "IP": "in-progress",
            "SC": "completed",
            "DC": "cancelled",
            "ER": "entered-in-error"
        }
        return mapping.get(order_status, "unknown")

    def _transform_order_category(self, obr: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform OBR service section to FHIR category"""
        service_section = obr.get("service_section_code", {})
        if service_section:
            return [{
                "coding": [{
                    "system": service_section.get("coding_system", ""),
                    "code": service_section.get("code", ""),
                    "display": service_section.get("description", "")
                }]
            }]
        return []

    def _transform_order_priority(self, obr: Dict[str, Any]) -> str:
        """Transform OBR priority to FHIR priority"""
        priority = obr.get("priority", "")
        mapping = {
            "S": "stat",
            "A": "urgent",
            "R": "routine",
            "P": "asap"
        }
        return mapping.get(priority, "routine")

    def _transform_order_code(self, obr: Dict[str, Any]) -> Dict[str, Any]:
        """Transform OBR universal service ID to FHIR code"""
        service_id = obr.get("universal_service_id", {})
        return {
            "coding": [{
                "system": service_id.get("coding_system", ""),
                "code": service_id.get("code", ""),
                "display": service_id.get("description", "")
            }],
            "text": service_id.get("description", "")
        }

    def _transform_order_detail(self, rxo: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform RXO pharmacy order to FHIR orderDetail"""
        # Simplified implementation
        return []

    def _build_patient_reference(self, pid: Dict[str, Any]) -> Dict[str, str]:
        """Build FHIR patient reference"""
        patient_id = pid.get("patient_identifier_list", [{}])[0].get("id_number", "")
        return {"reference": "Patient/{}".format(patient_id)}

    def _build_encounter_reference(self, pv1: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Build FHIR encounter reference"""
        visit_number = pv1.get("visit_number", "")
        if visit_number:
            return {"reference": "Encounter/{}".format(visit_number)}
        return None

    def _transform_order_date(self, obr: Dict[str, Any]) -> Optional[str]:
        """Transform OBR date to FHIR occurrenceDateTime"""
        date_str = obr.get("observation_date")
        if date_str:
            return date_str
        return None

    def _transform_authored_on(self, orc: Dict[str, Any]) -> Optional[str]:
        """Transform ORC date to FHIR authoredOn"""
        date_str = orc.get("date_time_of_transaction")
        if date_str:
            return date_str
        return None

    def _build_requester_reference(self, pv1: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build FHIR requester reference"""
        attending_doctor = pv1.get("attending_doctor", "")
        if attending_doctor:
            return {"reference": "Practitioner/{}".format(attending_doctor)}
        return None

    def _build_performer_reference(self, pv1: Dict[str, Any]) -> Optional[List[Dict[str, str]]]:
        """Build FHIR performer reference"""
        performing_facility = pv1.get("performing_facility", "")
        if performing_facility:
            return [{"reference": "Organization/{}".format(performing_facility)}]
        return None

    def _transform_reason_code(self, obr: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Transform OBR reason to FHIR reasonCode"""
        reason = obr.get("reason_for_study", {})
        if reason:
            return [{
                "coding": [{
                    "system": reason.get("coding_system", ""),
                    "code": reason.get("code", ""),
                    "display": reason.get("description", "")
                }]
            }]
        return None

    def _transform_supporting_info(self, obr: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Transform OBR supporting info to FHIR supportingInfo"""
        # Simplified implementation
        return None

    def _transform_order_notes(
        self,
        orc: Dict[str, Any],
        obr: Dict[str, Any]
    ) -> Optional[List[Dict[str, Any]]]:
        """Transform ORC/OBR notes to FHIR notes"""
        notes = []

        if obr.get("comment", ""):
            notes.append({
                "authorReference": {"reference": "Practitioner/unknown"},
                "text": obr["comment"]
            })

        return notes if notes else None

    def _transform_observation_status(self, obx: Dict[str, Any]) -> str:
        """Transform OBX status to FHIR observation status"""
        result_status = obx.get("observation_result_status", "")
        mapping = {
            "F": "final",
            "P": "preliminary",
            "C": "corrected",
            "X": "cancelled",
            "I": "entered-in-error"
        }
        return mapping.get(result_status, "final")

    def _transform_observation_category(self, obr: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform OBR service section to FHIR observation category"""
        # Reuse order category transformation
        return self._transform_order_category(obr)

    def _transform_observation_code(self, obx: Dict[str, Any]) -> Dict[str, Any]:
        """Transform OBX identifier to FHIR observation code"""
        identifier = obx.get("observation_identifier", {})
        return {
            "coding": [{
                "system": identifier.get("coding_system", ""),
                "code": identifier.get("code", ""),
                "display": identifier.get("description", "")
            }],
            "text": identifier.get("description", "")
        }

    def _transform_observation_datetime(self, obx: Dict[str, Any]) -> Optional[str]:
        """Transform OBX datetime to FHIR effectiveDateTime"""
        date_str = obx.get("observation_date")
        if date_str:
            return date_str
        return None

    def _transform_observation_issued(self, obr: Dict[str, Any]) -> Optional[str]:
        """Transform OBR report date to FHIR issued"""
        date_str = obr.get("result_status_change_date")
        if date_str:
            return date_str
        return None

    def _transform_observation_value(self, obx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform OBX value to FHIR valueQuantity"""
        value_type = obx.get("value_type", "")
        observation_value = obx.get("observation_value", "")

        if value_type == "NM":  # Numeric
            return {
                "value": float(observation_value) if observation_value else 0,
                "unit": obx.get("units", ""),
                "system": "http://unitsofmeasure.org",
                "code": obx.get("units", "")
            }
        elif value_type == "ST":  # String
            return None  # Use valueString instead
        elif value_type == "TS":  # Timestamp
            return None  # Use valueDateTime instead

        return None

    def _transform_observation_interpretation(self, obx: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Transform OBX abnormal flags to FHIR interpretation"""
        flags = obx.get("abnormal_flags", "")
        if not flags:
            return None

        mapping = {
            "H": "H",
            "L": "L",
            "N": "N",
            "A": "A",
            "HH": "HH",
            "LL": "LL"
        }

        code = mapping.get(flags[0], "N")

        return [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": code
            }]
        }]

    def _transform_reference_range(self, obx: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Transform OBX reference range to FHIR referenceRange"""
        if obx.get("reference_range"):
            return [{
                "low": {"value": obx["reference_range"].get("low", "")},
                "high": {"value": obx["reference_range"].get("high", "")},
                "text": obx["reference_range"].get("text", "")
            }]
        return None

    def _transform_observation_notes(self, obx: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """Transform OBX notes to FHIR observation notes"""
        # Simplified implementation
        return None

    def _transform_report_code(self, obr: Dict[str, Any]) -> Dict[str, Any]:
        """Transform OBR service ID to FHIR diagnostic report code"""
        service_id = obr.get("universal_service_id", {})
        return {
            "coding": [{
                "system": service_id.get("coding_system", ""),
                "code": service_id.get("code", ""),
                "display": service_id.get("description", "")
            }],
            "text": service_id.get("description", "")
        }

    def _transform_report_datetime(self, obr: Dict[str, Any]) -> Optional[str]:
        """Transform OBR observation date to FHIR effectiveDateTime"""
        date_str = obr.get("observation_date")
        if date_str:
            return date_str
        return None

    def _transform_report_issued(self, obr: Dict[str, Any]) -> Optional[str]:
        """Transform OBR report status date to FHIR issued"""
        date_str = obr.get("result_status_change_date")
        if date_str:
            return date_str
        return None

    def _transform_observation_identifiers(
        self,
        obr: Dict[str, Any],
        obx: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Transform OBR/OBX identifiers to FHIR identifiers"""
        identifiers = []

        # Use filler order number
        if obr.get("filler_order_number"):
            identifiers.append({
                "system": "urn:oid:2.16.840.1.113883.2.4.3.11",
                "value": obr["filler_order_number"]
            })

        return identifiers

    def _transform_pd1_extensions(self, pd1: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform PD1 segment to FHIR extensions"""
        extensions = []

        # Living arrangement (PD1-2)
        if pd1.get("living_arrangement"):
            extensions.append({
                "url": "http://hl7.org/fhir/StructureDefinition/patient-livingArrangement",
                "valueCodeableConcept": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0442",
                        "code": pd1["living_arrangement"]
                    }]
                }
            })

        return extensions

    async def _log_transformation(
        self,
        log_id: str,
        input_message: Dict[str, Any],
        output_message: Dict[str, Any],
        transformation_type: str,
        direction: str,
        processing_time_ms: int
    ) -> None:
        """Log transformation to database"""
        try:
            log = TransformationLog(
                log_id=log_id,
                source_format="HL7" if direction == TransformationDirection.HL7_TO_FHIR else "FHIR",
                target_format="FHIR" if direction == TransformationDirection.HL7_TO_FHIR else "HL7",
                transformation_type=transformation_type,
                input_message=input_message,
                output_message=output_message,
                status="success",
                processing_time_ms=processing_time_ms
            )
            self.db.add(log)
            await self.db.commit()

        except Exception as e:
            logger.error("Error logging transformation: {}".format(e))
            await self.db.rollback()


# =============================================================================
# FHIR to HL7 Transformer
# =============================================================================

class FHIRToHL7Transformer(object):
    """FHIR to HL7 message transformer

    Transforms FHIR R4 resources to HL7 v2.x messages.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def transform_patient_to_adt(
        self,
        fhir_resource: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform FHIR Patient resource to HL7 ADT message

        Args:
            fhir_resource: FHIR Patient resource
            config: Optional transformation config

        Returns:
            HL7 ADT message (A04)
        """
        log_id = "FHIR-HL7-{}".format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))
        start_time = datetime.utcnow()

        try:
            # Build HL7 message segments
            msh = self._build_msh_segment("ADT^A04")
            pid = self._build_pid_from_patient(fhir_resource)
            pv1 = self._build_pv1_segment()

            hl7_message = {
                "MSH": msh,
                "PID": pid,
                "PV1": pv1
            }

            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Log transformation
            await self._log_transformation(
                log_id,
                fhir_resource,
                hl7_message,
                "Patient",
                TransformationDirection.FHIR_TO_HL7,
                processing_time
            )

            return hl7_message

        except Exception as e:
            logger.error("Error transforming Patient to ADT: {}".format(e))
            raise

    def _build_msh_segment(self, message_type: str) -> Dict[str, Any]:
        """Build MSH segment"""
        return {
            "encoding_characters": "^~\\&",
            "sending_application": "SIMRS",
            "sending_facility": "HOSPITAL",
            "receiving_application": "EXTERNAL",
            "receiving_facility": "EXTERNAL",
            "date_time_of_message": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "message_type": message_type,
            "message_control_id": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
            "processing_id": "P",
            "version_id": "2.5"
        }

    def _build_pid_from_patient(self, patient: Dict[str, Any]) -> Dict[str, Any]:
        """Build PID segment from FHIR Patient resource"""
        pid = {}

        # Patient identifiers (PID-3)
        if patient.get("identifier"):
            pid["patient_identifier_list"] = []
            for identifier in patient["identifier"]:
                cx = {
                    "id_number": identifier.get("value", ""),
                    "assigning_authority": identifier.get("system", ""),
                    "identifier_type_code": "MR"
                }
                pid["patient_identifier_list"].append(cx)

        # Patient name (PID-5)
        if patient.get("name"):
            pid["patient_name"] = []
            for name in patient["name"]:
                xpn = {
                    "family_name": name.get("family", ""),
                    "given_name": name.get("given", [""])[0] if name.get("given") else "",
                    "name_type_code": self._map_fhir_name_use_to_hl7(name.get("use", "official"))
                }
                pid["patient_name"].append(xpn)

        # Patient DOB (PID-7)
        if patient.get("birthDate"):
            dob_str = patient["birthDate"]
            try:
                pid["date_of_birth"] = datetime.strptime(dob_str, "%Y-%m-%d")
            except ValueError:
                pass

        # Patient sex (PID-8)
        if patient.get("gender"):
            pid["administrative_sex"] = self._map_fhir_gender_to_hl7(patient["gender"])

        # Patient address (PID-11)
        if patient.get("address"):
            pid["patient_address"] = []
            for address in patient["address"]:
                xad = {
                    "street_address": address.get("line", [""])[0] if address.get("line") else "",
                    "city": address.get("city", ""),
                    "state_or_province": address.get("state", ""),
                    "zip_or_postal_code": address.get("postalCode", ""),
                    "country": address.get("country", ""),
                    "address_type": self._map_fhir_address_use_to_hl7(address.get("use", "home"))
                }
                pid["patient_address"].append(xad)

        # Phone numbers (PID-13, PID-14)
        if patient.get("telecom"):
            for telecom in patient["telecom"]:
                if telecom.get("system") == "phone":
                    if telecom.get("use") == "home":
                        pid["phone_home"] = telecom["value"]
                    elif telecom.get("use") == "work":
                        pid["phone_business"] = telecom["value"]
                elif telecom.get("system") == "email":
                    pid["email"] = telecom["value"]

        return pid

    def _build_pv1_segment(self) -> Dict[str, Any]:
        """Build PV1 segment"""
        return {
            "patient_class": "O",
            "visit_number": "",
            "attending_doctor": "",
            "performing_facility": ""
        }

    def _map_fhir_name_use_to_hl7(self, fhir_use: str) -> str:
        """Map FHIR name use to HL7 name type code"""
        mapping = {
            "usual": "L",
            "official": "F",
            "maiden": "M",
            "nickname": "D",
            "anonymous": "S",
            "old": "BA"
        }
        return mapping.get(fhir_use, "F")

    def _map_fhir_gender_to_hl7(self, fhir_gender: str) -> str:
        """Map FHIR gender to HL7 administrative sex"""
        mapping = {
            "male": "M",
            "female": "F",
            "other": "O",
            "unknown": "U"
        }
        return mapping.get(fhir_gender, "U")

    def _map_fhir_address_use_to_hl7(self, fhir_use: str) -> str:
        """Map FHIR address use to HL7 address type"""
        mapping = {
            "home": "H",
            "work": "W",
            "temp": "C",
            "old": "BA"
        }
        return mapping.get(fhir_use, "H")

    async def _log_transformation(
        self,
        log_id: str,
        input_message: Dict[str, Any],
        output_message: Dict[str, Any],
        transformation_type: str,
        direction: str,
        processing_time_ms: int
    ) -> None:
        """Log transformation to database"""
        try:
            log = TransformationLog(
                log_id=log_id,
                source_format="FHIR" if direction == TransformationDirection.FHIR_TO_HL7 else "HL7",
                target_format="HL7" if direction == TransformationDirection.FHIR_TO_HL7 else "FHIR",
                transformation_type=transformation_type,
                input_message=input_message,
                output_message=output_message,
                status="success",
                processing_time_ms=processing_time_ms
            )
            self.db.add(log)
            await self.db.commit()

        except Exception as e:
            logger.error("Error logging transformation: {}".format(e))
            await self.db.rollback()


# =============================================================================
# Main Transformation Service
# =============================================================================

class TransformationService(object):
    """Main transformation service

    Coordinates all message transformation operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.hl7_to_fhir = HL7ToFHIRTransformer(db)
        self.fhir_to_hl7 = FHIRToHL7Transformer(db)

    # HL7 to FHIR transformations
    async def transform_hl7_adt_to_fhir_patient(
        self,
        hl7_message: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform HL7 ADT message to FHIR Patient resource"""
        return await self.hl7_to_fhir.transform_adt_to_patient(hl7_message, config)

    async def transform_hl7_orm_to_fhir_service_request(
        self,
        hl7_message: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform HL7 ORM message to FHIR ServiceRequest resource"""
        return await self.hl7_to_fhir.transform_orm_to_service_request(hl7_message, config)

    async def transform_hl7_oru_to_fhir_observation(
        self,
        hl7_message: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform HL7 ORU message to FHIR Observation resources"""
        return await self.hl7_to_fhir.transform_oru_to_observation(hl7_message, config)

    # FHIR to HL7 transformations
    async def transform_fhir_patient_to_hl7_adt(
        self,
        fhir_resource: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Transform FHIR Patient resource to HL7 ADT message"""
        return await self.fhir_to_hl7.transform_patient_to_adt(fhir_resource, config)

    # History and statistics
    async def get_transformation_history(
        self,
        limit: int = 50,
        transformation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get transformation history"""
        try:
            query = select(TransformationLog)

            filters = []
            if transformation_type:
                filters.append(TransformationLog.transformation_type == transformation_type)

            if filters:
                query = query.where(and_(*filters))

            query = query.order_by(TransformationLog.transformed_at.desc()).limit(limit)

            result = await self.db.execute(query)
            logs = result.scalars().all()

            return [
                {
                    "log_id": log.log_id,
                    "source_format": log.source_format,
                    "target_format": log.target_format,
                    "transformation_type": log.transformation_type,
                    "status": log.status,
                    "processing_time_ms": log.processing_time_ms,
                    "transformed_at": log.transformed_at.isoformat()
                }
                for log in logs
            ]

        except Exception as e:
            logger.error("Error getting transformation history: {}".format(e))
            raise
