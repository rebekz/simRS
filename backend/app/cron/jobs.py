"""
Scheduled jobs for audit log retention and archival.

Runs periodic cleanup and archival tasks for compliance with UU 27/2022.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.db.session import get_db_context
from app.core.config import settings


class AuditLogRetentionJob:
    """
    Scheduled job for audit log retention and archival.

    Performs two tasks:
    1. Archives logs older than 1 year to archive table
    2. Deletes logs older than 6 years (compliance retention period)

    Schedule: Run daily at 2 AM
    """

    def __init__(self):
        self.archive_after_years = 1
        self.delete_after_years = 6
        self.batch_size = 1000

    async def run(self) -> dict:
        """
        Run the retention job.

        Returns:
            Dictionary with job results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "archived_count": 0,
            "deleted_count": 0,
            "errors": [],
        }

        try:
            async with get_db_context() as db:
                # Archive old logs
                archived = await self._archive_old_logs(db)
                results["archived_count"] = archived

                # Delete very old logs
                deleted = await self._delete_expired_logs(db)
                results["deleted_count"] = deleted

        except Exception as e:
            results["errors"].append(str(e))

        return results

    async def _archive_old_logs(self, db: AsyncSession) -> int:
        """
        Archive audit logs older than 1 year.

        Args:
            db: Database session

        Returns:
            Number of logs archived
        """
        cutoff_date = datetime.utcnow() - timedelta(days=365 * self.archive_after_years)

        # Copy to archive table
        query = text("""
            INSERT INTO audit_logs_archive
            (id, timestamp, user_id, username, action, resource_type, resource_id,
             ip_address, user_agent, request_path, request_method, success,
             failure_reason, additional_data)
            SELECT id, timestamp, user_id, username, action, resource_type, resource_id,
                   ip_address, user_agent, request_path, request_method, success,
                   failure_reason, additional_data
            FROM audit_logs
            WHERE timestamp < :cutoff_date
            ON CONFLICT (id) DO NOTHING
        """)

        result = await db.execute(query, {"cutoff_date": cutoff_date})
        archived_count = result.rowcount

        # Delete from main table after successful archive
        delete_query = text("""
            DELETE FROM audit_logs
            WHERE timestamp < :cutoff_date
            AND id IN (SELECT id FROM audit_logs_archive)
        """)

        await db.execute(delete_query, {"cutoff_date": cutoff_date})
        await db.commit()

        return archived_count

    async def _delete_expired_logs(self, db: AsyncSession) -> int:
        """
        Delete audit logs older than 6 years (after archive retention).

        Args:
            db: Database session

        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=365 * self.delete_after_years)

        # Delete from archive table
        query = text("""
            DELETE FROM audit_logs_archive
            WHERE timestamp < :cutoff_date
            RETURNING id
        """)

        result = await db.execute(query, {"cutoff_date": cutoff_date})
        deleted_count = len(result.all()) if result else 0

        await db.commit()

        return deleted_count


class AuditLogStatisticsJob:
    """
    Scheduled job to collect and store audit log statistics.

    Generates daily/weekly/monthly summaries for monitoring.
    """

    async def run(self) -> dict:
        """
        Run statistics collection job.

        Returns:
            Dictionary with statistics
        """
        stats = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_logs": 0,
            "failed_operations": 0,
            "unique_users": 0,
            "top_actions": {},
            "top_resources": {},
        }

        try:
            async with get_db_context() as db:
                # Count total logs in last 24 hours
                since = datetime.utcnow() - timedelta(days=1)

                total_query = text("""
                    SELECT COUNT(*) FROM audit_logs
                    WHERE timestamp >= :since
                """)
                result = await db.execute(total_query, {"since": since})
                stats["total_logs"] = result.scalar() or 0

                # Count failed operations
                failed_query = text("""
                    SELECT COUNT(*) FROM audit_logs
                    WHERE timestamp >= :since
                    AND success = false
                """)
                result = await db.execute(failed_query, {"since": since})
                stats["failed_operations"] = result.scalar() or 0

                # Count unique users
                users_query = text("""
                    SELECT COUNT(DISTINCT user_id) FROM audit_logs
                    WHERE timestamp >= :since
                    AND user_id IS NOT NULL
                """)
                result = await db.execute(users_query, {"since": since})
                stats["unique_users"] = result.scalar() or 0

                # Top actions
                actions_query = text("""
                    SELECT action, COUNT(*) as count
                    FROM audit_logs
                    WHERE timestamp >= :since
                    GROUP BY action
                    ORDER BY count DESC
                    LIMIT 10
                """)
                result = await db.execute(actions_query, {"since": since})
                stats["top_actions"] = {row.action: row.count for row in result}

                # Top resources
                resources_query = text("""
                    SELECT resource_type, COUNT(*) as count
                    FROM audit_logs
                    WHERE timestamp >= :since
                    GROUP BY resource_type
                    ORDER BY count DESC
                    LIMIT 10
                """)
                result = await db.execute(resources_query, {"since": since})
                stats["top_resources"] = {row.resource_type: row.count for row in result}

        except Exception as e:
            stats["error"] = str(e)

        return stats


# Job registry
SCHEDULED_JOBS = {
    "audit_retention": AuditLogRetentionJob,
    "audit_statistics": AuditLogStatisticsJob,
}


async def run_job(job_name: str) -> dict:
    """
    Run a specific scheduled job.

    Args:
        job_name: Name of the job to run

    Returns:
        Job results dictionary
    """
    if job_name not in SCHEDULED_JOBS:
        return {"error": f"Unknown job: {job_name}"}

    job_class = SCHEDULED_JOBS[job_name]
    job = job_class()
    return await job.run()


async def run_all_jobs() -> dict:
    """
    Run all scheduled jobs.

    Returns:
        Dictionary with results from all jobs
    """
    results = {}
    for job_name in SCHEDULED_JOBS:
        results[job_name] = await run_job(job_name)
    return results


if __name__ == "__main__":
    # Run jobs when script is executed directly
    import sys

    if len(sys.argv) > 1:
        job_name = sys.argv[1]
        result = asyncio.run(run_job(job_name))
        print(f"Job '{job_name}' completed:")
        print(result)
    else:
        results = asyncio.run(run_all_jobs())
        print("All jobs completed:")
        for job_name, result in results.items():
            print(f"\n{job_name}:")
            print(result)
