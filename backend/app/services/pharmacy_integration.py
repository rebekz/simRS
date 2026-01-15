"""Pharmacy Integration Service for STORY-024-08

This module provides services for:
- Electronic prescription transmission
- Medication dispensing workflows
- Refill request management
- Pharmacy inventory synchronization
- Drug interaction checking

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.pharmacy_integration import (
    PharmacySystem, PrescriptionTransmission, MedicationDispense, RefillRequest,
    PharmacyInventorySync, DrugInteractionCheck,
    PrescriptionStatus, DispenseStatus
)


logger = logging.getLogger(__name__)


class NCPDPBuilder(object):
    """Builds NCPDP (National Council for Prescription Drug Programs) scripts"""

    def __init__(self):
        pass

    def build_ncpdp_script(
        self,
        prescription_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """Build NCPDP NewRx script

        Args:
            prescription_data: Prescription data
            config: NCPDP configuration

        Returns:
            NCPDP script content
        """
        try:
            # This is a simplified NCPDP builder
            # In production, use a proper NCPDP library

            segments = []

            # Segment Group Header
            segments.append("~{MSH|^~\\&|SENDERID|RECEIVERID|{}|{}|NEWRX^TAMPER_EVIDENT~".format(
                datetime.utcnow().strftime("%Y%m%d%H%M%S"),
                config.get("control_number", "1234")
            ))

            # Patient Segment
            segments.append("~{PAT||{}|{}|{}|{}|{}|{}||||{}||||{}~".format(
                prescription_data.get("patient_id"),
                prescription_data.get("patient_last_name"),
                prescription_data.get("patient_first_name"),
                prescription_data.get("patient_dob").replace("-", "") if prescription_data.get("patient_dob") else "",
                prescription_data.get("patient_gender"),
                prescription_data.get("patient_address", {}).get("street"),
                prescription_data.get("patient_address", {}).get("city"),
                prescription_data.get("patient_address", {}).get("state"),
                prescription_data.get("patient_address", {}).get("zip")
            ))

            # Prescriber Segment
            segments.append("~{PRESCRIBER||{}|{}|{}|{}|{}~".format(
                prescription_data.get("prescriber_id"),
                prescription_data.get("prescriber_last_name"),
                prescription_data.get("prescriber_first_name"),
                prescription_data.get("prescriber_npi"),
                prescription_data.get("prescriber_dea"),
                prescription_data.get("prescriber_phone")
            ))

            # Medication Segment
            segments.append("~{DRUG||{}|{}|{}|{}|{}|{}~".format(
                prescription_data.get("medication_code"),
                prescription_data.get("medication_name"),
                prescription_data.get("generic_name"),
                prescription_data.get("dosage_form"),
                prescription_data.get("strength"),
                prescription_data.get("strength_unit")
            ))

            # Prescription Segment
            segments.append("~{PRESCRIPTION||{}|{}|{}|{}|{}|{}~".format(
                prescription_data.get("prescription_number"),
                prescription_data.get("quantity"),
                prescription_data.get("quantity_unit"),
                prescription_data.get("days_supply"),
                prescription_data.get("refills"),
                prescription_data.get("sig_text")
            ))

            # Combine segments
            script_content = "".join(segments)

            return script_content

        except Exception as e:
            logger.error("Error building NCPDP script: {}".format(e))
            raise ValueError("Failed to build NCPDP script: {}".format(str(e)))


class FHIRMedicationRequestBuilder(object):
    """Builds FHIR MedicationRequest resources"""

    def __init__(self):
        pass

    def build_medication_request(
        self,
        prescription_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build FHIR MedicationRequest resource

        Args:
            prescription_data: Prescription data

        Returns:
            FHIR MedicationRequest resource
        """
        try:
            resource = {
                "resourceType": "MedicationRequest",
                "id": "MedicationRequest-{}".format(prescription_data.get("prescription_number")),
                "status": "active",
                "intent": "order",
                "medicationCodeableConcept": {
                    "coding": [{
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": prescription_data.get("medication_code"),
                        "display": prescription_data.get("medication_name")
                    }],
                    "text": prescription_data.get("medication_name")
                },
                "subject": {
                    "reference": "Patient/{}".format(prescription_data.get("patient_id"))
                },
                "authoredOn": prescription_data.get("prescribed_date", datetime.utcnow().isoformat()),
                "requester": {
                    "reference": "Practitioner/{}".format(prescription_data.get("prescriber_id")),
                    "display": prescription_data.get("prescriber_name")
                },
                "dosageInstruction": [{
                    "text": prescription_data.get("sig_text"),
                    "route": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v3-RouteOfAdministration",
                            "code": prescription_data.get("route_code", "PO"),
                            "display": prescription_data.get("route", "Oral")
                        }]
                    },
                    "doseQuantity": {
                        "value": prescription_data.get("dose_quantity", 1),
                        "unit": prescription_data.get("dose_unit", "tab")
                    },
                    "timing": {
                        "repeat": {
                            "frequency": prescription_data.get("frequency")
                        }
                    }
                }],
                "dispenseRequest": {
                    "quantity": {
                        "value": prescription_data.get("quantity"),
                        "unit": prescription_data.get("quantity_unit")
                    },
                    "numberOfRepeatsAllowed": prescription_data.get("refills", 0)
                }
            }

            return resource

        except Exception as e:
            logger.error("Error building FHIR MedicationRequest: {}".format(e))
            raise ValueError("Failed to build FHIR MedicationRequest: {}".format(str(e)))


class PharmacyIntegrationService(object):
    """Service for pharmacy integration"""

    def __init__(self, db):
        self.db = db
        self.ncpdp_builder = NCPDPBuilder()
        self.fhir_builder = FHIRMedicationRequestBuilder()

    # ==========================================================================
    # Pharmacy System Management
    # ==========================================================================

    async def register_pharmacy_system(
        self,
        system_code: str,
        system_name: str,
        system_type: str,
        protocol: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Register external pharmacy system

        Args:
            system_code: System code
            system_name: System name
            system_type: System type (hospital, retail, mail_order)
            protocol: Communication protocol
            **kwargs: Additional system attributes

        Returns:
            Dict with system details
        """
        try:
            system = PharmacySystem(
                system_id="PHARM-{}".format(system_code),
                system_code=system_code,
                system_name=system_name,
                system_type=system_type,
                organization=kwargs.get("organization"),
                pharmacy_id=kwargs.get("pharmacy_id"),
                license_number=kwargs.get("license_number"),
                contact_name=kwargs.get("contact_name"),
                contact_email=kwargs.get("contact_email"),
                contact_phone=kwargs.get("contact_phone"),
                address=kwargs.get("address"),
                protocol=protocol,
                endpoint_url=kwargs.get("endpoint_url"),
                auth_type=kwargs.get("auth_type"),
                auth_credentials=kwargs.get("auth_credentials"),
                ncpdp_config=kwargs.get("ncpdp_config"),
                edi_config=kwargs.get("edi_config"),
                mapping_config=kwargs.get("mapping_config"),
                supported_formats=kwargs.get("supported_formats"),
                supports_e_prescribing=kwargs.get("supports_e_prescribing", False),
                supports_dispensing=kwargs.get("supports_dispensing", False),
                supports_inventory_sync=kwargs.get("supports_inventory_sync", False),
                supports_refill_requests=kwargs.get("supports_refill_requests", False),
                formulary_id=kwargs.get("formulary_id"),
                is_primary=kwargs.get("is_primary", False),
                test_mode=kwargs.get("test_mode", False)
            )

            self.db.add(system)
            await self.db.commit()

            logger.info("Registered pharmacy system: {}".format(system.system_id))

            return {
                "system_id": system.system_id,
                "system_code": system.system_code,
                "system_name": system.system_name,
                "status": system.status
            }

        except Exception as e:
            logger.error("Error registering pharmacy system: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to register pharmacy system: {}".format(str(e)))

    # ==========================================================================
    # Prescription Transmission
    # ==========================================================================

    async def transmit_prescription(
        self,
        prescription_id: int,
        pharmacy_system_id: int,
        prescription_data: Dict[str, Any],
        transmitted_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Transmit prescription to pharmacy system

        Args:
            prescription_id: Prescription ID
            pharmacy_system_id: Pharmacy system ID
            prescription_data: Prescription data
            transmitted_by: User ID

        Returns:
            Dict with transmission details
        """
        try:
            # Get pharmacy system
            system_query = select(PharmacySystem).where(PharmacySystem.id == pharmacy_system_id)
            system_result = await self.db.execute(system_query)
            system = system_result.scalar_one_or_none()

            if not system:
                raise ValueError("Pharmacy system {} not found".format(pharmacy_system_id))

            # Generate prescription number
            prescription_number = "RX-{}-{}".format(prescription_id, datetime.utcnow().strftime("%Y%m%d%H%M%S"))

            # Build NCPDP script if supported
            ncpdp_content = None
            if "NCPDP" in system.supported_formats or system.supports_e_prescribing:
                ncpdp_content = self.ncpdp_builder.build_ncpdp_script(
                    prescription_data,
                    system.ncpdp_config or {}
                )

            # Build FHIR resource if supported
            fhir_resource = None
            if "FHIR" in system.supported_formats:
                fhir_resource = self.fhir_builder.build_medication_request(prescription_data)

            # Create transmission record
            transmission = PrescriptionTransmission(
                transmission_id="TX-{}-{}".format(system.system_code, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                prescription_number=prescription_number,
                pharmacy_system_id=pharmacy_system_id,
                prescription_id=prescription_id,
                patient_id=prescription_data.get("patient_id"),
                encounter_id=prescription_data.get("encounter_id"),
                prescriber_id=prescription_data.get("prescriber_id"),
                prescriber_npi=prescription_data.get("prescriber_npi"),
                prescriber_dea=prescription_data.get("prescriber_dea"),
                patient_name=prescription_data.get("patient_name"),
                patient_dob=prescription_data.get("patient_dob"),
                patient_gender=prescription_data.get("patient_gender"),
                patient_address=prescription_data.get("patient_address"),
                primary_payer=prescription_data.get("primary_payer"),
                insurance_member_id=prescription_data.get("insurance_member_id"),
                insurance_group_number=prescription_data.get("insurance_group_number"),
                medication_id=prescription_data.get("medication_id"),
                medication_name=prescription_data.get("medication_name"),
                medication_code=prescription_data.get("medication_code"),
                generic_name=prescription_data.get("generic_name"),
                dosage_form=prescription_data.get("dosage_form"),
                strength=prescription_data.get("strength"),
                strength_unit=prescription_data.get("strength_unit"),
                quantity=prescription_data.get("quantity"),
                quantity_unit=prescription_data.get("quantity_unit"),
                days_supply=prescription_data.get("days_supply"),
                refills=prescription_data.get("refills", 0),
                refills_remaining=prescription_data.get("refills", 0),
                sig_text=prescription_data.get("sig_text"),
                dosage_instructions=prescription_data.get("dosage_instructions"),
                route=prescription_data.get("route"),
                frequency=prescription_data.get("frequency"),
                diagnosis_code=prescription_data.get("diagnosis_code"),
                diagnosis_description=prescription_data.get("diagnosis_description"),
                clinical_notes=prescription_data.get("clinical_notes"),
                prescription_data=prescription_data,
                ncpdp_script_content=ncpdp_content,
                fhir_resource=fhir_resource,
                status=PrescriptionStatus.SENT_TO_PHARMACY,
                sent_at=datetime.utcnow(),
                test_mode=system.test_mode
            )

            self.db.add(transmission)
            await self.db.commit()

            logger.info("Transmitted prescription: {}".format(transmission.prescription_number))

            return {
                "transmission_id": transmission.transmission_id,
                "prescription_number": transmission.prescription_number,
                "status": transmission.status,
                "sent_at": transmission.sent_at.isoformat()
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error transmitting prescription: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to transmit prescription: {}".format(str(e)))

    # ==========================================================================
    # Dispense Tracking
    # ==========================================================================

    async def record_dispense(
        self,
        prescription_transmission_id: int,
        dispense_data: Dict[str, Any],
        pharmacy_system_id: int
    ) -> Dict[str, Any]:
        """Record medication dispense from pharmacy

        Args:
            prescription_transmission_id: Prescription transmission ID
            dispense_data: Dispense data
            pharmacy_system_id: Pharmacy system ID

        Returns:
            Dict with dispense details
        """
        try:
            # Get prescription transmission
            query = select(PrescriptionTransmission).where(
                PrescriptionTransmission.id == prescription_transmission_id
            )
            result = await self.db.execute(query)
            transmission = result.scalar_one_or_none()

            if not transmission:
                raise ValueError("Prescription transmission {} not found".format(prescription_transmission_id))

            # Create dispense record
            dispense = MedicationDispense(
                dispense_id="DSP-{}-{}".format(
                    transmission.prescription_number,
                    datetime.utcnow().strftime("%Y%m%d%H%M%S")
                ),
                prescription_transmission_id=prescription_transmission_id,
                pharmacy_system_id=pharmacy_system_id,
                patient_id=transmission.patient_id,
                medication_id=transmission.medication_id,
                dispense_number=dispense_data.get("dispense_number"),
                dispense_date=dispense_data.get("dispense_date", datetime.utcnow()),
                quantity_dispensed=dispense_data.get("quantity_dispensed", transmission.quantity),
                days_supply=dispense_data.get("days_supply", transmission.days_supply),
                refills_remaining=transmission.refills_remaining - 1,
                medication_name=transmission.medication_name,
                medication_code=transmission.medication_code,
                dosage_form=transmission.dosage_form,
                strength=transmission.strength,
                strength_unit=transmission.strength_unit,
                dispenser_id=dispense_data.get("dispenser_id"),
                dispenser_name=dispense_data.get("dispenser_name"),
                pharmacy_id=dispense_data.get("pharmacy_id"),
                cost=dispense_data.get("cost"),
                price=dispense_data.get("price"),
                copay=dispense_data.get("copay"),
                status=DispenseStatus.DISPENSED,
                lot_number=dispense_data.get("lot_number"),
                expiration_date=dispense_data.get("expiration_date"),
                ndc=dispense_data.get("ndc"),
                dea_schedule=dispense_data.get("dea_schedule"),
                dispense_notes=dispense_data.get("dispense_notes"),
                patient_counseling=dispense_data.get("patient_counseling")
            )

            self.db.add(dispense)

            # Update transmission status
            if dispense.quantity_dispensed >= transmission.quantity:
                transmission.status = PrescriptionStatus.DISPENSED
            else:
                transmission.status = PrescriptionStatus.PARTIALLY_DISPENSED

            transmission.dispensed_at = dispense.dispense_date
            transmission.quantity_dispensed = (transmission.quantity_dispensed or 0) + dispense.quantity_dispensed
            transmission.partial_dispense_count += 1

            await self.db.commit()

            logger.info("Recorded dispense: {}".format(dispense.dispense_id))

            return {
                "dispense_id": dispense.dispense_id,
                "status": dispense.status,
                "dispense_date": dispense.dispense_date.isoformat()
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error recording dispense: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to record dispense: {}".format(str(e)))

    # ==========================================================================
    # Refill Management
    # ==========================================================================

    async def request_refill(
        self,
        prescription_transmission_id: int,
        refill_data: Dict[str, Any],
        pharmacy_system_id: int,
        requested_by: int
    ) -> Dict[str, Any]:
        """Request prescription refill

        Args:
            prescription_transmission_id: Prescription transmission ID
            refill_data: Refill data
            pharmacy_system_id: Pharmacy system ID
            requested_by: User ID

        Returns:
            Dict with refill request details
        """
        try:
            # Get prescription transmission
            query = select(PrescriptionTransmission).where(
                PrescriptionTransmission.id == prescription_transmission_id
            )
            result = await self.db.execute(query)
            transmission = result.scalar_one_or_none()

            if not transmission:
                raise ValueError("Prescription transmission {} not found".format(prescription_transmission_id))

            # Check if refills available
            if transmission.refills_remaining <= 0:
                raise ValueError("No refills remaining for prescription {}".format(
                    transmission.prescription_number
                ))

            # Calculate refill number
            refill_number = transmission.refills - transmission.refills_remaining + 1

            # Create refill request
            request = RefillRequest(
                request_id="RF-{}-{}".format(
                    transmission.prescription_number,
                    datetime.utcnow().strftime("%Y%m%d%H%M%S")
                ),
                prescription_transmission_id=prescription_transmission_id,
                pharmacy_system_id=pharmacy_system_id,
                patient_id=transmission.patient_id,
                requested_by=requested_by,
                refill_number=refill_number,
                quantity_requested=transmission.quantity,
                reason=refill_data.get("reason"),
                status="pending",
                submitted_at=datetime.utcnow()
            )

            self.db.add(request)
            await self.db.commit()

            logger.info("Created refill request: {}".format(request.request_id))

            return {
                "request_id": request.request_id,
                "refill_number": refill_number,
                "status": request.status,
                "submitted_at": request.submitted_at.isoformat()
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error requesting refill: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to request refill: {}".format(str(e)))

    # ==========================================================================
    # Drug Interaction Checking
    # ==========================================================================

    async def check_drug_interactions(
        self,
        medication_ids: List[int],
        patient_id: int,
        pharmacy_system_id: int,
        prescription_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Check drug interactions through pharmacy system

        Args:
            medication_ids: Medication IDs to check
            patient_id: Patient ID
            pharmacy_system_id: Pharmacy system ID
            prescription_id: Prescription ID (optional)

        Returns:
            Dict with interaction check results
        """
        try:
            from app.models.medication import Medication

            # Get medication details
            medication_query = select(Medication).where(
                Medication.id.in_(medication_ids)
            )
            med_result = await self.db.execute(medication_query)
            medications = med_result.scalars().all()

            medication_names = [m.name for m in medications]

            # Check interactions locally first
            local_interactions = await self._check_local_interactions(medication_ids, patient_id)

            # Create interaction check record
            check = DrugInteractionCheck(
                check_id="DI-{}-{}".format(patient_id, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                pharmacy_system_id=pharmacy_system_id,
                patient_id=patient_id,
                prescription_id=prescription_id,
                medication_ids=medication_ids,
                medication_names=medication_names,
                interaction_count=len(local_interactions),
                interactions=local_interactions,
                severity_levels=self._calculate_severity_levels(local_interactions),
                has_contraindications=any(i.get("severity") == "contraindicated" for i in local_interactions),
                has_major_interactions=any(i.get("severity") == "major" for i in local_interactions),
                has_moderate_interactions=any(i.get("severity") == "moderate" for i in local_interactions),
                requires_review=len(local_interactions) > 0,
                checked_at=datetime.utcnow()
            )

            self.db.add(check)
            await self.db.commit()

            logger.info("Drug interaction check completed: {} interactions".format(len(local_interactions)))

            return {
                "check_id": check.check_id,
                "interaction_count": check.interaction_count,
                "interactions": local_interactions,
                "has_contraindications": check.has_contraindications,
                "has_major_interactions": check.has_major_interactions,
                "requires_review": check.requires_review
            }

        except Exception as e:
            logger.error("Error checking drug interactions: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to check drug interactions: {}".format(str(e)))

    async def _check_local_interactions(
        self,
        medication_ids: List[int],
        patient_id: int
    ) -> List[Dict[str, Any]]:
        """Check drug interactions locally

        Args:
            medication_ids: Medication IDs
            patient_id: Patient ID

        Returns:
            List of interactions
        """
        try:
            from app.models.drug_interactions import DrugInteraction

            # Get interactions for medication combinations
            interactions = []

            for i in range(len(medication_ids)):
                for j in range(i + 1, len(medication_ids)):
                    # Check if interaction exists
                    query = select(DrugInteraction).where(
                        and_(
                            DrugInteraction.medication_1_id == medication_ids[i],
                            DrugInteraction.medication_2_id == medication_ids[j]
                        )
                    )
                    result = await self.db.execute(query)
                    interaction = result.scalar_one_or_none()

                    if interaction:
                        interactions.append({
                            "medication_1": interaction.medication_1_name,
                            "medication_2": interaction.medication_2_name,
                            "severity": interaction.severity,
                            "description": interaction.description,
                            "recommendation": interaction.recommendation
                        })

            return interactions

        except Exception as e:
            logger.error("Error checking local interactions: {}".format(e))
            return []

    def _calculate_severity_levels(self, interactions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate severity level counts

        Args:
            interactions: List of interactions

        Returns:
            Dict with severity counts
        """
        severity_levels = {
            "contraindicated": 0,
            "major": 0,
            "moderate": 0,
            "minor": 0
        }

        for interaction in interactions:
            severity = interaction.get("severity", "minor").lower()
            if "contraindicated" in severity:
                severity_levels["contraindicated"] += 1
            elif "major" in severity:
                severity_levels["major"] += 1
            elif "moderate" in severity:
                severity_levels["moderate"] += 1
            else:
                severity_levels["minor"] += 1

        return severity_levels


def get_pharmacy_integration_service(db):
    """Get or create pharmacy integration service instance

    Args:
        db: Database session

    Returns:
        PharmacyIntegrationService instance
    """
    return PharmacyIntegrationService(db)
