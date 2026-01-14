"""Hospital Configuration API Endpoints for STORY-039

This module provides API endpoints for:
- Hospital profile and branding
- Department management (wards, polyclinics, units)
- Room and bed configuration
- Doctor and staff directory
- Working hours and shifts
- Hospital branding (logo, letterhead)
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_superuser, get_db
from app.models.user import User
from app.schemas.hospital import (
    # Hospital profile schemas
    HospitalProfileCreate, HospitalProfileUpdate, HospitalProfileResponse,
    # Department schemas
    DepartmentCreate, DepartmentResponse,
    # Staff schemas
    StaffProfileCreate, StaffProfileResponse,
    # Shift schemas
    ShiftCreate, ShiftResponse,
    ShiftAssignmentCreate, ShiftAssignmentResponse,
    # Working hours schemas
    WorkingHoursCreate, WorkingHoursResponse,
    # Branding schemas
    BrandingConfigUpdate, BrandingConfigResponse,
    # Summary schema
    HospitalConfigurationSummary
)
from app.crud.hospital import (
    # Hospital profile operations
    get_hospital_profile, create_hospital_profile, update_hospital_profile, update_hospital_statistics,
    # Department operations
    get_department, get_departments, create_department, update_department, delete_department,
    # Staff operations
    get_staff_profile, get_staff_profile_by_user_id, get_staff_profiles,
    create_staff_profile, update_staff_profile, delete_staff_profile,
    # Shift operations
    get_shift, get_shifts, create_shift, update_shift, delete_shift,
    # Shift assignment operations
    get_shift_assignment, get_shift_assignments, create_shift_assignment, delete_shift_assignment,
    # Working hours operations
    get_working_hours, upsert_working_hours,
    # Branding operations
    get_branding_config, create_branding_config, update_branding_config,
    # Summary
    get_configuration_summary
)


router = APIRouter()


# =============================================================================
# Hospital Profile Endpoints
# =============================================================================

@router.get("/profile", response_model=HospitalProfileResponse)
def get_hospital_profile_endpoint(
    db: Session = Depends(get_db)
) -> HospitalProfileResponse:
    """Get hospital profile (public endpoint)"""
    hospital = get_hospital_profile(db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found. Please create one first."
        )
    return hospital


@router.post("/profile", response_model=HospitalProfileResponse, status_code=status.HTTP_201_CREATED)
def create_hospital_profile_endpoint(
    profile: HospitalProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> HospitalProfileResponse:
    """Create hospital profile (superuser only, can only be done once)"""
    existing = get_hospital_profile(db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital profile already exists. Use PUT to update."
        )

    hospital = create_hospital_profile(db, profile)
    return hospital


@router.put("/profile/{profile_id}", response_model=HospitalProfileResponse)
def update_hospital_profile_endpoint(
    profile_id: int,
    profile_update: HospitalProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> HospitalProfileResponse:
    """Update hospital profile (superuser only)"""
    hospital = update_hospital_profile(db, profile_id, profile_update)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found"
        )
    return hospital


@router.post("/profile/{profile_id}/refresh-statistics", response_model=HospitalProfileResponse)
def refresh_statistics(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> HospitalProfileResponse:
    """Refresh hospital statistics (superuser only)"""
    hospital = update_hospital_statistics(db)
    if not hospital or hospital.id != profile_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found"
        )
    return hospital


# =============================================================================
# Department Endpoints
# =============================================================================

@router.get("/departments", response_model=List[DepartmentResponse])
def list_departments(
    department_type: Optional[str] = Query(None, description="Filter by department type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[DepartmentResponse]:
    """List all departments with optional filtering"""
    departments = get_departments(db, department_type=department_type, is_active=is_active, skip=skip, limit=limit)
    return departments


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
def get_department_endpoint(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> DepartmentResponse:
    """Get department details"""
    department = get_department(db, department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return department


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department_endpoint(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> DepartmentResponse:
    """Create a new department (superuser only)"""
    hospital = get_hospital_profile(db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital profile must be created first"
        )

    # Check if code already exists
    existing = db.query(Department).filter(Department.code == department.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department code '{department.code}' already exists"
        )

    dept = create_department(db, department, hospital.id)
    return dept


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
def update_department_endpoint(
    department_id: int,
    department_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> DepartmentResponse:
    """Update department details (superuser only)"""
    department = update_department(db, department_id, department_update)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return department


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department_endpoint(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete a department (soft delete, superuser only)"""
    if not delete_department(db, department_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )


# =============================================================================
# Staff Profile Endpoints
# =============================================================================

@router.get("/staff", response_model=List[StaffProfileResponse])
def list_staff(
    role: Optional[str] = Query(None, description="Filter by role"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    employment_status: Optional[str] = Query(None, description="Filter by employment status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[StaffProfileResponse]:
    """List all staff profiles with optional filtering"""
    staff = get_staff_profiles(db, role=role, department_id=department_id, employment_status=employment_status, skip=skip, limit=limit)

    # Enrich with user data
    for s in staff:
        if s.user:
            s.email = s.user.email
            s.phone = s.user.phone
        if s.department:
            s.department_name = s.department.name
        if s.primary_department:
            s.primary_department_name = s.primary_department.name

    return staff


@router.get("/staff/me", response_model=StaffProfileResponse)
def get_my_staff_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StaffProfileResponse:
    """Get current user's staff profile"""
    staff = get_staff_profile_by_user_id(db, current_user.id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )

    # Enrich with user data
    if staff.user:
        staff.email = staff.user.email
        staff.phone = staff.user.phone
    if staff.department:
        staff.department_name = staff.department.name
    if staff.primary_department:
        staff.primary_department_name = staff.primary_department.name

    return staff


@router.get("/staff/{staff_id}", response_model=StaffProfileResponse)
def get_staff_profile_endpoint(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> StaffProfileResponse:
    """Get staff profile by ID"""
    staff = get_staff_profile(db, staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )

    # Enrich with user data
    if staff.user:
        staff.email = staff.user.email
        staff.phone = staff.user.phone
    if staff.department:
        staff.department_name = staff.department.name
    if staff.primary_department:
        staff.primary_department_name = staff.primary_department.name

    return staff


@router.post("/staff", response_model=StaffProfileResponse, status_code=status.HTTP_201_CREATED)
def create_staff_profile_endpoint(
    staff: StaffProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> StaffProfileResponse:
    """Create a new staff profile (superuser only)"""
    hospital = get_hospital_profile(db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital profile must be created first"
        )

    # Check if user exists
    from app.crud import user as user_crud
    user = user_crud.get_user(db, staff.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if employee_id already exists
    existing = db.query(StaffProfile).filter(StaffProfile.employee_id == staff.employee_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee ID '{staff.employee_id}' already exists"
        )

    staff_profile = create_staff_profile(db, staff, hospital.id)
    return staff_profile


@router.put("/staff/{staff_id}", response_model=StaffProfileResponse)
def update_staff_profile_endpoint(
    staff_id: int,
    staff_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> StaffProfileResponse:
    """Update staff profile (superuser only)"""
    staff = update_staff_profile(db, staff_id, staff_update)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )
    return staff


@router.delete("/staff/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_profile_endpoint(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete staff profile (superuser only)"""
    if not delete_staff_profile(db, staff_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff profile not found"
        )


# =============================================================================
# Shift Endpoints
# =============================================================================

@router.get("/shifts", response_model=List[ShiftResponse])
def list_shifts(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[ShiftResponse]:
    """List all shifts"""
    shifts = get_shifts(db, is_active=is_active)

    # Add total assigned staff count
    for shift in shifts:
        shift.total_assigned_staff = len([a for a in shift.assignments if a.is_active])

    return shifts


@router.get("/shifts/{shift_id}", response_model=ShiftResponse)
def get_shift_endpoint(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> ShiftResponse:
    """Get shift details"""
    shift = get_shift(db, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    shift.total_assigned_staff = len([a for a in shift.assignments if a.is_active])
    return shift


@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
def create_shift_endpoint(
    shift: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> ShiftResponse:
    """Create a new shift (superuser only)"""
    return create_shift(db, shift)


@router.put("/shifts/{shift_id}", response_model=ShiftResponse)
def update_shift_endpoint(
    shift_id: int,
    shift_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> ShiftResponse:
    """Update shift details (superuser only)"""
    shift = update_shift(db, shift_id, shift_update)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    return shift


@router.delete("/shifts/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shift_endpoint(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete shift (superuser only)"""
    if not delete_shift(db, shift_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )


# =============================================================================
# Shift Assignment Endpoints
# =============================================================================

@router.get("/shift-assignments", response_model=List[ShiftAssignmentResponse])
def list_shift_assignments(
    staff_id: Optional[int] = Query(None, description="Filter by staff ID"),
    shift_id: Optional[int] = Query(None, description="Filter by shift ID"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[ShiftAssignmentResponse]:
    """List shift assignments with optional filtering"""
    assignments = get_shift_assignments(db, staff_id=staff_id, shift_id=shift_id, department_id=department_id, is_active=is_active)

    # Enrich with related data
    for a in assignments:
        if a.staff:
            a.staff_name = a.staff.full_name
        if a.shift:
            a.shift_name = a.shift.name
        if a.department:
            a.department_name = a.department.name

    return assignments


@router.post("/shift-assignments", response_model=ShiftAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_shift_assignment_endpoint(
    assignment: ShiftAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> ShiftAssignmentResponse:
    """Create a new shift assignment (superuser only)"""
    # Validate staff and shift exist
    staff = get_staff_profile(db, assignment.staff_id)
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff not found"
        )

    shift = get_shift(db, assignment.shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )

    assignment_created = create_shift_assignment(db, assignment)

    # Enrich response
    assignment_created.staff_name = staff.full_name
    assignment_created.shift_name = shift.name

    return assignment_created


@router.delete("/shift-assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shift_assignment_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete shift assignment (soft delete, superuser only)"""
    if not delete_shift_assignment(db, assignment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift assignment not found"
        )


# =============================================================================
# Working Hours Endpoints
# =============================================================================

@router.get("/departments/{department_id}/working-hours", response_model=List[WorkingHoursResponse])
def get_department_working_hours(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[WorkingHoursResponse]:
    """Get working hours for a department (all 7 days)"""
    hours = get_working_hours(db, department_id)

    # Enrich with department name
    for h in hours:
        if h.department:
            h.department_name = h.department.name

    return hours


@router.put("/departments/{department_id}/working-hours", response_model=WorkingHoursResponse)
def upsert_working_hours_endpoint(
    department_id: int,
    working_hours: WorkingHoursCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> WorkingHoursResponse:
    """Create or update working hours for a department and day (superuser only)"""
    # Verify department exists
    dept = get_department(db, department_id)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    return upsert_working_hours(db, working_hours)


# =============================================================================
# Branding Configuration Endpoints
# =============================================================================

@router.get("/branding", response_model=BrandingConfigResponse)
def get_branding_config_endpoint(
    db: Session = Depends(get_db)
) -> BrandingConfigResponse:
    """Get hospital branding configuration (public endpoint)"""
    hospital = get_hospital_profile(db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found"
        )

    branding = get_branding_config(db, hospital.id)
    if not branding:
        # Return default branding
        return BrandingConfigResponse(
            id=0,
            hospital_id=hospital.id,
            updated_at=date.today()
        )

    return branding


@router.put("/branding", response_model=BrandingConfigResponse)
def update_branding_config_endpoint(
    branding_update: BrandingConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> BrandingConfigResponse:
    """Update hospital branding configuration (superuser only)"""
    hospital = get_hospital_profile(db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found"
        )

    branding = update_branding_config(db, hospital.id, branding_update)
    return branding


@router.post("/branding/logo", response_model=BrandingConfigResponse)
async def upload_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> BrandingConfigResponse:
    """Upload hospital logo (superuser only)"""
    hospital = get_hospital_profile(db)
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital profile not found"
        )

    # TODO: Implement file upload to S3/MinIO
    # For now, just return a placeholder URL
    logo_url = f"/uploads/logos/hospital_{hospital.id}_{file.filename}"

    branding_update = BrandingConfigUpdate(logo_url=logo_url)
    branding = update_branding_config(db, hospital.id, branding_update)

    return branding


# =============================================================================
# Configuration Summary Endpoint
# =============================================================================

@router.get("/configuration-summary", response_model=HospitalConfigurationSummary)
def get_config_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
) -> HospitalConfigurationSummary:
    """Get hospital configuration summary and completion status (superuser only)"""
    summary = get_configuration_summary(db)

    return HospitalConfigurationSummary(
        hospital_profile=summary["hospital_profile"],
        total_departments=summary["total_departments"],
        departments_by_type=summary["departments_by_type"],
        total_staff=summary["total_staff"],
        staff_by_role=summary["staff_by_role"],
        total_shifts=summary["total_shifts"],
        branding_configured=summary["branding_configured"],
        configuration_completion=summary["configuration_completion"],
        missing_configurations=summary["missing_configurations"]
    )
