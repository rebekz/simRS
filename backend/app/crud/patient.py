"""Patient CRUD operations for STORY-006: New Patient Registration

This module provides CRUD operations for Patient, EmergencyContact, and PatientInsurance models.
All functions are async and follow SQLAlchemy 2.0 patterns.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import Optional, List, Tuple
from datetime import datetime

from app.models.patient import Patient, EmergencyContact, PatientInsurance
from app.schemas.patient import PatientCreate, PatientUpdate


async def get_patient_by_id(db: AsyncSession, patient_id: int) -> Optional[Patient]:
    """
    Get patient by ID.

    Args:
        db: Database session
        patient_id: Patient ID

    Returns:
        Patient object or None
    """
    result = await db.execute(
        select(Patient).filter(Patient.id == patient_id)
    )
    return result.scalar_one_or_none()


async def get_patient_by_mrn(db: AsyncSession, medical_record_number: str) -> Optional[Patient]:
    """
    Get patient by Medical Record Number (MRN).

    Args:
        db: Database session
        medical_record_number: Medical Record Number

    Returns:
        Patient object or None
    """
    result = await db.execute(
        select(Patient).filter(Patient.medical_record_number == medical_record_number)
    )
    return result.scalar_one_or_none()


async def get_patient_by_nik(db: AsyncSession, nik: str) -> Optional[Patient]:
    """
    Get patient by NIK (Indonesian ID number).

    Args:
        db: Database session
        nik: 16-digit Indonesian ID number

    Returns:
        Patient object or None
    """
    result = await db.execute(
        select(Patient).filter(Patient.nik == nik)
    )
    return result.scalar_one_or_none()


async def search_patients(
    db: AsyncSession,
    search_term: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    is_active: bool = True
) -> Tuple[List[Patient], int]:
    """
    Search patients by name, phone, MRN, or NIK with pagination.

    Args:
        db: Database session
        search_term: Search term (matches name, phone, MRN, or NIK)
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        is_active: Filter by active status

    Returns:
        Tuple of (list of patients, total count)
    """
    # Build base query
    query = select(Patient).filter(Patient.is_active == is_active)
    count_query = select(func.count(Patient.id)).filter(Patient.is_active == is_active)

    # Add search conditions if search_term is provided
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Patient.full_name.ilike(search_pattern),
                Patient.phone.ilike(search_pattern),
                Patient.medical_record_number.ilike(search_pattern),
                Patient.nik.ilike(search_pattern)
            )
        )
        count_query = count_query.filter(
            or_(
                Patient.full_name.ilike(search_pattern),
                Patient.phone.ilike(search_pattern),
                Patient.medical_record_number.ilike(search_pattern),
                Patient.nik.ilike(search_pattern)
            )
        )

    # Order by most recently created
    query = query.order_by(Patient.created_at.desc())

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    patients = result.scalars().all()

    return list(patients), total


async def create_patient(db: AsyncSession, patient_in: PatientCreate) -> Patient:
    """
    Create a new patient with auto-generated MRN.

    Args:
        db: Database session
        patient_in: Patient creation data

    Returns:
        Created patient object

    Raises:
        ValueError: If duplicate patient exists
    """
    # Check for duplicates by NIK
    if patient_in.nik:
        existing_by_nik = await get_patient_by_nik(db, patient_in.nik)
        if existing_by_nik:
            raise ValueError(
                f"Patient with NIK {patient_in.nik} already exists "
                f"(MRN: {existing_by_nik.medical_record_number})"
            )

    # Check for duplicates by name and date of birth
    existing_by_name_dob = await detect_duplicates(
        db,
        patient_in.full_name,
        patient_in.date_of_birth
    )
    if existing_by_name_dob:
        raise ValueError(
            f"Patient with name '{patient_in.full_name}' and "
            f"date of birth '{patient_in.date_of_birth}' already exists "
            f"(MRN: {existing_by_name_dob.medical_record_number})"
        )

    # Generate unique MRN
    mrn = await generate_mrn(db)

    # Create patient object
    db_patient = Patient(
        medical_record_number=mrn,
        nik=patient_in.nik,
        full_name=patient_in.full_name,
        date_of_birth=patient_in.date_of_birth,
        gender=patient_in.gender,
        blood_type=patient_in.blood_type,
        marital_status=patient_in.marital_status,
        phone=patient_in.phone,
        email=patient_in.email,
        address=patient_in.address,
        city=patient_in.city,
        province=patient_in.province,
        postal_code=patient_in.postal_code,
        religion=patient_in.religion,
        occupation=patient_in.occupation,
        photo_url=patient_in.photo_url,
        is_active=True
    )

    db.add(db_patient)

    # Flush to get patient ID before adding relationships
    await db.flush()

    # Add emergency contacts
    for contact_in in patient_in.emergency_contacts:
        db_contact = EmergencyContact(
            patient_id=db_patient.id,
            name=contact_in.name,
            relationship=contact_in.relationship,
            phone=contact_in.phone,
            address=contact_in.address
        )
        db.add(db_contact)

    # Add insurance policies
    for insurance_in in patient_in.insurance_policies:
        db_insurance = PatientInsurance(
            patient_id=db_patient.id,
            insurance_type=insurance_in.insurance_type,
            insurance_number=insurance_in.insurance_number,
            member_name=insurance_in.member_name,
            expiry_date=insurance_in.expiry_date
        )
        db.add(db_insurance)

    await db.commit()
    await db.refresh(db_patient)

    return db_patient


async def update_patient(
    db: AsyncSession,
    patient_id: int,
    patient_in: PatientUpdate
) -> Optional[Patient]:
    """
    Update an existing patient.

    Args:
        db: Database session
        patient_id: Patient ID
        patient_in: Patient update data

    Returns:
        Updated patient object or None
    """
    db_patient = await get_patient_by_id(db, patient_id)
    if not db_patient:
        return None

    # Update fields that are provided
    update_data = patient_in.model_dump(exclude_unset=True, exclude_none=True)

    # Handle NIK change - check for duplicates
    if 'nik' in update_data and update_data['nik'] != db_patient.nik:
        existing_by_nik = await get_patient_by_nik(db, update_data['nik'])
        if existing_by_nik and existing_by_nik.id != patient_id:
            raise ValueError(f"Patient with NIK {update_data['nik']} already exists")

    # Update patient fields
    for field, value in update_data.items():
        if field not in ['emergency_contacts', 'insurance_policies']:
            setattr(db_patient, field, value)

    # Handle emergency contacts update if provided
    if 'emergency_contacts' in update_data and patient_in.emergency_contacts is not None:
        # Delete existing contacts
        await db.execute(
            select(EmergencyContact).filter(EmergencyContact.patient_id == patient_id)
        )
        existing_contacts = await db.execute(
            select(EmergencyContact).filter(EmergencyContact.patient_id == patient_id)
        )
        for contact in existing_contacts.scalars().all():
            await db.delete(contact)

        # Add new contacts
        for contact_in in patient_in.emergency_contacts:
            db_contact = EmergencyContact(
                patient_id=patient_id,
                name=contact_in.name,
                relationship=contact_in.relationship,
                phone=contact_in.phone,
                address=contact_in.address
            )
            db.add(db_contact)

    # Handle insurance policies update if provided
    if 'insurance_policies' in update_data and patient_in.insurance_policies is not None:
        # Delete existing policies
        existing_policies = await db.execute(
            select(PatientInsurance).filter(PatientInsurance.patient_id == patient_id)
        )
        for policy in existing_policies.scalars().all():
            await db.delete(policy)

        # Add new policies
        for insurance_in in patient_in.insurance_policies:
            db_insurance = PatientInsurance(
                patient_id=patient_id,
                insurance_type=insurance_in.insurance_type,
                insurance_number=insurance_in.insurance_number,
                member_name=insurance_in.member_name,
                expiry_date=insurance_in.expiry_date
            )
            db.add(db_insurance)

    await db.commit()
    await db.refresh(db_patient)

    return db_patient


async def detect_duplicates(
    db: AsyncSession,
    full_name: str,
    date_of_birth: datetime
) -> Optional[Patient]:
    """
    Detect potential duplicate patients by name and date of birth.

    Args:
        db: Database session
        full_name: Patient's full name
        date_of_birth: Patient's date of birth

    Returns:
        Patient object if duplicate found, None otherwise
    """
    result = await db.execute(
        select(Patient).filter(
            Patient.full_name == full_name,
            Patient.date_of_birth == date_of_birth,
            Patient.is_active == True
        )
    )
    return result.scalar_one_or_none()


async def generate_mrn(db: AsyncSession) -> str:
    """
    Generate a unique Medical Record Number (MRN).
    Format: RM-YYYY-XXXXX (where XXXXX is a sequential number)

    Args:
        db: Database session

    Returns:
        Unique MRN string
    """
    current_year = datetime.now().year

    # Find the highest sequence number for the current year
    mrn_pattern = f"RM-{current_year}-%"
    result = await db.execute(
        select(func.max(Patient.medical_record_number)).filter(
            Patient.medical_record_number.like(mrn_pattern)
        )
    )
    last_mrn = result.scalar()

    if last_mrn:
        # Extract sequence number from last MRN
        last_sequence = int(last_mrn.split('-')[-1])
        new_sequence = last_sequence + 1
    else:
        new_sequence = 1

    # Format: RM-YYYY-XXXXX (5-digit sequence with leading zeros)
    mrn = f"RM-{current_year}-{new_sequence:05d}"

    return mrn


async def deactivate_patient(db: AsyncSession, patient_id: int) -> Optional[Patient]:
    """
    Soft delete a patient by setting is_active to False.

    Args:
        db: Database session
        patient_id: Patient ID

    Returns:
        Deactivated patient object or None
    """
    db_patient = await get_patient_by_id(db, patient_id)
    if not db_patient:
        return None

    db_patient.is_active = False
    await db.commit()
    await db.refresh(db_patient)

    return db_patient


async def activate_patient(db: AsyncSession, patient_id: int) -> Optional[Patient]:
    """
    Reactivate a deactivated patient by setting is_active to True.

    Args:
        db: Database session
        patient_id: Patient ID

    Returns:
        Activated patient object or None
    """
    db_patient = await get_patient_by_id(db, patient_id)
    if not db_patient:
        return None

    db_patient.is_active = True
    await db.commit()
    await db.refresh(db_patient)

    return db_patient


async def count_patients(db: AsyncSession, is_active: bool = True) -> int:
    """
    Count total number of patients.

    Args:
        db: Database session
        is_active: Count only active patients

    Returns:
        Total count of patients
    """
    result = await db.execute(
        select(func.count(Patient.id)).filter(Patient.is_active == is_active)
    )
    return result.scalar()
