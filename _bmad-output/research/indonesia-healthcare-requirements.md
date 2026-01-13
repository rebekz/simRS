# Indonesia Healthcare System Requirements for SIMRS

**Research Date:** January 12, 2026
**Track:** Research Track 2
**Purpose:** Comprehensive research on Indonesia-specific healthcare system requirements that SIMRS MUST support

---

## Table of Contents

1. [BPJS Kesehatan Integration](#1-bpjs-kesehatan-integration)
2. [SATUSEHAT Platform](#2-satusehat-platform)
3. [Permenkes Regulations](#3-permenkes-regulations)
4. [Indonesian Medical Coding](#4-indonesian-medical-coding)
5. [Hospital Workflow Patterns](#5-hospital-workflow-patterns)
6. [Data Requirements](#6-data-requirements)
7. [Integration Architecture Recommendations](#7-integration-architecture-recommendations)
8. [References](#8-references)

---

## 1. BPJS Kesehatan Integration

### Overview
BPJS Kesehatan (Badan Penyelenggara Jaminan Sosial Kesehatan) is Indonesia's national health insurance implementation body. Integration with BPJS is **mandatory** for all healthcare facilities in Indonesia.

### API Endpoints and Services

#### 1.1 VClaim API (Primary Integration)
VClaim is the main API bridge for BPJS Kesehatan integration.

**Base URLs:**
- Production: `https://api.bpjs-kesehatan.go.id/vclaim-rest`
- Development: `https://dvlp.bpjs-kesehatan.go.id:9080/vclaim-rest-dev`

**Key Endpoints:**

| Service | Endpoint | Description |
|---------|----------|-------------|
| **SEP (Surat Eligibilitas Peserta)** | `/SEP` | Create eligibility letter for patient admission |
| **SEP Update** | `/SEP/Update` | Update SEP information (e.g., room changes) |
| **SEP Delete** | `/SEP/Delete` | Cancel/delete SEP |
| **SEP History** | `/SEP/tglSep/{tglSep}` | Retrieve SEP history by date |
| **Rujukan (Referral)** | `/Rujukan` | Get referral information |
| **Rujukan by No. Rujukan** | `/Rujukan/{noRujukan}` | Get specific referral details |
| **Rencana Kontrol (Control Plan)** | `/RencanaKontrol` | Create follow-up appointment plan |
| **Rencana Kontrol List** | `/RencanaKontrol/List` | Get control plan list by SEP |
| **Diagnosa** | `/referensi/diagnosa` | Get ICD-10 diagnosis codes |
| **Poli (Polyclinic)** | `/referensi/poli` | Get polyclinic list |
| **Faskes (Facility)** | `/referensi/faskes` | Get healthcare facility list |
| **Peserta (Participant)** | `/Peserta/nik/{nik}` | Get participant eligibility by NIK |
| **Peserta by BPJS Card** | `/Peserta/noKartu/{noKartu}` | Get participant eligibility by card number |

#### 1.2 Antrean (Queue) API
For online queue management integration.

**Base URL:** `https://api.bpjs-kesehatan.go.id/antrean-kp`

**Key Endpoints:**
- `/antrean/add` - Add new queue
- `/antrean/update` - Update queue status
- `/antrean/list` - Get queue list
- `/antrean/sisa` - Get remaining queue count
- `/antrean/batal` - Cancel queue

### Authentication Requirements

BPJS uses a custom signature-based authentication system.

#### Authentication Components

1. **Cons-ID (Consumer ID):** Unique identifier for the healthcare facility
2. **Timestamp:** Unix timestamp in seconds
3. **Signature:** HMAC-SHA256 hash generated from Cons-ID + Timestamp + Secret Key
4. **User Key:** Additional authentication key

#### Signature Generation Algorithm

```string
Signature = HMAC-SHA256(Cons-ID + ":" + Timestamp, Secret-Key)
```

#### HTTP Headers Required

```
X-cons-id: {cons-id}
X-timestamp: {timestamp}
X-signature: {generated-signature}
user_key: {user-key}
Content-Type: application/json
```

#### Authentication Flow

1. Generate current Unix timestamp
2. Create string: `{cons-id}:{timestamp}`
3. Generate HMAC-SHA256 hash using Consumer Secret
4. Include all four components in HTTP headers
5. Signature validation is performed on every request

### Data Formats for Claims

#### 1. SEP (Surat Eligibilitas Peserta) Format

**Request Structure:**
```json
{
  "request": {
    "t_sep": {
      "noKartu": "0001R00101XXXX",
      "tglSep": "2026-01-12",
      "tglRujukan": "2026-01-10",
      "noRujukan": "123456789",
      "ppkRujukan": "CODER1234",
      "ppkPelayanan": "CODER5678",
      "jnsPelayanan": "2",  // 1=Rawat Inap, 2=Rawat Jalan
      "klsRawat": "3",       // Kelas rawat
      "klsRawatHak": "3",
      "klsRawatNaik": "-",
      "pembiayaan": "-",
      "penanggungJawab": {
        "nama": "Dr. Example",
        "noSurat": "12345",
        "kodeDokter": "12345"
      },
      "diagAwal": "A00",     // ICD-10 code
      "poliTujuan": "INT",
      "eksekutif": "0"
    }
  }
}
```

#### 2. Rencana Kontrol (Control Plan) Format

```json
{
  "request": {
    "t_rencana_kontrol": {
      "noSEP": "1234567890",
      "tglRencanaKontrol": "2026-01-20",
      "poliTujuan": "INT",
      "kodeDokter": "12345"
    }
  }
}
```

#### 3. Claim (Klaim) Data Structure

Claims are submitted through E-Klaim system with the following key components:

- **SEP Data:** Patient eligibility and admission information
- **Diagnosis Codes:** ICD-10 codes for primary and secondary diagnoses
- **Procedure Codes:** Medical procedures performed
- **Drug Data:** Medications prescribed and administered
- **Tariff Data:** Cost components (professional fees, hotel services, etc.)
- **Provider Data:** Healthcare facility and practitioner information

### Webhook/Callback Patterns

BPJS Kesehatan integration primarily uses **request-response pattern** rather than webhooks:

- **Synchronous API:** Most operations use direct HTTP requests with immediate responses
- **Polling Pattern:** For checking claim status and eligibility updates
- **Batch Processing:** Claims are typically processed in batches (daily/hourly)
- **No Standard Webhook:** BPJS does not provide webhook notifications for events

**Alternative Patterns:**
- Regular polling for claim status updates
- Scheduled jobs for data synchronization
- Manual trigger through admin interface

### Common Integration Challenges

#### 1. Signature Authentication Complexity
- Challenge: HMAC-SHA256 signature generation must be exact
- Solution: Use tested libraries for signature generation
- Impact: Invalid signatures cause all API calls to fail

#### 2. Time Synchronization
- Challenge: Timestamp must match server time exactly
- Solution: Use NTP synchronization, allow small time drift tolerance
- Impact: Time mismatches cause authentication failures

#### 3. Data Format Variations
- Challenge: Different BPJS modules may use varying data structures
- Solution: Maintain versioned adapters for different BPJS API versions
- Impact: Breaking changes from BPJS require system updates

#### 4. Network Reliability
- Challenge: BPJS API may experience downtime or slow responses
- Solution: Implement retry logic, caching, and queue systems
- Impact: Service disruption affects patient registration and billing

#### 5. Testing Environment Limitations
- Challenge: Development environment may have incomplete data
- Solution: Comprehensive mock data and testing strategies
- Impact: Production bugs discovered late in development cycle

#### 6. Patient Data Matching
- Challenge: Inconsistent patient identifiers across systems
- Solution: Implement robust data matching and validation
- Impact: Duplicate patient records and claim rejections

---

## 2. SATUSEHAT Platform

### Overview
SATUSEHAT (Satu Sehat) is Indonesia's national health data exchange platform developed by the Ministry of Health (Kementerian Kesehatan). It serves as the central hub for healthcare data interoperability across all healthcare facilities in Indonesia.

### Platform Components

1. **FHIR Server:** HL7 FHIR R4-compliant server for healthcare data exchange
2. **Terminology Server:** Provides standardized coding systems (ICD-10, LOINC, SNOMED CT)
3. **Master Data Server:** Manages master indexes (patients, facilities, practitioners)
4. **Developer Hub:** API documentation, testing tools, and developer resources

### National Health Data Exchange API

#### Base URLs
- Production: `https://api-satusehat.kemkes.go.id`
- Staging: `https://api-satusehat-stg.dto.kemkes.go.id`

#### FHIR R4 Resources Supported

| Resource | Purpose | Key Operations |
|----------|---------|----------------|
| **Patient** | Patient demographic data | Create, Read, Update, Search |
| **Encounter** | Patient visits/admissions | Create, Read, Update |
| **Condition** | Diagnoses/problems | Create, Read, Search |
| **Observation** | Clinical observations (vitals, labs) | Create, Read, Search |
| **ServiceRequest** | Orders for procedures/services | Create, Read, Update |
| **MedicationRequest** | Medication prescriptions | Create, Read, Update |
| **MedicationAdministration** | Medication administration | Create, Read |
| **Location** | Hospital locations/departments | Read, Search |
| **Practitioner** | Healthcare providers | Read, Search |
| **Organization** | Healthcare facilities | Read, Search |
| **Composition** | Clinical documents | Create, Read |
| **DiagnosticReport** | Lab/radiology reports | Create, Read |

### Required Data Elements

#### 1. Patient Demographics (Patient Resource)

**Mandatory Fields:**
- `identifier`: NIK (Nomor Induk Kependudukan) - primary identifier
- `name`: Full legal name (at least one)
- `gender`: Male/Female
- `birthDate`: Date of birth
- `address`: At least one address
- `telecom`: Phone number (preferred)

**Conditional/Recommended Fields:**
- `maritalStatus`: Marital status
- `multipleBirth`: For multiple births (twins, etc.)
- `birthSex`: Biological sex at birth
- `deceasedBoolean`: Deceased status
- `communication`: Languages spoken

**Example Structure:**
```json
{
  "resourceType": "Patient",
  "identifier": [
    {
      "use": "official",
      "system": "https://fhir.kemkes.go.id/id/nik",
      "value": "3201010101010001"
    }
  ],
  "name": [
    {
      "use": "official",
      "text": "Budi Santoso"
    }
  ],
  "gender": "male",
  "birthDate": "1980-01-01",
  "address": [
    {
      "use": "home",
      "line": ["Jl. Sudirman No. 1"],
      "city": "Jakarta",
      "postalCode": "10110",
      "country": "ID"
    }
  ],
  "telecom": [
    {
      "system": "phone",
      "value": "08123456789",
      "use": "mobile"
    }
  ]
}
```

#### 2. Encounters (Encounter Resource)

**Mandatory Fields:**
- `status`: in-progress | finished | cancelled
- `class`: inpatient | outpatient | emergency | etc.
- `subject`: Reference to Patient
- `period`: Start and end date/time

**Required for Hospital Visits:**
- `hospitalization`: Admission details
- `location`: Locations visited during encounter
- `participant`: Healthcare providers involved

**Example Structure:**
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
    "start": "2026-01-12T08:00:00+07:00"
  },
  "hospitalization": {
    "admitSource": {
      "coding": [{
        "system": "http://terminology.hl7.org/CodeSystem/admit-source",
        "code": "emd"
      }]
    }
  }
}
```

#### 3. Conditions (Condition Resource)

**Mandatory Fields:**
- `clinicalStatus`: active | inactive | resolved
- `verificationStatus`: confirmed | provisional | differential
- `code`: ICD-10 code
- `subject`: Reference to Patient
- `encounter`: Reference to Encounter (when applicable)

**Required for Diagnosis:**
- `onsetDateTime`: When condition started
- `recorder`: Who recorded the diagnosis

**Example Structure:**
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
  },
  "encounter": {
    "reference": "Encounter/67890"
  },
  "onsetDateTime": "2026-01-12T08:00:00+07:00",
  "recordedDate": "2026-01-12T10:00:00+07:00"
}
```

### Integration Requirements for Hospitals

#### 1. Registration Requirements

- **Organization ID:** Obtain unique organization ID from SATUSEHAT
- **Client Credentials:** OAuth 2.0 client credentials for API access
- **Facility Registration:** Register all facility locations
- **Practitioner Registration:** Register all healthcare providers

#### 2. Data Submission Requirements

Hospitals must submit data for:
- **Patient Registration:** All new and returning patients
- **Encounters:** All inpatient, outpatient, and emergency visits
- **Diagnoses:** Primary and secondary diagnoses (ICD-10)
- **Procedures:** Medical procedures performed
- **Medications:** Prescriptions and administrations
- **Lab Results:** Laboratory test results with LOINC codes
- **Vital Signs:** Patient vitals and observations
- **Radiology Reports:** Diagnostic imaging reports

#### 3. Data Timeliness

- **Real-time:** Patient registration and eligibility checks
- **Near real-time:** Encounters and diagnoses (within 24 hours)
- **Batch:** Historical data migration and periodic updates

#### 4. Integration Levels

**Level 1 - Terdaftar (Registered):**
- Basic registration completed
- Organization profile created
- No active data submission

**Level 2 - Terintegrasi (Integrated):**
- Active API integration
- Submitting core data (Patient, Encounter, Condition)
- Minimum 50% data completeness

**Level 3 - Terkoneksi (Connected):**
- Full integration
- Submitting all required resource types
- Minimum 80% data completeness
- Advanced features enabled

### FHIR Standards Usage

#### 1. FHIR R4 Implementation

SATUSEHAT follows **HL7 FHIR R4** standard with Indonesian-specific extensions and profiles.

**Key Implementation Guides:**
- SATUSEHAT FHIR R4 Implementation Guide
- IHS (Indonesia Health Services) FHIR R4 Implementation Guide
- National Patient Summary (IPS) Implementation Guide

#### 2. Terminology Bindings

**Required Code Systems:**
- **ICD-10:** Diagnosis coding (WHO version)
- **LOINC:** Laboratory test identifiers
- **SNOMED CT:** Clinical terminology (growing adoption)
- **Local Systems:** Indonesian-specific codes where applicable

**Value Sets:**
- Indonesian administrative codes
- Facility type codes
- Service category codes
- Insurance type codes (BPJS categories)

#### 3. Search Parameters

Standard FHIR search parameters with Indonesian extensions:
- `identifier`: NIK-based patient search
- `name`: Name-based search
- `birthdate`: Date of birth search
- `gender`: Gender filtering
- Custom parameters for national program tracking

### Authentication & Authorization

#### OAuth 2.0 Client Credentials Flow

**Token Endpoint:**
```
POST https://api-satusehat.kemkes.go.id/oauth2/v1/token
```

**Request:**
```
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "patient/*.read patient/*.write encounter/*.read encounter/*.write"
}
```

**Using the Token:**
```
Authorization: Bearer {access_token}
```

#### Authentication Rules

1. **Client ID/Secret:**
   - One-to-one mapping with Organization ID
   - Cannot be shared across organizations
   - Must be kept secure (environment variables, secrets management)

2. **Token Management:**
   - Access tokens expire (typically 1 hour)
   - Implement automatic token refresh
   - Handle token expiration gracefully

3. **Scope-Based Access:**
   - Different scopes for different operations
   - Read vs. write permissions
   - Resource-specific access control

---

## 3. Permenkes Regulations

### Overview
Permenkes (Peraturan Menteri Kesehatan) are Minister of Health Regulations that establish mandatory requirements for healthcare information systems in Indonesia.

### Key Regulations

#### 3.1 Permenkes No. 82 Tahun 2013
**Title:** Sistem Informasi Manajemen Rumah Sakit (SIMRS)

**Key Provisions:**

1. **Mandatory Implementation (Pasal 3):**
   - Every hospital **must** implement SIMRS
   - Open source solutions are preferred
   - Must be integrated with government programs

2. **System Components (Pasal 4):**
   SIMRS must include:
   - Patient registration module
   - Medical records module
   - Pharmacy/medication management
   - Laboratory services
   - Radiology services
   - Inpatient management
   - Outpatient management
   - Emergency department (IGD) management
   - Financial/billing system
   - Human resources management
   - Inventory management
   - Reporting and analytics

3. **Integration Requirements (Pasal 5):**
   - Must integrate with Ministry of Health systems
   - Must support data exchange standards
   - Must ensure data security and privacy
   - Must provide interoperability with external systems

4. **Data Standards (Pasal 6):**
   - Use standardized medical codes (ICD-10, etc.)
   - Follow national data standards
   - Maintain data integrity and accuracy

5. **Technical Requirements (Pasal 7):**
   - System availability and reliability
   - Data backup and recovery
   - User access controls
   - Audit trail capabilities

#### 3.2 Permenkes No. 24 Tahun 2022
**Title:** Rekam Medis (Medical Records)

**Key Provisions:**

1. **Electronic Medical Records (EMR) Mandatory:**
   - All healthcare facilities **must** use electronic medical records
   - Effective date: August 31, 2022
   - Gradual implementation with deadlines

2. **Data Retention (Pasal 34):**
   - Inpatient records: Minimum 25 years
   - Outpatient records: Minimum 10 years
   - Medical imaging: 10-25 years depending on type
   - Death records: Permanent retention

3. **Privacy & Security (Pasal 35-37):**
   - Patient consent required for data access
   - Role-based access control mandatory
   - Audit trails for all access
   - Data encryption in transit and at rest
   - Breach notification requirements

4. **Authentication (Pasal 38):**
   - User authentication required
   - Two-factor authentication for sensitive data
   - Session management
   - Password policies

5. **Data Integration (Pasal 39-40):**
   - Must integrate with SATUSEHAT platform
   - Must support FHIR standards
   - Must submit required data elements
   - Interoperability requirements

6. **Digital Signature (Pasal 41):**
   - Medical records must be digitally signed
   - Practitioner authentication
   - Non-repudiation of authorship

7. **Backup & Recovery (Pasal 42-43):**
   - Regular backup required (minimum daily)
   - Off-site backup storage
   - Regular recovery testing
   - Disaster recovery planning

8. **Access Control (Pasal 44-45):**
   - Minimum privilege principle
   - Role-based access
   - Emergency access procedures
   - Access logging and monitoring

9. **Data Quality (Pasal 46-47):**
   - Data validation required
   - Regular data quality audits
   - Correction mechanisms
   - Version control

#### 3.3 Additional Relevant Regulations

**Permenkes No. 254 Tahun 2024 (Latest):**
- Updates on SATUSEHAT integration requirements
- Enhanced interoperability standards
- New data submission deadlines
- Updated technical specifications

**Permenkes No. 129 Tahun 2008:**
- Standar Pelayanan Minimal Rumah Sakit (SPM)
- Minimum service standards for hospitals
- Quality indicators and benchmarks

**UU No. 27 Tahun 2022:**
- Personal Data Protection (PDP) Law
- Comprehensive data protection framework
- Patient data rights
- Data controller/processor obligations

### Data Retention Requirements

#### Medical Records Retention Schedule

| Record Type | Retention Period | Legal Basis |
|-------------|------------------|-------------|
| **Inpatient Records** | 25 years from discharge | Permenkes 24/2022 Pasal 34 |
| **Outpatient Records** | 10 years from last visit | Permenkes 24/2022 Pasal 34 |
| **Medical Imaging (CT, MRI)** | 25 years | Permenkes 24/2022 Pasal 34 |
| **Medical Imaging (X-Ray)** | 10 years | Permenkes 24/2022 Pasal 34 |
| **Ultrasound Images** | 10 years | Permenkes 24/2022 Pasal 34 |
| **Laboratory Results** | 10 years | Permenkes 24/2022 Pasal 34 |
| **Death Records** | Permanent | Permenkes 24/2022 Pasal 34 |
| **Operative Reports** | 25 years | Permenkes 24/2022 Pasal 34 |
| **Anesthesia Records** | 25 years | Permenkes 24/2022 Pasal 34 |

#### Archival Requirements

1. **Preservation of Original:**
   - Original electronic records must be preserved
   - Format migration when needed
   - Maintain readability and integrity

2. **Archival Format:**
   - Standard formats (PDF/A for documents, DICOM for images)
   - Metadata preservation
   - Compression algorithms

3. **Accessibility:**
   - Records must be retrievable within reasonable time
   - Search capabilities required
   - Audit trail for access

### Privacy & Security Requirements

#### 1. Data Classification

**Sensitive Personal Data (PDP Law):**
- Health data and medical records
- Biometric data
- Genetic information
- Mental/physical health condition

**General Personal Data:**
- Name, NIK, address, phone
- Date of birth, gender
- Occupation, education

#### 2. Security Measures (Permenkes 24/2022 + UU 27/2022)

**Technical Safeguards:**
- Encryption in transit (TLS 1.2+)
- Encryption at rest (AES-256)
- Access controls and authentication
- Audit logging (all access)
- Intrusion detection/prevention
- Regular security updates
- Vulnerability management

**Administrative Safeguards:**
- Privacy policies and procedures
- Staff training on data protection
- Data protection officer (if required)
- Incident response procedures
- Business continuity planning
- Third-party risk management

**Physical Safeguards:**
- Secure server locations
- Access-controlled data centers
- Equipment security
- Document disposal procedures

#### 3. Patient Rights (UU 27/2022)

- Right to access their medical records
- Right to correct inaccurate data
- Right to request data deletion (with exceptions)
- Right to data portability
- Right to refuse processing (with exceptions)
- Right to be informed of data breaches

#### 4. Data Breach Requirements

- **Notification Timeline:** Notify within 3×24 hours for serious breaches
- **Notification Content:** What happened, what data, impact, remediation
- **Regulatory Notification:** Notify Ministry of Health and data protection authority
- **Patient Notification:** Notify affected individuals when high risk

### Mandatory Features for Hospital Systems

#### Core Modules (Permenkes 82/2013)

1. **Registration Module:**
   - Patient registration (new and returning)
   - Queue management
   - Appointment scheduling
   - Insurance verification (BPJS)
   - Patient card generation

2. **Medical Records Module:**
   - Electronic medical records
   - Clinical documentation
   - Diagnosis coding (ICD-10)
   - Procedure coding
   - Medical history
   - Allergies and contraindications

3. **Outpatient (Poli) Module:**
   - Clinic management
   - Doctor scheduling
   - Consultation documentation
   - Prescription management
   - Referral processing

4. **Inpatient (Rawat Inap) Module:**
   - Bed management
   - Admission/discharge/transfer
   - Nursing documentation
   - Daily progress notes
   - Discharge planning
   - Billing integration

5. **Emergency (IGD) Module:**
   - Triage system
   - Emergency registration
   - Critical care documentation
   - Fast-track processing
   - ambulance integration

6. **Pharmacy (Farmasi) Module:**
   - Prescription processing
   - Drug dispensing
   - Inventory management
   - Drug interaction checking
   - Batch number tracking
   - Expiry monitoring

7. **Laboratory Module:**
   - Test ordering
   - Sample tracking
   - Result entry and validation
   - LOINC coding
   - Quality control
   - Report generation

8. **Radiology Module:**
   - Exam ordering
   - DICOM integration
   - Image storage (PACS)
   - Report generation
   - Workflow management
   - Radiation dose tracking

9. **Billing Module:**
   - Tariff management
   - BPJS claim generation
   - Invoice generation
   - Payment processing
   - Insurance coordination of benefits

10. **Reporting Module:**
    - SIRS (Sistem Informasi Rumah Sakit) reports
    - Ministry of Health reports
    - BPJS reports
    - Quality indicators
    - Statistical reports

11. **Integration Module:**
    - SATUSEHAT FHIR integration
    - BPJS bridging
    - Lab system integration
    - Payment gateway integration
    - External referrals

---

## 4. Indonesian Medical Coding

### Overview
Indonesia utilizes specific medical coding standards for healthcare data classification, billing, and reporting. Compliance with these standards is mandatory for SIMRS.

### ICD-10-CM Indonesia

#### Usage in Indonesia

**Primary Purpose:** Diagnosis coding for:
- BPJS claims
- Medical records
- SATUSEHAT integration
- Epidemiological reporting
- Hospital statistics

**Version:** Indonesia uses ICD-10 2016 version for COVID-19 and newer conditions, but some systems still use ICD-10 2010.

#### Implementation Requirements

1. **Diagnosis Coding:**
   - **Primary Diagnosis:** Mandatory for all encounters
   - **Secondary Diagnoses:** Required for comorbidities
   - **Admission Diagnosis:** Required for inpatient admissions
   - **Discharge Diagnosis:** Required for inpatient discharges
   - **Complications:** Must be coded when present

2. **Coding Guidelines:**
   - Use highest specificity possible
   - Code to the utmost certainty
   - Follow WHO ICD-10 guidelines
   - Indonesian modifications apply
   - Regular updates from Ministry of Health

3. **Required Fields:**
   - **ICD-10 Code:** Alphanumeric code (e.g., "J18.9")
   - **Description:** Diagnosis name
   - **Coding Status:** Provisional/Confirmed
   - **Onset Date:** When diagnosis was made
   - **Recorder:** Who made the diagnosis

#### ICD-10 Code Structure

```
Format: X00.0
- First character: Letter (A-Z, except U)
- Second character: Number (0-9)
- Third character: Number (0-9)
- Decimal point
- Fourth character: Number (0-9) for subclassification

Example: J18.9 (Pneumonia, unspecified)
- J: Respiratory system
- 18: Pneumonia
- .9: Unspecified
```

#### Common ICD-10 Categories in Indonesian Hospitals

| Chapter | Code Range | Description |
|---------|------------|-------------|
| I | A00-B99 | Certain infectious and parasitic diseases |
| II | C00-D48 | Neoplasms |
| IX | I00-I99 | Diseases of the circulatory system |
| X | J00-J99 | Diseases of the respiratory system |
| XI | K00-K93 | Diseases of the digestive system |
| XIV | O00-O9A | Pregnancy, childbirth and the puerperium |
| XVIII | R00-R99 | Symptoms, signs and abnormal clinical findings |
| XIX | S00-T98 | Injury, poisoning and certain other consequences |
| XX | V00-Y99 | External causes of morbidity |
| XXI | Z00-Z99 | Factors influencing health status |

### LOINC for Lab Results

#### Overview
LOINC (Logical Observation Identifiers Names and Codes) is the international standard for laboratory test identification.

#### Implementation in SATUSEHAT

SATUSEHAT **requires** LOINC codes for laboratory test results submitted through the platform.

**Official LOINC Terminology for Indonesia:**
- SATUSEHAT provides LOINC terminology service
- Available at: `https://satusehat.kemkes.go.id/platform/docs/id/terminology/loinc/`

#### LOINC Code Structure

```
Format: 12345-6
- First part: 5-7 digit number (test identifier)
- Hyphen
- Last part: 1-2 digit check digit

Example: 2345-7 (Glucose [Moles/volume] in Serum or Plasma)
```

#### LOINC Usage Requirements

1. **Laboratory Test Coding:**
   - **Single Tests:** Individual laboratory tests
   - **Panels:** Groups of related tests
   - **Observations:** Clinical measurements

2. **Mandatory LOINC Fields:**
   - **LOINC Code:** Test identifier
   - **Test Name:** Descriptive name
   - **System:** Specimen type (Serum, Urine, etc.)
   - **Scale:** Type of result (Quant, Ord, Nom)
   - **Method:** Testing methodology (when relevant)

3. **Common Lab Test Categories:**
   - **Hematology:** CBC, coagulation studies
   - **Chemistry:** Electrolytes, enzymes, hormones
   - **Microbiology:** Cultures, sensitivities
   - **Immunology:** Serology, autoimmune tests
   - **Urinalysis:** Routine and microscopic exams

#### Examples of LOINC Codes

| Test | LOINC Code | Description |
|------|------------|-------------|
| Hemoglobin | 718-7 | Hemoglobin [Mass/volume] in Blood |
| WBC | 6690-2 | Leukocytes [#/volume] in Blood by Automated count |
| Platelet Count | 777-3 | Platelets [#/volume] in Blood by Automated count |
| Glucose | 2345-7 | Glucose [Moles/volume] in Serum or Plasma |
| Creatinine | 2160-0 | Creatinine [Moles/volume] in Serum or Plasma |
| AST (SGOT) | 1920-8 | Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma |

### SNOMED CT

#### Adoption in Indonesia

Indonesia became a SNOMED International member in 2023, through the Ministry of Health.

**Current Status:**
- Growing adoption for clinical terminology
- Used alongside ICD-10 and LOINC
- Provides more detailed clinical concepts
- SATUSEHAT terminology server includes SNOMED CT

#### Usage in Healthcare

1. **Clinical Documentation:**
   - Detailed clinical findings
   - Problem list entries
   - Clinical terminology standardization
   - Interoperability between systems

2. **Mapping to ICD-10:**
   - SNOMED CT → ICD-10 mapping for billing
   - More specific clinical concepts
   - Better data analytics

3. **Benefits:**
   - Greater specificity than ICD-10
   - Better clinical decision support
   - Improved data interoperability
   - Enhanced analytics capabilities

### Other Coding Standards

#### 1. ICD-9-CM Procedures

**Usage:** Inpatient procedure coding (being phased out for ICD-10-PCS)

**Current Status:**
- Still used in some Indonesian hospitals
- Transition to ICD-10-PCS ongoing
- BPJS may still accept ICD-9-CM codes

#### 2. ICD-10-PCS

**Usage:** Procedure coding for inpatient procedures

**Implementation:**
- Growing adoption
- Replaces ICD-9-CM volumes 2 and 3
- More detailed procedure classification

#### 3. Local Coding Systems

**Indonesia-Specific Codes:**
- **Specialty codes:** For certain medical specialties
- **Tariff codes:** For billing purposes (INACBG, etc.)
- **Facility codes:** Hospital department codes
- **Provider codes:** Healthcare provider identification

#### 4. Drug Coding

**Common Systems:**
- **ATC (Anatomical Therapeutic Chemical):** WHO drug classification
- **Local drug codes:** For national formulary
- **BPJS drug codes:** For insurance claims
- **Generic name coding:** Standardization of drug names

### Coding Implementation Requirements for SIMRS

#### 1. Code System Integration

- **Master Code Tables:** Maintain up-to-date code tables
- **Code Search:** Easy lookup and search functionality
- **Auto-suggestion:** Code suggestions based on clinical terms
- **Validation:** Validate codes against official releases
- **Version Control:** Track code versions and updates

#### 2. Multi-Axial Coding

- **Primary diagnosis:** Main reason for encounter
- **Secondary diagnoses:** Comorbidities and complications
- **Procedure codes:** All procedures performed
- **Admitting vs. Final:** Diagnosis code changes
- **Present on Admission:** Flag for conditions present on admission

#### 3. Coding Quality Assurance

- **Coder Training:** Certified medical coders
- **Coding Review:** Regular audit of coded data
- **DRG Impact:** Understanding coding impact on reimbursement
- **Query Process:** Query physicians for clarification
- **Documentation Improvement:** Support complete documentation

---

## 5. Hospital Workflow Patterns

### Overview
Indonesian hospitals follow specific workflow patterns that SIMRS must support. Understanding these workflows is critical for system design.

### Poli (Outpatient Clinic) Workflow

#### Standard Outpatient Flow

```
1. REGISTRATION (Pendaftaran)
   ├─ Patient arrives at registration desk
   ├─ New patient: Create patient record
   ├─ Returning patient: Retrieve existing record
   ├─ Verify insurance (BPJS) status
   ├─ Select clinic/polyclinic (Poli)
   ├─ Select doctor (if applicable)
   └─ Generate queue number

2. QUEUE MANAGEMENT (Antrian)
   ├─ Display patient queue on screen
   ├─ Send SMS notification (optional)
   ├─ Track waiting times
   └─ Prioritize emergency/elderly/pregnant patients

3. TRIAGE (Optional)
   ├─ Vital signs measurement (weight, height, BP, temp)
   ├─ Brief symptom assessment
   ├─ Urgency determination
   └─ Routing to appropriate care level

4. CONSULTATION (Pemeriksaan)
   ├─ Doctor reviews patient history
   ├─ Physical examination
   ├─ Diagnosis (ICD-10 coding)
   ├─ Treatment plan
   ├─ Prescriptions (if needed)
   ├─ Lab/radiology orders (if needed)
   ├─ Return appointment scheduling
   └─ Medical record completion

5. PHARMACY (Farmasi) - If prescriptions
   ├─ Receive prescription order
   ├─ Review drug interactions
   ├─ Prepare/dispense medications
   ├─ Patient counseling
   └─ Record dispensing

6. LABORATORY/RADIOLOGY (If ordered)
   ├─ Sample collection (for lab)
   ├─ Exam scheduling (for radiology)
   ├─ Test execution
   ├─ Result entry/validation
   ├─ Report generation
   └─ Result notification

7. BILLING (Kasir)
   ├─ Calculate fees (BPJS + co-pay + non-covered items)
   ├─ Generate invoice
   ├─ Process payment
   ├─ Print receipt
   └─ BPJS claim preparation

8. DISCHARGE (Pulang)
   ├─ Provide discharge instructions
   ├─ Schedule follow-up if needed
   ├─ Complete medical record
   └─ Patient exit
```

#### Key Integration Points

- **BPJS Integration:** SEP creation, eligibility verification
- **SATUSEHAT:** Patient, Encounter, Condition resources
- **Queue Management:** Real-time queue updates
- **Pharmacy:** Electronic prescribing integration
- **Laboratory:** Order/result interface
- **Billing:** Automatic fee calculation

### Rawat Inap (Inpatient) Workflow

#### Standard Inpatient Flow

```
1. ADMISSION (Pendaftaran Rawat Inap)
   ├─ Patient arrives for admission
   ├─ Verify doctor's admission order
   ├─ Check bed availability
   ├─ Create SEP (BPJS) for inpatient care
   ├─ Assign bed and room
   ├─ Patient registration/check-in
   ├─ Initial assessment
   └─ Nursing documentation

2. ADMISSION ASSESSMENT
   ├─ Nursing admission assessment
   ├─ Vital signs baseline
   ├─ Allergies and contraindications
   ├─ Medical history review
   ├─ Current medications reconciliation
   └─ Physical examination

3. DAILY CARE (Perawatan Harian)
   ├─ Vital signs monitoring (frequency based on acuity)
   ├─ Nursing care and documentation
   ├─ Medication administration
   ├─ Daily physician rounds
   ├─ Progress note updates
   ├─ Diet management
   ├─ Hygiene and comfort care
   └─ Family communication

4. DIAGNOSTIC PROCEDURES (If ordered)
   ├─ Laboratory tests
   ├─ Radiology/imaging
   ├─ Specialty consultations
   ├─ Therapeutic procedures
   └─ Results documentation

5. TREATMENT PROGRESSION
   ├─ Treatment plan updates
   ├─ Response to treatment evaluation
   ├─ Medication adjustments
   ├─ Nursing care plan modifications
   ├─ Discharge planning
   └─ Family/patient education

6. PRE-DISCHARGE
   ├─ Discharge planning completion
   ├─ Medication reconciliation
   ├─ Discharge prescriptions
   ├─ Discharge summaries
   ├─ Patient/family education
   ├─ Home care instructions
   └─ Follow-up appointments

7. DISCHARGE (Pulang)
   ├─ Final physician order
   ├─ Nursing discharge documentation
   ├─ BPJS claim finalization
   ├─ Bill settlement
   ├─ Discharge medication dispensing
   ├─ Patient/family education
   ├─ Arrange transportation (if needed)
   ├─ Bed cleaning and reset
   └─ Data archiving

8. TRANSFER OR DEATH (If applicable)
   ├─ Transfer to other facility
   ├─ ICU transfer
   ├─ Death documentation
   ├─ Autopsy coordination (if needed)
   └─ Bereavement support
```

#### Key Integration Points

- **BPJS:** SEP updates, room changes, discharge processing
- **SATUSEHAT:** Encounter resource (inpatient class)
- **Bed Management:** Real-time bed availability
- **Nursing Documentation:** Electronic nursing notes
- **Medication Administration:** MAR (Medication Administration Record)
- **Billing:** Daily charges, package rates

### IGD (Emergency Department - Gawat Darurat) Workflow

#### Standard Emergency Flow

```
1. TRIAGE
   ├─ Patient arrival at emergency entrance
   ├─ Immediate vital signs
   ├─ Primary assessment (Airway, Breathing, Circulation)
   ├─ Triage category assignment:
   │   ├─ KUNING (Yellow) - Semi-urgent
   │   ├─ MERAH (Red) - Life-threatening
   │   ├─ HIJAU (Green) - Non-urgent
   │   └─ HITAM (Black) - Deceased/DOA
   └─ Queue prioritization

2. EMERGENCY REGISTRATION
   ├─ Rapid patient registration
   ├─ Quick BPJS eligibility check
   ├─ Emergency SEP creation (if admitted)
   ├─ Medical record number assignment
   └─ Emergency sticker/tag

3. EMERGENCY ASSESSMENT
   ├─ Primary survey (ABCDE)
   ├─ Secondary survey
   ├─ Vital signs monitoring
   ├─ Diagnostic tests (FAST, labs, imaging)
   ├─ Emergency interventions
   └─ Stabilization

4. EMERGENCY TREATMENT
   ├─ Life-saving interventions
   ├─ Medication administration
   ├─ Procedural interventions
   ├─ Consultations
   ├─ Continuous monitoring
   └─ Documentation

5. DISPOSITION DECISION
   ├─ Discharge home (with instructions)
   ├─ Transfer to outpatient clinic
   ├─ Admission to ward (Rawat Inap)
   ├─ Admission to ICU (ICU/HCU)
   ├─ Transfer to other facility
   └─ Deceased

6. DISCHARGE/TRANSFER
   ├─ Discharge summary
   ├─ Prescriptions
   ├─ Instructions to patient/family
   ├─ Follow-up arrangements
   ├─ Transfer documentation
   └─ Medical record completion
```

#### Key Integration Points

- **BPJS:** Emergency SEP, fast-track processing
- **SATUSEHAT:** Emergency encounter resource
- **Triage System:** Automated triage categorization
- **Lab/Radiology:** STAT priority orders
- **ICU Integration:** Critical care data transfer

### Farmasi (Pharmacy) Workflow

#### Standard Pharmacy Flow

```
1. PRESCRIPTION RECEIPT
   ├─ Receive prescription (electronic or paper)
   ├─ Verify prescribing physician
   ├─ Check patient information
   └─ Enter into system (if paper)

2. PRESCRIPTION VALIDATION
   ├─ Review drug appropriateness
   ├─ Check drug-drug interactions
   ├─ Check allergies
   ├─ Verify dosage and frequency
   ├─ Check contraindications
   └─ Contact prescriber if issues

3. DISPENSING PREPARATION
   ├─ Locate medication in inventory
   ├─ Check expiry dates
   ├─ Count/package medication
   ├─ Label preparation
   ├─ Calculate dosage instructions
   └─ Prepare patient counseling points

4. QUALITY CONTROL
   ├─ Verify correct medication
   ├─ Verify correct dose
   ├─ Verify correct quantity
   ├─ Check for physical defects
   └─ Pharmacist signature/initials

5. PATIENT DISPENSING
   ├─ Call patient to pharmacy counter
   ├─ Verify patient identity
   ├─ Provide medication
   ├─ Patient counseling:
   │   ├─ What the medication is for
   │   ├─ How to take it
   │   ├─ When to take it
   │   ├─ Side effects
   │   ├─ Storage instructions
   │   └─ Other important information
   ├─ Answer questions
   └─ Document dispensing

6. INVENTORY UPDATE
   ├─ Decrease stock quantity
   ├─ Update dispensing records
   ├─ Check minimum stock levels
   └─ Trigger reorders if needed

7. BILLING INTEGRATION
   ├─ Calculate medication charges
   ├─ Check insurance coverage
   ├─ Apply co-pay calculations
   └─ Send charges to billing system
```

#### Key Integration Points

- **Electronic Prescribing:** Direct orders from clinicians
- **BPJS:** Drug formulary checks, coverage validation
- **Inventory Management:** Stock level tracking
- **Billing:** Automatic charge posting
- **Drug Interaction:** Clinical decision support

### Laboratorium Workflow

#### Standard Laboratory Flow

```
1. TEST ORDERING
   ├─ Receive test order (electronic)
   ├─ Verify test availability
   ├─ Check if patient fasting required
   ├─ Verify insurance coverage
   ├─ Schedule testing (if needed)
   └─ Generate barcode labels

2. SPECIMEN COLLECTION
   ├─ Identify patient
   ├─ Verify test orders
   ├─ Collect specimen
   ├─ Label specimen (barcode)
   ├─ Document collection time
   ├─ Document collection method
   └─ Transport to lab

3. SPECIMEN RECEIPT
   ├─ Receive specimen in lab
   ├─ Verify patient and test information
   ├─ Check specimen integrity
   ├─ Accept or reject specimen
   ├─ Log receipt time
   └─ Assign to technician

4. TEST PROCESSING
   ├─ Prepare specimen for testing
   ├─ Run tests (manual or automated)
   ├─ Quality control samples
   ├─ Raw data generation
   └─ Preliminary results

5. RESULT VALIDATION
   ├─ Review results
   ├─ Check reference ranges
   ├─ Flag abnormal values
   ├─ Technical validation
   ├─ Pathologist review (if needed)
   └─ Finalize results

6. REPORTING
   ├─ Enter results into system
   ├─ Assign LOINC codes
   ├─ Generate report
   ├─ Critical value notification (if applicable)
   ├─ Send to ordering physician
   ├─ Upload to SATUSEHAT (Observation resource)
   └─ Patient portal access (if available)

7. POST-ANALYTICAL
   ├─ Store specimen (if needed)
   ├─ Quality control documentation
   ├─ Proficiency testing
   ├─ Equipment maintenance
   └─ Reagent inventory management
```

#### Key Integration Points

- **SATUSEHAT:** Observation resources with LOINC codes
- **Electronic Orders:** Direct from clinical systems
- **Barcoding:** Specimen tracking
- **Auto-analyzers:** Instrument interfacing
- **Critical Values:** Alert system
- **Billing:** Automatic charge posting

### Radiologi Workflow

#### Standard Radiology Flow

```
1. EXAM ORDERING
   ├─ Receive imaging order
   ├─ Verify exam type and protocol
   ├─ Verify insurance coverage
   ├─ Schedule exam (if not STAT)
   ├─ Patient preparation instructions
   └─ Generate worklist

2. PATIENT PREPARATION
   ├─ Patient arrival at radiology
   ├─ Verify patient identity
   ├─ Check contraindications
   ├─ Pregnancy check (if applicable)
   ├─ Explain procedure
   └─ Obtain informed consent (if needed)

3. EXAM EXECUTION
   ├─ Patient positioning
   ├─ Protocol selection
   ├─ Image acquisition (modality):
   │   ├─ X-Ray
   │   ├─ CT Scan
   │   ├─ MRI
   │   ├─ Ultrasound
   │   └─ Other modalities
   ├─ Image quality check
   ├─ Repeat if needed
   └─ Complete exam

4. IMAGE PROCESSING
   ├─ Transfer images to PACS (DICOM)
   ├─ Post-processing (if needed)
   ├─ Image quality verification
   ├─ DICOM router integration (SATUSEHAT)
   └─ Archive images

5. REPORTING
   ├─ Radiologist reviews images
   ├─ Dictate/enter findings
   ├─ Generate report
   ├─ Attach key images
   ├─ Quality assurance review
   ├─ Finalize report
   ├─ Send to ordering physician
   └─ Upload to SATUSEHAT (DiagnosticReport resource)

6. COMMUNICATION
   ├─ Critical findings notification
   ├─ Preliminary report (if urgent)
   ├─ Final report availability
   ├─ Consultation with referring physician
   └─ Patient follow-up (if needed)

7. BILLING
   ├─ Post exam charges
   ├─ Calculate contrast media charges (if used)
   ├─ Radiologist professional fees
   └─ Insurance claim submission
```

#### Key Integration Points

- **PACS (Picture Archiving and Communication System):** DICOM image storage
- **RIS (Radiology Information System):** Exam workflow management
- **DICOM Router:** SATUSEHAT integration for imaging
- **Modality Worklist:** Direct to imaging equipment
- **Voice Recognition:** Dictation for reports
- **Billing:** Automatic charge posting

---

## 6. Data Requirements

### Data Localization Laws

#### Overview
Indonesia has enacted comprehensive data protection and localization laws that impact healthcare data management.

#### Legal Framework

**UU No. 27 Tahun 2022 - Personal Data Protection (PDP) Law**

Enacted: October 17, 2022
Effective: October 17, 2024 (2-year grace period)

**Key Provisions for Healthcare:**

1. **Sensitive Personal Data (Data Pribadi Sensitif):**
   - Health and medical data are classified as **sensitive personal data**
   - Requires enhanced protection measures
   - Special consent requirements
   - Stricter breach notification requirements

2. **Data Localization (Art. 39):**
   - **Critical public sector data** must be stored in Indonesia
   - Healthcare data likely falls under this category
   - May require on-premises or Indonesia-based cloud storage

3. **Cross-Border Transfer (Art. 40-41):**
   - Allowed if equivalent protection is maintained
   - Requires Ministry of Health approval for health data
   - Contractual safeguards required
   - Data subject consent may be required

#### Implementation Requirements

**For Healthcare Facilities:**

1. **Data Storage:**
   - Primary storage in Indonesia
   - Backup in Indonesia preferred
   - Use Indonesia-based cloud providers (local AWS, Google, Azure regions)
   - Document data locations

2. **Data Processing:**
   - Processing can occur outside Indonesia if safeguards in place
   - Data must remain under Indonesian legal control
   - Contractual protections with foreign processors

3. **Data Controller:**
   - Healthcare facility is the data controller
   - Must ensure all data processors comply with PDP Law
   - Responsible for breach notifications

### Data Sovereignty Requirements

#### Data Controller vs. Data Processor

**Data Controller (Pengendali Data Pribadi):**
- Determines purposes and means of processing
- Healthcare facilities (hospitals, clinics)
- Primary responsibility for compliance

**Data Processor (Pengolah Data Pribadi):**
- Processes on behalf of controller
- SIMRS vendors
- Cloud service providers
- Must follow controller's instructions

#### Healthcare Facility Obligations

1. **Register Data Processing:**
   - Maintain record of processing activities
   - Register with data protection authority (when established)
   - Document data flows

2. **Data Protection by Design:**
   - Build privacy into system design
   - Default to privacy-friendly settings
   - Minimize data collection
   - Pseudonymization when possible

3. **Data Subject Rights:**
   - Implement rights fulfillment processes
   - Respond to access requests
   - Handle deletion requests
   - Provide data portability

4. **Breach Management:**
   - Detect breaches promptly
   - Notify within 3×24 hours (serious breaches)
   - Document all breaches
   - Prevent recurrence

5. **DPO Appointment:**
   - Appoint Data Protection Officer if large scale or sensitive data
   - Contact point for data subjects and regulators
   - Monitor compliance

### Backup and Recovery Requirements

#### Regulatory Requirements

**Permenkes 24/2022 (Art. 42-43):**

1. **Backup Frequency:**
   - **Minimum:** Daily incremental backups
   - **Recommended:** Daily full + periodic differential
   - **Critical Systems:** Real-time replication

2. **Backup Storage:**
   - **On-site:** For fast recovery (short-term retention)
   - **Off-site:** For disaster recovery (long-term retention)
   - **Geographic separation:** Different location from primary
   - **Immutable backups:** Cannot be modified or deleted for retention period

3. **Retention Period:**
   - Align with medical record retention (10-25 years)
   - Keep backups for entire retention period
   - Document backup retention schedules

4. **Recovery Testing:**
   - **Frequency:** Quarterly minimum
   - **Scope:** Test critical systems regularly
   - **Documentation:** Keep test results
   - **Recovery Time Objective (RTO):** Define maximum acceptable downtime
   - **Recovery Point Objective (RPO):** Define maximum acceptable data loss

#### Technical Requirements

1. **Backup Types:**
   - **Full:** Complete backup of all data
   - **Incremental:** Only changes since last backup
   - **Differential:** Changes since last full backup
   - **Transaction Log:** Continuous database logging

2. **Backup Validation:**
   - Regular integrity checks
   - Test restore procedures
   - Verify backup completeness
   - Monitor backup success/failure

3. **Security Considerations:**
   - Encrypt backups (in transit and at rest)
   - Secure backup storage locations
   - Restrict backup access (role-based)
   - Secure backup encryption keys
   - Test restore with encryption

4. **Disaster Recovery Planning:**
   - **RTO (Recovery Time Objective):** Maximum acceptable downtime
     - Critical systems: < 4 hours
     - Important systems: < 24 hours
     - Non-critical systems: < 72 hours

   - **RPO (Recovery Point Objective):** Maximum acceptable data loss
     - Critical systems: < 15 minutes
     - Important systems: < 1 hour
     - Non-critical systems: < 24 hours

#### Recommended Backup Strategy

**Daily:**
- Incremental backup of all databases
- Transaction log backups (every 15-30 minutes for critical systems)
- Backup verification and health check

**Weekly:**
- Full backup of all systems
- Backup to off-site location
- Backup encryption validation

**Monthly:**
- Full backup to long-term storage
- Disaster recovery test (restore and validate)
- Backup performance review

**Quarterly:**
- Comprehensive disaster recovery drill
- RTO/RPO validation
- Update disaster recovery documentation

**Annually:**
- Complete backup strategy review
- Technology refresh if needed
- Compliance audit

### Data Retention Implementation

#### Retention Schedule Enforcement

SIMRS should implement automated retention enforcement:

1. **Active Data:**
   - Recent, frequently accessed data
   - High-performance storage
   - Immediate availability

2. **Archive Data:**
   - Past retention period for active use
   - Lower-cost storage
   - Retrieval within reasonable time (hours to days)

3. **Disposal:**
   - Secure deletion when retention period expires
   - Verify no legal holds before deletion
   - Document disposal process
   - Certificate of destruction

#### Data Lifecycle Management

```
1. CREATION
   ├─ Data created at patient encounter
   ├─ Metadata captured (date, creator, patient ID)
   ├─ Classification applied (sensitive personal data)
   └─ Retention clock starts

2. ACTIVE USE
   ├─ Frequent access (0-2 years)
   ├─ High-performance storage
   ├─ Immediate availability
   └─ Regular backups

3. ARCHIVAL
   ├─ Infrequent access (2-retention period years)
   ├─ Lower-cost storage
   ├─ Retrieve within hours/days
   ├─ Maintained for legal requirements
   └─ Still backed up

4. DISPOSAL
   ├─ Retention period exceeded
   ├─ No legal holds
   ├─ Secure deletion process
   ├─ Documentation of disposal
   └─ Certificate of destruction
```

### Data Quality Requirements

#### Data Quality Dimensions (Permenkes 24/2022)

1. **Accuracy:**
   - Data correctly represents reality
   - Validation rules enforced
   - Error detection and correction

2. **Completeness:**
   - All required data elements present
   - Missing data identified
   - Data completion tracking

3. **Consistency:**
   - Data consistent across systems
   - No contradictory information
   - Standardized formats and values

4. **Timeliness:**
   - Data entered promptly
   - Real-time or near real-time
   - Timestamps on all entries

5. **Validity:**
   - Data conforms to standards
   - Code values from authorized sets
   - Format validation

6. **Uniqueness:**
   - No duplicate records
   - Proper patient identification
   - De-duplication processes

#### Data Quality Assurance

1. **Input Validation:**
   - Required field enforcement
   - Data type validation
   - Range checks
   - Format validation
   - Code table validation

2. **Data Quality Monitoring:**
   - Regular data quality reports
   - Missing data alerts
   - Duplicate detection
   - Outlier detection
   - Trend analysis

3. **Data Quality Improvement:**
   - Regular audits
   - Root cause analysis of errors
   - Process improvements
   - Staff training
   - User feedback

---

## 7. Integration Architecture Recommendations

### Architecture Overview

Based on Indonesia's healthcare requirements, SIMRS should implement the following integration architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                         SIMRS Core                              │
├─────────────────────────────────────────────────────────────────┤
│  Registration │  Clinical  │  Pharmacy │  Lab  │  Radiology    │
└─────────────────┬───────────────────────┬──────────────────────┘
                  │                       │
         ┌────────▼────────┐     ┌──────▼──────────┐
         │ Integration Hub │     │   Data Store    │
         │  (FHIR Gateway) │     └─────────────────┘
         └────────┬────────┘
                  │
    ┌─────────────┼─────────────┬──────────────┐
    │             │             │              │
┌───▼────┐  ┌────▼───┐  ┌─────▼────┐  ┌─────▼─────┐
│ BPJS   │  │SATUSEHAT│  │Hospital  │  │External   │
│Bridge  │  │Platform│  │Systems   │  │Partners   │
└────────┘  └────────┘  └──────────┘  └───────────┘
```

### Integration Components

#### 1. BPJS Integration Layer

**Components:**
- **VClaim Client:** API client for BPJS VClaim
- **Antrean Client:** Queue management API client
- **Authentication Module:** Signature generation and validation
- **Data Mapper:** Transform SIMRS data to BPJS formats
- **Retry Logic:** Handle BPJS API failures gracefully
- **Cache Manager:** Cache reference data (diagnoses, polis, etc.)

**Features:**
- Automatic signature generation
- Token/credential management
- Request/response logging
- Error handling and retry
- Rate limiting compliance
- Monitoring and alerts

#### 2. SATUSEHAT Integration Layer

**Components:**
- **FHIR Server Client:** FHIR R4 API client
- **OAuth Manager:** Token acquisition and refresh
- **FHIR Mapper:** Transform internal data to FHIR resources
- **Terminology Service:** Code system validation
- **Submission Queue:** Queue for resource submission
- **Sync Manager:** Coordinate data submission

**Features:**
- OAuth 2.0 client credentials flow
- Automatic token refresh
- FHIR resource creation/updating
- Batch submission
- Error handling and retry
- Submission status tracking

#### 3. Internal Integration Hub

**Purpose:** Centralize all external integrations

**Benefits:**
- Single integration point for all external systems
- Consistent data transformation
- Centralized error handling
- Easier monitoring and troubleshooting
- Reusable components

**Components:**
- **FHIR Gateway:** Transform all data to FHIR internally
- **Message Queue:** Asynchronous processing
- **API Gateway:** Expose internal APIs
- **Event Bus:** Event-driven architecture
- **Monitoring:** Track all integrations

### Data Flow Architecture

#### 1. Patient Registration Flow

```
Patient Arrives
    ↓
SIMRS Registration
    ↓
[Check SATUSEHAT] → Patient exists? → Yes: Update
    ↓ No                         ↓
Create Patient in SATUSEHAT   Update Patient
    ↓                           ↓
Receive Patient ID      Receive Updated Patient
    ↓                           ↓
[Check BPJS] → Verify Eligibility
    ↓
Create SEP (BPJS)
    ↓
Proceed with Encounter
```

#### 2. Encounter Creation Flow

```
Encounter Created in SIMRS
    ↓
[Transform to FHIR] → Encounter Resource
    ↓
Submit to SATUSEHAT
    ↓
[If BPJS Patient] → Update SEP
    ↓
Monitor Encounter Progress
    ↓
[On Discharge] → Finalize Encounter
    ↓
Submit Final Encounter to SATUSEHAT
    ↓
[If BPJS] → Update SEP, Close Claim
```

#### 3. Lab Results Flow

```
Lab Order Created
    ↓
[Transform to FHIR] → ServiceRequest
    ↓
Submit to SATUSEHAT
    ↓
Sample Collected & Tested
    ↓
Results Available
    ↓
[Transform to FHIR] → Observation (with LOINC)
    ↓
Submit to SATUSEHAT
    ↓
Notify Ordering Physician
    ↓
[If Critical] → Alert notification
```

### Technical Recommendations

#### 1. API Management

**Use API Gateway for:**
- Rate limiting
- Authentication/authorization
- Request/response logging
- API versioning
- Traffic monitoring
- Caching

#### 2. Error Handling

**Implement:**
- Retry logic with exponential backoff
- Dead letter queues for failed messages
- Error logging and alerting
- Circuit breakers for failing services
- Graceful degradation

#### 3. Monitoring

**Track:**
- API call success rates
- Response times
- Error rates by endpoint
- Queue depths
- Token expiration and refresh
- Data submission completeness

#### 4. Security

**Implement:**
- Secure credential storage (vault)
- TLS for all external communications
- API encryption/signature validation
- Role-based access control
- Audit logging
- Regular security updates

#### 5. Performance

**Optimize:**
- Asynchronous processing for non-critical operations
- Caching of reference data
- Batch operations for bulk data
- Connection pooling
- Load balancing

### Deployment Architecture

#### Recommended Setup

**Development:**
- Local development environment
- Mock BPJS and SATUSEHAT services
- Test data sets

**Staging/UAT:**
- BPJS development environment
- SATUSEHAT staging environment
- Full integration testing
- Performance testing

**Production:**
- BPJS production environment
- SATUSEHAT production environment
- High availability setup
- Disaster recovery
- 24/7 monitoring

---

## 8. References

### Official Government Sources

1. **Permenkes No. 82 Tahun 2013 - Sistem Informasi Manajemen Rumah Sakit**
   - URL: `https://www.kemhan.go.id/itjen/wp-content/uploads/2017/03/bn87-2014.pdf`

2. **Permenkes No. 24 Tahun 2022 - Rekam Medis**
   - URL: `https://peraturan.bpk.go.id/Details/245544/permenkes-no-24-tahun-2022`
   - PDF: `https://keslan.kemkes.go.id/unduhan/fileunduhan_1662611251_882318.pdf`

3. **UU No. 27 Tahun 2022 - Perlindungan Data Pribadi**
   - Data Protection Law of Indonesia

4. **SATUSEHAT Platform Documentation**
   - Main: `https://satusehat.kemkes.go.id/platform/docs/`
   - Authentication: `https://satusehat.kemkes.go.id/platform/docs/id/api-catalogue/authentication/`
   - Interoperability: `https://satusehat.kemkes.go.id/platform/docs/id/interoperability/`

5. **BPJS Kesehatan VClaim API**
   - URL: `https://vclaim.bpjs-kesehatan.go.id/`

### Integration Documentation

6. **SATUSEHAT FHIR R4 Implementation Guide**
   - URL: `https://simplifier.net/guide/SATUSEHAT-FHIR-R4-Implementation-Guide/`

7. **IHS FHIR R4 Implementation Guide**
   - URL: `https://simplifier.net/guide/indonesia-satusehat-ihs-fhir-r4`

8. **SATUSEHAT Postman Collection**
   - URL: `https://www.postman.com/satusehat/satusehat-public`

9. **SATUSEHAT Klaim BPJS Integration**
   - URL: `https://satusehat.kemkes.go.id/platform/docs/id/interoperability/klaim-bpjs/`

### Technical Resources

10. **BPJS Integration Documentation (GitHub - ssecd/jkn)**
    - URL: `https://github.com/ssecd/jkn`
    - TypeScript client for BPJS bridging

11. **OpenFn SATUSEHAT Adaptor**
    - URL: `https://docs.openfn.org/adaptors/satusehat`
    - Integration patterns and authentication

12. **SATUSEHAT Mediator Client (PHP)**
    - URL: `https://github.com/kemenkesri/satusehat-mediator-client-php`

### Research and Academic Sources

13. **Implementation of FHIR SATUSEHAT API in Hospital Information Systems**
    - ResearchGate: `https://www.researchgate.net/publication/383771801_Implementation_of_FHIR_SATUSEHAT_API_in_Hospital_Information_System_Applications`

14. **Analysis of Hospital Management Information System (SIMRS) Implementation**
    - URL: `https://www.researchgate.net/publication/361728413_Implementation_Of_Hospital_Management_Information_System_SIMRS_At_Royal_Prima_Hospital`

15. **Adoption of Health Terminology Standard in Indonesia**
    - PubMed: `https://pubmed.ncbi.nlm.nih.gov/40775824/`
    - Covers SNOMED CT, LOINC, ICD-10 usage

16. **Enhancing Clinical Coding Expertise in Indonesia's National Health Insurance Program**
    - ResearchGate: `https://www.researchgate.net/publication/399195458_Enhancing_Clinical_Coding_Expertise_in_Indonesia's_National_Health_Insurance_Program`

### Data Protection and Privacy

17. **Personal Data Protection and Healthcare Services in Indonesia**
    - Tilleke & Gibbins: `https://www.tilleke.com/insights/personal-data-protection-and-healthcare-services-in-indonesia/67/`

18. **Indonesia Data Protection Laws**
    - DLA Piper: `https://www.dlapiperdataprotection.com/?t=law&c=ID`

### Medical Coding Standards

19. **LOINC Laboratory - SATUSEHAT Platform**
    - URL: `https://satusehat.kemkes.go.id/platform/docs/id/terminology/loinc/laboratory/`

20. **SNOMED International - Indonesia Member**
    - URL: `https://www.snomed.org/members/indonesia`

21. **ICD-10 Indonesia Implementation**
    - Various sources on ICD-10-CM usage in Indonesian healthcare

### Industry and Vendor Resources

22. **Bridging BPJS 2026: Panduan Implementasi**
    - Aido Health: `https://aido.id/his/bridging-bpjs/detail`

23. **SIMRS Implementation and Permenkes 82/2013**
    - Multiple hospital and vendor sites

### Hospital Workflow References

24. **SATUSEHAT Interoperability Guides**
    - Rawat Inap: `https://satusehat.kemkes.go.id/platform/docs/id/interoperability/rawat-inap-new/`
    - Interoperability Overview: `https://satusehat.kemkes.go.id/platform/docs/id/interoperability/`

25. **Hospital Management Information System (HMIS) Standards**
    - K teknologi: `https://kteknologi.co.id/en/hospital-management-information-system-hmis`

### Additional Resources

26. **DICOM Router - SATUSEHAT Platform**
    - URL: `https://satusehat.kemkes.go.id/platform/docs/id/dicom-system/dicom-router/`

27. **Laboratorium SATUSEHAT Integration**
    - URL: `https://satusehat.kemkes.go.id/platform/docs/id/terminology/loinc/laboratory/`

28. **Indonesia Hospital Accreditation Standards**
    - Various sources on hospital accreditation requirements

---

## Appendix: Key Terminology

**Bahasa Indonesia Terms Used in Indonesian Healthcare:**

- **BPJS Kesehatan:** Badan Penyelenggara Jaminan Sosial Kesehatan (National Health Insurance)
- **SIMRS:** Sistem Informasi Manajemen Rumah Sakit (Hospital Management Information System)
- **RME:** Rekam Medis Elektronik (Electronic Medical Record)
- **SATUSEHAT:** Indonesia's national health data exchange platform (One Health)
- **Fasyankes:** Fasilitas Kesehatan (Healthcare Facility)
- **Poli:** Poliklinik (Outpatient Clinic)
- **Rawat Jalan:** Outpatient Care
- **Rawat Inap:** Inpatient Care
- **IGD:** Instalasi Gawat Darurat (Emergency Department)
- **Puskesmas:** Pusat Kesehatan Masyarakat (Community Health Center)
- **RSUP:** Rumah Sakit Umum Pusat (Central General Hospital)
- **RSUD:** Rumah Sakit Umum Daerah (Regional General Hospital)
- **SEP:** Surat Eligibilitas Peserta (Participant Eligibility Letter)
- **SKDP:** Surat Kontrol Pengobatan Periodik (Periodic Treatment Control Letter)
- **SPRI:** Surat Pengantar Rawat Inap (Inpatient Referral Letter)
- **INACBG:** Indonesia Case Base Groups (DRG-like system)
- **Permenkes:** Peraturan Menteri Kesehatan (Minister of Health Regulation)
- **UU:** Undang-Undang (Law)
- **NIK:** Nomor Induk Kependudukan (Population Identification Number)
- **JKN:** Jaminan Kesehatan Nasional (National Health Insurance)
- **KIS:** Kartu Indonesia Sehat (Indonesia Health Card - historical)
- **Klaim:** Claim (insurance claim)
- **Tarif:** Fee/Tariff
- **Triage:** Patient prioritization system

---

**Document Version:** 1.0
**Last Updated:** January 12, 2026
**Research Track:** Track 2 - Indonesia Healthcare Requirements
**Status:** Complete

---

## Notes for Implementation

This research document provides comprehensive coverage of Indonesia-specific healthcare requirements. When implementing SIMRS for Indonesian healthcare facilities:

1. **Prioritize BPJS and SATUSEHAT integration** - These are non-negotiable requirements
2. **Follow Permenkes 82/2013 and 24/2022** - Compliance is mandatory
3. **Implement FHIR R4 standards** - Required for SATUSEHAT integration
4. **Support Indonesian medical coding** - ICD-10, LOINC, and emerging SNOMED CT
5. **Design for local workflows** - Poli, Rawat Inap, IGD, Farmasi, Laboratorium, Radiologi
6. **Ensure data protection compliance** - UU 27/2022 PDP Law
7. **Plan for data localization** - Store healthcare data in Indonesia
8. **Implement robust backup/recovery** - Per regulatory requirements
9. **Use integration hub architecture** - Simplify multiple external integrations
10. **Monitor and maintain** - Continuous compliance and performance tracking

For specific implementation details or technical questions, refer to the official documentation sources listed in Section 8 (References).
