"""Queue Management Service for STORY-010: Queue Management System

This module provides services for:
- Queue ticket generation and management
- Queue recall and calling
- Queue statistics and monitoring
- Digital display support
- Mobile queue status
- SMS/WhatsApp notifications
- Queue transfer and cancellation
- Priority queue management
- Offline queue operation

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, case, literal_column

from app.models.queue import (
    QueueTicket, QueueRecall, QueueNotification,
    QueueStatisticsCache, QueueSettings, QueueTransfer,
)
from app.models.patient import Patient
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.queue import QueueDepartment, QueueStatus, QueuePriority


logger = logging.getLogger(__name__)


class QueueNotFoundError(Exception):
    """Queue ticket not found error"""
    pass


class QueueOperationError(Exception):
    """Queue operation error"""
    pass


class QueueManagementService(object):
    """Service for queue management operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_queue_ticket(
        self,
        patient_id: int,
        department: QueueDepartment,
        priority: QueuePriority = QueuePriority.NORMAL,
        poli_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        appointment_id: Optional[int] = None,
        created_by: Optional[int] = None,
    ) -> QueueTicket:
        """Create a new queue ticket

        Args:
            patient_id: Patient ID
            department: Department to queue for
            priority: Queue priority
            poli_id: Polyclinic ID (for POLI department)
            doctor_id: Doctor ID
            appointment_id: Appointment ID (if pre-booked)
            created_by: User ID creating the ticket

        Returns:
            Created QueueTicket instance
        """
        # Generate ticket number
        ticket_number = await self._generate_ticket_number(department)

        # Calculate queue position
        queue_position = await self._get_next_queue_position(department)

        # Calculate people ahead
        people_ahead = max(0, queue_position - 1)

        # Calculate estimated wait time
        estimated_wait = await self._calculate_wait_time(department, people_ahead)

        # Create ticket
        ticket = QueueTicket(
            ticket_number=ticket_number,
            department=department,
            date=date.today(),
            patient_id=patient_id,
            priority=priority,
            status=QueueStatus.WAITING,
            poli_id=poli_id,
            doctor_id=doctor_id,
            appointment_id=appointment_id,
            queue_position=queue_position,
            people_ahead=people_ahead,
            estimated_wait_minutes=estimated_wait,
        )

        self.db.add(ticket)
        await self.db.flush()

        # Send notification if enabled
        await self._send_queue_notification(ticket, "issued")

        # Update statistics cache
        await self._update_queue_statistics(department)

        logger.info("Queue ticket created: {}".format(ticket_number))

        return ticket

    async def call_next_patient(
        self,
        department: QueueDepartment,
        counter: int,
        poli_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
        called_by: int = None,
    ) -> Optional[Dict[str, any]]:
        """Call next patient in queue

        Args:
            department: Department to call from
            counter: Counter number
            poli_id: Polyclinic ID (for POLI department)
            doctor_id: Doctor ID
            called_by: User ID calling the patient

        Returns:
            Called ticket info or None if no patients waiting
        """
        # Get next waiting ticket
        ticket = await self._get_next_waiting_ticket(department, poli_id, doctor_id)

        if not ticket:
            return None

        # Update ticket status
        ticket.status = QueueStatus.CALLED
        ticket.called_at = datetime.utcnow()
        ticket.serving_counter = counter

        # Create recall record
        recall = QueueRecall(
            ticket_id=ticket.id,
            counter=counter,
            announced=True,
            called_by_id=called_by or 0,
        )

        self.db.add(recall)
        await self.db.flush()

        # Send notification
        await self._send_queue_notification(ticket, "called")

        # Get patient info
        patient = await self._get_patient(ticket.patient_id)

        # Update statistics
        await self._update_queue_statistics(department)

        return {
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "patient_name": patient.full_name if patient else "Unknown",
            "patient_id": ticket.patient_id,
            "counter": counter,
            "queue_position": ticket.queue_position,
        }

    async def mark_patient_served(
        self,
        ticket_id: int,
        service_outcome: str = "completed",
        served_by: int = None,
    ) -> Dict[str, any]:
        """Mark patient as served

        Args:
            ticket_id: Ticket ID
            service_outcome: Service outcome (completed, referred, etc.)
            served_by: User ID marking as served

        Returns:
            Updated ticket info

        Raises:
            QueueNotFoundError: If ticket not found
        """
        # Get ticket
        ticket = await self._get_ticket_by_id(ticket_id)

        if not ticket:
            raise QueueNotFoundError("Ticket not found")

        # Update ticket
        ticket.status = QueueStatus.SERVED
        ticket.service_completed_at = datetime.utcnow()
        ticket.served_at = datetime.utcnow()

        # Calculate service time
        if ticket.service_started_at:
            service_time = (ticket.service_completed_at - ticket.service_started_at).total_seconds() / 60
        else:
            service_time = None

        await self.db.flush()

        # Update recall record
        query = select(QueueRecall).where(
            and_(
                QueueRecall.ticket_id == ticket_id,
                QueueRecall.patient_present.is_(None)
            )
        ).order_by(QueueRecall.recall_time.desc())

        result = await self.db.execute(query)
        recall = result.scalar_one_or_none()

        if recall:
            recall.patient_present = True

        # Send notification
        await self._send_queue_notification(ticket, "served")

        # Update statistics
        await self._update_queue_statistics(ticket.department)

        logger.info("Ticket {} marked as served".format(ticket.ticket_number))

        return {
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "status": ticket.status.value,
            "service_time_minutes": service_time,
        }

    async def mark_patient_no_show(
        self,
        ticket_id: int,
        reason: str = "Patient not present",
        marked_by: int = None,
    ) -> Dict[str, any]:
        """Mark patient as no-show

        Args:
            ticket_id: Ticket ID
            reason: Reason for no-show
            marked_by: User ID marking as no-show

        Returns:
            Updated ticket info

        Raises:
            QueueNotFoundError: If ticket not found
        """
        # Get ticket
        ticket = await self._get_ticket_by_id(ticket_id)

        if not ticket:
            raise QueueNotFoundError("Ticket not found")

        # Update ticket
        ticket.status = QueueStatus.SKIPPED
        ticket.cancelled_at = datetime.utcnow()
        ticket.cancellation_reason = reason

        await self.db.flush()

        # Update recall record
        query = select(QueueRecall).where(
            and_(
                QueueRecall.ticket_id == ticket_id,
                QueueRecall.patient_present.is_(None)
            )
        ).order_by(QueueRecall.recall_time.desc())

        result = await self.db.execute(query)
        recall = result.scalar_one_or_none()

        if recall:
            recall.patient_present = False
            recall.no_show_time = datetime.utcnow()

        # Update statistics
        await self._update_queue_statistics(ticket.department)

        logger.info("Ticket {} marked as no-show".format(ticket.ticket_number))

        return {
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "status": ticket.status.value,
        }

    async def cancel_queue_ticket(
        self,
        ticket_id: int,
        reason: str,
        cancelled_by: int = None,
    ) -> Dict[str, any]:
        """Cancel a queue ticket

        Args:
            ticket_id: Ticket ID
            reason: Cancellation reason
            cancelled_by: User ID cancelling

        Returns:
            Cancelled ticket info

        Raises:
            QueueNotFoundError: If ticket not found
            QueueOperationError: If ticket cannot be cancelled
        """
        # Get ticket
        ticket = await self._get_ticket_by_id(ticket_id)

        if not ticket:
            raise QueueNotFoundError("Ticket not found")

        # Check if can be cancelled
        if ticket.status in [QueueStatus.SERVED, QueueStatus.CANCELLED]:
            raise QueueOperationError(
                "Cannot cancel ticket with status: {}".format(ticket.status.value)
            )

        # Update ticket
        ticket.status = QueueStatus.CANCELLED
        ticket.cancelled_at = datetime.utcnow()
        ticket.cancellation_reason = reason

        await self.db.flush()

        # Send notification
        await self._send_queue_notification(ticket, "cancelled")

        # Update statistics
        await self._update_queue_statistics(ticket.department)

        logger.info("Ticket {} cancelled: {}".format(ticket.ticket_number, reason))

        return {
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "status": ticket.status.value,
            "reason": reason,
        }

    async def transfer_queue_ticket(
        self,
        ticket_id: int,
        to_department: QueueDepartment,
        to_poli_id: Optional[int] = None,
        to_doctor_id: Optional[int] = None,
        reason: str = None,
        transferred_by: int = None,
    ) -> Dict[str, any]:
        """Transfer queue ticket to another department/poli/doctor

        Args:
            ticket_id: Ticket ID
            to_department: Target department
            to_poli_id: Target polyclinic ID
            to_doctor_id: Target doctor ID
            reason: Transfer reason
            transferred_by: User ID initiating transfer

        Returns:
            New ticket info

        Raises:
            QueueNotFoundError: If ticket not found
            QueueOperationError: If ticket cannot be transferred
        """
        # Get ticket
        ticket = await self._get_ticket_by_id(ticket_id)

        if not ticket:
            raise QueueNotFoundError("Ticket not found")

        # Check if can be transferred
        if ticket.status in [QueueStatus.SERVED, QueueStatus.CANCELLED]:
            raise QueueOperationError(
                "Cannot transfer ticket with status: {}".format(ticket.status.value)
            )

        # Create transfer record
        transfer = QueueTransfer(
            ticket_id=ticket_id,
            from_department=ticket.department,
            to_department=to_department,
            from_poli_id=ticket.poli_id,
            to_poli_id=to_poli_id,
            from_doctor_id=ticket.doctor_id,
            to_doctor_id=to_doctor_id,
            reason=reason or "Patient transfer",
            transferred_by_id=transferred_by or 0,
        )

        self.db.add(transfer)
        await self.db.flush()

        # Cancel old ticket
        old_status = ticket.status
        ticket.status = QueueStatus.CANCELLED
        ticket.cancelled_at = datetime.utcnow()
        ticket.cancellation_reason = "Transferred to {}".format(to_department.value)

        # Create new ticket
        new_ticket = await self.create_queue_ticket(
            patient_id=ticket.patient_id,
            department=to_department,
            priority=ticket.priority,
            poli_id=to_poli_id,
            doctor_id=to_doctor_id,
            created_by=transferred_by,
        )

        # Link to appointment if exists
        if ticket.appointment_id:
            new_ticket.appointment_id = ticket.appointment_id

        await self.db.flush()

        logger.info(
            "Ticket {} transferred to {} as {}".format(
                ticket.ticket_number,
                to_department.value,
                new_ticket.ticket_number
            )
        )

        return {
            "old_ticket_number": ticket.ticket_number,
            "new_ticket_id": new_ticket.id,
            "new_ticket_number": new_ticket.ticket_number,
            "new_department": to_department.value,
            "new_queue_position": new_ticket.queue_position,
            "estimated_wait_minutes": new_ticket.estimated_wait_minutes,
        }

    async def get_department_queue_status(
        self,
        department: QueueDepartment,
        poli_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
    ) -> Dict[str, any]:
        """Get current queue status for department

        Args:
            department: Department to check
            poli_id: Filter by polyclinic
            doctor_id: Filter by doctor

        Returns:
            Queue status summary
        """
        today = date.today()

        # Build filters
        filters = [
            QueueTicket.department == department,
            QueueTicket.date == today,
        ]

        if poli_id:
            filters.append(QueueTicket.poli_id == poli_id)
        if doctor_id:
            filters.append(QueueTicket.doctor_id == doctor_id)

        # Count by status
        query = select(
            QueueTicket.status,
            func.count(QueueTicket.id)
        ).where(
            and_(*filters)
        ).group_by(QueueTicket.status)

        result = await self.db.execute(query)
        status_counts = {row[0]: row[1] for row in result}

        # Get currently serving
        serving_query = select(QueueTicket).where(
            and_(
                *filters,
                QueueTicket.status == QueueStatus.CALLED
            )
        ).order_by(QueueTicket.called_at)

        serving_result = await self.db.execute(serving_query)
        serving_tickets = serving_result.scalars().all()

        serving_list = []
        for t in serving_tickets:
            patient = await self._get_patient(t.patient_id)
            serving_list.append({
                "ticket_number": t.ticket_number,
                "counter": t.serving_counter,
                "patient_name": patient.full_name if patient else "Unknown",
                "called_at": t.called_at.isoformat() if t.called_at else None,
            })

        return {
            "department": department.value,
            "poli_id": poli_id,
            "doctor_id": doctor_id,
            "waiting": status_counts.get(QueueStatus.WAITING, 0),
            "called": status_counts.get(QueueStatus.CALLED, 0),
            "served": status_counts.get(QueueStatus.SERVED, 0),
            "skipped": status_counts.get(QueueStatus.SKIPPED, 0),
            "cancelled": status_counts.get(QueueStatus.CANCELLED, 0),
            "currently_serving": serving_list,
            "average_wait_time_minutes": await self._get_average_wait_time(department),
        }

    async def get_digital_display_data(
        self,
        department: QueueDepartment,
        poli_id: Optional[int] = None,
    ) -> Dict[str, any]:
        """Get data for digital queue display

        Args:
            department: Department to display
            poli_id: Filter by polyclinic

        Returns:
            Display data with current and recent tickets
        """
        today = date.today()

        # Get currently serving
        serving_query = select(QueueTicket).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today,
                QueueTicket.status == QueueStatus.CALLED,
            )
        )

        if poli_id:
            serving_query = serving_query.where(QueueTicket.poli_id == poli_id)

        serving_query = serving_query.order_by(QueueTicket.called_at.desc())

        serving_result = await self.db.execute(serving_query)
        serving_tickets = serving_result.scalars().all()

        current_serving = []
        for t in serving_tickets:
            patient = await self._get_patient(t.patient_id)
            current_serving.append({
                "ticket_number": t.ticket_number,
                "counter": t.serving_counter,
                "patient_name": patient.full_name if patient else "Unknown",
                "called_at": t.called_at.isoformat() if t.called_at else None,
            })

        # Get waiting (next 5)
        waiting_query = select(QueueTicket).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today,
                QueueTicket.status == QueueStatus.WAITING,
            )
        )

        if poli_id:
            waiting_query = waiting_query.where(QueueTicket.poli_id == poli_id)

        waiting_query = waiting_query.order_by(
            QueueTicket.priority.desc(),
            QueueTicket.queue_position.asc()
        ).limit(5)

        waiting_result = await self.db.execute(waiting_query)
        waiting_tickets = waiting_result.scalars().all()

        waiting_list = []
        for t in waiting_tickets:
            waiting_list.append({
                "ticket_number": t.ticket_number,
                "queue_position": t.queue_position,
                "estimated_wait_minutes": t.estimated_wait_minutes,
            })

        # Get recently served (last 3)
        recent_query = select(QueueTicket).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today,
                QueueTicket.status == QueueStatus.SERVED,
            )
        )

        if poli_id:
            recent_query = recent_query.where(QueueTicket.poli_id == poli_id)

        recent_query = recent_query.order_by(
            QueueTicket.served_at.desc()
        ).limit(3)

        recent_result = await self.db.execute(recent_query)
        recent_tickets = recent_result.scalars().all()

        recent_list = []
        for t in recent_tickets:
            patient = await self._get_patient(t.patient_id)
            recent_list.append({
                "ticket_number": t.ticket_number,
                "counter": t.serving_counter,
                "patient_name": patient.full_name if patient else "Unknown",
                "served_at": t.served_at.isoformat() if t.served_at else None,
            })

        # Get queue settings
        settings = await self._get_department_settings(department)

        return {
            "department": department.value,
            "poli_id": poli_id,
            "current_serving": current_serving,
            "waiting": waiting_list,
            "recently_served": recent_list,
            "total_waiting": len(waiting_list),
            "refresh_interval_seconds": settings.display_refresh_interval_seconds if settings else 10,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_patient_queue_status(
        self,
        ticket_id: int,
    ) -> Dict[str, any]:
        """Get queue status for patient's ticket

        Args:
            ticket_id: Ticket ID

        Returns:
            Patient queue status

        Raises:
            QueueNotFoundError: If ticket not found
        """
        # Get ticket
        ticket = await self._get_ticket_by_id(ticket_id)

        if not ticket:
            raise QueueNotFoundError("Ticket not found")

        # Get patient
        patient = await self._get_patient(ticket.patient_id)

        # Get current serving info
        currently_serving = None
        if ticket.status == QueueStatus.WAITING:
            serving_query = select(QueueTicket).where(
                and_(
                    QueueTicket.department == ticket.department,
                    QueueTicket.date == ticket.date,
                    QueueTicket.status == QueueStatus.CALLED,
                )
            )

            if ticket.poli_id:
                serving_query = serving_query.where(QueueTicket.poli_id == ticket.poli_id)

            if ticket.doctor_id:
                serving_query = serving_query.where(QueueTicket.doctor_id == ticket.doctor_id)

            serving_result = await self.db.execute(serving_query)
            serving_tickets = serving_result.scalars().all()

            if serving_tickets:
                t = serving_tickets[0]
                currently_serving = {
                    "ticket_number": t.ticket_number,
                    "counter": t.serving_counter,
                }

        return {
            "ticket_number": ticket.ticket_number,
            "patient_name": patient.full_name if patient else "Unknown",
            "department": ticket.department.value,
            "status": ticket.status.value,
            "queue_position": ticket.queue_position,
            "people_ahead": ticket.people_ahead,
            "estimated_wait_minutes": ticket.estimated_wait_minutes,
            "serving_counter": ticket.serving_counter,
            "called_at": ticket.called_at.isoformat() if ticket.called_at else None,
            "issued_at": ticket.issued_at.isoformat() if ticket.issued_at else None,
            "currently_serving": currently_serving,
        }

    async def get_queue_statistics(
        self,
        department: Optional[QueueDepartment] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, any]:
        """Get queue statistics

        Args:
            department: Filter by department (None for all)
            start_date: Start date (default: today)
            end_date: End date (default: today)

        Returns:
            Queue statistics
        """
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = date.today()

        # Build base query
        filters = [
            QueueTicket.date >= start_date,
            QueueTicket.date <= end_date,
        ]

        if department:
            filters.append(QueueTicket.department == department)

        # Get counts by status
        query = select(
            QueueTicket.status,
            func.count(QueueTicket.id)
        ).where(
            and_(*filters)
        ).group_by(QueueTicket.status)

        result = await self.db.execute(query)
        status_counts = {row[0]: row[1] for row in result}

        # Get counts by priority
        priority_query = select(
            QueueTicket.priority,
            func.count(QueueTicket.id)
        ).where(
            and_(*filters)
        ).group_by(QueueTicket.priority)

        priority_result = await self.db.execute(priority_query)
        priority_counts = {row[0]: row[1] for row in priority_result}

        # Calculate averages
        avg_wait_query = select(
            func.avg(
                func.extract(
                    "epoch",
                    QueueTicket.called_at - QueueTicket.issued_at
                ) / 60
            )
        ).where(
            and_(
                *filters,
                QueueTicket.called_at.isnot(None)
            )
        )

        avg_wait_result = await self.db.execute(avg_wait_query)
        avg_wait = avg_wait_result.scalar()

        avg_service_query = select(
            func.avg(
                func.extract(
                    "epoch",
                    QueueTicket.service_completed_at - QueueTicket.service_started_at
                ) / 60
            )
        ).where(
            and_(
                *filters,
                QueueTicket.service_completed_at.isnot(None),
                QueueTicket.service_started_at.isnot(None)
            )
        )

        avg_service_result = await self.db.execute(avg_service_query)
        avg_service = avg_service_result.scalar()

        return {
            "department": department.value if department else "all",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_issued": sum(status_counts.values()),
            "by_status": {
                "waiting": status_counts.get(QueueStatus.WAITING, 0),
                "called": status_counts.get(QueueStatus.CALLED, 0),
                "served": status_counts.get(QueueStatus.SERVED, 0),
                "skipped": status_counts.get(QueueStatus.SKIPPED, 0),
                "cancelled": status_counts.get(QueueStatus.CANCELLED, 0),
            },
            "by_priority": {
                "normal": priority_counts.get(QueuePriority.NORMAL, 0),
                "priority": priority_counts.get(QueuePriority.PRIORITIZED, 0),
                "urgent": priority_counts.get(QueuePriority.URGENT, 0),
            },
            "average_wait_time_minutes": float(avg_wait) if avg_wait else None,
            "average_service_time_minutes": float(avg_service) if avg_service else None,
        }

    # ==============================================================================
    # Private Helper Methods
    # ==============================================================================

    async def _get_ticket_by_id(self, ticket_id: int) -> Optional[QueueTicket]:
        """Get ticket by ID

        Args:
            ticket_id: Ticket ID

        Returns:
            QueueTicket instance or None
        """
        query = select(QueueTicket).where(QueueTicket.id == ticket_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_patient(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID

        Args:
            patient_id: Patient ID

        Returns:
            Patient instance or None
        """
        query = select(Patient).where(Patient.id == patient_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _generate_ticket_number(
        self,
        department: QueueDepartment,
    ) -> str:
        """Generate ticket number for department

        Args:
            department: Department

        Returns:
            Ticket number (e.g., "P-001")
        """
        prefixes = {
            QueueDepartment.POLI: "P",
            QueueDepartment.FARMASI: "F",
            QueueDepartment.LAB: "L",
            QueueDepartment.RADIOLOGI: "R",
            QueueDepartment.KASIR: "K",
            QueueDepartment.IGD: "E",
        }

        prefix = prefixes.get(department, "X")

        # Get next sequence
        today = date.today()

        query = select(func.count()).select_from(QueueTicket).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today
            )
        )

        result = await self.db.execute(query)
        count = result.scalar() or 0

        sequence = count + 1

        return "{0}-{1:03d}".format(prefix, sequence)

    async def _get_next_queue_position(
        self,
        department: QueueDepartment,
    ) -> int:
        """Get next queue position for department

        Args:
            department: Department

        Returns:
            Next queue position (1-indexed)
        """
        today = date.today()

        query = select(func.count()).select_from(QueueTicket).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today,
                QueueTicket.status == QueueStatus.WAITING
            )
        )

        result = await self.db.execute(query)
        waiting_count = result.scalar() or 0

        return waiting_count + 1

    async def _get_next_waiting_ticket(
        self,
        department: QueueDepartment,
        poli_id: Optional[int] = None,
        doctor_id: Optional[int] = None,
    ) -> Optional[QueueTicket]:
        """Get next waiting ticket

        Args:
            department: Department
            poli_id: Polyclinic ID
            doctor_id: Doctor ID

        Returns:
            Next waiting ticket or None
        """
        today = date.today()

        query = select(QueueTicket).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today,
                QueueTicket.status == QueueStatus.WAITING,
            )
        )

        if poli_id:
            query = query.where(QueueTicket.poli_id == poli_id)

        if doctor_id:
            query = query.where(QueueTicket.doctor_id == doctor_id)

        # Order by priority (urgent first), then queue position
        query = query.order_by(
            case(
                (QueueTicket.priority == QueuePriority.URGENT, 1),
                (QueueTicket.priority == QueuePriority.PRIORITIZED, 2),
                (QueueTicket.priority == QueuePriority.NORMAL, 3),
                else_=4
            ),
            QueueTicket.queue_position.asc()
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _calculate_wait_time(
        self,
        department: QueueDepartment,
        people_ahead: int,
    ) -> int:
        """Calculate estimated wait time

        Args:
            department: Department
            people_ahead: Number of people ahead

        Returns:
            Estimated wait time in minutes
        """
        # Get department settings
        settings = await self._get_department_settings(department)

        if settings:
            service_time = settings.average_service_time_minutes
        else:
            # Default service times by department
            service_times = {
                QueueDepartment.POLI: 10,
                QueueDepartment.FARMASI: 5,
                QueueDepartment.LAB: 3,
                QueueDepartment.RADIOLOGI: 15,
                QueueDepartment.KASIR: 3,
                QueueDepartment.IGD: 5,
            }
            service_time = service_times.get(department, 5)

        return people_ahead * service_time

    async def _get_department_settings(
        self,
        department: QueueDepartment,
    ) -> Optional[QueueSettings]:
        """Get department queue settings

        Args:
            department: Department

        Returns:
            QueueSettings or None
        """
        query = select(QueueSettings).where(
            QueueSettings.department == department
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _send_queue_notification(
        self,
        ticket: QueueTicket,
        notification_type: str,
    ):
        """Send queue notification (SMS/WhatsApp)

        Args:
            ticket: Queue ticket
            notification_type: Type of notification (issued, called, served, cancelled)
        """
        # Get patient
        patient = await self._get_patient(ticket.patient_id)

        if not patient or not patient.phone:
            return

        # Get settings
        settings = await self._get_department_settings(ticket.department)

        if not settings or not settings.enable_sms:
            return

        # Check if should send for this type
        should_send = False
        if notification_type == "issued" and settings.sms_on_issue:
            should_send = True
        elif notification_type == "called" and settings.sms_on_call:
            should_send = True

        if not should_send:
            return

        # Build message
        if notification_type == "issued":
            message = (
                "SIMRS: Nomor antrian Anda: {0}. "
                "Estimasi waktu tunggu: {1} menit. "
                "Department: {2}"
            ).format(
                ticket.ticket_number,
                ticket.estimated_wait_minutes or 0,
                ticket.department.value
            )
        elif notification_type == "called":
            message = (
                "SIMRS: Nomor antrian {0} telah dipanggil. "
                "Silakan ke loket {1}."
            ).format(
                ticket.ticket_number,
                ticket.serving_counter or 1
            )
        elif notification_type == "served":
            message = (
                "SIMRS: Terima kasih. "
                "Nomor antrian {0} telah dilayani."
            ).format(ticket.ticket_number)
        elif notification_type == "cancelled":
            message = (
                "SIMRS: Nomor antrian {0} telah dibatalkan. "
                "Silakan mengambil antrian baru."
            ).format(ticket.ticket_number)
        else:
            return

        # Create notification record
        notification = QueueNotification(
            ticket_id=ticket.id,
            notification_type="sms",
            message=message,
            phone_number=patient.phone,
            sent=False,  # Will be sent by background job
        )

        self.db.add(notification)
        await self.db.flush()

        logger.info(
            "Queue notification created: {} - {}".format(
                ticket.ticket_number,
                notification_type
            )
        )

    async def _update_queue_statistics(
        self,
        department: QueueDepartment,
    ):
        """Update queue statistics cache

        Args:
            department: Department to update
        """
        today = date.today()

        # Get or create cache entry
        query = select(QueueStatisticsCache).where(
            and_(
                QueueStatisticsCache.department == department,
                QueueStatisticsCache.date == today
            )
        )

        result = await self.db.execute(query)
        cache = result.scalar_one_or_none()

        if not cache:
            cache = QueueStatisticsCache(
                department=department,
                date=today,
            )
            self.db.add(cache)

        # Calculate statistics
        filters = [
            QueueTicket.department == department,
            QueueTicket.date == today,
        ]

        # Total issued
        issued_query = select(func.count()).select_from(QueueTicket).where(
            and_(*filters)
        )
        issued_result = await self.db.execute(issued_query)
        cache.total_issued = issued_result.scalar() or 0

        # Total served
        served_filters = filters + [QueueTicket.status == QueueStatus.SERVED]
        served_query = select(func.count()).select_from(QueueTicket).where(
            and_(*served_filters)
        )
        served_result = await self.db.execute(served_query)
        cache.total_served = served_result.scalar() or 0

        # Total waiting
        waiting_filters = filters + [QueueTicket.status == QueueStatus.WAITING]
        waiting_query = select(func.count()).select_from(QueueTicket).where(
            and_(*waiting_filters)
        )
        waiting_result = await self.db.execute(waiting_query)
        cache.total_waiting = waiting_result.scalar() or 0

        # Total cancelled
        cancelled_filters = filters + [QueueTicket.status == QueueStatus.CANCELLED]
        cancelled_query = select(func.count()).select_from(QueueTicket).where(
            and_(*cancelled_filters)
        )
        cancelled_result = await self.db.execute(cancelled_query)
        cache.total_cancelled = cancelled_result.scalar() or 0

        # Average wait time
        avg_wait_query = select(
            func.avg(
                func.extract(
                    "epoch",
                    QueueTicket.called_at - QueueTicket.issued_at
                ) / 60
            )
        ).where(
            and_(
                *filters,
                QueueTicket.called_at.isnot(None)
            )
        )

        avg_wait_result = await self.db.execute(avg_wait_query)
        cache.average_wait_time_minutes = avg_wait_result.scalar()

        # Set expiry
        cache.expires_at = datetime.utcnow() + timedelta(minutes=15)

        await self.db.flush()

    async def _get_average_wait_time(
        self,
        department: QueueDepartment,
    ) -> Optional[float]:
        """Get average wait time for department

        Args:
            department: Department

        Returns:
            Average wait time in minutes
        """
        today = date.today()

        query = select(
            func.avg(
                func.extract(
                    "epoch",
                    QueueTicket.called_at - QueueTicket.issued_at
                ) / 60
            )
        ).where(
            and_(
                QueueTicket.department == department,
                QueueTicket.date == today,
                QueueTicket.called_at.isnot(None)
            )
        )

        result = await self.db.execute(query)
        return result.scalar()


# Factory function
def get_queue_management_service(db: AsyncSession) -> QueueManagementService:
    """Get queue management service"""
    return QueueManagementService(db)
