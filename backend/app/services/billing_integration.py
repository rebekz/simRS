"""Billing System Integration Service for STORY-024-07

This module provides services for:
- Claims submission to billing systems
- Payment reconciliation
- EDI 837/835 processing
- Insurance company integration

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.billing_integration import (
    BillingSystem, ClaimSubmission, ClaimPayment, ClaimAdjustment,
    RemittanceAdvice, ClaimAttachment, ClaimStatus, PaymentStatus
)


logger = logging.getLogger(__name__)


class EDI837Builder(object):
    """Builds EDI 837 (professional/institutional claim) format"""

    def __init__(self):
        pass

    def build_837_professional(
        self,
        claim_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """Build EDI 837 Professional claim

        Args:
            claim_data: Claim data
            config: Billing configuration

        Returns:
            EDI 837 Professional formatted string
        """
        try:
            # This is a simplified EDI 837 builder
            # In production, use a proper EDI library

            segments = []

            # ISA Interchange Control Header
            segments.append("ISA*00*          *00*          *ZZ*SENDERID*ZZ*RECEIVERID*{}*{}*^*00501*{}*0*P*>~".format(
                datetime.utcnow().strftime("%Y%m%d"),
                datetime.utcnow().strftime("%H%M"),
                datetime.utcnow().strftime("%Y%m%d%H%M")
            ))

            # GS Functional Group Header
            segments.append("GS*HC*SENDERID*RECEIVERID*{}*{}*X*005010X222~".format(
                datetime.utcnow().strftime("%Y%m%d"),
                datetime.utcnow().strftime("%Y%m%d")
            ))

            # ST Transaction Set Header
            segments.append("ST*837*{}~".format(config.get("control_number", "0001")))

            # BHT Beginning Hierarchical Transaction
            segments.append("BHT*{}*{}*{}*{}*{}*{}~".format(
                config.get("hierarchical_level_code", "0019"),
                config.get("transaction_type", "CHAP"),
                claim_data.get("claim_number"),
                claim_data.get("submission_date", datetime.utcnow().strftime("%Y%m%d")),
                claim_data.get("submission_time", datetime.utcnow().strftime("%H%M")),
                config.get("transaction_code", "CGP")
            ))

            # NM1 Submitter Name
            segments.append("NM1*41*2*PROVIDER NAME*****46*SENDERID~")

            # PER Provider Contact Information
            segments.append("PER*IC*PROVIDER CONTACT*TE*{}*~".format(
                config.get("provider_phone", "")
            ))

            # More segments would follow for a complete 837...

            # Combine segments
            edi_content = "\n".join(segments)

            return edi_content

        except Exception as e:
            logger.error("Error building EDI 837 Professional: {}".format(e))
            raise ValueError("Failed to build EDI 837 Professional: {}".format(str(e)))

    def build_837_institutional(
        self,
        claim_data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> str:
        """Build EDI 837 Institutional claim

        Args:
            claim_data: Claim data
            config: Billing configuration

        Returns:
            EDI 837 Institutional formatted string
        """
        try:
            # Simplified institutional claim builder
            segments = []

            # ISA Interchange Control Header
            segments.append("ISA*00*          *00*          *ZZ*SENDERID*ZZ*RECEIVERID*{}*{}*^*00501*{}*0*P*>~".format(
                datetime.utcnow().strftime("%Y%m%d"),
                datetime.utcnow().strftime("%H%M"),
                datetime.utcnow().strftime("%Y%m%d%H%M")
            ))

            # GS Functional Group Header
            segments.append("GS*BI*SENDERID*RECEIVERID*{}*{}*X*005010X222~".format(
                datetime.utcnow().strftime("%Y%m%d"),
                datetime.utcnow().strftime("%Y%m%d")
            ))

            # ST Transaction Set Header
            segments.append("ST*837*{}~".format(config.get("control_number", "0001")))

            # BHT Beginning Hierarchical Transaction
            segments.append("BHT*{}*{}*{}*{}*{}*{}~".format(
                config.get("hierarchical_level_code", "0019"),
                config.get("transaction_type", "CHAP"),
                claim_data.get("claim_number"),
                claim_data.get("submission_date", datetime.utcnow().strftime("%Y%m%d")),
                claim_data.get("submission_time", datetime.utcnow().strftime("%H%M")),
                config.get("transaction_code", "CGP")
            ))

            # More segments would follow...

            # Combine segments
            edi_content = "\n".join(segments)

            return edi_content

        except Exception as e:
            logger.error("Error building EDI 837 Institutional: {}".format(e))
            raise ValueError("Failed to build EDI 837 Institutional: {}".format(str(e)))


class EDI835Parser(object):
    """Parses EDI 835 (Remittance Advice) format"""

    def __init__(self):
        pass

    def parse_835(self, x835_content: str) -> Dict[str, Any]:
        """Parse EDI 835 remittance advice

        Args:
            x835_content: EDI 835 content

        Returns:
            Dict with parsed remittance data
        """
        try:
            # Simplified X835 parser
            segments = x835_content.split("~")

            parsed_data = {
                "file_name": "",
                "sender_id": "",
                "receiver_id": "",
                "creation_date": "",
                "total_payment_amount": 0.0,
                "payment_count": 0,
                "payments": []
            }

            for segment in segments:
                if segment.startswith("ISA"):
                    parts = segment.split("*")
                    if len(parts) > 8:
                        parsed_data["sender_id"] = parts[6] if len(parts) > 6 else ""
                        parsed_data["receiver_id"] = parts[7] if len(parts) > 7 else ""

                elif segment.startswith("BPR"):
                    # BPR segment contains payment amount
                    parts = segment.split("*")
                    if len(parts) > 2:
                        try:
                            parsed_data["total_payment_amount"] = float(parts[2])
                        except (ValueError, IndexError):
                            pass

                # More segments would be parsed for a complete X835...

            return parsed_data

        except Exception as e:
            logger.error("Error parsing EDI 835: {}".format(e))
            raise ValueError("Failed to parse EDI 835: {}".format(str(e)))


class BillingIntegrationService(object):
    """Service for billing system integration"""

    def __init__(self, db):
        self.db = db
        self.edi_837_builder = EDI837Builder()
        self.edi_835_parser = EDI835Parser()

    # ==========================================================================
    # Billing System Management
    # ==========================================================================

    async def register_billing_system(
        self,
        system_code: str,
        system_name: str,
        system_type: str,
        protocol: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Register external billing system

        Args:
            system_code: System code
            system_name: System name
            system_type: System type (clearinghouse, insurance, payer)
            protocol: Communication protocol
            **kwargs: Additional system attributes

        Returns:
            Dict with system details
        """
        try:
            system = BillingSystem(
                system_id="BILL-{}".format(system_code),
                system_code=system_code,
                system_name=system_name,
                system_type=system_type,
                organization=kwargs.get("organization"),
                payer_id=kwargs.get("payer_id"),
                contact_name=kwargs.get("contact_name"),
                contact_email=kwargs.get("contact_email"),
                contact_phone=kwargs.get("contact_phone"),
                protocol=protocol,
                endpoint_url=kwargs.get("endpoint_url"),
                auth_type=kwargs.get("auth_type"),
                auth_credentials=kwargs.get("auth_credentials"),
                edi_config=kwargs.get("edi_config"),
                mapping_config=kwargs.get("mapping_config"),
                supported_formats=kwargs.get("supported_formats"),
                is_bpjs=kwargs.get("is_bpjs", False),
                bpjs_sep_type=kwargs.get("bpjs_sep_type"),
                test_mode=kwargs.get("test_mode", False)
            )

            self.db.add(system)
            await self.db.commit()

            logger.info("Registered billing system: {}".format(system.system_id))

            return {
                "system_id": system.system_id,
                "system_code": system.system_code,
                "system_name": system.system_name,
                "status": system.status
            }

        except Exception as e:
            logger.error("Error registering billing system: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to register billing system: {}".format(str(e)))

    # ==========================================================================
    # Claim Submission
    # ==========================================================================

    async def submit_claim(
        self,
        invoice_id: int,
        billing_system_id: int,
        claim_data: Dict[str, Any],
        submitted_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Submit claim to billing system

        Args:
            invoice_id: Invoice ID
            billing_system_id: Billing system ID
            claim_data: Claim data
            submitted_by: User ID

        Returns:
            Dict with submission details
        """
        try:
            # Get billing system
            system_query = select(BillingSystem).where(BillingSystem.id == billing_system_id)
            system_result = await self.db.execute(system_query)
            system = system_result.scalar_one_or_none()

            if not system:
                raise ValueError("Billing system {} not found".format(billing_system_id))

            # Generate claim number
            claim_number = "CLAIM-{}-{}".format(invoice_id, datetime.utcnow().strftime("%Y%m%d%H%M%S"))

            # Build EDI 837 if needed
            edi_content = None
            if system.protocol in ["EDI_X12", "EDI_837"]:
                if claim_data.get("claim_type") == "institutional":
                    edi_content = self.edi_837_builder.build_837_institutional(
                        claim_data,
                        {"control_number": claim_number}
                    )
                else:
                    edi_content = self.edi_837_builder.build_837_professional(
                        claim_data,
                        {"control_number": claim_number}
                    )

            # Create claim submission
            claim = ClaimSubmission(
                submission_id="SUB-{}-{}".format(system.system_code, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                claim_number=claim_number,
                billing_system_id=billing_system_id,
                invoice_id=invoice_id,
                patient_id=claim_data.get("patient_id"),
                encounter_id=claim_data.get("encounter_id"),
                claim_type=claim_data.get("claim_type", "professional"),
                service_type=claim_data.get("service_type"),
                claim_amount=claim_data.get("claim_amount", 0),
                patient_responsibility=claim_data.get("patient_responsibility", 0),
                service_start_date=claim_data.get("service_start_date"),
                service_end_date=claim_data.get("service_end_date"),
                admission_date=claim_data.get("admission_date"),
                discharge_date=claim_data.get("discharge_date"),
                billing_provider_npi=claim_data.get("billing_provider_npi"),
                rendering_provider_npi=claim_data.get("rendering_provider_npi"),
                facility_id=claim_data.get("facility_id"),
                principal_diagnosis=claim_data.get("principal_diagnosis"),
                principal_diagnosis_desc=claim_data.get("principal_diagnosis_desc"),
                admitting_diagnosis=claim_data.get("admitting_diagnosis"),
                other_diagnoses=claim_data.get("other_diagnoses"),
                procedures=claim_data.get("procedures"),
                claim_data=claim_data,
                edi_837_content=edi_content,
                status=ClaimStatus.SUBMITTED,
                submitted_at=datetime.utcnow(),
                test_mode=system.test_mode
            )

            self.db.add(claim)
            await self.db.commit()

            logger.info("Submitted claim: {}".format(claim.claim_number))

            return {
                "submission_id": claim.submission_id,
                "claim_number": claim.claim_number,
                "status": claim.status,
                "submitted_at": claim.submitted_at.isoformat()
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error submitting claim: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to submit claim: {}".format(str(e)))

    # ==========================================================================
    # Payment Reconciliation
    # ==========================================================================

    async def process_payment(
        self,
        payment_data: Dict[str, Any],
        billing_system_id: int
    ) -> Dict[str, Any]:
        """Process payment from billing system

        Args:
            payment_data: Payment data
            billing_system_id: Billing system ID

        Returns:
            Dict with payment details
        """
        try:
            # Get billing system
            system_query = select(BillingSystem).where(BillingSystem.id == billing_system_id)
            system_result = await self.db.execute(system_query)
            system = system_result.scalar_one_or_none()

            if not system:
                raise ValueError("Billing system {} not found".format(billing_system_id))

            # Create payment record
            payment = ClaimPayment(
                payment_id="PAY-{}-{}".format(system.system_code, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                claim_submission_id=payment_data.get("claim_submission_id"),
                billing_system_id=billing_system_id,
                patient_id=payment_data.get("patient_id"),
                payment_amount=payment_data.get("payment_amount", 0),
                payment_date=payment_data.get("payment_date", datetime.utcnow()),
                payment_method=payment_data.get("payment_method"),
                payment_reference=payment_data.get("payment_reference"),
                payer_name=payment_data.get("payer_name"),
                payer_id=payment_data.get("payer_id"),
                check_number=payment_data.get("check_number"),
                electronic_remittance_advice=payment_data.get("era_content"),
                status=PaymentStatus.COMPLETED
            )

            self.db.add(payment)

            # Update claim status
            if payment.claim_submission_id:
                claim_query = select(ClaimSubmission).where(
                    ClaimSubmission.id == payment.claim_submission_id
                )
                claim_result = await self.db.execute(claim_query)
                claim = claim_result.scalar_one_or_none()

                if claim:
                    claim.insurance_payment_amount = payment.payment_amount
                    claim.status = ClaimStatus.PAID
                    claim.adjudication_date = payment.payment_date

            await self.db.commit()

            logger.info("Processed payment: {}".format(payment.payment_id))

            return {
                "payment_id": payment.payment_id,
                "status": payment.status,
                "payment_amount": payment.payment_amount
            }

        except Exception as e:
            logger.error("Error processing payment: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to process payment: {}".format(str(e)))

    async def process_remittance_advice(
        self,
        x835_content: str,
        billing_system_id: int
    ) -> Dict[str, Any]:
        """Process electronic remittance advice (X835)

        Args:
            x835_content: EDI 835 content
            billing_system_id: Billing system ID

        Returns:
            Dict with processing result
        """
        try:
            # Parse X835
            parsed_data = self.edi_835_parser.parse_835(x835_content)

            # Store remittance advice
            remittance = RemittanceAdvice(
                remittance_id="ERA-{}-{}".format(billing_system_id, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                billing_system_id=billing_system_id,
                remittance_date=datetime.utcnow(),
                total_payment_amount=parsed_data.get("total_payment_amount", 0),
                payment_count=parsed_data.get("payment_count", 0),
                payer_name=parsed_data.get("payer_name", ""),
                payer_id=parsed_data.get("payer_id", ""),
                trace_number=parsed_data.get("trace_number", ""),
                x835_content=x835_content,
                parsed_data=parsed_data,
                processing_status="completed",
                processed_at=datetime.utcnow()
            )

            self.db.add(remittance)
            await self.db.commit()

            logger.info("Processed remittance advice: {}".format(remittance.remittance_id))

            return {
                "remittance_id": remittance.remittance_id,
                "total_payment_amount": remittance.total_payment_amount,
                "payment_count": remittance.payment_count
            }

        except Exception as e:
            logger.error("Error processing remittance advice: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to process remittance advice: {}".format(str(e)))

    # ==========================================================================
    # Claim Status Tracking
    # ==========================================================================

    async def get_claim_status(
        self,
        claim_number: str
    ) -> Dict[str, Any]:
        """Get claim status

        Args:
            claim_number: Claim number

        Returns:
            Dict with claim status
        """
        try:
            query = select(ClaimSubmission).where(ClaimSubmission.claim_number == claim_number)
            result = await self.db.execute(query)
            claim = result.scalar_one_or_none()

            if not claim:
                raise ValueError("Claim {} not found".format(claim_number))

            return {
                "claim_number": claim.claim_number,
                "status": claim.status,
                "submitted_at": claim.submitted_at.isoformat() if claim.submitted_at else None,
                "acknowledged_at": claim.acknowledged_at.isoformat() if claim.acknowledged_at else None,
                "processed_at": claim.processed_at.isoformat() if claim.processed_at else None,
                "claim_amount": claim.claim_amount,
                "approved_amount": claim.approved_amount,
                "insurance_payment_amount": claim.insurance_payment_amount,
                "payer_claim_number": claim.payer_claim_number,
                "payer_response_code": claim.payer_response_code,
                "payer_response_message": claim.payer_response_message
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error getting claim status: {}".format(e))
            raise ValueError("Failed to get claim status: {}".format(str(e)))


def get_billing_integration_service(db):
    """Get or create billing integration service instance

    Args:
        db: Database session

    Returns:
        BillingIntegrationService instance
    """
    return BillingIntegrationService(db)
