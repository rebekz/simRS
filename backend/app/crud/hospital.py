"""Hospital Configuration CRUD Operations for STORY-039

This module provides CRUD operations for:
- Hospital profile and branding
- Department management (wards, polyclinics, units)
- Room and bed configuration
- Doctor and staff directory
- Working hours and shifts
- Hospital branding (logo, letterhead)
"""
from typing import List, Optional, Dict
from datetime import date, time
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import Session

from app.models.hospital import (
    HospitalProfile, Department, StaffProfile, Shift,
    ShiftAssignment, WorkingHours, BrandingConfig
)
from app.schemas.hospital import (
    HospitalProfileCreate, HospitalProfileUpdate,
    DepartmentCreate, StaffProfileCreate, ShiftCreate,
    ShiftAssignmentCreate, WorkingHoursCreate, BrandingConfigUpdate
)


# =============================================================================
# Hospital Profile CRUD
# =============================================================================

def get_hospital_profile(db: Session) -> Optional[HospitalProfile]:
    """Get the hospital profile (singleton - only one profile exists)"""
    return db.query(HospitalProfile).first()


def create_hospital_profile(db: Session, profile: HospitalProfileCreate) -> HospitalProfile:
    """Create hospital profile (should only be called once)"""
    db_profile = HospitalProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_hospital_profile(db: Session, profile_id: int, profile_update: HospitalProfileUpdate) -> Optional[HospitalProfile]:
    """Update hospital profile"""
    db_profile = get_hospital_profile(db)
    if not db_profile or db_profile.id != profile_id:
        return None

    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)

    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_hospital_statistics(db: Session) -> Optional[HospitalProfile]:
    """Update denormalized statistics in hospital profile"""
    db_profile = get_hospital_profile(db)
    if not db_profile:
        return None

    # Count departments
    total_departments = db.query(func.count(Department.id)).filter(
        Department.hospital_id == db_profile.id
    ).scalar()

    # Count doctors
    total_doctors = db.query(func.count(StaffProfile.id)).filter(
        and_(
            StaffProfile.hospital_id == db_profile.id,
            StaffProfile.role == "doctor"
        )
    ).scalar()

    # Count total staff
    total_staff = db.query(func.count(StaffProfile.id)).filter(
        StaffProfile.hospital_id == db_profile.id
    ).scalar()

    # Count beds (from rooms table)
    from app.models.bed import Bed
    total_beds = db.query(func.count(Bed.id)).scalar()

    db_profile.total_departments = total_departments or 0
    db_profile.total_doctors = total_doctors or 0
    db_profile.total_staff = total_staff or 0
    db_profile.total_beds = total_beds or 0

    db.commit()
    db.refresh(db_profile)
    return db_profile


# =============================================================================
# Department CRUD
# =============================================================================

def get_department(db: Session, department_id: int) -> Optional[Department]:
    """Get department by ID"""
    return db.query(Department).filter(Department.id == department_id).first()


def get_departments(
    db: Session,
    department_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Department]:
    """Get list of departments with optional filtering"""
    query = db.query(Department)

    if department_type:
        query = query.filter(Department.department_type == department_type)
    if is_active is not None:
        query = query.filter(Department.is_active == is_active)

    return query.offset(skip).limit(limit).all()


def create_department(db: Session, department: DepartmentCreate, hospital_id: int) -> Department:
    """Create a new department"""
    db_department = Department(**department.model_dump(), hospital_id=hospital_id)
    db.add(db_department)
    db.commit()
    db.refresh(db_department)

    # Update hospital statistics
    update_hospital_statistics(db)

    return db_department


def update_department(db: Session, department_id: int, department_update: dict) -> Optional[Department]:
    """Update department details"""
    db_department = get_department(db, department_id)
    if not db_department:
        return None

    for field, value in department_update.items():
        if hasattr(db_department, field):
            setattr(db_department, field, value)

    db.commit()
    db.refresh(db_department)
    return db_department


def delete_department(db: Session, department_id: int) -> bool:
    """Delete a department (soft delete by setting is_active=False)"""
    db_department = get_department(db, department_id)
    if not db_department:
        return False

    db_department.is_active = False
    db.commit()

    # Update hospital statistics
    update_hospital_statistics(db)

    return True


# =============================================================================
# Staff Profile CRUD
# =============================================================================

def get_staff_profile(db: Session, staff_id: int) -> Optional[StaffProfile]:
    """Get staff profile by ID"""
    return db.query(StaffProfile).filter(StaffProfile.id == staff_id).first()


def get_staff_profile_by_user_id(db: Session, user_id: int) -> Optional[StaffProfile]:
    """Get staff profile by user ID"""
    return db.query(StaffProfile).filter(StaffProfile.user_id == user_id).first()


def get_staff_profiles(
    db: Session,
    role: Optional[str] = None,
    department_id: Optional[int] = None,
    employment_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[StaffProfile]:
    """Get list of staff profiles with optional filtering"""
    query = db.query(StaffProfile)

    if role:
        query = query.filter(StaffProfile.role == role)
    if department_id:
        query = query.filter(
            or_(
                StaffProfile.department_id == department_id,
                StaffProfile.primary_department_id == department_id
            )
        )
    if employment_status:
        query = query.filter(StaffProfile.employment_status == employment_status)

    return query.offset(skip).limit(limit).all()


def create_staff_profile(db: Session, staff: StaffProfileCreate, hospital_id: int) -> StaffProfile:
    """Create a new staff profile"""
    db_staff = StaffProfile(**staff.model_dump(), hospital_id=hospital_id)
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)

    # Update hospital statistics
    update_hospital_statistics(db)

    return db_staff


def update_staff_profile(db: Session, staff_id: int, staff_update: dict) -> Optional[StaffProfile]:
    """Update staff profile details"""
    db_staff = get_staff_profile(db, staff_id)
    if not db_staff:
        return None

    for field, value in staff_update.items():
        if hasattr(db_staff, field):
            setattr(db_staff, field, value)

    db.commit()
    db.refresh(db_staff)

    # Update hospital statistics if role changed
    if "role" in staff_update:
        update_hospital_statistics(db)

    return db_staff


def delete_staff_profile(db: Session, staff_id: int) -> bool:
    """Delete staff profile"""
    db_staff = get_staff_profile(db, staff_id)
    if not db_staff:
        return False

    db.delete(db_staff)
    db.commit()

    # Update hospital statistics
    update_hospital_statistics(db)

    return True


# =============================================================================
# Shift CRUD
# =============================================================================

def get_shift(db: Session, shift_id: int) -> Optional[Shift]:
    """Get shift by ID"""
    return db.query(Shift).filter(Shift.id == shift_id).first()


def get_shifts(db: Session, is_active: Optional[bool] = None) -> List[Shift]:
    """Get list of shifts"""
    query = db.query(Shift)
    if is_active is not None:
        query = query.filter(Shift.is_active == is_active)
    return query.all()


def create_shift(db: Session, shift: ShiftCreate) -> Shift:
    """Create a new shift"""
    db_shift = Shift(**shift.model_dump())
    db.add(db_shift)
    db.commit()
    db.refresh(db_shift)
    return db_shift


def update_shift(db: Session, shift_id: int, shift_update: dict) -> Optional[Shift]:
    """Update shift details"""
    db_shift = get_shift(db, shift_id)
    if not db_shift:
        return None

    for field, value in shift_update.items():
        if hasattr(db_shift, field):
            setattr(db_shift, field, value)

    db.commit()
    db.refresh(db_shift)
    return db_shift


def delete_shift(db: Session, shift_id: int) -> bool:
    """Delete shift"""
    db_shift = get_shift(db, shift_id)
    if not db_shift:
        return False

    db.delete(db_shift)
    db.commit()
    return True


# =============================================================================
# Shift Assignment CRUD
# =============================================================================

def get_shift_assignment(db: Session, assignment_id: int) -> Optional[ShiftAssignment]:
    """Get shift assignment by ID"""
    return db.query(ShiftAssignment).filter(ShiftAssignment.id == assignment_id).first()


def get_shift_assignments(
    db: Session,
    staff_id: Optional[int] = None,
    shift_id: Optional[int] = None,
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None
) -> List[ShiftAssignment]:
    """Get list of shift assignments with optional filtering"""
    query = db.query(ShiftAssignment)

    if staff_id:
        query = query.filter(ShiftAssignment.staff_id == staff_id)
    if shift_id:
        query = query.filter(ShiftAssignment.shift_id == shift_id)
    if department_id:
        query = query.filter(ShiftAssignment.department_id == department_id)
    if is_active is not None:
        query = query.filter(ShiftAssignment.is_active == is_active)

    return query.all()


def create_shift_assignment(db: Session, assignment: ShiftAssignmentCreate) -> ShiftAssignment:
    """Create a new shift assignment"""
    db_assignment = ShiftAssignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def delete_shift_assignment(db: Session, assignment_id: int) -> bool:
    """Delete shift assignment (soft delete by setting is_active=False)"""
    db_assignment = get_shift_assignment(db, assignment_id)
    if not db_assignment:
        return False

    db_assignment.is_active = False
    db.commit()
    return True


# =============================================================================
# Working Hours CRUD
# =============================================================================

def get_working_hours(db: Session, department_id: int) -> List[WorkingHours]:
    """Get working hours for a department (all days)"""
    return db.query(WorkingHours).filter(
        WorkingHours.department_id == department_id
    ).order_by(WorkingHours.day_of_week).all()


def upsert_working_hours(db: Session, working_hours: WorkingHoursCreate) -> WorkingHours:
    """Create or update working hours for a department and day"""
    # Check if exists
    existing = db.query(WorkingHours).filter(
        and_(
            WorkingHours.department_id == working_hours.department_id,
            WorkingHours.day_of_week == working_hours.day_of_week
        )
    ).first()

    if existing:
        # Update
        for field, value in working_hours.model_dump().items():
            if hasattr(existing, field):
                setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create
        db_working_hours = WorkingHours(**working_hours.model_dump())
        db.add(db_working_hours)
        db.commit()
        db.refresh(db_working_hours)
        return db_working_hours


# =============================================================================
# Branding Configuration CRUD
# =============================================================================

def get_branding_config(db: Session, hospital_id: int) -> Optional[BrandingConfig]:
    """Get branding configuration for hospital"""
    return db.query(BrandingConfig).filter(BrandingConfig.hospital_id == hospital_id).first()


def create_branding_config(db: Session, hospital_id: int) -> BrandingConfig:
    """Create default branding configuration"""
    db_branding = BrandingConfig(hospital_id=hospital_id)
    db.add(db_branding)
    db.commit()
    db.refresh(db_branding)
    return db_branding


def update_branding_config(
    db: Session,
    hospital_id: int,
    branding_update: BrandingConfigUpdate
) -> Optional[BrandingConfig]:
    """Update branding configuration"""
    db_branding = get_branding_config(db, hospital_id)

    if not db_branding:
        # Create if doesn't exist
        db_branding = create_branding_config(db, hospital_id)

    update_data = branding_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_branding, field, value)

    db.commit()
    db.refresh(db_branding)
    return db_branding


# =============================================================================
# Configuration Summary
# =============================================================================

def get_configuration_summary(db: Session) -> Dict:
    """Get hospital configuration summary and completion status"""
    hospital = get_hospital_profile(db)
    if not hospital:
        return {
            "configuration_completion": 0.0,
            "missing_configurations": ["Hospital profile not created"]
        }

    missing = []
    total_checks = 0
    completed_checks = 0

    # Check hospital profile
    total_checks += 1
    if hospital.name and hospital.address_line and hospital.phone and hospital.email:
        completed_checks += 1
    else:
        missing.append("Hospital profile incomplete")

    # Check BPJS codes
    total_checks += 1
    if hospital.bpjs_ppk_code:
        completed_checks += 1
    else:
        missing.append("BPJS PPK code not configured")

    # Check departments
    total_checks += 1
    dept_count = len(get_departments(db))
    if dept_count > 0:
        completed_checks += 1
    else:
        missing.append("No departments configured")

    # Check staff
    total_checks += 1
    staff_count = len(get_staff_profiles(db))
    if staff_count > 0:
        completed_checks += 1
    else:
        missing.append("No staff profiles created")

    # Check shifts
    total_checks += 1
    shift_count = len(get_shifts(db))
    if shift_count > 0:
        completed_checks += 1
    else:
        missing.append("No shifts configured")

    # Check branding
    total_checks += 1
    branding = get_branding_config(db, hospital.id)
    if branding and branding.logo_url:
        completed_checks += 1
    else:
        missing.append("Hospital logo not uploaded")

    completion = (completed_checks / total_checks * 100) if total_checks > 0 else 0

    # Get statistics by type
    departments_by_type = {}
    for dept in get_departments(db):
        departments_by_type[dept.department_type] = departments_by_type.get(dept.department_type, 0) + 1

    staff_by_role = {}
    for staff in get_staff_profiles(db):
        staff_by_role[staff.role] = staff_by_role.get(staff.role, 0) + 1

    return {
        "hospital_profile": hospital,
        "total_departments": dept_count,
        "departments_by_type": departments_by_type,
        "total_staff": staff_count,
        "staff_by_role": staff_by_role,
        "total_shifts": shift_count,
        "branding_configured": branding is not None and branding.logo_url is not None,
        "configuration_completion": round(completion, 2),
        "missing_configurations": missing
    }
