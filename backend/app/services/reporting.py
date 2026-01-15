"""Reporting & Analytics Service for EPIC-013

This module provides services for:
- Report generation and execution
- Metric aggregation (operational, clinical, financial)
- Report scheduling and distribution
- Regulatory report generation

Python 3.5+ compatible
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, case, text
from sqlalchemy.orm import selectinload

from app.models.reporting import (
    Report, ReportSchedule, ReportExecution,
    OperationalMetric, ClinicalQualityMetric, FinancialMetric, RegulatoryReport,
    ReportType
)
from app.models.user import User
from app.models.encounter import Encounter
from app.models.patient import Patient


logger = logging.getLogger(__name__)


class ReportingService(object):
    """Service for reporting and analytics"""

    def __init__(self, db):
        self.db = db

    # ==========================================================================
    # Report Management
    # ==========================================================================

    async def create_report(
        self,
        name: str,
        code: str,
        report_type: str,
        description: Optional[str] = None,
        config: Optional[dict] = None,
        query_definition: Optional[str] = None,
        layout_definition: Optional[dict] = None,
        output_formats: Optional[List[str]] = None,
        default_output_format: str = "pdf",
        required_role: Optional[str] = None,
        created_by: Optional[int] = None,
        is_system: bool = False
    ) -> Dict[str, Any]:
        """Create a new report

        Args:
            name: Report name
            code: Unique report code
            report_type: Type of report
            description: Report description
            config: Report configuration
            query_definition: SQL query or data source
            layout_definition: Layout and visualization config
            output_formats: Supported output formats
            default_output_format: Default output format
            required_role: Required role to access
            created_by: User ID who created report
            is_system: Whether this is a system report

        Returns:
            Dict with report details
        """
        try:
            # Check if code already exists
            existing = await self.get_report_by_code(code)
            if existing:
                raise ValueError("Report code '{}' already exists".format(code))

            report = Report(
                name=name,
                code=code,
                description=description,
                report_type=report_type,
                config=config or {},
                query_definition=query_definition,
                layout_definition=layout_definition or {},
                output_formats=output_formats or ["pdf"],
                default_output_format=default_output_format,
                required_role=required_role,
                created_by=created_by,
                updated_by=created_by,
                is_system=is_system,
                is_active=True
            )

            self.db.add(report)
            await self.db.commit()

            logger.info("Created report: {}".format(name))

            return {
                "report_id": report.id,
                "name": report.name,
                "code": report.code,
                "report_type": report.report_type,
                "message": "Report created successfully"
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error creating report: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to create report: {}".format(str(e)))

    async def get_report(self, report_id: int) -> Dict[str, Any]:
        """Get report by ID

        Args:
            report_id: Report ID

        Returns:
            Dict with report details
        """
        try:
            query = select(Report).where(Report.id == report_id)
            result = await self.db.execute(query)
            report = result.scalar_one_or_none()

            if not report:
                raise ValueError("Report {} not found".format(report_id))

            return {
                "report_id": report.id,
                "name": report.name,
                "code": report.code,
                "description": report.description,
                "report_type": report.report_type,
                "category": report.category,
                "is_active": report.is_active,
                "is_system": report.is_system,
                "is_scheduled": report.is_scheduled,
                "config": report.config,
                "output_formats": report.output_formats,
                "default_output_format": report.default_output_format,
                "required_role": report.required_role,
                "created_at": report.created_at.isoformat() if report.created_at else None,
                "updated_at": report.updated_at.isoformat() if report.updated_at else None
            }

        except ValueError:
            raise
        except Exception as e:
            logger.error("Error getting report: {}".format(e))
            raise ValueError("Failed to get report: {}".format(str(e)))

    async def get_report_by_code(self, code: str) -> Optional[Report]:
        """Get report by code"""
        query = select(Report).where(Report.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_reports(
        self,
        report_type: Optional[str] = None,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List reports with filtering

        Args:
            report_type: Filter by report type
            category: Filter by category
            is_active: Filter by active status
            page: Page number
            per_page: Items per page

        Returns:
            Dict with reports list and pagination info
        """
        try:
            # Build filters
            filters = []

            if report_type:
                filters.append(Report.report_type == report_type)
            if category:
                filters.append(Report.category == category)
            if is_active is not None:
                filters.append(Report.is_active == is_active)

            # Get total count
            count_query = select(func.count(Report.id))
            if filters:
                count_query = count_query.where(and_(*filters))
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar() or 0

            # Get reports with pagination
            offset = (page - 1) * per_page
            query = select(Report)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(Report.name.asc()).limit(per_page).offset(offset)

            result = await self.db.execute(query)
            reports = result.scalars().all()

            # Build response
            report_list = [
                {
                    "report_id": r.id,
                    "name": r.name,
                    "code": r.code,
                    "description": r.description,
                    "report_type": r.report_type,
                    "category": r.category,
                    "is_active": r.is_active,
                    "is_scheduled": r.is_scheduled,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                }
                for r in reports
            ]

            return {
                "reports": report_list,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
            }

        except Exception as e:
            logger.error("Error listing reports: {}".format(e))
            raise ValueError("Failed to list reports: {}".format(str(e)))

    async def execute_report(
        self,
        report_id: int,
        parameters: Optional[dict] = None,
        output_format: str = "json",
        triggered_by: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a report and return results

        Args:
            report_id: Report ID
            parameters: Report parameters
            output_format: Output format (json, csv, pdf, xlsx)
            triggered_by: User ID who triggered execution

        Returns:
            Dict with execution results
        """
        try:
            # Get report
            query = select(Report).where(Report.id == report_id)
            result = await self.db.execute(query)
            report = result.scalar_one_or_none()

            if not report:
                raise ValueError("Report {} not found".format(report_id))

            # Create execution record
            execution = ReportExecution(
                report_id=report_id,
                status="running",
                started_at=datetime.utcnow(),
                parameters=parameters or {},
                output_format=output_format,
                triggered_by=triggered_by
            )
            self.db.add(execution)
            await self.db.flush()

            # Generate report data based on type
            data = None
            if report.code == "daily_census":
                data = await self._generate_daily_census(parameters)
            elif report.code == "department_utilization":
                data = await self._generate_department_utilization(parameters)
            elif report.code == "bed_occupancy":
                data = await self._generate_bed_occupancy(parameters)
            elif report.code == "patient_wait_times":
                data = await self._generate_patient_wait_times(parameters)
            elif report.code == "revenue_summary":
                data = await self._generate_revenue_summary(parameters)
            elif report.code == "bpjs_claim_analytics":
                data = await self._generate_bpjs_claim_analytics(parameters)
            elif report.code == "clinical_quality_summary":
                data = await self._generate_clinical_quality_summary(parameters)
            elif report.query_definition:
                # Execute custom query
                data = await self._execute_custom_query(report.query_definition, parameters)
            else:
                data = {"message": "Report type not implemented"}

            # Update execution record
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = int((execution.completed_at - execution.started_at).total_seconds())
            execution.row_count = len(data) if isinstance(data, list) else 1

            await self.db.commit()

            logger.info("Executed report: {} in {} seconds".format(
                report.name, execution.duration_seconds
            ))

            return {
                "execution_id": execution.id,
                "report_id": report_id,
                "report_name": report.name,
                "status": execution.status,
                "duration_seconds": execution.duration_seconds,
                "row_count": execution.row_count,
                "data": data,
                "executed_at": execution.started_at.isoformat()
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            logger.error("Error executing report: {}".format(e))
            # Update execution with error
            if execution:
                execution.status = "failed"
                execution.completed_at = datetime.utcnow()
                execution.error_message = str(e)
                await self.db.commit()
            await self.db.rollback()
            raise ValueError("Failed to execute report: {}".format(str(e)))

    # ==========================================================================
    # Operational Reports
    # ==========================================================================

    async def _generate_daily_census(self, parameters: dict) -> Dict[str, Any]:
        """Generate daily census report"""
        try:
            report_date = parameters.get("report_date", datetime.utcnow().date())

            # Count inpatients by department
            from app.models.encounter import Encounter
            from app.models.department import Department

            query = select(
                Department.name,
                func.count(Encounter.id).label("count")
            ).join(
                Encounter, Department.id == Encounter.department_id
            ).where(
                and_(
                    Encounter.encounter_type == "inpatient",
                    Encounter.status == "active",
                    func.date(Encounter.created_at) == report_date
                )
            ).group_by(Department.name)

            result = await self.db.execute(query)
            inpatient_by_dept = {row[0]: row[1] for row in result.all()}

            # Count outpatient visits
            outpatient_query = select(func.count(Encounter.id)).where(
                and_(
                    Encounter.encounter_type == "outpatient",
                    func.date(Encounter.created_at) == report_date
                )
            )
            outpatient_result = await self.db.execute(outpatient_query)
            outpatient_count = outpatient_result.scalar() or 0

            # Count emergency visits
            emergency_query = select(func.count(Encounter.id)).where(
                and_(
                    Encounter.encounter_type == "emergency",
                    func.date(Encounter.created_at) == report_date
                )
            )
            emergency_result = await self.db.execute(emergency_query)
            emergency_count = emergency_result.scalar() or 0

            return {
                "report_date": str(report_date),
                "inpatient_by_department": inpatient_by_dept,
                "total_inpatients": sum(inpatient_by_dept.values()),
                "outpatient_visits": outpatient_count,
                "emergency_visits": emergency_count,
                "total_patients": sum(inpatient_by_dept.values()) + outpatient_count + emergency_count
            }

        except Exception as e:
            logger.error("Error generating daily census: {}".format(e))
            raise

    async def _generate_department_utilization(self, parameters: dict) -> List[Dict[str, Any]]:
        """Generate department utilization report"""
        try:
            from app.models.encounter import Encounter
            from app.models.department import Department

            start_date = parameters.get("start_date")
            end_date = parameters.get("end_date")

            query = select(
                Department.id,
                Department.name,
                func.count(Encounter.id).label("encounter_count")
            ).outerjoin(
                Encounter, Department.id == Encounter.department_id
            )

            if start_date:
                query = query.where(func.date(Encounter.created_at) >= start_date)
            if end_date:
                query = query.where(func.date(Encounter.created_at) <= end_date)

            query = query.group_by(Department.id, Department.name)
            query = query.order_by(func.count(Encounter.id).desc())

            result = await self.db.execute(query)

            return [
                {
                    "department_id": row[0],
                    "department_name": row[1],
                    "encounter_count": row[2]
                }
                for row in result.all()
            ]

        except Exception as e:
            logger.error("Error generating department utilization: {}".format(e))
            raise

    async def _generate_bed_occupancy(self, parameters: dict) -> Dict[str, Any]:
        """Generate bed occupancy report"""
        try:
            from app.models.bed import Bed, BedStatus

            # Get all beds by status
            query = select(
                Bed.status,
                func.count(Bed.id).label("count")
            ).group_by(Bed.status)

            result = await self.db.execute(query)
            beds_by_status = {row[0]: row[1] for row in result.all()}

            total_beds = sum(beds_by_status.values())
            occupied_beds = beds_by_status.get(BedStatus.OCCUPIED, 0)
            occupancy_rate = (occupied_beds / total_beds * 100) if total_beds > 0 else 0

            return {
                "total_beds": total_beds,
                "occupied_beds": occupied_beds,
                "available_beds": beds_by_status.get(BedStatus.AVAILABLE, 0),
                "maintenance_beds": beds_by_status.get(BedStatus.MAINTENANCE, 0),
                "occupancy_rate": round(occupancy_rate, 2),
                "beds_by_status": beds_by_status
            }

        except Exception as e:
            logger.error("Error generating bed occupancy: {}".format(e))
            raise

    async def _generate_patient_wait_times(self, parameters: dict) -> Dict[str, Any]:
        """Generate patient wait time report"""
        try:
            from app.models.encounter import Encounter
            from app.models.queue import QueueEntry

            # Calculate average wait times by department
            query = select(
                func.coalesce(QueueEntry.department_id, 0).label("department_id"),
                func.avg(
                    func.extract("epoch", QueueEntry.called_at - QueueEntry.created_at)
                ).label("avg_wait_seconds")
            ).where(
                and_(
                    QueueEntry.called_at.isnot(None),
                    QueueEntry.created_at >= datetime.utcnow() - timedelta(days=30)
                )
            ).group_by(
                func.coalesce(QueueEntry.department_id, 0)
            )

            result = await self.db.execute(query)

            wait_times = [
                {
                    "department_id": row[0],
                    "avg_wait_seconds": round(row[1], 2) if row[1] else 0,
                    "avg_wait_minutes": round(row[1] / 60, 2) if row[1] else 0
                }
                for row in result.all()
            ]

            overall_avg = sum(w["avg_wait_seconds"] for w in wait_times) / len(wait_times) if wait_times else 0

            return {
                "wait_times_by_department": wait_times,
                "overall_avg_wait_seconds": round(overall_avg, 2),
                "overall_avg_wait_minutes": round(overall_avg / 60, 2)
            }

        except Exception as e:
            logger.error("Error generating patient wait times: {}".format(e))
            raise

    # ==========================================================================
    # Financial Reports
    # ==========================================================================

    async def _generate_revenue_summary(self, parameters: dict) -> Dict[str, Any]:
        """Generate revenue summary report"""
        try:
            from app.models.billing import Invoice, InvoiceStatus

            start_date = parameters.get("start_date")
            end_date = parameters.get("end_date")

            # Total revenue
            query = select(func.sum(Invoice.total_amount))
            if start_date:
                query = query.where(func.date(Invoice.created_at) >= start_date)
            if end_date:
                query = query.where(func.date(Invoice.created_at) <= end_date)
            query = query.where(Invoice.status != InvoiceStatus.CANCELLED)

            result = await self.db.execute(query)
            total_revenue = result.scalar() or 0

            # Revenue by payer type
            payer_query = select(
                Invoice.payer_type,
                func.sum(Invoice.total_amount).label("amount")
            ).where(Invoice.status != InvoiceStatus.CANCELLED)

            if start_date:
                payer_query = payer_query.where(func.date(Invoice.created_at) >= start_date)
            if end_date:
                payer_query = payer_query.where(func.date(Invoice.created_at) <= end_date)

            payer_query = payer_query.group_by(Invoice.payer_type)

            payer_result = await self.db.execute(payer_query)
            revenue_by_payer = {row[0]: float(row[1]) for row in payer_result.all()}

            # Invoice count
            count_query = select(func.count(Invoice.id)).where(
                Invoice.status != InvoiceStatus.CANCELLED
            )
            if start_date:
                count_query = count_query.where(func.date(Invoice.created_at) >= start_date)
            if end_date:
                count_query = count_query.where(func.date(Invoice.created_at) <= end_date)

            count_result = await self.db.execute(count_query)
            invoice_count = count_result.scalar() or 0

            return {
                "period": {
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None
                },
                "total_revenue": float(total_revenue),
                "invoice_count": invoice_count,
                "revenue_by_payer": revenue_by_payer,
                "average_invoice_amount": float(total_revenue / invoice_count) if invoice_count > 0 else 0
            }

        except Exception as e:
            logger.error("Error generating revenue summary: {}".format(e))
            raise

    async def _generate_bpjs_claim_analytics(self, parameters: dict) -> Dict[str, Any]:
        """Generate BPJS claim analytics report"""
        try:
            from app.models.bpjs import BPJSClaim, ClaimStatus

            start_date = parameters.get("start_date")
            end_date = parameters.get("end_date")

            # Total claims
            total_query = select(func.count(BPJSClaim.id))
            if start_date:
                total_query = total_query.where(func.date(BPJSClaim.submitted_at) >= start_date)
            if end_date:
                total_query = total_query.where(func.date(BPJSClaim.submitted_at) <= end_date)

            total_result = await self.db.execute(total_query)
            total_claims = total_result.scalar() or 0

            # Claims by status
            status_query = select(
                BPJSClaim.status,
                func.count(BPJSClaim.id).label("count")
            ).group_by(BPJSClaim.status)

            if start_date:
                status_query = status_query.where(func.date(BPJSClaim.submitted_at) >= start_date)
            if end_date:
                status_query = status_query.where(func.date(BPJSClaim.submitted_at) <= end_date)

            status_result = await self.db.execute(status_query)
            claims_by_status = {row[0]: row[1] for row in status_result.all()}

            # Total claim amount
            amount_query = select(func.sum(BPJSClaim.claim_amount))
            if start_date:
                amount_query = amount_query.where(func.date(BPJSClaim.submitted_at) >= start_date)
            if end_date:
                amount_query = amount_query.where(func.date(BPJSClaim.submitted_at) <= end_date)

            amount_result = await self.db.execute(amount_query)
            total_amount = amount_result.scalar() or 0

            # Approved amount
            approved_query = select(func.sum(BPJSClaim.approved_amount)).where(
                BPJSClaim.status == ClaimStatus.APPROVED
            )
            if start_date:
                approved_query = approved_query.where(func.date(BPJSClaim.submitted_at) >= start_date)
            if end_date:
                approved_query = approved_query.where(func.date(BPJSClaim.submitted_at) <= end_date)

            approved_result = await self.db.execute(approved_query)
            approved_amount = approved_result.scalar() or 0

            approval_rate = (claims_by_status.get(ClaimStatus.APPROVED, 0) / total_claims * 100) if total_claims > 0 else 0

            return {
                "period": {
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None
                },
                "total_claims": total_claims,
                "claims_by_status": claims_by_status,
                "total_claim_amount": float(total_amount),
                "approved_amount": float(approved_amount),
                "approval_rate": round(approval_rate, 2)
            }

        except Exception as e:
            logger.error("Error generating BPJS claim analytics: {}".format(e))
            raise

    # ==========================================================================
    # Clinical Quality Reports
    # ==========================================================================

    async def _generate_clinical_quality_summary(self, parameters: dict) -> Dict[str, Any]:
        """Generate clinical quality summary report"""
        try:
            from app.models.encounter import Encounter
            from app.models.clinical_note import ClinicalNote

            # Get metrics for the period
            start_date = parameters.get("start_date")
            end_date = parameters.get("end_date")

            # Total encounters with clinical notes
            notes_query = select(
                func.count(func.distinct(ClinicalNote.encounter_id))
            ).where(
                ClinicalNote.is_signed == True
            )

            if start_date:
                notes_query = notes_query.where(func.date(ClinicalNote.created_at) >= start_date)
            if end_date:
                notes_query = notes_query.where(func.date(ClinicalNote.created_at) <= end_date)

            notes_result = await self.db.execute(notes_query)
            documented_encounters = notes_result.scalar() or 0

            # Total encounters
            encounter_query = select(func.count(Encounter.id))
            if start_date:
                encounter_query = encounter_query.where(func.date(Encounter.created_at) >= start_date)
            if end_date:
                encounter_query = encounter_query.where(func.date(Encounter.created_at) <= end_date)

            encounter_result = await self.db.execute(encounter_query)
            total_encounters = encounter_result.scalar() or 0

            documentation_rate = (documented_encounters / total_encounters * 100) if total_encounters > 0 else 0

            return {
                "period": {
                    "start_date": str(start_date) if start_date else None,
                    "end_date": str(end_date) if end_date else None
                },
                "total_encounters": total_encounters,
                "documented_encounters": documented_encounters,
                "documentation_rate": round(documentation_rate, 2),
                "target_rate": 95.0,
                "meets_target": documentation_rate >= 95.0
            }

        except Exception as e:
            logger.error("Error generating clinical quality summary: {}".format(e))
            raise

    # ==========================================================================
    # Custom Query Execution
    # ==========================================================================

    async def _execute_custom_query(self, query_text: str, parameters: dict) -> List[Dict[str, Any]]:
        """Execute custom SQL query"""
        try:
            # Simple parameter substitution
            # WARNING: This is a basic implementation. For production, use proper parameterized queries
            for key, value in parameters.items():
                if isinstance(value, str):
                    query_text = query_text.replace("{{{}}}".format(key), "'{}'".format(value))
                elif value is None:
                    query_text = query_text.replace("{{{}}}".format(key), "NULL")
                else:
                    query_text = query_text.replace("{{{}}}".format(key), str(value))

            # Execute query
            result = await self.db.execute(text(query_text))
            rows = result.fetchall()
            columns = result.keys()

            return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error("Error executing custom query: {}".format(e))
            raise

    # ==========================================================================
    # Metric Aggregation
    # ==========================================================================

    async def aggregate_daily_metrics(self, metric_date: datetime) -> Dict[str, Any]:
        """Aggregate and store daily operational metrics

        Args:
            metric_date: Date to aggregate metrics for

        Returns:
            Dict with aggregation results
        """
        try:
            metrics_created = 0

            # Aggregate daily census
            census_data = await self._generate_daily_census({"report_date": metric_date.date()})

            # Store inpatient metrics by department
            for dept_name, count in census_data.get("inpatient_by_department", {}).items():
                metric = OperationalMetric(
                    metric_date=metric_date,
                    metric_type="daily_census_inpatient",
                    department_name=dept_name,
                    metric_count=count,
                    metadata={"report_date": str(metric_date.date())}
                )
                self.db.add(metric)
                metrics_created += 1

            # Store outpatient and emergency counts
            metric = OperationalMetric(
                metric_date=metric_date,
                metric_type="daily_census_outpatient",
                metric_count=census_data.get("outpatient_visits", 0),
                metadata={"report_date": str(metric_date.date())}
            )
            self.db.add(metric)
            metrics_created += 1

            metric = OperationalMetric(
                metric_date=metric_date,
                metric_type="daily_census_emergency",
                metric_count=census_data.get("emergency_visits", 0),
                metadata={"report_date": str(metric_date.date())}
            )
            self.db.add(metric)
            metrics_created += 1

            await self.db.commit()

            logger.info("Aggregated {} daily metrics for {}".format(metrics_created, metric_date))

            return {
                "metric_date": str(metric_date),
                "metrics_created": metrics_created,
                "message": "Daily metrics aggregated successfully"
            }

        except Exception as e:
            logger.error("Error aggregating daily metrics: {}".format(e))
            await self.db.rollback()
            raise ValueError("Failed to aggregate daily metrics: {}".format(str(e)))


def get_reporting_service(db):
    """Get or create reporting service instance

    Args:
        db: Database session

    Returns:
        ReportingService instance
    """
    return ReportingService(db)
