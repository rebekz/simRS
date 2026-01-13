"""
Backup monitoring and alerting module for SIMRS.

Monitors backup status, sends alerts on failures, and provides
backup statistics and health status.
"""

import os
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)


class BackupAlert:
    """Represents a backup alert notification."""

    def __init__(
        self,
        alert_type: str,
        severity: str,
        message: str,
        metadata: Optional[Dict] = None
    ):
        self.alert_type = alert_type  # "backup_failed", "backup_missing", "disk_full"
        self.severity = severity  # "critical", "warning", "info"
        self.message = message
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        return {
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class BackupMonitor:
    """
    Monitors backup status and sends alerts.

    Checks for:
    - Failed backups
    - Missing backups (gaps in schedule)
    - Disk space issues
    - Old backups (retention policy)
    """

    def __init__(
        self,
        backup_dir: str = "/backup",
        alert_email: Optional[str] = None,
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None
    ):
        self.backup_dir = Path(backup_dir)
        self.alert_email = alert_email or os.getenv("BACKUP_ALERT_EMAIL")
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")

        # Backup schedules
        self.daily_interval = timedelta(hours=26)  # Allow 2h grace period
        self.weekly_interval = timedelta(days=8)
        self.monthly_interval = timedelta(days=32)

        # Disk space thresholds
        self.disk_warning_threshold = 80  # Percentage
        self.disk_critical_threshold = 90  # Percentage

    def check_backup_status(self) -> List[BackupAlert]:
        """
        Check backup status and return list of alerts.

        Returns:
            List of BackupAlert objects
        """
        alerts = []

        # Check daily backups
        alerts.extend(self._check_daily_backups())

        # Check weekly backups
        alerts.extend(self._check_weekly_backups())

        # Check monthly backups
        alerts.extend(self._check_monthly_backups())

        # Check disk space
        alerts.extend(self._check_disk_space())

        # Check WAL archives
        alerts.extend(self._check_wal_archives())

        return alerts

    def _check_daily_backups(self) -> List[BackupAlert]:
        """Check if daily backups are current."""
        alerts = []
        daily_dir = self.backup_dir / "daily"

        if not daily_dir.exists():
            return [
                BackupAlert(
                    "backup_missing",
                    "critical",
                    "Daily backup directory not found",
                    {"directory": str(daily_dir)}
                )
            ]

        # Get most recent backup
        backups = sorted(daily_dir.glob("simrs_*.sql.gz.enc"), reverse=True)

        if not backups:
            return [
                BackupAlert(
                    "backup_missing",
                    "critical",
                    "No daily backups found",
                    {"directory": str(daily_dir)}
                )
            ]

        # Check age of most recent backup
        latest_backup = backups[0]
        backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
        age = datetime.now() - backup_time

        if age > self.daily_interval:
            alerts.append(
                BackupAlert(
                    "backup_missing",
                    "critical",
                    f"Latest daily backup is {age} old (expected < {self.daily_interval})",
                    {
                        "latest_backup": str(latest_backup.name),
                        "age_hours": age.total_seconds() / 3600
                    }
                )
            )

        return alerts

    def _check_weekly_backups(self) -> List[BackupAlert]:
        """Check if weekly backups are current."""
        alerts = []
        weekly_dir = self.backup_dir / "weekly"

        if not weekly_dir.exists():
            return []  # Weekly backups are optional

        backups = sorted(weekly_dir.glob("simrs_*.sql.gz.enc"), reverse=True)

        if not backups:
            return []  # Weekly backups might not exist yet

        # Check age of most recent backup
        latest_backup = backups[0]
        backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
        age = datetime.now() - backup_time

        if age > self.weekly_interval:
            alerts.append(
                BackupAlert(
                    "backup_missing",
                    "warning",
                    f"Latest weekly backup is {age} old (expected < {self.weekly_interval})",
                    {
                        "latest_backup": str(latest_backup.name),
                        "age_days": age.days
                    }
                )
            )

        return alerts

    def _check_monthly_backups(self) -> List[BackupAlert]:
        """Check if monthly backups are current."""
        alerts = []
        monthly_dir = self.backup_dir / "monthly"

        if not monthly_dir.exists():
            return []  # Monthly backups are optional

        backups = sorted(monthly_dir.glob("simrs_*.sql.gz.enc"), reverse=True)

        if not backups:
            return []  # Monthly backups might not exist yet

        # Check age of most recent backup
        latest_backup = backups[0]
        backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
        age = datetime.now() - backup_time

        if age > self.monthly_interval:
            alerts.append(
                BackupAlert(
                    "backup_missing",
                    "warning",
                    f"Latest monthly backup is {age} old (expected < {self.monthly_interval})",
                    {
                        "latest_backup": str(latest_backup.name),
                        "age_days": age.days
                    }
                )
            )

        return alerts

    def _check_disk_space(self) -> List[BackupAlert]:
        """Check disk space on backup volume."""
        alerts = []

        try:
            stat = os.statvfs(self.backup_dir)
            total = stat.f_frsize * stat.f_blocks
            used = stat.f_frsize * (stat.f_blocks - stat.f_bavail)
            usage_percent = (used / total) * 100

            if usage_percent >= self.disk_critical_threshold:
                alerts.append(
                    BackupAlert(
                        "disk_full",
                        "critical",
                        f"Backup disk is {usage_percent:.1f}% full (critical threshold: {self.disk_critical_threshold}%)",
                        {
                            "usage_percent": usage_percent,
                            "total_gb": total / (1024**3),
                            "used_gb": used / (1024**3),
                            "free_gb": (total - used) / (1024**3)
                        }
                    )
                )
            elif usage_percent >= self.disk_warning_threshold:
                alerts.append(
                    BackupAlert(
                        "disk_full",
                        "warning",
                        f"Backup disk is {usage_percent:.1f}% full (warning threshold: {self.disk_warning_threshold}%)",
                        {
                            "usage_percent": usage_percent,
                            "total_gb": total / (1024**3),
                            "used_gb": used / (1024**3),
                            "free_gb": (total - used) / (1024**3)
                        }
                    )
                )

        except Exception as e:
            logger.error(f"Failed to check disk space: {e}")
            alerts.append(
                BackupAlert(
                    "monitoring_error",
                    "warning",
                    f"Failed to check disk space: {e}",
                    {"error": str(e)}
                )
            )

        return alerts

    def _check_wal_archives(self) -> List[BackupAlert]:
        """Check if WAL archiving is active."""
        alerts = []
        wal_dir = self.backup_dir / "wal"

        if not wal_dir.exists():
            return []  # WAL archiving might not be configured yet

        # Get most recent WAL file
        wal_files = sorted(wal_dir.glob("*.gz"), reverse=True)

        if not wal_files:
            # Check if WAL archiving is configured
            alerts.append(
                BackupAlert(
                    "wal_missing",
                    "warning",
                    "No WAL archives found. WAL archiving may not be configured.",
                    {"directory": str(wal_dir)}
                )
            )
            return alerts

        # Check age of most recent WAL file
        latest_wal = wal_files[0]
        wal_time = datetime.fromtimestamp(latest_wal.stat().st_mtime)
        age = datetime.now() - wal_time

        # WAL files should be archived continuously (every 5-15 minutes)
        if age > timedelta(minutes=30):
            alerts.append(
                BackupAlert(
                    "wal_missing",
                    "warning",
                    f"Latest WAL archive is {age} old (WAL archiving may be stalled)",
                    {
                        "latest_wal": str(latest_wal.name),
                        "age_minutes": age.total_seconds() / 60
                    }
                )
            )

        return alerts

    def send_email_alert(self, alert: BackupAlert) -> bool:
        """
        Send email alert.

        Args:
            alert: BackupAlert to send

        Returns:
            True if email was sent successfully
        """
        if not self.alert_email:
            logger.warning("No alert email configured")
            return False

        if not self.smtp_server:
            logger.warning("SMTP server not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"[SIMRS Backup Alert] {alert.alert_type} - {alert.severity.upper()}"
            msg["From"] = self.smtp_user
            msg["To"] = self.alert_email

            # Create email body
            text_body = f"""
SIMRS Backup Alert

Type: {alert.alert_type}
Severity: {alert.severity.upper()}
Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Message:
{alert.message}

Metadata:
{json.dumps(alert.metadata, indent=2)}
"""

            html_body = f"""
<html>
  <body>
    <h2>SIMRS Backup Alert</h2>
    <p><strong>Type:</strong> {alert.alert_type}</p>
    <p><strong>Severity:</strong> {alert.severity.upper()}</p>
    <p><strong>Time:</strong> {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h3>Message</h3>
    <p>{alert.message}</p>

    <h3>Metadata</h3>
    <pre>{json.dumps(alert.metadata, indent=2)}</pre>
  </body>
</html>
"""

            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Alert email sent to {self.alert_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False

    def send_alerts(self, alerts: List[BackupAlert]) -> int:
        """
        Send all alerts via email.

        Args:
            alerts: List of BackupAlert objects

        Returns:
            Number of alerts sent successfully
        """
        sent = 0

        for alert in alerts:
            if alert.severity in ["critical", "warning"]:
                if self.send_email_alert(alert):
                    sent += 1

        return sent

    def get_backup_stats(self) -> Dict:
        """
        Get backup statistics.

        Returns:
            Dictionary with backup statistics
        """
        stats = {
            "daily_backups": 0,
            "weekly_backups": 0,
            "monthly_backups": 0,
            "wal_files": 0,
            "total_size_gb": 0,
            "latest_backup": None,
            "oldest_backup": None
        }

        # Count backups
        for backup in self.backup_dir.rglob("simrs_*.sql.gz.enc"):
            stats["total_size_gb"] += backup.stat().st_size / (1024**3)

            if "daily" in str(backup):
                stats["daily_backups"] += 1
            elif "weekly" in str(backup):
                stats["weekly_backups"] += 1
            elif "monthly" in str(backup):
                stats["monthly_backups"] += 1

        # Count WAL files
        wal_dir = self.backup_dir / "wal"
        if wal_dir.exists():
            stats["wal_files"] = len(list(wal_dir.glob("*.gz")))

        # Get latest and oldest backups
        all_backups = list(self.backup_dir.rglob("simrs_*.sql.gz.enc"))
        if all_backups:
            all_backups.sort(key=lambda b: b.stat().st_mtime)
            stats["oldest_backup"] = all_backups[0].name
            stats["latest_backup"] = all_backups[-1].name

        return stats


def main():
    """CLI for backup monitoring."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor SIMRS backups and send alerts"
    )
    parser.add_argument(
        "--backup-dir",
        default="/backup",
        help="Backup directory path"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check backup status and display alerts"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display backup statistics"
    )
    parser.add_argument(
        "--alert",
        action="store_true",
        help="Send email alerts for any issues"
    )

    args = parser.parse_args()

    monitor = BackupMonitor(backup_dir=args.backup_dir)

    if args.stats:
        stats = monitor.get_backup_stats()
        print(json.dumps(stats, indent=2))

    if args.check:
        alerts = monitor.check_backup_status()
        if alerts:
            print(f"Found {len(alerts)} alerts:")
            for alert in alerts:
                print(f"  [{alert.severity.upper()}] {alert.alert_type}: {alert.message}")
        else:
            print("No alerts - all backups look good!")

    if args.alert:
        alerts = monitor.check_backup_status()
        sent = monitor.send_alerts(alerts)
        print(f"Sent {sent} alert(s)")


if __name__ == "__main__":
    main()
