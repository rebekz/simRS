"""Reporting & Analytics Models for EPIC-013

This module provides database models for:
- Report definitions and templates
- Report scheduling and execution
- Operational metrics
- Clinical quality metrics
- Financial metrics

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Enum as SQLEnum, JSON, Numeric, Float, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class ReportType:
    """Report type constants"""
    OPERATIONAL = "operational"
    CLINICAL_QUALITY = "clinical_quality"
    FINANCIAL = "financial"
    EXECUTIVE = "executive"
    REGULATORY = "regulatory"


class Report(Base):
    """Report model for defining and storing report configurations"""
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, comment="Report name")
    code = Column(String(100), unique=True, nullable=False, index=True, comment="Report code for reference")
    description = Column(Text, nullable=True, comment="Report description")
    report_type = Column(String(50), nullable=False, index=True, comment="Type of report")
    category = Column(String(100), nullable=True, index=True, comment="Report category")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether report is active")
    is_system = Column(Boolean, default=False, nullable=False, comment="System report (cannot be deleted)")

    # Report configuration
    config = Column(JSON, nullable=True, comment="Report configuration (parameters, filters, columns)")
    query_definition = Column(Text, nullable=True, comment="SQL query or data source definition")
    layout_definition = Column(JSON, nullable=True, comment="Report layout and visualization")

    # Scheduling
    is_scheduled = Column(Boolean, default=False, nullable=False, comment="Whether report is scheduled")
    schedule_cron = Column(String(100), nullable=True, comment="Cron expression for schedule")
    schedule_timezone = Column(String(50), default="Asia/Jakarta", comment="Timezone for schedule")

    # Output settings
    output_formats = Column(JSON, nullable=True, comment="Supported output formats (pdf, xlsx, csv, html)")
    default_output_format = Column(String(20), default="pdf", comment="Default output format")

    # Access control
    required_role = Column(String(50), nullable=True, comment="Minimum role required to run report")
    department_restricted = Column(Boolean, default=False, comment="Restrict to user's department")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    executions = relationship("ReportExecution", back_populates="report", cascade="all, delete-orphan")
    schedules = relationship("ReportSchedule", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        {"extend_existing": True, "comment": "Report definitions and configurations"},
    )


class ReportSchedule(Base):
    """Report schedule model for automated report generation"""
    __tablename__ = "report_schedule"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False, comment="Schedule name")
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether schedule is active")

    # Schedule configuration
    cron_expression = Column(String(100), nullable=False, comment="Cron expression")
    timezone = Column(String(50), default="Asia/Jakarta", comment="Timezone for schedule")

    # Parameters
    parameters = Column(JSON, nullable=True, comment="Report parameters for scheduled run")

    # Distribution
    distribution_method = Column(String(50), nullable=True, comment="Distribution method (email, save, webhook)")
    distribution_config = Column(JSON, nullable=True, comment="Distribution configuration")
    recipients = Column(JSON, nullable=True, comment="List of recipients")

    # Timing
    next_run_at = Column(DateTime(timezone=True), nullable=True, comment="Next scheduled run time")
    last_run_at = Column(DateTime(timezone=True), nullable=True, comment="Last run time")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    report = relationship("Report", back_populates="schedules")

    __table_args__ = (
        {"extend_existing": True, "comment": "Report schedules for automated generation"},
    )


class ReportExecution(Base):
    """Report execution model for tracking report runs"""
    __tablename__ = "report_execution"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    schedule_id = Column(Integer, ForeignKey("report_schedules.id", ondelete="SET NULL"), nullable=True)

    # Execution details
    status = Column(String(50), nullable=False, index=True, comment="Execution status (pending, running, completed, failed)")
    started_at = Column(DateTime(timezone=True), nullable=True, comment="Execution start time")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Execution completion time")
    duration_seconds = Column(Integer, nullable=True, comment="Execution duration in seconds")

    # Parameters
    parameters = Column(JSON, nullable=True, comment="Parameters used for this execution")

    # Results
    row_count = Column(Integer, nullable=True, comment="Number of rows generated")
    file_path = Column(String(500), nullable=True, comment="Path to generated report file")
    file_size_bytes = Column(Integer, nullable=True, comment="Size of generated file")
    output_format = Column(String(20), nullable=True, comment="Output format used")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    stack_trace = Column(Text, nullable=True, comment="Stack trace for debugging")

    # Metadata
    triggered_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who triggered execution")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    report = relationship("Report", back_populates="executions")

    __table_args__ = (
        {"extend_existing": True, "comment": "Report execution history"},
    )


class OperationalMetric(Base):
    """Operational metrics model for daily operational statistics"""
    __tablename__ = "operational_metric"

    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Date of metric")
    metric_type = Column(String(100), nullable=False, index=True, comment="Type of metric")

    # Department breakdown
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True, index=True)
    department_name = Column(String(100), nullable=True, comment="Department name for snapshot")

    # Metrics
    metric_value = Column(Float, nullable=True, comment="Metric value")
    metric_count = Column(Integer, nullable=True, comment="Metric count")
    report_metadata = Column(JSON, nullable=True, comment="Additional metric metadata")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Daily operational metrics"},
    )


class ClinicalQualityMetric(Base):
    """Clinical quality metrics model for quality reporting"""
    __tablename__ = "clinical_quality_metric"

    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Date of metric")
    metric_name = Column(String(100), nullable=False, index=True, comment="Quality metric name")

    # Thresholds
    target_value = Column(Float, nullable=True, comment="Target/threshold value")
    actual_value = Column(Float, nullable=True, comment="Actual measured value")
    percentage = Column(Float, nullable=True, comment="Percentage achievement")

    # Status
    status = Column(String(50), nullable=True, comment="Status (met, not_met, exceeded)")

    # Breakdown
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    report_metadata = Column(JSON, nullable=True, comment="Additional metadata")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Clinical quality metrics"},
    )


class FinancialMetric(Base):
    """Financial metrics model for financial reporting"""
    __tablename__ = "financial_metric"

    id = Column(Integer, primary_key=True, index=True)
    metric_date = Column(DateTime(timezone=True), nullable=False, index=True, comment="Date of metric")
    metric_type = Column(String(100), nullable=False, index=True, comment="Type of financial metric")

    # Amounts
    amount = Column(Numeric(15, 2), nullable=True, comment="Financial amount")
    count = Column(Integer, nullable=True, comment="Transaction count")
    average_amount = Column(Numeric(15, 2), nullable=True, comment="Average amount")

    # Breakdown
    payer_type = Column(String(50), nullable=True, index=True, comment="Payer type (BPJS, Asuransi, Umum)")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    report_metadata = Column(JSON, nullable=True, comment="Additional metadata")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Financial metrics"},
    )


class RegulatoryReport(Base):
    """Regulatory report model for tracking regulatory submissions"""
    __tablename__ = "regulatory_report"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(50), nullable=False, index=True, comment="Report code (SIRS, Kemenkes, etc.)")
    report_period_start = Column(DateTime(timezone=True), nullable=False, comment="Report period start")
    report_period_end = Column(DateTime(timezone=True), nullable=False, comment="Report period end")

    # Submission tracking
    status = Column(String(50), nullable=False, index=True, comment="Submission status")
    submitted_at = Column(DateTime(timezone=True), nullable=True, comment="Submission timestamp")
    submission_reference = Column(String(100), nullable=True, comment="Submission reference number")

    # Content
    report_data = Column(JSON, nullable=True, comment="Report data payload")
    response_data = Column(JSON, nullable=True, comment="Response from regulatory authority")

    # Verification
    is_verified = Column(Boolean, default=False, comment="Whether report was verified")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="Verification timestamp")
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Regulatory report submissions"},
    )
