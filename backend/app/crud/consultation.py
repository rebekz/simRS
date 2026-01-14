"""Consultation Workflow CRUD operations for STORY-016: Doctor Consultation Workflow

This module provides CRUD operations for the doctor consultation workflow.
"""
from datetime import datetime, date, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.encounter import Encounter, Diagnosis, Treatment
from app.models.patient import Patient
from app.models.icd10 import ICD10Code
from app.models.allergy import Allergy
from app.models.problem_list import ProblemList


async def start_consultation(
    db: AsyncSession,
    patient_id: int,
    encounter_type: str,
    doctor_id: int,
    department: Optional[str] = None,
    chief_complaint: Optional[str] = None,
) -> Encounter:
    """
    Start a new consultation encounter.

    Creates a new encounter and returns the encounter ID.
    """
    encounter = Encounter(
        patient_id=patient_id,
        encounter_type=encounter_type,
        encounter_date=date.today(),
        department=department,
        doctor_id=doctor_id,
        chief_complaint=chief_complaint,
        status="active",
    )

    db.add(encounter)
    await db.commit()
    await db.refresh(encounter)

    return encounter


async def get_consultation_session(
    db: AsyncSession,
    encounter_id: int,
) -> Optional[Encounter]:
    """Get consultation session by ID."""
    stmt = select(Encounter).where(Encounter.id == encounter_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_patient_summary_for_consultation(
    db: AsyncSession,
    patient_id: int,
) -> Dict[str, Any]:
    """
    Get patient summary for consultation display.

    Includes demographics, insurance, last visit, chronic problems,
    active allergies, and current medications.
    """
    # Get patient
    patient_stmt = select(Patient).where(Patient.id == patient_id)
    patient_result = await db.execute(patient_stmt)
    patient = patient_result.scalar_one_or_none()

    if not patient:
        raise ValueError(f"Patient with ID {patient_id} not found")

    # Calculate age
    age = None
    if patient.date_of_birth:
        today = date.today()
        age = today.year - patient.date_of_birth.year - (
            (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
        )

    # Get last encounter
    encounter_stmt = (
        select(Encounter)
        .where(
            and_(
                Encounter.patient_id == patient_id,
                Encounter.status == "completed",
            )
        )
        .order_by(desc(Encounter.encounter_date))
        .limit(1)
    )
    encounter_result = await db.execute(encounter_stmt)
    last_encounter = encounter_result.scalar_one_or_none()

    # Get chronic problems
    problem_stmt = select(ProblemList).where(
        and_(
            ProblemList.patient_id == patient_id,
            ProblemList.status == "active",
            ProblemList.is_chronic == True,
        )
    )
    problem_result = await db.execute(problem_stmt)
    chronic_problems = problem_result.scalars().all()

    # Get active allergies (drug allergies)
    allergy_stmt = select(Allergy).where(
        and_(
            Allergy.patient_id == patient_id,
            Allergy.status == "active",
            Allergy.allergy_type == "drug",
        )
    )
    allergy_result = await db.execute(allergy_stmt)
    drug_allergies = allergy_result.scalars().all()

    # Get current treatments
    treatment_stmt = select(Treatment).where(
        and_(
            Treatment.encounter_id.in_(
                select(Encounter.id).where(
                    and_(
                        Encounter.patient_id == patient_id,
                        Encounter.status == "completed",
                    )
                )
            ),
            Treatment.is_active == True,
        )
    ).order_by(desc(Treatment.created_at)).limit(20)

    treatment_result = await db.execute(treatment_stmt)
    current_medications = treatment_result.scalars().all()

    return {
        "patient_id": patient.id,
        "medical_record_number": patient.medical_record_number,
        "full_name": patient.full_name,
        "date_of_birth": patient.date_of_birth,
        "age": age,
        "gender": patient.gender,
        "phone": patient.phone,
        "email": patient.email,
        "blood_type": patient.blood_type,
        "marital_status": patient.marital_status,
        "religion": patient.religion,
        "occupation": patient.occupation,
        "address": patient.address,
        "insurance_type": patient.insurances[0].insurance_type if patient.insurances else None,
        "insurance_number": patient.insurances[0].insurance_number if patient.insurances else None,
        "insurance_expiry": patient.insurances[0].expiry_date if patient.insurances else None,
        "last_visit_date": last_encounter.encounter_date if last_encounter else None,
        "chronic_problems": [p.problem_name for p in chronic_problems],
        "active_allergies": [a.allergen for a in drug_allergies],
        "current_medications": [t.treatment_name for t in current_medications],
    }


async def update_consultation_documentation(
    db: AsyncSession,
    encounter_id: int,
    chief_complaint: Optional[str] = None,
    present_illness: Optional[str] = None,
    physical_examination: Optional[str] = None,
    vital_signs: Optional[Dict[str, Any]] = None,
    clinical_note_id: Optional[int] = None,
) -> Optional[Encounter]:
    """Update consultation documentation."""
    stmt = select(Encounter).where(Encounter.id == encounter_id)
    result = await db.execute(stmt)
    encounter = result.scalar_one_or_none()

    if not encounter:
        return None

    if chief_complaint is not None:
        encounter.chief_complaint = chief_complaint
    if present_illness is not None:
        encounter.present_illness = present_illness
    if physical_examination is not None:
        encounter.physical_examination = physical_examination
    if vital_signs is not None:
        encounter.vital_signs = vital_signs
    # clinical_note_id would be stored separately if needed

    encounter.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(encounter)

    return encounter


async def add_diagnosis_to_consultation(
    db: AsyncSession,
    encounter_id: int,
    icd10_code_id: int,
    diagnosis_name: str,
    diagnosis_type: str = "primary",
    is_chronic: bool = False,
) -> Diagnosis:
    """Add diagnosis to consultation encounter."""
    # Verify encounter exists
    encounter_stmt = select(Encounter).where(Encounter.id == encounter_id)
    encounter_result = await db.execute(encounter_stmt)
    if not encounter_result.scalar_one_or_none():
        raise ValueError(f"Encounter with ID {encounter_id} not found")

    # Verify ICD-10 code exists
    icd10_stmt = select(ICD10Code).where(ICD10Code.id == icd10_code_id)
    icd10_result = await db.execute(icd10_stmt)
    icd10_code = icd10_result.scalar_one_or_none()
    if not icd10_code:
        raise ValueError(f"ICD-10 code with ID {icd10_code_id} not found")

    diagnosis = Diagnosis(
        encounter_id=encounter_id,
        icd_10_code=icd10_code.code,
        diagnosis_name=diagnosis_name,
        diagnosis_type=diagnosis_type,
        is_chronic=is_chronic,
    )

    db.add(diagnosis)
    await db.commit()
    await db.refresh(diagnosis)

    return diagnosis


async def add_treatment_to_consultation(
    db: AsyncSession,
    encounter_id: int,
    treatment_type: str,
    treatment_name: str,
    description: Optional[str] = None,
    dosage: Optional[str] = None,
    frequency: Optional[str] = None,
    duration: Optional[str] = None,
    route: Optional[str] = None,
    is_active: bool = True,
) -> Treatment:
    """Add treatment to consultation encounter."""
    # Verify encounter exists
    encounter_stmt = select(Encounter).where(Encounter.id == encounter_id)
    encounter_result = await db.execute(encounter_stmt)
    if not encounter_result.scalar_one_or_none():
        raise ValueError(f"Encounter with ID {encounter_id} not found")

    treatment = Treatment(
        encounter_id=encounter_id,
        treatment_type=treatment_type,
        treatment_name=treatment_name,
        description=description,
        dosage=dosage,
        frequency=frequency,
        duration=duration,
        route=route,
        is_active=is_active,
    )

    db.add(treatment)
    await db.commit()
    await db.refresh(treatment)

    return treatment


async def complete_consultation(
    db: AsyncSession,
    encounter_id: int,
    end_time: Optional[datetime] = None,
    notes: Optional[str] = None,
    follow_up_required: bool = False,
    follow_up_date: Optional[date] = None,
    next_appointment_date: Optional[date] = None,
    next_appointment_department: Optional[str] = None,
) -> Optional[Encounter]:
    """Complete a consultation encounter."""
    stmt = select(Encounter).options(
        selectinload(Encounter.diagnoses),
        selectinload(Encounter.treatments),
    ).where(Encounter.id == encounter_id)

    result = await db.execute(stmt)
    encounter = result.scalar_one_or_none()

    if not encounter:
        return None

    encounter.status = "completed"
    encounter.end_time = end_time or datetime.now(timezone.utc)
    encounter.notes = notes
    encounter.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(encounter)

    return encounter


async def get_active_consultations(
    db: AsyncSession,
    doctor_id: int,
    limit: int = 50,
) -> List[Encounter]:
    """Get active consultations for a doctor."""
    stmt = (
        select(Encounter)
        .where(
            and_(
                Encounter.doctor_id == doctor_id,
                Encounter.status == "active",
                Encounter.encounter_type == "outpatient",
            )
        )
        .order_by(Encounter.start_time)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_consultation_templates(
    db: AsyncSession,
    specialty: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Get consultation templates for auto-population.

    In production, these would be stored in a database table.
    For now, returns common templates.
    """
    templates = [
        {
            "id": "template-uhd-general",
            "name": "Poli Umum - Template Standar",
            "specialty": "general",
            "description": "Template konsultasi poli umum standar",
            "template": {
                "chief_complaint_template": "Keluhan utama: ",
                "present_illness_template": """Riwayat penyakit sekarang:
- Onset:
- Progres:
- Faktor pencetus:
- Gejala disertai:
- Gejala tidak disertai: """,
                "physical_exam_template": """Keadaan umum:
- Kesadaran: CM
- TTV: TD /mmHg, Nadi /menit, RR /menit, Suhu °C
- Kepala:
- Mata:
- Telinga:
- Hidung:
- Tenggorok:
- Leher:
- Thorax:
- Cor:
- Pulmo:
- Abdomen:
- Ekstremitas: """,
                "assessment_template": "Diagnosis kerja: ",
                "plan_template": """Rencana tatalaksana:
- Edukasi:
- Terapi:
- Tindak lanjut:""",
            },
        },
        {
            "id": "template-uhd-pedia",
            "name": "Poli Anak - Template Standar",
            "specialty": "pediatrics",
            "description": "Template konsultasi poli anak standar",
            "template": {
                "chief_complaint_template": "Keluhan utama (anak/orang tua): ",
                "present_illness_template": """Riwayat penyakit sekarang:
- Keluhan utama:
- Riwayat kelahiran:
- Riwayat tumbuh kembang:
- Riwayat imunisasi:
- Riwayat penyakit keluarga:""",
                "physical_exam_template": """Keadaan umum anak:
- Kesadaran: CM
- TTV (umur-appropriate): TD /mmHg, Nadi /menit, RR /menit, Suhu °C, BB kg, TB cm
- Kepala:
- Mata:
- Telinga:
- Hidung:
- Tenggorok:
- Leher:
- Thorax:
- Cor:
- Pulmo:
- Abdomen:
- Ekstremitas: """,
                "assessment_template": "Diagnosis kerja: ",
                "plan_template": """Rencana tatalaksana:
- Edukasi orang tua:
- Terapi:
- Tindak lanjut:""",
            },
        },
        {
            "id": "template-uhd-internal",
            "name": "Poli Penyakit Dalam - Template Standar",
            "specialty": "internal",
            "description": "Template konsultasi poli penyakit dalam standar",
            "template": {
                "chief_complaint_template": "Keluhan utama: ",
                "present_illness_template": """Anamnesis:
- Keluhan utama:
- Riwayat penyakit sekarang:
- Riwayat penyakit dahulu:
- Riwayat penyakit keluarga:
- Riwayat sosial:
- Riwayat alergi obat/makanan:""",
                "physical_exam_template": """Keadaan umum:
- Kesadaran: CM
- TTV: TD /mmHg, Nadi /menit, RR /menit, Suhu °C, BW kg
- Inspeksi:
- Palpasi:
- Perkusi:
- Auskultasi:""",
                "assessment_template": "Diagnosis kerja: ",
                "plan_template": """Rencana tatalaksana:
- Non-farmakologi:
- Farmakologi:
- Edukasi:
- Tindak lanjut:""",
            },
        },
    ]

    if specialty:
        templates = [t for t in templates if t["specialty"] == specialty]

    return templates


async def get_patient_education_materials(
    db: AsyncSession,
    icd10_codes: Optional[List[str]] = None,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    """
    Get patient education materials based on diagnoses.

    In production, these would be stored in a database table.
    For now, returns common materials.
    """
    # Common education materials
    materials = [
        {
            "id": "edu-001",
            "title": "Cara Mencuci Tangan dengan Benar",
            "description": "Edukasi tentang teknik mencuci tangan yang benar untuk mencegah infeksi",
            "icd10_codes": [],
            "content_type": "text",
            "content": "Langkah-langkah mencuci tangan:\n1. Basahi tangan dengan air bersih\n2. Gunakan sabun\n3. Gosok seluruh permukaan tangan selama 20 detik\n4. Bilas dengan air bersih\n5. Keringkan dengan handuk bersih",
            "language": "id",
        },
        {
            "id": "edu-002",
            "title": "Diet Rendah Garam untuk Hipertensi",
            "description": "Panduan diet rendah garam untuk pasien hipertensi",
            "icd10_codes": ["I10"],
            "content_type": "text",
            "content": "Panduan diet rendah garam:\n- Hindari makanan olahan dan kaleng\n- Gunakan rempah sebagai pengganti garam\n- Perbanyak buah dan sayuran\n- Batasi asupan garam maksimal 1 sendok teh per hari",
            "language": "id",
        },
        {
            "id": "edu-003",
            "title": "Manajemen Diabetes Melitus Tipe 2",
            "description": "Edukasi tentang pengelolaan diabetes untuk pasien dan keluarga",
            "icd10_codes": ["E11"],
            "content_type": "text",
            "content": "Pengelolaan diabetes:\n1. Kontrol gula darah secara teratur\n2. Konsumsi makanan bergizi seimbang\n3. Olahraga teratur 30 menit/hari\n4. Konsumsi obat sesuai anjuran dokter\n5. Periksa komplikasi secara rutin",
            "language": "id",
        },
    ]

    if icd10_codes:
        # Filter materials by ICD-10 codes
        filtered_materials = []
        for material in materials:
            if any(code in material["icd10_codes"] for code in icd10_codes):
                filtered_materials.append(material)
        materials = filtered_materials + [m for m in materials if not m["icd10_codes"]]

    return materials[:limit]
