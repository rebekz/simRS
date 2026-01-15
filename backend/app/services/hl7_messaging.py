"""HL7 v2.x Message Parsing and Routing Service for STORY-024-01

This module provides services for:
- HL7 message parsing (MSH, PID, PV1, ORC, OBR, OBX segments)
- HL7 message routing based on configurable rules
- HL7 acknowledgment generation (ACK/NAK)
- HL7 error handling and tracking

Python 3.5+ compatible
"""

import logging
import re
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.hl7 import (
    HL7Message, HL7Acknowledgment, HL7Error, HL7RoutingRule,
    HL7SequenceNumber, HL7MessageType, HL7MessageStatus
)


logger = logging.getLogger(__name__)


class HL7Parser(object):
    """HL7 v2.x message parser"""

    # HL7 field separator
    FIELD_SEPARATOR = "|"
    COMPONENT_SEPARATOR = "^"
    SUBCOMPONENT_SEPARATOR = "&"
    REPETITION_SEPARATOR = "~"
    ESCAPE_CHARACTER = "\\"

    def __init__(self):
        self.encoding_chars = {}

    def parse_message(self, raw_message: str) -> Dict[str, Any]:
        """Parse HL7 message into structured format

        Args:
            raw_message: Raw HL7 message string

        Returns:
            Dict with parsed message segments and fields
        """
        try:
            # Split message into segments
            segments = raw_message.strip().split("\r")

            if not segments:
                raise ValueError("Empty HL7 message")

            parsed = {
                "raw_message": raw_message,
                "segments": {},
                "encoding_chars": {}
            }

            # Parse MSH segment first (for encoding characters)
            msh_segment = segments[0]
            if msh_segment.startswith("MSH"):
                parsed["segments"]["MSH"] = self._parse_msh_segment(msh_segment)
                parsed["encoding_chars"] = parsed["segments"]["MSH"].get("encoding_chars", {})

            # Parse remaining segments
            for segment in segments[1:]:
                if not segment:
                    continue

                # Get segment identifier (first 3 characters)
                segment_id = segment[:3]

                # Parse segment based on type
                if segment_id == "PID":
                    parsed["segments"]["PID"] = self._parse_pid_segment(segment, parsed["encoding_chars"])
                elif segment_id == "PV1":
                    parsed["segments"]["PV1"] = self._parse_pv1_segment(segment, parsed["encoding_chars"])
                elif segment_id == "ORC":
                    parsed["segments"]["ORC"] = self._parse_orc_segment(segment, parsed["encoding_chars"])
                elif segment_id == "OBR":
                    parsed["segments"]["OBR"] = self._parse_obr_segment(segment, parsed["encoding_chars"])
                elif segment_id == "OBX":
                    parsed["segments"]["OBX"] = self._parse_obx_segment(segment, parsed["encoding_chars"])
                else:
                    # Generic segment parsing
                    parsed["segments"][segment_id] = self._parse_generic_segment(segment, parsed["encoding_chars"])

            return parsed

        except Exception as e:
            logger.error("Error parsing HL7 message: {}".format(e))
            raise ValueError("Failed to parse HL7 message: {}".format(str(e)))

    def _parse_msh_segment(self, segment: str) -> Dict[str, Any]:
        """Parse MSH (Message Header) segment"""
        try:
            fields = segment.split(self.FIELD_SEPARATOR)

            return {
                "segment_type": fields[0] if len(fields) > 0 else None,
                "encoding_chars": fields[1] if len(fields) > 1 else None,
                "sending_application": fields[2] if len(fields) > 2 else None,
                "sending_facility": fields[3] if len(fields) > 3 else None,
                "receiving_application": fields[4] if len(fields) > 4 else None,
                "receiving_facility": fields[5] if len(fields) > 5 else None,
                "datetime": fields[6] if len(fields) > 6 else None,
                "security": fields[7] if len(fields) > 7 else None,
                "message_type": fields[8] if len(fields) > 8 else None,
                "message_control_id": fields[9] if len(fields) > 9 else None,
                "processing_id": fields[10] if len(fields) > 10 else None,
                "version": fields[11] if len(fields) > 11 else None,
                "sequence_number": fields[12] if len(fields) > 12 else None,
                "continuation_pointer": fields[13] if len(fields) > 13 else None,
                "accept_ack_type": fields[14] if len(fields) > 14 else None,
                "application_ack_type": fields[15] if len(fields) > 15 else None,
                "country_code": fields[16] if len(fields) > 16 else None,
            }
        except Exception as e:
            logger.error("Error parsing MSH segment: {}".format(e))
            raise

    def _parse_pid_segment(self, segment: str, encoding_chars: dict) -> Dict[str, Any]:
        """Parse PID (Patient Identification) segment"""
        try:
            fields = segment.split(self.FIELD_SEPARATOR)

            return {
                "segment_type": fields[0] if len(fields) > 0 else None,
                "set_id": fields[1] if len(fields) > 1 else None,
                "external_id": fields[2] if len(fields) > 2 else None,
                "internal_id": fields[3] if len(fields) > 3 else None,
                "alternate_id": fields[4] if len(fields) > 4 else None,
                "patient_name": fields[5] if len(fields) > 5 else None,
                "mother_maiden_name": fields[6] if len(fields) > 6 else None,
                "datetime_of_birth": fields[7] if len(fields) > 7 else None,
                "sex": fields[8] if len(fields) > 8 else None,
                "patient_alias": fields[9] if len(fields) > 9 else None,
                "race": fields[10] if len(fields) > 10 else None,
                "patient_address": fields[11] if len(fields) > 11 else None,
                "county_code": fields[12] if len(fields) > 12 else None,
                "phone_home": fields[13] if len(fields) > 13 else None,
                "phone_business": fields[14] if len(fields) > 14 else None,
                "primary_language": fields[15] if len(fields) > 15 else None,
                "marital_status": fields[16] if len(fields) > 16 else None,
                "religion": fields[17] if len(fields) > 17 else None,
                "account_number": fields[18] if len(fields) > 18 else None,
                "ssn_number": fields[19] if len(fields) > 19 else None,
                "drivers_license": fields[20] if len(fields) > 20 else None,
            }
        except Exception as e:
            logger.error("Error parsing PID segment: {}".format(e))
            raise

    def _parse_pv1_segment(self, segment: str, encoding_chars: dict) -> Dict[str, Any]:
        """Parse PV1 (Patient Visit) segment"""
        try:
            fields = segment.split(self.FIELD_SEPARATOR)

            return {
                "segment_type": fields[0] if len(fields) > 0 else None,
                "set_id": fields[1] if len(fields) > 1 else None,
                "patient_class": fields[2] if len(fields) > 2 else None,
                "assigned_patient_location": fields[3] if len(fields) > 3 else None,
                "admission_type": fields[4] if len(fields) > 4 else None,
                "preadmit_number": fields[5] if len(fields) > 5 else None,
                "prior_location": fields[6] if len(fields) > 6 else None,
                "attending_doctor": fields[7] if len(fields) > 7 else None,
                "referring_doctor": fields[8] if len(fields) > 8 else None,
                "consulting_doctor": fields[9] if len(fields) > 9 else None,
                "hospital_service": fields[10] if len(fields) > 10 else None,
                "temporary_location": fields[11] if len(fields) > 11 else None,
                "preadmit_test_indicator": fields[12] if len(fields) > 12 else None,
            }
        except Exception as e:
            logger.error("Error parsing PV1 segment: {}".format(e))
            raise

    def _parse_orc_segment(self, segment: str, encoding_chars: dict) -> Dict[str, Any]:
        """Parse ORC (Order Control) segment"""
        try:
            fields = segment.split(self.FIELD_SEPARATOR)

            return {
                "segment_type": fields[0] if len(fields) > 0 else None,
                "order_control": fields[1] if len(fields) > 1 else None,
                "placer_order_number": fields[2] if len(fields) > 2 else None,
                "filler_order_number": fields[3] if len(fields) > 3 else None,
                "placer_group_number": fields[4] if len(fields) > 4 else None,
                "order_status": fields[5] if len(fields) > 5 else None,
                "response_flag": fields[6] if len(fields) > 6 else None,
                "quantity_timing": fields[7] if len(fields) > 7 else None,
                "parent": fields[8] if len(fields) > 8 else None,
                "datetime_of_transaction": fields[9] if len(fields) > 9 else None,
            }
        except Exception as e:
            logger.error("Error parsing ORC segment: {}".format(e))
            raise

    def _parse_obr_segment(self, segment: str, encoding_chars: dict) -> Dict[str, Any]:
        """Parse OBR (Observation Request) segment"""
        try:
            fields = segment.split(self.FIELD_SEPARATOR)

            return {
                "segment_type": fields[0] if len(fields) > 0 else None,
                "set_id": fields[1] if len(fields) > 1 else None,
                "placer_order_number": fields[2] if len(fields) > 2 else None,
                "filler_order_number": fields[3] if len(fields) > 3 else None,
                "universal_service_id": fields[4] if len(fields) > 4 else None,
                "priority": fields[5] if len(fields) > 5 else None,
                "requested_datetime": fields[6] if len(fields) > 6 else None,
                "observation_datetime": fields[7] if len(fields) > 7 else None,
                "observation_end_datetime": fields[8] if len(fields) > 8 else None,
                "collection_volume": fields[9] if len(fields) > 9 else None,
                "collector_identifier": fields[10] if len(fields) > 10 else None,
                "specimen_action_code": fields[11] if len(fields) > 11 else None,
                "danger_code": fields[12] if len(fields) > 12 else None,
                "relevant_clinical_info": fields[13] if len(fields) > 13 else None,
            }
        except Exception as e:
            logger.error("Error parsing OBR segment: {}".format(e))
            raise

    def _parse_obx_segment(self, segment: str, encoding_chars: dict) -> Dict[str, Any]:
        """Parse OBX (Observation Result) segment"""
        try:
            fields = segment.split(self.FIELD_SEPARATOR)

            return {
                "segment_type": fields[0] if len(fields) > 0 else None,
                "set_id": fields[1] if len(fields) > 1 else None,
                "value_type": fields[2] if len(fields) > 2 else None,
                "observation_identifier": fields[3] if len(fields) > 3 else None,
                "observation_sub_id": fields[4] if len(fields) > 4 else None,
                "observation_value": fields[5] if len(fields) > 5 else None,
                "units": fields[6] if len(fields) > 6 else None,
                "reference_range": fields[7] if len(fields) > 7 else None,
                "abnormal_flags": fields[8] if len(fields) > 8 else None,
                "probability": fields[9] if len(fields) > 9 else None,
                "nature_of_abnormal_test": fields[10] if len(fields) > 10 else None,
                "observation_result_status": fields[11] if len(fields) > 11 else None,
                "effective_date": fields[12] if len(fields) > 12 else None,
            }
        except Exception as e:
            logger.error("Error parsing OBX segment: {}".format(e))
            raise

    def _parse_generic_segment(self, segment: str, encoding_chars: dict) -> Dict[str, Any]:
        """Parse generic segment"""
        try:
            fields = segment.split(self.FIELD_SEPARATOR)

            return {
                "segment_type": fields[0] if len(fields) > 0 else None,
                "fields": fields[1:] if len(fields) > 1 else []
            }
        except Exception as e:
            logger.error("Error parsing generic segment: {}".format(e))
            raise

    def create_acknowledgment(
        self,
        original_message: Dict[str, Any],
        ack_code: str,
        error_message: Optional[str] = None
    ) -> str:
        """Create HL7 acknowledgment message

        Args:
            original_message: Original parsed HL7 message
            ack_code: Acknowledgment code (AA, AE, AR, CA, CE, CR)
            error_message: Error message for NAK

        Returns:
            Raw HL7 acknowledgment message string
        """
        try:
            msh = original_message.get("segments", {}).get("MSH", {})
            message_control_id = msh.get("message_control_id", "")
            sending_app = msh.get("sending_application", "")
            sending_facility = msh.get("sending_facility", "")
            receiving_app = msh.get("receiving_application", "")
            receiving_facility = msh.get("receiving_facility", "")

            # Build MSH segment for ACK
            msh_ack = "MSH|^~\\&|{}|{}|{}|{}|{}||ACK|{}|P|2.5".format(
                receiving_app,
                receiving_facility,
                sending_app,
                sending_facility,
                datetime.utcnow().strftime("%Y%m%d%H%M%S"),
                message_control_id
            )

            # Build MSA segment (Message Acknowledgment)
            if error_message:
                msa_ack = "MSA|{}|{}|{}".format(ack_code, message_control_id, error_message)
            else:
                msa_ack = "MSA|{}|{}".format(ack_code, message_control_id)

            return msh_ack + "\r" + msa_ack + "\r"

        except Exception as e:
            logger.error("Error creating acknowledgment: {}".format(e))
            raise ValueError("Failed to create acknowledgment: {}".format(str(e)))


class HL7MessagingService(object):
    """Service for HL7 message processing and routing"""

    def __init__(self, db):
        self.db = db
        self.parser = HL7Parser()

    # ==========================================================================
    # Message Processing
    # ==========================================================================

    async def receive_message(
        self,
        raw_message: str,
        source_system: Optional[str] = None
    ) -> Dict[str, Any]:
        """Receive and process incoming HL7 message

        Args:
            raw_message: Raw HL7 message string
            source_system: Source system identifier

        Returns:
            Dict with processing result and acknowledgment
        """
        try:
            # Parse message
            parsed_message = self.parser.parse_message(raw_message)

            # Extract metadata from MSH
            msh = parsed_message.get("segments", {}).get("MSH", {})
            message_type = msh.get("message_type", "")
            message_control_id = msh.get("message_control_id", "")

            if not message_control_id:
                raise ValueError("Missing message control ID in MSH segment")

            # Check for duplicate message
            existing = await self._get_message_by_control_id(message_control_id)
            if existing:
                logger.warning("Duplicate message with control ID: {}".format(message_control_id))
                # Return original acknowledgment for duplicate
                if existing.acknowledgment:
                    return {
                        "message_id": existing.id,
                        "status": "duplicate",
                        "acknowledgment": existing.acknowledgment.raw_acknowledgment
                    }

            # Create message record
            message = HL7Message(
                message_id=message_control_id,
                message_type=message_type,
                trigger_event=msh.get("message_type", "").split("^")[1] if "^" in msh.get("message_type", "") else None,
                version=msh.get("version", "2.5"),
                raw_message=raw_message,
                parsed_message=parsed_message,
                sending_facility=msh.get("sending_facility"),
                sending_application=msh.get("sending_application"),
                receiving_facility=msh.get("receiving_facility"),
                receiving_application=msh.get("receiving_application"),
                message_control_id=message_control_id,
                source_system=source_system,
                status=HL7MessageStatus.PROCESSING
            )

            self.db.add(message)
            await self.db.flush()

            # Route message
            routing_result = await self._route_message(message, parsed_message)

            # Generate acknowledgment
            ack_code = "AA"  # Application Accept
            error_message = None

            if routing_result.get("success"):
                message.status = HL7MessageStatus.PROCESSED
                message.processed_at = datetime.utcnow()
            else:
                ack_code = "AE"  # Application Error
                error_message = routing_result.get("error", "Routing failed")
                message.status = HL7MessageStatus.FAILED
                message.error_message = error_message

            # Create acknowledgment
            raw_ack = self.parser.create_acknowledgment(
                parsed_message,
                ack_code,
                error_message
            )

            # Store acknowledgment
            acknowledgment = HL7Acknowledgment(
                message_id=message.id,
                ack_type="ACK" if ack_code == "AA" else "NAK",
                ack_code=ack_code,
                raw_acknowledgment=raw_ack,
                parsed_acknowledgment=self.parser.parse_message(raw_ack),
                error_message=error_message
            )

            self.db.add(acknowledgment)
            await self.db.commit()

            logger.info(
                "Processed HL7 message {}: type={}, status={}".format(
                    message_control_id, message_type, ack_code
                )
            )

            return {
                "message_id": message.id,
                "message_control_id": message_control_id,
                "status": message.status,
                "acknowledgment": raw_ack,
                "routing_result": routing_result
            }

        except ValueError as e:
            logger.error("Error receiving HL7 message: {}".format(e))
            await self.db.rollback()

            # Generate NAK for parsing errors
            nak_ack = self._create_error_nak(raw_message, str(e))
            return {
                "status": "error",
                "error": str(e),
                "acknowledgment": nak_ack
            }
        except Exception as e:
            logger.error("Unexpected error receiving HL7 message: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to receive HL7 message: {}".format(str(e)))

    async def _route_message(
        self,
        message: HL7Message,
        parsed_message: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route message based on routing rules

        Args:
            message: HL7 message object
            parsed_message: Parsed message data

        Returns:
            Dict with routing result
        """
        try:
            # Get active routing rules
            rules = await self._get_applicable_routing_rules(message)

            if not rules:
                return {
                    "success": True,
                    "message": "No matching routing rules, message stored only"
                }

            results = []
            for rule in rules:
                result = await self._apply_routing_rule(message, rule)
                results.append(result)

            # Update rule statistics
            for rule in rules:
                rule.total_messages_processed += 1

            await self.db.commit()

            return {
                "success": all(r.get("success", False) for r in results),
                "rules_applied": len(results),
                "results": results
            }

        except Exception as e:
            logger.error("Error routing message: {}".format(e))
            return {
                "success": False,
                "error": str(e)
            }

    async def _get_applicable_routing_rules(
        self,
        message: HL7Message
    ) -> List[HL7RoutingRule]:
        """Get applicable routing rules for message

        Args:
            message: HL7 message

        Returns:
            List of applicable routing rules sorted by priority
        """
        try:
            query = select(HL7RoutingRule).where(
                and_(
                    HL7RoutingRule.is_active == True,
                    or_(
                        HL7RoutingRule.message_type_filter == message.message_type,
                        HL7RoutingRule.message_type_filter.is_(None)
                    ),
                    or_(
                        HL7RoutingRule.sending_facility_filter == message.sending_facility,
                        HL7RoutingRule.sending_facility_filter.is_(None)
                    ),
                    or_(
                        HL7RoutingRule.sending_application_filter == message.sending_application,
                        HL7RoutingRule.sending_application_filter.is_(None)
                    )
                )
            ).order_by(HL7RoutingRule.priority.desc())

            result = await self.db.execute(query)
            return list(result.scalars().all())

        except Exception as e:
            logger.error("Error getting routing rules: {}".format(e))
            return []

    async def _apply_routing_rule(
        self,
        message: HL7Message,
        rule: HL7RoutingRule
    ) -> Dict[str, Any]:
        """Apply routing rule to message

        Args:
            message: HL7 message
            rule: Routing rule to apply

        Returns:
            Dict with routing result
        """
        try:
            # Link message to routing rule
            message.routing_rule_id = rule.id

            # For now, just mark as routed
            # In production, this would forward to target systems
            return {
                "success": True,
                "rule_id": rule.id,
                "action": rule.action,
                "target_system": rule.target_system
            }

        except Exception as e:
            logger.error("Error applying routing rule: {}".format(e))
            return {
                "success": False,
                "rule_id": rule.id,
                "error": str(e)
            }

    async def _get_message_by_control_id(
        self,
        control_id: str
    ) -> Optional[HL7Message]:
        """Get message by control ID

        Args:
            control_id: Message control ID

        Returns:
            HL7 message or None
        """
        query = select(HL7Message).where(
            HL7Message.message_control_id == control_id
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _create_error_nak(self, raw_message: str, error_message: str) -> str:
        """Create error NAK acknowledgment

        Args:
            raw_message: Original raw message
            error_message: Error message

        Returns:
            NAK acknowledgment string
        """
        try:
            # Extract MSH segment
            segments = raw_message.split("\r")
            msh_segment = segments[0] if segments else ""

            # Create minimal NAK
            nak = "MSH|^~\\&|SIMRS|SIMRS||||||ACK|ERROR|P|2.5\r"
            nak += "MSA|CE|ERROR|{}\r".format(error_message)

            return nak

        except Exception as e:
            logger.error("Error creating NAK: {}".format(e))
            return "MSH|^~\\&|SIMRS|SIMRS||||||ACK|ERROR|P|2.5\rMSA|CE|SYSTEM_ERROR\r"

    # ==========================================================================
    # Message Query
    # ==========================================================================

    async def get_message(
        self,
        message_id: int
    ) -> Dict[str, Any]:
        """Get message by ID

        Args:
            message_id: Message ID

        Returns:
            Dict with message details
        """
        try:
            query = select(HL7Message).options(
                selectinload(HL7Message.acknowledgment),
                selectinload(HL7Message.errors),
                selectinload(HL7Message.routing_rule)
            ).where(HL7Message.id == message_id)

            result = await self.db.execute(query)
            message = result.scalar_one_or_none()

            if not message:
                raise ValueError("Message {} not found".format(message_id))

            return {
                "message_id": message.id,
                "message_control_id": message.message_control_id,
                "message_type": message.message_type,
                "trigger_event": message.trigger_event,
                "status": message.status,
                "raw_message": message.raw_message,
                "parsed_message": message.parsed_message,
                "sending_facility": message.sending_facility,
                "sending_application": message.sending_application,
                "created_at": message.created_at.isoformat() if message.created_at else None,
                "processed_at": message.processed_at.isoformat() if message.processed_at else None,
                "acknowledgment": {
                    "ack_type": message.acknowledgment.ack_type if message.acknowledgment else None,
                    "ack_code": message.acknowledgment.ack_code if message.acknowledgment else None,
                    "raw_acknowledgment": message.acknowledgment.raw_acknowledgment if message.acknowledgment else None,
                },
                "errors": [
                    {
                        "error_type": e.error_type,
                        "error_message": e.error_message,
                        "created_at": e.created_at.isoformat() if e.created_at else None
                    }
                    for e in message.errors
                ]
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error getting message: {}".format(e))
            raise ValueError("Failed to get message: {}".format(str(e)))

    async def list_messages(
        self,
        status: Optional[str] = None,
        message_type: Optional[str] = None,
        sending_facility: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List messages with filtering

        Args:
            status: Filter by status
            message_type: Filter by message type
            sending_facility: Filter by sending facility
            page: Page number
            per_page: Items per page

        Returns:
            Dict with messages list and pagination info
        """
        try:
            # Build filters
            filters = []

            if status:
                filters.append(HL7Message.status == status)
            if message_type:
                filters.append(HL7Message.message_type == message_type)
            if sending_facility:
                filters.append(HL7Message.sending_facility == sending_facility)

            # Get total count
            count_query = select(func.count(HL7Message.id))
            if filters:
                count_query = count_query.where(and_(*filters))
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar() or 0

            # Get messages with pagination
            offset = (page - 1) * per_page
            query = select(HL7Message)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(HL7Message.created_at.desc()).limit(per_page).offset(offset)

            result = await self.db.execute(query)
            messages = result.scalars().all()

            # Build response
            message_list = [
                {
                    "message_id": m.id,
                    "message_control_id": m.message_control_id,
                    "message_type": m.message_type,
                    "trigger_event": m.trigger_event,
                    "status": m.status,
                    "sending_facility": m.sending_facility,
                    "sending_application": m.sending_application,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                    "processed_at": m.processed_at.isoformat() if m.processed_at else None,
                }
                for m in messages
            ]

            return {
                "messages": message_list,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
            }

        except Exception as e:
            logger.error("Error listing messages: {}".format(e))
            raise ValueError("Failed to list messages: {}".format(str(e)))


def get_hl7_messaging_service(db):
    """Get or create HL7 messaging service instance

    Args:
        db: Database session

    Returns:
        HL7MessagingService instance
    """
    return HL7MessagingService(db)
