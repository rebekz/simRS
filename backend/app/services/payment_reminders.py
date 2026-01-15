"""Payment Reminder Service

STORY-022-08: Payment Due Reminders
Service for payment reminders, invoice delivery, and payment tracking.

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.notifications import (
    Notification,
    NotificationLog,
    NotificationStatus,
    NotificationChannel,
    NotificationPriority,
    NotificationType,
)
from app.services.notification_preferences import get_preference_manager


logger = logging.getLogger(__name__)


class PaymentReminderService(object):
    """Service for payment reminders and invoice delivery"""

    # Reminder schedules (days before/after due date)
    REMINDER_SCHEDULES = {
        "7_days_before": -7,    # 7 days before due
        "3_days_before": -3,    # 3 days before due
        "due_date": 0,           # On due date
        "overdue": 1,            # 1 day after due
        "overdue_7": 7,          # 7 days after due
        "overdue_30": 30,        # 30 days after due
    }

    # Message templates
    REMINDER_7D_TEMPLATE = (
        "PAYMENT REMINDER\n\n"
        "Dear {patient_name},\n\n"
        "You have an invoice due in 7 days:\n\n"
        "Invoice #: {invoice_number}\n"
        "Amount Due: {amount}\n"
        "Due Date: {due_date}\n"
        "Description: {description}\n\n"
        "Please ensure payment is made by the due date.\n\n"
        "Payment Options:\n"
        "- Pay online: {payment_link}\n"
        "- Bank Transfer: {bank_details}\n"
        "- In-person: Visit cashier\n\n"
        "Thank you!"
    )

    REMINDER_3D_TEMPLATE = (
        "PAYMENT DUE SOON - 3 DAYS\n\n"
        "Dear {patient_name},\n\n"
        "This is a reminder that your payment is due in 3 days:\n\n"
        "Invoice #: {invoice_number}\n"
        "Amount Due: {amount}\n"
        "Due Date: {due_date}\n\n"
        "Please make payment promptly to avoid late fees.\n\n"
        "Quick Pay: {payment_link}\n\n"
        "Thank you!"
    )

    DUE_DATE_TEMPLATE = (
        "PAYMENT DUE TODAY\n\n"
        "Dear {patient_name},\n\n"
        "Your payment is due TODAY:\n\n"
        "Invoice #: {invoice_number}\n"
        "Amount Due: {amount}\n"
        "Due Date: {due_date}\n\n"
        "Please make payment now to avoid late fees.\n\n"
        "Pay Now: {payment_link}\n\n"
        "Thank you!"
    )

    OVERDUE_TEMPLATE = (
        "PAYMENT OVERDUE\n\n"
        "Dear {patient_name},\n\n"
        "Your payment is OVERDUE:\n\n"
        "Invoice #: {invoice_number}\n"
        "Amount Due: {amount}\n"
        "Due Date: {due_date}\n"
        "Days Overdue: {days_overdue}\n\n"
        "Please make payment immediately to avoid service disruption.\n\n"
        "Pay Now: {payment_link}\n"
        "Contact Us: {hospital_phone}\n\n"
        "Thank you!"
    )

    INVOICE_TEMPLATE = (
        "INVOICE - {hospital_name}\n\n"
        "Dear {patient_name},\n\n"
        "Your invoice is ready:\n\n"
        "Invoice #: {invoice_number}\n"
        "Date: {invoice_date}\n"
        "Amount Due: {amount}\n"
        "Due Date: {due_date}\n\n"
        "Services:\n"
        "{services}\n\n"
        "Total: {amount}\n\n"
        "Please pay by: {due_date}\n\n"
        "Payment Link: {payment_link}\n"
        "View Invoice: {invoice_link}\n\n"
        "Thank you for choosing {hospital_name}!"
    )

    PAYMENT_CONFIRMED_TEMPLATE = (
        "PAYMENT RECEIVED\n\n"
        "Dear {patient_name},\n\n"
        "Your payment has been received:\n\n"
        "Invoice #: {invoice_number}\n"
        "Amount Paid: {amount}\n"
        "Payment Date: {payment_date}\n"
        "Transaction ID: {transaction_id}\n\n"
        "Thank you for your payment!\n"
        "Remaining Balance: {remaining_balance}\n\n"
        "{hospital_name}"
    )

    INSURANCE_CLAIM_SUBMITTED = (
        "INSURANCE CLAIM SUBMITTED\n\n"
        "Dear {patient_name},\n\n"
        "Your BPJS insurance claim has been submitted:\n\n"
        "Invoice #: {invoice_number}\n"
        "Claim Amount: {amount}\n"
        "Claim Date: {claim_date}\n\n"
        "We will notify you when the claim is processed.\n\n"
        "Claim ID: {claim_id}\n\n"
        "Thank you!"
    )

    INSURANCE_CLAIM_APPROVED = (
        "INSURANCE CLAIM APPROVED\n\n"
        "Dear {patient_name},\n\n"
        "Good news! Your BPJS insurance claim has been APPROVED:\n\n"
        "Invoice #: {invoice_number}\n"
        "Approved Amount: {amount}\n"
        "Claim ID: {claim_id}\n\n"
        "Your insurance has covered this service.\n\n"
        "Patient Responsibility: {patient_responsibility}\n\n"
        "Thank you!"
    )

    INSURANCE_CLAIM_REJECTED = (
        "INSURANCE CLAIM UPDATE\n\n"
        "Dear {patient_name},\n\n"
        "Your BPJS insurance claim requires attention:\n\n"
        "Invoice #: {invoice_number}\n"
        "Claim Amount: {amount}\n"
        "Status: {status}\n"
        "Reason: {reason}\n\n"
        "Patient Responsibility: {patient_responsibility}\n\n"
        "Please contact our billing department for assistance.\n"
        "Hospital Phone: {hospital_phone}\n\n"
        "You may appeal this decision within {appeal_days} days.\n\n"
        "Thank you!"
    )

    def __init__(self, db):
        self.db = db
        self.preference_manager = get_preference_manager(db)

    async def schedule_payment_reminders(self, invoice_data):
        """Schedule all reminders for an invoice

        Args:
            invoice_data: Dictionary with invoice details
                - patient_id, patient_name
                - invoice_id, invoice_number
                - amount, due_date
                - description, services
                - payment_link, invoice_link

        Returns:
            Dictionary with scheduled reminder IDs
        """
        try:
            due_date = invoice_data.get("due_date")
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            elif isinstance(due_date, datetime):
                due_date = due_date.date()

            scheduled = {}

            # Schedule pre-due reminders
            for reminder_type, days_offset in self.REMINDER_SCHEDULES.items():
                if "before" in reminder_type or reminder_type == "due_date":
                    reminder_date = due_date + timedelta(days=days_offset)
                    reminder_at = datetime.combine(reminder_date, datetime.min.time()) + timedelta(hours=9)

                    # Only schedule if in future
                    if reminder_at > datetime.utcnow():
                        notification_id = await self._schedule_reminder(
                            invoice_data,
                            reminder_at,
                            reminder_type
                        )
                        scheduled[reminder_type] = notification_id

            logger.info(
                "Scheduled {} payment reminders for invoice {}".format(
                    len(scheduled), invoice_data.get("invoice_id")
                )
            )

            return scheduled

        except Exception as e:
            logger.error("Error scheduling payment reminders: {}".format(e))
            return {}

    async def send_invoice_delivery(self, invoice_data):
        """Send invoice to patient immediately

        Args:
            invoice_data: Invoice details

        Returns:
            Notification ID or None
        """
        try:
            # Check preferences (invoice delivery important, default to email + in-app)
            enabled_channels = await self.preference_manager.get_enabled_channels(
                invoice_data.get("patient_id"),
                "patient",
                "payment_reminder"
            )

            # Ensure email is included for invoices
            if "email" not in enabled_channels and "in_app" not in enabled_channels:
                enabled_channels = ["email", "in_app"]

            # Format services list
            services = invoice_data.get("services", [])
            if isinstance(services, list):
                services_text = "\n".join(["- {}".format(s) for s in services])
            else:
                services_text = str(services)

            message = self.INVOICE_TEMPLATE.format(
                patient_name=invoice_data.get("patient_name"),
                hospital_name=invoice_data.get("hospital_name", "SIMRS Hospital"),
                invoice_number=invoice_data.get("invoice_number"),
                invoice_date=invoice_data.get("invoice_date", datetime.utcnow().strftime("%Y-%m-%d")),
                amount=invoice_data.get("amount"),
                due_date=invoice_data.get("due_date", datetime.utcnow().strftime("%Y-%m-%d")),
                services=services_text,
                payment_link=invoice_data.get("payment_link", "https://portal.simrs.hospital/pay"),
                invoice_link=invoice_data.get("invoice_link", "https://portal.simrs.hospital/invoices")
            )

            # Send to enabled channels
            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=invoice_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.PAYMENT_REMINDER,
                    channel=channel,
                    priority=NotificationPriority.NORMAL,
                    status=NotificationStatus.PENDING,
                    title="Invoice: " + invoice_data.get("invoice_number"),
                    message=message,
                    metadata={
                        "invoice_id": invoice_data.get("invoice_id"),
                        "invoice_number": invoice_data.get("invoice_number"),
                        "amount": invoice_data.get("amount"),
                        "reminder_type": "invoice_delivery",
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent invoice delivery for invoice {}".format(
                    invoice_data.get("invoice_number")
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending invoice delivery: {}".format(e))
            await self.db.rollback()
            return None

    async def send_payment_confirmation(self, payment_data):
        """Send payment confirmation to patient

        Args:
            payment_data: Payment details
                - patient_id, patient_name
                - invoice_id, invoice_number
                - amount, payment_date
                - transaction_id, remaining_balance

        Returns:
            Notification ID or None
        """
        try:
            # Payment confirmations always sent (in-app + email)
            channels = [NotificationChannel.IN_APP, NotificationChannel.EMAIL]

            message = self.PAYMENT_CONFIRMED_TEMPLATE.format(
                patient_name=payment_data.get("patient_name"),
                invoice_number=payment_data.get("invoice_number"),
                amount=payment_data.get("amount"),
                payment_date=payment_data.get("payment_date", datetime.utcnow().strftime("%Y-%m-%d")),
                transaction_id=payment_data.get("transaction_id"),
                remaining_balance=payment_data.get("remaining_balance", "0"),
                hospital_name=payment_data.get("hospital_name", "SIMRS Hospital")
            )

            notification_ids = []
            for channel in channels:
                notification = Notification(
                    recipient_id=payment_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.PAYMENT_REMINDER,
                    channel=channel,
                    priority=NotificationPriority.NORMAL,
                    status=NotificationStatus.PENDING,
                    title="Payment Received - " + payment_data.get("invoice_number"),
                    message=message,
                    metadata={
                        "invoice_id": payment_data.get("invoice_id"),
                        "transaction_id": payment_data.get("transaction_id"),
                        "amount": payment_data.get("amount"),
                        "reminder_type": "payment_confirmed",
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent payment confirmation for invoice {}".format(
                    payment_data.get("invoice_number")
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending payment confirmation: {}".format(e))
            await self.db.rollback()
            return None

    async def send_insurance_claim_notification(self, claim_data):
        """Send insurance claim status notification

        Args:
            claim_data: Claim details
                - patient_id, patient_name
                - invoice_id, invoice_number
                - claim_id, amount
                - status (submitted, approved, rejected)
                - reason (for rejected)
                - patient_responsibility
                - appeal_days

        Returns:
            Notification ID or None
        """
        try:
            status = claim_data.get("status", "").lower()

            if status == "submitted":
                template = self.INSURANCE_CLAIM_SUBMITTED
                title = "BPJS Claim Submitted"
                priority = NotificationPriority.NORMAL
            elif status == "approved":
                template = self.INSURANCE_CLAIM_APPROVED
                title = "BPJS Claim Approved"
                priority = NotificationPriority.NORMAL
            else:
                template = self.INSURANCE_CLAIM_REJECTED
                title = "BPJS Claim Update - Action Required"
                priority = NotificationPriority.HIGH

            # Check preferences
            enabled_channels = await self.preference_manager.get_enabled_channels(
                claim_data.get("patient_id"),
                "patient",
                "payment_reminder"
            )

            if not enabled_channels:
                return None

            message = template.format(
                patient_name=claim_data.get("patient_name"),
                invoice_number=claim_data.get("invoice_number"),
                amount=claim_data.get("amount"),
                claim_date=claim_data.get("claim_date", datetime.utcnow().strftime("%Y-%m-%d")),
                claim_id=claim_data.get("claim_id"),
                status=claim_data.get("status"),
                reason=claim_data.get("reason", "Please contact billing"),
                patient_responsibility=claim_data.get("patient_responsibility", claim_data.get("amount")),
                hospital_phone=claim_data.get("hospital_phone", "Contact hospital"),
                appeal_days=claim_data.get("appeal_days", 30)
            )

            # Send to enabled channels
            notification_ids = []
            for channel in self._get_channel_objects(enabled_channels):
                notification = Notification(
                    recipient_id=claim_data.get("patient_id"),
                    user_type="patient",
                    notification_type=NotificationType.PAYMENT_REMINDER,
                    channel=channel,
                    priority=priority,
                    status=NotificationStatus.PENDING,
                    title=title,
                    message=message,
                    metadata={
                        "invoice_id": claim_data.get("invoice_id"),
                        "claim_id": claim_data.get("claim_id"),
                        "status": status,
                        "reminder_type": "insurance_claim",
                    },
                    scheduled_at=datetime.utcnow()
                )
                self.db.add(notification)
                await self.db.flush()
                notification_ids.append(notification.id)

            await self.db.commit()

            logger.info(
                "Sent insurance claim notification ({}) to patient {}".format(
                    status, claim_data.get("patient_id")
                )
            )

            return notification_ids[0] if notification_ids else None

        except Exception as e:
            logger.error("Error sending insurance claim notification: {}".format(e))
            await self.db.rollback()
            return None

    async def cancel_payment_reminders(self, invoice_id):
        """Cancel all pending reminders for an invoice

        Args:
            invoice_id: Invoice ID

        Returns:
            Number of reminders cancelled
        """
        try:
            # Find all pending reminders for this invoice
            query = select(Notification).where(
                and_(
                    Notification.notification_type == NotificationType.PAYMENT_REMINDER,
                    Notification.status == NotificationStatus.PENDING,
                    Notification.metadata["invoice_id"].astext == str(invoice_id)
                )
            )
            result = await self.db.execute(query)
            notifications = result.scalars().all()

            # Cancel each reminder
            cancelled = 0
            for notification in notifications:
                notification.status = NotificationStatus.CANCELLED
                notification.updated_at = datetime.utcnow()
                cancelled += 1

            await self.db.commit()

            logger.info(
                "Cancelled {} payment reminders for invoice {}".format(
                    cancelled, invoice_id
                )
            )

            return cancelled

        except Exception as e:
            logger.error("Error cancelling reminders: {}".format(e))
            await self.db.rollback()
            return 0

    async def _schedule_reminder(self, invoice_data, scheduled_at, reminder_type):
        """Schedule a payment reminder

        Args:
            invoice_data: Invoice details
            scheduled_at: When to send
            reminder_type: Type of reminder

        Returns:
            Notification ID or None
        """
        try:
            # Select template based on type
            if reminder_type == "7_days_before":
                template = self.REMINDER_7D_TEMPLATE
                priority = NotificationPriority.NORMAL
            elif reminder_type == "3_days_before":
                template = self.REMINDER_3D_TEMPLATE
                priority = NotificationPriority.NORMAL
            elif reminder_type == "due_date":
                template = self.DUE_DATE_TEMPLATE
                priority = NotificationPriority.HIGH
            else:
                template = self.OVERDUE_TEMPLATE
                priority = NotificationPriority.HIGH

            # Calculate days overdue for overdue template
            days_overdue = 0
            if "overdue" in reminder_type:
                days = reminder_type.replace("overdue_", "")
                days_overdue = int(days) if days.isdigit() else 1

            message = template.format(
                patient_name=invoice_data.get("patient_name"),
                invoice_number=invoice_data.get("invoice_number"),
                amount=invoice_data.get("amount"),
                due_date=invoice_data.get("due_date"),
                description=invoice_data.get("description", "Hospital services"),
                payment_link=invoice_data.get("payment_link", "https://portal.simrs.hospital/pay"),
                bank_details=invoice_data.get("bank_details", "Transfer to BCA 1234567890"),
                hospital_phone=invoice_data.get("hospital_phone", "123-456-7890"),
                days_overdue=days_overdue
            )

            notification = Notification(
                recipient_id=invoice_data.get("patient_id"),
                user_type="patient",
                notification_type=NotificationType.PAYMENT_REMINDER,
                channel=NotificationChannel.SMS,  # Default to SMS
                priority=priority,
                status=NotificationStatus.PENDING,
                title="Payment Reminder",
                message=message,
                metadata={
                    "invoice_id": invoice_data.get("invoice_id"),
                    "invoice_number": invoice_data.get("invoice_number"),
                    "amount": invoice_data.get("amount"),
                    "reminder_type": reminder_type,
                },
                scheduled_at=scheduled_at
            )
            self.db.add(notification)
            await self.db.flush()

            return notification.id

        except Exception as e:
            logger.error("Error scheduling reminder: {}".format(e))
            return None

    def _get_channel_objects(self, channel_names):
        """Convert channel names to NotificationChannel enums"""
        channel_map = {
            "email": NotificationChannel.EMAIL,
            "sms": NotificationChannel.SMS,
            "push": NotificationChannel.PUSH,
            "in_app": NotificationChannel.IN_APP,
            "whatsapp": NotificationChannel.WHATSAPP
        }
        return [channel_map.get(ch) for ch in channel_names if ch in channel_map]


def get_payment_reminder_service(db):
    """Get or create payment reminder service instance

    Args:
        db: Database session

    Returns:
        PaymentReminderService instance
    """
    return PaymentReminderService(db)
