"""Device/Instrument Integration Service for STORY-024-05

This module provides services for:
- Medical device registration and configuration
- Device communication and data capture
- Lab analyzer integration
- Device alert management

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.device_integration import (
    Device, DeviceData, DeviceCommand, DeviceAlert, DeviceCalibration,
    DeviceType, DeviceProtocol, DeviceStatus
)


logger = logging.getLogger(__name__)


class HL7DeviceParser(object):
    """Parses HL7 messages from medical devices"""

    def __init__(self):
        pass

    def parse_oru_r01(self, raw_message: str) -> Dict[str, Any]:
        """Parse HL7 ORU^R01 message from device

        Args:
            raw_message: Raw HL7 ORU^R01 message

        Returns:
            Dict with parsed observation data
        """
        try:
            # Simple HL7 parser (in production, use full HL7 parser)
            segments = raw_message.strip().split("\r")

            parsed_data = {
                "message_type": "ORU^R01",
                "segments": {}
            }

            for segment in segments:
                if segment.startswith("MSH"):
                    parsed_data["segments"]["MSH"] = self._parse_msh(segment)
                elif segment.startswith("PID"):
                    parsed_data["segments"]["PID"] = self._parse_pid(segment)
                elif segment.startswith("OBX"):
                    if "OBX" not in parsed_data["segments"]:
                        parsed_data["segments"]["OBX"] = []
                    parsed_data["segments"]["OBX"].append(self._parse_obx(segment))
                elif segment.startswith("OBR"):
                    parsed_data["segments"]["OBR"] = self._parse_obr(segment)

            return parsed_data

        except Exception as e:
            logger.error("Error parsing HL7 message: {}".format(e))
            raise ValueError("Failed to parse HL7 message: {}".format(str(e)))

    def _parse_msh(self, segment: str) -> Dict[str, Any]:
        """Parse MSH segment"""
        fields = segment.split("|")
        return {
            "encoding_chars": fields[1] if len(fields) > 1 else "",
            "sending_app": fields[2] if len(fields) > 2 else "",
            "sending_facility": fields[3] if len(fields) > 3 else "",
            "message_type": fields[8] if len(fields) > 8 else ""
        }

    def _parse_pid(self, segment: str) -> Dict[str, Any]:
        """Parse PID segment"""
        fields = segment.split("|")
        return {
            "patient_id": fields[3] if len(fields) > 3 else "",
            "patient_name": fields[5] if len(fields) > 5 else "",
            "dob": fields[7] if len(fields) > 7 else ""
        }

    def _parse_obx(self, segment: str) -> Dict[str, Any]:
        """Parse OBX segment"""
        fields = segment.split("|")
        return {
            "set_id": fields[1] if len(fields) > 1 else "",
            "value_type": fields[2] if len(fields) > 2 else "",
            "observation_id": fields[3] if len(fields) > 3 else "",
            "observation_value": fields[5] if len(fields) > 5 else "",
            "units": fields[6] if len(fields) > 6 else "",
            "reference_range": fields[7] if len(fields) > 7 else "",
            "abnormal_flag": fields[8] if len(fields) > 8 else ""
        }

    def _parse_obr(self, segment: str) -> Dict[str, Any]:
        """Parse OBR segment"""
        fields = segment.split("|")
        return {
            "placer_order_number": fields[2] if len(fields) > 2 else "",
            "filler_order_number": fields[3] if len(fields) > 3 else "",
            "universal_service_id": fields[4] if len(fields) > 4 else ""
        }


class ASTMDeviceParser(object):
    """Parses ASTM messages from lab analyzers"""

    def __init__(self):
        pass

    def parse_astm_message(self, raw_message: str) -> Dict[str, Any]:
        """Parse ASTM message from lab analyzer

        Args:
            raw_message: Raw ASTM message

        Returns:
            Dict with parsed data
        """
        try:
            # Simple ASTM parser
            records = raw_message.split("\r")

            parsed_data = {
                "message_type": "ASTM",
                "records": []
            }

            for record in records:
                if record.startswith("H"):  # Header record
                    parsed_data["records"].append(self._parse_header(record))
                elif record.startswith("P"):  # Patient record
                    parsed_data["records"].append(self._parse_patient(record))
                elif record.startswith("O"):  # Order record
                    parsed_data["records"].append(self._parse_order(record))
                elif record.startswith("R"):  # Result record
                    parsed_data["records"].append(self._parse_result(record))

            return parsed_data

        except Exception as e:
            logger.error("Error parsing ASTM message: {}".format(e))
            raise ValueError("Failed to parse ASTM message: {}".format(str(e)))

    def _parse_header(self, record: str) -> Dict[str, Any]:
        """Parse header record"""
        fields = record.split("|")
        return {
            "record_type": "H",
            "sender": fields[2] if len(fields) > 2 else "",
            "receiver": fields[3] if len(fields) > 3 else ""
        }

    def _parse_patient(self, record: str) -> Dict[str, Any]:
        """Parse patient record"""
        fields = record.split("|")
        return {
            "record_type": "P",
            "patient_id": fields[2] if len(fields) > 2 else "",
            "patient_name": fields[3] if len(fields) > 3 else ""
        }

    def _parse_order(self, record: str) -> Dict[str, Any]:
        """Parse order record"""
        fields = record.split("|")
        return {
            "record_type": "O",
            "sample_id": fields[2] if len(fields) > 2 else "",
            "test_code": fields[3] if len(fields) > 3 else ""
        }

    def _parse_result(self, record: str) -> Dict[str, Any]:
        """Parse result record"""
        fields = record.split("|")
        return {
            "record_type": "R",
            "test_code": fields[2] if len(fields) > 2 else "",
            "result_value": fields[3] if len(fields) > 3 else "",
            "units": fields[4] if len(fields) > 4 else ""
        }


class VitalsDataParser(object):
    """Parses vitals monitoring data"""

    def __init__(self):
        pass

    def parse_vitals_data(self, raw_data: str, data_format: str = "json") -> Dict[str, Any]:
        """Parse vitals monitoring data

        Args:
            raw_data: Raw data from device
            data_format: Data format (json, hl7, csv)

        Returns:
            Dict with parsed vitals
        """
        try:
            if data_format == "json":
                import json
                return json.loads(raw_data)
            elif data_format == "hl7":
                # Use HL7 parser
                hl7_parser = HL7DeviceParser()
                parsed = hl7_parser.parse_oru_r01(raw_data)
                return self._extract_vitals_from_hl7(parsed)
            elif data_format == "csv":
                return self._parse_vitals_csv(raw_data)
            else:
                raise ValueError("Unsupported data format: {}".format(data_format))

        except Exception as e:
            logger.error("Error parsing vitals data: {}".format(e))
            raise ValueError("Failed to parse vitals data: {}".format(str(e)))

    def _extract_vitals_from_hl7(self, hl7_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract vitals from HL7 parsed data"""
        vitals = {}
        obx_segments = hl7_data.get("segments", {}).get("OBX", [])

        for obx in obx_segments:
            obs_id = obx.get("observation_id", "")
            value = obx.get("observation_value", "")

            if "HR" in obs_id.upper():
                vitals["heart_rate"] = int(value) if value else None
            elif "NBP" in obs_id.upper() or "BP" in obs_id.upper():
                # Blood pressure may be systolic/diastolic
                if "/" in value:
                    parts = value.split("/")
                    vitals["blood_pressure_systolic"] = int(parts[0]) if parts[0] else None
                    vitals["blood_pressure_diastolic"] = int(parts[1]) if len(parts) > 1 and parts[1] else None
            elif "SPO2" in obs_id.upper() or "O2" in obs_id.upper():
                vitals["spo2"] = float(value) if value else None
            elif "TEMP" in obs_id.upper():
                vitals["temperature"] = float(value) if value else None
            elif "RESP" in obs_id.upper():
                vitals["respiratory_rate"] = int(value) if value else None

        return vitals

    def _parse_vitals_csv(self, csv_data: str) -> Dict[str, Any]:
        """Parse CSV format vitals data"""
        vitals = {}
        lines = csv_data.strip().split("\n")

        for line in lines:
            parts = line.split(",")
            if len(parts) >= 2:
                key = parts[0].strip().lower()
                value = parts[1].strip()

                if key == "heart_rate" or key == "hr":
                    vitals["heart_rate"] = int(value)
                elif key == "blood_pressure" or key == "bp":
                    if "/" in value:
                        systolic, diastolic = value.split("/")
                        vitals["blood_pressure_systolic"] = int(systolic)
                        vitals["blood_pressure_diastolic"] = int(diastolic)
                elif key == "spo2" or key == "o2_sat":
                    vitals["spo2"] = float(value)
                elif key == "temperature" or key == "temp":
                    vitals["temperature"] = float(value)
                elif key == "respiratory_rate" or key == "rr":
                    vitals["respiratory_rate"] = int(value)
                elif key == "weight" or key == "wt":
                    vitals["weight"] = float(value)
                elif key == "height" or key == "ht":
                    vitals["height"] = float(value)
                elif key == "glucose" or key == "bg":
                    vitals["blood_glucose"] = float(value)

        return vitals


class DeviceIntegrationService(object):
    """Service for device integration"""

    def __init__(self, db):
        self.db = db
        self.hl7_parser = HL7DeviceParser()
        self.astm_parser = ASTMDeviceParser()
        self.vitals_parser = VitalsDataParser()

    # ==========================================================================
    # Device Management
    # ==========================================================================

    async def register_device(
        self,
        device_name: str,
        device_type: str,
        serial_number: str,
        protocol: str,
        connection_params: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Register a new medical device

        Args:
            device_name: Device name
            device_type: Device type
            serial_number: Device serial number
            protocol: Communication protocol
            connection_params: Connection parameters
            **kwargs: Additional device attributes

        Returns:
            Dict with device details
        """
        try:
            device = Device(
                device_id="DEV-{}".format(serial_number),
                device_name=device_name,
                device_type=device_type,
                serial_number=serial_number,
                protocol=protocol,
                connection_params=connection_params,
                manufacturer=kwargs.get("manufacturer"),
                model=kwargs.get("model"),
                firmware_version=kwargs.get("firmware_version"),
                location=kwargs.get("location"),
                department=kwargs.get("department"),
                station=kwargs.get("station"),
                endpoint_url=kwargs.get("endpoint_url"),
                auth_type=kwargs.get("auth_type"),
                auth_credentials=kwargs.get("auth_credentials"),
                auto_capture=kwargs.get("auto_capture", False),
                capture_interval_seconds=kwargs.get("capture_interval_seconds"),
                data_format=kwargs.get("data_format", "json"),
                mapping_config=kwargs.get("mapping_config"),
                status=DeviceStatus.OFFLINE
            )

            self.db.add(device)
            await self.db.commit()

            logger.info("Registered device: {}".format(device.device_id))

            return {
                "device_id": device.device_id,
                "device_name": device.device_name,
                "status": device.status,
                "message": "Device registered successfully"
            }

        except Exception as e:
            logger.error("Error registering device: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to register device: {}".format(str(e)))

    async def get_device_status(
        self,
        device_id: str
    ) -> Dict[str, Any]:
        """Get device status

        Args:
            device_id: Device identifier

        Returns:
            Dict with device status
        """
        try:
            query = select(Device).where(Device.device_id == device_id)
            result = await self.db.execute(query)
            device = result.scalar_one_or_none()

            if not device:
                raise ValueError("Device {} not found".format(device_id))

            return {
                "device_id": device.device_id,
                "device_name": device.device_name,
                "device_type": device.device_type,
                "status": device.status,
                "last_heartbeat_at": device.last_heartbeat_at.isoformat() if device.last_heartbeat_at else None,
                "last_communication_at": device.last_communication_at.isoformat() if device.last_communication_at else None,
                "error_message": device.error_message,
                "error_count": device.error_count,
                "next_calibration_due": device.next_calibration_due.isoformat() if device.next_calibration_due else None
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error getting device status: {}".format(e))
            raise ValueError("Failed to get device status: {}".format(str(e)))

    # ==========================================================================
    # Data Capture
    # ==========================================================================

    async def capture_device_data(
        self,
        device_id: str,
        raw_data: str,
        patient_id: Optional[int] = None,
        encounter_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Capture data from medical device

        Args:
            device_id: Device identifier
            raw_data: Raw data from device
            patient_id: Patient ID (optional)
            encounter_id: Encounter ID (optional)

        Returns:
            Dict with capture result
        """
        try:
            # Get device
            query = select(Device).where(Device.device_id == device_id)
            result = await self.db.execute(query)
            device = result.scalar_one_or_none()

            if not device:
                raise ValueError("Device {} not found".format(device_id))

            # Parse data based on device type and protocol
            parsed_data = await self._parse_device_data(device, raw_data)

            # Create data record
            data_record = DeviceData(
                record_id="DR-{}-{}".format(device.device_id, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                device_id=device.id,
                patient_id=patient_id,
                encounter_id=encounter_id,
                data_type=device.device_type,
                raw_data=raw_data,
                parsed_data=parsed_data,
                measured_at=datetime.utcnow()
            )

            # Populate common measurement fields
            self._populate_measurement_fields(data_record, parsed_data)

            self.db.add(data_record)

            # Update device status
            device.last_communication_at = datetime.utcnow()
            device.status = DeviceStatus.ONLINE
            device.error_count = 0
            device.error_message = None

            await self.db.commit()

            logger.info("Captured data from device: {}".format(device.device_id))

            return {
                "record_id": data_record.record_id,
                "device_id": device.device_id,
                "data_type": data_record.data_type,
                "measured_at": data_record.measured_at.isoformat(),
                "parsed_data": parsed_data
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error capturing device data: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to capture device data: {}".format(str(e)))

    async def _parse_device_data(self, device: Device, raw_data: str) -> Dict[str, Any]:
        """Parse device data based on protocol and type"""
        protocol = device.protocol.upper()
        data_format = device.data_format or "json"

        if protocol == DeviceProtocol.HL7:
            return self.hl7_parser.parse_oru_r01(raw_data)
        elif protocol == DeviceProtocol.ASTM:
            return self.astm_parser.parse_astm_message(raw_data)
        elif device.device_type == DeviceType.VITALS_MONITOR:
            return self.vitals_parser.parse_vitals_data(raw_data, data_format)
        else:
            # Try to parse as JSON
            try:
                import json
                return json.loads(raw_data)
            except Exception:
                return {"raw": raw_data}

    def _populate_measurement_fields(self, data_record: DeviceData, parsed_data: Dict[str, Any]):
        """Populate measurement fields from parsed data"""
        # Extract vitals if present
        if "heart_rate" in parsed_data:
            data_record.heart_rate = int(parsed_data["heart_rate"])
        if "blood_pressure_systolic" in parsed_data:
            data_record.blood_pressure_systolic = int(parsed_data["blood_pressure_systolic"])
        if "blood_pressure_diastolic" in parsed_data:
            data_record.blood_pressure_diastolic = int(parsed_data["blood_pressure_diastolic"])
        if "respiratory_rate" in parsed_data:
            data_record.respiratory_rate = int(parsed_data["respiratory_rate"])
        if "temperature" in parsed_data:
            data_record.temperature = float(parsed_data["temperature"])
        if "spo2" in parsed_data:
            data_record.spo2 = float(parsed_data["spo2"])
        if "weight" in parsed_data:
            data_record.weight = float(parsed_data["weight"])
        if "height" in parsed_data:
            data_record.height = float(parsed_data["height"])
        if "blood_glucose" in parsed_data:
            data_record.blood_glucose = float(parsed_data["blood_glucose"])

        # Extract lab analyzer data
        if "test_code" in parsed_data:
            data_record.test_code = parsed_data["test_code"]
        if "test_name" in parsed_data:
            data_record.test_name = parsed_data["test_name"]
        if "sample_id" in parsed_data:
            data_record.sample_id = parsed_data["sample_id"]
        if "result_value" in parsed_data:
            try:
                data_record.measurement_value = float(parsed_data["result_value"])
            except (ValueError, TypeError):
                data_record.measurement_value = None
        if "unit" in parsed_data or "units" in parsed_data:
            data_record.measurement_unit = parsed_data.get("unit") or parsed_data.get("units")

    # ==========================================================================
    # Alert Management
    # ==========================================================================

    async def create_device_alert(
        self,
        device_id: str,
        alert_type: str,
        alert_severity: str,
        alert_message: str,
        patient_id: Optional[int] = None,
        alert_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create device alert

        Args:
            device_id: Device identifier
            alert_type: Alert type
            alert_severity: Alert severity
            alert_message: Alert message
            patient_id: Patient ID (optional)
            alert_data: Additional alert data

        Returns:
            Dict with alert details
        """
        try:
            # Get device
            query = select(Device).where(Device.device_id == device_id)
            result = await self.db.execute(query)
            device = result.scalar_one_or_none()

            if not device:
                raise ValueError("Device {} not found".format(device_id))

            # Create alert
            alert = DeviceAlert(
                alert_id="ALERT-{}-{}".format(device.device_id, datetime.utcnow().strftime("%Y%m%d%H%M%S")),
                device_id=device.id,
                patient_id=patient_id,
                alert_type=alert_type,
                alert_severity=alert_severity,
                alert_message=alert_message,
                alert_data=alert_data
            )

            self.db.add(alert)
            await self.db.commit()

            logger.info("Created device alert: {}".format(alert.alert_id))

            return {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type,
                "alert_severity": alert.alert_severity,
                "created_at": alert.created_at.isoformat()
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error creating device alert: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create device alert: {}".format(str(e)))


def get_device_integration_service(db):
    """Get or create device integration service instance

    Args:
        db: Database session

    Returns:
        DeviceIntegrationService instance
    """
    return DeviceIntegrationService(db)
