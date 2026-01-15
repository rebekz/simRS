"""Audit Service for STORY-003: Audit Logging System

This module provides services for audit log management, including:
- Query and filtering of audit logs
- Export functionality
- Alerting for sensitive operations
- Retention policy management

Python 3.5+ compatible
"""

import logging
import csv
import io
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.audit_log import AuditLog
from app.models.system_alerts import SystemAlert, AlertSeverity, AlertStatus
from app.models.user import User
from app.core.encryption import encrypt_field


logger = logging.getLogger(__name__)


# Sensitive operation patterns that require alerting
SENSITIVE_OPERATION_RULES = {
    "data_export": {
        "actions": ["READ"],
        "resources": ["patients", "bulk_export", "export"],
        "severity": AlertSeverity.HIGH,
        "message_template": "Sensitive data export performed by {username}: {resource_type}",
    },
    "data_deletion": {
        "actions": ["DELETE"],
        "resources": ["patients", "medical_records", "encounters"],
        "severity": AlertSeverity.CRITICAL,
        "message_template": "Critical data deletion by {username}: {resource_type}/{resource_id}",
    },
    "permission_change": {
        "actions": ["CREATE", "UPDATE"],
        "resources": ["users", "permissions", "roles"],
        "severity": AlertSeverity.HIGH,
        "message_template": "Permission change by {username}: {resource_type}",
    },
    "auth_failure": {
        "actions": ["LOGIN", "AUTH"],
        "resources": ["auth", "login"],
        "failure_only": True,
        "severity": AlertSeverity.MEDIUM,
        "message_template": "Authentication failure for {username} from {ip_address}",
    },
    "bulk_operation": {
        "actions": ["CREATE", "UPDATE", "DELETE"],
        "resources": ["bulk", "batch"],
        "severity": AlertSeverity.HIGH,
        "message_template": "Bulk operation by {username}: {action} on {resource_type}",
    },
}


class AuditQueryService(object):
    """Service for querying and filtering audit logs"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Query audit logs with filters

        Args:
            user_id: Filter by user ID
            username: Filter by username (partial match)
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            start_date: Filter by start date
            end_date: Filter by end date
            success: Filter by success status
            limit: Maximum records to return
            offset: Number of records to skip

        Returns:
            Dict with logs list, total count, and pagination info
        """
        try:
            # Build base query
            query = select(AuditLog)

            # Apply filters
            conditions = []
            if user_id is not None:
                conditions.append(AuditLog.user_id == user_id)
            if username is not None:
                conditions.append(AuditLog.username.ilike("%{}%".format(username)))
            if action is not None:
                conditions.append(AuditLog.action == action)
            if resource_type is not None:
                conditions.append(AuditLog.resource_type == resource_type)
            if resource_id is not None:
                conditions.append(AuditLog.resource_id == resource_id)
            if start_date is not None:
                conditions.append(AuditLog.timestamp >= start_date)
            if end_date is not None:
                conditions.append(AuditLog.timestamp <= end_date)
            if success is not None:
                conditions.append(AuditLog.success == success)

            if conditions:
                query = query.where(and_(*conditions))

            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            count_result = await self.db.execute(count_query)
            total = count_result.scalar() or 0

            # Get paginated results
            query = query.order_by(AuditLog.timestamp.desc())
            query = query.limit(limit).offset(offset)

            result = await self.db.execute(query)
            logs = result.scalars().all()

            # Convert to dict for response
            log_dicts = []
            for log in logs:
                log_dicts.append({
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "user_id": log.user_id,
                    "username": log.username,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "request_path": log.request_path,
                    "request_method": log.request_method,
                    "success": log.success,
                    "failure_reason": log.failure_reason,
                })

            return {
                "total": total,
                "items": log_dicts,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total,
            }

        except Exception as e:
            logger.error("Error querying audit logs: {}".format(e))
            raise

    async def get_audit_log_by_id(self, log_id: int) -> Optional[Dict[str, Any]]:
        """Get a single audit log by ID

        Args:
            log_id: Audit log ID

        Returns:
            Audit log dict or None if not found
        """
        try:
            result = await self.db.execute(
                select(AuditLog).where(AuditLog.id == log_id)
            )
            log = result.scalar_one_or_none()

            if not log:
                return None

            return {
                "id": log.id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "user_id": log.user_id,
                "username": log.username,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "request_path": log.request_path,
                "request_method": log.request_method,
                "request_body": log.request_body,  # Decrypted via property
                "response_body": log.response_body,  # Decrypted via property
                "changes": log.changes,  # Decrypted via property
                "success": log.success,
                "failure_reason": log.failure_reason,
                "additional_data": log.additional_data,
            }

        except Exception as e:
            logger.error("Error getting audit log {}: {}".format(log_id, e))
            raise


class AuditStatsService(object):
    """Service for generating audit log statistics"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Generate audit log statistics

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Statistics dict with totals, breakdowns, and trends
        """
        try:
            # Build base query with date filters
            base_query = select(AuditLog)
            conditions = []
            if start_date:
                conditions.append(AuditLog.timestamp >= start_date)
            if end_date:
                conditions.append(AuditLog.timestamp <= end_date)
            if conditions:
                base_query = base_query.where(and_(*conditions))

            # Total logs
            total_query = select(func.count()).select_from(base_query.subquery())
            total_result = await self.db.execute(total_query)
            total = total_result.scalar() or 0

            # By action
            action_query = select(
                AuditLog.action,
                func.count().label("count")
            ).select_from(base_query.subquery()).group_by(AuditLog.action)
            action_result = await self.db.execute(action_query)
            by_action = {row.action: row.count for row in action_result}

            # By resource type
            resource_query = select(
                AuditLog.resource_type,
                func.count().label("count")
            ).select_from(base_query.subquery()).group_by(AuditLog.resource_type)
            resource_result = await self.db.execute(resource_query)
            by_resource_type = {row.resource_type: row.count for row in resource_result}

            # By user (top 10)
            user_query = select(
                AuditLog.username,
                func.count().label("count")
            ).select_from(base_query.subquery()).group_by(
                AuditLog.username
            ).order_by(func.count().desc()).limit(10)
            user_result = await self.db.execute(user_query)
            by_user = {row.username: row.count for row in user_result if row.username}

            # Failed operations
            failed_query = select(func.count()).select_from(
                base_query.where(AuditLog.success == False).subquery()
            )
            failed_result = await self.db.execute(failed_query)
            failed_operations = failed_result.scalar() or 0

            # Recent activity (last 24 hours)
            recent_start = datetime.utcnow() - timedelta(hours=24)
            recent_query = select(func.count()).select_from(
                base_query.where(AuditLog.timestamp >= recent_start).subquery()
            )
            recent_result = await self.db.execute(recent_query)
            recent_activity = recent_result.scalar() or 0

            return {
                "total_logs": total,
                "by_action": by_action,
                "by_resource_type": by_resource_type,
                "by_user": by_user,
                "failed_operations": failed_operations,
                "recent_activity_24h": recent_activity,
                "date_range_start": start_date,
                "date_range_end": end_date,
            }

        except Exception as e:
            logger.error("Error generating audit statistics: {}".format(e))
            raise


class AuditExportService(object):
    """Service for exporting audit logs"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_to_csv(
        self,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> str:
        """Export audit logs to CSV format

        Args:
            user_id: Filter by user ID
            action: Filter by action
            resource_type: Filter by resource type
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            CSV string
        """
        try:
            # Build query
            query = select(AuditLog)
            conditions = []
            if user_id is not None:
                conditions.append(AuditLog.user_id == user_id)
            if action is not None:
                conditions.append(AuditLog.action == action)
            if resource_type is not None:
                conditions.append(AuditLog.resource_type == resource_type)
            if start_date is not None:
                conditions.append(AuditLog.timestamp >= start_date)
            if end_date is not None:
                conditions.append(AuditLog.timestamp <= end_date)

            if conditions:
                query = query.where(and_(*conditions))

            query = query.order_by(AuditLog.timestamp.desc())

            result = await self.db.execute(query)
            logs = result.scalars().all()

            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)

            # Header
            writer.writerow([
                "ID", "Timestamp", "User ID", "Username", "Action",
                "Resource Type", "Resource ID", "IP Address",
                "Request Path", "Request Method", "Success",
                "Failure Reason"
            ])

            # Data rows
            for log in logs:
                writer.writerow([
                    log.id,
                    log.timestamp.isoformat() if log.timestamp else "",
                    log.user_id or "",
                    log.username or "",
                    log.action,
                    log.resource_type,
                    log.resource_id or "",
                    log.ip_address or "",
                    log.request_path or "",
                    log.request_method or "",
                    "Yes" if log.success else "No",
                    log.failure_reason or "",
                ])

            return output.getvalue()

        except Exception as e:
            logger.error("Error exporting audit logs: {}".format(e))
            raise


class AuditAlertService(object):
    """Service for alerting on sensitive audit events"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_and_alert_sensitive_operation(
        self,
        audit_log: AuditLog,
    ) -> Optional[SystemAlert]:
        """Check if audit log represents sensitive operation and create alert

        Args:
            audit_log: The audit log entry to check

        Returns:
            Created SystemAlert if sensitive, None otherwise
        """
        try:
            # Check each sensitive operation rule
            for rule_name, rule_config in SENSITIVE_OPERATION_RULES.items():
                if await self._matches_rule(audit_log, rule_config):
                    # Create alert
                    alert = await self._create_alert(audit_log, rule_config)
                    if alert:
                        logger.warning(
                            "Sensitive operation detected: {} by {} - {}".format(
                                audit_log.action,
                                audit_log.username,
                                rule_name
                            )
                        )
                        return alert

            return None

        except Exception as e:
            logger.error("Error checking sensitive operation: {}".format(e))
            return None

    async def _matches_rule(
        self,
        audit_log: AuditLog,
        rule_config: Dict[str, Any],
    ) -> bool:
        """Check if audit log matches a sensitive operation rule

        Args:
            audit_log: The audit log to check
            rule_config: Rule configuration dict

        Returns:
            True if matches, False otherwise
        """
        # Check action
        if audit_log.action not in rule_config.get("actions", []):
            return False

        # Check resource
        resources = rule_config.get("resources", [])
        resource_match = any(
            r.lower() in audit_log.resource_type.lower()
            for r in resources
        )
        if not resource_match:
            return False

        # Check if failure-only rule
        if rule_config.get("failure_only") and audit_log.success:
            return False

        return True

    async def _create_alert(
        self,
        audit_log: AuditLog,
        rule_config: Dict[str, Any],
    ) -> Optional[SystemAlert]:
        """Create a system alert for sensitive operation

        Args:
            audit_log: The audit log entry
            rule_config: Rule configuration dict

        Returns:
            Created SystemAlert or None
        """
        try:
            # Format message
            message = rule_config.get("message_template", "Sensitive operation detected").format(
                username=audit_log.username or "anonymous",
                resource_type=audit_log.resource_type,
                resource_id=audit_log.resource_id or "unknown",
                action=audit_log.action,
                ip_address=audit_log.ip_address or "unknown",
            )

            # Create alert
            alert = SystemAlert(
                severity=rule_config.get("severity", AlertSeverity.MEDIUM),
                component="audit",
                alert_type="sensitive_operation",
                message=message,
                details={
                    "audit_log_id": audit_log.id,
                    "username": audit_log.username,
                    "action": audit_log.action,
                    "resource_type": audit_log.resource_type,
                    "resource_id": audit_log.resource_id,
                    "ip_address": audit_log.ip_address,
                    "timestamp": audit_log.timestamp.isoformat() if audit_log.timestamp else None,
                },
                status=AlertStatus.OPEN,
            )

            self.db.add(alert)
            await self.db.flush()

            return alert

        except Exception as e:
            logger.error("Error creating alert: {}".format(e))
            return None


class AuditRetentionService(object):
    """Service for managing audit log retention policies"""

    # Retention periods for different log types (in years)
    RETENTION_POLICIES = {
        "default": 6,  # 6 years default (UU 27/2022 requirement)
        "patient_data": 25,  # 25 years for inpatient records
        "financial": 10,  # 10 years for billing/financial
        "system": 3,  # 3 years for system operations
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def cleanup_old_logs(self, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up audit logs older than retention period

        Args:
            dry_run: If True, only report what would be deleted

        Returns:
            Dict with cleanup statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=365 * self.RETENTION_POLICIES["default"])

            # Count logs to be deleted
            count_query = select(func.count()).where(
                and_(
                    AuditLog.timestamp < cutoff_date,
                    AuditLog.success == True,  # Only delete successful operations
                )
            )
            count_result = await self.db.execute(count_query)
            to_delete = count_result.scalar() or 0

            deleted = 0
            if not dry_run and to_delete > 0:
                # Delete in batches
                batch_size = 1000
                while True:
                    delete_query = select(AuditLog).where(
                        and_(
                            AuditLog.timestamp < cutoff_date,
                            AuditLog.success == True,
                        )
                    ).limit(batch_size)

                    result = await self.db.execute(delete_query)
                    logs_to_delete = result.scalars().all()

                    if not logs_to_delete:
                        break

                    for log in logs_to_delete:
                        await self.db.delete(log)

                    deleted += len(logs_to_delete)

                    if len(logs_to_delete) < batch_size:
                        break

                    # Commit each batch
                    await self.db.commit()

            else:
                deleted = to_delete

            return {
                "cutoff_date": cutoff_date.isoformat(),
                "retention_years": self.RETENTION_POLICIES["default"],
                "logs_to_delete": to_delete,
                "logs_deleted": deleted,
                "dry_run": dry_run,
            }

        except Exception as e:
            logger.error("Error cleaning up old logs: {}".format(e))
            raise


# Factory functions
def get_query_service(db: AsyncSession) -> AuditQueryService:
    """Get audit query service"""
    return AuditQueryService(db)


def get_stats_service(db: AsyncSession) -> AuditStatsService:
    """Get audit statistics service"""
    return AuditStatsService(db)


def get_export_service(db: AsyncSession) -> AuditExportService:
    """Get audit export service"""
    return AuditExportService(db)


def get_alert_service(db: AsyncSession) -> AuditAlertService:
    """Get audit alert service"""
    return AuditAlertService(db)


def get_retention_service(db: AsyncSession) -> AuditRetentionService:
    """Get audit retention service"""
    return AuditRetentionService(db)
