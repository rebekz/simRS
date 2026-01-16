"""Online Appointment Booking Service for STORY-009: Online Appointment Booking

This module provides services for:
- Patient appointment booking with slot availability
- Real-time slot availability display
- Appointment confirmation and reminders
- Appointment cancellation and rescheduling
- Queue number reservation for appointments
- Mobile JKN API integration for BPJS patients

Python 3.5+ compatible
"""

import logging
from datetime import datetime, date, time, timedelta
from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc, func, not_

from app.models.appointments import (
    Appointment, AppointmentSlot, AppointmentType,
    AppointmentStatus, BookingChannel, AppointmentPriority,
)
from app.models.patient import Patient
from app.models.user import User
from app.models.queue import QueueTicket, QueueDepartment, QueueStatus, QueuePriority
from app.models.audit_log import AuditLog
from app.models.master_data import Poli


logger = logging.getLogger(__name__)


class AppointmentValidationError(Exception):
    """Appointment validation error"""
    pass


class AppointmentUnavailableError(Exception):
    """Appointment slot unavailable error"""
    pass


class AppointmentBookingService(object):
    """Service for appointment booking operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def book_appointment(
        self,
        patient_id: int,
        department_id: int,
        doctor_id: Optional[int],
        appointment_date: date,
        appointment_time: time,
        appointment_type: AppointmentType,
        reason_for_visit: Optional[str] = None,
        symptoms: Optional[str] = None,
        duration_minutes: int = 30,
        booking_channel: BookingChannel = BookingChannel.WEB,
        priority: AppointmentPriority = AppointmentPriority.ROUTINE,
        booked_by: Optional[int] = None,
    ) -> Appointment:
        """Book a new appointment

        Args:
            patient_id: Patient ID
            department_id: Department ID
            doctor_id: Doctor ID (optional)
            appointment_date: Appointment date
            appointment_time: Appointment time
            appointment_type: Type of appointment
            reason_for_visit: Patient's reason
            symptoms: Patient's symptoms
            duration_minutes: Expected duration
            booking_channel: How appointment was booked
            priority: Appointment priority
            booked_by: User ID making booking

        Returns:
            Created Appointment instance

        Raises:
            AppointmentValidationError: If validation fails
            AppointmentUnavailableError: If slot is unavailable
        """
        # Validate appointment data
        await self._validate_appointment_data(
            patient_id, department_id, doctor_id,
            appointment_date, appointment_time, duration_minutes
        )

        # Check slot availability
        is_available = await self._check_slot_availability(
            department_id=department_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            duration_minutes=duration_minutes,
        )

        if not is_available:
            raise AppointmentUnavailableError(
                "Slot tidak tersedia pada tanggal dan jam tersebut"
            )

        # Generate appointment number
        appointment_number = await self._generate_appointment_number()

        # Calculate end time
        start_datetime = datetime.combine(appointment_date, appointment_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        end_time = end_datetime.time()

        # Create appointment
        appointment = Appointment(
            appointment_number=appointment_number,
            patient_id=patient_id,
            department_id=department_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            appointment_type=appointment_type,
            status=AppointmentStatus.SCHEDULED,
            booking_channel=booking_channel,
            priority=priority,
            reason_for_visit=reason_for_visit,
            symptoms=symptoms,
        )

        self.db.add(appointment)
        await self.db.flush()

        # Create audit log
        await self._create_appointment_audit_log(
            appointment,
            booked_by,
            "CREATE"
        )

        logger.info(
            "Appointment booked: {} - Patient {} - Doctor {} - {}".format(
                appointment_number,
                patient_id,
                doctor_id,
                appointment_date
            )
        )

        return appointment

    async def get_available_slots(
        self,
        department_id: int,
        doctor_id: Optional[int],
        appointment_date: date,
    ) -> List[Dict[str, any]]:
        """Get available appointment slots for doctor and date

        Args:
            department_id: Department ID
            doctor_id: Doctor ID
            appointment_date: Appointment date

        Returns:
            List of available time slots
        """
        # Get slot configuration for doctor/department
        slots = await self._get_slot_configuration(
            department_id=department_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
        )

        # Get existing appointments
        existing_appointments = await self._get_existing_appointments(
            department_id=department_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
        )

        # Calculate available slots
        available_slots = []

        for slot in slots:
            slot_start = slot["start_time"]
            slot_end = slot["end_time"]

            # Check if slot is already booked
            is_booked = False
            for appt in existing_appointments:
                appt_start = appt.appointment_time
                appt_end = appt.end_time

                # Check for overlap
                if self._time_ranges_overlap(
                    slot_start, slot_end,
                    appt_start, appt_end
                ):
                    is_booked = True
                    break

            if not is_booked:
                available_slots.append({
                    "start_time": slot_start.strftime("%H:%M"),
                    "end_time": slot_end.strftime("%H:%M"),
                    "available": True,
                })

        return available_slots

    async def cancel_appointment(
        self,
        appointment_id: int,
        cancellation_reason: str,
        cancelled_by: int,
    ) -> Appointment:
        """Cancel an appointment

        Args:
            appointment_id: Appointment ID
            cancellation_reason: Reason for cancellation
            cancelled_by: User ID cancelling

        Returns:
            Cancelled appointment

        Raises:
            AppointmentValidationError: If validation fails
        """
        # Get appointment
        appointment = await self._get_appointment_by_id(appointment_id)

        if not appointment:
            raise AppointmentValidationError("Appointment not found")

        # Check if can be cancelled
        if appointment.status in [
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.NO_SHOW
        ]:
            raise AppointmentValidationError(
                "Cannot cancel appointment with status: {}".format(
                    appointment.status.value
                )
            )

        # Update appointment
        old_status = appointment.status
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = cancellation_reason
        appointment.cancelled_at = datetime.utcnow()
        appointment.cancelled_by = cancelled_by

        await self.db.flush()

        # Cancel associated queue ticket if exists
        if appointment.queue_number:
            await self._cancel_queue_ticket(appointment)

        # Create audit log
        await self._create_appointment_audit_log(
            appointment,
            cancelled_by,
            "CANCEL",
            {
                "old_status": old_status.value,
                "cancellation_reason": cancellation_reason,
            }
        )

        logger.info(
            "Appointment cancelled: {} - Reason: {}".format(
                appointment.appointment_number,
                cancellation_reason
            )
        )

        return appointment

    async def reschedule_appointment(
        self,
        appointment_id: int,
        new_appointment_date: date,
        new_appointment_time: time,
        rescheduled_by: int,
    ) -> Dict[str, any]:
        """Reschedule an appointment

        Args:
            appointment_id: Appointment ID
            new_appointment_date: New appointment date
            new_appointment_time: New appointment time
            rescheduled_by: User ID rescheduling

        Returns:
            Updated appointment info

        Raises:
            AppointmentValidationError: If validation fails
            AppointmentUnavailableError: If new slot is unavailable
        """
        # Get appointment
        appointment = await self._get_appointment_by_id(appointment_id)

        if not appointment:
            raise AppointmentValidationError("Appointment not found")

        # Check if can be rescheduled
        if appointment.status in [
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.NO_SHOW
        ]:
            raise AppointmentValidationError(
                "Cannot reschedule appointment with status: {}".format(
                    appointment.status.value
                )
            )

        # Store old details
        old_date = appointment.appointment_date
        old_time = appointment.appointment_time

        # Check new slot availability
        is_available = await self._check_slot_availability(
            department_id=appointment.department_id,
            doctor_id=appointment.doctor_id,
            appointment_date=new_appointment_date,
            appointment_time=new_appointment_time,
            duration_minutes=appointment.duration_minutes,
            exclude_appointment_id=appointment_id,
        )

        if not is_available:
            raise AppointmentUnavailableError(
                "Slot baru tidak tersedia"
            )

        # Update appointment
        appointment.appointment_date = new_appointment_date
        appointment.appointment_time = new_appointment_time

        # Recalculate end time
        start_datetime = datetime.combine(new_appointment_date, new_appointment_time)
        end_datetime = start_datetime + timedelta(minutes=appointment.duration_minutes)
        appointment.end_time = end_datetime.time()

        await self.db.flush()

        # Cancel old queue ticket if exists
        if appointment.queue_number:
            await self._cancel_queue_ticket(appointment)

        # Create audit log
        await self._create_appointment_audit_log(
            appointment,
            rescheduled_by,
            "RESCHEDULE",
            {
                "old_date": old_date.isoformat() if old_date else None,
                "old_time": old_time.strftime("%H:%M") if old_time else None,
                "new_date": new_appointment_date.isoformat(),
                "new_time": new_appointment_time.strftime("%H:%M"),
            }
        )

        logger.info(
            "Appointment rescheduled: {} from {} {} to {} {}".format(
                appointment.appointment_number,
                old_date, old_time,
                new_appointment_date, new_appointment_time
            )
        )

        return {
            "appointment_id": appointment.id,
            "appointment_number": appointment.appointment_number,
            "old_date": old_date.isoformat() if old_date else None,
            "old_time": old_time.strftime("%H:%M") if old_time else None,
            "new_date": new_appointment_date.isoformat(),
            "new_time": new_appointment_time.strftime("%H:%M"),
            "message": "Appointment rescheduled successfully",
        }

    async def confirm_appointment(
        self,
        appointment_id: int,
    ) -> Appointment:
        """Confirm an appointment

        Args:
            appointment_id: Appointment ID

        Returns:
            Confirmed appointment

        Raises:
            AppointmentValidationError: If validation fails
        """
        # Get appointment
        appointment = await self._get_appointment_by_id(appointment_id)

        if not appointment:
            raise AppointmentValidationError("Appointment not found")

        # Update status
        appointment.status = AppointmentStatus.CONFIRMED

        await self.db.flush()

        logger.info("Appointment confirmed: {}".format(appointment.appointment_number))

        return appointment

    async def check_in_appointment(
        self,
        appointment_id: int,
    ) -> Dict[str, any]:
        """Check in patient for appointment

        Args:
            appointment_id: Appointment ID

        Returns:
            Check-in result with queue number

        Raises:
            AppointmentValidationError: If validation fails
        """
        # Get appointment
        appointment = await self._get_appointment_by_id(appointment_id)

        if not appointment:
            raise AppointmentValidationError("Appointment not found")

        # Check if can check in
        if appointment.status not in [
            AppointmentStatus.SCHEDULED,
            AppointmentStatus.CONFIRMED
        ]:
            raise AppointmentValidationError(
                "Cannot check in appointment with status: {}".format(
                    appointment.status.value
                )
            )

        # Determine department for queue
        department = await self._get_queue_department(appointment.department_id)

        if not department:
            raise AppointmentValidationError("Invalid department for queue")

        # Generate queue number
        from app.services.queue_management import get_queue_management_service

        queue_service = get_queue_management_service(self.db)

        # Create queue ticket
        queue_ticket = await queue_service.create_queue_ticket(
            patient_id=appointment.patient_id,
            department=department,
            priority=QueuePriority.NORMAL,
            poli_id=appointment.department_id,
            doctor_id=appointment.doctor_id,
            appointment_id=appointment.id,
            created_by=None,
        )

        # Update appointment
        appointment.status = AppointmentStatus.CHECKED_IN
        appointment.check_in_time = datetime.utcnow()
        appointment.queue_number = queue_ticket.ticket_number
        appointment.queue_position = queue_ticket.queue_position
        appointment.estimated_wait_time_minutes = queue_ticket.estimated_wait_minutes

        await self.db.flush()

        logger.info(
            "Appointment checked in: {} - Queue: {}".format(
                appointment.appointment_number,
                queue_ticket.ticket_number
            )
        )

        return {
            "appointment_id": appointment.id,
            "appointment_number": appointment.appointment_number,
            "queue_number": queue_ticket.ticket_number,
            "queue_position": queue_ticket.queue_position,
            "estimated_wait_minutes": queue_ticket.estimated_wait_minutes,
            "check_in_time": appointment.check_in_time.isoformat() if appointment.check_in_time else None,
            "message": "Checked in successfully",
        }

    async def get_patient_appointments(
        self,
        patient_id: int,
        status: Optional[AppointmentStatus] = None,
        upcoming_only: bool = False,
        limit: int = 20,
    ) -> List[Dict[str, any]]:
        """Get appointments for patient

        Args:
            patient_id: Patient ID
            status: Filter by status
            upcoming_only: Only show upcoming appointments
            limit: Max results

        Returns:
            List of appointments
        """
        query = select(Appointment).where(
            Appointment.patient_id == patient_id
        )

        if status:
            query = query.where(Appointment.status == status)

        if upcoming_only:
            today = date.today()
            query = query.where(
                and_(
                    Appointment.appointment_date >= today,
                    Appointment.status.in_([
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED,
                    ])
                )
            )

        query = query.order_by(
            Appointment.appointment_date.asc(),
            Appointment.appointment_time.asc()
        ).limit(limit)

        result = await self.db.execute(query)
        appointments = result.scalars().all()

        return [
            {
                "id": a.id,
                "appointment_number": a.appointment_number,
                "appointment_date": a.appointment_date.isoformat() if a.appointment_date else None,
                "appointment_time": a.appointment_time.strftime("%H:%M") if a.appointment_time else None,
                "end_time": a.end_time.strftime("%H:%M") if a.end_time else None,
                "appointment_type": a.appointment_type.value,
                "status": a.status.value,
                "department_id": a.department_id,
                "doctor_id": a.doctor_id,
                "reason_for_visit": a.reason_for_visit,
                "queue_number": a.queue_number,
                "booking_channel": a.booking_channel.value,
            }
            for a in appointments
        ]

    async def get_doctor_appointments(
        self,
        doctor_id: int,
        appointment_date: date,
    ) -> List[Dict[str, any]]:
        """Get appointments for doctor on specific date

        Args:
            doctor_id: Doctor ID
            appointment_date: Appointment date

        Returns:
            List of appointments
        """
        query = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_date == appointment_date,
            )
        ).order_by(
            Appointment.appointment_time.asc()
        )

        result = await self.db.execute(query)
        appointments = result.scalars().all()

        appointment_list = []
        for a in appointments:
            patient = await self._get_patient(a.patient_id)

            appointment_list.append({
                "id": a.id,
                "appointment_number": a.appointment_number,
                "appointment_time": a.appointment_time.strftime("%H:%M") if a.appointment_time else None,
                "end_time": a.end_time.strftime("%H:%M") if a.end_time else None,
                "duration_minutes": a.duration_minutes,
                "appointment_type": a.appointment_type.value,
                "status": a.status.value,
                "priority": a.priority.value,
                "patient_name": patient.full_name if patient else "Unknown",
                "reason_for_visit": a.reason_for_visit,
                "symptoms": a.symptoms,
                "notes": a.notes,
            })

        return appointment_list

    # ==============================================================================
    # Private Helper Methods
    # ==============================================================================

    async def _get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID

        Args:
            appointment_id: Appointment ID

        Returns:
            Appointment instance or None
        """
        query = select(Appointment).where(Appointment.id == appointment_id)
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

    async def _validate_appointment_data(
        self,
        patient_id: int,
        department_id: int,
        doctor_id: Optional[int],
        appointment_date: date,
        appointment_time: time,
        duration_minutes: int,
    ):
        """Validate appointment data

        Args:
            patient_id: Patient ID
            department_id: Department ID
            doctor_id: Doctor ID
            appointment_date: Appointment date
            appointment_time: Appointment time
            duration_minutes: Duration in minutes

        Raises:
            AppointmentValidationError: If validation fails
        """
        errors = []

        # Validate patient exists
        patient = await self._get_patient(patient_id)
        if not patient:
            errors.append("Patient not found")

        # Validate date is not in the past
        if appointment_date < date.today():
            errors.append("Appointment date cannot be in the past")

        # Validate duration
        if duration_minutes <= 0 or duration_minutes > 240:  # Max 4 hours
            errors.append("Duration must be between 1 and 240 minutes")

        # Validate time is within working hours
        if not self._is_working_hours(appointment_time):
            errors.append("Appointment time must be within working hours")

        if errors:
            raise AppointmentValidationError("; ".join(errors))

    async def _check_slot_availability(
        self,
        department_id: int,
        doctor_id: Optional[int],
        appointment_date: date,
        appointment_time: time,
        duration_minutes: int,
        exclude_appointment_id: Optional[int] = None,
    ) -> bool:
        """Check if appointment slot is available

        Args:
            department_id: Department ID
            doctor_id: Doctor ID
            appointment_date: Appointment date
            appointment_time: Appointment time
            duration_minutes: Duration in minutes
            exclude_appointment_id: Appointment ID to exclude from check

        Returns:
            True if available, False otherwise
        """
        # Get existing appointments
        query = select(Appointment).where(
            and_(
                Appointment.department_id == department_id,
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.CHECKED_IN,
                ]),
            )
        )

        if doctor_id:
            query = query.where(Appointment.doctor_id == doctor_id)

        if exclude_appointment_id:
            query = query.where(Appointment.id != exclude_appointment_id)

        result = await self.db.execute(query)
        existing_appointments = result.scalars().all()

        # Calculate new appointment time range
        new_start = appointment_time
        new_end = (datetime.combine(date.today(), appointment_time) +
                  timedelta(minutes=duration_minutes)).time()

        # Check for overlaps
        for appt in existing_appointments:
            appt_start = appt.appointment_time
            appt_end = appt.end_time

            if self._time_ranges_overlap(
                new_start, new_end,
                appt_start, appt_end
            ):
                return False  # Slot is taken

        return True  # Slot is available

    async def _get_slot_configuration(
        self,
        department_id: int,
        doctor_id: Optional[int],
        appointment_date: date,
    ) -> List[Dict[str, any]]:
        """Get slot configuration for doctor/department

        Args:
            department_id: Department ID
            doctor_id: Doctor ID
            appointment_date: Appointment date

        Returns:
            List of configured time slots
        """
        # Check for explicit slot configuration
        query = select(AppointmentSlot).where(
            and_(
                AppointmentSlot.department_id == department_id,
                AppointmentSlot.slot_date == appointment_date,
                AppointmentSlot.is_available == True,
            )
        )

        if doctor_id:
            query = query.where(AppointmentSlot.doctor_id == doctor_id)
        else:
            query = query.where(AppointmentSlot.doctor_id.is_(None))

        query = query.order_by(AppointmentSlot.start_time)

        result = await self.db.execute(query)
        slots = result.scalars().all()

        if slots:
            # Return configured slots
            return [
                {
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "max_bookings": s.max_bookings,
                }
                for s in slots
            ]

        # Return default working hours slots
        return self._get_default_slots()

    def _get_default_slots(self) -> List[Dict[str, any]]:
        """Get default time slots based on working hours

        Returns:
            List of default time slots
        """
        # Default working hours: 08:00 - 17:00
        # Default slot duration: 30 minutes
        slots = []

        start_hour = 8
        end_hour = 17
        slot_duration = 30  # minutes

        current_time = time(hour=start_hour, minute=0)

        while current_time < time(hour=end_hour):
            end_time = (
                datetime.combine(date.today(), current_time) +
                timedelta(minutes=slot_duration)
            ).time()

            slots.append({
                "start_time": current_time,
                "end_time": end_time,
                "max_bookings": 1,
            })

            # Move to next slot
            current_time = end_time

        return slots

    async def _get_existing_appointments(
        self,
        department_id: int,
        doctor_id: Optional[int],
        appointment_date: date,
    ) -> List[Appointment]:
        """Get existing appointments for slot calculation

        Args:
            department_id: Department ID
            doctor_id: Doctor ID
            appointment_date: Appointment date

        Returns:
            List of existing appointments
        """
        query = select(Appointment).where(
            and_(
                Appointment.department_id == department_id,
                Appointment.appointment_date == appointment_date,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.CHECKED_IN,
                ]),
            )
        )

        if doctor_id:
            query = query.where(Appointment.doctor_id == doctor_id)

        query = query.order_by(Appointment.appointment_time)

        result = await self.db.execute(query)
        return result.scalars().all()

    def _time_ranges_overlap(
        self,
        start1: time,
        end1: time,
        start2: time,
        end2: time,
    ) -> bool:
        """Check if two time ranges overlap

        Args:
            start1: First range start
            end1: First range end
            start2: Second range start
            end2: Second range end

        Returns:
            True if ranges overlap
        """
        return start1 < end2 and start2 < end1

    def _is_working_hours(self, appointment_time: time) -> bool:
        """Check if time is within working hours

        Args:
            appointment_time: Time to check

        Returns:
            True if within working hours
        """
        # Default working hours: 08:00 - 17:00
        start_time = time(hour=8, minute=0)
        end_time = time(hour=17, minute=0)

        return start_time <= appointment_time < end_time

    async def _generate_appointment_number(self) -> str:
        """Generate unique appointment number

        Returns:
            Appointment number (format:APT-YYYYMMDD-XXXXX)
        """
        today = date.today()
        date_str = today.strftime("%Y%m%d")

        # Get count for today
        query = select(func.count()).select_from(Appointment).where(
            Appointment.created_at >= datetime.combine(today, datetime.min.time())
        )

        result = await self.db.execute(query)
        count = result.scalar() or 0

        sequence = count + 1

        return "APT-{0}-{1:05d}".format(date_str, sequence)

    async def _get_queue_department(self, department_id: int) -> Optional[QueueDepartment]:
        """Get queue department from department ID

        Args:
            department_id: Department ID

        Returns:
            QueueDepartment or None
        """
        # This is a simplified mapping - in production, this would
        # be based on department configuration
        from app.models.master_data import Department

        query = select(Department).where(Department.id == department_id)
        result = await self.db.execute(query)
        department = result.scalar_one_or_none()

        if not department:
            return None

        # Map department name to queue department
        dept_name_lower = department.name.lower() if department.name else ""

        if "poli" in dept_name_lower or "clinic" in dept_name_lower:
            return QueueDepartment.POLI
        elif "farmasi" in dept_name_lower or "pharmacy" in dept_name_lower:
            return QueueDepartment.FARMASI
        elif "lab" in dept_name_lower or "laboratory" in dept_name_lower:
            return QueueDepartment.LAB
        elif "radiologi" in dept_name_lower or "radiology" in dept_name_lower:
            return QueueDepartment.RADIOLOGI
        elif "kasir" in dept_name_lower or "cashier" in dept_name_lower:
            return QueueDepartment.KASIR
        elif "igd" in dept_name_lower or "emergency" in dept_name_lower:
            return QueueDepartment.IGD

        return QueueDepartment.POLI  # Default

    async def _cancel_queue_ticket(self, appointment: Appointment):
        """Cancel associated queue ticket

        Args:
            appointment: Appointment with queue number
        """
        if not appointment.queue_number:
            return

        query = select(QueueTicket).where(
            and_(
                QueueTicket.ticket_number == appointment.queue_number,
                QueueTicket.status == QueueStatus.WAITING
            )
        )

        result = await self.db.execute(query)
        ticket = result.scalar_one_or_none()

        if ticket:
            ticket.status = QueueStatus.CANCELLED
            ticket.cancelled_at = datetime.utcnow()
            ticket.cancellation_reason = "Appointment cancelled"

            await self.db.flush()

    async def _create_appointment_audit_log(
        self,
        appointment: Appointment,
        user_id: int,
        action: str,
        additional_data: Optional[Dict] = None,
    ):
        """Create audit log for appointment

        Args:
            appointment: Appointment
            user_id: User ID
            action: Action performed
            additional_data: Additional data
        """
        # Get user info
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        username = user.username if user else "system"

        audit_data = {
            "appointment_number": appointment.appointment_number,
            "patient_id": appointment.patient_id,
            "department_id": appointment.department_id,
            "doctor_id": appointment.doctor_id,
            "appointment_date": appointment.appointment_date.isoformat() if appointment.appointment_date else None,
            "appointment_time": appointment.appointment_time.strftime("%H:%M") if appointment.appointment_time else None,
            "appointment_type": appointment.appointment_type.value,
        }

        if additional_data:
            audit_data.update(additional_data)

        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type="Appointment",
            resource_id=appointment.appointment_number,
            request_path="/appointments",
            request_method="POST",
            success=True,
            additional_data=audit_data,
        )

        self.db.add(audit_log)
        await self.db.flush()


# Factory function
def get_appointment_booking_service(db: AsyncSession) -> AppointmentBookingService:
    """Get appointment booking service"""
    return AppointmentBookingService(db)
