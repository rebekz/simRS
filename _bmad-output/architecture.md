# SIMRS - System Architecture

**Version:** 1.0
**Date:** 2026-01-13
**Status:** Draft

---

## 1. Architecture Overview

### 1.1 Design Principles
- **Offline-first for 21% of Puskesmas** with limited connectivity
- **Security-first** (patient data protection under UU 27/2022 PDP Law)
- **Scalability** for small clinics to large hospitals
- **Modularity** for phased implementation
- **BPJS/SATUSEHAT integration readiness** (mandatory Indonesian requirements)
- **Indonesian localization** (language, currency, medical coding, geographic structure)

### 1.2 High-Level Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Browser  │  │  PWA App   │  │   Mobile   │           │
│  │ (Next.js)  │  │ (Service   │  │ (Optional) │           │
│  │            │  │  Worker)   │  │            │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS/WSS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │  FastAPI + Rate Limiting + CORS + Auth Middleware  │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│  │ Patient │ │ Medical │ │ Pharmacy│ │ Billing │         │
│  │ Service │ │ Record  │ │ Service │ │ Service │         │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │
│  │   Lab   │ │ Radiolo │ │   IGD   │ │  BPJS   │         │
│  │ Service │ │   gy     │ │ Service │ │ Service │         │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  PostgreSQL (Primary) + Redis (Cache/Sessions)     │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │  BPJS    │ │SATUSEHAT │ │  PCare   │ │ e-Katalog│     │
│  │  VClaim  │ │ FHIR R4  │ │  API     │ │  API     │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### 2.1 Backend
- **Framework:** FastAPI (Python 3.11+)
- **Async Runtime:** uvicorn + asyncio
- **ORM:** SQLAlchemy 2.0 (async)
- **Validation:** Pydantic v2
- **Authentication:** JWT + refresh tokens
- **Background Tasks:** Celery + Redis
- **API Documentation:** Auto-generated OpenAPI (Swagger/ReDoc)

### 2.2 Frontend
- **Framework:** Next.js 15 (React 19)
- **Styling:** Tailwind CSS + shadcn/ui
- **State:** Zustand + React Query
- **Forms:** React Hook Form + Zod
- **PWA:** next-pwa for offline capability
- **TypeScript:** Full type safety

### 2.3 Database
- **Primary:** PostgreSQL 16
- **Cache:** Redis 7
- **Search:** pg_trgm (built-in PostgreSQL)
- **Connection Pooling:** SQLAlchemy pool

### 2.4 Deployment
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Nginx
- **Process Manager:** systemd
- **One-command install:** `./install.sh`

---

## 3. Database Schema Design

### 3.1 Core Entities
```sql
-- Patient (Pasien)
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    medical_record_number VARCHAR(50) UNIQUE NOT NULL,
    nik VARCHAR(16) UNIQUE,  -- Indonesian ID
    name VARCHAR(200) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,  -- L/P
    blood_type VARCHAR(3),  -- A/B/O/AB/-
    address TEXT,
    province_code VARCHAR(2),  -- Indonesian geographic codes
    regency_code VARCHAR(4),
    district_code VARCHAR(6),
    village_code VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(100),
    occupation VARCHAR(100),
    education VARCHAR(50),  -- TS/S1-S3
    marital_status VARCHAR(20),  -- BELUM MENIKAH/MENIKAH/JANDA/DUDA
    religion VARCHAR(20),  -- Islam/Kristen/Katolik/Hindu/Buddha/Konghucu
    bpjs_number VARCHAR(30),  -- BPJS card number
    insurance_type VARCHAR(10),  -- BPJ/UMUM/ASURANSI
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- MedicalRecord (RekamMedis)
CREATE TABLE medical_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    encounter_id INTEGER REFERENCES encounters(id),
    record_type VARCHAR(50),  -- diagnosis/procedure/nursing_note
    code VARCHAR(20),  -- ICD-10 or procedure code
    description TEXT,
    severity VARCHAR(20),  -- primary/secondary
    recorded_by INTEGER REFERENCES users(id),
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Encounter (Kunjungan - Rawat Jalan/Inap/IGD)
CREATE TABLE encounters (
    id SERIAL PRIMARY KEY,
    encounter_number VARCHAR(50) UNIQUE NOT NULL,
    patient_id INTEGER REFERENCES patients(id),
    encounter_type VARCHAR(20) NOT NULL,  -- outpatient/inpatient/emergency
    status VARCHAR(20) NOT NULL,  -- planned/in-progress/finished/cancelled
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP,
    department_id INTEGER REFERENCES departments(id),
    doctor_id INTEGER REFERENCES users(id),
    room_id INTEGER REFERENCES rooms(id),
    bed_id INTEGER REFERENCES beds(id),
    bpjs_sep_number VARCHAR(30),  -- BPJS SEP reference
    created_at TIMESTAMP DEFAULT NOW()
);

-- User (Pengguna)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- doctor/nurse/pharmacist/receptionist/admin
    department_id INTEGER REFERENCES departments(id),
    license_number VARCHAR(50),  -- Medical license (SIP)
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Staff (Staf - Dokter/Perawat)
CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    staff_type VARCHAR(50) NOT NULL,  -- doctor/nurse/midwife/pharmacist
    specialty VARCHAR(100),  -- Poli spesialisasi
    license_number VARCHAR(50),
    nip VARCHAR(50),  -- Nomor Induk Pegawai
    employment_type VARCHAR(20),  -- permanent/contract/ honorary
    created_at TIMESTAMP DEFAULT NOW()
);

-- Department (Departemen/Poliklinik)
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    department_type VARCHAR(50),  -- clinical/administrative/support
    bpjs_code VARCHAR(10),  -- BPJS poli code mapping
    is_active BOOLEAN DEFAULT TRUE
);

-- Room/Bed (Ruang/Tempat Tidur)
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    room_class VARCHAR(10),  -- 1/2/3/VVIP
    bed_capacity INTEGER,
    hourly_rate DECIMAL(15,2),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE beds (
    id SERIAL PRIMARY KEY,
    room_id INTEGER REFERENCES rooms(id),
    bed_number VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'available',  -- available/occupied/maintenance
    current_encounter_id INTEGER REFERENCES encounters(id)
);

-- Medication (Obat)
CREATE TABLE medications (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    generic_name VARCHAR(200),
    strength VARCHAR(50),
    dosage_form VARCHAR(50),  -- tablet/capsule/syrup/injection
    bpjs_code VARCHAR(50),  -- BPJS drug code
    atc_code VARCHAR(20),  -- Anatomical Therapeutic Chemical
    is_active BOOLEAN DEFAULT TRUE
);

-- Procedure (Tindakan)
CREATE TABLE procedures (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    procedure_type VARCHAR(50),  -- consultation/surgery/diagnostic
    icd_9_cm_code VARCHAR(10),
    bpjs_tarif_id VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE
);

-- LabResult (HasilLab)
CREATE TABLE lab_results (
    id SERIAL PRIMARY KEY,
    encounter_id INTEGER REFERENCES encounters(id),
    test_code VARCHAR(50),
    test_name VARCHAR(200),
    loinc_code VARCHAR(10),  -- LOINC terminology
    result_value TEXT,
    unit VARCHAR(50),
    reference_range VARCHAR(100),
    abnormal_flag BOOLEAN,
    performed_at TIMESTAMP,
    performed_by INTEGER REFERENCES users(id),
    verified_by INTEGER REFERENCES users(id)
);

-- RadiologyExam (PemeriksaanRadiologi)
CREATE TABLE radiology_exams (
    id SERIAL PRIMARY KEY,
    encounter_id INTEGER REFERENCES encounters(id),
    exam_code VARCHAR(50),
    exam_name VARCHAR(200),
    modality VARCHAR(20),  -- XRAY/CT/MRI/US
    body_part VARCHAR(100),
    dicom_study_uid VARCHAR(100),
    report_text TEXT,
    performed_at TIMESTAMP,
    radiologist_id INTEGER REFERENCES users(id)
);
```

### 3.2 BPJS-Specific Tables
```sql
-- BPJS SEP (Surat Eligibility Peserta)
CREATE TABLE bpjs_sep (
    id SERIAL PRIMARY KEY,
    sep_number VARCHAR(30) UNIQUE NOT NULL,
    encounter_id INTEGER REFERENCES encounters(id) UNIQUE,
    bpjs_card_number VARCHAR(30),
    referral_number VARCHAR(50),
    referring_facility_code VARCHAR(20),
    service_type VARCHAR(10),  -- 1=Rawat Inap, 2=Rawat Jalan
    initial_diagnosis_code VARCHAR(10),  -- ICD-10
    target_poli_code VARCHAR(10),
    room_class VARCHAR(10),
    accident_indicator VARCHAR(1),  -- 0-3
    sep_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- BPJS Antrian (Queue Management)
CREATE TABLE bpjs_queue (
    id SERIAL PRIMARY KEY,
    encounter_id INTEGER REFERENCES encounters(id),
    booking_code VARCHAR(50) UNIQUE,
    queue_number INTEGER,
    queue_date DATE,
    poli_code VARCHAR(10),
    doctor_id INTEGER REFERENCES users(id),
    status VARCHAR(20),  -- booked/check-in/called/finished/missed
    estimated_time TIME
);

-- BPJS Referensi (Reference Data)
CREATE TABLE bpjs_reference (
    id SERIAL PRIMARY KEY,
    reference_type VARCHAR(50),  -- poli/diagnosa/faskes/dokter
    code VARCHAR(50),
    name VARCHAR(200),
    bpjs_data JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 3.3 Audit & Security
```sql
-- AuditLog (Log Aktivitas)
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id INTEGER REFERENCES users(id),
    username VARCHAR(100),
    action VARCHAR(50),  -- CREATE/READ/UPDATE/DELETE
    resource_type VARCHAR(50),  -- Patient/Diagnosis/Prescription
    resource_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    failure_reason TEXT,
    additional_data JSONB
);

-- Session (Sesi Pengguna)
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token_hash VARCHAR(255) UNIQUE,
    refresh_token_hash VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    is_revoked BOOLEAN DEFAULT FALSE
);

-- Permission (Izin Akses)
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,  -- create/read/update/delete
    granted BOOLEAN DEFAULT TRUE
);
```

---

## 4. API Design

### 4.1 RESTful Conventions
- Resource-based URLs: `/api/v1/patients/{id}`
- HTTP verbs: GET, POST, PUT, PATCH, DELETE
- Status codes: proper 2xx, 4xx, 5xx usage
- Pagination: cursor-based for large datasets

### 4.2 Authentication Flow
```
1. Login POST /api/v1/auth/login
   Body: {username, password}
   Response: {access_token, refresh_token, expires_in}

2. Subsequent: Bearer token in Authorization header
   Header: Authorization: Bearer {access_token}

3. Refresh: POST /api/v1/auth/refresh
   Body: {refresh_token}
   Response: {access_token, refresh_token}

4. Logout: POST /api/v1/auth/logout
   Header: Authorization: Bearer {access_token}
   Response: {message: "Logged out successfully"}
```

### 4.3 Key Endpoints by Module

**Authentication:**
```
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
```

**Patient Registration:**
```
POST   /api/v1/patients                    # Create new patient
GET    /api/v1/patients                    # List with search & pagination
GET    /api/v1/patients/{id}               # Get patient details
PUT    /api/v1/patients/{id}               # Update patient
DELETE /api/v1/patients/{id}               # Delete patient (soft delete)
GET    /api/v1/patients/{id}/encounters    # Patient visit history
```

**Encounters (Kunjungan):**
```
POST   /api/v1/encounters                   # Register patient visit
GET    /api/v1/encounters                   # List encounters
GET    /api/v1/encounters/{id}              # Encounter details
PUT    /api/v1/encounters/{id}              # Update encounter
PATCH  /api/v1/encounters/{id}/status       # Update status (admit/discharge)
GET    /api/v1/encounters/{id}/medical-record  # Full medical record
```

**Medical Records:**
```
GET    /api/v1/encounters/{id}/diagnoses   # Patient diagnoses
POST   /api/v1/encounters/{id}/diagnoses   # Add diagnosis (ICD-10)
PUT    /api/v1/encounters/{id}/diagnoses/{code}  # Update diagnosis
DELETE /api/v1/encounters/{id}/diagnoses/{code}  # Remove diagnosis

GET    /api/v1/patients/{id}/allergies     # Patient allergies
POST   /api/v1/patients/{id}/allergies     # Add allergy
DELETE /api/v1/patients/{id}/allergies/{id}  # Remove allergy

GET    /api/v1/encounters/{id}/vitals      # Vital signs
POST   /api/v1/encounters/{id}/vitals      # Add vitals
```

**Prescriptions (Resep):**
```
POST   /api/v1/encounters/{id}/prescriptions    # Create prescription
GET    /api/v1/encounters/{id}/prescriptions    # List prescriptions
GET    /api/v1/prescriptions/{id}               # Prescription details
PUT    /api/v1/prescriptions/{id}/status        # Update status
GET    /api/v1/prescriptions/{id}/dispense      # Dispensing info
POST   /api/v1/prescriptions/{id}/dispense      # Dispense medication
```

**Laboratory:**
```
POST   /api/v1/encounters/{id}/lab-orders       # Order lab test
GET    /api/v1/encounters/{id}/lab-orders       # List lab orders
GET    /api/v1/lab-orders/{id}                  # Lab order details
PUT    /api/v1/lab-orders/{id}/results          # Enter results
POST   /api/v1/lab-orders/{id}/verify           # Verify results
```

**Radiology:**
```
POST   /api/v1/encounters/{id}/radiology-orders # Order radiology exam
GET    /api/v1/encounters/{id}/radiology-orders # List radiology orders
GET    /api/v1/radiology-orders/{id}            # Exam details
PUT    /api/v1/radiology-orders/{id}/report     # Enter report
POST   /api/v1/radiology-orders/{id}/verify     # Verify report
```

**BPJS Integration:**
```
POST   /api/v1/bpjs/sep                        # Create SEP
GET    /api/v1/bpjs/sep/{noSep}                # Query SEP
PUT    /api/v1/bpjs/sep/{noSep}                # Update SEP
DELETE /api/v1/bpjs/sep/{noSep}                # Delete SEP
GET    /api/v1/bpjs/peserta/nik/{nik}          # Check eligibility by NIK
GET    /api/v1/bpjs/peserta/kartu/{noKartu}     # Check eligibility by card
GET    /api/v1/bpjs/rujukan/{noRujukan}         # Get referral info
POST   /api/v1/bpjs/antrian                     # Register queue
PUT    /api/v1/bpjs/antrian/{kodeBooking}       # Update queue
```

**SATUSEHAT Integration:**
```
POST   /api/v1/satusehat/patients               # Sync patient to SATUSEHAT
GET    /api/v1/satusehat/patients/{id}          # Get patient from SATUSEHAT
POST   /api/v1/satusehat/encounters             # Sync encounter
POST   /api/v1/satusehat/conditions             # Sync diagnosis (FHIR Condition)
POST   /api/v1/satusehat/observations           # Sync lab results (FHIR Observation)
```

**Billing:**
```
POST   /api/v1/encounters/{id}/bills           # Create bill
GET    /api/v1/encounters/{id}/bills           # Get bills
PUT    /api/v1/bills/{id}                       # Update bill
POST   /api/v1/bills/{id}/items                 # Add bill item
GET    /api/v1/bills/{id}/calculate             # Calculate total
POST   /api/v1/bills/{id}/payment               # Process payment
```

**Queue (Antrian):**
```
POST   /api/v1/queues                          # Register queue
GET    /api/v1/queues                          # List queues
PUT    /api/v1/queues/{id}/status              # Update queue status
GET    /api/v1/queues/active                   # Get active queues
DELETE /api/v1/queues/{id}                     # Cancel queue
```

---

## 5. Security Architecture

### 5.1 Authentication & Authorization
- **RBAC:** Role-based access control
- **Roles:** Admin, Dokter, Perawat, Apoteker, Kasir, Pendaftaran, Keperawatan, Farmasi
- **Permissions:** Granular per-module permissions
- **Audit:** All actions logged with user + timestamp + IP

### 5.2 Data Protection
- **Encryption in transit:** TLS 1.3
- **Encryption at rest:** PostgreSQL transparent encryption (pgcrypto)
- **Sensitive data hashing:** passwords, NIK
- **Field-level encryption:** extra-sensitive fields (psychiatry, HIV)

### 5.3 Compliance
- **UU 27/2022 PDP Law:** Indonesia's data protection law
- **BPJS data handling guidelines**
- **Audit trail retention:** minimum 6 years (aligned with medical records)
- **Breach notification:** within 3×24 hours

### 5.4 Role Definitions
```python
class Permission(str, Enum):
    # Patient records
    PATIENT_READ = "patient:read"
    PATIENT_WRITE = "patient:write"
    PATIENT_DELETE = "patient:delete"
    PATIENT_EXPORT = "patient:export"

    # Medical records
    DIAGNOSIS_READ = "diagnosis:read"
    DIAGNOSIS_WRITE = "diagnosis:write"
    PRESCRIPTION_READ = "prescription:read"
    PRESCRIPTION_WRITE = "prescription:write"
    VITALS_READ = "vitals:read"
    VITALS_WRITE = "vitals:write"

    # Clinical services
    LAB_READ = "lab:read"
    LAB_WRITE = "lab:write"
    LAB_VERIFY = "lab:verify"
    RADIOLOGY_READ = "radiology:read"
    RADIOLOGY_WRITE = "radiology:write"
    RADIOLOGY_VERIFY = "radiology:verify"

    # Pharmacy
    PHARMACY_DISPENSE = "pharmacy:dispense"
    PHARMACY_INVENTORY = "pharmacy:inventory"

    # Billing
    BILLING_READ = "billing:read"
    BILLING_WRITE = "billing:write"
    BILLING_APPROVE = "billing:approve"

    # Administration
    USER_MANAGE = "user:manage"
    CONFIG_EDIT = "config:edit"
    AUDIT_LOG_VIEW = "audit:read"
    REPORT_VIEW = "report:read"

class Role(str, Enum):
    ADMIN = "admin"
    DOKTER = "doctor"
    PERAWAT = "nurse"
    APOTEKER = "pharmacist"
    KASIR = "cashier"
    PENDAFTARAN = "receptionist"
    KEPERAWATAN = "nursing_manager"
    FARMASI_MANAGER = "pharmacy_manager"
    SUPERADMIN = "superadmin"

ROLE_PERMISSIONS = {
    Role.DOKTER: [
        Permission.PATIENT_READ,
        Permission.PATIENT_WRITE,
        Permission.DIAGNOSIS_READ,
        Permission.DIAGNOSIS_WRITE,
        Permission.PRESCRIPTION_READ,
        Permission.PRESCRIPTION_WRITE,
        Permission.VITALS_READ,
        Permission.VITALS_WRITE,
        Permission.LAB_READ,
        Permission.RADIOLOGY_READ,
    ],
    Role.PERAWAT: [
        Permission.PATIENT_READ,
        Permission.VITALS_READ,
        Permission.VITALS_WRITE,
        Permission.DIAGNOSIS_READ,
        Permission.PRESCRIPTION_READ,
        Permission.LAB_READ,
        Permission.RADIOLOGY_READ,
    ],
    Role.APOTEKER: [
        Permission.PRESCRIPTION_READ,
        Permission.PRESCRIPTION_WRITE,
        Permission.PHARMACY_DISPENSE,
        Permission.PHARMACY_INVENTORY,
    ],
    Role.PENDAFTARAN: [
        Permission.PATIENT_READ,
        Permission.PATIENT_WRITE,
    ],
    Role.KASIR: [
        Permission.BILLING_READ,
        Permission.BILLING_WRITE,
        Permission.PATIENT_READ,
    ],
    Role.ADMIN: [
        Permission.USER_MANAGE,
        Permission.CONFIG_EDIT,
        Permission.AUDIT_LOG_VIEW,
        Permission.REPORT_VIEW,
    ],
    Role.SUPERADMIN: [
        # All permissions
    ],
}
```

---

## 6. Integration Patterns

### 6.1 BPJS VClaim API
```python
class BPJSVClaimClient:
    """Async client for BPJS VClaim API"""

    def __init__(self, cons_id: str, secret_key: str, user_key: str):
        self.cons_id = cons_id
        self.secret_key = secret_key
        self.user_key = user_key
        self.base_url = "https://api.bpjs-kesehatan.go.id/vclaim-rest"

    def _generate_signature(self) -> tuple[str, str, str]:
        """Generate BPJS signature authentication"""
        timestamp = str(int(time.time()))
        data = f"{self.cons_id}&{timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).digest().hex()
        return timestamp, signature

    def _get_headers(self) -> dict:
        """Get request headers with authentication"""
        timestamp, signature = self._generate_signature()
        return {
            "X-cons-id": self.cons_id,
            "X-timestamp": timestamp,
            "X-signature": signature,
            "user_key": self.user_key,
            "Content-Type": "application/json"
        }

    async def create_sep(self, sep_data: dict) -> dict:
        """Create SEP (Surat Eligibilitas Peserta)"""
        url = f"{self.base_url}/SEP"
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=sep_data, headers=headers)
            return response.json()

    async def update_sep(self, sep_data: dict) -> dict:
        """Update existing SEP"""
        url = f"{self.base_url}/SEP/Update"
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.put(url, json=sep_data, headers=headers)
            return response.json()

    async def delete_sep(self, sep_number: str) -> dict:
        """Delete/cancel SEP"""
        url = f"{self.base_url}/SEP/Delete"
        headers = self._get_headers()
        data = {"request": {"t_sep": {"noSep": sep_number, "user": "SYSTEM"}}}
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, json=data, headers=headers)
            return response.json()

    async def query_sep(self, sep_number: str) -> dict:
        """Query SEP by number"""
        url = f"{self.base_url}/SEP/{sep_number}"
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.json()

    async def check_eligibility_by_nik(self, nik: str) -> dict:
        """Check patient eligibility by NIK"""
        url = f"{self.base_url}/Peserta/nik/{nik}"
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.json()

    async def get_referral(self, referral_number: str) -> dict:
        """Get referral (rujukan) information"""
        url = f"{self.base_url}/Rujukan/{referral_number}"
        headers = self._get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            return response.json()
```

### 6.2 SATUSEHAT FHIR R4
```python
class SatuSehatClient:
    """FHIR client for SATUSEHAT platform integration"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api-satusehat.kemkes.go.id/fhir-r4/v1"
        self.auth_url = "https://api-satusehat.kemkes.go.id/oauth2/v1"
        self.access_token = None

    async def get_token(self) -> str:
        """Get OAuth 2.0 access token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.auth_url}/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                }
            )
            self.access_token = response.json()["access_token"]
            return self.access_token

    async def upload_patient(self, patient_data: dict) -> dict:
        """Upload patient to SATUSEHAT (FHIR Patient resource)"""
        if not self.access_token:
            await self.get_token()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/fhir+json"
        }

        fhir_patient = {
            "resourceType": "Patient",
            "identifier": [{
                "use": "official",
                "system": "https://fhir.kemkes.go.id/id/nik",
                "value": patient_data["nik"]
            }],
            "name": [{"text": patient_data["name"]}],
            "gender": patient_data["gender"],
            "birthDate": patient_data["date_of_birth"]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/Patient",
                json=fhir_patient,
                headers=headers
            )
            return response.json()

    async def upload_condition(self, encounter_id: str, diagnosis: dict) -> dict:
        """Upload diagnosis to SATUSEHAT (FHIR Condition resource)"""
        if not self.access_token:
            await self.get_token()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/fhir+json"
        }

        fhir_condition = {
            "resourceType": "Condition",
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active"
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed"
                }]
            },
            "code": {
                "coding": [{
                    "system": "http://hl7.org/fhir/sid/icd-10",
                    "code": diagnosis["code"],
                    "display": diagnosis["description"]
                }]
            },
            "subject": {
                "reference": f"Patient/{diagnosis['patient_id']}"
            },
            "encounter": {
                "reference": f"Encounter/{encounter_id}"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/Condition",
                json=fhir_condition,
                headers=headers
            )
            return response.json()

    async def upload_observation(self, lab_result: dict) -> dict:
        """Upload lab result to SATUSEHAT (FHIR Observation resource)"""
        if not self.access_token:
            await self.get_token()

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/fhir+json"
        }

        fhir_observation = {
            "resourceType": "Observation",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": lab_result["loinc_code"],
                    "display": lab_result["test_name"]
                }]
            },
            "subject": {
                "reference": f"Patient/{lab_result['patient_id']}"
            },
            "encounter": {
                "reference": f"Encounter/{lab_result['encounter_id']}"
            },
            "valueQuantity": {
                "value": lab_result["result_value"],
                "unit": lab_result["unit"]
            },
            "referenceRange": [{
                "text": lab_result["reference_range"]
            }]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/Observation",
                json=fhir_observation,
                headers=headers
            )
            return response.json()
```

### 6.3 Offline Sync Strategy
```
1. Service Worker intercepts API calls when offline
2. IndexedDB stores pending mutations
3. Background sync when connection restored
4. Conflict resolution: last-write-wins with timestamp
5. Queue-based synchronization with retry logic
```

**Service Worker Implementation:**
```javascript
// Service worker for offline capability
const CACHE_NAME = 'simrs-v1';
const QUEUE_NAME = 'simrs-sync-queue';

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll([
                '/',
                '/offline.html',
                '/manifest.json',
                '/static/css/main.css',
                '/static/js/main.js'
            ]);
        })
    );
});

self.addEventListener('fetch', (event) => {
    // Network-first for API, cache-first for static
    if (event.request.url.includes('/api/')) {
        event.respondWith(networkFirst(event.request));
    } else {
        event.respondWith(cacheFirst(event.request));
    }
});

async function networkFirst(request) {
    try {
        const response = await fetch(request);
        return response;
    } catch (error) {
        // Offline - queue request for later
        await queueRequest(request);
        return new Response(JSON.stringify({ offline: true }), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

async function queueRequest(request) {
    const queue = await openDB();
    await queue.add(QUEUE_NAME, {
        request: request.clone(),
        timestamp: Date.now()
    });
}

// Background sync when online
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-queue') {
        event.waitUntil(processQueue());
    }
});

async function processQueue() {
    const queue = await openDB();
    const items = await queue.getAll(QUEUE_NAME);

    for (const item of items) {
        try {
            await fetch(item.request);
            await queue.delete(QUEUE_NAME, item.id);
        } catch (error) {
            console.error('Sync failed for item:', item);
        }
    }
}
```

---

## 7. Scalability & Performance

### 7.1 Caching Strategy
- **Redis** for session data (15-minute TTL)
- **Redis** for frequently accessed reference data (ICD-10, medications: 1-hour TTL)
- **HTTP caching** headers for static assets
- **Service Worker cache** for PWA assets

### 7.2 Database Optimization
- **Proper indexing** on foreign keys and search fields
- **Connection pooling** (SQLAlchemy pool: 20 connections)
- **Read replicas** for reporting (optional scaling)
- **Partitioning** for large historical tables (by year)

### 7.3 Performance Targets
- **API response:** < 200ms (p95)
- **Page load:** < 2s (3G connection)
- **Offline support:** 24+ hours cached data
- **Queue processing:** < 5 minutes sync when online

### 7.4 Database Indexing Strategy
```sql
-- Patient search optimization
CREATE INDEX idx_patients_nik ON patients(nik) WHERE nik IS NOT NULL;
CREATE INDEX idx_patients_name_trgm ON patients USING gin(name gin_trgm_ops);
CREATE INDEX idx_patients_bpjs ON patients(bpjs_number) WHERE bpjs_number IS NOT NULL;

-- Encounter optimization
CREATE INDEX idx_encounters_patient ON encounters(patient_id);
CREATE INDEX idx_encounters_type_status ON encounters(encounter_type, status);
CREATE INDEX idx_encounters_dates ON encounters(start_datetime, end_datetime);

-- Medical record search
CREATE INDEX idx_medical_records_patient_code ON medical_records(patient_id, record_type, code);
CREATE INDEX idx_medical_records_encounter ON medical_records(encounter_id);

-- BPJS optimization
CREATE INDEX idx_bpjs_sep_encounter ON bpjs_sep(encounter_id);
CREATE INDEX idx_bpjs_sep_number ON bpjs_sep(sep_number);
CREATE INDEX idx_bpjs_queue_date ON bpjs_queues(queue_date, status);

-- Audit log retention
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_user_resource ON audit_logs(user_id, resource_type, timestamp);
```

---

## 8. Deployment Architecture

### 8.1 Docker Compose Setup
```yaml
version: '3.8'

services:
  # Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  # Frontend (Next.js)
  frontend:
    image: simrs-frontend:${VERSION}
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=https://localhost/api
      - NEXT_PUBLIC_OFFLINE_MODE=true
    restart: unless-stopped

  # Backend (FastAPI)
  backend:
    image: simrs-backend:${VERSION}
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://simrs:${DB_PASSWORD}@db:5432/simrs
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - BPJS_CONS_ID=${BPJS_CONS_ID}
      - BPJS_SECRET_KEY=${BPJS_SECRET_KEY}
      - BPJS_USER_KEY=${BPJS_USER_KEY}
      - SATUSEHAT_CLIENT_ID=${SATUSEHAT_CLIENT_ID}
      - SATUSEHAT_CLIENT_SECRET=${SATUSEHAT_CLIENT_SECRET}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL database
  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=simrs
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=simrs
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U simrs"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis (cache + queue)
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Celery worker (background tasks)
  celery-worker:
    image: simrs-backend:${VERSION}
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://simrs:${DB_PASSWORD}@db:5432/simrs
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    restart: unless-stopped

  # MinIO (object storage)
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_USER}
      - MINIO_ROOT_PASSWORD=${MINIO_PASSWORD}
    volumes:
      - minio-data:/data
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
  minio-data:
```

### 8.2 Server Requirements (Minimum)
- **CPU:** 4 cores
- **RAM:** 8 GB (16 GB recommended for medium hospitals)
- **Storage:** 100 GB SSD (2 TB recommended for large hospitals)
- **OS:** Linux (Ubuntu 22.04 LTS recommended)
- **Network:** Gigabit Ethernet
- **Power:** UPS (uninterruptible power supply)

### 8.3 One-Command Installation
```bash
#!/bin/bash
# install.sh - One-command SIMRS installation

echo "Installing SIMRS..."

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com | bash
    usermod -aG docker $USER
fi

# Clone repository
git clone https://github.com/your-org/simrs.git
cd simrs

# Copy environment template
cp .env.example .env

# Prompt for configuration
read -p "Enter hospital name: " HOSPITAL_NAME
read -p "Enter database password: " DB_PASSWORD
read -p "Enter BPJS Cons ID: " BPJS_CONS_ID
read -p "Enter BPJS Secret Key: " BPJS_SECRET_KEY
read -p "Enter BPJS User Key: " BPJS_USER_KEY

# Update .env file
sed -i "s/HOSPITAL_NAME=.*/HOSPITAL_NAME=$HOSPITAL_NAME/" .env
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
sed -i "s/BPJS_CONS_ID=.*/BPJS_CONS_ID=$BPJS_CONS_ID/" .env
sed -i "s/BPJS_SECRET_KEY=.*/BPJS_SECRET_KEY=$BPJS_SECRET_KEY/" .env
sed -i "s/BPJS_USER_KEY=.*/BPJS_USER_KEY=$BPJS_USER_KEY/" .env

# Generate secrets
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env

# Build and start services
docker-compose build
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create admin user
docker-compose exec backend python -c "
from app.models import User
from app.database import SessionLocal
db = SessionLocal()
admin = User(
    username='admin',
    hashed_password='$2b$12$...',
    full_name='Administrator',
    role='admin'
)
db.add(admin)
db.commit()
"

echo "SIMRS installation complete!"
echo "Access at: http://localhost"
echo "Default admin: admin/admin123"
echo "Please change admin password immediately."
```

---

## 9. Monitoring & Observability

### 9.1 Application Logging
- **Structured JSON logging** (python-json-logger)
- **Log levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log rotation:** Daily with 30-day retention
- **Centralized logging:** Optional ELK stack integration

### 9.2 Health Checks
```
GET /api/v1/health              # Service health
GET /api/v1/health/db           # Database connectivity
GET /api/v1/health/redis        # Cache connectivity
GET /api/v1/health/bpjs         # BPJS API connectivity
GET /api/v1/health/satusehat    # SATUSEHAT API connectivity
```

### 9.3 Metrics (Optional Enhancement)
- **Request rate:** requests per second by endpoint
- **Error rate:** 4xx, 5xx percentages
- **Latency:** p50, p95, p99 response times
- **Database performance:** query duration, connection pool usage
- **Cache performance:** hit/miss ratio
- **Queue depth:** background task queue length

### 9.4 Alerting
- **Service down:** Immediate alert
- **High error rate:** Alert if > 5% for 5 minutes
- **Slow queries:** Alert if > 1s for p95
- **Disk space:** Alert if > 80% used
- **BPJS API failures:** Alert if > 10% failure rate

---

## 10. Development Architecture

### 10.1 Project Structure
```
simrs/
├── backend/
│   ├── app/
│   │   ├── api/                    # API routes
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── patients.py
│   │   │   │   ├── encounters.py
│   │   │   │   ├── medical_records.py
│   │   │   │   ├── prescriptions.py
│   │   │   │   ├── laboratory.py
│   │   │   │   ├── radiology.py
│   │   │   │   ├── billing.py
│   │   │   │   ├── bpjs.py
│   │   │   │   └── satusehat.py
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── patient.py
│   │   │   ├── encounter.py
│   │   │   ├── medical_record.py
│   │   │   ├── user.py
│   │   │   └── bpjs.py
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── patient.py
│   │   │   ├── encounter.py
│   │   │   └── ...
│   │   ├── services/               # Business logic
│   │   │   ├── patient_service.py
│   │   │   ├── encounter_service.py
│   │   │   ├── bpjs_service.py
│   │   │   └── satusehat_service.py
│   │   ├── core/                   # Config, security
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   ├── integrations/           # External integrations
│   │   │   ├── bpjs_client.py
│   │   │   └── satusehat_client.py
│   │   ├── tasks/                  # Celery tasks
│   │   │   └── background_tasks.py
│   │   ├── database.py             # DB connection
│   │   └── main.py                 # FastAPI app
│   ├── tests/
│   │   ├── api/
│   │   ├── services/
│   │   └── conftest.py
│   ├── alembic/                    # Database migrations
│   │   └── versions/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                        # Next.js app directory
│   │   ├── (auth)/
│   │   │   └── login/
│   │   ├── dashboard/
│   │   ├── patients/
│   │   ├── encounters/
│   │   ├── medical-records/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                     # shadcn/ui components
│   │   ├── patients/
│   │   ├── encounters/
│   │   └── forms/
│   ├── lib/
│   │   ├── api.ts                  # API client
│   │   ├── auth.ts                 # Auth utilities
│   │   └── utils.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   └── useOffline.ts
│   ├── styles/
│   │   └── globals.css
│   ├── public/
│   │   └── icons/
│   ├── Dockerfile
│   ├── next.config.js
│   ├── package.json
│   └── tailwind.config.ts
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── nginx/
│   ├── nginx.conf
│   └── ssl/
├── scripts/
│   ├── install.sh                  # One-command install
│   ├── backup.sh                   # Backup script
│   └── update.sh                   # Update script
├── .env.example
├── README.md
└── docker-compose.yml
```

### 10.2 Testing Strategy
- **Backend:** pytest with async support
- **Frontend:** Vitest + React Testing Library
- **E2E:** Playwright
- **API integration:** Mocked BPJS/SATUSEHAT responses
- **Performance:** Locust for load testing

---

## 11. Indonesian Localization

### 11.1 Language Support
- **UI Language:** Indonesian (Bahasa Indonesia)
- **Database:** UTF-8 encoding
- **Date Format:** DD-MM-YYYY (display), YYYY-MM-DD (storage)
- **Currency:** IDR (Rupiah) - Rp 1.000.000 (dots as thousands separator)
- **Number Format:** No decimal places for currency

### 11.2 Medical Coding Standards
- **ICD-10:** Diagnosis coding (Indonesian adaptation)
- **ICD-9-CM:** Procedure coding
- **LOINC:** Laboratory tests (SATUSEHAT requirement)
- **INA-CBG:** DRG-like system for BPJS reimbursement
- **ATC:** Drug classification (Anatomical Therapeutic Chemical)

### 11.3 Geographic Structure
```python
# Indonesian administrative divisions (BPS codes)
PROVINCES = {
    "11": "Aceh",
    "12": "Sumatera Utara",
    "13": "Sumatera Barat",
    "14": "Riau",
    "15": "Jambi",
    "16": "Sumatera Selatan",
    "17": "Bengkulu",
    "18": "Lampung",
    "19": "Kepulauan Bangka Belitung",
    "21": "Kepulauan Riau",
    "31": "DKI Jakarta",
    "32": "Jawa Barat",
    "33": "Jawa Tengah",
    "34": "DI Yogyakarta",
    "35": "Jawa Timur",
    "36": "Banten",
    "51": "Bali",
    "52": "Nusa Tenggara Barat",
    "53": "Nusa Tenggara Timur",
    "61": "Kalimantan Barat",
    "62": "Kalimantan Tengah",
    "63": "Kalimantan Selatan",
    "64": "Kalimantan Timur",
    "65": "Kalimantan Utara",
    "71": "Sulawesi Utara",
    "72": "Sulawesi Tengah",
    "73": "Sulawesi Selatan",
    "74": "Sulawesi Tenggara",
    "75": "Gorontalo",
    "76": "Sulawesi Barat",
    "81": "Maluku",
    "82": "Maluku Utara",
    "91": "Papua",
    "92": "Papua Barat",
    "94": "Papua Selatan",
    "93": "Papua Tengah",
    "95": "Papua Pegunungan"
}
```

### 11.4 Demographic Fields
```python
# Indonesian-specific demographics
RELIGIONS = [
    "Islam",
    "Kristen",
    "Katolik",
    "Hindu",
    "Buddha",
    "Konghucu"
]

MARITAL_STATUS = [
    "BELUM MENIKAH",  # Never married
    "MENIKAH",        # Married
    "JANDA",          # Widow
    "DUDA"            # Widower
]

EDUCATION = [
    "TS",     # Tidak Sekolah (No school)
    "TK",     # Kindergarten
    "SD",     # Primary school
    "SMP",    # Junior high
    "SMA",    # Senior high
    "D1", "D2", "D3", "D4",  # Diplomas
    "S1",     # Bachelor
    "S2",     # Master
    "S3"      # Doctorate
]

BLOOD_TYPES = ["A", "B", "O", "AB", "-"]  # - = Unknown
```

---

## 12. BPJS Integration Requirements

### 12.1 BPJS API Endpoints

**VClaim API (Primary):**
```
Base URL: https://api.bpjs-kesehatan.go.id/vclaim-rest

Key Services:
- POST   /SEP                     # Create SEP
- PUT    /SEP/Update              # Update SEP
- DELETE /SEP/Delete             # Delete SEP
- GET    /SEP/{noSep}             # Query SEP
- GET    /Rujukan/{noRujukan}     # Get referral
- GET    /Peserta/nik/{nik}       # Check eligibility by NIK
- GET    /Peserta/noKartu/{kartu} # Check eligibility by card
- GET    /referensi/diagnosa      # Search ICD-10
- GET    /referensi/poli          # Search polyclinic
```

**Antrean (Queue) API:**
```
Base URL: https://api.bpjs-kesehatan.go.id/antrean-kp

Key Services:
- POST   /antrean/add             # Add queue
- PUT    /antrean/update          # Update queue status
- GET    /antrean/list            # Get queue list
- DELETE /antrean/batal           # Cancel queue
```

**PCare API (Primary Care):**
```
Base URL: https://api.bpjs-kesehatan.go.id/pcare-rest-dev

Key Services:
- POST   /pendaftaran             # Register patient
- GET    /kunjungan               # Get visits
- POST   /obat/diberikan          # Record medications
```

### 12.2 BPJS Authentication

**HMAC-SHA256 Signature:**
```python
import hmac
import hashlib
import time

def generate_bpjs_signature(cons_id: str, secret_key: str) -> tuple[str, str, str]:
    """Generate BPJS VClaim authentication headers"""
    timestamp = str(int(time.time()))
    data = f"{cons_id}&{timestamp}"
    signature = hmac.new(
        secret_key.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "X-cons-id": cons_id,
        "X-timestamp": timestamp,
        "X-signature": signature,
        "Content-Type": "application/json"
    }
    return headers
```

### 12.3 BPJS Data Mapping

**SEP Data Structure:**
```python
class SEPRequest(BaseModel):
    noKartu: str                    # BPJS card number
    tglSep: date                    # SEP date
    tglRujukan: date                # Referral date
    noRujukan: str                  # Referral number
    ppkRujukan: str                 # Referring facility code
    ppkPelayanan: str               # Current facility code
    jnsPelayanan: str               # 1=Inpatient, 2=Outpatient
    klsRawat: str                   # Room class (1/2/3)
    diagAwal: str                   # Initial diagnosis (ICD-10)
    poliTujuan: str                 # Target polyclinic code
    eksekutif: str                  # 0=Regular, 1=Executive

    # Doctor info
    penanggungJawab: dict = {
        "nama": str,                # Doctor name
        "noSurat": str,             # License number
        "kodeDokter": str           # Doctor code
    }

    # Accident info (if applicable)
    lakalantas: str = "0"           # 0=No, 1=Yes, 2=Industrial, 3=Traffic
```

---

## 13. SATUSEHAT Integration Requirements

### 13.1 FHIR R4 Resources

**Patient Resource:**
```json
{
  "resourceType": "Patient",
  "identifier": [{
    "use": "official",
    "system": "https://fhir.kemkes.go.id/id/nik",
    "value": "3201010101010001"
  }],
  "name": [{
    "use": "official",
    "text": "Budi Santoso"
  }],
  "gender": "male",
  "birthDate": "1980-01-01",
  "address": [{
    "use": "home",
    "line": ["Jl. Sudirman No. 1"],
    "city": "Jakarta",
    "postalCode": "10110",
    "country": "ID"
  }]
}
```

**Encounter Resource:**
```json
{
  "resourceType": "Encounter",
  "status": "in-progress",
  "class": {
    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
    "code": "IMP",
    "display": "inpatient encounter"
  },
  "subject": {
    "reference": "Patient/12345"
  },
  "period": {
    "start": "2026-01-13T08:00:00+07:00"
  }
}
```

**Condition Resource (Diagnosis):**
```json
{
  "resourceType": "Condition",
  "clinicalStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
      "code": "active"
    }]
  },
  "verificationStatus": {
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
      "code": "confirmed"
    }]
  },
  "code": {
    "coding": [{
      "system": "http://hl7.org/fhir/sid/icd-10",
      "code": "J18.9",
      "display": "Pneumonia, unspecified"
    }]
  },
  "subject": {
    "reference": "Patient/12345"
  }
}
```

**Observation Resource (Lab Results):**
```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "2345-7",
      "display": "Glucose [Moles/volume] in Serum or Plasma"
    }]
  },
  "subject": {
    "reference": "Patient/12345"
  },
  "valueQuantity": {
    "value": 5.5,
    "unit": "mmol/L",
    "system": "http://unitsofmeasure.org",
    "code": "mmol/L"
  },
  "referenceRange": [{
    "low": {
      "value": 3.9,
      "unit": "mmol/L"
    },
    "high": {
      "value": 6.1,
      "unit": "mmol/L"
    }
  }]
}
```

### 13.2 SATUSEHAT OAuth 2.0

**Token Request:**
```python
async def get_satusehat_token(client_id: str, client_secret: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api-satusehat.kemkes.go.id/oauth2/v1/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            }
        )
        return response.json()["access_token"]
```

**Using the Token:**
```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/fhir+json"
}
```

---

## 14. Compliance & Regulatory Requirements

### 14.1 Permenkes No. 82 Tahun 2013 (SIMRS Mandatory)
- **Mandatory implementation:** All hospitals must use SIMRS
- **Open source preferred:** Open source solutions preferred
- **Integration required:** Must integrate with government programs
- **Data standards:** Use standardized medical codes (ICD-10, etc.)

### 14.2 Permenkes No. 24 Tahun 2022 (Electronic Medical Records)
- **EMR mandatory:** All healthcare facilities must use electronic medical records
- **Data retention:** Inpatient records: 25 years, Outpatient records: 10 years
- **Privacy & security:** Role-based access control, audit trails, encryption
- **Digital signature:** Medical records must be digitally signed
- **Backup & recovery:** Regular backup required (minimum daily)

### 14.3 UU No. 27 Tahun 2022 (Personal Data Protection)
- **Sensitive personal data:** Health data classified as sensitive
- **Data localization:** Critical public sector data must be stored in Indonesia
- **Breach notification:** Notify within 3×24 hours for serious breaches
- **Patient rights:** Access, correction, deletion (with exceptions), portability

### 14.4 Data Retention Schedule

| Record Type | Retention Period | Legal Basis |
|-------------|------------------|-------------|
| Inpatient Records | 25 years from discharge | Permenkes 24/2022 Pasal 34 |
| Outpatient Records | 10 years from last visit | Permenkes 24/2022 Pasal 34 |
| Medical Imaging (CT, MRI) | 25 years | Permenkes 24/2022 Pasal 34 |
| Medical Imaging (X-Ray) | 10 years | Permenkes 24/2022 Pasal 34 |
| Laboratory Results | 10 years | Permenkes 24/2022 Pasal 34 |
| Death Records | Permanent | Permenkes 24/2022 Pasal 34 |
| Audit Logs | 6 years | Recommended (aligned with medical records) |

---

## 15. Backup & Disaster Recovery

### 15.1 Backup Strategy
```bash
#!/bin/bash
# backup.sh - Daily backup script

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups"
DB_NAME="simrs"
DB_USER="simrs"

# Database backup
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# MinIO backup (if using)
mc mirror minio/simrs-documents $BACKUP_DIR/minio_$DATE/

# Upload to offsite (optional)
# aws s3 sync $BACKUP_DIR s3://simrs-backups/

# Cleanup old backups (keep 90 days)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +90 -delete
find $BACKUP_DIR -type d -name "minio_*" -mtime +90 -exec rm -rf {} +
```

### 15.2 Restore Procedure
```bash
#!/bin/bash
# restore.sh - Restore from backup

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file>"
    exit 1
fi

# Stop services
docker-compose stop backend celery-worker

# Restore database
gunzip < $BACKUP_FILE | psql -U simrs -h localhost simrs

# Restart services
docker-compose start backend celery-worker

echo "Restore complete: $BACKUP_FILE"
```

### 15.3 Disaster Recovery Plan
- **RTO (Recovery Time Objective):** < 4 hours for critical systems
- **RPO (Recovery Point Objective):** < 15 minutes data loss
- **Backup frequency:** Daily full + continuous WAL archiving
- **Offsite backup:** Weekly backup to external storage
- **Recovery testing:** Quarterly disaster recovery drill

---

## 16. Implementation Roadmap

### Phase 1: Foundation (Months 1-3)
- Set up development environment
- Implement authentication system
- Design database schema
- Build patient registration module
- Basic BPJS eligibility checking

### Phase 2: Core Features (Months 4-6)
- Medical records module
- Outpatient (Rawat Jalan) workflow
- Inpatient (Rawat Inap) workflow
- Emergency (IGD) basic workflow
- Prescriptions and medications
- Offline-first PWA

### Phase 3: Advanced Features (Months 7-9)
- Integration with SATUSEHAT
- Full BPJS VClaim integration
- Laboratory module
- Radiology module
- Pharmacy inventory management
- Billing module
- Queue management (Antrian)

### Phase 4: Optimization (Months 10-12)
- Performance optimization
- Security audit and hardening
- User training materials
- Deployment documentation
- Production deployment
- Post-deployment support

---

## 17. Success Metrics

### 17.1 Technical Metrics
- **Uptime:** > 99.5% (downtime < 3.65 days/year)
- **Response time:** < 500ms for 95% of requests
- **Offline functionality:** 100% of core features work offline
- **Data sync:** < 5 minutes latency for sync when online
- **BPJS API success rate:** > 98%

### 17.2 User Metrics
- **Adoption:** > 80% of staff using system within 3 months
- **Satisfaction:** > 4/5 user satisfaction score
- **Training completion:** > 90% of staff complete training
- **Error rate:** < 1% of operations require manual correction

### 17.3 Compliance Metrics
- **Data retention:** 100% compliance with retention schedules
- **Audit trail:** 100% of actions logged and retrievable
- **BPJS SEP creation:** < 2 minutes from patient registration
- **SATUSEHAT sync:** 90% of encounters synced within 24 hours

---

## 18. Conclusion

This architecture document provides a comprehensive blueprint for building a modern, Indonesia-specific Hospital Information Management System (SIMRS) that meets all regulatory requirements while leveraging current best practices in software architecture.

**Key Success Factors:**

1. **Offline-first design** is non-negotiable for Indonesian context (21% of Puskesmas with limited internet)
2. **BPJS/SATUSEHAT integration** is mandatory and must be implemented from the start
3. **Security by default** - encryption, audit logs, access control (UU 27/2022 compliance)
4. **Indonesian localization** - language, currency, medical coding, geographic structure
5. **Simplicity over complexity** - easier to maintain with local talent
6. **Phased implementation** - start with core features, expand gradually
7. **Local capacity building** - train hospital IT staff for sustainability

This architecture provides a solid foundation for a modern, reliable hospital information system that can serve Indonesia's diverse healthcare landscape, from small Puskesmas in remote areas to large teaching hospitals in major cities.

---

**Document Version:** 1.0
**Last Updated:** 2026-01-13
**Status:** Draft
**Next Review:** 2026-07-13 (or as technology/regulations change)

---

## References

1. **Permenkes No. 82 Tahun 2013** - Sistem Informasi Manajemen Rumah Sakit
2. **Permenkes No. 24 Tahun 2022** - Rekam Medis Elektronik
3. **UU No. 27 Tahun 2022** - Perlindungan Data Pribadi
4. **BPJS Kesehatan VClaim API** - https://apijkn.bpjs-kesehatan.go.id/vclaim-rest
5. **SATUSEHAT Platform** - https://satusehat.kemkes.go.id/platform/docs/
6. **SIMRS-Khanza Analysis** - https://github.com/mas-elkhanza/SIMRS-Khanza
7. **FastAPI Documentation** - https://fastapi.tiangolo.com/
8. **Next.js Documentation** - https://nextjs.org/docs
9. **PostgreSQL Documentation** - https://www.postgresql.org/docs/
10. **Docker Compose Documentation** - https://docs.docker.com/compose/

---

*This architecture document is a comprehensive guide for building SIMRS for Indonesian hospitals. It should be reviewed and updated regularly as technology evolves and regulations change.*
