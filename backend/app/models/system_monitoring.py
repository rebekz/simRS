"""System Monitoring Models for STORY-005: System Monitoring

This module provides database models for:
- System performance metrics (CPU, memory, disk, network)
- Database performance metrics
- Application performance metrics
- Health check results
- Monitoring thresholds and alerts

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class MetricType:
    """Metric type constants"""
    SYSTEM = "system"          # CPU, memory, disk
    DATABASE = "database"       # DB connection pool, query performance
    APPLICATION = "application" # Request rate, response time
    CUSTOM = "custom"           # Custom application metrics


class MetricUnit:
    """Metric unit constants"""
    PERCENT = "percent"
    BYTES = "bytes"
    MILLISECONDS = "milliseconds"
    COUNT = "count"
    PER_SECOND = "per_second"


class SystemMetric(Base):
    """System metric model

    Stores time-series system performance metrics.
    """
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique metric ID")

    # Metric identification
    metric_type = Column(String(50), nullable=False, index=True, comment="Metric type (system, database, application)")
    metric_name = Column(String(255), nullable=False, index=True, comment="Metric name (cpu.usage, memory.available, etc.)")
    metric_unit = Column(String(50), nullable=True, comment="Unit of measurement")

    # Metric value
    metric_value = Column(Float, nullable=False, comment="Metric value")
    tags = Column(JSON, nullable=True, comment="Tags for filtering (host, instance, etc.)")

    # Time series
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, comment="When metric was recorded")
    interval = Column(String(20), nullable=False, default="minute", comment="Aggregation interval (second, minute, hour)")

    # Metadata
    source = Column(String(100), nullable=True, comment="Metric source (hostname, service name)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "System performance metrics time-series"},
    )


class DatabaseMetric(Base):
    """Database performance metric model

    Stores PostgreSQL performance metrics.
    """
    __tablename__ = "database_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique metric ID")

    # Connection metrics
    active_connections = Column(Integer, nullable=True, comment="Active database connections")
    idle_connections = Column(Integer, nullable=True, comment="Idle connections")
    total_connections = Column(Integer, nullable=True, comment="Total connections")
    max_connections = Column(Integer, nullable=True, comment="Maximum allowed connections")

    # Query performance
    avg_query_duration_ms = Column(Float, nullable=True, comment="Average query duration")
    slow_query_count = Column(Integer, nullable=True, comment="Number of slow queries")
    query_count = Column(Integer, nullable=True, comment="Total queries in interval")
    failed_query_count = Column(Integer, nullable=True, comment="Failed queries")

    # Transaction metrics
    transaction_count = Column(Integer, nullable=True, comment="Transactions in interval")
    rollback_count = Column(Integer, nullable=True, comment="Transaction rollbacks")
    deadlock_count = Column(Integer, nullable=True, comment="Deadlocks detected")

    # Cache performance
    cache_hit_ratio = Column(Float, nullable=True, comment="Cache hit ratio (0-1)")

    # Storage
    database_size_bytes = Column(Integer, nullable=True, comment="Database size in bytes")
    transaction_log_size_bytes = Column(Integer, nullable=True, comment="Transaction log size")

    # Replication (if applicable)
    replication_lag_bytes = Column(Integer, nullable=True, comment="Replication lag")
    is_replica = Column(Boolean, nullable=False, default=False, comment="Whether this is a replica")

    # Time series
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, comment="When metric was recorded")
    interval = Column(String(20), nullable=False, default="minute", comment="Aggregation interval")

    # Metadata
    hostname = Column(String(255), nullable=True, comment="Database hostname")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Database performance metrics"},
    )


class ApplicationMetric(Base):
    """Application performance metric model

    Stores FastAPI application performance metrics.
    """
    __tablename__ = "application_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique metric ID")

    # Request metrics
    endpoint = Column(String(255), nullable=False, index=True, comment="API endpoint path")
    method = Column(String(10), nullable=False, comment="HTTP method")
    request_count = Column(Integer, nullable=False, comment="Number of requests")

    # Response time metrics
    avg_response_time_ms = Column(Float, nullable=True, comment="Average response time")
    p50_response_time_ms = Column(Float, nullable=True, comment="Median response time")
    p95_response_time_ms = Column(Float, nullable=True, comment="95th percentile response time")
    p99_response_time_ms = Column(Float, nullable=True, comment="99th percentile response time")

    # Error metrics
    error_count = Column(Integer, nullable=False, default=0, comment="Number of errors")
    error_rate = Column(Float, nullable=True, comment="Error rate (0-1)")
    status_5xx_count = Column(Integer, nullable=False, default=0, comment="5xx errors")
    status_4xx_count = Column(Integer, nullable=False, default=0, comment="4xx errors")

    # Throughput
    requests_per_second = Column(Float, nullable=True, comment="Requests per second")

    # Time series
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, comment="When metric was recorded")
    interval = Column(String(20), nullable=False, default="minute", comment="Aggregation interval")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Application performance metrics"},
    )


class HealthCheckResult(Base):
    """Health check result model

    Stores results of system health checks.
    """
    __tablename__ = "health_check_results"

    id = Column(Integer, primary_key=True, index=True)
    check_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique check ID")

    # Check identification
    check_name = Column(String(255), nullable=False, index=True, comment="Health check name")
    check_type = Column(String(50), nullable=False, comment="Check type (system, database, api, external)")
    component = Column(String(100), nullable=False, index=True, comment="Component being checked")

    # Check result
    status = Column(String(20), nullable=False, index=True, comment="Status (healthy, degraded, unhealthy)")
    response_time_ms = Column(Integer, nullable=True, comment="Check response time")
    message = Column(String(500), nullable=True, comment="Status message")

    # Details
    details = Column(JSON, nullable=True, comment="Additional check details")
    output = Column(Text, nullable=True, comment="Check output text")

    # Error info
    error = Column(Text, nullable=True, comment="Error message if failed")
    error_type = Column(String(100), nullable=True, comment="Error type")

    # Time series
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, comment="When check was performed")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Health check results"},
    )


class MonitoringThreshold(Base):
    """Monitoring threshold model

    Defines alerting thresholds for metrics.
    """
    __tablename__ = "monitoring_thresholds"

    id = Column(Integer, primary_key=True, index=True)

    # Threshold identification
    name = Column(String(255), unique=True, nullable=False, index=True, comment="Threshold name")
    metric_name = Column(String(255), nullable=False, index=True, comment="Metric to monitor")
    metric_type = Column(String(50), nullable=False, comment="Metric type (system, database, application)")

    # Threshold values
    warning_threshold = Column(Float, nullable=True, comment="Warning threshold value")
    critical_threshold = Column(Float, nullable=True, comment="Critical threshold value")
    comparison = Column(String(10), nullable=False, default=">", comment="Comparison operator (>, <, >=, <=, =)")

    # Conditions
    tags = Column(JSON, nullable=True, comment="Tags to match (filter specific instances)")
    duration_seconds = Column(Integer, nullable=False, default=300, comment="Duration before alerting (breach time)")

    # Alerting
    alert_on_warning = Column(Boolean, nullable=False, default=True, comment="Send alert on warning")
    alert_on_critical = Column(Boolean, nullable=False, default=True, comment="Send alert on critical")
    notification_channels = Column(JSON, nullable=True, comment="Notification channels (email, slack, etc.)")

    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Whether threshold is active")

    # Metadata
    description = Column(Text, nullable=True, comment="Threshold description")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who created threshold")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    creator = relationship("User")

    __table_args__ = (
        {"extend_existing": True, "comment": "Monitoring alert thresholds"},
    )


class MetricAggregation(Base):
    """Metric aggregation model

    Stores pre-aggregated metrics for performance.
    """
    __tablename__ = "metric_aggregations"

    id = Column(Integer, primary_key=True, index=True)
    aggregation_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique aggregation ID")

    # Aggregation identification
    metric_name = Column(String(255), nullable=False, index=True, comment="Aggregated metric name")
    metric_type = Column(String(50), nullable=False, comment="Metric type")

    # Aggregation period
    interval = Column(String(20), nullable=False, comment="Aggregation interval (hour, day, week)")
    period_start = Column(DateTime(timezone=True), nullable=False, index=True, comment="Period start")
    period_end = Column(DateTime(timezone=True), nullable=False, comment="Period end")

    # Aggregated values
    avg_value = Column(Float, nullable=True, comment="Average value")
    min_value = Column(Float, nullable=True, comment="Minimum value")
    max_value = Column(Float, nullable=True, comment="Maximum value")
    sum_value = Column(Float, nullable=True, comment="Sum of values")
    count = Column(Integer, nullable=False, comment="Number of samples")

    # Percentiles
    p50_value = Column(Float, nullable=True, comment="Median (50th percentile)")
    p95_value = Column(Float, nullable=True, comment="95th percentile")
    p99_value = Column(Float, nullable=True, comment="99th percentile")

    # Tags
    tags = Column(JSON, nullable=True, comment="Tags for this aggregation")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Aggregated metrics for performance"},
    )


class AlertEscalation(Base):
    """Alert escalation model

    Tracks alert escalation history.
    """
    __tablename__ = "alert_escalations"

    id = Column(Integer, primary_key=True, index=True)
    escalation_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique escalation ID")

    # Related alert
    alert_id = Column(Integer, ForeignKey("system_alerts.id"), nullable=False, index=True, comment="Related system alert")

    # Escalation details
    escalation_level = Column(Integer, nullable=False, comment="Current escalation level")
    previous_level = Column(Integer, nullable=True, comment="Previous escalation level")
    escalation_reason = Column(Text, nullable=True, comment="Reason for escalation")

    # Notification
    notified_users = Column(JSON, nullable=True, comment="Users notified at this level")
    notification_channels = Column(JSON, nullable=True, comment="Channels used for notification")

    # Status
    acknowledged = Column(Boolean, nullable=False, default=False, comment="Whether escalation was acknowledged")
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who acknowledged")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="Acknowledgment timestamp")

    # Timestamps
    escalated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="Escalation timestamp")

    # Relationships
    alert = relationship("SystemAlert", foreign_keys=[alert_id])
    acknowledger = relationship("User")

    __table_args__ = (
        {"extend_existing": True, "comment": "Alert escalation tracking"},
    )
