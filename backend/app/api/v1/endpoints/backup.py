"""Backup Management API Endpoints for STORY-004: Automated Backup System

This module provides API endpoints for:
- Triggering and scheduling backups
- Monitoring backup jobs
- Restoring from backups
- Backup verification
- Backup retention management

Python 3.5+ compatible
"""

import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.db.session import get_db
from app.models.user import User
from app.models.backup import (
    BackupJob, BackupRestore, BackupVerification,
    BackupStatus, BackupType,
)
from app.services.backup import (
    get_backup_service,
    get_restore_service,
    get_verification_service,
    get_retention_service,
)
from app.core.deps import get_current_user, get_current_admin_user


logger = logging.getLogger(__name__)


router = APIRouter()


# =============================================================================
# Pydantic Models
# =============================================================================

class BackupCreateRequest(BaseModel):
    """Request to create a new backup job"""
    job_name: str = Field(..., description="Human-readable job name")
    backup_type: str = Field("full", description="Backup type (full, differential, incremental)")
    source_type: str = Field(..., description="Source type (database, files, uploads)")
    source_path: Optional[str] = Field(None, description="Source path for file backups")
    storage_type: str = Field("local", description="Storage type (local, s3, gcs, azure)")
    storage_path: Optional[str] = Field(None, description="Storage destination path")
    encryption_enabled: bool = Field(True, description="Whether to encrypt backup")
    retention_days: int = Field(30, description="Days to retain backup")


class RestoreCreateRequest(BaseModel):
    """Request to create a restore job"""
    backup_job_id: int = Field(..., description="Source backup job ID")
    backup_path: str = Field(..., description="Path to backup file")
    target_type: str = Field(..., description="Target type (database, files)")
    target_path: Optional[str] = Field(None, description="Target path for files")
    restore_options: Optional[dict] = Field(None, description="Additional restore options")
    dry_run: bool = Field(True, description="Dry run without actual restoration")
    approval_notes: Optional[str] = Field(None, description="Approval notes")


class BackupJobResponse(BaseModel):
    """Response model for backup job"""
    id: int
    job_id: str
    job_name: str
    backup_type: str
    source_type: str
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    backup_path: Optional[str]
    backup_size_bytes: Optional[int]
    checksum: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True


class BackupListResponse(BaseModel):
    """Response model for backup list"""
    total: int
    items: List[BackupJobResponse]
    limit: int
    offset: int
    has_more: bool


# =============================================================================
# Backup Job Endpoints
# =============================================================================

@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_backup_job(
    request: BackupCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new backup job (admin only)"""
    try:
        service = get_backup_service(db)

        backup_job = await service.create_backup_job(
            job_name=request.job_name,
            backup_type=request.backup_type,
            source_type=request.source_type,
            storage_type=request.storage_type,
            storage_path=request.storage_path,
            source_path=request.source_path,
            encryption_enabled=request.encryption_enabled,
            retention_days=request.retention_days,
            created_by=current_user.id,
        )

        await db.commit()

        return {
            "id": backup_job.id,
            "job_id": backup_job.job_id,
            "message": "Backup job created successfully",
            "status": backup_job.status,
        }

    except Exception as e:
        await db.rollback()
        logger.error("Error creating backup job: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create backup job"
        )


@router.post("/jobs/{job_id}/execute")
async def execute_backup_job(
    job_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a backup job (admin only)"""
    try:
        # Get backup job
        result = await db.execute(
            select(BackupJob).where(BackupJob.id == job_id)
        )
        backup_job = result.scalar_one_or_none()

        if not backup_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Backup job not found"
            )

        # Update triggerer
        backup_job.last_triggered_by = current_user.id

        # Execute backup
        service = get_backup_service(db)
        updated_job = await service.execute_backup(backup_job)

        await db.commit()

        return {
            "id": updated_job.id,
            "job_id": updated_job.job_id,
            "status": updated_job.status,
            "backup_path": updated_job.backup_path,
            "backup_size_bytes": updated_job.backup_size_bytes,
            "duration_seconds": updated_job.duration_seconds,
        }

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error("Error executing backup: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute backup"
        )


@router.get("/jobs", response_model=BackupListResponse)
async def list_backup_jobs(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    limit: int = Query(50, ge=1, le=100, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List backup jobs with filters"""
    try:
        # Build query
        query = select(BackupJob)

        conditions = []
        if status_filter:
            conditions.append(BackupJob.status == status_filter)
        if source_type:
            conditions.append(BackupJob.source_type == source_type)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(BackupJob.id)
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await db.execute(select(func.count()).select_from(count_query))
        total = count_result.scalar() or 0

        # Get paginated results
        query = query.order_by(desc(BackupJob.created_at))
        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        jobs = result.scalars().all()

        return BackupListResponse(
            total=total,
            items=[BackupJobResponse.model_validate(job) for job in jobs],
            limit=limit,
            offset=offset,
            has_more=offset + limit < total,
        )

    except Exception as e:
        logger.error("Error listing backup jobs: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list backup jobs"
        )


@router.get("/jobs/{job_id}", response_model=BackupJobResponse)
async def get_backup_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get backup job details"""
    try:
        result = await db.execute(
            select(BackupJob).where(BackupJob.id == job_id)
        )
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Backup job not found"
            )

        return BackupJobResponse.model_validate(job)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting backup job: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get backup job"
        )


# =============================================================================
# Restore Endpoints
# =============================================================================

@router.post("/restore", status_code=status.HTTP_201_CREATED)
async def create_restore_job(
    request: RestoreCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a restore job (admin only)"""
    try:
        service = get_restore_service(db)

        restore_job = await service.create_restore_job(
            backup_job_id=request.backup_job_id,
            backup_path=request.backup_path,
            target_type=request.target_type,
            target_path=request.target_path,
            restore_options=request.restore_options,
            dry_run=request.dry_run,
            requested_by=current_user.id,
        )

        await db.commit()

        return {
            "id": restore_job.id,
            "restore_id": restore_job.restore_id,
            "message": "Restore job created successfully",
            "status": restore_job.status,
            "requires_approval": restore_job.requires_approval,
        }

    except Exception as e:
        await db.rollback()
        logger.error("Error creating restore job: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create restore job"
        )


@router.post("/restore/{restore_id}/approve")
async def approve_restore_job(
    restore_id: int,
    approval_notes: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve a restore job (admin only)"""
    try:
        result = await db.execute(
            select(BackupRestore).where(BackupRestore.id == restore_id)
        )
        restore_job = result.scalar_one_or_none()

        if not restore_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restore job not found"
            )

        # Update approval
        restore_job.approved_by = current_user.id
        restore_job.approved_at = datetime.utcnow()
        restore_job.approval_notes = approval_notes

        await db.commit()

        return {
            "id": restore_job.id,
            "restore_id": restore_job.restore_id,
            "message": "Restore job approved successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("Error approving restore job: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve restore job"
        )


@router.post("/restore/{restore_id}/execute")
async def execute_restore_job(
    restore_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute a restore job (admin only)"""
    try:
        result = await db.execute(
            select(BackupRestore).where(BackupRestore.id == restore_id)
        )
        restore_job = result.scalar_one_or_none()

        if not restore_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restore job not found"
            )

        # Execute restore
        service = get_restore_service(db)
        updated_job = await service.execute_restore(restore_job)

        await db.commit()

        return {
            "id": updated_job.id,
            "restore_id": updated_job.restore_id,
            "status": updated_job.status,
            "files_restored": updated_job.files_restored,
            "validation_passed": updated_job.validation_passed,
        }

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error("Error executing restore: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute restore"
        )


# =============================================================================
# Verification Endpoints
# =============================================================================

@router.post("/verify/{job_id}", status_code=status.HTTP_201_CREATED)
async def verify_backup(
    job_id: int,
    verification_type: str = Query("checksum", description="Verification type"),
    test_restoration: bool = Query(False, description="Test restoration"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify backup integrity"""
    try:
        service = get_verification_service(db)

        verification = await service.verify_backup(
            backup_job_id=job_id,
            verification_type=verification_type,
            test_restoration=test_restoration,
            verified_by=current_user.id,
        )

        await db.commit()

        return {
            "id": verification.id,
            "verification_id": verification.verification_id,
            "status": verification.status,
            "checksum_match": verification.checksum_match,
            "issues_found": verification.issues_found,
            "corruption_detected": verification.corruption_detected,
        }

    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error("Error verifying backup: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify backup"
        )


# =============================================================================
# Retention Endpoints
# =============================================================================

@router.post("/cleanup")
async def cleanup_old_backups(
    dry_run: bool = Query(True, description="If true, only report what would be deleted"),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Clean up old backups (admin only)"""
    try:
        service = get_retention_service(db)

        result = await service.cleanup_old_backups(dry_run=dry_run)

        # Commit if not dry run
        if not dry_run:
            await db.commit()

        return result

    except Exception as e:
        await db.rollback()
        logger.error("Error cleaning up backups: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup backups"
        )


@router.get("/retention-info")
async def get_retention_info(
    current_user: User = Depends(get_current_user),
):
    """Get backup retention policy information"""
    return {
        "retention_days": 30,  # DEFAULT_RETENTION_DAYS
        "description": "Backup retention periods",
        "policies": {
            "daily": "30 days",
            "weekly": "12 weeks (~3 months)",
            "monthly": "84 months (~7 years)",
        },
    }


# =============================================================================
# Statistics Endpoints
# =============================================================================

@router.get("/statistics")
async def get_backup_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get backup system statistics"""
    try:
        # Get job counts by status
        status_query = select(
            BackupJob.status,
            func.count(BackupJob.id).label("count")
        ).group_by(BackupJob.status)

        status_result = await db.execute(status_query)
        by_status = {row.status: row.count for row in status_result}

        # Get total backups
        total_query = select(func.count()).select_from(BackupJob)
        total_result = await db.execute(total_query)
        total_backups = total_result.scalar() or 0

        # Get successful backups
        success_query = select(func.count()).select_from(
            BackupJob.__table__.c().where(
                BackupJob.status == BackupStatus.COMPLETED
            )
        )
        success_result = await db.execute(success_query)
        successful_backups = success_result.scalar() or 0

        # Get total backup size
        size_query = select(func.coalesce(func.sum(BackupJob.backup_size_bytes), 0))
        size_result = await db.execute(size_query)
        total_size_bytes = size_result.scalar() or 0

        # Get recent backups (last 24 hours)
        recent_start = datetime.utcnow() - timedelta(hours=24)
        recent_query = select(func.count()).select_from(
            BackupJob.__table__.c().where(
                BackupJob.created_at >= recent_start
            )
        )
        recent_result = await db.execute(recent_query)
        recent_backups = recent_result.scalar() or 0

        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": total_backups - successful_backups,
            "by_status": by_status,
            "total_size_bytes": total_size_bytes,
            "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
            "recent_backups_24h": recent_backups,
        }

    except Exception as e:
        logger.error("Error getting backup statistics: {}".format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
