"""Training Management CRUD Operations

This module provides CRUD operations for:
- Module Management: Training modules (courses, lessons, content)
- Assignment Management: User, role, and department training assignments
- Progress Tracking: User progress through training modules
- Completion Management: Training completion records and certificates
- Reporting: Training statistics, compliance reports, and summaries
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, case
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal

# Import models (these will need to be created separately)
# For now, we'll reference them as if they exist
# from app.models.training import (
#     TrainingModule, TrainingAssignment, TrainingProgress,
#     TrainingCompletion, TrainingLesson
# )


# =============================================================================
# Module Management
# =============================================================================

async def get_training_module(
    db: AsyncSession,
    module_id: int
) -> Optional[Any]:
    """Get a training module by ID"""
    from app.models.training import TrainingModule

    result = await db.execute(
        select(TrainingModule).filter(TrainingModule.id == module_id)
    )
    return result.scalar_one_or_none()


async def get_training_modules(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_mandatory: Optional[bool] = None,
) -> List[Any]:
    """Get list of training modules with optional filters"""
    from app.models.training import TrainingModule

    query = select(TrainingModule)

    conditions = []
    if category is not None:
        conditions.append(TrainingModule.category == category)
    if is_active is not None:
        conditions.append(TrainingModule.is_active == is_active)
    if is_mandatory is not None:
        conditions.append(TrainingModule.is_mandatory == is_mandatory)

    if conditions:
        query = query.filter(and_(*conditions))

    query = query.order_by(TrainingModule.title).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def create_training_module(
    db: AsyncSession,
    title: str,
    description: str,
    category: str,
    content: Dict[str, Any],
    duration_minutes: int,
    is_mandatory: bool = False,
    is_active: bool = True,
    valid_for_months: Optional[int] = None,
    prerequisites: Optional[List[int]] = None,
) -> Any:
    """Create a new training module"""
    from app.models.training import TrainingModule

    db_module = TrainingModule(
        title=title,
        description=description,
        category=category,
        content=content,
        duration_minutes=duration_minutes,
        is_mandatory=is_mandatory,
        is_active=is_active,
        valid_for_months=valid_for_months,
        prerequisites=prerequisites or [],
    )

    db.add(db_module)
    await db.commit()
    await db.refresh(db_module)

    return db_module


async def update_training_module(
    db: AsyncSession,
    module_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    content: Optional[Dict[str, Any]] = None,
    duration_minutes: Optional[int] = None,
    is_mandatory: Optional[bool] = None,
    is_active: Optional[bool] = None,
    valid_for_months: Optional[int] = None,
    prerequisites: Optional[List[int]] = None,
) -> Optional[Any]:
    """Update a training module"""
    db_module = await get_training_module(db, module_id)
    if not db_module:
        return None

    update_data = {
        "title": title,
        "description": description,
        "category": category,
        "content": content,
        "duration_minutes": duration_minutes,
        "is_mandatory": is_mandatory,
        "is_active": is_active,
        "valid_for_months": valid_for_months,
        "prerequisites": prerequisites,
    }

    for field, value in update_data.items():
        if value is not None:
            setattr(db_module, field, value)

    await db.commit()
    await db.refresh(db_module)

    return db_module


async def delete_training_module(
    db: AsyncSession,
    module_id: int,
) -> bool:
    """Delete a training module (soft delete by setting is_active=False)"""
    db_module = await get_training_module(db, module_id)
    if not db_module:
        return False

    # Soft delete
    db_module.is_active = False
    db_module.deleted_at = datetime.utcnow()

    await db.commit()
    return True


async def get_modules_by_category(
    db: AsyncSession,
    category: str,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    """Get training modules by category"""
    from app.models.training import TrainingModule

    result = await db.execute(
        select(TrainingModule)
        .filter(
            TrainingModule.category == category,
            TrainingModule.is_active == True
        )
        .order_by(TrainingModule.title)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_mandatory_modules(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    """Get all mandatory training modules"""
    from app.models.training import TrainingModule

    result = await db.execute(
        select(TrainingModule)
        .filter(
            TrainingModule.is_mandatory == True,
            TrainingModule.is_active == True
        )
        .order_by(TrainingModule.title)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_active_modules(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    """Get all active training modules"""
    from app.models.training import TrainingModule

    result = await db.execute(
        select(TrainingModule)
        .filter(TrainingModule.is_active == True)
        .order_by(TrainingModule.title)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# =============================================================================
# Assignment Management
# =============================================================================

async def get_training_assignment(
    db: AsyncSession,
    assignment_id: int,
) -> Optional[Any]:
    """Get a training assignment by ID"""
    from app.models.training import TrainingAssignment

    result = await db.execute(
        select(TrainingAssignment).filter(TrainingAssignment.id == assignment_id)
    )
    return result.scalar_one_or_none()


async def get_user_assignments(
    db: AsyncSession,
    user_id: int,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    """Get all training assignments for a user"""
    from app.models.training import TrainingAssignment

    query = select(TrainingAssignment).filter(TrainingAssignment.user_id == user_id)

    if status:
        query = query.filter(TrainingAssignment.status == status)

    query = query.order_by(TrainingAssignment.assigned_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def create_assignment(
    db: AsyncSession,
    user_id: int,
    module_id: int,
    assigned_by: int,
    due_date: Optional[date] = None,
    priority: str = "normal",
) -> Any:
    """Create a new training assignment"""
    from app.models.training import TrainingAssignment

    db_assignment = TrainingAssignment(
        user_id=user_id,
        module_id=module_id,
        assigned_by=assigned_by,
        due_date=due_date,
        priority=priority,
        status="pending",
    )

    db.add(db_assignment)
    await db.commit()
    await db.refresh(db_assignment)

    return db_assignment


async def update_assignment(
    db: AsyncSession,
    assignment_id: int,
    due_date: Optional[date] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[Any]:
    """Update a training assignment"""
    db_assignment = await get_training_assignment(db, assignment_id)
    if not db_assignment:
        return None

    update_data = {
        "due_date": due_date,
        "priority": priority,
        "status": status,
    }

    for field, value in update_data.items():
        if value is not None:
            setattr(db_assignment, field, value)

    await db.commit()
    await db.refresh(db_assignment)

    return db_assignment


async def assign_training_to_user(
    db: AsyncSession,
    user_id: int,
    module_id: int,
    assigned_by: int,
    due_date: Optional[date] = None,
) -> Any:
    """Assign a training module to a specific user"""
    return await create_assignment(
        db=db,
        user_id=user_id,
        module_id=module_id,
        assigned_by=assigned_by,
        due_date=due_date,
    )


async def assign_training_to_role(
    db: AsyncSession,
    role: str,
    module_id: int,
    assigned_by: int,
    due_date: Optional[date] = None,
) -> List[Any]:
    """Assign a training module to all users with a specific role"""
    from app.models.user import User
    from app.models.training import TrainingAssignment

    # Get all users with the specified role
    result = await db.execute(
        select(User).filter(User.role == role, User.is_active == True)
    )
    users = result.scalars().all()

    assignments = []
    for user in users:
        # Check if assignment already exists
        existing = await db.execute(
            select(TrainingAssignment).filter(
                TrainingAssignment.user_id == user.id,
                TrainingAssignment.module_id == module_id,
                TrainingAssignment.status.in_(["pending", "in_progress"])
            )
        )
        if existing.scalar_one_or_none():
            continue  # Skip if already assigned

        assignment = await create_assignment(
            db=db,
            user_id=user.id,
            module_id=module_id,
            assigned_by=assigned_by,
            due_date=due_date,
        )
        assignments.append(assignment)

    return assignments


async def assign_training_to_department(
    db: AsyncSession,
    department_id: int,
    module_id: int,
    assigned_by: int,
    due_date: Optional[date] = None,
) -> List[Any]:
    """Assign a training module to all users in a department"""
    from app.models.user import User

    # Get all users in the department
    result = await db.execute(
        select(User).filter(
            User.department_id == department_id,
            User.is_active == True
        )
    )
    users = result.scalars().all()

    assignments = []
    for user in users:
        assignment = await create_assignment(
            db=db,
            user_id=user.id,
            module_id=module_id,
            assigned_by=assigned_by,
            due_date=due_date,
        )
        assignments.append(assignment)

    return assignments


async def get_overdue_assignments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    """Get all overdue training assignments"""
    from app.models.training import TrainingAssignment

    today = date.today()

    result = await db.execute(
        select(TrainingAssignment)
        .filter(
            TrainingAssignment.due_date < today,
            TrainingAssignment.status.in_(["pending", "in_progress"])
        )
        .order_by(TrainingAssignment.due_date.asc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_completed_assignments(
    db: AsyncSession,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    """Get completed training assignments"""
    from app.models.training import TrainingAssignment

    query = select(TrainingAssignment).filter(
        TrainingAssignment.status == "completed"
    )

    if user_id:
        query = query.filter(TrainingAssignment.user_id == user_id)

    query = query.order_by(TrainingAssignment.completed_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


# =============================================================================
# Progress Tracking
# =============================================================================

async def get_user_progress(
    db: AsyncSession,
    user_id: int,
    module_id: int,
) -> Optional[Any]:
    """Get user progress for a specific training module"""
    from app.models.training import TrainingProgress

    result = await db.execute(
        select(TrainingProgress).filter(
            TrainingProgress.user_id == user_id,
            TrainingProgress.module_id == module_id
        )
    )
    return result.scalar_one_or_none()


async def update_progress(
    db: AsyncSession,
    user_id: int,
    module_id: int,
    lesson_id: Optional[int] = None,
    time_spent_minutes: int = 0,
) -> Any:
    """Update user progress for a training module"""
    from app.models.training import TrainingProgress

    progress = await get_user_progress(db, user_id, module_id)

    if progress:
        # Update existing progress
        progress.time_spent_minutes += time_spent_minutes
        progress.last_accessed_at = datetime.utcnow()

        if lesson_id:
            if not progress.completed_lessons:
                progress.completed_lessons = []
            if lesson_id not in progress.completed_lessons:
                progress.completed_lessons.append(lesson_id)

        await db.commit()
        await db.refresh(progress)
        return progress
    else:
        # Create new progress record
        db_progress = TrainingProgress(
            user_id=user_id,
            module_id=module_id,
            time_spent_minutes=time_spent_minutes,
            completed_lessons=[lesson_id] if lesson_id else [],
            status="in_progress",
            last_accessed_at=datetime.utcnow(),
        )

        db.add(db_progress)
        await db.commit()
        await db.refresh(db_progress)

        return db_progress


async def mark_lesson_complete(
    db: AsyncSession,
    user_id: int,
    module_id: int,
    lesson_id: int,
    time_spent_minutes: int = 0,
) -> Any:
    """Mark a lesson as complete for a user"""
    progress = await get_user_progress(db, user_id, module_id)

    if progress:
        if not progress.completed_lessons:
            progress.completed_lessons = []

        if lesson_id not in progress.completed_lessons:
            progress.completed_lessons.append(lesson_id)

        progress.time_spent_minutes += time_spent_minutes
        progress.last_accessed_at = datetime.utcnow()

        await db.commit()
        await db.refresh(progress)

        return progress
    else:
        return await update_progress(db, user_id, module_id, lesson_id, time_spent_minutes)


async def calculate_completion_percentage(
    db: AsyncSession,
    user_id: int,
    module_id: int,
) -> float:
    """Calculate completion percentage for a user in a module"""
    from app.models.training import TrainingProgress, TrainingModule, TrainingLesson

    progress = await get_user_progress(db, user_id, module_id)
    if not progress:
        return 0.0

    # Get total lessons in module
    result = await db.execute(
        select(func.count(TrainingLesson.id)).filter(
            TrainingLesson.module_id == module_id
        )
    )
    total_lessons = result.scalar() or 1  # Avoid division by zero

    # Get completed lessons count
    completed_count = len(progress.completed_lessons) if progress.completed_lessons else 0

    return round((completed_count / total_lessons) * 100, 2)


async def get_training_statistics(
    db: AsyncSession,
    module_id: int,
) -> Dict[str, Any]:
    """Get training statistics for a module"""
    from app.models.training import TrainingProgress, TrainingAssignment

    # Total enrolled
    enrolled_result = await db.execute(
        select(func.count(TrainingAssignment.id)).filter(
            TrainingAssignment.module_id == module_id
        )
    )
    total_enrolled = enrolled_result.scalar() or 0

    # Total completed
    completed_result = await db.execute(
        select(func.count(TrainingAssignment.id)).filter(
            TrainingAssignment.module_id == module_id,
            TrainingAssignment.status == "completed"
        )
    )
    total_completed = completed_result.scalar() or 0

    # Total in progress
    in_progress_result = await db.execute(
        select(func.count(TrainingProgress.id)).filter(
            TrainingProgress.module_id == module_id,
            TrainingProgress.status == "in_progress"
        )
    )
    total_in_progress = in_progress_result.scalar() or 0

    # Average completion percentage
    completion_rates = []
    result = await db.execute(
        select(TrainingProgress).filter(TrainingProgress.module_id == module_id)
    )
    all_progress = result.scalars().all()

    for progress in all_progress:
        percentage = await calculate_completion_percentage(db, progress.user_id, module_id)
        completion_rates.append(percentage)

    avg_completion = sum(completion_rates) / len(completion_rates) if completion_rates else 0

    return {
        "total_enrolled": total_enrolled,
        "total_completed": total_completed,
        "total_in_progress": total_in_progress,
        "completion_rate": round((total_completed / total_enrolled * 100) if total_enrolled > 0 else 0, 2),
        "average_completion_percentage": round(avg_completion, 2),
    }


# =============================================================================
# Completion Management
# =============================================================================

async def complete_training(
    db: AsyncSession,
    user_id: int,
    module_id: int,
    score: Optional[float] = None,
    certificate_issued: bool = False,
) -> Any:
    """Mark a training module as completed for a user"""
    from app.models.training import TrainingCompletion, TrainingProgress, TrainingAssignment

    # Check if already completed
    existing_result = await db.execute(
        select(TrainingCompletion).filter(
            TrainingCompletion.user_id == user_id,
            TrainingCompletion.module_id == module_id
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        return existing  # Already completed

    # Create completion record
    db_completion = TrainingCompletion(
        user_id=user_id,
        module_id=module_id,
        completed_at=datetime.utcnow(),
        score=score,
        certificate_issued=certificate_issued,
    )

    db.add(db_completion)

    # Update progress
    progress = await get_user_progress(db, user_id, module_id)
    if progress:
        progress.status = "completed"
        progress.completed_at = datetime.utcnow()

    # Update assignment status
    assignment_result = await db.execute(
        select(TrainingAssignment).filter(
            TrainingAssignment.user_id == user_id,
            TrainingAssignment.module_id == module_id,
            TrainingAssignment.status.in_(["pending", "in_progress"])
        )
    )
    assignment = assignment_result.scalar_one_or_none()
    if assignment:
        assignment.status = "completed"
        assignment.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(db_completion)

    return db_completion


async def record_completion(
    db: AsyncSession,
    user_id: int,
    module_id: int,
    score: Optional[float] = None,
    passed: bool = True,
    time_spent_minutes: int = 0,
    notes: Optional[str] = None,
) -> Any:
    """Record training completion with details"""
    from app.models.training import TrainingCompletion

    # Check if already completed
    existing_result = await db.execute(
        select(TrainingCompletion).filter(
            TrainingCompletion.user_id == user_id,
            TrainingCompletion.module_id == module_id
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        return existing  # Already completed

    db_completion = TrainingCompletion(
        user_id=user_id,
        module_id=module_id,
        completed_at=datetime.utcnow(),
        score=score,
        passed=passed,
        time_spent_minutes=time_spent_minutes,
        notes=notes,
    )

    db.add(db_completion)
    await db.commit()
    await db.refresh(db_completion)

    # Mark training as complete
    await complete_training(db, user_id, module_id, score, certificate_issued=passed)

    return db_completion


async def get_completion_certificate(
    db: AsyncSession,
    user_id: int,
    module_id: int,
) -> Optional[Any]:
    """Get completion certificate for a user and module"""
    from app.models.training import TrainingCompletion

    result = await db.execute(
        select(TrainingCompletion).filter(
            TrainingCompletion.user_id == user_id,
            TrainingCompletion.module_id == module_id,
            TrainingCompletion.passed == True
        )
    )
    completion = result.scalar_one_or_none()

    if completion and completion.certificate_issued:
        return completion

    return None


async def get_user_completions(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    """Get all training completions for a user"""
    from app.models.training import TrainingCompletion

    result = await db.execute(
        select(TrainingCompletion)
        .filter(TrainingCompletion.user_id == user_id)
        .order_by(TrainingCompletion.completed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_module_completions(
    db: AsyncSession,
    module_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    """Get all completions for a specific module"""
    from app.models.training import TrainingCompletion

    result = await db.execute(
        select(TrainingCompletion)
        .filter(TrainingCompletion.module_id == module_id)
        .order_by(TrainingCompletion.completed_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# =============================================================================
# Reporting
# =============================================================================

async def get_training_report(
    db: AsyncSession,
    module_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Any]:
    """Generate detailed training report for a module"""
    from app.models.training import TrainingCompletion, TrainingAssignment, TrainingProgress

    # Get module info
    module = await get_training_module(db, module_id)

    # Get completions in date range
    conditions = [TrainingCompletion.module_id == module_id]

    if start_date:
        conditions.append(TrainingCompletion.completed_at >= start_date)
    if end_date:
        conditions.append(TrainingCompletion.completed_at <= end_date)

    result = await db.execute(
        select(TrainingCompletion).filter(and_(*conditions))
    )
    completions = result.scalars().all()

    # Calculate statistics
    total_assignments_result = await db.execute(
        select(func.count(TrainingAssignment.id)).filter(
            TrainingAssignment.module_id == module_id
        )
    )
    total_assignments = total_assignments_result.scalar() or 0

    total_completions = len(completions)

    # Calculate average score
    scores = [c.score for c in completions if c.score is not None]
    avg_score = sum(scores) / len(scores) if scores else None

    # Calculate average time
    times = [c.time_spent_minutes for c in completions if c.time_spent_minutes]
    avg_time = sum(times) / len(times) if times else None

    return {
        "module_id": module_id,
        "module_title": module.title if module else "Unknown",
        "period": {
            "start": start_date,
            "end": end_date,
        },
        "total_assignments": total_assignments,
        "total_completions": total_completions,
        "completion_rate": round((total_completions / total_assignments * 100) if total_assignments > 0 else 0, 2),
        "average_score": round(avg_score, 2) if avg_score else None,
        "average_time_minutes": round(avg_time, 2) if avg_time else None,
        "completions": completions,
    }


async def get_user_training_summary(
    db: AsyncSession,
    user_id: int,
) -> Dict[str, Any]:
    """Get comprehensive training summary for a user"""
    from app.models.training import TrainingAssignment, TrainingCompletion

    # Get all assignments
    all_assignments_result = await db.execute(
        select(TrainingAssignment).filter(TrainingAssignment.user_id == user_id)
    )
    all_assignments = all_assignments_result.scalars().all()

    # Count by status
    pending = sum(1 for a in all_assignments if a.status == "pending")
    in_progress = sum(1 for a in all_assignments if a.status == "in_progress")
    completed = sum(1 for a in all_assignments if a.status == "completed")
    overdue = sum(1 for a in all_assignments if a.due_date and a.due_date < date.today() and a.status in ["pending", "in_progress"])

    # Get completions
    completions_result = await db.execute(
        select(TrainingCompletion).filter(TrainingCompletion.user_id == user_id)
    )
    completions = completions_result.scalars().all()

    # Calculate total time spent
    total_time = sum(c.time_spent_minutes for c in completions if c.time_spent_minutes)

    # Get recent completions
    recent_completions = sorted(completions, key=lambda c: c.completed_at, reverse=True)[:5]

    return {
        "user_id": user_id,
        "total_assignments": len(all_assignments),
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "overdue": overdue,
        "total_time_spent_minutes": total_time,
        "recent_completions": recent_completions,
    }


async def get_completion_rates(
    db: AsyncSession,
    module_ids: Optional[List[int]] = None,
    department_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Get completion rates for modules, optionally filtered by department"""
    from app.models.training import TrainingModule, TrainingAssignment, TrainingCompletion
    from app.models.user import User

    if module_ids:
        modules_result = await db.execute(
            select(TrainingModule).filter(TrainingModule.id.in_(module_ids))
        )
    else:
        modules_result = await db.execute(select(TrainingModule))

    modules = modules_result.scalars().all()

    rates = []
    for module in modules:
        # Get total assignments
        if department_id:
            # Filter by department
            total_result = await db.execute(
                select(func.count(TrainingAssignment.id))
                .join(User, TrainingAssignment.user_id == User.id)
                .filter(
                    TrainingAssignment.module_id == module.id,
                    User.department_id == department_id
                )
            )
            completed_result = await db.execute(
                select(func.count(TrainingAssignment.id))
                .join(User, TrainingAssignment.user_id == User.id)
                .filter(
                    TrainingAssignment.module_id == module.id,
                    TrainingAssignment.status == "completed",
                    User.department_id == department_id
                )
            )
        else:
            total_result = await db.execute(
                select(func.count(TrainingAssignment.id)).filter(
                    TrainingAssignment.module_id == module.id
                )
            )
            completed_result = await db.execute(
                select(func.count(TrainingAssignment.id)).filter(
                    TrainingAssignment.module_id == module.id,
                    TrainingAssignment.status == "completed"
                )
            )

        total = total_result.scalar() or 0
        completed = completed_result.scalar() or 0

        rates.append({
            "module_id": module.id,
            "module_title": module.title,
            "category": module.category,
            "total_assigned": total,
            "total_completed": completed,
            "completion_rate": round((completed / total * 100) if total > 0 else 0, 2),
        })

    return rates


async def get_overall_training_stats(
    db: AsyncSession,
) -> Dict[str, Any]:
    """Get overall training statistics across all modules"""
    from app.models.training import TrainingModule, TrainingAssignment, TrainingCompletion

    # Total modules
    modules_result = await db.execute(select(func.count(TrainingModule.id)))
    total_modules = modules_result.scalar() or 0

    # Active modules
    active_result = await db.execute(
        select(func.count(TrainingModule.id)).filter(TrainingModule.is_active == True)
    )
    active_modules = active_result.scalar() or 0

    # Mandatory modules
    mandatory_result = await db.execute(
        select(func.count(TrainingModule.id)).filter(TrainingModule.is_mandatory == True)
    )
    mandatory_modules = mandatory_result.scalar() or 0

    # Total assignments
    assignments_result = await db.execute(select(func.count(TrainingAssignment.id)))
    total_assignments = assignments_result.scalar() or 0

    # Completed assignments
    completed_result = await db.execute(
        select(func.count(TrainingAssignment.id)).filter(
            TrainingAssignment.status == "completed"
        )
    )
    total_completed = completed_result.scalar() or 0

    # Overdue assignments
    overdue_result = await db.execute(
        select(func.count(TrainingAssignment.id)).filter(
            TrainingAssignment.due_date < date.today(),
            TrainingAssignment.status.in_(["pending", "in_progress"])
        )
    )
    total_overdue = overdue_result.scalar() or 0

    # Total completions
    completions_result = await db.execute(select(func.count(TrainingCompletion.id)))
    total_completions = completions_result.scalar() or 0

    # Completions in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_result = await db.execute(
        select(func.count(TrainingCompletion.id)).filter(
            TrainingCompletion.completed_at >= thirty_days_ago
        )
    )
    recent_completions = recent_result.scalar() or 0

    return {
        "modules": {
            "total": total_modules,
            "active": active_modules,
            "mandatory": mandatory_modules,
        },
        "assignments": {
            "total": total_assignments,
            "completed": total_completed,
            "overdue": total_overdue,
            "completion_rate": round((total_completed / total_assignments * 100) if total_assignments > 0 else 0, 2),
        },
        "completions": {
            "total": total_completions,
            "last_30_days": recent_completions,
        },
    }


async def generate_compliance_report(
    db: AsyncSession,
    department_id: Optional[int] = None,
    role: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate compliance report for mandatory training"""
    from app.models.training import TrainingModule, TrainingAssignment, TrainingCompletion
    from app.models.user import User

    # Get all mandatory modules
    mandatory_result = await db.execute(
        select(TrainingModule).filter(
            TrainingModule.is_mandatory == True,
            TrainingModule.is_active == True
        )
    )
    mandatory_modules = mandatory_result.scalars().all()

    # Build base query for users
    user_query = select(User).filter(User.is_active == True)

    if department_id:
        user_query = user_query.filter(User.department_id == department_id)
    if role:
        user_query = user_query.filter(User.role == role)

    users_result = await db.execute(user_query)
    users = users_result.scalars().all()

    # Calculate compliance per user
    user_compliance = []
    total_compliant = 0

    for user in users:
        # Check mandatory module completion
        completed_mandatory = 0
        total_mandatory = len(mandatory_modules)

        for module in mandatory_modules:
            # Check if user has completed this module
            completion_result = await db.execute(
                select(TrainingCompletion).filter(
                    TrainingCompletion.user_id == user.id,
                    TrainingCompletion.module_id == module.id
                )
            )
            completion = completion_result.scalar_one_or_none()

            if completion:
                # Check if completion is still valid (not expired)
                if module.valid_for_months:
                    expiry_date = completion.completed_at + timedelta(days=module.valid_for_months * 30)
                    if expiry_date > datetime.utcnow():
                        completed_mandatory += 1
                else:
                    completed_mandatory += 1

        compliance_rate = (completed_mandatory / total_mandatory * 100) if total_mandatory > 0 else 100
        is_compliant = compliance_rate >= 100

        if is_compliant:
            total_compliant += 1

        user_compliance.append({
            "user_id": user.id,
            "user_name": user.full_name,
            "role": user.role,
            "department_id": user.department_id,
            "completed_mandatory": completed_mandatory,
            "total_mandatory": total_mandatory,
            "compliance_rate": round(compliance_rate, 2),
            "is_compliant": is_compliant,
        })

    # Overall compliance rate
    overall_rate = (total_compliant / len(users) * 100) if users else 100

    return {
        "period": {
            "generated_at": datetime.utcnow().isoformat(),
        },
        "filters": {
            "department_id": department_id,
            "role": role,
        },
        "summary": {
            "total_users": len(users),
            "total_compliant": total_compliant,
            "total_non_compliant": len(users) - total_compliant,
            "compliance_rate": round(overall_rate, 2),
            "mandatory_modules": len(mandatory_modules),
        },
        "user_compliance": user_compliance,
    }
