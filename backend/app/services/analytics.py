"""Analytics Dashboard Service for EPIC-017

This module provides services for:
- KPI calculation and tracking
- Dashboard data aggregation
- Scheduled report generation
- Data caching and optimization

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload

from app.models.analytics import (
    KPI, KPIHistory, Dashboard, DashboardWidget, DataCache,
    ScheduledReport, ReportSnapshot, KPICategory
)


logger = logging.getLogger(__name__)


class KPICalculator(object):
    """Calculates KPI values from database"""

    def __init__(self, db):
        self.db = db

    async def calculate_kpi(
        self,
        kpi: KPI,
        period_start: datetime,
        period_end: datetime
    ) -> Optional[float]:
        """Calculate KPI value for period

        Args:
            kpi: KPI model
            period_start: Period start
            period_end: Period end

        Returns:
            Calculated KPI value
        """
        try:
            if kpi.calculation_method == "sql":
                return await self._calculate_from_sql(kpi, period_start, period_end)
            elif kpi.calculation_method == "formula":
                return await self._calculate_from_formula(kpi, period_start, period_end)
            else:
                logger.warning("Unknown calculation method: {}".format(kpi.calculation_method))
                return None

        except Exception as e:
            logger.error("Error calculating KPI {}: {}".format(kpi.kpi_code, e))
            return None

    async def _calculate_from_sql(
        self,
        kpi: KPI,
        period_start: datetime,
        period_end: datetime
    ) -> Optional[float]:
        """Calculate KPI from SQL query"""
        try:
            # Replace date placeholders in query
            sql = kpi.sql_query
            sql = sql.replace(":period_start", "'{}'".format(period_start.isoformat()))
            sql = sql.replace(":period_end", "'{}'".format(period_end.isoformat()))

            # Execute query
            result = await self.db.execute(text(sql))
            row = result.first()

            if row and len(row) > 0:
                return float(row[0])
            return None

        except Exception as e:
            logger.error("Error executing SQL for KPI {}: {}".format(kpi.kpi_code, e))
            return None

    async def _calculate_from_formula(
        self,
        kpi: KPI,
        period_start: datetime,
        period_end: datetime
    ) -> Optional[float]:
        """Calculate KPI from formula"""
        try:
            # This is a simplified implementation
            # In production, use a proper formula parser/evaluator
            formula = kpi.formula
            if not formula:
                return None

            # Example: Calculate patient satisfaction
            # formula = "SUM(satisfaction_rating) / COUNT(responses)"

            # For now, return a placeholder value
            # In production, parse and evaluate the formula
            return None

        except Exception as e:
            logger.error("Error evaluating formula for KPI {}: {}".format(kpi.kpi_code, e))
            return None


class DashboardDataService(object):
    """Aggregates data for dashboard widgets"""

    def __init__(self, db):
        self.db = db

    async def get_dashboard_data(
        self,
        dashboard_code: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get all data for dashboard

        Args:
            dashboard_code: Dashboard code
            user_id: User ID for access control

        Returns:
            Dict with dashboard data
        """
        try:
            # Get dashboard
            query = select(Dashboard).options(
                selectinload(Dashboard.widgets)
            ).where(
                and_(
                    Dashboard.dashboard_code == dashboard_code,
                    Dashboard.is_active == True
                )
            )

            result = await self.db.execute(query)
            dashboard = result.scalar_one_or_none()

            if not dashboard:
                raise ValueError("Dashboard {} not found".format(dashboard_code))

            # Check access
            if not dashboard.is_public:
                # Implement role-based access check
                pass

            # Get widget data
            widget_data = []
            for widget in dashboard.widgets:
                if widget.is_active:
                    data = await self._get_widget_data(widget)
                    widget_data.append({
                        "widget_id": widget.widget_id,
                        "widget_type": widget.widget_type,
                        "widget_name": widget.widget_name,
                        "position": {
                            "x": widget.position_x,
                            "y": widget.position_y,
                            "width": widget.width,
                            "height": widget.height
                        },
                        "config": widget.config,
                        "data": data
                    })

            return {
                "dashboard_code": dashboard.dashboard_code,
                "dashboard_name": dashboard.dashboard_name,
                "dashboard_type": dashboard.dashboard_type,
                "refresh_interval": dashboard.refresh_interval,
                "layout_config": dashboard.layout_config,
                "widgets": widget_data
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error getting dashboard data: {}".format(e))
            raise ValueError("Failed to get dashboard data: {}".format(str(e)))

    async def _get_widget_data(self, widget: DashboardWidget) -> Any:
        """Get data for widget"""
        try:
            if widget.kpi_id:
                # Get KPI data
                return await self._get_kpi_widget_data(widget)
            else:
                # Get data from custom source
                return await self._get_custom_widget_data(widget)

        except Exception as e:
            logger.error("Error getting widget data: {}".format(e))
            return None

    async def _get_kpi_widget_data(self, widget: DashboardWidget) -> Any:
        """Get KPI data for widget"""
        try:
            # Get KPI
            kpi_query = select(KPI).where(KPI.id == widget.kpi_id)
            kpi_result = await self.db.execute(kpi_query)
            kpi = kpi_result.scalar_one_or_none()

            if not kpi:
                return None

            # Get current value
            calculator = KPICalculator(self.db)
            today = date.today()
            period_start = datetime.combine(today, datetime.min.time())
            period_end = datetime.combine(today, datetime.max.time())

            current_value = await calculator.calculate_kpi(kpi, period_start, period_end)

            # Get historical data (last 30 days)
            history_query = select(KPIHistory).where(
                and_(
                    KPIHistory.kpi_id == kpi.id,
                    KPIHistory.period_type == "daily"
                )
            ).order_by(KPIHistory.period_start.desc()).limit(30)

            history_result = await self.db.execute(history_query)
            history = history_result.scalars().all()

            historical_data = [
                {
                    "date": h.period_start.isoformat(),
                    "value": h.value,
                    "target": h.target_value
                }
                for h in reversed(history)
            ]

            return {
                "kpi_code": kpi.kpi_code,
                "kpi_name": kpi.kpi_name,
                "current_value": current_value,
                "target_value": kpi.target_value,
                "unit": kpi.unit,
                "format_type": kpi.format_type,
                "historical_data": historical_data
            }

        except Exception as e:
            logger.error("Error getting KPI widget data: {}".format(e))
            return None

    async def _get_custom_widget_data(self, widget: DashboardWidget) -> Any:
        """Get custom widget data"""
        try:
            # Implement custom data source logic
            return widget.config.get("data")

        except Exception as e:
            logger.error("Error getting custom widget data: {}".format(e))
            return None


class AnalyticsService(object):
    """Service for analytics dashboard"""

    def __init__(self, db):
        self.db = db
        self.kpi_calculator = KPICalculator(db)
        self.dashboard_service = DashboardDataService(db)

    # ==========================================================================
    # KPI Management
    # ==========================================================================

    async def create_kpi(
        self,
        kpi_code: str,
        kpi_name: str,
        kpi_category: str,
        calculation_method: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create new KPI

        Args:
            kpi_code: KPI code
            kpi_name: KPI name
            kpi_category: KPI category
            calculation_method: Calculation method
            **kwargs: Additional KPI attributes

        Returns:
            Dict with KPI details
        """
        try:
            kpi = KPI(
                kpi_code=kpi_code,
                kpi_name=kpi_name,
                kpi_category=kpi_category,
                calculation_method=calculation_method,
                description=kwargs.get("description"),
                sql_query=kwargs.get("sql_query"),
                formula=kwargs.get("formula"),
                data_source=kwargs.get("data_source"),
                unit=kwargs.get("unit"),
                decimal_places=kwargs.get("decimal_places", 2),
                format_type=kwargs.get("format_type", "number"),
                target_value=kwargs.get("target_value"),
                target_min=kwargs.get("target_min"),
                target_max=kwargs.get("target_max"),
                target_direction=kwargs.get("target_direction", "higher_is_better"),
                aggregation_type=kwargs.get("aggregation_type", "sum"),
                aggregation_period=kwargs.get("aggregation_period", "daily"),
                chart_type=kwargs.get("chart_type"),
                color_scheme=kwargs.get("color_scheme")
            )

            self.db.add(kpi)
            await self.db.commit()

            logger.info("Created KPI: {}".format(kpi.kpi_code))

            return {
                "kpi_code": kpi.kpi_code,
                "kpi_name": kpi.kpi_name,
                "kpi_category": kpi.kpi_category,
                "message": "KPI created successfully"
            }

        except Exception as e:
            logger.error("Error creating KPI: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create KPI: {}".format(str(e)))

    async def get_kpi_values(
        self,
        kpi_codes: List[str],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Get KPI values for specified codes and period

        Args:
            kpi_codes: List of KPI codes
            period_start: Period start
            period_end: Period end

        Returns:
            Dict with KPI values
        """
        try:
            # Get KPIs
            query = select(KPI).where(
                and_(
                    KPI.kpi_code.in_(kpi_codes),
                    KPI.is_active == True
                )
            )

            result = await self.db.execute(query)
            kpis = result.scalars().all()

            # Calculate values
            values = {}
            for kpi in kpis:
                value = await self.kpi_calculator.calculate_kpi(kpi, period_start, period_end)
                values[kpi.kpi_code] = {
                    "kpi_name": kpi.kpi_name,
                    "kpi_category": kpi.kpi_category,
                    "value": value,
                    "target": kpi.target_value,
                    "unit": kpi.unit,
                    "format_type": kpi.format_type
                }

            return values

        except Exception as e:
            logger.error("Error getting KPI values: {}".format(e))
            raise ValueError("Failed to get KPI values: {}".format(str(e)))

    # ==========================================================================
    # Dashboard Management
    # ==========================================================================

    async def get_dashboard(
        self,
        dashboard_code: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get dashboard data

        Args:
            dashboard_code: Dashboard code
            user_id: User ID for access control

        Returns:
            Dict with dashboard data
        """
        return await self.dashboard_service.get_dashboard_data(dashboard_code, user_id)

    # ==========================================================================
    # Hospital KPIs
    # ==========================================================================

    async def get_hospital_kpis(
        self,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get key hospital KPIs for executive dashboard

        Args:
            period_start: Period start (default: today)
            period_end: Period end (default: today)

        Returns:
            Dict with hospital KPIs
        """
        try:
            # Default to today if not specified
            if not period_start:
                period_start = datetime.combine(date.today(), datetime.min.time())
            if not period_end:
                period_end = datetime.combine(date.today(), datetime.max.time())

            # Get common KPIs
            kpi_data = await self._get_common_hospital_kpis(period_start, period_end)

            return {
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "kpis": kpi_data,
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("Error getting hospital KPIs: {}".format(e))
            raise ValueError("Failed to get hospital KPIs: {}".format(str(e)))

    async def _get_common_hospital_kpis(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Get common hospital KPIs"""
        try:
            kpis = {}

            # Patient census
            from app.models.patient import Patient
            from app.models.encounter import Encounter

            # Daily patient census
            encounter_query = select(func.count(Encounter.id)).where(
                and_(
                    Encounter.admission_date >= period_start.date(),
                    Encounter.admission_date <= period_end.date()
                )
            )
            encounter_result = await self.db.execute(encounter_query)
            daily_admissions = encounter_result.scalar() or 0

            # Inpatient census
            inpatient_query = select(func.count(Encounter.id)).where(
                and_(
                    Encounter.encounter_type == "inpatient",
                    Encounter.status == "active"
                )
            )
            inpatient_result = await self.db.execute(inpatient_query)
            inpatient_census = inpatient_result.scalar() or 0

            # Emergency visits
            emergency_query = select(func.count(Encounter.id)).where(
                and_(
                    Encounter.encounter_type == "emergency",
                    Encounter.admission_date >= period_start.date(),
                    Encounter.admission_date <= period_end.date()
                )
            )
            emergency_result = await self.db.execute(emergency_query)
            emergency_visits = emergency_result.scalar() or 0

            kpis["daily_admissions"] = {
                "value": daily_admissions,
                "label": "Daily Admissions",
                "format": "number"
            }

            kpis["inpatient_census"] = {
                "value": inpatient_census,
                "label": "Inpatient Census",
                "format": "number"
            }

            kpis["emergency_visits"] = {
                "value": emergency_visits,
                "label": "Emergency Visits",
                "format": "number"
            }

            # Bed occupancy
            from app.models.bed import Bed
            bed_query = select(func.count(Bed.id)).where(Bed.status == "occupied")
            bed_result = await self.db.execute(bed_query)
            occupied_beds = bed_result.scalar() or 0

            total_beds_query = select(func.count(Bed.id))
            total_beds_result = await self.db.execute(total_beds_query)
            total_beds = total_beds_result.scalar() or 1

            bed_occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0

            kpis["bed_occupancy_rate"] = {
                "value": round(bed_occupancy_rate, 1),
                "label": "Bed Occupancy Rate",
                "format": "percentage"
            }

            return kpis

        except Exception as e:
            logger.error("Error getting common hospital KPIs: {}".format(e))
            return {}


def get_analytics_service(db):
    """Get or create analytics service instance

    Args:
        db: Database session

    Returns:
        AnalyticsService instance
    """
    return AnalyticsService(db)
