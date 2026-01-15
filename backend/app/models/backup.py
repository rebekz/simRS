"""Backup Models for STORY-004: Automated Backup System

This module provides database models for:
- Automated backup jobs and schedules
- Backup retention policies
- Backup restoration tracking
- Backup monitoring and alerting

Python 3.5+ compatible
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, JSON, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.session import Base


class BackupStatus:
    """Backup status constants"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackupType:
    """Backup type constants"""
    FULL = "full"
    DIFFERENTIAL = "differential"
    INCREMENTAL = "incremental"


class BackupJob(Base):
    """Backup job model

    Tracks automated backup jobs for database and file system backups.
    """
    __tablename__ = "backup_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique job ID")

    # Job configuration
    job_name = Column(String(255), nullable=False, comment="Human-readable job name")
    backup_type = Column(String(20), nullable=False, index=True, comment="Backup type (full, differential, incremental)")
    source_type = Column(String(50), nullable=False, comment="Source type (database, files, uploads)")
    source_path = Column(Text, nullable=True, comment="Source path for file backups")

    # Schedule
    schedule_type = Column(String(20), nullable=False, comment="Schedule type (manual, daily, weekly, monthly)")
    cron_expression = Column(String(100), nullable=True, comment="Cron expression for flexible scheduling")
    scheduled_time = Column(String(10), nullable=True, comment="Scheduled time (HH:MM format)")

    # Storage
    storage_type = Column(String(50), nullable=False, comment="Storage type (local, s3, gcs, azure, sftp)")
    storage_path = Column(Text, nullable=True, comment="Storage destination path")
    storage_config = Column(JSON, nullable=True, comment="Storage credentials and config")

    # Execution
    status = Column(String(20), nullable=False, index=True, default=BackupStatus.PENDING, comment="Backup job status")
    started_at = Column(DateTime(timezone=True), nullable=True, comment="Job start time")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Job completion time")
    duration_seconds = Column(Integer, nullable=True, comment="Job duration in seconds")

    # Results
    backup_path = Column(Text, nullable=True, comment="Path where backup was stored")
    backup_size_bytes = Column(Integer, nullable=True, comment="Size of backup in bytes")
    checksum = Column(String(100), nullable=True, comment="Backup file checksum (SHA256)")
    files_count = Column(Integer, nullable=True, comment="Number of files in backup")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")
    max_retries = Column(Integer, nullable=False, default=3, comment="Maximum retry attempts")

    # Encryption
    encryption_enabled = Column(Boolean, nullable=False, default=True, comment="Whether backup is encrypted")
    encryption_method = Column(String(50), nullable=True, comment="Encryption method (AES-256)")

    # Retention
    retention_days = Column(Integer, nullable=False, default=30, comment="Days to retain this backup")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who created the job")
    last_triggered_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who triggered the job")
    notes = Column(Text, nullable=True, comment="Additional notes")
    tags = Column(JSON, nullable=True, comment="Tags for categorization")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    triggerer = relationship("User", foreign_keys=[last_triggered_by])

    __table_args__ = (
        {"comment": "Automated backup jobs"},
    )


class BackupRetention(Base):
    """Backup retention policy model

    Manages retention policies for different backup types.
    """
    __tablename__ = "backup_retention_policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique policy ID")

    # Policy configuration
    policy_name = Column(String(255), nullable=False, comment="Policy name")
    description = Column(Text, nullable=True, comment="Policy description")

    # Retention periods
    daily_retention_days = Column(Integer, nullable=False, default=30, comment="Daily backups retention")
    weekly_retention_weeks = Column(Integer, nullable=False, default=12, comment="Weekly backups retention")
    monthly_retention_months = Column(Integer, nullable=False, default=84, comment="Monthly backups retention")

    # Archive settings
    archive_enabled = Column(Boolean, nullable=False, default=False, comment="Enable long-term archival")
    archive_location = Column(String(255), nullable=True, comment="Archive location (s3, glacier, etc.)")
    archive_after_days = Column(Integer, nullable=True, comment="Days before archiving")

    # Auto-cleanup
    auto_cleanup_enabled = Column(Boolean, nullable=False, default=True, comment="Enable automatic cleanup")
    cleanup_schedule = Column(String(100), nullable=True, comment="Cleanup schedule (cron)")

    # Notifications
    notify_on_cleanup = Column(Boolean, nullable=False, default=True, comment="Notify on cleanup operations")
    notification_recipients = Column(JSON, nullable=True, comment="Email/recipient list")

    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True, comment="Whether policy is active")

    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    creator = relationship("User")

    __table_args__ = (
        {"comment": "Backup retention policies"},
    )


class BackupRestore(Base):
    """Backup restoration model

    Tracks backup restoration operations.
    """
    __tablename__ = "backup_restorations"

    id = Column(Integer, primary_key=True, index=True)
    restore_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique restore ID")

    # Source backup
    backup_job_id = Column(Integer, ForeignKey("backup_jobs.id"), nullable=False, comment="Source backup job ID")
    backup_path = Column(Text, nullable=False, comment="Path to backup file to restore")

    # Restoration target
    target_type = Column(String(50), nullable=False, comment="Target type (database, files)")
    target_path = Column(Text, nullable=True, comment="Target path for file restoration")

    # Options
    restore_options = Column(JSON, nullable=True, comment="Restore options (overwrite, create_new, etc.)")
    dry_run = Column(Boolean, nullable=False, default=False, comment="Dry run without actual restoration")

    # Execution
    status = Column(String(20), nullable=False, index=True, default=BackupStatus.PENDING, comment="Restore status")
    started_at = Column(DateTime(timezone=True), nullable=True, comment="Restore start time")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Restore completion time")
    duration_seconds = Column(Integer, nullable=True, comment="Restore duration in seconds")

    # Results
    files_restored = Column(Integer, nullable=True, comment="Number of files restored")
    bytes_restored = Column(Integer, nullable=True, comment="Bytes restored")
    tables_restored = Column(Integer, nullable=True, comment="Number of database tables restored")

    # Validation
    checksum_verified = Column(Boolean, nullable=True, comment="Whether backup checksum was verified")
    validation_passed = Column(Boolean, nullable=True, comment="Whether post-restore validation passed")
    validation_errors = Column(Text, nullable=True, comment="Validation error messages")

    # Error handling
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    retry_count = Column(Integer, nullable=False, default=0, comment="Number of retry attempts")

    # Approval
    requires_approval = Column(Boolean, nullable=False, default=True, comment="Whether restore requires approval")
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who approved restore")
    approved_at = Column(DateTime(timezone=True), nullable=True, comment="Approval timestamp")
    approval_notes = Column(Text, nullable=True, comment="Approval notes")

    # Metadata
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="User who requested restore")
    notes = Column(Text, nullable=True, comment="Additional notes")
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    # Relationships
    backup_job = relationship("BackupJob")
    requester = relationship("User", foreign_keys=[requested_by])
    approver = relationship("User", foreign_keys=[approved_by])

    __table_args__ = (
        {"comment": "Backup restoration operations"},
    )


class BackupVerification(Base):
    """Backup verification model

    Tracks backup integrity verification and testing.
    """
    __tablename__ = "backup_verifications"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique verification ID")

    # Source backup
    backup_job_id = Column(Integer, ForeignKey("backup_jobs.id"), nullable=False, comment="Backup job to verify")

    # Verification type
    verification_type = Column(String(50), nullable=False, comment="Type (checksum, restore_test, integrity)")
    test_restoration = Column(Boolean, nullable=False, default=False, comment="Whether to test restoration")

    # Results
    status = Column(String(20), nullable=False, index=True, comment="Verification status")
    started_at = Column(DateTime(timezone=True), nullable=True, comment="Verification start time")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="Verification completion time")

    # Checksum verification
    checksum_algorithm = Column(String(20), nullable=True, comment="Algorithm used (SHA256, MD5)")
    expected_checksum = Column(String(100), nullable=True, comment="Expected checksum value")
    actual_checksum = Column(String(100), nullable=True, comment="Actual checksum value")
    checksum_match = Column(Boolean, nullable=True, comment="Whether checksums match")

    # Test restoration
    test_restore_db_name = Column(String(100), nullable=True, comment="Test database name")
    test_restore_successful = Column(Boolean, nullable=True, comment="Whether test restore succeeded")
    test_restore_errors = Column(Text, nullable=True, comment="Test restore errors")

    # Integrity check
    corruption_detected = Column(Boolean, nullable=False, default=False, comment="Whether corruption was detected")
    corruption_details = Column(Text, nullable=True, comment="Details of any corruption")

    # Issues
    issues_found = Column(Integer, nullable=False, default=0, comment="Number of issues found")
    issues_details = Column(JSON, nullable=True, comment="Details of issues found")

    # Metadata
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="User who triggered verification")
    notes = Column(Text, nullable=True, comment="Additional notes")
    created_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False)

    # Relationships
    backup_job = relationship("BackupJob")
    verifier = relationship("User")

    __table_args__ = (
        {"comment": "Backup integrity verification"},
    )


class BackupMetrics(Base):
    """Backup metrics model

    Tracks backup performance metrics and trends.
    """
    __tablename__ = "backup_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String(100), unique=True, nullable=False, index=True, comment="Unique metric ID")

    # Associated backup
    backup_job_id = Column(Integer, ForeignKey("backup_jobs.id"), nullable=False, index=True, comment="Associated backup job")

    # Performance metrics
    duration_seconds = Column(Integer, nullable=False, comment="Backup duration in seconds")
    backup_size_bytes = Column(Integer, nullable=False, comment="Backup size in bytes")
    compression_ratio = Column(Float, nullable=True, comment="Compression ratio achieved")
    throughput_mb_per_sec = Column(Float, nullable=True, comment="Throughput in MB/s")

    # Resource usage
    cpu_usage_percent = Column(Float, nullable=True, comment="CPU usage during backup")
    memory_usage_mb = Column(Integer, nullable=True, comment="Memory usage during backup")
    disk_io_mb = Column(Integer, nullable=True, comment="Disk I/O in MB")

    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=datetime.utcnow, nullable=False, index=True, comment="When metric was recorded")

    # Relationships
    backup_job = relationship("BackupJob")

    __table_args__ = (
        {"comment": "Backup performance metrics"},
    )
