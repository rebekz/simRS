"""Training Management API endpoints

This module provides REST API endpoints for managing training modules,
assignments, user progress tracking, and compliance reporting.
All endpoints require authentication and appropriate permissions.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

from app.db.session import get_db
from app.core.deps import get_current_user, require_permission, get_request_info
from app.models.user import User
from app.schemas.training import (
    # Module schemas
    TrainingModuleCreate,
    TrainingModuleUpdate,
    TrainingModuleResponse,
    TrainingModuleListResponse,
    # Assignment schemas
    TrainingAssignmentCreate,
    TrainingAssignmentUpdate,
    TrainingAssignmentResponse,
    TrainingAssignmentListResponse,
    BulkAssignmentCreate,
    BulkAssignmentResponse,
    # Progress schemas
    TrainingProgressUpdate,
    TrainingProgressResponse,
    UserAssignmentListResponse,
    # Statistics schemas
    OverallStatsResponse,
    UserStatsResponse,
    ModuleStatsResponse,
    ComplianceReportResponse,
    CompletionReportResponse,
)
from app.crud import training as training_crud
from app.crud.audit_log import create_audit_log

router = APIRouter()


class TrainingStatus(str, Enum):
    """Training module status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AssignmentStatus(str, Enum):
    """Training assignment status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class CompletionStatus(str, Enum):
    """Training completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ============================================================================
# Module Management (Admin)
# ============================================================================

@router.get("/modules", response_model=TrainingModuleListResponse, status_code=status.HTTP_200_OK)
async def list_training_modules(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: Optional[TrainingStatus] = Query(None, description="Filter by module status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    List all training modules with pagination and filtering (Admin only).

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        status_filter: Optional status filter (draft, published, archived)
        category: Optional category filter
        search: Optional search term for title/description
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        Paginated list of training modules
    """
    modules, total = await training_crud.list_modules(
        db=db,
        skip=skip,
        limit=limit,
        status_filter=status_filter.value if status_filter else None,
        category=category,
        search=search
    )

    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return TrainingModuleListResponse(
        items=modules,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/modules/{module_id}", response_model=TrainingModuleResponse, status_code=status.HTTP_200_OK)
async def get_training_module(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    Get a specific training module by ID (Admin only).

    Args:
        module_id: Training module ID
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        Training module details

    Raises:
        HTTPException 404: If module not found
    """
    module = await training_crud.get_module_by_id(db, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training module with ID {module_id} not found"
        )
    return module


@router.post("/modules", response_model=TrainingModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_training_module(
    module_in: TrainingModuleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "create"))
):
    """
    Create a new training module (Admin only).

    Args:
        module_in: Training module creation data
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with training:create permission

    Returns:
        Created training module

    Raises:
        HTTPException 400: If validation error occurs
    """
    try:
        module = await training_crud.create_module(db, module_in, current_user.id)

        # Log module creation
        request_info = await get_request_info(request)
        await create_audit_log(
            db=db,
            action="TRAINING_MODULE_CREATED",
            resource_type="TrainingModule",
            username=current_user.username,
            user_id=current_user.id,
            resource_id=str(module.id),
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return module
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/modules/{module_id}", response_model=TrainingModuleResponse, status_code=status.HTTP_200_OK)
async def update_training_module(
    module_id: int,
    module_in: TrainingModuleUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "update"))
):
    """
    Update an existing training module (Admin only).

    Args:
        module_id: Training module ID
        module_in: Training module update data
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with training:update permission

    Returns:
        Updated training module

    Raises:
        HTTPException 404: If module not found
        HTTPException 400: If validation error occurs
    """
    try:
        module = await training_crud.update_module(db, module_id, module_in, current_user.id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training module with ID {module_id} not found"
            )

        # Log module update
        request_info = await get_request_info(request)
        await create_audit_log(
            db=db,
            action="TRAINING_MODULE_UPDATED",
            resource_type="TrainingModule",
            username=current_user.username,
            user_id=current_user.id,
            resource_id=str(module_id),
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return module
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_module(
    module_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "delete"))
):
    """
    Delete a training module (Admin only).

    Args:
        module_id: Training module ID
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with training:delete permission

    Raises:
        HTTPException 404: If module not found
        HTTPException 400: If module has active assignments
    """
    try:
        success = await training_crud.delete_module(db, module_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training module with ID {module_id} not found"
            )

        # Log module deletion
        request_info = await get_request_info(request)
        await create_audit_log(
            db=db,
            action="TRAINING_MODULE_DELETED",
            resource_type="TrainingModule",
            username=current_user.username,
            user_id=current_user.id,
            resource_id=str(module_id),
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# Assignment Management
# ============================================================================

@router.get("/assignments", response_model=TrainingAssignmentListResponse, status_code=status.HTTP_200_OK)
async def list_training_assignments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    status_filter: Optional[AssignmentStatus] = Query(None, description="Filter by assignment status"),
    module_id: Optional[int] = Query(None, description="Filter by module ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    List all training assignments with pagination and filtering (Admin/Manager).

    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        status_filter: Optional status filter
        module_id: Optional module ID filter
        user_id: Optional user ID filter
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        Paginated list of training assignments
    """
    assignments, total = await training_crud.list_assignments(
        db=db,
        skip=skip,
        limit=limit,
        status_filter=status_filter.value if status_filter else None,
        module_id=module_id,
        user_id=user_id
    )

    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return TrainingAssignmentListResponse(
        items=assignments,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/assignments/{assignment_id}", response_model=TrainingAssignmentResponse, status_code=status.HTTP_200_OK)
async def get_training_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    Get a specific training assignment by ID.

    Args:
        assignment_id: Training assignment ID
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        Training assignment details

    Raises:
        HTTPException 404: If assignment not found
    """
    assignment = await training_crud.get_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training assignment with ID {assignment_id} not found"
        )
    return assignment


@router.post("/assignments", response_model=TrainingAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_training_assignment(
    assignment_in: TrainingAssignmentCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "create"))
):
    """
    Create a new training assignment (Admin/Manager).

    Args:
        assignment_in: Training assignment creation data
        request: FastAPI Request object
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user with training:create permission

    Returns:
        Created training assignment

    Raises:
        HTTPException 400: If validation error occurs
    """
    try:
        assignment = await training_crud.create_assignment(db, assignment_in, current_user.id)

        # Send notification in background
        if background_tasks:
            background_tasks.add_task(
                training_crud.send_assignment_notification,
                db, assignment.id
            )

        # Log assignment creation
        request_info = await get_request_info(request)
        await create_audit_log(
            db=db,
            action="TRAINING_ASSIGNED",
            resource_type="TrainingAssignment",
            username=current_user.username,
            user_id=current_user.id,
            resource_id=str(assignment.id),
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/assign-bulk", response_model=BulkAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def bulk_assign_training(
    bulk_assignment: BulkAssignmentCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "create"))
):
    """
    Bulk assign training to multiple users or roles (Admin/Manager).

    Args:
        bulk_assignment: Bulk assignment data with module, users/roles, due date
        request: FastAPI Request object
        background_tasks: FastAPI background tasks
        db: Database session
        current_user: Authenticated user with training:create permission

    Returns:
        Bulk assignment response with success/failure counts

    Raises:
        HTTPException 400: If validation error occurs
    """
    try:
        result = await training_crud.bulk_assign_training(
            db=db,
            module_id=bulk_assignment.module_id,
            user_ids=bulk_assignment.user_ids,
            roles=bulk_assignment.roles,
            due_date=bulk_assignment.due_date,
            assigned_by=current_user.id,
            background_tasks=background_tasks
        )

        # Log bulk assignment
        request_info = await get_request_info(request)
        await create_audit_log(
            db=db,
            action="TRAINING_BULK_ASSIGNED",
            resource_type="TrainingAssignment",
            username=current_user.username,
            user_id=current_user.id,
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
            details=f"Module {bulk_assignment.module_id} assigned to {result.successful_count} users"
        )

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/assignments/{assignment_id}", response_model=TrainingAssignmentResponse, status_code=status.HTTP_200_OK)
async def update_training_assignment(
    assignment_id: int,
    assignment_in: TrainingAssignmentUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "update"))
):
    """
    Update an existing training assignment (Admin/Manager).

    Args:
        assignment_id: Training assignment ID
        assignment_in: Training assignment update data
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with training:update permission

    Returns:
        Updated training assignment

    Raises:
        HTTPException 404: If assignment not found
        HTTPException 400: If validation error occurs
    """
    try:
        assignment = await training_crud.update_assignment(db, assignment_id, assignment_in)
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training assignment with ID {assignment_id} not found"
            )

        # Log assignment update
        request_info = await get_request_info(request)
        await create_audit_log(
            db=db,
            action="TRAINING_ASSIGNMENT_UPDATED",
            resource_type="TrainingAssignment",
            username=current_user.username,
            user_id=current_user.id,
            resource_id=str(assignment_id),
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return assignment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_assignment(
    assignment_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "delete"))
):
    """
    Cancel/delete a training assignment (Admin/Manager).

    Args:
        assignment_id: Training assignment ID
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user with training:delete permission

    Raises:
        HTTPException 404: If assignment not found
    """
    success = await training_crud.delete_assignment(db, assignment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training assignment with ID {assignment_id} not found"
        )

    # Log assignment deletion
    request_info = await get_request_info(request)
    await create_audit_log(
        db=db,
        action="TRAINING_ASSIGNMENT_CANCELLED",
        resource_type="TrainingAssignment",
        username=current_user.username,
        user_id=current_user.id,
        resource_id=str(assignment_id),
        ip_address=request_info["ip_address"],
        user_agent=request_info["user_agent"],
        request_path=request_info["request_path"],
        request_method=request_info["request_method"],
        success=True,
    )


# ============================================================================
# User Progress (All Users)
# ============================================================================

@router.get("/my-assignments", response_model=UserAssignmentListResponse, status_code=status.HTTP_200_OK)
async def get_my_assignments(
    status_filter: Optional[AssignmentStatus] = Query(None, description="Filter by assignment status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's training assignments.

    Args:
        status_filter: Optional status filter
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        db: Database session
        current_user: Authenticated user

    Returns:
        Paginated list of user's training assignments
    """
    assignments, total = await training_crud.get_user_assignments(
        db=db,
        user_id=current_user.id,
        status_filter=status_filter.value if status_filter else None,
        skip=skip,
        limit=limit
    )

    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return UserAssignmentListResponse(
        items=assignments,
        total=total,
        page=page,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/my-progress/{module_id}", response_model=TrainingProgressResponse, status_code=status.HTTP_200_OK)
async def get_my_progress(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's progress for a specific module.

    Args:
        module_id: Training module ID
        db: Database session
        current_user: Authenticated user

    Returns:
        User's training progress for the module

    Raises:
        HTTPException 404: If no assignment found for this module
    """
    progress = await training_crud.get_user_progress(db, current_user.id, module_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No training assignment found for module {module_id}"
        )
    return progress


@router.post("/progress/{assignment_id}", response_model=TrainingProgressResponse, status_code=status.HTTP_200_OK)
async def update_progress(
    assignment_id: int,
    progress_in: TrainingProgressUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update training progress for an assignment.

    Args:
        assignment_id: Training assignment ID
        progress_in: Progress update data (percentage_completed, last_position)
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated training progress

    Raises:
        HTTPException 404: If assignment not found
        HTTPException 400: If validation error occurs
    """
    try:
        # Verify ownership
        assignment = await training_crud.get_assignment_by_id(db, assignment_id)
        if not assignment or assignment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training assignment with ID {assignment_id} not found"
            )

        progress = await training_crud.update_progress(db, assignment_id, progress_in)

        # Log progress update
        request_info = await get_request_info(request)
        await create_audit_log(
            db=db,
            action="TRAINING_PROGRESS_UPDATED",
            resource_type="TrainingProgress",
            username=current_user.username,
            user_id=current_user.id,
            resource_id=str(assignment_id),
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return progress
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/complete/{assignment_id}", response_model=TrainingProgressResponse, status_code=status.HTTP_200_OK)
async def mark_complete(
    assignment_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a training assignment as completed.

    Args:
        assignment_id: Training assignment ID
        request: FastAPI Request object
        db: Database session
        current_user: Authenticated user

    Returns:
        Updated training progress with completed status

    Raises:
        HTTPException 404: If assignment not found
        HTTPException 400: If validation error occurs
    """
    try:
        # Verify ownership
        assignment = await training_crud.get_assignment_by_id(db, assignment_id)
        if not assignment or assignment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Training assignment with ID {assignment_id} not found"
            )

        progress = await training_crud.mark_completed(db, assignment_id, current_user.id)

        # Log completion
        request_info = await get_request_info(request)
        await create_audit_log(
            db=db,
            action="TRAINING_COMPLETED",
            resource_type="TrainingProgress",
            username=current_user.username,
            user_id=current_user.id,
            resource_id=str(assignment_id),
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            request_path=request_info["request_path"],
            request_method=request_info["request_method"],
            success=True,
        )

        return progress
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# Reporting (Admin/Manager)
# ============================================================================

@router.get("/stats/overall", response_model=OverallStatsResponse, status_code=status.HTTP_200_OK)
async def get_overall_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    Get overall training statistics (Admin/Manager).

    Args:
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        Overall training statistics including total modules, assignments,
        completion rates, and overdue counts
    """
    stats = await training_crud.get_overall_statistics(db)
    return stats


@router.get("/stats/user/{user_id}", response_model=UserStatsResponse, status_code=status.HTTP_200_OK)
async def get_user_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    Get training statistics for a specific user (Admin/Manager).

    Args:
        user_id: User ID to get statistics for
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        User-specific training statistics

    Raises:
        HTTPException 404: If user not found
    """
    stats = await training_crud.get_user_statistics(db, user_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found or has no training data"
        )
    return stats


@router.get("/stats/module/{module_id}", response_model=ModuleStatsResponse, status_code=status.HTTP_200_OK)
async def get_module_stats(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    Get training statistics for a specific module (Admin/Manager).

    Args:
        module_id: Module ID to get statistics for
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        Module-specific training statistics

    Raises:
        HTTPException 404: If module not found
    """
    stats = await training_crud.get_module_statistics(db, module_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Training module with ID {module_id} not found"
        )
    return stats


@router.get("/report/compliance", response_model=ComplianceReportResponse, status_code=status.HTTP_200_OK)
async def get_compliance_report(
    department: Optional[str] = Query(None, description="Filter by department"),
    role: Optional[str] = Query(None, description="Filter by role"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    Get compliance report showing mandatory training completion (Admin/Manager).

    Args:
        department: Optional department filter
        role: Optional role filter
        start_date: Optional start date for report period
        end_date: Optional end date for report period
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        Compliance report with completion rates and non-compliant users
    """
    report = await training_crud.get_compliance_report(
        db=db,
        department=department,
        role=role,
        start_date=start_date,
        end_date=end_date
    )
    return report


@router.get("/report/completion", response_model=CompletionReportResponse, status_code=status.HTTP_200_OK)
async def get_completion_report(
    module_id: Optional[int] = Query(None, description="Filter by module ID"),
    group_by: str = Query("user", description="Group report by: user, department, or module"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("training", "read"))
):
    """
    Get detailed completion report (Admin/Manager).

    Args:
        module_id: Optional module ID filter
        group_by: How to group the report (user, department, module)
        start_date: Optional start date for report period
        end_date: Optional end date for report period
        db: Database session
        current_user: Authenticated user with training:read permission

    Returns:
        Detailed completion report with progress data

    Raises:
        HTTPException 400: If invalid group_by parameter
    """
    if group_by not in ["user", "department", "module"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="group_by must be one of: user, department, module"
        )

    report = await training_crud.get_completion_report(
        db=db,
        module_id=module_id,
        group_by=group_by,
        start_date=start_date,
        end_date=end_date
    )
    return report
