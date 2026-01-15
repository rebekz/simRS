"""System Alert Service

Service layer for system alert management.
Supports alert creation, acknowledgment, resolution, and alert rule management.
STORY-022-06: System Alerts and Monitoring
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.models.system_alerts import (
    SystemAlert,
    AlertRule,
    AlertSeverity,
    AlertStatus,
)


class SystemAlertService:
    """Service for managing system alerts and alert rules"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_alert(
        self,
        severity: str,
        component: str,
        alert_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new system alert

        Args:
            severity: Alert severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
            component: System component that generated the alert
            alert_type: Type of alert (e.g., database_down, api_timeout)
            message: Alert message describing the issue
            details: Optional additional details in JSON format

        Returns:
            Dict with alert_id and status

        Raises:
            ValueError: If validation fails
        """
        try:
            # Validate severity
            valid_severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
            if severity not in valid_severities:
                raise ValueError(
                    "Invalid severity '{severity}'. Must be one of: {severities}".format(
                        severity=severity,
                        severities=", ".join(valid_severities)
                    )
                )

            # Create alert
            alert = SystemAlert(
                severity=severity,
                component=component,
                alert_type=alert_type,
                message=message,
                details=details,
                status=AlertStatus.OPEN.value
            )

            self.db.add(alert)
            await self.db.flush()  # Get the alert ID

            # Send notification for critical/high alerts
            if severity in ["CRITICAL", "HIGH"]:
                await self._send_alert_notification(alert)

            await self.db.commit()

            return {
                "alert_id": alert.id,
                "severity": alert.severity,
                "component": alert.component,
                "alert_type": alert.alert_type,
                "status": alert.status,
                "message": "System alert created successfully",
                "created_at": alert.created_at
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise ValueError("Failed to create alert: {error}".format(error=str(e)))

    async def acknowledge_alert(
        self,
        alert_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Acknowledge an alert

        Args:
            alert_id: The alert ID
            user_id: The user ID acknowledging the alert

        Returns:
            Dict with updated alert status

        Raises:
            ValueError: If alert not found or already acknowledged
        """
        try:
            result = await self.db.execute(
                select(SystemAlert).where(SystemAlert.id == alert_id)
            )
            alert = result.scalar_one_or_none()

            if not alert:
                raise ValueError("Alert {alert_id} not found".format(alert_id=alert_id))

            if alert.status != AlertStatus.OPEN.value:
                raise ValueError(
                    "Alert {alert_id} cannot be acknowledged. Current status: {status}".format(
                        alert_id=alert_id,
                        status=alert.status
                    )
                )

            # Update alert
            alert.status = AlertStatus.ACKNOWLEDGED.value
            alert.acknowledged_by = user_id
            alert.acknowledged_at = datetime.utcnow()
            alert.updated_at = datetime.utcnow()

            await self.db.commit()

            return {
                "alert_id": alert.id,
                "status": alert.status,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at,
                "message": "Alert acknowledged successfully"
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise ValueError("Failed to acknowledge alert: {error}".format(error=str(e)))

    async def resolve_alert(
        self,
        alert_id: int
    ) -> Dict[str, Any]:
        """Mark an alert as resolved

        Args:
            alert_id: The alert ID

        Returns:
            Dict with updated alert status

        Raises:
            ValueError: If alert not found
        """
        try:
            result = await self.db.execute(
                select(SystemAlert).where(SystemAlert.id == alert_id)
            )
            alert = result.scalar_one_or_none()

            if not alert:
                raise ValueError("Alert {alert_id} not found".format(alert_id=alert_id))

            # Update alert
            alert.status = AlertStatus.RESOLVED.value
            alert.resolved_at = datetime.utcnow()
            alert.updated_at = datetime.utcnow()

            await self.db.commit()

            return {
                "alert_id": alert.id,
                "status": alert.status,
                "resolved_at": alert.resolved_at,
                "message": "Alert resolved successfully"
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise ValueError("Failed to resolve alert: {error}".format(error=str(e)))

    async def get_alert(
        self,
        alert_id: int
    ) -> Dict[str, Any]:
        """Get alert by ID

        Args:
            alert_id: The alert ID

        Returns:
            Dict with alert details

        Raises:
            ValueError: If alert not found
        """
        try:
            result = await self.db.execute(
                select(SystemAlert).where(SystemAlert.id == alert_id)
            )
            alert = result.scalar_one_or_none()

            if not alert:
                raise ValueError("Alert {alert_id} not found".format(alert_id=alert_id))

            return {
                "alert_id": alert.id,
                "severity": alert.severity,
                "component": alert.component,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "details": alert.details,
                "status": alert.status,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at,
                "resolved_at": alert.resolved_at,
                "created_at": alert.created_at,
                "updated_at": alert.updated_at
            }

        except ValueError:
            raise
        except Exception as e:
            raise ValueError("Failed to get alert: {error}".format(error=str(e)))

    async def list_alerts(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        component: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """List alerts with pagination and filtering

        Args:
            severity: Optional severity filter
            status: Optional status filter
            component: Optional component filter
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Dict with alerts list and pagination info
        """
        try:
            # Build query filters
            filters = []

            if severity:
                filters.append(SystemAlert.severity == severity)
            if status:
                filters.append(SystemAlert.status == status)
            if component:
                filters.append(SystemAlert.component == component)

            # Get total count
            count_query = select(func.count(SystemAlert.id))
            if filters:
                count_query = count_query.where(and_(*filters))
            count_result = await self.db.execute(count_query)
            total_count = count_result.scalar() or 0

            # Get alerts with pagination
            offset = (page - 1) * per_page
            query = select(SystemAlert)
            if filters:
                query = query.where(and_(*filters))
            query = query.order_by(SystemAlert.created_at.desc()).limit(per_page).offset(offset)

            result = await self.db.execute(query)
            alerts = result.scalars().all()

            # Build response
            alert_list = [
                {
                    "alert_id": alert.id,
                    "severity": alert.severity,
                    "component": alert.component,
                    "alert_type": alert.alert_type,
                    "message": alert.message,
                    "details": alert.details,
                    "status": alert.status,
                    "acknowledged_by": alert.acknowledged_by,
                    "acknowledged_at": alert.acknowledged_at,
                    "resolved_at": alert.resolved_at,
                    "created_at": alert.created_at,
                    "updated_at": alert.updated_at
                }
                for alert in alerts
            ]

            return {
                "alerts": alert_list,
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page if per_page > 0 else 0
            }

        except Exception as e:
            raise ValueError("Failed to list alerts: {error}".format(error=str(e)))

    async def create_rule(
        self,
        name: str,
        component: str,
        alert_type: str,
        severity: str,
        condition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new alert rule

        Args:
            name: Unique name for the alert rule
            component: System component this rule applies to
            alert_type: Type of alert to be generated
            severity: Severity level for alerts
            condition: Rule conditions in JSON format

        Returns:
            Dict with rule_id and status

        Raises:
            ValueError: If validation fails or rule name already exists
        """
        try:
            # Validate severity
            valid_severities = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
            if severity not in valid_severities:
                raise ValueError(
                    "Invalid severity '{severity}'. Must be one of: {severities}".format(
                        severity=severity,
                        severities=", ".join(valid_severities)
                    )
                )

            # Check if rule name already exists
            existing = await self.db.execute(
                select(AlertRule).where(AlertRule.name == name)
            )
            if existing.scalar_one_or_none():
                raise ValueError("Alert rule with name '{name}' already exists".format(name=name))

            # Create rule
            rule = AlertRule(
                name=name,
                component=component,
                alert_type=alert_type,
                severity=severity,
                condition=condition,
                enabled=True
            )

            self.db.add(rule)
            await self.db.flush()  # Get the rule ID

            await self.db.commit()

            return {
                "rule_id": rule.id,
                "name": rule.name,
                "component": rule.component,
                "alert_type": rule.alert_type,
                "severity": rule.severity,
                "enabled": rule.enabled,
                "message": "Alert rule created successfully",
                "created_at": rule.created_at
            }

        except ValueError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise ValueError("Failed to create alert rule: {error}".format(error=str(e)))

    async def list_rules(
        self,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """List alert rules

        Args:
            enabled_only: If True, only return enabled rules

        Returns:
            List of alert rule dicts
        """
        try:
            # Build query
            query = select(AlertRule)

            if enabled_only:
                query = query.where(AlertRule.enabled == True)

            query = query.order_by(AlertRule.name.asc())

            result = await self.db.execute(query)
            rules = result.scalars().all()

            # Build response
            rule_list = [
                {
                    "rule_id": rule.id,
                    "name": rule.name,
                    "component": rule.component,
                    "alert_type": rule.alert_type,
                    "severity": rule.severity,
                    "condition": rule.condition,
                    "enabled": rule.enabled,
                    "created_at": rule.created_at,
                    "updated_at": rule.updated_at
                }
                for rule in rules
            ]

            return rule_list

        except Exception as e:
            raise ValueError("Failed to list alert rules: {error}".format(error=str(e)))

    async def _send_alert_notification(
        self,
        alert: SystemAlert
    ) -> None:
        """Send notification for critical/high alerts

        Integrates with NotificationService to send notifications
        for critical and high severity alerts.

        Args:
            alert: The SystemAlert object
        """
        try:
            # Import here to avoid circular dependency
            from app.services.notification_service import NotificationService
            from app.schemas.notifications import (
                SendNotificationRequest,
                NotificationChannel,
                NotificationType,
                NotificationPriority
            )

            # Create notification service instance
            notification_service = NotificationService(self.db)

            # Prepare notification message
            subject = "{severity} Alert: {component} - {alert_type}".format(
                severity=alert.severity,
                component=alert.component,
                alert_type=alert.alert_type
            )

            message = "System Alert:\n\nSeverity: {severity}\nComponent: {component}\nType: {type}\n\n{msg}".format(
                severity=alert.severity,
                component=alert.component,
                type=alert.alert_type,
                msg=alert.message
            )

            # Create notification request
            # Note: In production, you would determine the appropriate recipient_id
            # based on the component and alert type (e.g., system administrators, on-call staff)
            # For now, this is a placeholder that demonstrates the integration
            notification_request = SendNotificationRequest(
                recipient_id=1,  # Placeholder - would be determined dynamically
                recipient_type="staff",
                channel=NotificationChannel.IN_APP,
                type=NotificationType.SYSTEM_ALERT,
                priority=NotificationPriority.HIGH if alert.severity == "HIGH" else NotificationPriority.URGENT,
                subject=subject,
                message=message,
                data={
                    "alert_id": alert.id,
                    "severity": alert.severity,
                    "component": alert.component,
                    "alert_type": alert.alert_type,
                    "details": alert.details
                }
            )

            # Send notification (fire and forget - errors shouldn't fail the alert creation)
            try:
                await notification_service.send_notification(notification_request)
            except Exception:
                # Log error but don't fail the alert creation
                # In production, you would log this to a proper logging system
                pass

        except Exception:
            # Silently fail - notification failure shouldn't prevent alert creation
            # In production, you would log this to a proper logging system
            pass
