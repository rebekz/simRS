"""Analytics Dashboard Models for EPIC-017

This module provides database models for:
- KPI definitions and targets
- Dashboard configurations
- Scheduled reports and snapshots
- Data aggregation and caching

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class KPICategory:
    """KPI category constants"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    CLINICAL = "clinical"
    PATIENT = "patient"
    QUALITY = "quality"
    RESOURCE = "resource"


class KPI(Base):
    """KPI (Key Performance Indicator) definition model

    Stores KPI definitions with calculation logic, targets,
    and historical tracking.
    """
    __tablename__ = "kpis"

    id = Column(Integer, primary_key=True, index=True)
    kpi_code = Column(String(100), unique=True, nullable=False, index=True, comment="KPI code")
    kpi_name = Column(String(255), nullable=False, comment="KPI name")
    kpi_category = Column(String(50), nullable=False, index=True, comment="KPI category")
    description = Column(Text, nullable=True, comment="KPI description")

    # Calculation
    calculation_method = Column(String(100), nullable=False, comment="Calculation method")
    sql_query = Column(Text, nullable=True, comment="SQL query for calculation")
    formula = Column(Text, nullable=True, comment="Calculation formula")
    data_source = Column(String(100), nullable=True, comment="Data source table/view")

    # Units and format
    unit = Column(String(50), nullable=True, comment="Unit of measure")
    decimal_places = Column(Integer, nullable=False, default=2, comment="Decimal places for display")
    format_type = Column(String(50), nullable=True, comment="Format type (number, percentage, currency)")

    # Targets
    target_value = Column(Float, nullable=True, comment="Target value")
    target_min = Column(Float, nullable=True, comment="Minimum acceptable value")
    target_max = Column(Float, nullable=True, comment="Maximum acceptable value")
    target_direction = Column(String(20), nullable=False, default="higher_is_better", comment="Target direction")

    # Aggregation
    aggregation_type = Column(String(50), nullable=False, default="sum", comment="Aggregation type (sum, avg, count)")
    aggregation_period = Column(String(50), nullable=False, default="daily", comment="Aggregation period")

    # Visualization
    chart_type = Column(String(50), nullable=True, comment="Recommended chart type")
    color_scheme = Column(String(100), nullable=True, comment="Color scheme for visualization")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether KPI is active")
    display_order = Column(Integer, nullable=False, default=0, comment="Display order in dashboard")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    history = relationship("KPIHistory", back_populates="kpi", cascade="all, delete-orphan")

    __table_args__ = (
        {"comment": "KPI definitions"},
    )


class KPIHistory(Base):
    """KPI historical data model

    Stores historical KPI values for trend analysis.
    """
    __tablename__ = "kpi_history"

    id = Column(Integer, primary_key=True, index=True)
    kpi_id = Column(Integer, ForeignKey("kpis.id"), nullable=False, index=True, comment="KPI ID")

    # Value
    period_start = Column(DateTime(timezone=True), nullable=False, index=True, comment="Period start")
    period_end = Column(DateTime(timezone=True), nullable=False, comment="Period end")
    period_type = Column(String(50), nullable=False, comment="Period type (daily, weekly, monthly)")
    value = Column(Float, nullable=False, comment="KPI value for period")

    # Comparison
    target_value = Column(Float, nullable=True, comment="Target value for period")
    variance = Column(Float, nullable=True, comment="Variance from target")
    variance_percent = Column(Float, nullable=True, comment="Variance percentage")

    # Context
    numerator = Column(Float, nullable=True, comment="Numerator value")
    denominator = Column(Float, nullable=True, comment="Denominator value")
    analytics_metadata = Column(JSON, nullable=True, comment="Additional metadata")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    kpi = relationship("KPI", back_populates="history")

    __table_args__ = (
        {"comment": "KPI historical data"},
    )


class Dashboard(Base):
    """Dashboard configuration model

    Stores dashboard configurations with widget layouts.
    """
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_code = Column(String(100), unique=True, nullable=False, index=True, comment="Dashboard code")
    dashboard_name = Column(String(255), nullable=False, comment="Dashboard name")
    description = Column(Text, nullable=True, comment="Dashboard description")

    # Configuration
    dashboard_type = Column(String(50), nullable=False, comment="Dashboard type (executive, clinical, operational)")
    layout_config = Column(JSON, nullable=False, comment="Layout configuration")
    refresh_interval = Column(Integer, nullable=False, default=300, comment="Refresh interval (seconds)")

    # Access control
    is_public = Column(Boolean, default=False, nullable=False, comment="Whether dashboard is public")
    allowed_roles = Column(JSON, nullable=True, comment="Allowed user roles")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether dashboard is active")
    display_order = Column(Integer, nullable=False, default=0, comment="Display order")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")

    __table_args__ = (
        {"comment": "Dashboard configurations"},
    )


class DashboardWidget(Base):
    """Dashboard widget model

    Stores widget definitions for dashboards.
    """
    __tablename__ = "dashboard_widgets"

    id = Column(Integer, primary_key=True, index=True)
    widget_id = Column(String(100), unique=True, nullable=False, index=True, comment="Widget ID")

    # Entity mapping
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=False, index=True, comment="Dashboard ID")
    kpi_id = Column(Integer, ForeignKey("kpis.id"), nullable=True, index=True, comment="KPI ID")

    # Widget configuration
    widget_type = Column(String(50), nullable=False, comment="Widget type (chart, metric, table)")
    widget_name = Column(String(255), nullable=False, comment="Widget name")
    description = Column(Text, nullable=True, comment="Widget description")

    # Position and size
    position_x = Column(Integer, nullable=False, default=0, comment="X position")
    position_y = Column(Integer, nullable=False, default=0, comment="Y position")
    width = Column(Integer, nullable=False, default=4, comment="Widget width (grid units)")
    height = Column(Integer, nullable=False, default=3, comment="Widget height (grid units)")

    # Display configuration
    config = Column(JSON, nullable=False, comment="Widget configuration")
    data_source = Column(String(100), nullable=True, comment="Data source")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, comment="Whether widget is active")
    display_order = Column(Integer, nullable=False, default=0, comment="Display order")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")

    __table_args__ = (
        {"comment": "Dashboard widgets"},
    )


class DataCache(Base):
    """Analytics data cache model

    Stores pre-computed analytics data for performance.
    """
    __tablename__ = "analytics_cache"

    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, nullable=False, index=True, comment="Cache key")

    # Cache data
    data = Column(JSON, nullable=False, comment="Cached data")
    data_type = Column(String(50), nullable=False, index=True, comment="Data type")

    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=False, comment="Valid from")
    valid_until = Column(DateTime(timezone=True), nullable=True, comment="Valid until")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Analytics data cache"},
    )


class ScheduledReport(Base):
    """Scheduled report model

    Stores scheduled analytics report configurations.
    """
    __tablename__ = "scheduled_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), unique=True, nullable=False, index=True, comment="Report ID")

    # Report details
    report_name = Column(String(255), nullable=False, comment="Report name")
    report_type = Column(String(50), nullable=False, comment="Report type")
    description = Column(Text, nullable=True, comment="Report description")

    # Schedule
    schedule_type = Column(String(50), nullable=False, comment="Schedule type (daily, weekly, monthly)")
    schedule_config = Column(JSON, nullable=False, comment="Schedule configuration")
    next_run_at = Column(DateTime(timezone=True), nullable=True, index=True, comment="Next run time")

    # Recipients
    recipients = Column(JSON, nullable=False, comment="Report recipients")
    format = Column(String(50), nullable=False, default="pdf", comment="Report format")

    # Content
    kpi_ids = Column(JSON, nullable=True, comment="Included KPIs")
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=True, comment="Dashboard snapshot")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True, comment="Whether report is active")
    last_run_at = Column(DateTime(timezone=True), nullable=True, comment="Last run time")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Scheduled analytics reports"},
    )


class ReportSnapshot(Base):
    """Report snapshot model

    Stores historical report snapshots.
    """
    __tablename__ = "report_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    snapshot_id = Column(String(100), unique=True, nullable=False, index=True, comment="Snapshot ID")

    # Entity mapping
    scheduled_report_id = Column(Integer, ForeignKey("scheduled_reports.id"), nullable=True, index=True, comment="Scheduled report ID")
    report_type = Column(String(50), nullable=False, comment="Report type")

    # Content
    report_data = Column(JSON, nullable=False, comment="Report data")
    summary = Column(Text, nullable=True, comment="Report summary")

    # Period
    period_start = Column(DateTime(timezone=True), nullable=True, comment="Report period start")
    period_end = Column(DateTime(timezone=True), nullable=True, comment="Report period end")

    # File storage
    file_path = Column(String(500), nullable=True, comment="Generated file path")
    file_size = Column(Integer, nullable=True, comment="File size in bytes")

    # Metadata
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"comment": "Report snapshots"},
    )
