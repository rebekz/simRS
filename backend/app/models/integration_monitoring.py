"""Integration Monitoring Models for STORY-024-11

This module provides database models for:
- Integration endpoint monitoring
- Integration logs and errors
- Performance metrics tracking
- Health check status

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float, func
from sqlalchemy.orm import relationship
from app.db.session import Base


class EndpointStatus:
    """Endpoint status constants"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class MessageDirection:
    """Message direction constants"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class ErrorSeverity:
    """Error severity constants"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class IntegrationEndpoint(Base):
    """Integration endpoint model

    Stores configuration and status of external integration endpoints.
    """
    __tablename__ = "integration_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(String(100), unique=True, nullable=False, index=True, comment="Endpoint ID")
    endpoint_name = Column(String(255), nullable=False, comment="Endpoint name")
    endpoint_code = Column(String(100), unique=True, nullable=False, index=True, comment="Endpoint code")

    # Endpoint configuration
    endpoint_type = Column(String(50), nullable=False, index=True, comment="Endpoint type (HL7, FHIR, DICOM, REST, etc.)")
    endpoint_url = Column(String(500), nullable=True, comment="Endpoint URL")
    protocol = Column(String(50), nullable=False, comment="Communication protocol")
    port = Column(Integer, nullable=True, comment="Port number")

    # Authentication
    auth_type = Column(String(50), nullable=True, comment="Authentication type")
    auth_credentials = Column(JSON, nullable=True, comment="Encrypted credentials")

    # Configuration
    endpoint_config = Column(JSON, nullable=True, comment="Endpoint configuration")
    timeout_seconds = Column(Integer, nullable=False, default=30, comment="Request timeout")
    retry_attempts = Column(Integer, nullable=False, default=3, comment="Number of retry attempts")
    retry_delay_ms = Column(Integer, nullable=False, default=1000, comment="Retry delay in milliseconds")

    # Health monitoring
    status = Column(String(50), nullable=False, index=True, default=EndpointStatus.OFFLINE, comment="Endpoint status")
    last_health_check = Column(DateTime(timezone=True), nullable=True, comment="Last health check timestamp")
    last_success = Column(DateTime(timezone=True), nullable=True, comment="Last successful connection")
    last_error = Column(DateTime(timezone=True), nullable=True, comment="Last error timestamp")
    last_error_message = Column(Text, nullable=True, comment="Last error message")

    # Statistics
    total_requests = Column(Integer, nullable=False, default=0, comment="Total requests sent")
    successful_requests = Column(Integer, nullable=False, default=0, comment="Successful requests")
    failed_requests = Column(Integer, nullable=False, default=0, comment="Failed requests")
    average_response_time_ms = Column(Float, nullable=True, comment="Average response time")
    uptime_percentage = Column(Float, nullable=True, comment="Uptime percentage")

    # Alerting
    alert_on_failure = Column(Boolean, nullable=False, default=True, comment="Alert on endpoint failure")
    alert_on_slow_response = Column(Boolean, nullable=False, default=False, comment="Alert on slow response")
    slow_response_threshold_ms = Column(Integer, nullable=False, default=5000, comment="Slow response threshold")

    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Whether endpoint is active")
    is_monitored = Column(Boolean, nullable=False, default=True, comment="Whether endpoint is monitored")

    # Metadata
    description = Column(Text, nullable=True, comment="Endpoint description")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    logs = relationship("IntegrationLog", back_populates="endpoint", cascade="all, delete-orphan")
    errors = relationship("IntegrationError", back_populates="endpoint", cascade="all, delete-orphan")
    health_checks = relationship("HealthCheck", back_populates="endpoint", cascade="all, delete-orphan")

    __table_args__ = (
        {"extend_existing": True, "comment": "Integration endpoint configuration and monitoring"},
    )


class IntegrationLog(Base):
    """Integration log model

    Logs all integration message traffic.
    """
    __tablename__ = "integration_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(100), unique=True, nullable=False, index=True, comment="Log ID")

    # Endpoint association
    endpoint_id = Column(Integer, ForeignKey("integration_endpoints.id"), nullable=True, index=True, comment="Endpoint ID")

    # Message info
    message_type = Column(String(50), nullable=False, index=True, comment="Message type (ADT, ORM, ORU, etc.)")
    message_id = Column(String(100), nullable=True, index=True, comment="Message ID")
    correlation_id = Column(String(100), nullable=True, index=True, comment="Correlation ID for tracing")
    direction = Column(String(20), nullable=False, index=True, comment="Message direction (inbound/outbound)")

    # Message content
    message_content = Column(JSON, nullable=True, comment="Message content (parsed)")
    raw_message = Column(Text, nullable=True, comment="Raw message string")

    # Processing info
    status = Column(String(50), nullable=False, index=True, comment="Processing status (success, error, pending)")
    status_code = Column(Integer, nullable=True, comment="HTTP status code or HL7 ACK code")
    response_time_ms = Column(Integer, nullable=True, comment="Response time in milliseconds")

    # Response
    response_content = Column(JSON, nullable=True, comment="Response content")
    response_raw = Column(Text, nullable=True, comment="Raw response string")

    # Error handling
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=True, comment="Error message")
    error_details = Column(JSON, nullable=True, comment="Detailed error information")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    endpoint = relationship("IntegrationEndpoint", back_populates="logs")

    __table_args__ = (
        {"extend_existing": True, "comment": "Integration message logs"},
    )


class IntegrationError(Base):
    """Integration error model

    Stores integration errors for analysis and alerting.
    """
    __tablename__ = "integration_errors"

    id = Column(Integer, primary_key=True, index=True)
    error_id = Column(String(100), unique=True, nullable=False, index=True, comment="Error ID")

    # Endpoint association
    endpoint_id = Column(Integer, ForeignKey("integration_endpoints.id"), nullable=True, index=True, comment="Endpoint ID")
    log_id = Column(Integer, ForeignKey("integration_logs.id"), nullable=True, index=True, comment="Related log ID")

    # Error classification
    error_type = Column(String(50), nullable=False, index=True, comment="Error type (parsing, validation, transformation, transmission)")
    error_category = Column(String(50), nullable=False, index=True, comment="Error category (network, auth, protocol, data)")
    severity = Column(String(50), nullable=False, index=True, default=ErrorSeverity.ERROR, comment="Error severity")

    # Error details
    error_code = Column(String(50), nullable=True, comment="Error code")
    error_message = Column(Text, nullable=False, comment="Error message")
    error_details = Column(JSON, nullable=True, comment="Detailed error information")
    stack_trace = Column(Text, nullable=True, comment="Stack trace for debugging")

    # Resolution
    is_resolved = Column(Boolean, nullable=False, default=False, index=True, comment="Whether error is resolved")
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="Resolution timestamp")
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Resolved by")
    resolution_notes = Column(Text, nullable=True, comment="Resolution notes")

    # Alerting
    alert_sent = Column(Boolean, nullable=False, default=False, comment="Whether alert was sent")
    alert_sent_at = Column(DateTime(timezone=True), nullable=True, comment="Alert sent timestamp")
    escalation_level = Column(Integer, nullable=False, default=0, comment="Escalation level")

    # Metadata
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    endpoint = relationship("IntegrationEndpoint", back_populates="errors")

    __table_args__ = (
        {"extend_existing": True, "comment": "Integration error tracking"},
    )


class HealthCheck(Base):
    """Health check model

    Stores health check results for endpoints.
    """
    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)
    check_id = Column(String(100), unique=True, nullable=False, index=True, comment="Health check ID")

    # Endpoint association
    endpoint_id = Column(Integer, ForeignKey("integration_endpoints.id"), nullable=False, index=True, comment="Endpoint ID")

    # Check details
    check_type = Column(String(50), nullable=False, comment="Check type (connectivity, authentication, full)")
    status = Column(String(50), nullable=False, index=True, comment="Check status (healthy, unhealthy, degraded)")
    response_time_ms = Column(Integer, nullable=True, comment="Response time in milliseconds")

    # Check results
    is_reachable = Column(Boolean, nullable=False, comment="Whether endpoint is reachable")
    is_authenticated = Column(Boolean, nullable=True, comment="Whether authentication succeeded")
    details = Column(JSON, nullable=True, comment="Additional check details")

    # Error info
    error_code = Column(String(50), nullable=True, comment="Error code if check failed")
    error_message = Column(Text, nullable=True, comment="Error message if check failed")

    # Metadata
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    endpoint = relationship("IntegrationEndpoint", back_populates="health_checks")

    __table_args__ = (
        {"extend_existing": True, "comment": "Health check results"},
    )


class IntegrationMetric(Base):
    """Integration metric model

    Stores performance and operational metrics for integrations.
    """
    __tablename__ = "integration_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(100), unique=True, nullable=False, index=True, comment="Metric ID")

    # Entity
    endpoint_id = Column(Integer, ForeignKey("integration_endpoints.id"), nullable=True, index=True, comment="Endpoint ID")
    metric_type = Column(String(50), nullable=False, index=True, comment="Metric type (throughput, error_rate, response_time)")

    # Metric data
    metric_name = Column(String(255), nullable=False, comment="Metric name")
    metric_value = Column(Float, nullable=False, comment="Metric value")
    metric_unit = Column(String(50), nullable=True, comment="Metric unit")

    # Time series
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True, comment="Metric timestamp")
    interval = Column(String(20), nullable=False, comment="Interval (minute, hour, day)")

    # Dimensions
    dimensions = Column(JSON, nullable=True, comment="Metric dimensions for filtering")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        {"extend_existing": True, "comment": "Integration performance metrics"},
    )


class IntegrationAlert(Base):
    """Integration alert model

    Stores alerts generated from integration monitoring.
    """
    __tablename__ = "integration_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(100), unique=True, nullable=False, index=True, comment="Alert ID")

    # Entity
    endpoint_id = Column(Integer, ForeignKey("integration_endpoints.id"), nullable=True, index=True, comment="Related endpoint ID")
    error_id = Column(Integer, ForeignKey("integration_errors.id"), nullable=True, index=True, comment="Related error ID")

    # Alert details
    alert_type = Column(String(50), nullable=False, index=True, comment="Alert type (endpoint_down, high_error_rate, slow_response)")
    severity = Column(String(50), nullable=False, index=True, comment="Alert severity (info, warning, error, critical)")
    title = Column(String(255), nullable=False, comment="Alert title")
    message = Column(Text, nullable=False, comment="Alert message")
    details = Column(JSON, nullable=True, comment="Additional alert details")

    # Status
    status = Column(String(50), nullable=False, index=True, default="open", comment="Alert status (open, acknowledged, resolved)")
    acknowledged_at = Column(DateTime(timezone=True), nullable=True, comment="Acknowledged timestamp")
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Acknowledged by")
    resolved_at = Column(DateTime(timezone=True), nullable=True, comment="Resolved timestamp")
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="Resolved by")
    resolution_notes = Column(Text, nullable=True, comment="Resolution notes")

    # Escalation
    escalation_level = Column(Integer, nullable=False, default=0, comment="Escalation level")
    escalated_at = Column(DateTime(timezone=True), nullable=True, comment="Escalation timestamp")

    # Notification
    notification_sent = Column(Boolean, nullable=False, default=False, comment="Whether notification was sent")
    notification_channels = Column(JSON, nullable=True, comment="Channels notified (email, sms, in_app)")

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        {"extend_existing": True, "comment": "Integration monitoring alerts"},
    )
