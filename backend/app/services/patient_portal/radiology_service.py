"""Radiology Results Service for Patient Portal

Service for patients to view their radiology/imaging results with reports.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, desc
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.models.radiology_orders import RadiologyOrder, RadiologyOrderStatus
from app.schemas.patient_portal.radiology_results import (
    RadiologyResultDetail,
    RadiologyResultListItem,
    RadiologyResultsListResponse,
    CriticalFindingAlert,
    RadiologyExamExplanation,
    ImagingStudyInfo,
)


class RadiologyResultsService:
    """Service for handling radiology results viewing for patients"""

    # Patient-friendly explanations for imaging modalities
    MODALITY_EXPLANATIONS = {
        "CT": {
            "description": "Computed Tomography - uses X-rays to create detailed cross-sectional images",
            "what_it_is": "A painless imaging test that uses X-rays and computer technology to create detailed images of bones, muscles, fat, and organs",
            "why_its_done": "To diagnose bone injuries, lung conditions, heart disease, cancers, internal bleeding, and infections",
            "how_to_prepare": "May need to fast for 4-6 hours if contrast will be used. Wear comfortable clothing without metal",
            "what_to_expect": "You'll lie on a table that slides into a donut-shaped scanner. The scanner makes noise as it rotates around you",
            "duration": "15-30 minutes",
            "risks": "Small amount of radiation exposure. Contrast may cause allergic reaction in some patients",
            "results_timing": "Results typically available within 24-48 hours. STAT exams within 1-2 hours",
        },
        "MRI": {
            "description": "Magnetic Resonance Imaging - uses magnetic fields and radio waves",
            "what_it_is": "A painless imaging test that uses powerful magnets and radio waves to create detailed images of organs and tissues",
            "why_its_done": "To diagnose brain/spine conditions, joint injuries, tumors, heart problems, and abdominal organ issues",
            "how_to_prepare": "Remove all metal objects. May need to fast. Tell staff about any implants or metal in your body",
            "what_to_expect": "You'll lie on a table that slides into a tube-shaped scanner. Loud tapping sounds occur during scanning",
            "duration": "30-60 minutes",
            "risks": "Very safe with no radiation. Not suitable for people with certain implants or metal in their body",
            "results_timing": "Results typically available within 24-48 hours. STAT exams within 2-4 hours",
        },
        "XRAY": {
            "description": "X-Ray Imaging - uses electromagnetic radiation",
            "what_it_is": "A quick imaging test that uses small amounts of radiation to create images of bones and certain tissues",
            "why_its_done": "To diagnose fractures, pneumonia, heart enlargement, digestive issues, and foreign objects",
            "how_to_prepare": "No special preparation needed. Remove jewelry and metal objects from the area being X-rayed",
            "what_to_expect": "You'll position the body part being imaged between the X-ray machine and a detector. May need multiple views",
            "duration": "10-15 minutes",
            "risks": "Very low radiation exposure. Generally safe for all ages",
            "results_timing": "Results typically available within 1-2 hours. STAT exams within 30 minutes",
        },
        "US": {
            "description": "Ultrasound Imaging - uses sound waves",
            "what_it_is": "A painless imaging test that uses sound waves to create images of internal organs and tissues",
            "why_its_done": "To examine abdomen, pelvis, pregnancy, heart (echocardiogram), and blood vessels (Doppler)",
            "how_to_prepare": "May need to fast or have full bladder depending on exam type. Wear loose clothing",
            "what_to_expect": "Gel is applied to skin and a handheld device (transducer) is moved over the area",
            "duration": "20-45 minutes",
            "risks": "No risks - uses sound waves, no radiation",
            "results_timing": "Results typically available within 24 hours. STAT exams within 1-2 hours",
        },
        "FLUOROSCOPY": {
            "description": "Fluoroscopy - real-time X-ray imaging",
            "what_it_is": "A continuous X-ray beam that creates moving images of internal organs in real-time",
            "why_its_done": "To examine digestive tract (barium swallow), blood vessels (angiography), and guide procedures",
            "how_to_prepare": "May need to fast. Contrast material may be given",
            "what_to_expect": "You'll lie on an X-ray table while a fluoroscope moves over you, creating live images",
            "duration": "30 minutes to 2 hours depending on procedure",
            "risks": "Higher radiation dose than standard X-ray. Contrast may cause allergic reaction",
            "results_timing": "Results typically available within 24-48 hours",
        },
        "MAMMOGRAPHY": {
            "description": "Mammography - breast imaging",
            "what_it_is": "A specialized X-ray imaging of the breast tissue to detect abnormalities",
            "why_its_done": "To screen for or diagnose breast cancer and other breast conditions",
            "how_to_prepare": "Avoid using deodorant, powder, or lotion on breasts/underarms. Schedule when breasts are not tender",
            "what_to_expect": "Breast is compressed between plates while X-ray images are taken. May be uncomfortable",
            "duration": "20-30 minutes",
            "risks": "Small amount of radiation. Temporary discomfort during compression",
            "results_timing": "Results typically available within 1-2 days. You'll receive a letter within 30 days",
        },
        "NUCLEAR_MEDICINE": {
            "description": "Nuclear Medicine - uses radioactive tracers",
            "what_it_is": "Imaging that uses small amounts of radioactive material to diagnose and treat diseases",
            "why_its_done": "To evaluate organ function, detect cancer, heart disease, bone fractures, and thyroid conditions",
            "how_to_prepare": "May need to fast. Certain medications may need to be stopped",
            "what_to_expect": "Radioactive tracer is given (injected, swallowed, or inhaled). Special camera images the tracer distribution",
            "duration": "1-4 hours depending on exam",
            "risks": "Small radiation dose. Allergic reaction to tracer is rare",
            "results_timing": "Results typically available within 1-3 days",
        },
        "PET": {
            "description": "PET Scan - Positron Emission Tomography",
            "what_it_is": "An imaging test that uses radioactive tracer to show metabolic activity in cells",
            "why_its_done": "To detect cancer, heart disease, brain disorders, and evaluate treatment response",
            "how_to_prepare": "Fast for 6 hours. No exercise for 24 hours before. Drink plenty of water",
            "what_to_expect": "Radioactive tracer is injected. Rest quietly for 60 minutes while tracer circulates, then scan for 30-45 minutes",
            "duration": "2-3 hours total",
            "risks": "Small radiation dose from tracer. Rare allergic reaction",
            "results_timing": "Results typically available within 2-3 days",
        },
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_radiology_results(
        self, patient_id: int, include_historical: bool = True
    ) -> RadiologyResultsListResponse:
        """Get patient's radiology results grouped by recent (90 days) and historical

        Args:
            patient_id: Patient ID
            include_historical: Whether to include historical results

        Returns:
            RadiologyResultsListResponse with recent and historical results
        """
        # Get all radiology orders for this patient
        query = (
            select(RadiologyOrder)
            .options(selectinload(RadiologyOrder.ordering_provider))
            .where(RadiologyOrder.patient_id == patient_id)
            .order_by(desc(RadiologyOrder.ordered_at))
        )

        result = await self.db.execute(query)
        radiology_orders = result.scalars().all()

        # Split into recent (90 days) and historical
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        recent_results = []
        historical_results = []
        pending_count = 0
        critical_alerts = 0

        for order in radiology_orders:
            is_recent = order.ordered_at >= ninety_days_ago if order.ordered_at else False
            is_pending = order.status in [
                RadiologyOrderStatus.ORDERED,
                RadiologyOrderStatus.SCHEDULED,
                RadiologyOrderStatus.IN_PROGRESS,
            ]

            if is_pending:
                pending_count += 1

            if order.critical_findings:
                critical_alerts += 1

            list_item = RadiologyResultListItem(
                id=order.id,
                order_number=order.order_number,
                procedure_name=order.procedure_name,
                modality=order.modality or "UNKNOWN",
                body_part=order.body_part,
                exam_date=order.ordered_at.date() if order.ordered_at else date.today(),
                status=order.status,
                has_critical_findings=order.critical_findings,
                has_report=bool(order.final_report or order.preliminary_report),
                ordered_by=order.ordering_provider.full_name if order.ordering_provider else "Unknown",
            )

            if is_recent:
                recent_results.append(list_item)
            elif include_historical:
                historical_results.append(list_item)

        return RadiologyResultsListResponse(
            recent_results=recent_results,
            historical_results=historical_results,
            total_recent=len(recent_results),
            total_historical=len(historical_results),
            pending_count=pending_count,
            critical_alerts=critical_alerts,
        )

    async def get_radiology_result_detail(
        self, patient_id: int, radiology_order_id: int
    ) -> Optional[RadiologyResultDetail]:
        """Get detailed radiology result with reports

        Args:
            patient_id: Patient ID
            radiology_order_id: Radiology order ID

        Returns:
            RadiologyResultDetail with exam details and reports
        """
        # Get radiology order with all relationships
        result = await self.db.execute(
            select(RadiologyOrder)
            .options(
                selectinload(RadiologyOrder.ordering_provider),
                selectinload(RadiologyOrder.radiologist),
            )
            .where(
                and_(
                    RadiologyOrder.id == radiology_order_id,
                    RadiologyOrder.patient_id == patient_id,
                )
            )
        )
        radiology_order = result.scalar_one_or_none()

        if not radiology_order:
            return None

        return RadiologyResultDetail(
            id=radiology_order.id,
            order_number=radiology_order.order_number,
            accession_number=radiology_order.accession_number,
            procedure_code=radiology_order.procedure_code,
            procedure_name=radiology_order.procedure_name,
            modality=radiology_order.modality or "UNKNOWN",
            body_part=radiology_order.body_part,
            view_position=radiology_order.view_position,
            status=radiology_order.status,
            priority=radiology_order.priority,
            clinical_indication=radiology_order.clinical_indication,
            clinical_history=radiology_order.clinical_history,
            contrast_required=radiology_order.contrast_required,
            contrast_type=radiology_order.contrast_type,
            radiation_dose_msv=radiology_order.radiation_dose_msv,
            preliminary_report=radiology_order.preliminary_report,
            preliminary_report_at=radiology_order.preliminary_report_at,
            final_report=radiology_order.final_report,
            final_report_at=radiology_order.final_report_at,
            findings=radiology_order.findings,
            impression=radiology_order.impression,
            critical_findings=radiology_order.critical_findings,
            critical_findings_notified=radiology_order.critical_findings_notified,
            image_count=radiology_order.image_count,
            series_count=radiology_order.series_count,
            ordered_at=radiology_order.ordered_at,
            scheduled_at=radiology_order.scheduled_at,
            procedure_completed_at=radiology_order.procedure_completed_at,
            ordered_by_name=radiology_order.ordering_provider.full_name if radiology_order.ordering_provider else "Unknown",
            radiologist_name=radiology_order.radiologist.full_name if radiology_order.radiologist else None,
        )

    async def get_critical_alerts(self, patient_id: int) -> List[CriticalFindingAlert]:
        """Get critical finding alerts for patient

        Args:
            patient_id: Patient ID

        Returns:
            List of critical finding alerts
        """
        result = await self.db.execute(
            select(RadiologyOrder)
            .where(
                and_(
                    RadiologyOrder.patient_id == patient_id,
                    RadiologyOrder.critical_findings == True,
                )
            )
            .order_by(desc(RadiologyOrder.procedure_completed_at))
        )
        radiology_orders = result.scalars().all()

        alerts = []
        for order in radiology_orders:
            alert_text = order.impression or "Critical finding detected - review full report"
            alerts.append(
                CriticalFindingAlert(
                    radiology_order_id=order.id,
                    procedure_name=order.procedure_name,
                    critical_finding=alert_text[:200],  # Truncate for alert
                    alert_time=order.final_report_at or datetime.utcnow(),
                    notified=order.critical_findings_notified,
                )
            )

        return alerts

    def get_modality_explanation(self, modality: str) -> Optional[RadiologyExamExplanation]:
        """Get patient-friendly explanation for an imaging modality

        Args:
            modality: Modality code (CT, MRI, XRAY, etc.)

        Returns:
            RadiologyExamExplanation with modality details
        """
        explanation = self.MODALITY_EXPLANATIONS.get(modality.upper())

        if not explanation:
            return None

        return RadiologyExamExplanation(
            modality=modality,
            description=explanation["description"],
            what_it_is=explanation["what_it_is"],
            why_its_done=explanation["why_its_done"],
            how_to_prepare=explanation.get("how_to_prepare"),
            what_to_expect=explanation["what_to_expect"],
            duration=explanation["duration"],
            risks=explanation["risks"],
            results_timing=explanation["results_timing"],
        )
