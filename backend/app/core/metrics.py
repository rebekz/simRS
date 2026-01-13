"""
Prometheus metrics for SIMRS application.

This module defines custom Prometheus metrics for monitoring
application performance and health.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Optional
import os


# Application info
app_info = Info(
    'simrs_application',
    'SIMRS Application information'
)


# Request metrics
http_requests_total = Counter(
    'simrs_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'simrs_http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=(.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_requests_in_progress = Gauge(
    'simrs_http_requests_in_progress',
    'HTTP requests currently in progress',
    ['method', 'endpoint']
)


# Database metrics
db_queries_total = Counter(
    'simrs_db_queries_total',
    'Total database queries',
    ['operation', 'table']
)

db_query_duration_seconds = Histogram(
    'simrs_db_query_duration_seconds',
    'Database query latency',
    ['operation', 'table'],
    buckets=(.001, .005, .01, .025, .05, .1, .25, .5, 1.0, 2.5, 5.0)
)

db_connections_active = Gauge(
    'simrs_db_connections_active',
    'Active database connections',
    ['state']  # state: idle, active, used
)


# Cache metrics (Redis)
cache_operations_total = Counter(
    'simrs_cache_operations_total',
    'Total cache operations',
    ['operation', 'status']  # operation: get, set, delete; status: hit, miss, error
)

cache_duration_seconds = Histogram(
    'simrs_cache_duration_seconds',
    'Cache operation latency',
    ['operation'],
    buckets=(.0001, .0005, .001, .005, .01, .025, .05, .1)
)


# Authentication metrics
auth_attempts_total = Counter(
    'simrs_auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']  # method: login, mfa, refresh; status: success, failure
)

auth_sessions_active = Gauge(
    'simrs_auth_sessions_active',
    'Active user sessions'
)


# Business logic metrics
patient_registrations_total = Counter(
    'simrs_patient_registrations_total',
    'Total patient registrations',
    ['type']  # type: new, returning
)

bpjs_api_calls_total = Counter(
    'simrs_bpjs_api_calls_total',
    'Total BPJS API calls',
    ['endpoint', 'status']  # status: success, failure, timeout
)

bpjs_api_duration_seconds = Histogram(
    'simrs_bpjs_api_duration_seconds',
    'BPJS API call latency',
    ['endpoint'],
    buckets=(.1, .5, 1.0, 2.5, 5.0, 10.0, 30.0)
)


# Audit metrics
audit_log_entries_total = Counter(
    'simrs_audit_log_entries_total',
    'Total audit log entries',
    ['action', 'resource']
)


# Backup metrics
backup_operations_total = Counter(
    'simrs_backup_operations_total',
    'Total backup operations',
    ['type', 'status']  # type: full, wal; status: success, failure
)

backup_size_bytes = Gauge(
    'simrs_backup_size_bytes',
    'Backup size in bytes',
    ['type']
)

backup_last_success_timestamp = Gauge(
    'simrs_backup_last_success_timestamp',
    'Last successful backup timestamp',
    ['type']
)


# System health metrics
system_health_status = Gauge(
    'simrs_system_health_status',
    'System health status (1=healthy, 0=unhealthy)',
    ['service']  # service: database, redis, minio, external_api
)

disk_usage_bytes = Gauge(
    'simrs_disk_usage_bytes',
    'Disk usage in bytes',
    ['mount_point', 'type']  # type: used, free, total
)

memory_usage_bytes = Gauge(
    'simrs_memory_usage_bytes',
    'Memory usage in bytes',
    ['type']  # type: used, free, total, cached, buffers
)


# Error metrics
errors_total = Counter(
    'simrs_errors_total',
    'Total errors',
    ['type', 'severity']  # type: validation, database, external_api; severity: warning, error, critical
)


# Task/Job metrics
background_jobs_total = Counter(
    'simrs_background_jobs_total',
    'Total background jobs executed',
    ['job_type', 'status']
)

background_job_duration_seconds = Histogram(
    'simrs_background_job_duration_seconds',
    'Background job duration',
    ['job_type'],
    buckets=(1, 5, 10, 30, 60, 300, 600, 1800)
)


def initialize_metrics():
    """Initialize metrics with default values."""
    app_info.info({
        'version': os.getenv('VERSION', '1.0.0'),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'app_name': 'SIMRS'
    })
