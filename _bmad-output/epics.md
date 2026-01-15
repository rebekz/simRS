# SIMRS - Epic Breakdown Document

**Version:** 1.0
**Date:** 2026-01-13
**Status:** Draft
**Based on:** PRD v1.0

---

## Table of Contents
1. [Epic Ordering Strategy](#epic-ordering-strategy)
2. [Cross-Cutting Concerns](#cross-cutting-concerns)
3. [MVP Definition](#mvp-definition)
4. [Detailed Epic Breakdown](#detailed-epic-breakdown)
5. [Implementation Timeline](#implementation-timeline)

---

## Epic Ordering Strategy

### Implementation Principles

The epics are ordered based on:

1. **Dependencies First**: Foundation epics must be completed before dependent features
2. **Business Value**: High-impact features (BPJS integration, patient registration) prioritized
3. **Technical Risk**: Riskier components (integrations, offline-first) addressed early
4. **Regulatory Compliance**: Mandatory requirements (BPJS, SATUSEHAT) in MVP
5. **User Adoption**: Core clinical workflows prioritized over advanced features

### Critical Path Dependencies

```
Foundation & Security → Patient Registration → Medical Records
                                    ↓
                          Outpatient Management → BPJS Integration
                                    ↓
                          Inpatient Management → Billing & Claims
                                    ↓
                          Clinical Support (Pharmacy, Lab, Radiology)
                                    ↓
                          Emergency Department → Advanced Features
```

---

## Cross-Cutting Concerns

These concerns span multiple epics and must be addressed consistently:

### 1. Security & Authentication
**Scope**: All epics
**Key Requirements**:
- Role-Based Access Control (RBAC)
- Multi-factor authentication for remote access
- Audit logging for all patient data access
- Data encryption (transit and rest)
- Session management (30-minute timeout)
- Emergency access protocols

**Implementation**: Every epic must include security considerations in acceptance criteria

---

### 2. BPJS Integration
**Scope**: Multiple epics (Registration, Outpatient, Inpatient, Billing)
**Key Requirements**:
- VClaim API integration (patient eligibility, SEP management)
- Antrean API integration (queue management)
- Aplicare API integration (bed availability)
- e-Claim submission and tracking
- Error handling and retry logic
- API rate limit monitoring

**Implementation**: Dedicated BPJS Integration epic provides reusable components

---

### 3. SATUSEHAT Integration
**Scope**: Medical Records, Clinical Support epics
**Key Requirements**:
- FHIR R4 resource submission (Patient, Encounter, Condition, Observation)
- OAuth 2.0 authentication
- LOINC coding for lab tests
- ICD-10 coding for diagnoses
- Data synchronization (within 24 hours)
- Error handling and validation

**Implementation**: Phased approach (Level 1 → Level 2 → Level 3)

---

### 4. Offline-First Architecture
**Scope**: All user-facing epics
**Key Requirements**:
- Service Workers for caching
- IndexedDB for local storage
- Background sync for queued operations
- Conflict resolution for concurrent edits
- Progressive enhancement
- Bandwidth optimization

**Implementation**: Technical foundation epic establishes architecture patterns

---

### 5. Data Retention & Archival
**Scope**: All data-storing epics
**Key Requirements**:
- Inpatient records: 25 years retention
- Outpatient records: 10 years retention
- Medical imaging: 10-25 years retention
- Automated backup and archival
- Data deletion policies (with exceptions)
- Audit log retention: 6 years

---

## MVP Definition

### MVP Scope (Months 1-6)

**Goal**: Deployable system for 3-5 pilot hospitals with core functionality

#### Included in MVP:

1. **Foundation & Security** (Epic 1)
   - User authentication and RBAC
   - Audit logging
   - Basic deployment (Docker Compose)

2. **Patient Registration** (Epic 2)
   - New and returning patient registration
   - BPJS eligibility checking
   - Queue management
   - Basic online booking

3. **Medical Records** (Epic 3)
   - Patient history
   - Problem list (ICD-10)
   - Allergy tracking
   - Basic clinical notes (SOAP)
   - Medication list

4. **Outpatient Management** (Epic 4)
   - Doctor consultation workflow
   - Prescription writing
   - Lab/radiology ordering (basic)
   - BPJS SEP generation

5. **Inpatient Management** (Epic 5)
   - Bed management
   - Admission/discharge/transfer
   - Basic nursing documentation
   - Discharge planning

6. **Pharmacy - Basic** (Epic 6 - Partial)
   - Prescription processing
   - Basic inventory management
   - Drug dispensing
   - Drug interaction checking

7. **Billing - Basic** (Epic 9 - Partial)
   - Invoice generation
   - Payment processing
   - BPJS claim preparation
   - Basic financial reports

8. **BPJS Integration** (Epic 10)
   - VClaim API
   - Antrean API
   - Basic e-Claim

9. **SATUSEHAT - Level 1** (Epic 11 - Partial)
   - Organization registration
   - Patient data synchronization
   - Basic encounter data

#### Excluded from MVP (Phase 2+):

- Full Laboratory module (Epic 7)
- Full Radiology module (Epic 8)
- Emergency Department (Epic 12)
- Advanced medical records features
- Mobile apps (iOS/Android)
- Telemedicine
- Advanced analytics
- AI clinical decision support
- Full SATUSEHAT Level 2/3

---

## Detailed Epic Breakdown

### Epic 1: Foundation & Security Infrastructure

**Epic ID**: EPIC-001
**Business Value**: Provides secure, scalable foundation for all hospital operations
**Complexity**: High
**Estimated Duration**: 4-6 weeks

#### Dependencies
- None (this is the foundation epic)

#### Key User Stories

1. As an IT administrator, I want to deploy the system with a single command so that I can set up the hospital quickly
2. As a system administrator, I want to manage users and roles so that staff have appropriate access
3. As a security officer, I want all patient data access logged so that we can comply with regulations
4. As a developer, I want reusable authentication and authorization components so that I don't duplicate code
5. As a system administrator, I want automated backups so that patient data is never lost

#### Acceptance Criteria

**Deployment**:
- [ ] Docker Compose setup works with single command
- [ ] Database migrations run automatically
- [ ] Health check endpoints operational
- [ ] System accessible via HTTPS

**Authentication & Authorization**:
- [ ] Login/logout functionality working
- [ ] Role-based access control (RBAC) implemented
- [ ] Permission model supports resource-based and action-based permissions
- [ ] Session timeout after 30 minutes of inactivity
- [ ] Multi-factor authentication for remote access
- [ ] Password policies enforced (12+ chars, complexity, expiration)

**Security**:
- [ ] All data encrypted in transit (TLS 1.3)
- [ ] All sensitive data encrypted at rest
- [ ] Audit logging for all CRUD operations
- [ ] Audit logs include: timestamp, user, action, resource, IP address
- [ ] Audit logs retained for 6 years
- [ ] Failed login attempts logged and monitored

**Backup & Recovery**:
- [ ] Automated daily backups at 2 AM
- [ ] Backup restoration tested and documented
- [ ] Off-site backup storage (encrypted)
- [ ] Recovery time objective <4 hours for critical systems
- [ ] Backup retention policy implemented (30/365/84 months)

**Monitoring**:
- [ ] System health monitoring operational
- [ ] Error tracking and alerting configured
- [ ] Performance metrics collected (response time, uptime)
- [ ] API rate limit monitoring

#### Technical Notes
- Tech stack: FastAPI, PostgreSQL, Redis, Docker Compose
- Authentication: JWT tokens with refresh token rotation
- Encryption: PostgreSQL pgcrypto for sensitive fields
- Backup: pg_dump + WAL archiving
- Monitoring: Prometheus + Grafana (or simpler solution for MVP)

---

### Epic 2: Patient Registration & Queue Management

**Epic ID**: EPIC-002
**Business Value**: First point of contact for patients - critical for patient experience and BPJS compliance
**Complexity**: Medium
**Estimated Duration**: 3-4 weeks

#### Dependencies
- Epic 1 (Foundation & Security)

#### Key User Stories

1. As a registration clerk, I want to register new patients quickly so that wait times are reduced
2. As a registration clerk, I want to verify BPJS eligibility instantly so that we avoid claim rejections
3. As a patient, I want to book appointments online so that I don't have to wait in long queues
4. As a registration clerk, I want to search existing patients easily so that I can check them in quickly
5. As a hospital administrator, I want to monitor queue lengths so that I can allocate staff efficiently

#### Acceptance Criteria

**New Patient Registration**:
- [ ] Registration time <3 minutes per patient
- [ ] Capture all required demographics (NIK, name, DOB, address, phone)
- [ ] Auto-generate unique medical record number (no. RM)
- [ ] NIK validation (16 digits)
- [ ] Duplicate patient detection (by NIK or name+DOB)
- [ ] Patient photo capture (optional)
- [ ] Emergency contact information captured
- [ ] Insurance information captured (BPJS, Asuransi, Umum)

**BPJS Integration**:
- [ ] BPJS eligibility check completes in <5 seconds
- [ ] Display BPJS membership status
- [ ] Validate BPJS card number
- [ ] Handle BPJS API failures gracefully
- [ ] Cache eligibility results (with expiration)

**Returning Patient Registration**:
- [ ] Patient lookup time <10 seconds
- [ ] Support multiple search methods (MRN, BPJS, NIK, name+DOB, phone)
- [ ] Display last visit date and diagnoses
- [ ] Highlight changes in patient information
- [ ] Quick check-in functionality
- [ ] Verify current insurance status

**Online Booking**:
- [ ] Patient self-service booking portal
- [ ] Display available appointment slots in real-time
- [ ] Select doctor and polyclinic
- [ ] Send booking confirmation (SMS/WhatsApp)
- [ ] Queue management integration
- [ ] Cancel/reschedule appointments
- [ ] Mobile JKN API integration

**Queue Management**:
- [ ] Queue number generation per department (Poli, Farmasi, Lab, Radiologi, Kasir)
- [ ] Digital queue display screens
- [ ] SMS queue notifications
- [ ] Queue status via mobile web
- [ ] Priority queue management (lansia, ibu hamil, difabel, emergency)
- [ ] Average wait time display
- [ ] BPJS Antrean API integration

#### Technical Notes
- Integrates with BPJS VClaim API (eligibility check)
- Integrates with BPJS Antrean API (queue management)
- Offline-first: Patient lookup works offline, syncs when online
- Barcode generation for patient ID bands
- SMS gateway integration for notifications

---

### Epic 3: Medical Records & Clinical Documentation

**Epic ID**: EPIC-003
**Business Value**: Core clinical data repository - essential for patient care and regulatory compliance
**Complexity**: High
**Estimated Duration**: 5-6 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)

#### Key User Stories

1. As a doctor, I want to view complete patient history instantly so that I can make informed decisions
2. As a doctor, I want to document encounters quickly using SOAP notes so that I can focus on patients
3. As a nurse, I want to see allergy alerts prominently so that I can prevent adverse reactions
4. As a doctor, I want to search ICD-10 codes easily so that I can document diagnoses accurately
5. As a hospital administrator, I want complete medical records for regulatory compliance

#### Acceptance Criteria

**Patient History**:
- [ ] Display complete history in single view
- [ ] Timeline visualization of past encounters
- [ ] Quick access to recent visits
- [ ] Search by date range
- [ ] Export to PDF (patient copy)
- [ ] Include: demographics, contacts, insurance, emergency contacts
- [ ] Medical history: past visits, hospitalizations, surgeries, allergies, chronic conditions
- [ ] Family medical history
- [ ] Social history (smoking, alcohol, occupation)
- [ ] Immunization records

**Problem List (ICD-10-CM Indonesia)**:
- [ ] ICD-10 code lookup <5 seconds
- [ ] Search by code or description
- [ ] Display Indonesian descriptions
- [ ] Maintain active problem list
- [ ] Problem status tracking (Active, Resolved, Chronic, Acute)
- [ ] Onset date recording
- [ ] Recorder attribution (who diagnosed)
- [ ] Link problems to encounters
- [ ] Show problem history
- [ ] Common codes favorites

**Allergy Tracking**:
- [ ] Allergy alerts always visible in patient banner
- [ ] Drug allergy recording (allergen, reaction, severity, onset date, source)
- [ ] Food allergy recording
- [ ] Environmental allergy recording
- [ ] Alert during prescription writing
- [ ] Warning before administering medication
- [ ] Prevent prescribing allergens
- [ ] Document allergy source (patient-reported, tested)
- [ ] "No Known Allergies" (NKA) option
- [ ] Support multiple allergies

**Medication List**:
- [ ] Show active medications prominently
- [ ] Current medication list (drug name, dose, frequency, route, start date, prescriber)
- [ ] Medication history
- [ ] Discontinued medications with reason
- [ ] Drug interaction checking
- [ ] Duplicate therapy warnings
- [ ] Medication reconciliation on admission
- [ ] Indication (reason for use)

**Clinical Notes**:
- [ ] Auto-save every 30 seconds
- [ ] Require digital signature for attestation
- [ ] Track all changes with audit trail
- [ ] Support structured templates (SOAP, admission, progress, discharge, consult, procedure)
- [ ] Free text option with auto-save
- [ ] Voice-to-text dictation (optional - Phase 2)
- [ ] Version control with audit trail
- [ ] Note sharing (with patient consent)
- [ ] Export to PDF

#### Technical Notes
- ICD-10-CM Indonesia database integration
- FHIR R4 Condition resources for SATUSEHAT sync
- Rich text editor for clinical notes
- Digital signature implementation
- Offline-first: View and create records offline
- Full-text search for patient history

---

### Epic 4: Outpatient Management (Poli Rawat Jalan)

**Epic ID**: EPIC-004
**Business Value**: Core clinical workflow for majority of patient visits - directly impacts hospital revenue
**Complexity**: Medium-High
**Estimated Duration**: 4-5 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)
- Epic 3 (Medical Records)

#### Key User Stories

1. As a doctor, I want to start consultations quickly so that I can see more patients
2. As a doctor, I want to write prescriptions with drug interaction checks so that patient safety is ensured
3. As a doctor, I want to order lab and radiology tests electronically so that results are tracked
4. As a doctor, I want to generate BPJS SEP automatically so that claims are not rejected
5. As a patient, I want to schedule follow-up appointments easily so that I continue my care

#### Acceptance Criteria

**Doctor Consultation Workflow**:
- [ ] Start consultation in <5 seconds
- [ ] Display patient summary (demographics, vital signs, history)
- [ ] Auto-populate common templates
- [ ] Save progress automatically
- [ ] Complete encounter in <10 minutes
- [ ] Clinical documentation: chief complaint, HPI, physical exam, assessment, treatment plan
- [ ] Quick diagnosis entry (ICD-10 codes)
- [ ] Prescription writing integration
- [ ] Lab/radiology ordering integration
- [ ] Return appointment scheduling
- [ ] Patient education materials

**Prescription Management**:
- [ ] Electronic prescribing interface
- [ ] Drug search (generic and brand) with auto-complete
- [ ] Dose and frequency selection
- [ ] Quantity calculation
- [ ] Route of administration
- [ ] Special instructions
- [ ] Check interactions in <3 seconds
- [ ] Alert for all drug-drug, drug-disease, drug-allergy interactions
- [ ] Display BPJS coverage status
- [ ] Print prescriptions with barcode
- [ ] Support compound prescriptions (racikan)
- [ ] Electronic prescription to pharmacy

**Lab/Radiology Requests**:
- [ ] Complete order in <2 minutes
- [ ] Test catalog search
- [ ] Package selection (panel)
- [ ] Clinical indication
- [ ] Priority selection (routine, urgent, STAT)
- [ ] Auto-select LOINC codes (lab)
- [ ] Procedure codes (radiology)
- [ ] Check insurance coverage
- [ ] Track order status
- [ ] Alert when results ready
- [ ] FHIR ServiceRequest integration

**BPJS SEP Generation**:
- [ ] Generate SEP in <10 seconds
- [ ] Automatic SEP creation (patient eligibility verified, diagnosis populated, poli mapped, doctor assigned)
- [ ] Validate all required fields
- [ ] SEP updates (room changes, diagnosis updates, policy changes)
- [ ] SEP cancellation
- [ ] SEP history tracking
- [ ] Handle BPJS API failures gracefully
- [ ] Display SEP status

#### Technical Notes
- BPJS VClaim API integration (SEP creation/updates)
- Drug interaction database integration
- LOINC code lookup for lab tests
- FHIR ServiceRequest for SATUSEHAT
- Offline-first: Create encounters offline, sync SEP when online
- Integration with Epic 3 (Medical Records) for data persistence

---

### Epic 5: Inpatient Management (Rawat Inap)

**Epic ID**: EPIC-005
**Business Value**: Manages complex, high-value patient stays - critical for revenue and care quality
**Complexity**: High
**Estimated Duration**: 5-6 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)
- Epic 3 (Medical Records)

#### Key User Stories

1. As a nurse, I want to view bed availability in real-time so that I can assign patients efficiently
2. As a doctor, I want to admit patients quickly so that care is not delayed
3. As a nurse, I want to document daily care at bedside so that records are accurate
4. As a doctor, I want to track patient progress daily so that I can adjust treatment plans
5. As a discharge planner, I want to prepare discharges efficiently so that beds are available for new patients

#### Acceptance Criteria

**Bed Management**:
- [ ] Real-time bed availability dashboard
- [ ] Total beds per room (occupied, available, maintenance)
- [ ] Assign bed in <30 seconds
- [ ] Prevent double-booking
- [ ] View bed by ward/room
- [ ] Filter by class (VVIP, VIP, 1, 2, 3)
- [ ] Filter by gender (male/female/mixed)
- [ ] Assign patient to bed
- [ ] Transfer patient between beds
- [ ] Room status (clean/soiled, maintenance, isolation)
- [ ] Bed request workflow (request, approve, assign, notify)
- [ ] Sync with BPJS Aplicare (real-time bed reporting)

**Room/Ward Assignment**:
- [ ] Complete admission in <5 minutes
- [ ] Verify doctor's admission order
- [ ] Check bed availability
- [ ] Select room and bed
- [ ] Update BPJS SEP automatically
- [ ] Generate admission papers
- [ ] Room transfer workflow (initiate, approve, update bed, update SEP)
- [ ] Track all bed changes
- [ ] Prevent room conflicts
- [ ] Estimated discharge date
- [ ] Discharge criteria tracking

**Daily Care Notes**:
- [ ] Document care in real-time
- [ ] Auto-save documentation
- [ ] Require digital signature
- [ ] Nursing documentation (flow sheets, narrative notes, care plans, patient education)
- [ ] Physician progress notes (daily rounds, assessment and plan, orders)
- [ ] Interdisciplinary notes (respiratory therapy, physical therapy, nutrition, social work)
- [ ] Shift documentation (shift handoff, change of shift report)
- [ ] Template-based and free text
- [ ] Support care plans
- [ ] Export to discharge summary

**Discharge Planning**:
- [ ] Complete discharge in <30 minutes
- [ ] Discharge readiness assessment (clinical stability, medication reconciliation, education completed, follow-up scheduled)
- [ ] Discharge orders (medications, instructions, activity restrictions, diet, follow-up)
- [ ] Generate discharge summary automatically (admission diagnosis, procedures, treatment, discharge diagnosis, medications, follow-up)
- [ ] Reconcile medications
- [ ] Schedule follow-up appointments
- [ ] Finalize BPJS claim
- [ ] Update BPJS SEP (close SEP on discharge)

**BPJS SEP Continuity**:
- [ ] Create SEP within 24 hours of admission
- [ ] Inpatient service type (jnsPelayanan = 1)
- [ ] Room class assignment
- [ ] Initial diagnosis
- [ ] Update SEP for all changes (room class, diagnosis, doctor, policy)
- [ ] Close SEP on discharge (final diagnosis, discharge disposition, LOS)
- [ ] Generate Inacbg grouping data
- [ ] Calculate package rate
- [ ] Adjust for ICU/ventilator
- [ ] Track SEP lifecycle

#### Technical Notes
- BPJS Aplicare API integration (bed availability)
- BPJS VClaim API integration (SEP management for inpatient)
- Inacbg grouper integration (calculate package rates)
- Real-time bed availability updates
- Offline-first: View bed status offline, update when online
- Mobile-optimized for bedside documentation

---

### Epic 6: Pharmacy Management

**Epic ID**: EPIC-006
**Business Value**: Ensures medication safety and inventory control - critical for patient safety and cost management
**Complexity**: Medium-High
**Estimated Duration**: 4-5 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)
- Epic 3 (Medical Records)

#### Key User Stories

1. As a pharmacist, I want to process prescriptions quickly so that patients don't wait long
2. As a pharmacist, I want barcode scanning for dispensing so that errors are prevented
3. As a pharmacy manager, I want to track stock levels so that we never run out of essential drugs
4. As a pharmacist, I want automatic drug interaction alerts so that patient safety is ensured
5. As a pharmacy manager, I want expiry alerts so that expired drugs are not dispensed

#### Acceptance Criteria

**Inventory Management**:
- [ ] Drug master file (generic name, brand names, dosage forms, BPJS codes, e-Katalog codes, manufacturer)
- [ ] Real-time stock updates
- [ ] Current stock levels, bin locations, expiry dates, batch numbers
- [ ] Stock transactions (purchase orders, goods received, adjustments, transfers, returns)
- [ ] Near-expiry alerts (3 months)
- [ ] Expired drug quarantine
- [ ] Prevent dispensing expired drugs
- [ ] First-in-first-out (FIFO) dispensing
- [ ] Minimum stock levels and reorder point alerts
- [ ] Auto-generate purchase orders
- [ ] Track stock movements

**Prescription Dispensing**:
- [ ] Process prescription in <5 minutes
- [ ] Receive prescriptions electronically
- [ ] Queue by priority
- [ ] Barcode patient verification
- [ ] Verify prescription
- [ ] Check drug interactions
- [ ] Check stock availability
- [ ] Barcode scan all drugs (verify correct drug and dose, prevent errors)
- [ ] Count/package medication
- [ ] Label generation
- [ ] Pharmacist verification
- [ ] Document counseling
- [ ] Dispensing history

**Drug Interactions Checking**:
- [ ] Check interactions in <3 seconds
- [ ] Alert for all interactions (drug-drug, drug-disease, drug-allergy, drug-food, therapeutic duplications)
- [ ] Display severity levels (contraindicated, severe, moderate, mild)
- [ ] Display recommendations
- [ ] Require override reason
- [ ] Alert at prescribing and dispensing
- [ ] Document resolution
- [ ] Update interaction database regularly
- [ ] Custom interaction rules

**E-Katalog Integration** (Phase 2):
- [ ] Display E-Katalog prices
- [ ] Government procurement prices
- [ ] Price comparison
- [ ] Create PO from E-Katalog
- [ ] Track order delivery
- [ ] Report price variances
- [ ] Update prices automatically

#### Technical Notes
- Drug interaction database integration
- BPJS formulary integration (coverage status)
- Barcode scanning integration
- E-Katalog API integration (Phase 2)
- Inventory alerts and notifications
- Offline-first: View inventory offline, sync when online

---

### Epic 7: Laboratory Information System

**Epic ID**: EPIC-007
**Business Value**: Essential for diagnosis and treatment decisions - critical for clinical quality
**Complexity**: High
**Estimated Duration**: 5-6 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)
- Epic 3 (Medical Records)

#### Key User Stories

1. As a doctor, I want to order lab tests electronically so that results are tracked
2. As a lab technologist, I want barcode-based sample tracking so that samples are not mixed up
3. As a lab technologist, I want automatic result capture from analyzers so that errors are reduced
4. As a pathologist, I want to review and verify results before release so that quality is ensured
5. As a doctor, I want to receive critical value alerts immediately so that patient care is not delayed

#### Acceptance Criteria

**Test Requests**:
- [ ] Order tests in <2 minutes
- [ ] Electronic test ordering
- [ ] Test catalog (all available tests)
- [ ] Test panels (groups of tests)
- [ ] Custom panels
- [ ] Clinical indication
- [ ] Priority selection (routine, urgent, STAT)
- [ ] Specimen requirements
- [ ] Auto-assign LOINC codes
- [ ] Generate barcode labels
- [ ] Track order status
- [ ] Sync with SATUSEHAT (FHIR ServiceRequest)

**Result Entry**:
- [ ] Auto-capture from instruments
- [ ] Manual result entry
- [ ] Batch result entry
- [ ] Quality control results
- [ ] Result validation (reference ranges by age/gender, delta checks, critical value flags, abnormal highlighting)
- [ ] Flag abnormal values
- [ ] Alert for critical values (direct notification to physician)
- [ ] Require verification before release
- [ ] Track result modifications
- [ ] Pathologist review queue
- [ ] Electronic signature
- [ ] Comments and addendum

**Quality Control**:
- [ ] Run QC daily
- [ ] QC material management (lot tracking, expiry monitoring, storage conditions)
- [ ] Daily QC runs
- [ ] Levey-Jennings charts
- [ ] Apply Westgard rules
- [ ] Alert for out-of-control
- [ ] Document corrective actions
- [ ] Maintenance records
- [ ] PT enrollment and tracking
- [ ] PT performance reports

**LIS Integration**:
- [ ] Interface with major analyzers
- [ ] Bidirectional communication (ASTM, HL7)
- [ ] Auto-send worklist to analyzers
- [ ] Auto-capture results from analyzers
- [ ] Barcode-based tracking
- [ ] Result formatting and unit conversion
- [ ] Auto-verification rules
- [ ] DICOM for image capture

#### Technical Notes
- LOINC code integration
- ASTM/HL7 protocol support for analyzer interfaces
- FHIR Observation resources for SATUSEHAT sync
- Critical value alerting system
- Quality control dashboards
- Instrument interfacing middleware

---

### Epic 8: Radiology Information System

**Epic ID**: EPIC-008
**Business Value**: Supports diagnostic imaging - essential for modern hospital services
**Complexity**: High
**Estimated Duration**: 5-6 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)
- Epic 3 (Medical Records)

#### Key User Stories

1. As a radiologist, I want to receive exam worklists electronically so that I don't have to re-enter data
2. As a radiologic technologist, I want to send images to PACS automatically so that they are not lost
3. As a radiologist, I want to use report templates so that I can dictate reports quickly
4. As a doctor, I want to view radiology reports and images so that I can make diagnoses
5. As a radiologist, I want to alert physicians about critical findings so that patient care is not delayed

#### Acceptance Criteria

**Modality Worklist**:
- [ ] Send worklist to modalities
- [ ] Exam scheduling
- [ ] Track exam status in real-time
- [ ] DICOM MWL (Modality Worklist) support
- [ ] Screen for contraindications (pregnancy, contrast allergy, kidney function)
- [ ] Select appropriate protocols (standard by exam type, custom, radiologist preferences)
- [ ] Receive status updates from equipment

**Image Management (PACS Integration)**:
- [ ] Store images in PACS
- [ ] Display images in web viewer
- [ ] Link images to reports
- [ ] Export to CD
- [ ] Meet retention requirements (25 years CT/MRI, 10 years X-ray)
- [ ] Receive images from equipment
- [ ] Image compression
- [ ] Image lifecycle management
- [ ] Image backup
- [ ] CD burning with viewer

**Report Generation**:
- [ ] Complete report in <5 minutes
- [ ] Standard templates by modality
- [ ] Custom templates
- [ ] Macros and shortcuts
- [ ] Voice recognition (optional - Phase 2)
- [ ] Transcription workflow
- [ ] Report finalization
- [ ] Send report to ordering physician
- [ ] Upload to SATUSEHAT (DiagnosticReport)
- [ ] Patient portal access
- [ ] Alert for critical findings
- [ ] Direct notification to physician
- [ ] Document communication

#### Technical Notes
- DICOM MWL (Modality Worklist) integration
- PACS integration (optional for MVP - can use existing PACS)
- FHIR DiagnosticReport for SATUSEHAT sync
- Report template engine
- Critical value alerting
- Web-based DICOM viewer (if PACS not available)

---

### Epic 9: Billing, Finance & Claims

**Epic ID**: EPIC-009
**Business Value**: Ensures revenue capture and timely payment - critical for financial sustainability
**Complexity**: High
**Estimated Duration**: 5-6 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)
- Epic 4 (Outpatient Management)
- Epic 5 (Inpatient Management)

#### Key User Stories

1. As a billing staff, I want to generate invoices automatically so that billing errors are reduced
2. As a billing staff, I want to submit BPJS claims electronically so that payments are received quickly
3. As a cashier, I want to process payments efficiently so that patient checkout is fast
4. As a hospital administrator, I want to track claim status so that revenue is predictable
5. As a finance manager, I want financial reports so that I can monitor hospital performance

#### Acceptance Criteria

**Invoice Generation**:
- [ ] Capture all charges (professional fees, hotel services, drugs, lab, radiology, procedures, supplies)
- [ ] Apply correct billing rules
- [ ] Generate accurate invoices
- [ ] Support multiple payers (BPJS, Asuransi, Umum)
- [ ] Package rates (BPJS INA-CBG)
- [ ] Fee-for-service (private insurance)
- [ ] Discount rules
- [ ] Co-payment calculations
- [ ] Invoice approval workflow
- [ ] Approve invoices before discharge

**BPJS Claims Processing**:
- [ ] Generate e-Claim files automatically
- [ ] Validate claim data
- [ ] Group by INA-CBG
- [ ] Calculate package rate
- [ ] Submit claims within BPJS deadline (21 days after discharge)
- [ ] Submit to BPJS gateway
- [ ] Track submission status
- [ ] Handle submission errors
- [ ] Respond to verification queries
- [ ] Submit additional documents
- [ ] Track claim payment status
- [ ] Payment reconciliation
- [ ] Payment posting
- [ ] Claim analytics (submission rate, approval rate, rejection reasons, payment timeliness)

**Insurance (Asuransi) Handling**:
- [ ] Support multiple insurance plans
- [ ] Insurance master (companies, plans, coverage rules, pre-auth requirements)
- [ ] Verify eligibility
- [ ] Get pre-authorizations
- [ ] Generate insurance claims
- [ ] Track claim status
- [ ] Coordinate benefits (primary payer BPJS, secondary payer private insurance, patient responsibility)
- [ ] Explanation of benefits (EOB)

**Payment Processing**:
- [ ] Process payments accurately
- [ ] Support multiple payment methods (cash, credit/debit cards, bank transfer, virtual account, payment gateway)
- [ ] Generate receipts
- [ ] Allocate payments to invoices
- [ ] Payment reconciliation
- [ ] Track patient deposits
- [ ] Manage accounts receivable
- [ ] Payment reminders
- [ ] Collections management
- [ ] Financial reports (revenue, aging, payments)

#### Technical Notes
- BPJS e-Claim API integration
- Inacbg grouper integration (calculate INA-CBG packages)
- Insurance eligibility verification APIs
- Payment gateway integration
- Financial reporting engine
- Invoice workflow approval

---

### Epic 10: BPJS Kesehatan Integration

**Epic ID**: EPIC-010
**Business Value**: Mandatory for regulatory compliance and revenue - critical for hospital operations
**Complexity**: High
**Estimated Duration**: 4-5 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)

#### Key User Stories

1. As a registration clerk, I want to verify BPJS eligibility instantly so that we know coverage status
2. As a doctor, I want to generate SEP automatically so that claims are not rejected
3. As a hospital administrator, I want to report bed availability in real-time so that compliance is maintained
4. As a billing staff, I want to submit claims electronically so that payments are received quickly
5. As a system administrator, I want to monitor BPJS API performance so that issues are detected early

#### Acceptance Criteria

**VClaim API**:
- [ ] Patient eligibility checking
- [ ] SEP creation, update, deletion
- [ ] Referral (rujukan) information
- [ ] Diagnosis/procedure lookup
- [ ] Facility and provider lookup
- [ ] Claim status monitoring
- [ ] Summary of bill (SRB)
- [ ] All VClaim endpoints functional
- [ ] Handle API failures gracefully
- [ ] Retry failed requests
- [ ] Log all API calls
- [ ] Monitor API performance

**Antrean (Queue) API**:
- [ ] Online booking integration
- [ ] Queue management
- [ ] Queue status updates
- [ ] Queue list publication
- [ ] Real-time sync

**Aplicare API**:
- [ ] Bed availability reporting
- [ ] Real-time bed updates
- [ ] Room class information
- [ ] Automatic sync (every update)

**PCare API (Puskesmas)**:
- [ ] Patient registration
- [ ] Visit documentation (kunjungan)
- [ ] Medication administration
- [ ] Group activities (kegiatan kelompok)
- [ ] Laboratory tests (limited)
- [ ] Referrals (rujukan)

**iCare / SATUSEHAT Bridge**:
- [ ] FHIR resource submission
- [ ] Patient data synchronization
- [ ] Encounter data
- [ ] Diagnosis data

**Error Handling & Monitoring**:
- [ ] Comprehensive error handling
- [ ] Retry logic with exponential backoff
- [ ] Cache reference data (diagnoses, polis, facilities)
- [ ] Queue failed requests for retry
- [ ] Monitor API performance and availability
- [ ] Rate limit monitoring
- [ ] Alert on API failures
- [ ] Maintain API version compatibility
- [ ] Regular testing with BPJS sandbox

#### Technical Notes
- BPJS API client library (reusable components)
- OAuth authentication for BPJS APIs
- Message queue for failed requests
- API response caching
- Comprehensive logging
- Monitoring dashboard

---

### Epic 11: SATUSEHAT FHIR R4 Integration

**Epic ID**: EPIC-011
**Business Value**: Mandatory for regulatory compliance - critical for future healthcare data exchange
**Complexity**: High
**Estimated Duration**: 4-6 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 3 (Medical Records)

#### Key User Stories

1. As a hospital administrator, I want to register facility with SATUSEHAT so that we are compliant
2. As a system, I want to sync patient demographics automatically so that data is consistent
3. As a system, I want to submit encounter data so that reporting is automated
4. As a system, I want to sync diagnoses with ICD-10 codes so that epidemiological reporting is accurate
5. As a developer, I want reusable FHIR components so that integration is maintainable

#### Acceptance Criteria

**Level 1 (Terdaftar) - MVP**:
- [ ] Organization registration
- [ ] Facility data submission
- [ ] OAuth 2.0 authentication working
- [ ] Client credentials configured
- [ ] Basic connectivity verified

**Level 2 (Terintegrasi) - Phase 2**:
- [ ] Patient resource submission (demographics)
- [ ] Encounter resource submission (visit documentation)
- [ ] Condition resource submission (diagnoses with ICD-10)
- [ ] Auto-sync patient data
- [ ] Sync encounters within 24 hours
- [ ] Handle SATUSEHAT API errors
- [ ] Submit required FHIR resources
- [ ] Validation of FHIR resources

**Level 3 (Terkoneksi) - Phase 3**:
- [ ] Observation resources (lab results with LOINC, vital signs)
- [ ] ServiceRequest resources (lab and radiology orders)
- [ ] MedicationRequest resources (prescriptions)
- [ ] MedicationAdministration resources (medications given)
- [ ] DiagnosticReport resources (lab and radiology reports)
- [ ] Immunization resources (vaccination records)
- [ ] Practitioner resources (healthcare provider data)

**FHIR Resources**:
- [ ] Patient: Demographic data synchronization
- [ ] Encounter: Visit documentation (outpatient, inpatient, emergency)
- [ ] Condition: Diagnoses (ICD-10 codes)
- [ ] Observation: Lab results (LOINC), vital signs
- [ ] ServiceRequest: Lab and radiology orders
- [ ] MedicationRequest: Prescriptions
- [ ] MedicationAdministration: Medication given
- [ ] DiagnosticReport: Lab and radiology reports
- [ ] Immunization: Vaccination records
- [ ] Organization: Facility data
- [ ] Practitioner: Healthcare provider data

**Error Handling & Monitoring**:
- [ ] OAuth token auto-refresh
- [ ] Queue failed submissions
- [ ] Comprehensive FHIR validation
- [ ] Monitor submission status
- [ ] Test in SATUSEHAT staging environment
- [ ] Maintain FHIR resource versioning
- [ ] Handle SATUSEHAT API errors gracefully

#### Technical Notes
- FHIR R4 client library
- OAuth 2.0 authentication with token refresh
- LOINC terminology service integration
- ICD-10 terminology service integration
- FHIR resource validation
- Message queue for async submissions
- Comprehensive error handling and retry logic

---

### Epic 12: Emergency Department (IGD)

**Epic ID**: EPIC-012
**Business Value**: Critical for life-saving care - high-impact, high-risk department
**Complexity**: High
**Estimated Duration**: 4-5 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)
- Epic 3 (Medical Records)
- Epic 4 (Outpatient Management)

#### Key User Stories

1. As a triage nurse, I want to categorize patients by severity so that critical patients are seen first
2. As a registration clerk, I want to register emergency patients quickly so that care is not delayed
3. As an emergency doctor, I want to activate emergency protocols with one click so that treatment is immediate
4. As a nurse, I want to document emergency care in real-time so that records are accurate
5. As an emergency doctor, I want to track critical time metrics so that quality of care is monitored

#### Acceptance Criteria

**Triage System**:
- [ ] Complete triage in <5 minutes
- [ ] Assign appropriate category
- [ ] Display category prominently
- [ ] Indonesian triage categories (KUNING/Yellow, MERAH/Red, HIJAU/Green, HITAM/Black)
- [ ] Triage assessment (vital signs, chief complaint, ABCDE primary assessment, triage score)
- [ ] Periodic reassessment
- [ ] Update triage category
- [ ] Track triage metrics (wait times by category, patient acuity, resource utilization)

**Rapid Registration**:
- [ ] Register patient in <2 minutes
- [ ] Minimal required fields
- [ ] Register later for complete data
- [ ] Unknown patient registration (John Doe)
- [ ] Verify BPJS in <10 seconds
- [ ] Create emergency SEP
- [ ] Generate patient ID band (barcode, triage category, allergy alert)
- [ ] Assign bed automatically

**Emergency Protocols**:
- [ ] Activate protocols with one click
- [ ] Clinical decision support
- [ ] Emergency drug dosing display
- [ ] Emergency procedures reference
- [ ] Emergency order sets (trauma activation, stroke activation, STEMI activation, sepsis protocol)
- [ ] Rapid response team activation
- [ ] Code blue documentation
- [ ] Track critical time metrics (door to needle, door to balloon, time to antibiotics)
- [ ] Document code events

**Emergency Documentation**:
- [ ] Real-time documentation
- [ ] Emergency-specific templates
- [ ] Time tracking
- [ ] Team documentation
- [ ] Handoff documentation
- [ ] Disposition tracking

#### Technical Notes
- Triage algorithm implementation
- Emergency protocol activation system
- Critical time metric tracking
- Emergency SEP creation (special handling)
- Integration with BPJS VClaim API
- Rapid registration workflow
- Mobile-optimized for emergency use

---

### Epic 13: Reporting & Analytics

**Epic ID**: EPIC-013
**Business Value**: Provides visibility into operations and clinical quality - essential for decision-making
**Complexity**: Medium
**Estimated Duration**: 3-4 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration)
- Epic 3 (Medical Records)
- Epic 4 (Outpatient Management)
- Epic 5 (Inpatient Management)
- Epic 9 (Billing)

#### Key User Stories

1. As a hospital administrator, I want to see daily operational statistics so that I can manage resources
2. As a quality officer, I want clinical quality reports so that I can monitor care standards
3. As a finance manager, I want revenue reports so that I can track financial performance
4. As a hospital director, I want executive dashboards so that I can make strategic decisions
5. As a reporting staff, I want to generate regulatory reports automatically so that compliance is ensured

#### Acceptance Criteria

**Operational Reports**:
- [ ] Daily census (inpatient, outpatient, emergency)
- [ ] Department utilization rates
- [ ] Bed occupancy rates
- [ ] Average length of stay
- [ ] Patient wait times
- [ ] Staff productivity metrics
- [ ] Queue analytics

**Clinical Quality Reports**:
- [ ] Medical record completeness (>95%)
- [ ] Medication error rate (<0.5%)
- [ ] Diagnosis coding accuracy (>90%)
- [ ] Lab result TAT (<24 hours)
- [ ] Readmission rates
- [ ] Complication rates
- [ ] Mortality rates
- [ ] Patient satisfaction scores

**Financial Reports**:
- [ ] Revenue reports (daily, monthly, yearly)
- [ ] Expense reports
- [ ] Profitability analysis
- [ ] BPJS claim analytics (submission rate, approval rate, rejection reasons, payment timeliness)
- [ ] Aging reports (accounts receivable)
- [ ] Cost per patient visit
- [ ] Revenue by department
- [ ] Insurance payment analysis

**Regulatory Reports**:
- [ ] SIRS (Sistem Informasi Rumah Sakit Terpadu) reporting
- [ ] Kemenkes reporting
- [ ] BPJS reporting requirements
- [ ] Automated report submission
- [ ] Report scheduling
- [ ] Report archiving

**Executive Dashboards**:
- [ ] Real-time operational overview
- [ ] Key performance indicators (KPIs)
- [ ] Trends and patterns
- [ ] Drill-down capabilities
- [ ] Customizable dashboards
- [ ] Mobile access

**Export & Scheduling**:
- [ ] Export to PDF, Excel, CSV
- [ ] Schedule automated reports
- [ ] Email reports
- [ ] Report templates
- [ ] Custom report builder

#### Technical Notes
- Business intelligence framework
- Data warehouse for analytics
- Scheduled report generation
- Export to multiple formats
- Dashboard framework
- Data visualization library
- Automated report submission to regulatory bodies

---

### Epic 14: User Management & Training

**Epic ID**: EPIC-014
**Business Value**: Ensures system is used effectively and securely - critical for adoption and compliance
**Complexity**: Low-Medium
**Estimated Duration**: 2-3 weeks

#### Dependencies
- Epic 1 (Foundation & Security)

#### Key User Stories

1. As an IT administrator, I want to manage users and roles easily so that staff have appropriate access
2. As a department head, I want to request access for my staff so that they can start using the system
3. As a training coordinator, I want to track training completion so that compliance is ensured
4. As a user, I want to access help documentation easily so that I can learn to use the system
5. As an auditor, I want to see user access logs so that compliance can be verified

#### Acceptance Criteria

**User Management**:
- [ ] Create, update, deactivate users
- [ ] Assign roles and permissions
- [ ] Department-based access
- [ ] User profile management
- [ ] Bulk user import
- [ ] User access request workflow
- [ ] Password reset functionality
- [ ] User activity logs

**Role & Permission Management**:
- [ ] Define custom roles
- [ ] Assign permissions to roles
- [ ] Hierarchical roles (Superadmin > Admin > User)
- [ ] Resource-based permissions
- [ ] Action-based permissions
- [ ] Data-level permissions
- [ ] Emergency access roles

**Training Management**:
- [ ] Training module assignment
- [ ] Training progress tracking
- [ ] Training completion reporting
- [ ] Training materials repository
- [ ] User guides and manuals
- [ ] Video tutorials
- [ ] Interactive tutorials
- [ ] Training completion >90%

**Help & Support**:
- [ ] In-application help
- [ ] Context-sensitive help
- [ ] FAQ system
- [ ] Support ticket system
- [ ] Knowledge base
- [ ] Search functionality

**Audit & Compliance**:
- [ ] User access logs
- [ ] Permission change logs
- [ ] Training completion logs
- [ ] Compliance reports
- [ ] Audit trail export

#### Technical Notes
- User management interface
- Role-based access control UI
- Training content management system
- Help documentation platform
- Support ticketing system
- Audit reporting

---

### Epic 15: System Configuration & Master Data

**Epic ID**: EPIC-015
**Business Value**: Allows system customization for different hospitals - essential for flexibility
**Complexity**: Medium
**Estimated Duration**: 3-4 weeks

#### Dependencies
- Epic 1 (Foundation & Security)

#### Key User Stories

1. As a system administrator, I want to configure hospital information so that documents are branded correctly
2. As a system administrator, I want to manage department structure so that access control works properly
3. As a system administrator, I want to manage master data (ICD-10, LOINC, drugs) so that clinical decisions are accurate
4. As a system administrator, I want to configure billing rules so that invoices are generated correctly
5. As a system administrator, I want to manage integration settings so that external APIs work properly

#### Acceptance Criteria

**Hospital Configuration**:
- [ ] Hospital profile (name, address, contact, license, BPJS PPK code)
- [ ] Department structure (wards, polyclinics, units)
- [ ] Room and bed configuration
- [ ] Doctor and staff directory
- [ ] Working hours and shifts
- [ ] Hospital branding (logo, letterhead)

**Master Data Management**:
- [ ] ICD-10-CM Indonesia database
- [ ] LOINC database
- [ ] Drug formulary (generic and brand names)
- [ ] BPJS drug codes
- [ ] Procedure codes
- [ ] Room classes and rates
- [ ] Insurance companies and plans
- [ ] Reference data management

**Billing Configuration**:
- [ ] Billing rules setup
- [ ] Package rates configuration
- [ ] Discount rules
- [ ] Co-payment rules
- [ ] Invoice templates
- [ ] Receipt templates
- [ ] Tax configuration

**Integration Configuration**:
- [ ] BPJS API credentials (Cons-ID, Secret Key)
- [ ] BPJS API settings (sandbox/production)
- [ ] SATUSEHAT OAuth credentials
- [ ] SATUSEHAT client ID
- [ ] SMS gateway settings
- [ ] Email server settings
- [ ] Payment gateway settings
- [ ] External system endpoints

**System Settings**:
- [ ] System-wide settings
- [ ] Feature flags
- [ ] Notification preferences
- [ ] Backup settings
- [ ] Security settings
- [ ] Performance tuning parameters

#### Technical Notes
- Configuration management interface
- Master data import/export
- Data validation
- Reference data synchronization
- Configuration versioning
- Settings management UI

---

## Implementation Timeline

### Phase 1: MVP (Months 1-6)

#### Month 1-2: Foundation
- Epic 1: Foundation & Security Infrastructure (Weeks 1-6)
- Epic 15: System Configuration & Master Data (Weeks 3-6, parallel with Epic 1)
- Epic 14: User Management & Training (Weeks 5-8, parallel)

#### Month 2-3: Core Clinical
- Epic 2: Patient Registration & Queue Management (Weeks 7-10)
- Epic 3: Medical Records & Clinical Documentation (Weeks 9-14)

#### Month 3-4: Care Management
- Epic 4: Outpatient Management (Weeks 13-17)
- Epic 5: Inpatient Management (Weeks 15-20)

#### Month 4-5: Support Services
- Epic 6: Pharmacy Management (Weeks 18-22)
- Epic 10: BPJS Integration (Weeks 15-19, overlaps with care management)

#### Month 5-6: Financial & Compliance
- Epic 9: Billing, Finance & Claims (Weeks 21-26)
- Epic 11: SATUSEHAT Integration - Level 1 (Weeks 23-26)

#### Month 6: Testing & Deployment
- Integration testing (Weeks 25-26)
- BPJS certification (Week 26)
- SATUSEHAT Level 1 certification (Week 26)
- Pilot deployment preparation (Weeks 25-26)

---

### Phase 2: Advanced Features (Months 7-12)

#### Month 7-8: Clinical Support
- Epic 7: Laboratory Information System (Weeks 27-32)
- Epic 8: Radiology Information System (Weeks 31-36)

#### Month 8-9: Emergency & Analytics
- Epic 12: Emergency Department (Weeks 35-39)
- Epic 13: Reporting & Analytics (Weeks 37-40)

#### Month 10-11: Advanced Integration
- Epic 11: SATUSEHAT Integration - Level 2 (Weeks 41-46)
- BPJS Aplicare integration (Weeks 41-42)

#### Month 11-12: Mobile & Polish
- Mobile apps development (iOS/Android) (Weeks 45-52)
- Performance optimization (Weeks 49-52)
- User feedback iteration (Weeks 45-52)

---

### Phase 3: Strategic Features (Months 13-24)

#### Telemedicine Platform
- Video consultations
- Remote monitoring
- Patient portal
- Online prescriptions

#### Advanced Analytics
- Business intelligence dashboards
- Population health
- Predictive analytics
- Performance metrics

#### AI Clinical Decision Support
- Diagnosis prediction
- Advanced drug interaction checking
- Treatment recommendations
- Alert fatigue reduction

#### Advanced Integration
- SATUSEHAT Level 3 certification
- Additional insurance providers
- Third-party system integrations
- Health information exchange

#### Enterprise Features
- Multi-hospital deployments
- Hospital networks
- Centralized reporting
- Shared services

---

## Epic Summary Table

| Epic ID | Epic Name | Complexity | Duration | Phase | Dependencies |
|---------|-----------|------------|----------|-------|--------------|
| EPIC-001 | Foundation & Security | High | 4-6 weeks | MVP | None |
| EPIC-002 | Patient Registration | Medium | 3-4 weeks | MVP | EPIC-001 |
| EPIC-003 | Medical Records | High | 5-6 weeks | MVP | EPIC-001, EPIC-002 |
| EPIC-004 | Outpatient Management | Med-High | 4-5 weeks | MVP | EPIC-001, EPIC-002, EPIC-003 |
| EPIC-005 | Inpatient Management | High | 5-6 weeks | MVP | EPIC-001, EPIC-002, EPIC-003 |
| EPIC-006 | Pharmacy Management | Med-High | 4-5 weeks | MVP | EPIC-001, EPIC-002, EPIC-003 |
| EPIC-007 | Laboratory System | High | 5-6 weeks | Phase 2 | EPIC-001, EPIC-002, EPIC-003 |
| EPIC-008 | Radiology System | High | 5-6 weeks | Phase 2 | EPIC-001, EPIC-002, EPIC-003 |
| EPIC-009 | Billing & Finance | High | 5-6 weeks | MVP | EPIC-001, EPIC-002, EPIC-004, EPIC-005 |
| EPIC-010 | BPJS Integration | High | 4-5 weeks | MVP | EPIC-001, EPIC-002 |
| EPIC-011 | SATUSEHAT Integration | High | 4-6 weeks | MVP+ | EPIC-001, EPIC-003 |
| EPIC-012 | Emergency Department | High | 4-5 weeks | Phase 2 | EPIC-001, EPIC-002, EPIC-003, EPIC-004 |
| EPIC-013 | Reporting & Analytics | Medium | 3-4 weeks | Phase 2 | Multiple |
| EPIC-014 | User Management | Low-Med | 2-3 weeks | MVP | EPIC-001 |
| EPIC-015 | System Configuration | Medium | 3-4 weeks | MVP | EPIC-001 |
| EPIC-016 | Mobile App (React Native) | High | 8-10 weeks | Phase 2 | Multiple |
| EPIC-017 | Analytics Dashboard | High | 5-6 weeks | Phase 2 | Multiple |
| EPIC-018 | Telemedicine Platform | High | 6-8 weeks | Phase 2 | EPIC-001, EPIC-002, EPIC-003, EPIC-004 |
| EPIC-019 | AI Diagnosis Assistant | High | 8-10 weeks | Phase 3 | EPIC-001, EPIC-003, EPIC-004, EPIC-007, EPIC-008 |
| EPIC-020 | Advanced Inventory Management | Medium | 4-5 weeks | Phase 2 | EPIC-001, EPIC-006 |
| EPIC-021 | Staff Portal | Medium-High | 4-5 weeks | Phase 2 | EPIC-001, EPIC-014, EPIC-015 |
| EPIC-022 | Patient Portal | High | 5-6 weeks | Phase 2 | Multiple |
| EPIC-023 | Notification System | Medium | 4-5 weeks | MVP+ | EPIC-001 |
| EPIC-024 | Advanced Reporting | Medium | 3-4 weeks | Phase 2 | Multiple |
| EPIC-025 | Integration Hub (HL7/FHIR) | High | 6-8 weeks | Phase 2 | EPIC-001, EPIC-003, EPIC-010, EPIC-011, EPIC-007, EPIC-008 |

---

## Risk Assessment by Epic

### High Risk Epics (require early attention)
1. **EPIC-001 (Foundation)**: Failure here blocks everything
2. **EPIC-010 (BPJS Integration)**: External dependency, certification critical
3. **EPIC-011 (SATUSEHAT)**: External dependency, evolving platform
4. **EPIC-003 (Medical Records)**: Complex clinical workflows, critical for care
5. **EPIC-016 (Mobile App)**: Cross-platform complexity, offline-first architecture
6. **EPIC-018 (Telemedicine)**: WebRTC integration, real-time video streaming
7. **EPIC-019 (AI Diagnosis)**: ML model complexity, regulatory approval, accuracy requirements
8. **EPIC-022 (Patient Portal)**: Security compliance, data privacy, user experience
9. **EPIC-025 (Integration Hub)**: Multiple standards (HL7/FHIR), third-party dependencies

### Medium Risk Epics
1. **EPIC-004 (Outpatient)**: Core workflow, high usage
2. **EPIC-005 (Inpatient)**: Complex workflows, revenue impact
3. **EPIC-009 (Billing)**: Financial impact, regulatory requirements
4. **EPIC-007 (Laboratory)**: Instrument integration challenges
5. **EPIC-008 (Radiology)**: PACS integration complexity
6. **EPIC-017 (Analytics Dashboard)**: Data warehouse complexity, ETL pipelines
7. **EPIC-020 (Advanced Inventory)**: Predictive analytics, multi-location tracking
8. **EPIC-021 (Staff Portal)**: HR/payroll integration, data privacy
9. **EPIC-023 (Notification System)**: Multi-channel delivery, cost management
10. **EPIC-024 (Advanced Reporting)**: Complex query builder, performance optimization

### Lower Risk Epics
1. **EPIC-002 (Registration)**: Well-defined scope
2. **EPIC-006 (Pharmacy)**: Established patterns
3. **EPIC-012 (Emergency)**: Specialized but contained
4. **EPIC-013 (Reporting)**: Can be phased in
5. **EPIC-014 (User Management)**: Standard functionality
6. **EPIC-015 (Configuration)**: Mostly setup work

---

## Success Criteria by Epic

### MVP Success (All MVP epics must meet these)
- [ ] All acceptance criteria met
- [ ] Security audit passed
- [ ] BPJS certification obtained
- [ ] SATUSEHAT Level 1 certified
- [ ] Performance benchmarks met (<500ms response time)
- [ ] Offline capabilities functional
- [ ] User testing completed with >80% satisfaction

### Phase 2 Success
- [ ] All Phase 2 epics delivered
- [ ] SATUSEHAT Level 2 certified
- [ ] Mobile apps launched
- [ ] Clinical quality metrics met
- [ ] User adoption >80%

### Phase 3 Success
- [ ] SATUSEHAT Level 3 certified
- [ ] Telemedicine operational
- [ ] Advanced analytics deployed
- [ ] Multi-hospital deployments
- [ ] 50-100 hospitals live

---

**Document Version:** 1.1
**Last Updated:** 2026-01-15
**Status:** Draft - Ready for Review
**Next Review:** After Architecture Approval

---

## What's New in Version 1.1

Added 10 new advanced epics for Phase 2 and Phase 3 development:
- **EPIC-016**: Mobile App (React Native) - Cross-platform mobile application
- **EPIC-017**: Analytics Dashboard - Hospital KPIs and business intelligence
- **EPIC-018**: Telemedicine Platform - Video consultation integration
- **EPIC-019**: AI Diagnosis Assistant - ML-powered clinical decision support
- **EPIC-020**: Advanced Inventory Management - Predictive pharmacy inventory
- **EPIC-021**: Staff Portal - Self-service HR and staff management
- **EPIC-022**: Patient Portal - Patient self-service features
- **EPIC-023**: Notification System - Multi-channel notifications (SMS/Email/Push)
- **EPIC-024**: Advanced Reporting - Custom report builder and ad-hoc queries
- **EPIC-025**: Integration Hub - HL7/FHIR gateway for third-party systems

Each epic includes detailed user stories, acceptance criteria, technical architecture, and implementation phases.
