"""User Management API endpoints for STORY-037

This module provides API endpoints for:
- User CRUD operations
- Role assignment
- Department management
- Bulk user import
- Password reset (admin function)
- User activity logs
- User access requests
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_current_admin_user, get_db
from app.models.user import User, UserRole
from app.schemas.user_management import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, UserSearchQuery,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    BulkUserImportRequest, BulkUserImportResponse,
    AdminPasswordReset, PasswordResetResponse,
    UserActivityLogsResponse, UserActivityLogResponse,
    UserAccessRequestCreate, UserAccessRequestResponse, AccessRequestDecision,
    RoleResponse,
)
from app.crud import user_management as crud


router = APIRouter()


# =============================================================================
# Role Management
# =============================================================================

@router.get("/users/roles", response_model=List[RoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_user),
) -> List[RoleResponse]:
    """List all available roles with display names and descriptions"""
    roles = [
        RoleResponse(
            role=UserRole.ADMIN,
            display_name="Administrator",
            description="Full system access including user management",
            permissions=["*"],
        ),
        RoleResponse(
            role=UserRole.DOCTOR,
            display_name="Dokter",
            description="Doctor access for consultations, prescriptions, and patient records",
            permissions=["patients.read", "encounters.write", "prescriptions.write"],
        ),
        RoleResponse(
            role=UserRole.NURSE,
            display_name="Perawat",
            description="Nurse access for patient care and documentation",
            permissions=["patients.read", "vitals.write", "documentation.write"],
        ),
        RoleResponse(
            role=UserRole.PHARMACIST,
            display_name="Apoteker",
            description="Pharmacist access for dispensing and inventory management",
            permissions=["inventory.read", "inventory.write", "dispensing.write"],
        ),
        RoleResponse(
            role=UserRole.RECEPTIONIST,
            display_name="Petugas Pendaftaran",
            description="Reception access for patient registration and check-in",
            permissions=["patients.write", "registration.write"],
        ),
        RoleResponse(
            role=UserRole.LAB_STAFF,
            display_name="Staff Laboratorium",
            description="Lab staff access for test ordering and results",
            permissions=["lab.write", "results.write"],
        ),
        RoleResponse(
            role=UserRole.RADIOLOGY_STAFF,
            display_name="Staff Radiologi",
            description="Radiology staff access for imaging procedures",
            permissions=["radiology.write", "imaging.write"],
        ),
        RoleResponse(
            role=UserRole.BILLING_STAFF,
            display_name="Staff Keuangan",
            description="Billing staff access for invoices and payments",
            permissions=["billing.write", "payments.write"],
        ),
        RoleResponse(
            role=UserRole.SUPPORT_STAFF,
            display_name="Staff Pendukung",
            description="Basic support staff access",
            permissions=["basic.read"],
        ),
    ]
    return roles


# =============================================================================
# User Management Endpoints
# =============================================================================

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> UserResponse:
    """Create a new user (admin only)"""
    # Check if username already exists
    existing = await crud.get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    existing = await crud.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Create user
    user = await crud.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        password=user_data.password,
        role=user_data.role,
        department_id=user_data.department_id,
        phone=user_data.phone,
        employee_id=user_data.employee_id,
        license_number=user_data.license_number,
        is_active=user_data.is_active,
    )

    department_name = None
    if user.department:
        department_name = user.department.name

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department_id=user.department_id,
        department_name=department_name,
        phone=user.phone,
        employee_id=user.employee_id,
        license_number=user.license_number,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        failed_login_attempts=user.failed_login_attempts,
        locked_until=user.locked_until,
        password_changed_at=user.password_changed_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/users", response_model=UserListResponse)
async def list_users(
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    department_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> UserListResponse:
    """List users with filtering and pagination (admin only)"""
    users, total = await crud.list_users(
        db=db,
        search=search,
        role=role,
        department_id=department_id,
        is_active=is_active,
        page=page,
        page_size=page_size,
    )

    user_responses = []
    for user in users:
        department_name = None
        if user.department:
            department_name = user.department.name

        user_responses.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            department_id=user.department_id,
            department_name=department_name,
            phone=user.phone,
            employee_id=user.employee_id,
            license_number=user.license_number,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            mfa_enabled=user.mfa_enabled,
            last_login=user.last_login,
            failed_login_attempts=user.failed_login_attempts,
            locked_until=user.locked_until,
            password_changed_at=user.password_changed_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ))

    return UserListResponse(
        users=user_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> UserResponse:
    """Get user by ID (admin only)"""
    user = await crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    department_name = None
    if user.department:
        department_name = user.department.name

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department_id=user.department_id,
        department_name=department_name,
        phone=user.phone,
        employee_id=user.employee_id,
        license_number=user.license_number,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        failed_login_attempts=user.failed_login_attempts,
        locked_until=user.locked_until,
        password_changed_at=user.password_changed_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> UserResponse:
    """Update user information (admin only)"""
    user = await crud.update_user(
        db=db,
        user_id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        department_id=user_data.department_id,
        phone=user_data.phone,
        employee_id=user_data.employee_id,
        license_number=user_data.license_number,
        is_active=user_data.is_active,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    department_name = None
    if user.department:
        department_name = user.department.name

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        department_id=user.department_id,
        department_name=department_name,
        phone=user.phone,
        employee_id=user.employee_id,
        license_number=user.license_number,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        mfa_enabled=user.mfa_enabled,
        last_login=user.last_login,
        failed_login_attempts=user.failed_login_attempts,
        locked_until=user.locked_until,
        password_changed_at=user.password_changed_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Deactivate a user (soft delete, admin only)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    success = await crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deactivated successfully"}


@router.post("/users/{user_id}/reset-password", response_model=PasswordResetResponse)
async def reset_user_password(
    user_id: int,
    reset_data: AdminPasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> PasswordResetResponse:
    """Reset user password (admin only)"""
    user = await crud.change_user_password(
        db=db,
        user_id=user_id,
        new_password=reset_data.new_password,
        force_change_on_next_login=reset_data.force_change_on_next_login,
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return PasswordResetResponse(
        user_id=user.id,
        username=user.username,
        reset_at=user.updated_at,
        force_change_on_next_login=reset_data.force_change_on_next_login,
    )


@router.post("/users/bulk-import", response_model=BulkUserImportResponse)
async def bulk_import_users(
    import_data: BulkUserImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> BulkUserImportResponse:
    """Bulk import users (admin only)"""
    users_data = [user.model_dump() for user in import_data.users]
    succeeded, failed, errors = await crud.bulk_import_users(
        db=db,
        users_data=users_data,
        send_welcome_email=import_data.send_welcome_email,
    )

    return BulkUserImportResponse(
        total=len(import_data.users),
        succeeded=succeeded,
        failed=failed,
        errors=errors,
    )


# =============================================================================
# Department Management Endpoints
# =============================================================================

@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    department_data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> DepartmentResponse:
    """Create a new department (admin only)"""
    # Check if department code already exists
    existing = await crud.get_department_by_code(db, department_data.code)
    if existing:
        raise HTTPException(status_code=400, detail="Department code already exists")

    department = await crud.create_department(
        db=db,
        name=department_data.name,
        code=department_data.code,
        description=department_data.description,
        parent_department_id=department_data.parent_department_id,
    )

    return DepartmentResponse(
        id=department.id,
        name=department.name,
        code=department.code,
        description=department.description,
        parent_department_id=department.parent_department_id,
        created_at=department.created_at,
        updated_at=department.updated_at,
    )


@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(
    parent_department_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DepartmentResponse]:
    """List all departments"""
    departments = await crud.list_departments(
        db=db,
        parent_department_id=parent_department_id,
    )

    return [
        DepartmentResponse(
            id=dept.id,
            name=dept.name,
            code=dept.code,
            description=dept.description,
            parent_department_id=dept.parent_department_id,
            created_at=dept.created_at,
            updated_at=dept.updated_at,
        )
        for dept in departments
    ]


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentResponse:
    """Get department by ID"""
    department = await crud.get_department(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    return DepartmentResponse(
        id=department.id,
        name=department.name,
        code=department.code,
        description=department.description,
        parent_department_id=department.parent_department_id,
        created_at=department.created_at,
        updated_at=department.updated_at,
    )


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> DepartmentResponse:
    """Update department information (admin only)"""
    department = await crud.update_department(
        db=db,
        department_id=department_id,
        name=department_data.name,
        description=department_data.description,
        parent_department_id=department_data.parent_department_id,
    )
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    return DepartmentResponse(
        id=department.id,
        name=department.name,
        code=department.code,
        description=department.description,
        parent_department_id=department.parent_department_id,
        created_at=department.created_at,
        updated_at=department.updated_at,
    )


# =============================================================================
# User Activity Logs Endpoints
# =============================================================================

@router.get("/users/{user_id}/activity-logs", response_model=UserActivityLogsResponse)
async def get_user_activity_logs(
    user_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> UserActivityLogsResponse:
    """Get activity logs for a specific user (admin only)"""
    logs, total = await crud.get_user_activity_logs(
        db=db,
        user_id=user_id,
        page=page,
        page_size=page_size,
    )

    log_responses = []
    for log in logs:
        username = None
        if log.user:
            username = log.user.username

        log_responses.append(UserActivityLogResponse(
            id=log.id,
            user_id=log.user_id,
            username=username,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at,
            details=log.details,
        ))

    return UserActivityLogsResponse(
        logs=log_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/activity-logs", response_model=UserActivityLogsResponse)
async def get_all_activity_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> UserActivityLogsResponse:
    """Get all activity logs (admin only)"""
    logs, total = await crud.get_user_activity_logs(
        db=db,
        user_id=None,
        page=page,
        page_size=page_size,
    )

    log_responses = []
    for log in logs:
        username = None
        if log.user:
            username = log.user.username

        log_responses.append(UserActivityLogResponse(
            id=log.id,
            user_id=log.user_id,
            username=username,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            created_at=log.created_at,
            details=log.details,
        ))

    return UserActivityLogsResponse(
        logs=log_responses,
        total=total,
        page=page,
        page_size=page_size,
    )


# =============================================================================
# User Access Request Endpoints
# =============================================================================

@router.post("/users/access-requests", response_model=UserAccessRequestResponse)
async def create_access_request(
    request_data: UserAccessRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserAccessRequestResponse:
    """Create a new access request"""
    request = await crud.create_access_request(
        db=db,
        user_id=current_user.id,
        requested_role=request_data.requested_role,
        reason=request_data.reason,
        requested_department_id=request_data.requested_department_id,
    )

    requested_dept_name = None
    if request.requested_department:
        requested_dept_name = request.requested_department.name

    return UserAccessRequestResponse(
        id=request.id,
        user_id=request.user_id,
        username=request.user.username,
        full_name=request.user.full_name,
        requested_role=request.requested_role,
        requested_department_id=request.requested_department_id,
        requested_department_name=requested_dept_name,
        reason=request.reason,
        status=request.status,
        requested_at=request.requested_at,
        reviewed_at=request.reviewed_at,
        reviewed_by=request.reviewed_by,
        review_notes=request.review_notes,
    )


@router.get("/users/access-requests", response_model=List[UserAccessRequestResponse])
async def list_access_requests(
    status: Optional[str] = Query(None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> List[UserAccessRequestResponse]:
    """List user access requests (admin only)"""
    requests, total = await crud.list_access_requests(
        db=db,
        status=status,
        page=page,
        page_size=page_size,
    )

    responses = []
    for req in requests:
        requested_dept_name = None
        if req.requested_department:
            requested_dept_name = req.requested_department.name

        responses.append(UserAccessRequestResponse(
            id=req.id,
            user_id=req.user_id,
            username=req.user.username,
            full_name=req.user.full_name,
            requested_role=req.requested_role,
            requested_department_id=req.requested_department_id,
            requested_department_name=requested_dept_name,
            reason=req.reason,
            status=req.status,
            requested_at=req.requested_at,
            reviewed_at=req.reviewed_at,
            reviewed_by=req.reviewed_by,
            review_notes=req.review_notes,
        ))

    return responses


@router.put("/users/access-requests/{request_id}", response_model=UserAccessRequestResponse)
async def decide_access_request(
    request_id: int,
    decision: AccessRequestDecision,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
) -> UserAccessRequestResponse:
    """Approve or reject an access request (admin only)"""
    request = await crud.update_access_request(
        db=db,
        request_id=request_id,
        status=decision.decision,
        reviewed_by=current_user.id,
        review_notes=decision.review_notes,
        assign_role=decision.assign_role,
        assign_department_id=decision.assign_department_id,
    )
    if not request:
        raise HTTPException(status_code=404, detail="Access request not found")

    requested_dept_name = None
    if request.requested_department:
        requested_dept_name = request.requested_department.name

    return UserAccessRequestResponse(
        id=request.id,
        user_id=request.user_id,
        username=request.user.username,
        full_name=request.user.full_name,
        requested_role=request.requested_role,
        requested_department_id=request.requested_department_id,
        requested_department_name=requested_dept_name,
        reason=request.reason,
        status=request.status,
        requested_at=request.requested_at,
        reviewed_at=request.reviewed_at,
        reviewed_by=request.reviewed_by,
        review_notes=request.review_notes,
    )
