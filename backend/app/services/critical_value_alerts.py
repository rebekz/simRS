"""Critical Value Alert System

Detects critical lab values and sends immediate alerts to physicians
with escalation for unacknowledged alerts.

STORY-022-05: Critical Value Alerts to Physicians
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.notifications import (
    Notification,
    NotificationLog,
    CriticalAlert,
    NotificationStatus,
    NotificationChannel,
    NotificationPriority,
    NotificationType,
)
from app.services.notification_channels import ChannelProviderFactory


logger = logging.getLogger(__name__)


class CriticalValueAlert(object):
    """Critical value alert data"""
    def __init__(self, patient_id, patient_name, mrn, test_name, value,
                 unit, critical_range, ordering_physician, patient_location=None,
                 result_timestamp=None):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.mrn = mrn
        self.test_name = test_name
        self.value = value
        self.unit = unit
        self.critical_range = critical_range
        self.ordering_physician = ordering_physician
        self.patient_location = patient_location
        self.result_timestamp = result_timestamp or datetime.utcnow()


class CriticalValueDetector(object):
    """Detects critical values from lab results"""

    # Default critical value thresholds
    DEFAULT_THRESHOLDS = {
        # Hematology
        "WBC": {
            "critical_low": 2.0,   # x10^9/L
            "critical_high": 50.0,  # x10^9/L
            "unit": "x10^9/L",
            "name": "White Blood Cell Count"
        },
        "Hemoglobin": {
            "critical_low": 7.0,   # g/dL
            "critical_high": 20.0, # g/dL
            "unit": "g/dL",
            "name": "Hemoglobin"
        },
        "Platelets": {
            "critical_low": 20,    # x10^9/L
            "critical_high": 1000, # x10^9/L
            "unit": "x10^9/L",
            "name": "Platelet Count"
        },
        # Chemistry
        "Sodium": {
            "critical_low": 120,   # mmol/L
            "critical_high": 160,  # mmol/L
            "unit": "mmol/L",
            "name": "Sodium"
        },
        "Potassium": {
            "critical_low": 2.5,   # mmol/L
            "critical_high": 6.5,   # mmol/L
            "unit": "mmol/L",
            "name": "Potassium"
        },
        "Glucose": {
            "critical_low": 2.2,   # mmol/L (40 mg/dL)
            "critical_high": 33.3,  # mmol/L (600 mg/dL)
            "unit": "mmol/L",
            "name": "Glucose"
        },
        "Creatinine": {
            "critical_high": 500,   # umol/L
            "unit": "umol/L",
            "name": "Creatinine"
        },
        # Cardiac
        "Troponin": {
            "critical_high": 0.5,   # ug/L
            "unit": "ug/L",
            "name": "Troponin"
        },
        "BNP": {
            "critical_high": 400,   # ng/L
            "unit": "ng/L",
            "name": "B-Type Natriuretic Peptide"
        },
        # Arterial Blood Gas
        "pH": {
            "critical_low": 7.2,
            "critical_high": 7.6,
            "unit": "pH",
            "name": "pH"
        },
        "pO2": {
            "critical_low": 50,    # mm Hg
            "unit": "mm Hg",
            "name": "Partial Pressure of Oxygen"
        },
        "pCO2": {
            "critical_low": 20,    # mm Hg
            "critical_high": 70,   # mm Hg
            "unit": "mm Hg",
            "name": "Partial Pressure of CO2"
        },
    }

    def __init__(self, db):
        self.db = db
        self.thresholds = self.DEFAULT_THRESHOLDS.copy()

    async def check_lab_result(self, lab_result):
        """Check if lab result contains critical value

        Args:
            lab_result: Dictionary with keys test_name, value, unit, etc.

        Returns:
            CriticalValueAlert if critical, None otherwise
        """
        test_name = lab_result.get("test_name", "")
        value = lab_result.get("value")

        if value is None:
            return None

        # Try to find matching threshold
        threshold = self._find_threshold(test_name)
        if not threshold:
            return None

        # Check if value is critical
        critical_low = threshold.get("critical_low")
        critical_high = threshold.get("critical_high")

        is_critical = False
        if critical_low is not None and value < critical_low:
            is_critical = True
            range_str = "< {}".format(critical_low)
        elif critical_high is not None and value > critical_high:
            is_critical = True
            range_str = "> {}".format(critical_high)
        else:
            return None

        # Create critical value alert
        alert = CriticalValueAlert(
            patient_id=lab_result.get("patient_id"),
            patient_name=lab_result.get("patient_name", ""),
            mrn=lab_result.get("mrn", ""),
            test_name=threshold["name"],
            value=value,
            unit=threshold["unit"],
            critical_range=range_str,
            ordering_physician=lab_result.get("ordering_physician"),
            patient_location=lab_result.get("patient_location"),
            result_timestamp=lab_result.get("result_timestamp")
        )

        logger.warning(
            "CRITICAL VALUE DETECTED: {} = {} {} for patient {} ({})".format(
                alert.test_name, alert.value, alert.unit, alert.patient_name, alert.mrn
            )
        )

        return alert

    def _find_threshold(self, test_name):
        """Find threshold for given test name"""
        # Exact match
        if test_name in self.thresholds:
            return self.thresholds[test_name]

        # Partial match (case insensitive)
        test_lower = test_name.lower()
        for key, threshold in self.thresholds.items():
            if key.lower() in test_lower or test_lower in key.lower():
                return threshold

        return None


class CriticalValueEscalationEngine(object):
    """Handles escalation of unacknowledged critical value alerts"""

    ESCALATION_TIMEOUTS = {
        "first_escalation": 300,    # 5 minutes - alert ordering physician again
        "second_escalation": 900,   # 15 minutes - escalate to department head
        "third_escalation": 1800,   # 30 minutes - escalate to chief of staff
    }

    def __init__(self, db):
        self.db = db
        self.running = False

    async def start(self):
        """Start escalation monitoring"""
        if self.running:
            return

        self.running = True
        logger.info("Critical value escalation engine started")

    async def stop(self):
        """Stop escalation monitoring"""
        self.running = False
        logger.info("Critical value escalation engine stopped")

    async def monitor_alerts(self):
        """Background task to monitor unacknowledged alerts"""
        while self.running:
            try:
                await self._check_and_escalate()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error("Error in escalation monitoring: {}".format(e))
                await asyncio.sleep(60)

    async def _check_and_escalate(self):
        """Check for alerts that need escalation"""
        # Find unacknowledged critical alerts
        query = select(Notification).where(
            and_(
                Notification.notification_type == NotificationType.CRITICAL_ALERT,
                Notification.status == NotificationStatus.SENT,
                Notification.created_at < datetime.utcnow() - timedelta(minutes=5)
            )
        )
        result = await self.db.execute(query)
        unacknowledged = result.scalars().all()

        for alert in unacknowledged:
            await self._process_escalation(alert)

    async def _process_escalation(self, alert):
        """Process escalation for a single alert"""
        time_since_sent = datetime.utcnow() - alert.created_at
        minutes_elapsed = time_since_sent.total_seconds() / 60

        escalation_level = alert.metadata.get("escalation_level", 0) if alert.metadata else 0

        # Check if escalation is needed
        should_escalate = False
        new_level = escalation_level

        if escalation_level == 0 and minutes_elapsed >= 5:
            should_escalate = True
            new_level = 1
        elif escalation_level == 1 and minutes_elapsed >= 15:
            should_escalate = True
            new_level = 2
        elif escalation_level == 2 and minutes_elapsed >= 30:
            should_escalate = True
            new_level = 3

        if should_escalate and new_level <= 3:
            await self._escalate_alert(alert, new_level)

    async def _escalate_alert(self, alert, escalation_level):
        """Escalate alert to next level"""
        time_since_sent = datetime.utcnow() - alert.created_at
        minutes_elapsed = time_since_sent.total_seconds() / 60

        metadata = alert.metadata or {}
        old_level = metadata.get("escalation_level", 0)

        # Determine escalation action
        if escalation_level == 1:
            # First escalation - notify ordering physician again via SMS
            recipients = [alert.recipient_id]
            channels = [NotificationChannel.SMS, NotificationChannel.PUSH]
            message = (
                "REMINDER: Critical value for {} ({}: {} {}) requires your "
                "immediate attention. Patient: {} (MRN: {})".format(
                    alert.title,
                    alert.message,
                    "URGENT" if escalation_level >= 1 else "IMPORTANT",
                    alert.metadata.get("patient_name", ""),
                    alert.metadata.get("mrn", "")
                )
            )
        elif escalation_level == 2:
            # Second escalation - notify department head
            department = alert.metadata.get("department", "")
            recipients = await self._get_department_heads(department)
            channels = [NotificationChannel.SMS, NotificationChannel.PUSH, NotificationChannel.EMAIL]
            message = (
                "ESCALATION: Critical value for {} ({}: {} {}) not acknowledged "
                "by ordering physician. Patient: {} (MRN: {}). "
                "Please follow up immediately.".format(
                    alert.title,
                    alert.message,
                    "URGENT",
                    alert.metadata.get("patient_name", ""),
                    alert.metadata.get("mrn", "")
                )
            )
        elif escalation_level == 3:
            # Third escalation - notify chief of staff
            recipients = await self._get_chief_of_staff()
            channels = [NotificationChannel.SMS, NotificationChannel.PUSH, NotificationChannel.EMAIL]
            message = (
                "CRITICAL ESCALATION: Critical value for {} ({}: {} {}) not "
                "acknowledged for 30 minutes. Patient: {} (MRN: {}). "
                "Immediate intervention required.".format(
                    alert.title,
                    alert.message,
                    "CRITICAL",
                    alert.metadata.get("patient_name", ""),
                    alert.metadata.get("mrn", "")
                )
            )
        else:
            return

        # Send escalated notification
        for recipient_id in recipients:
            for channel in channels:
                await self._send_escalation_notification(
                    recipient_id, channel, message, alert, escalation_level
                )

        # Update original alert metadata
        metadata["escalation_level"] = escalation_level
        metadata["escalated_at"] = datetime.utcnow().isoformat()
        alert.metadata = metadata
        alert.updated_at = datetime.utcnow()

        # Log escalation
        log = NotificationLog(
            notification_id=alert.id,
            status="escalated",
            message="Escalated to level {}".format(escalation_level)
        )
        self.db.add(log)
        await self.db.commit()

        logger.warning(
            "Alert {} escalated to level {} ({} minutes)".format(
                alert.id, escalation_level, int(minutes_elapsed)
            )
        )

    async def _get_department_heads(self, department):
        """Get department heads for escalation"""
        # In production, query database
        return [1, 2]  # Mock IDs

    async def _get_chief_of_staff(self):
        """Get chief of staff for escalation"""
        # In production, query database
        return [3]  # Mock ID

    async def _send_escalation_notification(self, recipient_id, channel, message,
                                           original_alert, escalation_level):
        """Send escalation notification"""
        notification = Notification(
            recipient_id=recipient_id,
            user_type="doctor",
            notification_type=NotificationType.CRITICAL_ALERT,
            channel=channel,
            priority=NotificationPriority.URGENT,
            status=NotificationStatus.PENDING,
            title="ESCALATION: Critical Value Alert",
            message=message,
            metadata={
                "original_alert_id": str(original_alert.id),
                "escalation_level": escalation_level,
                "patient_name": original_alert.metadata.get("patient_name"),
                "mrn": original_alert.metadata.get("mrn"),
            },
            scheduled_at=datetime.utcnow()
        )
        self.db.add(notification)
        await self.db.commit()


class CriticalValueAlertService(object):
    """Main service for critical value alerts"""

    def __init__(self, db):
        self.db = db
        self.detector = CriticalValueDetector(db)
        self.escalation_engine = CriticalValueEscalationEngine(db)

    async def process_lab_result(self, lab_result):
        """Process lab result and send alert if critical

        Args:
            lab_result: Dictionary containing lab result data

        Returns:
            Created notification ID if critical, None otherwise
        """
        # Check for critical value
        alert = await self.detector.check_lab_result(lab_result)
        if not alert:
            return None

        # Create and send critical alert
        notification = await self._send_critical_alert(alert)

        # Log the critical value for compliance
        await self._log_critical_value(alert, notification.id)

        return notification.id

    async def _send_critical_alert(self, alert):
        """Send critical value alert to ordering physician"""
        # Build message content
        message = (
            "CRITICAL VALUE ALERT\n\n"
            "Patient: {} (MRN: {})\n"
            "Test: {}\n"
            "Value: {} {}\n"
            "Critical Range: {}\n"
            "Timestamp: {}\n"
            "Ordering Physician: Dr. {}\n"
            "Location: {}\n\n"
            "Please acknowledge immediately and take appropriate action."
        ).format(
            alert.patient_name,
            alert.mrn,
            alert.test_name,
            alert.value,
            alert.unit,
            alert.critical_range,
            alert.result_timestamp.strftime("%Y-%m-%d %H:%M") if alert.result_timestamp else "",
            alert.ordering_physician,
            alert.patient_location or "Not specified"
        )

        # Get ordering physician's contact info
        physician_id = alert.ordering_physician
        if not physician_id:
            logger.error("No ordering physician specified for critical value")
            return None

        # Send notification via multiple channels
        notification_ids = []
        channels = [NotificationChannel.SMS, NotificationChannel.PUSH, NotificationChannel.IN_APP]

        for channel in channels:
            notification = Notification(
                recipient_id=physician_id,
                user_type="doctor",
                notification_type=NotificationType.CRITICAL_ALERT,
                channel=channel,
                priority=NotificationPriority.URGENT,
                status=NotificationStatus.PENDING,
                title="CRITICAL VALUE: {}".format(alert.test_name),
                message=message,
                metadata={
                    "patient_id": alert.patient_id,
                    "patient_name": alert.patient_name,
                    "mrn": alert.mrn,
                    "test_name": alert.test_name,
                    "value": alert.value,
                    "unit": alert.unit,
                    "critical_range": alert.critical_range,
                    "result_timestamp": alert.result_timestamp.isoformat() if alert.result_timestamp else None,
                    "escalation_level": 0,
                },
                scheduled_at=datetime.utcnow()
            )
            self.db.add(notification)
            await self.db.flush()

            # Queue for delivery
            from app.services.notification_queue import get_queue_processor
            processor = get_queue_processor(self.db)
            await processor.enqueue(notification.id, NotificationPriority.URGENT)

            notification_ids.append(notification.id)

        # Create acknowledgment record
        await self._create_acknowledgment_record(alert, notification_ids[0])

        await self.db.commit()
        return notification

    async def _create_acknowledgment_record(self, alert, notification_id):
        """Create critical alert database record for tracking"""
        critical_alert = CriticalAlert(
            patient_id=alert.patient_id,
            patient_name=alert.patient_name,
            mrn=alert.mrn,
            test_name=alert.test_name,
            test_value=str(alert.value),
            test_unit=alert.unit,
            critical_range=alert.critical_range,
            ordering_physician_id=alert.ordering_physician,
            patient_location=alert.patient_location,
            result_timestamp=alert.result_timestamp,
            notification_id=notification_id,
            acknowledged=False,
            escalation_level=0
        )
        self.db.add(critical_alert)
        await self.db.flush()

        logger.info(
            "Created critical alert record {} for patient {} (MRN: {})".format(
                critical_alert.id, alert.patient_name, alert.mrn
            )
        )

    async def _log_critical_value(self, alert, notification_id):
        """Log critical value for regulatory compliance"""
        log = NotificationLog(
            notification_id=notification_id,
            status="critical_value_detected",
            message="Critical value detected and alert sent: {} = {} {}".format(
                alert.test_name, alert.value, alert.unit
            ),
            error_details={
                "patient_id": alert.patient_id,
                "mrn": alert.mrn,
                "value": alert.value,
                "unit": alert.unit,
                "critical_range": alert.critical_range,
                "timestamp": alert.result_timestamp.isoformat() if alert.result_timestamp else None,
            }
        )
        self.db.add(log)
        await self.db.commit()

    async def acknowledge_alert(self, notification_id, physician_id, action_taken):
        """Acknowledge critical value alert

        Args:
            notification_id: Notification ID
            physician_id: Physician ID acknowledging
            action_taken: Description of action taken

        Returns:
            Updated notification
        """
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()

        if not notification:
            raise ValueError("Notification {} not found".format(notification_id))

        # Update notification status
        notification.status = NotificationStatus.DELIVERED
        notification.delivered_at = datetime.utcnow()
        notification.updated_at = datetime.utcnow()

        # Update metadata with acknowledgment
        metadata = notification.metadata or {}
        metadata["acknowledged_by"] = physician_id
        metadata["acknowledged_at"] = datetime.utcnow().isoformat()
        metadata["action_taken"] = action_taken
        notification.metadata = metadata

        # Also update the CriticalAlert record
        critical_alert_result = await self.db.execute(
            select(CriticalAlert).where(CriticalAlert.notification_id == notification_id)
        )
        critical_alert = critical_alert_result.scalar_one_or_none()

        if critical_alert:
            critical_alert.acknowledged = True
            critical_alert.acknowledged_at = datetime.utcnow()
            critical_alert.acknowledged_by = physician_id
            critical_alert.action_taken = action_taken
            critical_alert.updated_at = datetime.utcnow()

        # Log acknowledgment
        log = NotificationLog(
            notification_id=notification_id,
            status="acknowledged",
            message="Acknowledged by physician {}. Action: {}".format(
                physician_id, action_taken
            ),
            error_details={
                "acknowledged_by": physician_id,
                "action_taken": action_taken,
                "acknowledged_at": metadata["acknowledged_at"]
            }
        )
        self.db.add(log)

        await self.db.commit()

        logger.info(
            "Critical value alert {} acknowledged by physician {}".format(
                notification_id, physician_id
            )
        )

        return notification

    async def get_unacknowledged_alerts(self, physician_id=None):
        """Get unacknowledged critical value alerts

        Args:
            physician_id: Optional filter by physician

        Returns:
            List of unacknowledged alerts
        """
        filters = [
            Notification.notification_type == NotificationType.CRITICAL_ALERT,
            Notification.status.in_([NotificationStatus.SENT, NotificationStatus.DELIVERED])
        ]

        if physician_id:
            filters.append(Notification.recipient_id == physician_id)

        query = select(Notification).where(
            and_(*filters)
        ).order_by(Notification.created_at.desc())

        result = await self.db.execute(query)
        return result.scalars().all()
