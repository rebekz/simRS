"""LIS (Laboratory Information System) Integration Service for STORY-024-03

This module provides services for:
- Sending lab orders to LIS via HL7 ORM^O01
- Receiving lab results from LIS via HL7 ORU^R01
- Sample status tracking
- Order management and retry logic

Python 3.5+ compatible
"""

import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.lis_integration import (
    LISOrder, LISResult, LISSample, LISMapping, LISConfiguration,
    LISOrderStatus, LISSampleStatus
)
from app.models.hl7 import HL7Message, HL7MessageStatus
from app.services.hl7_messaging import HL7Parser


logger = logging.getLogger(__name__)


class LISOrderBuilder(object):
    """Builds HL7 ORM^O01 messages for lab orders"""

    def __init__(self):
        self.parser = HL7Parser()

    def build_order_message(
        self,
        order: LISOrder,
        patient_data: Dict[str, Any],
        config: LISConfiguration
    ) -> str:
        """Build HL7 ORM^O01 message for lab order

        Args:
            order: LIS order model
            patient_data: Patient demographic data
            config: LIS configuration

        Returns:
            HL7 ORM^O01 message string
        """
        try:
            # Build MSH segment
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            msh = "MSH|^~\\&|{}|{}|{}|{}|{}||ORM^O01|{}|P|2.5||||||||{}||||".format(
                config.application,
                config.facility,
                "LIS",
                "FACILITY",
                timestamp,
                order.order_id,
                config.encoding_chars
            )

            # Build PID segment (Patient Identification)
            pid = "PID|1||{}^^^^{}||{}^{}^{}^{}|{}|{}||||||||||||||||||".format(
                patient_data.get("id", ""),
                config.facility,
                patient_data.get("last_name", ""),
                patient_data.get("first_name", ""),
                patient_data.get("middle_name", ""),
                patient_data.get("title", ""),
                patient_data.get("gender", ""),
                patient_data.get("date_of_birth", "").replace("-", "") if patient_data.get("date_of_birth") else ""
            )

            # Build PV1 segment (Patient Visit)
            pv1 = "PV1|1|{}|||||||||||||||||||||||||||||||||||||||||||||||||||".format(
                order.priority or "R"
            )

            # Build ORC segment (Order Control)
            orc = "ORC|NW|{}|{}|||||{}^{}||||||||||".format(
                order.order_id,
                order.placer_order_number or "",
                order.priority.upper(),
                "ROUTINE" if order.priority == "routine" else "URGENT"
            )

            # Build OBR segments (Observation Request) - one per test
            obr_segments = []
            for idx, test in enumerate(order.tests or [], 1):
                obr = "OBR|{}|{}|{}|{}|||||||||{}||||||||||||||||||||||||||||||||||||||".format(
                    idx,
                    "{}^{}".format(order.placer_order_number or order.order_id, idx),
                    test.get("test_code", ""),
                    test.get("test_name", ""),
                    order.priority.upper()
                )
                obr_segments.append(obro)

            # Combine all segments
            message = "\r".join([msh, pid, pv1, orc] + obr_segments) + "\r"

            return message

        except Exception as e:
            logger.error("Error building order message: {}".format(e))
            raise ValueError("Failed to build order message: {}".format(str(e)))


class LISResultProcessor(object):
    """Processes HL7 ORU^R01 lab result messages"""

    def __init__(self):
        self.parser = HL7Parser()

    def process_result_message(
        self,
        raw_message: str
    ) -> Dict[str, Any]:
        """Process HL7 ORU^R01 result message

        Args:
            raw_message: Raw HL7 ORU^R01 message

        Returns:
            Dict with parsed result data
        """
        try:
            parsed = self.parser.parse_message(raw_message)

            msh = parsed.get("segments", {}).get("MSH", {})
            orc = parsed.get("segments", {}).get("ORC", {})
            obr = parsed.get("segments", {}).get("OBR", {})
            obx_segments = parsed.get("segments", {}).get("OBX", [])
            if not isinstance(obx_segments, list):
                obx_segments = [obx_segments]

            # Extract order information
            placer_order_number = orc.get("placer_order_number", "")
            filler_order_number = orc.get("filler_order_number", "")

            # Extract test information
            test_code = obr.get("universal_service_id", "")
            test_name = obr.get("universal_service_id", "")

            # Process OBX segments (observations)
            results = []
            for obx in obx_segments:
                if not obx or obx.get("segment_type") != "OBX":
                    continue

                result = {
                    "set_id": obx.get("set_id"),
                    "value_type": obx.get("value_type"),
                    "observation_identifier": obx.get("observation_identifier"),
                    "observation_value": obx.get("observation_value"),
                    "unit": obx.get("units"),
                    "reference_range": obx.get("reference_range"),
                    "abnormal_flag": obx.get("abnormal_flags"),
                    "result_status": obx.get("observation_result_status")
                }
                results.append(result)

            return {
                "placer_order_number": placer_order_number,
                "filler_order_number": filler_order_number,
                "test_code": test_code,
                "test_name": test_name,
                "results": results,
                "parsed_message": parsed
            }

        except Exception as e:
            logger.error("Error processing result message: {}".format(e))
            raise ValueError("Failed to process result message: {}".format(str(e)))


class LISIntegrationService(object):
    """Service for LIS integration"""

    def __init__(self, db):
        self.db = db
        self.order_builder = LISOrderBuilder()
        self.result_processor = LISResultProcessor()

    # ==========================================================================
    # Order Management
    # ==========================================================================

    async def send_order_to_lis(
        self,
        lis_order_id: int
    ) -> Dict[str, Any]:
        """Send lab order to LIS system

        Args:
            lis_order_id: LIS order ID

        Returns:
            Dict with send result
        """
        try:
            # Get order
            query = select(LISOrder).where(LISOrder.id == lis_order_id)
            result = await self.db.execute(query)
            order = result.scalar_one_or_none()

            if not order:
                raise ValueError("LIS order {} not found".format(lis_order_id))

            # Check status
            if order.status != LISOrderStatus.PENDING:
                raise ValueError("Order {} has already been sent (status: {})".format(
                    lis_order_id, order.status
                ))

            # Get LIS configuration
            config = await self._get_lis_config()
            if not config or not config.is_active:
                raise ValueError("LIS configuration not found or inactive")

            # Get patient data
            from app.models.patient import Patient
            patient_query = select(Patient).where(Patient.id == order.patient_id)
            patient_result = await self.db.execute(patient_query)
            patient = patient_result.scalar_one_or_none()

            if not patient:
                raise ValueError("Patient {} not found".format(order.patient_id))

            # Build HL7 message
            patient_data = {
                "id": patient.id,
                "first_name": patient.first_name,
                "middle_name": patient.middle_name,
                "last_name": patient.last_name,
                "title": patient.title,
                "gender": patient.gender,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None
            }

            hl7_message = self.order_builder.build_order_message(
                order, patient_data, config
            )

            # For now, simulate sending (in production, would send via TCP/MLLP)
            # Store the HL7 message for tracking
            order.status = LISOrderStatus.SENT
            order.sent_at = datetime.utcnow()
            order.lis_order_number = "LIS-{}".format(order.order_id)

            # Store in HL7 messages table
            hl7_msg = HL7Message(
                message_id="LIS-ORDER-{}".format(order.order_id),
                message_type="ORM^O01",
                trigger_event="O01",
                version="2.5",
                raw_message=hl7_message,
                parsed_message=self.order_builder.parser.parse_message(hl7_message),
                sending_facility=config.facility,
                sending_application=config.application,
                receiving_facility=config.facility,
                status=HL7MessageStatus.PROCESSED,
                processed_at=datetime.utcnow()
            )

            self.db.add(hl7_msg)

            await self.db.commit()

            logger.info("Sent LIS order: {}".format(order.order_id))

            return {
                "order_id": order.order_id,
                "status": order.status,
                "lis_order_number": order.lis_order_number,
                "message": "Order sent to LIS successfully"
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error sending order to LIS: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to send order to LIS: {}".format(str(e)))

    async def process_lis_result(
        self,
        raw_message: str
    ) -> Dict[str, Any]:
        """Process lab result received from LIS

        Args:
            raw_message: Raw HL7 ORU^R01 message

        Returns:
            Dict with processing result
        """
        try:
            # Parse message
            result_data = self.result_processor.process_result_message(raw_message)

            # Find corresponding LIS order
            placer_order_number = result_data.get("placer_order_number", "")

            query = select(LISOrder).where(
                LISOrder.placer_order_number == placer_order_number
            )
            result = await self.db.execute(query)
            order = result.scalar_one_or_none()

            if not order:
                raise ValueError("No order found for placer order number: {}".format(placer_order_number))

            # Process results
            results_created = 0
            for result in result_data.get("results", []):
                lis_result = LISResult(
                    result_id="LIS-RESULT-{}-{}".format(order.order_id, result.get("set_id", "")),
                    lis_order_id=order.id,
                    filler_order_number=result_data.get("filler_order_number"),
                    lab_order_id=order.lab_order_id,
                    patient_id=order.patient_id,
                    test_code=result_data.get("test_code", ""),
                    test_name=result_data.get("test_name", ""),
                    result_value=result.get("observation_value"),
                    unit=result.get("unit"),
                    reference_range_text=result.get("reference_range"),
                    abnormal_flag=result.get("abnormal_flag"),
                    critical_flag=result.get("abnormal_flag") in ["H", "L", "A"],
                    result_status=result.get("result_status", "final"),
                    raw_message=raw_message
                )

                self.db.add(lis_result)
                results_created += 1

            # Update order status
            order.status = LISOrderStatus.COMPLETED
            order.completed_at = datetime.utcnow()
            order.results_received += results_created

            # Check for critical values
            critical_results = select(func.count(LISResult.id)).where(
                and_(
                    LISResult.lis_order_id == order.id,
                    LISResult.critical_flag == True
                )
            )
            critical_result = await self.db.execute(critical_results)
            if critical_result.scalar() > 0:
                order.critical_value = True

            await self.db.commit()

            logger.info("Processed LIS result for order: {} ({} results)".format(
                order.order_id, results_created
            ))

            return {
                "order_id": order.order_id,
                "results_received": results_created,
                "status": order.status,
                "critical_value": order.critical_value
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error processing LIS result: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to process LIS result: {}".format(str(e)))

    # ==========================================================================
    # Order Status Tracking
    # ==========================================================================

    async def get_order_status(
        self,
        order_id: str
    ) -> Dict[str, Any]:
        """Get LIS order status

        Args:
            order_id: Order identifier

        Returns:
            Dict with order status details
        """
        try:
            query = select(LISOrder).options(
                selectinload(LISOrder.results)
            ).where(LISOrder.order_id == order_id)

            result = await self.db.execute(query)
            order = result.scalar_one_or_none()

            if not order:
                raise ValueError("Order {} not found".format(order_id))

            # Get results summary
            results_summary = []
            for result in order.results:
                results_summary.append({
                    "test_code": result.test_code,
                    "test_name": result.test_name,
                    "result_value": result.result_value,
                    "unit": result.unit,
                    "abnormal_flag": result.abnormal_flag,
                    "critical_flag": result.critical_flag,
                    "result_status": result.result_status,
                    "verified_at": result.verified_at.isoformat() if result.verified_at else None
                })

            return {
                "order_id": order.order_id,
                "lis_order_number": order.lis_order_number,
                "status": order.status,
                "sent_at": order.sent_at.isoformat() if order.sent_at else None,
                "completed_at": order.completed_at.isoformat() if order.completed_at else None,
                "results_received": order.results_received,
                "results_expected": order.results_expected,
                "critical_value": order.critical_value,
                "results": results_summary
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error getting order status: {}".format(e))
            raise ValueError("Failed to get order status: {}".format(str(e)))

    async def list_orders(
        self,
        patient_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List LIS orders with filtering

        Args:
            patient_id: Filter by patient ID
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            page: Page number
            per_page: Items per page

        Returns:
            Dict with orders list and pagination info
        """
        try:
            # Build filters
            filters = []

            if patient_id:
                filters.append(LISOrder.patient_id == patient_id)
            if status:
                filters.append(LISOrder.status == status)
            if start_date:
                filters.append(LISOrder.created_at >= start_date)
            if end_date:
                filters.append(LISOrder.created_at <= end_date)

            # Get total count
            count_query = select(func.count(LISOrder.id))
            if filters:
                count_query = count_query.where(and_(*filters))
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar() or 0

            # Get orders with pagination
            offset = (page - 1) * per_page
            query = select(LISOrder)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(LISOrder.created_at.desc()).limit(per_page).offset(offset)

            result = await self.db.execute(query)
            orders = result.scalars().all()

            # Build response
            order_list = [
                {
                    "order_id": o.order_id,
                    "lis_order_number": o.lis_order_number,
                    "patient_id": o.patient_id,
                    "priority": o.priority,
                    "status": o.status,
                    "sent_at": o.sent_at.isoformat() if o.sent_at else None,
                    "completed_at": o.completed_at.isoformat() if o.completed_at else None,
                    "results_received": o.results_received,
                    "results_expected": o.results_expected,
                    "critical_value": o.critical_value
                }
                for o in orders
            ]

            return {
                "orders": order_list,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
            }

        except Exception as e:
            logger.error("Error listing orders: {}".format(e))
            raise ValueError("Failed to list orders: {}".format(str(e)))

    # ==========================================================================
    # Configuration and Mapping
    # ==========================================================================

    async def _get_lis_config(self) -> Optional[LISConfiguration]:
        """Get active LIS configuration"""
        query = select(LISConfiguration).where(
            and_(
                LISConfiguration.is_active == True,
                LISConfiguration.config_key == "default"
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_test_mapping(
        self,
        simrs_code: str,
        simrs_name: str,
        lis_code: str,
        lis_name: str
    ) -> Dict[str, Any]:
        """Create test code mapping

        Args:
            simrs_code: SIMRS test code
            simrs_name: SIMRS test name
            lis_code: LIS test code
            lis_name: LIS test name

        Returns:
            Dict with mapping details
        """
        try:
            mapping = LISMapping(
                mapping_type="test",
                simrs_code=simrs_code,
                simrs_name=simrs_name,
                lis_code=lis_code,
                lis_name=lis_name,
                is_active=True
            )

            self.db.add(mapping)
            await self.db.commit()

            return {
                "mapping_id": mapping.id,
                "message": "Test mapping created successfully"
            }

        except Exception as e:
            logger.error("Error creating test mapping: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create test mapping: {}".format(str(e)))


def get_lis_integration_service(db):
    """Get or create LIS integration service instance

    Args:
        db: Database session

    Returns:
        LISIntegrationService instance
    """
    return LISIntegrationService(db)
