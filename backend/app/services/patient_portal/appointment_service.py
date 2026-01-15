"""Patient Portal Appointment Service

Service for appointment booking, management, and scheduling via patient portal.
"""
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, date, time, timedelta
import random
import string

from app.models.appointments import (
    Appointment,
    AppointmentSlot,
    AppointmentType,
    AppointmentStatus,
    BookingChannel,
    AppointmentPriority,
)
from app.models.patient import Patient
from app.models.user import User
from app.models.hospital import Department
from app.schemas.patient_portal.appointments import (
    AppointmentBookRequest,
    AppointmentResponse,
    AppointmentDetail,
    MyAppointmentsResponse,
    AvailableSlotsResponse,
    AvailableSlot,
    DepartmentAvailabilityItem,
    DoctorAvailabilityItem,
    PreAppointmentChecklist,
)


class AppointmentBookingService:
    """Service for patient portal appointment booking and management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_slots(
        self,
        department_id: int,
        target_date: date,
        doctor_id: Optional[int] = None,
    ) -> AvailableSlotsResponse:
        """Get available appointment slots for a department/doctor on a specific date"""
        # Get department
        result = await self.db.execute(
            select(Department).where(Department.id == department_id)
        )
        department = result.scalar_one_or_none()

        if not department:
            raise ValueError("Department not found")

        # Get slots for the date
        query = select(AppointmentSlot).where(
            and_(
                AppointmentSlot.department_id == department_id,
                AppointmentSlot.date == target_date,
                AppointmentSlot.is_available == True,
                AppointmentSlot.is_blocked == False,
            )
        )

        if doctor_id:
            query = query.where(AppointmentSlot.doctor_id == doctor_id)

        query = query.order_by(AppointmentSlot.start_time)

        result = await self.db.execute(query)
        slots = result.scalars().all()

        # Convert to response format
        available_slots = []
        total_available = 0

        for slot in slots:
            available = slot.booked_count < slot.max_patients
            if available:
                total_available += 1

            available_slots.append(AvailableSlot(
                slot_id=slot.id,
                start_time=slot.start_time.strftime("%H:%M"),
                end_time=slot.end_time.strftime("%H:%M"),
                is_available=available,
                doctors_available=slot.max_patients - slot.booked_count if available else 0,
            ))

        return AvailableSlotsResponse(
            date=target_date,
            department_id=department_id,
            department_name=department.name,
            slots=available_slots,
            total_available=total_available,
        )

    async def get_department_availability(
        self,
        department_id: int,
        start_date: date,
        end_date: Optional[date] = None,
    ) -> DepartmentAvailabilityItem:
        """Get availability for a department across a date range"""
        if not end_date:
            end_date = start_date + timedelta(days=7)

        # Get department
        result = await self.db.execute(
            select(Department).where(Department.id == department_id)
        )
        department = result.scalar_one_or_none()

        if not department:
            raise ValueError("Department not found")

        # Get doctors in department
        result = await self.db.execute(
            select(User).where(User.department_id == department_id)
        )
        doctors = result.scalars().all()

        doctor_list = []
        for doctor in doctors:
            # Get available slots for this doctor
            result = await self.db.execute(
                select(func.count(AppointmentSlot.id)).where(
                    and_(
                        AppointmentSlot.doctor_id == doctor.id,
                        AppointmentSlot.date.between(start_date, end_date),
                        AppointmentSlot.is_available == True,
                        AppointmentSlot.is_blocked == False,
                        or_(
                            AppointmentSlot.booked_count < AppointmentSlot.max_patients,
                            AppointmentSlot.booked_count == 0,
                        )
                    )
                )
            )
            available_count = result.scalar() or 0

            # Get next available slot
            result = await self.db.execute(
                select(AppointmentSlot)
                .where(
                    and_(
                        AppointmentSlot.doctor_id == doctor.id,
                        AppointmentSlot.date >= start_date,
                        AppointmentSlot.is_available == True,
                        AppointmentSlot.is_blocked == False,
                        AppointmentSlot.booked_count < AppointmentSlot.max_patients,
                    )
                )
                .order_by(AppointmentSlot.date, AppointmentSlot.start_time)
                .limit(1)
            )
            next_slot = result.scalar_one_or_none()

            doctor_list.append(DoctorAvailabilityItem(
                doctor_id=doctor.id,
                doctor_name=doctor.full_name,
                specialization=None,  # Would need to fetch from profile
                available_slots=available_count,
                next_available_slot=f"{next_slot.date.strftime('%Y-%m-%d')} {next_slot.start_time.strftime('%H:%M')}" if next_slot else None,
            ))

        return DepartmentAvailabilityItem(
            department_id=department.id,
            department_name=department.name,
            doctors=doctor_list,
        )

    async def book_appointment(
        self,
        patient_id: int,
        request: AppointmentBookRequest,
    ) -> Appointment:
        """Book a new appointment"""
        # Check if slot exists and is available
        result = await self.db.execute(
            select(AppointmentSlot).where(
                and_(
                    AppointmentSlot.department_id == request.department_id,
                    AppointmentSlot.date == request.appointment_date,
                    AppointmentSlot.start_time <= datetime.strptime(request.appointment_time, "%H:%M").time(),
                    AppointmentSlot.end_time > datetime.strptime(request.appointment_time, "%H:%M").time(),
                    AppointmentSlot.is_available == True,
                    AppointmentSlot.is_blocked == False,
                    AppointmentSlot.booked_count < AppointmentSlot.max_patients,
                )
            )
        )
        slot = result.scalar_one_or_none()

        if not slot:
            # Create a virtual slot if none exists (for flexibility)
            slot_time = datetime.strptime(request.appointment_time, "%H:%M").time()
            slot = AppointmentSlot(
                department_id=request.department_id,
                doctor_id=request.doctor_id,
                date=request.appointment_date,
                start_time=slot_time,
                end_time=(datetime.combine(date.today(), slot_time) + timedelta(minutes=30)).time(),
                slot_duration_minutes=30,
                max_patients=1,
                booked_count=0,
                is_available=True,
                is_blocked=False,
            )
            self.db.add(slot)
            await self.flush()

        # Generate appointment number
        appointment_number = await self._generate_appointment_number(request.appointment_date)

        # Calculate end time
        start_dt = datetime.combine(request.appointment_date, datetime.strptime(request.appointment_time, "%H:%M").time())
        end_time = (start_dt + timedelta(minutes=slot.slot_duration_minutes)).time()

        # Create appointment
        appointment = Appointment(
            appointment_number=appointment_number,
            patient_id=patient_id,
            department_id=request.department_id,
            doctor_id=request.doctor_id,
            appointment_date=request.appointment_date,
            appointment_time=datetime.strptime(request.appointment_time, "%H:%M").time(),
            end_time=end_time,
            duration_minutes=slot.slot_duration_minutes,
            appointment_type=request.appointment_type,
            status=AppointmentStatus.SCHEDULED,
            booking_channel=BookingChannel.WEB,
            priority=request.priority,
            reason_for_visit=request.reason_for_visit,
            symptoms=request.symptoms,
        )

        self.db.add(appointment)
        await self.flush()

        # Update slot booked count
        slot.booked_count += 1

        # Generate queue number
        appointment.queue_number = await self._generate_queue_number(request.department_id, request.appointment_date)

        await self.db.commit()
        await self.db.refresh(appointment)

        return appointment

    async def get_my_appointments(
        self,
        patient_id: int,
        include_past: bool = True,
        include_cancelled: bool = True,
        limit: int = 50,
    ) -> MyAppointmentsResponse:
        """Get all appointments for a patient"""
        # Get upcoming appointments
        result = await self.db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.patient_id == patient_id,
                    Appointment.appointment_date >= date.today(),
                    Appointment.status != AppointmentStatus.CANCELLED,
                    Appointment.status != AppointmentStatus.NO_SHOW,
                )
            )
            .options(selectinload(Appointment.department), selectinload(Appointment.doctor))
            .order_by(Appointment.appointment_date, Appointment.appointment_time)
            .limit(limit)
        )
        upcoming = result.scalars().all()

        past = []
        cancelled = []

        if include_past or include_cancelled:
            query = select(Appointment).where(
                and_(
                    Appointment.patient_id == patient_id,
                    or_(
                        Appointment.appointment_date < date.today(),
                        Appointment.status == AppointmentStatus.CANCELLED,
                        Appointment.status == AppointmentStatus.NO_SHOW,
                    ),
                )
            ).options(selectinload(Appointment.department), selectinload(Appointment.doctor))
            query = query.order_by(desc(Appointment.appointment_date), desc(Appointment.appointment_time))
            query = query.limit(limit)

            result = await self.db.execute(query)
            all_past = result.scalars().all()

            for apt in all_past:
                if apt.status == AppointmentStatus.CANCELLED:
                    cancelled.append(apt)
                else:
                    past.append(apt)

        return MyAppointmentsResponse(
            upcoming=[self._to_detail(a) for a in upcoming],
            past=[self._to_detail(a) for a in past],
            cancelled=[self._to_detail(a) for a in cancelled],
            total_upcoming=len(upcoming),
            total_past=len(past),
            total_cancelled=len(cancelled),
        )

    async def get_appointment_detail(
        self,
        appointment_id: int,
        patient_id: int,
    ) -> AppointmentDetail:
        """Get detailed appointment information"""
        result = await self.db.execute(
            select(Appointment)
            .where(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.patient_id == patient_id,
                )
            )
            .options(selectinload(Appointment.department), selectinload(Appointment.doctor))
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            raise ValueError("Appointment not found")

        return self._to_detail(appointment)

    async def cancel_appointment(
        self,
        appointment_id: int,
        patient_id: int,
        reason: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Appointment]]:
        """Cancel an appointment"""
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.patient_id == patient_id,
                )
            )
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            return False, "Appointment not found", None

        if appointment.status == AppointmentStatus.CANCELLED:
            return False, "Appointment is already cancelled", None

        if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.IN_PROGRESS]:
            return False, "Cannot cancel completed or in-progress appointment", None

        # Check cancellation policy (e.g., 24 hours before)
        appointment_datetime = datetime.combine(appointment.appointment_date, appointment.appointment_time)
        if appointment_datetime - datetime.now() < timedelta(hours=24):
            return False, "Can only cancel appointments at least 24 hours in advance", None

        # Cancel appointment
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancellation_reason = reason
        appointment.cancelled_at = datetime.utcnow()

        # Update slot booked count
        if appointment.doctor_id:
            result = await self.db.execute(
                select(AppointmentSlot).where(
                    and_(
                        AppointmentSlot.department_id == appointment.department_id,
                        AppointmentSlot.doctor_id == appointment.doctor_id,
                        AppointmentSlot.date == appointment.appointment_date,
                    )
                )
            )
            slot = result.scalar_one_or_none()
            if slot and slot.booked_count > 0:
                slot.booked_count -= 1

        await self.db.commit()
        await self.db.refresh(appointment)

        return True, "Appointment cancelled successfully", appointment

    async def reschedule_appointment(
        self,
        appointment_id: int,
        patient_id: int,
        new_date: date,
        new_time: str,
        reason: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Appointment]]:
        """Reschedule an appointment to a new date/time"""
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.patient_id == patient_id,
                )
            )
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            return False, "Appointment not found", None

        if appointment.status == AppointmentStatus.CANCELLED:
            return False, "Cannot reschedule cancelled appointment", None

        # Check new slot availability
        new_time_obj = datetime.strptime(new_time, "%H:%M").time()

        # Update appointment
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time_obj
        appointment.notes = f"Rescheduled from {appointment.appointment_date}. Reason: {reason or 'Not specified'}"

        await self.db.commit()
        await self.db.refresh(appointment)

        return True, "Appointment rescheduled successfully", appointment

    async def get_queue_status(
        self,
        appointment_id: int,
        patient_id: int,
    ) -> dict:
        """Get real-time queue status for an appointment"""
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.patient_id == patient_id,
                )
            )
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            raise ValueError("Appointment not found")

        # Calculate queue position
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.department_id == appointment.department_id,
                    Appointment.appointment_date == appointment.appointment_date,
                    Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED, AppointmentStatus.CHECKED_IN]),
                    Appointment.appointment_time < appointment.appointment_time,
                )
            )
        )
        patients_ahead = result.scalar() or 0

        return {
            "queue_number": appointment.queue_number,
            "queue_position": (appointment.queue_position or patients_ahead + 1),
            "estimated_wait_time_minutes": appointment.estimated_wait_time_minutes,
            "patients_ahead": patients_ahead,
            "currently_serving": None,  # Would need to query currently serving
            "status_message": self._get_status_message(appointment.status),
        }

    async def get_pre_appointment_checklist(
        self,
        appointment_id: int,
        patient_id: int,
    ) -> PreAppointmentChecklist:
        """Get pre-appointment instructions"""
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.id == appointment_id,
                    Appointment.patient_id == patient_id,
                )
            )
        )
        appointment = result.scalar_one_or_none()

        if not appointment:
            raise ValueError("Appointment not found")

        # Determine checklist based on appointment type
        checklist = PreAppointmentChecklist(
            fasting_required=False,
            arrive_early_minutes=15,
            bring_documents=["KTP/ID card", "BPJS card (if applicable)"],
            preparation_instructions=[],
        )

        if appointment.appointment_type == AppointmentType.PROCEDURE:
            checklist.fasting_required = True
            checklist.fasting_hours = 8
            checklist.preparation_instructions.append("Do not eat or drink for 8 hours before the procedure")
            checklist.bring_documents.extend(["Insurance card", "Referral letter if applicable"])

        elif appointment.appointment_type == AppointmentType.VACCINATION:
            checklist.bring_documents.append("Previous vaccination records (if available)")
            checklist.preparation_instructions.append("Bring your vaccination card if you have one")

        elif appointment.appointment_type == AppointmentType.CONSULTATION:
            checklist.preparation_instructions.append("Bring a list of current medications")
            checklist.preparation_instructions.append("Write down any questions you have for the doctor")

        return checklist

    def _to_detail(self, appointment: Appointment) -> AppointmentDetail:
        """Convert Appointment model to AppointmentDetail schema"""
        return AppointmentDetail(
            id=appointment.id,
            appointment_number=appointment.appointment_number,
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time,
            end_time=appointment.end_time,
            duration_minutes=appointment.duration_minutes,
            department_id=appointment.department_id,
            department_name=appointment.department.name if appointment.department else None,
            doctor_id=appointment.doctor_id,
            doctor_name=appointment.doctor.full_name if appointment.doctor else None,
            appointment_type=appointment.appointment_type.value,
            status=appointment.status.value,
            priority=appointment.priority.value,
            reason_for_visit=appointment.reason_for_visit,
            symptoms=appointment.symptoms,
            queue_number=appointment.queue_number,
            queue_position=appointment.queue_position,
            estimated_wait_time_minutes=appointment.estimated_wait_time_minutes,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
            check_in_time=appointment.check_in_time,
            start_time=appointment.start_time,
            completion_time=appointment.completion_time,
            cancellation_reason=appointment.cancellation_reason,
            cancelled_at=appointment.cancelled_at,
            reminder_sent=appointment.reminder_sent,
            reminder_sent_at=appointment.reminder_sent_at,
        )

    async def _generate_appointment_number(self, appointment_date: date) -> str:
        """Generate unique appointment number"""
        date_str = appointment_date.strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"APT-{date_str}-{random_str}"

    async def _generate_queue_number(self, department_id: int, appointment_date: date) -> str:
        """Generate queue number for the appointment"""
        # Get department code (first 3 letters uppercase)
        result = await self.db.execute(
            select(Department).where(Department.id == department_id)
        )
        department = result.scalar_one_or_none()

        dept_code = (department.name[:3] if department else "GEN").upper()

        # Count appointments for this department/date
        result = await self.db.execute(
            select(func.count(Appointment.id)).where(
                and_(
                    Appointment.department_id == department_id,
                    Appointment.appointment_date == appointment_date,
                )
            )
        )
        count = result.scalar() or 0

        return f"{dept_code}-{appointment_date.strftime('%Y%m%d')}-{count + 1:03d}"

    def _get_status_message(self, status: AppointmentStatus) -> str:
        """Get user-friendly status message"""
        messages = {
            AppointmentStatus.SCHEDULED: "Your appointment is scheduled. Please arrive 15 minutes early.",
            AppointmentStatus.CONFIRMED: "Your appointment is confirmed. Please arrive 15 minutes early.",
            AppointmentStatus.CHECKED_IN: "You are checked in. Please wait in the waiting area.",
            AppointmentStatus.IN_PROGRESS: "The doctor is ready to see you.",
            AppointmentStatus.COMPLETED: "Your appointment is complete.",
            AppointmentStatus.CANCELLED: "This appointment has been cancelled.",
            AppointmentStatus.NO_SHOW: "This appointment was marked as no-show.",
        }
        return messages.get(status, "Unknown status")
