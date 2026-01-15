"""Lab Results Service for Patient Portal

Service for patients to view their laboratory results with explanations
and historical trending.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, desc, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import secrets

from app.models.lab_orders import LabOrder, LabOrderStatus
from app.models.patients import Patient
from app.schemas.patient_portal.lab_results import (
    LabResultDetail,
    LabResultListItem,
    LabResultsListResponse,
    TestHistoryPoint,
    TestHistoryResponse,
    LabResultDocument,
    CriticalValueAlert,
    LabTestExplanation,
    TestResultItem,
    AbnormalFlag,
)


class LabResultsService:
    """Service for handling lab results viewing for patients"""

    # Patient-friendly explanations for common lab tests
    TEST_EXPLANATIONS = {
        "CBC": {
            "description": "Complete Blood Count - measures different components of your blood",
            "what_it_measures": "Red blood cells, white blood cells, hemoglobin, hematocrit, and platelets",
            "why_its_done": "To evaluate overall health, diagnose conditions like anemia, infection, and inflammation",
            "how_to_prepare": "No special preparation needed",
            "what_results_mean": "Results show if your blood cell counts are within normal ranges",
            "normal_range": "Varies by component and demographic factors",
            "abnormal_values_mean": "May indicate anemia, infection, inflammation, or other blood disorders",
            "next_steps_if_abnormal": "Consult with your doctor for interpretation and follow-up testing if needed",
        },
        "HBA1C": {
            "description": "Hemoglobin A1c - measures average blood sugar over past 2-3 months",
            "what_it_measures": "Percentage of hemoglobin coated with sugar (glycated hemoglobin)",
            "why_its_done": "To diagnose and monitor diabetes and prediabetes",
            "how_to_prepare": "No special preparation needed",
            "what_results_mean": "Shows average blood sugar control over time",
            "normal_range": "Below 5.7% (normal), 5.7-6.4% (prediabetes), 6.5%+ (diabetes)",
            "abnormal_values_mean": "Higher values indicate poorer blood sugar control",
            "next_steps_if_abnormal": "Discuss with doctor for diabetes management plan",
        },
        "LIPID": {
            "description": "Lipid Panel - measures cholesterol and triglycerides",
            "what_it_measures": "Total cholesterol, LDL, HDL, and triglycerides",
            "why_its_done": "To assess cardiovascular risk and heart health",
            "how_to_prepare": "Fast for 9-12 hours before the test",
            "what_results_mean": "Shows levels of different types of cholesterol in blood",
            "normal_range": "Total: <200 mg/dL, LDL: <100 mg/dL, HDL: >40 mg/dL (men), >50 mg/dL (women)",
            "abnormal_values_mean": "High LDL or triglycerides increase heart disease risk",
            "next_steps_if_abnormal": "Lifestyle changes, medication, or further cardiac evaluation",
        },
        "BMP": {
            "description": "Basic Metabolic Panel - measures blood sugar, kidney function, and electrolytes",
            "what_it_measures": "Glucose, calcium, sodium, potassium, CO2, chloride, BUN, creatinine",
            "why_its_done": "To evaluate kidney function, blood sugar, and electrolyte balance",
            "how_to_prepare": "Fast for 8-10 hours before the test",
            "what_results_mean": "Shows how well kidneys are working and electrolyte balance",
            "normal_range": "Varies by component and lab",
            "abnormal_values_mean": "May indicate kidney problems, diabetes, or electrolyte imbalance",
            "next_steps_if_abnormal": "Follow up with doctor for diagnosis and treatment",
        },
        "TSH": {
            "description": "Thyroid Stimulating Hormone - measures thyroid function",
            "what_it_measures": "Level of TSH hormone produced by pituitary gland",
            "why_its_done": "To diagnose thyroid disorders (hypothyroidism or hyperthyroidism)",
            "how_to_prepare": "No special preparation needed (may need to stop certain medications)",
            "what_results_mean": "TSH levels indicate if thyroid is overactive or underactive",
            "normal_range": "0.4 - 4.0 mIU/L (varies by lab)",
            "abnormal_values_mean": "High TSH = underactive thyroid, Low TSH = overactive thyroid",
            "next_steps_if_abnormal": "Consult with doctor for thyroid function evaluation and treatment",
        },
        "UA": {
            "description": "Urinalysis - examines urine for various substances",
            "what_it_measures": "Appearance, concentration, content of urine",
            "why_its_done": "To screen for kidney disease, urinary tract infections, and other conditions",
            "how_to_prepare": "Clean catch midstream urine sample",
            "what_results_mean": "Shows presence of bacteria, blood, protein, glucose, etc.",
            "normal_range": "Clear, yellow; no bacteria, blood, protein, or glucose",
            "abnormal_values_mean": "May indicate infection, kidney disease, diabetes, or other conditions",
            "next_steps_if_abnormal": "Follow up with doctor for diagnosis and treatment",
        },
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_lab_results(
        self, patient_id: int, include_historical: bool = True
    ) -> LabResultsListResponse:
        """Get patient's lab results grouped by recent (90 days) and historical

        Args:
            patient_id: Patient ID
            include_historical: Whether to include historical results

        Returns:
            LabResultsListResponse with recent and historical results
        """
        # Get all lab orders for this patient
        query = (
            select(LabOrder)
            .options(selectinload(LabOrder.ordering_provider))
            .where(LabOrder.patient_id == patient_id)
            .order_by(desc(LabOrder.ordered_at))
        )

        result = await self.db.execute(query)
        lab_orders = result.scalars().all()

        # Split into recent (90 days) and historical
        ninety_days_ago = datetime.utcnow() - timedelta(days=90)
        recent_results = []
        historical_results = []
        pending_count = 0
        critical_alerts = 0

        for order in lab_orders:
            is_recent = order.ordered_at >= ninety_days_ago if order.ordered_at else False
            is_pending = order.status in [LabOrderStatus.ORDERED, LabOrderStatus.COLLECTED, LabOrderStatus.PROCESSING]
            has_critical = self._has_critical_values(order)

            if is_pending:
                pending_count += 1

            if has_critical:
                critical_alerts += 1

            list_item = LabResultListItem(
                id=order.id,
                order_number=order.order_number,
                test_name=order.test_name,
                test_date=order.ordered_at.date() if order.ordered_at else date.today(),
                status=order.status,
                has_abnormal_results=order.abnormal_flag or False,
                has_critical_results=has_critical,
                ordered_by=order.ordering_provider.full_name if order.ordering_provider else "Unknown",
            )

            if is_recent:
                recent_results.append(list_item)
            elif include_historical:
                historical_results.append(list_item)

        return LabResultsListResponse(
            recent_results=recent_results,
            historical_results=historical_results,
            total_recent=len(recent_results),
            total_historical=len(historical_results),
            pending_count=pending_count,
            critical_alerts=critical_alerts,
        )

    async def get_lab_result_detail(self, patient_id: int, lab_order_id: int) -> Optional[LabResultDetail]:
        """Get detailed lab result with explanations

        Args:
            patient_id: Patient ID
            lab_order_id: Lab order ID

        Returns:
            LabResultDetail with test results and explanations
        """
        # Get lab order with results
        result = await self.db.execute(
            select(LabOrder)
            .options(selectinload(LabOrder.ordering_provider))
            .where(
                and_(
                    LabOrder.id == lab_order_id,
                    LabOrder.patient_id == patient_id,
                )
            )
        )
        lab_order = result.scalar_one_or_none()

        if not lab_order:
            return None

        # Parse results from JSON
        result_items = self._parse_lab_results(lab_order.results)

        # Get patient-friendly explanation
        explanation = self._get_test_explanation(lab_order.test_code)

        return LabResultDetail(
            id=lab_order.id,
            order_number=lab_order.order_number,
            test_name=lab_order.test_name,
            test_code=lab_order.test_code,
            loinc_code=lab_order.loinc_code,
            status=lab_order.status,
            priority=lab_order.priority,
            clinical_indication=lab_order.clinical_indication,
            specimen_type=lab_order.specimen_type,
            results=result_items,
            results_interpretation=lab_order.results_interpretation,
            reference_range=lab_order.reference_range,
            abnormal_flag=lab_order.abnormal_flag,
            test_description=explanation.get("description") if explanation else None,
            what_it_measures=explanation.get("what_it_measures") if explanation else None,
            what_results_mean=explanation.get("what_results_mean") if explanation else None,
            ordered_at=lab_order.ordered_at,
            specimen_collected_at=lab_order.collected_at,
            completed_at=lab_order.completed_at,
            ordered_by_name=lab_order.ordering_provider.full_name if lab_order.ordering_provider else "Unknown",
        )

    async def get_test_history(
        self, patient_id: int, test_code: str, months: int = 12
    ) -> Optional[TestHistoryResponse]:
        """Get historical results for a specific test for trending

        Args:
            patient_id: Patient ID
            test_code: Test code to get history for
            months: Number of months of history to retrieve

        Returns:
            TestHistoryResponse with historical data points
        """
        # Get all completed lab orders for this test
        cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
        result = await self.db.execute(
            select(LabOrder)
            .where(
                and_(
                    LabOrder.patient_id == patient_id,
                    LabOrder.test_code == test_code,
                    LabOrder.status == LabOrderStatus.COMPLETED,
                    LabOrder.completed_at >= cutoff_date,
                )
            )
            .order_by(LabOrder.completed_at)
        )
        lab_orders = result.scalars().all()

        if not lab_orders:
            return None

        # Extract history points from results
        history = []
        for order in lab_orders:
            # Try to extract numeric value from results
            value = self._extract_numeric_value(order.results)
            if value is not None:
                history.append(
                    TestHistoryPoint(
                        date=order.completed_at.date() if order.completed_at else date.today(),
                        value=value,
                        is_abnormal=order.abnormal_flag or False,
                        reference_range=order.reference_range,
                    )
                )

        # Determine trend
        trend = self._calculate_trend(history)

        return TestHistoryResponse(
            test_code=test_code,
            test_name=lab_orders[0].test_name if lab_orders else test_code,
            unit=self._extract_unit(lab_orders[0].results) if lab_orders else "",
            history=history,
            trend=trend,
            normal_range=lab_orders[0].reference_range if lab_orders else None,
        )

    async def get_critical_alerts(self, patient_id: int) -> List[CriticalValueAlert]:
        """Get critical value alerts for patient

        Args:
            patient_id: Patient ID

        Returns:
            List of critical value alerts
        """
        result = await self.db.execute(
            select(LabOrder)
            .where(
                and_(
                    LabOrder.patient_id == patient_id,
                    LabOrder.status == LabOrderStatus.COMPLETED,
                    LabOrder.abnormal_flag == True,
                )
            )
            .order_by(desc(LabOrder.completed_at))
        )
        lab_orders = result.scalars().all()

        alerts = []
        for order in lab_orders:
            if self._has_critical_values(order):
                alerts.append(
                    CriticalValueAlert(
                        lab_order_id=order.id,
                        test_name=order.test_name,
                        critical_value=self._get_critical_value(order.results),
                        normal_range=order.reference_range or "N/A",
                        alert_time=order.completed_at or datetime.utcnow(),
                        notified=False,  # Would check notification table
                    )
                )

        return alerts

    def _parse_lab_results(self, results: Optional[Dict[str, Any]]) -> List[TestResultItem]:
        """Parse lab results JSON into structured format"""
        if not results:
            return []

        items = []
        if isinstance(results, dict):
            for test_name, test_data in results.items():
                if isinstance(test_data, dict):
                    items.append(
                        TestResultItem(
                            test_name=test_name,
                            result_value=str(test_data.get("value", "N/A")),
                            unit=test_data.get("unit"),
                            reference_range=test_data.get("reference_range"),
                            abnormal_flag=test_data.get("abnormal_flag"),
                            is_abnormal=test_data.get("is_abnormal", False),
                            is_critical=test_data.get("is_critical", False),
                        )
                    )
                else:
                    items.append(
                        TestResultItem(
                            test_name=test_name,
                            result_value=str(test_data),
                            is_abnormal=False,
                            is_critical=False,
                        )
                    )
        elif isinstance(results, list):
            for item in results:
                if isinstance(item, dict):
                    items.append(
                        TestResultItem(
                            test_name=item.get("name", "Unknown"),
                            result_value=str(item.get("value", "N/A")),
                            unit=item.get("unit"),
                            reference_range=item.get("reference_range"),
                            abnormal_flag=item.get("abnormal_flag"),
                            is_abnormal=item.get("is_abnormal", False),
                            is_critical=item.get("is_critical", False),
                        )
                    )

        return items

    def _get_test_explanation(self, test_code: str) -> Optional[Dict[str, str]]:
        """Get patient-friendly explanation for a test"""
        # Try exact match first
        if test_code in self.TEST_EXPLANATIONS:
            return self.TEST_EXPLANATIONS[test_code]

        # Try partial match
        for code, explanation in self.TEST_EXPLANATIONS.items():
            if code in test_code.upper() or test_code.upper() in code:
                return explanation

        return None

    def _has_critical_values(self, lab_order: LabOrder) -> bool:
        """Check if lab order has critical values"""
        if not lab_order.results:
            return False

        results = lab_order.results
        if isinstance(results, dict):
            for test_data in results.values():
                if isinstance(test_data, dict) and test_data.get("is_critical"):
                    return True
        elif isinstance(results, list):
            for item in results:
                if isinstance(item, dict) and item.get("is_critical"):
                    return True

        return False

    def _get_critical_value(self, results: Optional[Dict[str, Any]]) -> str:
        """Extract critical value from results"""
        if not results:
            return "N/A"

        if isinstance(results, dict):
            for test_name, test_data in results.items():
                if isinstance(test_data, dict) and test_data.get("is_critical"):
                    return f"{test_name}: {test_data.get('value', 'N/A')}"

        return "Critical value present"

    def _extract_numeric_value(self, results: Optional[Dict[str, Any]]) -> Optional[float]:
        """Extract numeric value from results for trending"""
        if not results:
            return None

        if isinstance(results, dict):
            # Look for a "value" key
            if "value" in results:
                try:
                    return float(results["value"])
                except (ValueError, TypeError):
                    pass

            # Try first numeric value
            for v in results.values():
                try:
                    return float(v)
                except (ValueError, TypeError):
                    continue

        return None

    def _extract_unit(self, results: Optional[Dict[str, Any]]) -> str:
        """Extract unit from results"""
        if not results:
            return ""

        if isinstance(results, dict):
            return results.get("unit", "")

        return ""

    def _calculate_trend(self, history: List[TestHistoryPoint]) -> Optional[str]:
        """Calculate trend direction from history points"""
        if len(history) < 2:
            return None

        # Simple linear regression for trend
        values = [point.value for point in history]
        n = len(values)

        sum_x = sum(range(n))
        sum_y = sum(values)
        sum_xy = sum(i * v for i, v in enumerate(values))
        sum_x2 = sum(i ** 2 for i in range(n))

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)

        if slope > 0.1:
            return "worsening"  # Assuming higher is worse (context-dependent)
        elif slope < -0.1:
            return "improving"
        else:
            return "stable"
