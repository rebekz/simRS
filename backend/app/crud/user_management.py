"""User Management CRUD Operations for STORY-037

This module provides CRUD operations for:
- User management (create, read, update, delete, list, search)
- Department management
- Role assignment
- Bulk user import
- Password reset
- User activity logs
- User access requests
"""
from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.models.hospital import Department
from app.models.user_management import UserAccessRequest
from app.models.audit_log import AuditLog
from app.core.security import get_password_hash, verify_password


# =============================================================================
# User Management CRUD
# =============================================================================

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID with department loaded"""
    stmt = select(User).options(selectinload(User.department)).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    stmt = select(User).options(selectinload(User.department)).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    stmt = select(User).options(selectinload(User.department)).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_users(
    db: AsyncSession,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[User], int]:
    """List users with filtering and pagination"""
    # Build query conditions
    conditions = []

    if search:
        search_pattern = f"%{search}%"
        conditions.append(
            or_(
                User.username.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.employee_id.ilike(search_pattern),
            )
        )

    if role:
        conditions.append(User.role == role)

    if department_id:
        conditions.append(User.department_id == department_id)

    if is_active is not None:
        conditions.append(User.is_active == is_active)

    # Build query
    stmt = select(User).options(selectinload(User.department))

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # Get total count
    count_stmt = select(User.id)
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = len(count_result.all())

    # Apply pagination and ordering
    stmt = stmt.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    users = result.scalars().all()

    return list(users), total


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    full_name: str,
    password: str,
    role: UserRole,
    department_id: Optional[int] = None,
    phone: Optional[str] = None,
    employee_id: Optional[str] = None,
    license_number: Optional[str] = None,
    is_active: bool = True,
) -> User:
    """Create a new user"""
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        role=role,
        department_id=department_id,
        phone=phone,
        employee_id=employee_id,
        license_number=license_number,
        is_active=is_active,
        password_changed_at=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    # Load department relationship
    await db.refresh(user, ["department"])
    return user


async def update_user(
    db: AsyncSession,
    user_id: int,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    role: Optional[UserRole] = None,
    department_id: Optional[int] = None,
    phone: Optional[str] = None,
    employee_id: Optional[str] = None,
    license_number: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> Optional[User]:
    """Update user information"""
    user = await get_user(db, user_id)
    if not user:
        return None

    if email is not None:
        user.email = email
    if full_name is not None:
        user.full_name = full_name
    if role is not None:
        user.role = role
    if department_id is not None:
        user.department_id = department_id
    if phone is not None:
        user.phone = phone
    if employee_id is not None:
        user.employee_id = employee_id
    if license_number is not None:
        user.license_number = license_number
    if is_active is not None:
        user.is_active = is_active

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete a user (soft delete by setting is_active=False)"""
    user = await get_user(db, user_id)
    if not user:
        return False

    user.is_active = False
    await db.commit()
    return True


async def change_user_password(
    db: AsyncSession,
    user_id: int,
    new_password: str,
    force_change_on_next_login: bool = True,
) -> Optional[User]:
    """Change user password (admin function)"""
    user = await get_user(db, user_id)
    if not user:
        return None

    user.hashed_password = get_password_hash(new_password)
    user.password_changed_at = datetime.utcnow()
    user.failed_login_attempts = 0  # Reset failed login attempts

    await db.commit()
    await db.refresh(user)
    return user


# =============================================================================
# Department Management CRUD
# =============================================================================

async def get_department(db: AsyncSession, department_id: int) -> Optional[Department]:
    """Get department by ID"""
    stmt = select(Department).where(Department.id == department_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_department_by_code(db: AsyncSession, code: str) -> Optional[Department]:
    """Get department by code"""
    stmt = select(Department).where(Department.code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_departments(
    db: AsyncSession,
    parent_department_id: Optional[int] = None,
) -> List[Department]:
    """List all departments with optional parent filter"""
    stmt = select(Department)
    if parent_department_id is not None:
        stmt = stmt.where(Department.parent_department_id == parent_department_id)
    stmt = stmt.order_by(Department.name)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_department(
    db: AsyncSession,
    name: str,
    code: str,
    description: Optional[str] = None,
    parent_department_id: Optional[int] = None,
) -> Department:
    """Create a new department"""
    department = Department(
        name=name,
        code=code,
        description=description,
        parent_department_id=parent_department_id,
    )
    db.add(department)
    await db.commit()
    await db.refresh(department)
    return department


async def update_department(
    db: AsyncSession,
    department_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    parent_department_id: Optional[int] = None,
) -> Optional[Department]:
    """Update department information"""
    department = await get_department(db, department_id)
    if not department:
        return None

    if name is not None:
        department.name = name
    if description is not None:
        department.description = description
    if parent_department_id is not None:
        department.parent_department_id = parent_department_id

    await db.commit()
    await db.refresh(department)
    return department


# =============================================================================
# Bulk User Import
# =============================================================================

async def bulk_import_users(
    db: AsyncSession,
    users_data: List[dict],
    send_welcome_email: bool = False,
) -> Tuple[int, int, List[dict]]:
    """Bulk import users from a list of user data

    Returns:
        Tuple of (succeeded_count, failed_count, errors)
    """
    succeeded = 0
    failed = 0
    errors = []

    for idx, user_data in enumerate(users_data):
        try:
            # Check if username or email already exists
            existing_user = await get_user_by_username(db, user_data["username"])
            if existing_user:
                errors.append({
                    "row": idx + 1,
                    "username": user_data["username"],
                    "error": "Username already exists"
                })
                failed += 1
                continue

            existing_user = await get_user_by_email(db, user_data["email"])
            if existing_user:
                errors.append({
                    "row": idx + 1,
                    "username": user_data["username"],
                    "error": "Email already exists"
                })
                failed += 1
                continue

            # Get department by code if provided
            department_id = None
            if "department_code" in user_data and user_data["department_code"]:
                dept = await get_department_by_code(db, user_data["department_code"])
                if dept:
                    department_id = dept.id

            # Create user
            await create_user(
                db=db,
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                password=user_data["password"],
                role=user_data["role"],
                department_id=department_id,
                phone=user_data.get("phone"),
                employee_id=user_data.get("employee_id"),
                license_number=user_data.get("license_number"),
            )
            succeeded += 1

        except Exception as e:
            errors.append({
                "row": idx + 1,
                "username": user_data.get("username", "unknown"),
                "error": str(e)
            })
            failed += 1

    return succeeded, failed, errors


# =============================================================================
# User Activity Logs
# =============================================================================

async def get_user_activity_logs(
    db: AsyncSession,
    user_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[AuditLog], int]:
    """Get user activity logs with optional user filter"""
    # Build query
    stmt = select(AuditLog).options(selectinload(AuditLog.user))

    if user_id is not None:
        stmt = stmt.where(AuditLog.user_id == user_id)

    # Get total count
    count_stmt = select(AuditLog.id)
    if user_id is not None:
        count_stmt = count_stmt.where(AuditLog.user_id == user_id)
    count_result = await db.execute(count_stmt)
    total = len(count_result.all())

    # Apply pagination and ordering
    stmt = stmt.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    logs = result.scalars().all()

    return list(logs), total


# =============================================================================
# User Access Requests
# =============================================================================

async def create_access_request(
    db: AsyncSession,
    user_id: int,
    requested_role: UserRole,
    reason: str,
    requested_department_id: Optional[int] = None,
) -> UserAccessRequest:
    """Create a new user access request"""
    request = UserAccessRequest(
        user_id=user_id,
        requested_role=requested_role,
        requested_department_id=requested_department_id,
        reason=reason,
        status="pending",
    )
    db.add(request)
    await db.commit()
    await db.refresh(request)
    return request


async def list_access_requests(
    db: AsyncSession,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[UserAccessRequest], int]:
    """List user access requests with optional status filter"""
    # Build query
    stmt = select(UserAccessRequest).options(
        selectinload(UserAccessRequest.user),
        selectinload(UserAccessRequest.requested_department),
    )

    if status is not None:
        stmt = stmt.where(UserAccessRequest.status == status)

    # Get total count
    count_stmt = select(UserAccessRequest.id)
    if status is not None:
        count_stmt = count_stmt.where(UserAccessRequest.status == status)
    count_result = await db.execute(count_stmt)
    total = len(count_result.all())

    # Apply pagination and ordering
    stmt = stmt.order_by(UserAccessRequest.requested_at.desc()).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(stmt)
    requests = result.scalars().all()

    return list(requests), total


async def get_access_request(db: AsyncSession, request_id: int) -> Optional[UserAccessRequest]:
    """Get access request by ID"""
    stmt = select(UserAccessRequest).options(
        selectinload(UserAccessRequest.user),
        selectinload(UserAccessRequest.requested_department),
    ).where(UserAccessRequest.id == request_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def update_access_request(
    db: AsyncSession,
    request_id: int,
    status: str,
    reviewed_by: int,
    review_notes: Optional[str] = None,
    assign_role: Optional[UserRole] = None,
    assign_department_id: Optional[int] = None,
) -> Optional[UserAccessRequest]:
    """Update access request with decision"""
    request = await get_access_request(db, request_id)
    if not request:
        return None

    request.status = status
    request.reviewed_at = datetime.utcnow()
    request.reviewed_by = reviewed_by
    request.review_notes = review_notes

    # If approved, update user role/department
    if status == "approved" and assign_role:
        user = request.user
        user.role = assign_role
        if assign_department_id is not None:
            user.department_id = assign_department_id

    await db.commit()
    await db.refresh(request)
    return request
