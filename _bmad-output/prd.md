# SIMRS - Hospital Information Management System
## Product Requirements Document

**Version:** 1.0
**Date:** 2026-01-13
**Status:** Draft

---

## 1. Executive Summary

### Product Vision
SIMRS (Sistem Informasi Manajemen Rumah Sakit) is a modern, comprehensive Hospital Information Management System designed specifically for Indonesian healthcare facilities. Our vision is to provide an accessible, reliable, and compliant digital platform that transforms hospital operations through technology while meeting all Indonesian regulatory requirements.

### Target Market
**Primary Market:** Indonesian healthcare facilities across all tiers:
- **RS (Rumah Sakit):** General hospitals (Type A, B, C, D)
- **RSIA (Rumah Sakit Bersalin):** Maternity hospitals
- **RSJ (Rumah Sakit Jiwa):** Psychiatric hospitals
- **RSB (Rumah Sakit Bedah):** Surgical hospitals
- **Puskesmas:** Community health centers (primary care)

**Market Context:**
- 10,378 Puskesmas nationwide (22% with limited/no internet)
- 2,900+ hospitals across Indonesia
- Growing BPJS Kesehatan coverage (95%+ population)
- Mandatory SIMRS implementation (Permenkes 82/2013)

### Key Differentiators vs SIMRS-Khanza

| Aspect | SIMRS-Khanza | Our SIMRS |
|--------|--------------|-----------|
| **Architecture** | Desktop-first (Java Swing) | Web/mobile-first (PWA) |
| **Deployment** | Client-server, local installation | Cloud-ready, Docker Compose |
| **Technology** | Java 8, MySQL 5.1 | Modern stack (FastAPI/Next.js, PostgreSQL) |
| **Offline Support** | Limited | Full offline-first PWA |
| **UI/UX** | Traditional desktop UI | Modern, responsive web UI |
| **Mobile Access** | Minimal | Native mobile apps |
| **Integration** | Mature BPJS, basic SATUSEHAT | Full BPJS + SATUSEHAT FHIR R4 |
| **Database** | 1,116 tables (complex) | Simplified, normalized schema |
| **Updates** | Manual updates | Over-the-air updates |
| **Scalability** | Monolithic | Microservices-ready |

**Unique Value Propositions:**
1. **Offline-First Architecture:** Critical for 22% of Puskesmas with limited internet
2. **Modern Web Interface:** Accessible from any device, no installation required
3. **SATUSEHAT-Native:** Built on FHIR R4 from the ground up
4. **Indonesian Healthcare Expertise:** Deep BPJS and local regulatory compliance
5. **Simplified Deployment:** One-command Docker setup vs complex installation
6. **Mobile-First Design:** Native apps for doctors, nurses, and patients
7. **Scalable Architecture:** Grows from small clinics to large hospital networks

---

## 2. Problem Statement

### Current Challenges in Indonesian Healthcare IT

#### 2.1 Infrastructure Limitations
- **Internet Connectivity:** 21-22% of Puskesmas have limited or no internet access (29-49% in Papua/Maluku)
- **Hardware Constraints:** 60.7% of facilities have only 4GB RAM, 43.7% use Intel i3 CPUs
- **Power Reliability:** 8.02% lack 24-hour electricity
- **IT Talent Shortage:** Limited technical expertise outside major cities

#### 2.2 Regulatory Burden
- **Complex Compliance:** Multiple overlapping regulations (Permenkes 82/2013, 24/2022, UU 27/2022)
- **Mandatory Integrations:** BPJS Kesehatan, SATUSEHAT, Ministry of Health reporting
- **Data Retention:** 10-25 year retention requirements for medical records
- **Strict Security:** Personal data protection law (UU 27/2022) with severe penalties

#### 2.3 Existing Solution Limitations

**SIMRS-Khanza (Market Leader) Weaknesses:**
1. **Desktop-Only:** Requires local installation, cannot access remotely
2. **Dated Technology:** Java 8, Swing UI, no modern web/mobile support
3. **Complex Deployment:** Difficult installation, maintenance burden
4. **Limited Offline:** No true offline capabilities
5. **Poor Mobile Experience:** Not optimized for smartphones/tablets
6. **Manual Updates:** Time-consuming update process
7. **Schema Complexity:** 1,116 tables creates maintenance challenges

**Commercial Solutions:**
- **Expensive:** Prohibitively costly for small hospitals/Puskesmas
- **Foreign Systems:** Poor Indonesian localization and BPJS integration
- **Rigid:** Cannot adapt to local workflows
- **Vendor Lock-in:** Difficult to customize or extend

#### 2.4 Operational Pain Points
- **Paper-Based Processes:** Many departments still use manual records
- **Siloed Systems:** Poor integration between departments
- **BPJS Claim Rejections:** Incomplete data causing payment delays
- **Patient Data Fragmentation:** Incomplete medical histories
- **Inefficient Workflows:** Time wasted on manual tasks
- **Poor Decision Making:** Lack of real-time analytics

---

## 3. Goals & Success Metrics

### Primary Objectives

#### 3.1 Strategic Goals (12 Months)
1. **Launch MVP:** Core modules for basic hospital operations
2. **BPJS Compliance:** Full VClaim API integration and certification
3. **SATUSEHAT Integration:** FHIR R4 Level 2 (Terintegrasi) certification
4. **Pilot Deployments:** 5-10 early adopter hospitals
5. **Regulatory Approval:** Permenkes 82/2013 and 24/2022 compliance

#### 3.2 Product Goals
1. **User Adoption:** >80% staff adoption within 3 months of deployment
2. **System Reliability:** >99.5% uptime (downtime < 3.65 days/year)
3. **Performance:** <500ms response time for 95% of requests
4. **Offline Capability:** 100% of core features work offline
5. **Mobile Access:** Native apps for iOS and Android

#### 3.3 Business Goals
1. **Cost Effective:** 50% lower TCO than commercial alternatives
2. **Fast Implementation:** <4 weeks from contract to go-live
3. **Scalable:** Support single facilities to hospital networks
4. **Sustainable:** Open-source with enterprise support options

### Success Metrics (KPIs)

#### 3.4 Technical KPIs
| Metric | Target | Measurement |
|--------|--------|-------------|
| System Uptime | >99.5% | Monitoring system |
| Response Time (p95) | <500ms | APM tools |
| Offline Functionality | 100% core features | Testing checklist |
| Data Sync Latency | <5 minutes | Sync logs |
| API Success Rate | >99% | BPJS/SATUSEHAT logs |
| Page Load Time | <3s | Browser metrics |

#### 3.5 User KPIs
| Metric | Target | Measurement |
|--------|--------|-------------|
| User Adoption | >80% within 3 months | Usage analytics |
| User Satisfaction | >4/5 stars | User surveys |
| Training Completion | >90% of staff | LMS tracking |
| Error Rate | <1% of operations | Error logs |
| Support Tickets | <5 tickets/100 users | Help desk system |

#### 3.6 Business KPIs
| Metric | Target | Measurement |
|--------|--------|-------------|
| Implementation Time | <4 weeks | Project tracking |
| Claim Approval Rate | >95% | BPJS reports |
| Time to Payment | <30 days | Financial reports |
| Cost per Patient Visit | Reduce 20% | Cost accounting |
| Patient Wait Time | Reduce 30% | Queue management |

#### 3.7 Clinical KPIs
| Metric | Target | Measurement |
|--------|--------|-------------|
| Medical Record Completeness | >95% | Chart audits |
| Medication Error Rate | <0.5% | Incident reports |
| Diagnosis Coding Accuracy | >90% | Claim audits |
| Lab Result TAT | <24 hours | Lab system |
| Patient Satisfaction | >4/5 | Patient surveys |

---

## 4. Target Users & Personas

### User Segments

#### 4.1 Hospital Administrators
**Role:** Direktur, Direktur Pelayanan, Kepala Instalasi

**Responsibilities:**
- Overall hospital operations
- Regulatory compliance
- Financial performance
- Quality improvement
- Staff management

**Pain Points:**
- Lack of real-time operational visibility
- Difficulty tracking regulatory compliance
- Manual report preparation
- BPJS claim management complexity
- Budget constraints

**Key Needs:**
- Executive dashboards
- Regulatory reporting
- Financial analytics
- BPJS claim tracking
- Performance metrics

**Usage Patterns:**
- Daily: Review dashboards, approve critical items
- Weekly: Generate reports, review performance
- Monthly: Board reporting, compliance review

---

#### 4.2 Doctors (Dokter)
**Specializations:**
- Spesialis (Specialists): Internal medicine, surgery, pediatrics, etc.
- Dokter Umum (General Practitioners)
- Dokter Poli (Polyclinic doctors)

**Responsibilities:**
- Patient consultation and diagnosis
- Treatment planning
- Prescription writing
- Medical documentation
- Clinical decision making

**Pain Points:**
- Time-consuming documentation
- Difficulty accessing patient history
- Drug interaction checking burden
- BPJS SEP creation complexity
- Lack of mobile access

**Key Needs:**
- Intuitive clinical documentation
- Quick patient history access
- Electronic prescribing
- Mobile access for rounds
- Decision support tools

**Usage Patterns:**
- Continuous throughout shift
- High frequency: Patient lookup, documentation
- Critical: Must work offline in poor connectivity areas

---

#### 4.3 Nurses (Perawat)
**Roles:**
- Perawat Rawat Inap (Inpatient nurses)
- Perawat Rawat Jalan (Outpatient nurses)
- Perawat IGD (Emergency nurses)
- Perawat Anestesi (OR nurses)

**Responsibilities:**
- Patient care delivery
- Vital signs monitoring
- Medication administration
- Documentation
- Patient education

**Pain Points:**
- Paper-based charting
- Difficulty tracking medication administration
- Manual vital sign recording
- Communication gaps with doctors
- Heavy workload

**Key Needs:**
- Mobile charting at bedside
- Medication administration tracking (MAR)
- Vital signs capture
- Task management
- Doctor communication

**Usage Patterns:**
- Continuous during shift
- High volume: Documentation, vital signs
- Mobile-first: Tablet/phone usage at bedside

---

#### 4.4 Pharmacists (Apoteker)
**Roles:**
- Apoteker (Clinical pharmacists)
- Asisten Apoteker (Pharmacy assistants)
- Teknisi Farmasi (Pharmacy technicians)

**Responsibilities:**
- Prescription verification
- Drug dispensing
- Patient counseling
- Inventory management
- Clinical pharmacy services

**Pain Points:**
- Manual drug interaction checking
- Inventory management complexity
- Expiry tracking burden
- BPJS e-Claim complexity
- High prescription volume

**Key Needs:**
- Automated interaction checking
- Barcode scanning for dispensing
- Inventory alerts
- BPJS formulary integration
- Clinical decision support

**Usage Patterns:**
- Continuous during pharmacy hours
- High volume: Prescription processing
- Transactional: Process each prescription quickly

---

#### 4.5 Laboratory Staff
**Roles:**
- Pathologist (Pathologists)
- Analis Medis (Medical technologists)
- Staff Laboratorium (Lab assistants)

**Responsibilities:**
- Test processing
- Result entry and validation
- Quality control
- Equipment maintenance
- Report generation

**Pain Points:**
- Manual result entry
- Sample tracking challenges
- Quality control documentation
- Critical value notification
- LOINC coding complexity

**Key Needs:**
- Barcode sample tracking
- Instrument interfacing
- LOINC code lookup
- Critical value alerts
- Quality control dashboards

**Usage Patterns:**
- Batch processing: Process samples in groups
- Critical: STAT results require immediate attention
- Integration: Connect to analyzers and EHR

---

#### 4.6 Radiology Staff
**Roles:**
- Radiologer (Radiologists)
- Radiografer (Radiologic technologists)
- Staff Radiologi (Radiology staff)

**Responsibilities:**
- Exam performance
- Image acquisition
- Report generation
- DICOM management
- Radiation safety

**Pain Points:**
- DICOM integration complexity
- Report dictation burden
- Image storage management
- Worklist management
- Radiation dose tracking

**Key Needs:**
- PACS integration
- Modality worklist
- Report templates
- Image distribution
- Dose tracking

**Usage Patterns:**
- Exam-driven: Process orders as they come
- Critical: STAT exams for emergencies
- Integration-heavy: PACS, RIS, modalities

---

#### 4.7 Registration & Billing Staff
**Roles:**
- Staff Pendaftaran (Registration clerks)
- Kasir (Cashiers)
- Staff BPJS (Insurance specialists)
- Staff Keuangan (Finance staff)

**Responsibilities:**
- Patient registration
- Insurance verification
- Billing and invoicing
- Payment processing
- BPJS claim submission

**Pain Points:**
- BPJS eligibility checking complexity
- Manual claim preparation
- Billing errors
- Payment reconciliation
- Long patient queues

**Key Needs:**
- Quick patient lookup
- BPJS eligibility auto-check
- Automated billing
- Queue management
- Claim tracking

**Usage Patterns:**
- Transactional: Process each patient quickly
- High volume: Registration and billing
- Integration: BPJS, SATUSEHAT APIs

---

#### 4.8 IT Administrators
**Roles:**
- IT Manager
- System Administrator
- Database Administrator
- Network Engineer

**Responsibilities:**
- System deployment
- User management
- Backup and recovery
- Security management
- Technical support

**Pain Points:**
- Complex installation procedures
- Manual update processes
- Security compliance burden
- Limited technical documentation
- Troubleshooting challenges

**Key Needs:**
- Simple deployment
- Automated updates
- Security monitoring
- Backup automation
- Comprehensive documentation

**Usage Patterns:**
- Regular: Maintenance tasks
- On-demand: Troubleshooting and support
- Strategic: Planning and upgrades

---

### User Persona Example: Dr. Siti (Spesialis Penyakit Dalam)

**Background:**
- Age: 42
- Role: Internal Medicine Specialist
- Hospital: RSUD Type B in Surabaya
- Experience: 15 years practice

**Typical Day:**
- 7:00 AM: Ward rounds (20-30 inpatients)
- 9:00 AM: Polyclinic (30-40 outpatients)
- 12:00 PM: Documentation, lunch
- 1:00 PM: Continue polyclinic
- 4:00 PM: More ward rounds, consultations
- 6:00 PM: Finish

**Technology Comfort:** Moderate - uses smartphone, basic EMR, but frustrated with complex interfaces

**Goals:**
- See patients efficiently (not waste time on software)
- Access complete patient histories instantly
- Write prescriptions quickly
- Complete documentation before going home
- Monitor admitted patients remotely

**Frustrations with Current Systems:**
- Slow, laggy desktop application
- Cannot check on patients from home
- Complex prescription interface
- No mobile app for rounds
- System crashes when internet is slow

**What Would Delight:**
- Fast, responsive interface
- Mobile app for rounds
- Offline capabilities for slow network
- Quick prescription writing with drug interaction checks
- Patient summary at a glance

---

## 5. Core Features by Module

### 5.1 Patient Registration (Pendaftaran)

#### 5.1.1 New Patient Registration
**User Stories:**
- As a registration clerk, I want to register new patients quickly to reduce wait times
- As a patient, I want to provide my information once and have it stored securely

**Features:**
- Capture patient demographics:
  - NIK (Nomor Induk Kependudukan) - primary identifier
  - Full name (nama lengkap)
  - Date of birth (tanggal lahir)
  - Place of birth (tempat lahir)
  - Gender (jenis kelamin)
  - Address (complete with province, regency, district, village)
  - Phone number (no. telepon)
  - Email (optional)
- Generate medical record number (no. RM)
- BPJS card validation:
  - Verify BPJS membership via VClaim API
  - Check eligibility (peserta status)
  - Display member information
- NIK validation (optional Dukcapil integration)
- Patient photo capture (optional)
- Emergency contact information
- Family/patient responsible party (penanggung jawab)
- Insurance information capture (BPJS, Asuransi, Umum)

**Acceptance Criteria:**
- Registration time < 3 minutes per patient
- BPJS eligibility check completes in < 5 seconds
- Auto-generate unique medical record number
- Validate NIK format (16 digits)
- Duplicate patient detection (by NIK or name+DOB)

#### 5.1.2 Returning Patient Registration
**Features:**
- Search existing patients by:
  - Medical record number (no. RM)
  - BPJS card number
  - NIK
  - Name + date of birth
  - Phone number
- Quick check-in (registrasi kunjungan)
- Update patient information if changed
- Verify current insurance status
- Select visit type (Poli, IGD, Rawat Inap)
- Queue number generation

**Acceptance Criteria:**
- Patient lookup time < 10 seconds
- Support multiple search methods
- Display last visit date and diagnoses
- Highlight changes in patient information

#### 5.1.3 Online Booking Integration
**Features:**
- Patient self-service booking portal
- Display available appointment slots
- Select doctor and polyclinic
- Receive booking confirmation (SMS/WhatsApp)
- Queue management integration
- Cancel/reschedule appointments
- Mobile JKN API integration (BPJS appointment)

**Acceptance Criteria:**
- Real-time availability display
- Confirm booking immediately
- Send SMS confirmation
- Sync with hospital schedule
- Support booking cancellation

#### 5.1.4 Queue Management (Antrian)
**Features:**
- Queue number generation per department:
  - Pendaftaran (Registration)
  - Poli (Polyclinic)
  - Farmasi (Pharmacy)
  - Laboratorium
  - Radiologi
  - Kasir (Billing)
- Digital queue display screens
- SMS queue notifications
- Queue status via mobile app
- Priority queue management:
  - Elderly (lansia)
  - Pregnant women (ibu hamil)
  - Disabled (difabel)
  - Emergency cases
- Queue analytics and reporting

**Acceptance Criteria:**
- Real-time queue updates
- Mobile queue number access
- Average wait time display
- Queue priority rules enforced
- BPJS Antrean API integration

---

### 5.2 Medical Records (Rekam Medis)

#### 5.2.1 Patient History
**Features:**
- Comprehensive patient profile:
  - Demographics
  - Contact information
  - Insurance information
  - Emergency contacts
- Medical history timeline:
  - Past visits (encounters)
  - Hospitalizations
  - Surgeries
  - Allergies
  - Chronic conditions
- Family medical history
- Social history (smoking, alcohol, occupation)
- Immunization records

**Acceptance Criteria:**
- Display complete history in single view
- Timeline visualization
- Quick access to recent visits
- Search by date range
- Export to PDF (patient copy)

#### 5.2.2 Problem List (ICD-10-CM Indonesia)
**Features:**
- Maintain active problem list
- ICD-10-CM diagnosis coding:
  - Search by code or description
  - Indonesian terminology
  - Code validation
  - Common codes favorites
- Problem status tracking:
  - Active
  - Resolved
  - Chronic
  - Acute
- Onset date recording
- Recorder attribution (who diagnosed)
- Problem linkage to encounters

**Acceptance Criteria:**
- ICD-10 code lookup < 5 seconds
- Display Indonesian descriptions
- Track problem resolution
- Link problems to encounters
- Show problem history

#### 5.2.3 Allergy Tracking
**Features:**
- Drug allergy recording:
  - Allergen (medication)
  - Reaction (rash, anaphylaxis, etc.)
  - Severity (mild, moderate, severe)
  - Onset date
  - Source (patient-reported, tested)
- Food allergy recording
- Environmental allergy recording
- Allergy alerts:
  - Display prominently in patient banner
  - Alert during prescription writing
  - Warning before administering medication
- "No Known Allergies" (NKA) option

**Acceptance Criteria:**
- Allergy alerts always visible
- Prevent prescribing allergens
- Document allergy source
- Display reaction and severity
- Support multiple allergies

#### 5.2.4 Medication List
**Features:**
- Current medication list:
  - Drug name (generic and brand)
  - Dose and frequency
  - Route of administration
  - Start date
  - Prescribing doctor
  - Indication (reason for use)
- Medication history
- Discontinued medications with reason
- Drug interaction checking
- Duplicate therapy warnings

**Acceptance Criteria:**
- Show active medications prominently
- Alert for interactions
- Detect duplicate therapies
- Track medication changes
- Medication reconciliation on admission

#### 5.2.5 Clinical Notes
**Features:**
- Structured documentation templates:
  - SOAP notes (Subjective, Objective, Assessment, Plan)
  - Admission notes
  - Progress notes
  - Discharge summaries
  - Consultation notes
  - Procedure notes
- Free text option with auto-save
- Voice-to-text dictation (optional)
- Digital signature required for attestation
- Version control with audit trail
- Note sharing (with patient consent)

**Acceptance Criteria:**
- Auto-save every 30 seconds
- Require digital signature
- Track all changes with audit trail
- Support structured and free text
- Export to PDF

---

### 5.3 Outpatient Management (Poli Rawat Jalan)

#### 5.3.1 Doctor Consultation Workflow
**Features:**
- Encounter management:
  - Start consultation
  - Patient information display
  - Vital signs review
  - Medical history review
  - Current medication review
- Clinical documentation:
  - Chief complaint
  - History of present illness
  - Physical examination
  - Assessment (diagnosis)
  - Treatment plan
- Quick diagnosis entry (ICD-10 codes)
- Prescription writing
- Lab/radiology ordering
- Return appointment scheduling
- Patient education materials

**Acceptance Criteria:**
- Start consultation in < 5 seconds
- Display patient summary
- Auto-populate common templates
- Save progress automatically
- Complete encounter in < 10 minutes

#### 5.3.2 Prescription Management
**Features:**
- Electronic prescribing:
  - Drug search (generic and brand)
  - Auto-complete suggestions
  - Dose and frequency selection
  - Quantity calculation
  - Route of administration
  - Special instructions
- Drug interaction checking:
  - Drug-drug interactions
  - Drug-disease interactions
  - Drug-allergy interactions
  - Contraindications
- BPJS formulary checking:
  - Covered status
  - Prior authorization requirements
  - Generic substitution requirements
- Prescription printing:
  - Hospital copy
  - Patient copy
  - Barcode for pharmacy
- Electronic prescription to pharmacy

**Acceptance Criteria:**
- Check interactions in < 3 seconds
- Alert for all interactions
- Display BPJS coverage status
- Print prescriptions with barcode
- Support compound prescriptions (racikan)

#### 5.3.3 Lab/Radiology Requests
**Features:**
- Electronic ordering:
  - Test catalog search
  - Package selection (panel)
  - Clinical indication
  - Priority (routine, urgent, STAT)
  - Insurance pre-authorization
- Order tracking:
  - Status updates
  - Result notifications
  - Critical value alerts
- Integration with SATUSEHAT:
  - FHIR ServiceRequest
  - LOINC coding for lab
  - Procedure codes for radiology

**Acceptance Criteria:**
- Complete order in < 2 minutes
- Auto-select LOINC codes
- Check insurance coverage
- Track order status
- Alert when results ready

#### 5.3.4 BPJS SEP Generation
**Features:**
- Automatic SEP creation:
  - Patient eligibility verified
  - Diagnosis populated
  - Polyclinic mapped
  - Doctor assigned
- SEP updates:
  - Room changes
  - Diagnosis updates
  - Policy changes
- SEP cancellation
- SEP history tracking
- BPJS VClaim API integration

**Acceptance Criteria:**
- Generate SEP in < 10 seconds
- Validate all required fields
- Handle BPJS API failures gracefully
- Track all SEP changes
- Display SEP status

---

### 5.4 Inpatient Management (Rawat Inap)

#### 5.4.1 Bed Management
**Features:**
- Real-time bed availability:
  - Total beds per room
  - Occupied beds
  - Available beds
  - Maintenance beds
- Bed assignment:
  - View bed by ward/room
  - Filter by class (VVIP, VIP, 1, 2, 3)
  - Filter by gender (male/female/mixed)
  - Assign patient to bed
  - Transfer patient between beds
- Room status:
  - Clean/soiled status
  - Maintenance status
  - Isolation rooms
- Bed request workflow:
  - Request bed
  - Approve request
  - Assign bed
  - Notify patient
- BPJS Aplicare integration (real-time bed reporting)

**Acceptance Criteria:**
- Real-time bed updates
- Assign bed in < 30 seconds
- Prevent double-booking
- Sync with BPJS Aplicare
- Display bed availability dashboard

#### 5.4.2 Room/Ward Assignment
**Features:**
- Admission workflow:
  - Verify doctor's admission order
  - Check bed availability
  - Select room and bed
  - Update BPJS SEP
  - Generate admission papers
- Room transfer:
  - Initiate transfer
  - Get approval
  - Update bed assignment
  - Update BPJS SEP (room class change)
- Discharge planning:
  - Estimated discharge date
  - Discharge criteria tracking
  - Discharge checklist

**Acceptance Criteria:**
- Complete admission in < 5 minutes
- Update BPJS SEP automatically
- Track all bed changes
- Prevent room conflicts
- Support room transfers

#### 5.4.3 Daily Care Notes
**Features:**
- Nursing documentation:
  - Flow sheets (vital signs, intake/output)
  - Narrative notes
  - Care plans
  - Patient education
- Physician progress notes:
  - Daily rounds notes
  - Assessment and plan
  - Orders and treatments
- Interdisciplinary notes:
  - Respiratory therapy
  - Physical therapy
  - Nutrition
  - Social work
- Shift documentation:
  - Shift handoff
  - Change of shift report
- Template-based and free text

**Acceptance Criteria:**
- Document care in real-time
- Auto-save documentation
- Require digital signature
- Support care plans
- Export to discharge summary

#### 5.4.4 Discharge Planning
**Features:**
- Discharge readiness assessment:
  - Clinical stability
  - Medication reconciliation
  - Patient education completed
  - Follow-up appointments scheduled
- Discharge orders:
  - Discharge medications
  - Discharge instructions
  - Activity restrictions
  - Diet recommendations
  - Follow-up appointments
- Discharge summary generation:
  - Admission diagnosis
  - Procedures performed
  - Course of treatment
  - Discharge diagnosis
  - Discharge medications
  - Follow-up plan
- BPJS claim finalization

**Acceptance Criteria:**
- Complete discharge in < 30 minutes
- Generate discharge summary automatically
- Reconcile medications
- Schedule follow-up appointments
- Finalize BPJS claim

#### 5.4.5 BPJS SEP Continuity
**Features:**
- SEP creation on admission:
  - Inpatient service type (jnsPelayanan = 1)
  - Room class assignment
  - Initial diagnosis
- SEP updates during stay:
  - Room class changes
  - Diagnosis updates
  - Doctor changes
  - Policy changes
- SEP closure on discharge:
  - Final diagnosis
  - Discharge disposition
  - Length of stay
- Inacbg grouper integration:
  - Generate grouping data
  - Calculate package rate
  - Adjust for ICU/ventilator

**Acceptance Criteria:**
- Create SEP within 24 hours of admission
- Update SEP for all changes
- Close SEP on discharge
- Generate Inacbg data
- Track SEP lifecycle

---

### 5.5 Emergency Department (IGD)

#### 5.5.1 Tiage System
**Features:**
- Indonesian triage categories:
  - **KUNING (Yellow):** Semi-urgent, can wait
  - **MERAH (Red):** Emergency, immediate attention
  - **HIJAU (Green):** Non-urgent, routine care
  - **HITAM (Black):** Deceased/DOA (dead on arrival)
- Triage assessment:
  - Vital signs capture
  - Chief complaint
  - Primary assessment (ABCDE)
  - Triage score calculation
- Triage reassessment:
  - Periodic reassessment
  - Update triage category
- Triage analytics:
  - Wait times by category
  - Patient acuity distribution
  - Resource utilization

**Acceptance Criteria:**
- Complete triage in < 5 minutes
- Assign appropriate category
- Display category prominently
- Reassess periodically
- Track triage metrics

#### 5.5.2 Rapid Registration
**Features:**
- Quick patient registration:
  - Minimal required fields
  - Register later for complete data
- Unknown patient registration (John Doe)
- BPJS quick check:
  - Verify eligibility
  - Create emergency SEP
- Emergency sticker/tag generation:
  - Patient barcode
  - Triage category
  - Allergy alert
- Auto-assign to emergency bed

**Acceptance Criteria:**
- Register patient in < 2 minutes
- Verify BPJS in < 10 seconds
- Create emergency SEP
- Generate patient ID band
- Assign bed automatically

#### 5.5.3 Emergency Protocols
**Features:**
- Clinical decision support:
  - CPR protocols
  - Emergency drug dosing
  - Emergency procedures
- Emergency order sets:
  - Trauma activation
  - Stroke activation
  - STEMI activation
  - Sepsis protocol
- Rapid response team activation
- Code blue documentation
- Time tracking:
  - Door to needle time
  - Door to balloon time
  - Time to antibiotics

**Acceptance Criteria:**
- Activate protocols with one click
- Display emergency drug dosing
- Track critical time metrics
- Document code events
- Support team activation

---

### 5.6 Pharmacy (Farmasi)

#### 5.6.1 Inventory Management
**Features:**
- Drug master file:
  - Generic name
  - Brand names
  - Dosage forms and strengths
  - BPJS drug codes
  - e-Katalog codes
  - Manufacturer information
- Stock management:
  - Current stock levels
  - Bin locations
  - Expiry dates
  - Batch numbers
- Stock transactions:
  - Purchase orders
  - Goods received
  - Stock adjustments
  - Stock transfers
  - Returns to supplier
- Expiry monitoring:
  - Near-expiry alerts (3 months)
  - Expired drug quarantine
  - First-in-first-out (FIFO) dispensing
- Minimum stock levels:
  - Reorder point alerts
  - Maximum stock levels
  - Economic order quantity

**Acceptance Criteria:**
- Real-time stock updates
- Alert for near-expiry drugs
- Prevent dispensing expired drugs
- Auto-generate purchase orders
- Track stock movements

#### 5.6.2 Prescription Dispensing
**Features:**
- Electronic prescription processing:
  - Receive prescriptions electronically
  - Queue by priority
  - Barcode patient verification
- Dispensing workflow:
  - Verify prescription
  - Check drug interactions
  - Check stock availability
  - Select drug (with barcode scan)
  - Count/package medication
  - Label generation
  - Pharmacist verification
- Barcode scanning:
  - Scan drug barcode
  - Verify correct drug
  - Verify correct dose
  - Prevent dispensing errors
- Patient counseling documentation
- Dispensing history

**Acceptance Criteria:**
- Process prescription in < 5 minutes
- Barcode scan all drugs
- Verify patient identity
- Check all interactions
- Document counseling

#### 5.6.3 Drug Interactions Checking
**Features:**
- Interaction types:
  - Drug-drug interactions
  - Drug-disease interactions
  - Drug-allergy interactions
  - Drug-food interactions
  - Therapeutic duplications
- Severity levels:
  - Contraindicated (do not use)
  - Severe (avoid combination)
  - Moderate (use caution)
  - Mild (monitor)
- Interaction management:
  - Alert at prescribing
  - Alert at dispensing
  - Document resolution
  - Override with reason
- Custom interaction rules
- Drug interaction database updates

**Acceptance Criteria:**
- Check interactions in < 3 seconds
- Alert for all interactions
- Display severity and recommendations
- Require override reason
- Update interaction database regularly

#### 5.6.4 E-Katalog Integration
**Features:**
- E-Katalog price lookup:
  - Government procurement prices
  - Price comparison
  - Price updates
- E-Katalog product catalog:
  - Available products
  - Approved suppliers
  - Contract terms
- Purchase order integration:
  - Create PO from E-Katalog
  - Track order status
  - Receive goods
- Price variance reporting:
  - Actual vs. E-Katalog price
  - Variance approval workflow

**Acceptance Criteria:**
- Display E-Katalog prices
- Create PO from E-Katalog
- Track order delivery
- Report price variances
- Update prices automatically

---

### 5.7 Laboratory (Laboratorium)

#### 5.7.1 Test Requests
**Features:**
- Electronic test ordering:
  - Test catalog (all available tests)
  - Test panels (groups of tests)
  - Custom panels
  - Clinical indication
  - Priority (routine, urgent, STAT)
  - Specimen requirements
- Order tracking:
  - Order status
  - Sample status
  - Result status
  - TAT (turnaround time) tracking
- Sample labeling:
  - Barcode label generation
  - Patient identification
  - Test information
  - Collection date/time
- Integration with SATUSEHAT:
  - FHIR ServiceRequest
  - LOINC code assignment

**Acceptance Criteria:**
- Order tests in < 2 minutes
- Auto-assign LOINC codes
- Generate barcode labels
- Track order status
- Sync with SATUSEHAT

#### 5.7.2 Result Entry
**Features:**
- Result capture:
  - Manual result entry
  - Instrument interfacing (auto-capture)
  - Batch result entry
  - Quality control results
- Result validation:
  - Reference ranges by age/gender
  - Delta checks (change from previous)
  - Critical value flags
  - Abnormal result highlighting
- Pathologist review:
  - Review queue
  - Electronic signature
  - Comments and addendum
- Result verification:
  - Technologist verification
  - Pathologist verification
  - Verification workflow

**Acceptance Criteria:**
- Auto-capture from instruments
- Flag abnormal values
- Alert for critical values
- Require verification before release
- Track result modifications

#### 5.7.3 Quality Control
**Features:**
- QC material management:
  - QC lot tracking
  - Expiry monitoring
  - Storage conditions
- QC testing:
  - Daily QC runs
  - Levey-Jennings charts
  - Westgard rules application
  - Out-of-control alerts
- QC documentation:
  - QC results
  - Corrective actions
  - Maintenance records
- Proficiency testing:
  - PT enrollment
  - PT results tracking
  - PT performance reports

**Acceptance Criteria:**
- Run QC daily
- Plot Levey-Jennings charts
- Apply Westgard rules
- Alert for out-of-control
- Document corrective actions

#### 5.7.4 LIS Integration
**Features:**
- Instrument interfacing:
  - Bidirectional communication
  - Worklist to analyzers
  - Results from analyzers
  - Barcode-based tracking
- Middleware functionality:
  - Result formatting
  - Unit conversion
  - Result validation rules
  - Auto-verification
- Integration standards:
  - ASTM, HL7 protocols
  - DICOM for image capture
  - Proprietary analyzer interfaces

**Acceptance Criteria:**
- Interface with major analyzers
- Auto-send worklist
- Auto-capture results
- Support ASTM and HL7
- Barcode-based tracking

---

### 5.8 Radiology

#### 5.8.1 Modality Worklist
**Features:**
- Worklist management:
  - Exam scheduling
  - Worklist to modalities
  - Exam status tracking
- Modality integration:
  - DICOM MWL (Modality Worklist)
  - Send orders to equipment
  - Receive status updates
- Patient safety checks:
  - Pregnancy screening
  - Contrast allergy check
  - Kidney function (eGFR) for contrast
- Protocol selection:
  - Standard protocols by exam type
  - Custom protocols
  - Radiologist preferences

**Acceptance Criteria:**
- Send worklist to modalities
- Track exam status in real-time
- Screen for contraindications
- Select appropriate protocols
- Support DICOM MWL

#### 5.8.2 Image Management (PACS Optional)
**Features:**
- PACS integration:
  - DICOM image storage
  - Image retrieval
  - Image viewing (Web viewer)
  - Image distribution
- Modality integration:
  - Receive images from equipment
  - Store in PACS
  - Link to patient record
- Image management:
  - Image compression
  - Image lifecycle (retention)
  - Image backup
- CD burning:
  - Export images to CD/DVD
  - Include viewer
  - Patient discharge media

**Acceptance Criteria:**
- Store images in PACS
- Display images in web viewer
- Link images to reports
- Export to CD
- Meet retention requirements

#### 5.8.3 Report Generation
**Features:**
- Report templates:
  - Standard templates by modality
  - Custom templates
  - Macros and shortcuts
- Dictation support:
  - Voice recognition
  - Transcription workflow
  - Report finalization
- Report distribution:
  - Send to ordering physician
  - Upload to SATUSEHAT (DiagnosticReport)
  - Patient portal access
- Critical findings:
  - Critical value alerts
  - Direct notification to physician
  - Document communication

**Acceptance Criteria:**
- Complete report in < 5 minutes
- Use standard templates
- Alert for critical findings
- Send report to physician
- Sync with SATUSEHAT

---

### 5.9 Billing & Finance (Keuangan)

#### 5.9.1 Invoice Generation
**Features:**
- Charge capture:
  - Professional fees (doctor fees)
  - Hotel services (room charges)
  - Drugs and medications
  - Laboratory tests
  - Radiology exams
  - Procedures and treatments
  - Medical supplies
- Billing rules:
  - Package rates (BPJS INA-CBG)
  - Fee-for-service (private insurance)
  - Discount rules
  - Co-payment calculations
- Invoice generation:
  - Detailed invoice
  - Summary invoice
  - Provisional invoice
  - Final invoice
- Invoice approval workflow
- Invoice printing and emailing

**Acceptance Criteria:**
- Capture all charges
- Apply correct billing rules
- Generate accurate invoices
- Support multiple payers
- Approve invoices before discharge

#### 5.9.2 BPJS Claims Processing
**Features:**
- e-Claim data generation:
  - Generate claim file
  - Validate claim data
  - Group by INA-CBG
  - Calculate package rate
- Claim submission:
  - Submit to BPJS gateway
  - Track submission status
  - Handle submission errors
- Claim verification:
  - BPJS verification process
  - Respond to queries
  - Submit additional documents
- Claim payment tracking:
  - Payment status
  - Payment reconciliation
  - Payment posting
- Claim analytics:
  - Submission rate
  - Approval rate
  - Rejection reasons
  - Payment timeliness

**Acceptance Criteria:**
- Generate e-Claim files automatically
- Submit claims within BPJS deadline
- Track claim status
- Resolve claim queries
- Reconcile payments

#### 5.9.3 Insurance (Asuransi) Handling
**Features:**
- Insurance master:
  - Insurance companies
  - Insurance plans
  - Coverage rules
  - Pre-authorization requirements
- Eligibility verification:
  - Check coverage
  - Verify pre-auth
  - Get authorization number
- Claims processing:
  - Generate claims
  - Submit to insurance
  - Track claim status
- Coordination of benefits:
  - Primary payer (BPJS)
  - Secondary payer (private insurance)
  - Patient responsibility
- Explanation of benefits (EOB)

**Acceptance Criteria:**
- Support multiple insurance plans
- Verify eligibility
- Get pre-authorizations
- Generate insurance claims
- Coordinate benefits

#### 5.9.4 Payment Processing
**Features:**
- Payment methods:
  - Cash
  - Credit/debit cards
  - Bank transfer
  - Virtual account
  - Payment gateway integration
- Payment processing:
  - Receive payment
  - Allocate to invoices
  - Generate receipts
  - Payment reconciliation
- Patient deposits:
  - Accept deposits
  - Track deposit balance
  - Apply to final bill
  - Refund excess
- Accounts receivable:
  - Track patient balances
  - Payment reminders
  - Collections management
- Financial reports:
  - Revenue reports
  - Aging reports
  - Payment reports

**Acceptance Criteria:**
- Process payments accurately
- Generate receipts
- Track patient deposits
- Manage accounts receivable
- Reconcile payments

---

### 5.10 Integration Module

#### 5.10.1 BPJS Kesehatan
**VClaim API:**
- Patient eligibility checking
- SEP creation, update, deletion
- Referral (rujukan) information
- Diagnosis/procedure lookup
- Facility and provider lookup
- Claim status monitoring
- Summary of bill (SRB)

**Antrean (Queue) API:**
- Online booking integration
- Queue management
- Queue status updates
- Queue list publication

**Aplicare API:**
- Bed availability reporting
- Real-time bed updates
- Room class information

**PCare API (Puskesmas):**
- Patient registration
- Visit documentation
- Medication administration
- Group activities

**iCare / SATUSEHAT Integration:**
- FHIR resource submission
- Patient data synchronization
- Encounter data
- Diagnosis data

**Acceptance Criteria:**
- All BPJS APIs functional
- Handle API failures gracefully
- Retry failed requests
- Log all API calls
- Monitor API performance

#### 5.10.2 SATUSEHAT FHIR R4
**FHIR Resources:**
- **Patient:** Demographic data synchronization
- **Encounter:** Visit documentation (outpatient, inpatient, emergency)
- **Condition:** Diagnoses (ICD-10 codes)
- **Observation:** Lab results (with LOINC codes), vital signs
- **ServiceRequest:** Lab and radiology orders
- **MedicationRequest:** Prescriptions
- **MedicationAdministration:** Medication given
- **DiagnosticReport:** Lab and radiology reports
- **Immunization:** Vaccination records
- **Organization:** Facility data
- **Practitioner:** Healthcare provider data

**Integration Levels:**
- Level 1 (Terdaftar): Organization registration
- Level 2 (Terintegrasi): Core data submission (Patient, Encounter, Condition)
- Level 3 (Terkoneksi): Full integration with all resources

**Acceptance Criteria:**
- OAuth 2.0 authentication working
- Submit required FHIR resources
- Auto-sync patient data
- Sync encounters within 24 hours
- Handle SATUSEHAT API errors

#### 5.10.3 PCare (Puskesmas)
**PCare Integration:**
- Patient registration
- Visit documentation (kunjungan)
- Medication administration
- Group activities (kegiatan kelompok)
- Laboratory tests (limited)
- Referrals (rujukan)

**Acceptance Criteria:**
- Register patients in PCare
- Document visits
- Record medications given
- Submit group activities
- Create referrals

---

## 6. Non-Functional Requirements

### 6.1 Performance

#### 6.1.1 Response Times
| Operation | Target | Maximum |
|-----------|--------|----------|
| Page load | <2s | <3s |
| API request | <200ms | <500ms |
| Database query | <100ms | <300ms |
| Patient search | <1s | <2s |
| BPJS API call | <5s | <10s |
| Report generation | <10s | <30s |
| Large data export | <30s | <60s |

#### 6.1.2 Concurrent Users
| Deployment Size | Concurrent Users | Simultaneous Requests |
|-----------------|------------------|----------------------|
| Small (Puskesmas) | 10-20 | 50-100 |
| Medium (RS Type C) | 50-100 | 250-500 |
| Large (RS Type A) | 200-500 | 1,000-2,000 |

#### 6.1.3 Data Volume Handling
| Data Type | Volume | Retention |
|-----------|--------|-----------|
| Patients | 100,000+ | 25 years |
| Encounters | 1M+ | 25 years (inpatient), 10 years (outpatient) |
| Medical records | 10M+ documents | Per regulatory requirements |
| Lab results | 5M+ | 10 years |
| Images (PACS) | 10TB+ | 25 years (CT/MRI), 10 years (X-ray) |

**Performance Strategies:**
- Database indexing on all foreign keys
- Query optimization and EXPLAIN analysis
- Caching frequently accessed data (Redis)
- Database partitioning for large tables
- Archive old data to separate storage
- CDN for static assets
- Load balancing for high-traffic deployments

---

### 6.2 Security & Compliance

#### 6.2.1 Data Encryption
**Encryption in Transit:**
- TLS 1.3 for all external communications
- HTTPS for all web traffic
- Secure API communications

**Encryption at Rest:**
- Database encryption (PostgreSQL pgcrypto or Transparent Data Encryption)
- File system encryption (LUKS on Linux)
- Backup encryption (AES-256)
- Password hashing (bcrypt with salt)

**Key Management:**
- Secure key storage (HashiCorp Vault or equivalent)
- Key rotation policies
- Separate keys for different data types
- Hardware security modules (HSM) for large deployments

#### 6.2.2 Access Control (RBAC)
**Role-Based Access Control:**
- Hierarchical roles (Superadmin > Admin > User)
- Department-based access (doctors see their department's patients)
- Least privilege principle
- Context-aware access (emergency override)

**Permission Model:**
- Resource-based permissions (patient:read, patient:write)
- Action-based permissions (create, read, update, delete, export)
- Data-level permissions (only own department)
- Special access categories (VIP patients, psychiatric records)

**Authentication:**
- Multi-factor authentication for:
  - Remote access
  - Administrative accounts
  - Financial transactions
  - Sensitive data access
- Session timeout (30 minutes inactivity)
- Password policies:
  - Minimum 12 characters
  - Complexity requirements
  - Expiration (90 days)
  - History (no reuse of last 10)

#### 6.2.3 Audit Logging
**Mandatory Audit Events:**
- User authentication (success/failure)
- Patient record access (who accessed what and when)
- Data modifications (create, update, delete)
- Data export (PDF, Excel, API)
- Administrative actions (user management, config changes)
- Failed operations (unauthorized access attempts)

**Audit Log Format:**
- Timestamp
- User ID and username
- Action (CREATE, READ, UPDATE, DELETE)
- Resource type (Patient, Diagnosis, Prescription, etc.)
- Resource ID
- IP address
- User agent
- Success/failure
- Failure reason (if applicable)
- Additional data (JSONB)

**Audit Log Retention:**
- Active database: 6 months
- Archive database: 6 years
- Backup: Permanent (offsite, encrypted)

#### 6.2.4 BPJS Data Handling Requirements
**Data Classification:**
- BPJS patient data: Sensitive personal data
- SEP information: Confidential
- Claim data: Financial records

**Handling Requirements:**
- Encrypt all BPJS data
- Secure BPJS credentials (Cons-ID, Secret Key)
- Log all BPJS API calls
- Validate BPJS data before submission
- Handle BPJS API errors gracefully
- Retry failed BPJS requests
- Monitor BPJS API rate limits

#### 6.2.5 UU 27/2022 PDP Law Compliance
**Personal Data Protection:**
- **Data Collection:** Collect only necessary data
- **Data Purpose:** Specify purpose at collection
- **Data Consent:** Obtain explicit consent
- **Data Access:** Allow patients to access their data
- **Data Correction:** Allow patients to correct errors
- **Data Deletion:** Allow data deletion (with exceptions)
- **Data Portability:** Provide data in portable format
- **Data Breach:** Notify within 3×24 hours

**Data Controller Responsibilities:**
- Register data processing activities
- Implement privacy by design
- Conduct data protection impact assessments
- Appoint Data Protection Officer (if required)
- Ensure data processor compliance
- Document data processing

---

### 6.3 Availability

#### 6.3.1 Uptime Requirements
| System Class | Uptime Target | Downtime Allowed/Year |
|--------------|---------------|----------------------|
| Critical | 99.9% | 8.76 hours |
| High | 99.5% | 43.8 hours |
| Standard | 99.0% | 87.6 hours |

**High Availability Features:**
- Database replication (master-slave)
- Auto-failover on failure
- Load balancing
- Redundant servers
- Health monitoring and alerts
- Graceful degradation

#### 6.3.2 Offline-First Capability
**Offline Functionality Levels:**

**Level 1 (No Internet):**
- View patient records
- Create new encounters
- Write prescriptions
- Order lab/radiology
- Queue transactions for sync

**Level 2 (Limited Internet):**
- All Level 1 features
- Sync queued records
- Fetch latest patient data
- Reference data updates

**Level 3 (Good Internet):**
- All features
- Real-time updates
- Live dashboards
- Medical imaging
- Telemedicine

**Offline Technical Implementation:**
- Service Workers for caching
- IndexedDB for local storage
- Background sync for queued operations
- Conflict resolution for concurrent edits
- Progressive enhancement strategy

#### 6.3.3 Disaster Recovery
**Recovery Time Objectives (RTO):**
| System | RTO | RPO |
|--------|-----|-----|
| Critical (patient care) | <4 hours | <15 min |
| Important (billing, claims) | <24 hours | <1 hour |
| Non-critical (analytics) | <72 hours | <24 hours |

**Disaster Recovery Strategy:**
- Daily automated backups
- Weekly off-site backup
- Backup to cloud storage (Indonesia region)
- Documented disaster recovery procedures
- Quarterly disaster recovery testing
- Backup restoration verification

---

### 6.4 Usability

#### 6.4.1 WCAG 2.1 AA Compliance
**Accessibility Features:**
- Screen reader compatibility
- Keyboard navigation for all features
- Color contrast ratios (4.5:1 for text)
- Text resizing (up to 200%)
- Focus indicators
- Alternative text for images
- Captioning for video content
- Forms accessibility (labels, error messages)

#### 6.4.2 Keyboard Shortcuts for Clinicians
**Global Shortcuts:**
- `Ctrl/Cmd + K`: Quick search (patient, test, drug)
- `Ctrl/Cmd + N`: New record
- `Ctrl/Cmd + S`: Save
- `Ctrl/Cmd + P`: Print
- `Ctrl/Cmd + F`: Find within page
- `Escape`: Close modal/dialog

**Clinical Shortcuts:**
- `Ctrl/Cmd + D`: Diagnose (ICD-10 lookup)
- `Ctrl/Cmd + R`: Prescription writing
- `Ctrl/Cmd + L`: Lab order
- `Ctrl/Cmd + X`: Radiology order
- `Ctrl/Cmd + T`: Task list
- `Ctrl/Cmd + H`: Patient history

#### 6.4.3 Indonesian Language Localization
**Language Support:**
- Primary language: Indonesian (Bahasa Indonesia)
- All UI text in Indonesian
- Medical terminology in Indonesian
- Currency: IDR (Rupiah)
- Date format: DD-MM-YYYY
- Number format: 1.000.000,00 (dots for thousands)

**Regional Support:**
- Timezone: WIB, WITA, WIT
- Indonesian address structure (provinces, regencies, districts, villages)
- Indonesian demographic data (ethnic groups, languages, religions)

#### 6.4.4 Mobile-Responsive Design
**Responsive Breakpoints:**
- Desktop: >1024px
- Tablet: 768px - 1024px
- Mobile: <768px

**Mobile Optimization:**
- Touch-friendly interface (minimum 44×44px touch targets)
- Swipe gestures (left/right navigation)
- Bottom navigation for thumb-friendly access
- Simplified forms (reduce typing)
- Camera integration (scan barcodes, capture documents)
- Offline data caching
- Push notifications (alerts, reminders)

---

## 7. Technical Requirements

### 7.1 Tech Stack (From Research Evaluation)

#### 7.1.1 Backend
**Primary Choice: FastAPI (Python)**
- **Reasons:**
  - Modern async performance for concurrent operations
  - Type safety with Pydantic (critical for medical data)
  - Automatic OpenAPI documentation
  - Strong Indonesian talent pool
  - Excellent healthcare ecosystem

**Alternative: Django (Python)**
- For teams preferring batteries-included approach
- Built-in admin interface
- Strong security track record

#### 7.1.2 Database
**Primary Choice: PostgreSQL 15+**
- **Reasons:**
  - Superior JSONB for flexible medical records
  - Advanced indexing for complex queries
  - Strong encryption features
  - Proven in healthcare systems
  - Better performance than MySQL

**Backup Strategy:**
- Daily full backups (pg_dump)
- Continuous WAL archiving
- Weekly off-site backup
- Monthly disaster recovery test

#### 7.1.3 Frontend
**Primary Choice: Next.js 15 (React)**
- **Reasons:**
  - Server-side rendering for slow hospital networks
  - PWA capabilities for offline functionality
  - Massive ecosystem for medical visualizations
  - Strong TypeScript support
  - Excellent performance

**Alternative: Nuxt (Vue)**
- For teams preferring simpler APIs
- Gentler learning curve
- Smaller bundle sizes

#### 7.1.4 Deployment
**Primary Choice: Docker Compose**
- **Reasons:**
  - One-command installation
  - Version-controlled infrastructure
  - Easy rollback and updates
  - Resource isolation
  - On-premises friendly

**Services:**
- Backend (FastAPI)
- Frontend (Next.js)
- Database (PostgreSQL)
- Cache (Redis)
- Object Storage (MinIO for images/documents)

#### 7.1.5 Additional Components
- **Caching:** Redis (sessions, cache, message queue)
- **Storage:** MinIO (S3-compatible for medical images/documents)
- **API Gateway:** NGINX (reverse proxy, SSL termination)
- **Monitoring:** Prometheus + Grafana (metrics, dashboards)

---

### 7.2 Browser Support
**Supported Browsers (Latest 2 Versions):**
- Google Chrome (recommended)
- Microsoft Edge
- Mozilla Firefox
- Safari (macOS and iOS)

**Minimum Browser Versions:**
- Chrome 90+
- Edge 90+
- Firefox 88+
- Safari 14+

**Mobile Browsers:**
- Chrome Mobile (Android 10+)
- Safari Mobile (iOS 14+)

---

### 7.3 On-Prem Deployment (Docker Compose)

#### 7.3.1 Minimum Server Requirements
**Small Facility (Puskesmas, < 50 concurrent users):**
- CPU: 4 cores (Intel i5 or AMD Ryzen 5)
- RAM: 8GB (16GB recommended)
- Storage: 1TB SSD (2TB recommended)
- Network: Gigabit Ethernet
- Power: UPS (uninterruptible power supply)

**Medium Facility (RS Type C, 50-100 concurrent users):**
- CPU: 8 cores
- RAM: 16GB
- Storage: 2TB SSD
- Network: Gigabit Ethernet
- Power: UPS + Generator backup

**Large Facility (RS Type A/B, 200+ concurrent users):**
- CPU: 16+ cores
- RAM: 32GB+
- Storage: 4TB+ SSD
- Network: 10Gb Ethernet
- Power: UPS + Generator + Redundant power
- High availability setup (load balancing, replication)

#### 7.3.2 Installation Process
```bash
# 1. Download SIMRS package
wget https://releases.simrs.id/simrs-latest.tar.gz
tar -xzf simrs-latest.tar.gz
cd simrs

# 2. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 3. Start services
docker-compose up -d

# 4. Run database migrations
docker-compose exec backend alembic upgrade head

# 5. Create admin user
docker-compose exec backend python create_admin.py

# 6. Access application
open http://localhost
```

#### 7.3.3 Update Process
```bash
# 1. Backup database
docker-compose exec db pg_dump -U simrs simrs > backups/pre-update-$(date +%Y%m%d).sql

# 2. Pull latest images
docker-compose pull

# 3. Run migrations
docker-compose exec backend alembic upgrade head

# 4. Restart services
docker-compose up -d

# 5. Verify health
docker-compose ps
```

---

### 7.4 Database Requirements

#### 7.4.1 Schema Design Principles
- **Normalized Schema:** Reduce redundancy (aim for 3NF)
- **Consistent Naming:** Use clear, consistent column names
- **Appropriate Data Types:** Use correct types for efficiency
- **Indexing Strategy:** Index foreign keys and frequently queried columns
- **Partitioning:** Partition large tables by date
- **Soft Deletes:** Use deleted_at instead of DELETE for audit trail

#### 7.4.2 Database Size Estimates
| Facility | Annual Patients | Database Growth | 5-Year Size |
|----------|----------------|-----------------|-------------|
| Puskesmas | 10,000 | 10 GB/year | 50 GB |
| RS Type C | 50,000 | 50 GB/year | 250 GB |
| RS Type B | 100,000 | 100 GB/year | 500 GB |
| RS Type A | 200,000 | 200 GB/year | 1 TB |

**Note:** Excludes medical images (PACS), which require separate storage (10TB+ for large hospitals)

#### 7.4.3 Backup Strategy
- **Incremental Backups:** Every 6 hours
- **Full Backups:** Daily at 2 AM (low traffic)
- **WAL Archiving:** Continuous
- **Off-site Backup:** Weekly to encrypted external drive
- **Retention:**
  - Daily backups: 30 days
  - Weekly backups: 12 months
  - Monthly backups: 7 years

---

## 8. Regulatory & Compliance

### 8.1 Permenkes 82 Tahun 2013 (SIMRS Mandate)

#### Key Provisions (Pasal 3-8)
**Pasal 3: Mandatory Implementation**
- Every hospital MUST implement SIMRS
- Open source solutions are preferred
- Must integrate with government programs

**Pasal 4: System Components**
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

**Pasal 5: Integration Requirements**
- Must integrate with Ministry of Health systems
- Must support data exchange standards
- Must ensure data security and privacy
- Must provide interoperability

**Pasal 6: Data Standards**
- Use standardized medical codes (ICD-10, etc.)
- Follow national data standards
- Maintain data integrity and accuracy

**Pasal 7: Technical Requirements**
- System availability and reliability
- Data backup and recovery
- User access controls
- Audit trail capabilities

**Compliance Strategy:**
- Implement all required modules
- Integrate with SATUSEHAT platform
- Follow FHIR R4 standards
- Implement comprehensive audit logging
- Regular security assessments

---

### 8.2 Permenkes 24 Tahun 2022 (Medical Records)

#### Key Provisions

**Electronic Medical Records Mandatory:**
- All healthcare facilities MUST use electronic medical records
- Effective date: August 31, 2022

**Data Retention (Pasal 34):**
- Inpatient records: Minimum 25 years
- Outpatient records: Minimum 10 years
- Medical imaging: 10-25 years depending on type
- Death records: Permanent retention

**Privacy & Security (Pasal 35-37):**
- Patient consent required for data access
- Role-based access control mandatory
- Audit trails for all access
- Data encryption in transit and at rest
- Breach notification requirements

**Authentication (Pasal 38):**
- User authentication required
- Two-factor authentication for sensitive data
- Session management
- Password policies

**Data Integration (Pasal 39-40):**
- Must integrate with SATUSEHAT platform
- Must support FHIR standards
- Must submit required data elements
- Interoperability requirements

**Digital Signature (Pasal 41):**
- Medical records must be digitally signed
- Practitioner authentication
- Non-repudiation of authorship

**Backup & Recovery (Pasal 42-43):**
- Regular backup required (minimum daily)
- Off-site backup storage
- Regular recovery testing
- Disaster recovery planning

**Access Control (Pasal 44-45):**
- Minimum privilege principle
- Role-based access
- Emergency access procedures
- Access logging and monitoring

**Data Quality (Pasal 46-47):**
- Data validation required
- Regular data quality audits
- Correction mechanisms
- Version control

**Compliance Strategy:**
- Implement full EMR with digital signatures
- Implement data retention policies
- Encrypt all data (transit and at rest)
- Implement RBAC with emergency access
- Daily automated backups
- Regular data quality audits

---

### 8.3 BPJS Kesehatan Requirements

#### Integration Requirements
**Mandatory Integrations:**
1. **VClaim API:** Patient eligibility, SEP creation, claims
2. **Aplicare API:** Real-time bed availability reporting
3. **Antrean API:** Online appointment queue management
4. **e-Claim:** Electronic claim submission

#### SEP (Surat Eligibilitas Peserta) Requirements
**Creation Rules:**
- Must create SEP before or at admission
- Valid for 90 days (can be extended)
- Must update SEP for significant changes (room, diagnosis)
- Must close SEP on discharge

**Data Requirements:**
- Patient information (name, BPJS number, NIK)
- Diagnosis (ICD-10 code)
- Facility information (PPK)
- Service type (inpatient/outpatient)
- Room class
- Referral information (if applicable)

#### e-Claim Submission
**Submission Timeline:**
- Submit within 21 days after discharge
- Submit through BPJS gateway
- Attach all required documents
- Respond to verification queries

**Claim Requirements:**
- Complete medical record documentation
- ICD-10 coding for all diagnoses
- Procedure codes for all procedures
- Itemized billing
- Medical justification for services

---

### 8.4 Medical Coding Standards

#### ICD-10-CM Indonesia
**Usage:**
- Diagnosis coding for:
  - BPJS claims
  - Medical records
  - SATUSEHAT integration
  - Epidemiological reporting

**Version:**
- ICD-10 2016 version (Indonesian adaptation)
- Regular updates from Ministry of Health

**Implementation:**
- Primary diagnosis: Mandatory for all encounters
- Secondary diagnoses: Required for comorbidities
- Admission diagnosis: Required for inpatient admissions
- Discharge diagnosis: Required for inpatient discharges

#### LOINC for Lab Results
**Usage:**
- Required for SATUSEHAT Observation resources
- Laboratory test identification
- Standardized test coding

**Implementation:**
- All lab tests must have LOINC codes
- Use SATUSEHAT terminology service
- Map local test codes to LOINC

#### SNOMED CT
**Status:**
- Indonesia became SNOMED International member in 2023
- Growing adoption for clinical terminology
- Used alongside ICD-10 and LOINC

**Usage:**
- Detailed clinical findings
- Problem list entries
- Clinical terminology standardization
- Mapping to ICD-10 for billing

---

## 9. Out of Scope

### Features for Future Releases

#### Phase 2 Features (6-12 months after MVP)
- Telemedicine platform (video consultations)
- Advanced analytics and business intelligence
- AI clinical decision support
- Patient portal (mobile app)
- Staff mobile app
- Integration with additional insurance providers
- Supply chain management
- Asset management
- Facilities management

#### Phase 3 Features (12-24 months after MVP)
- Machine learning for diagnosis prediction
- Integration with wearable devices
- Genomic medicine support
- Population health management
- Remote patient monitoring
- Advanced imaging AI (radiology decision support)
- Blockchain for medical records (optional)
- Voice recognition for clinical documentation
- Natural language processing for clinical notes

### Explicitly Excluded Functionality

#### Not in Scope for Initial Release
- **PACS (Picture Archiving and Communication System):** Use existing PACS, integrate via DICOM
- **LIS (Laboratory Information System):** Use existing LIS, integrate via HL7/ASTM
- **RIS (Radiology Information System):** Use existing RIS, integrate via HL7
- **EMR (Electronic Medical Records) migration:** Historical data migration will be separate project
- **Accounting system:** Basic financials only, full accounting in future
- **Payroll system:** HR master data only, full payroll in future
- **ERP integration:** Inventory and procurement only, full ERP in future
- **Hospital information systems other than core modules:** Specialized systems (e.g., dialysis) in future

#### Will Not Support
- **Paper-based workflows:** All workflows must be digital
- **Offline-only mode:** Offline-first with sync when online
- **Multi-tenant SaaS:** Single-hospital deployment only (multi-tenant in future)
- **International deployments:** Indonesia-specific only
- **Non-Indonesian languages:** Indonesian only, English for technical terms

---

## 10. Dependencies & Risks

### 10.1 External API Dependencies

#### BPJS Kesehatan APIs
**Dependencies:**
- VClaim API (https://apijkn.bpjs-kesehatan.go.id/vclaim-rest)
- Aplicare API (https://new-api.bpjs-kesehatan.go.id/aplicaresws)
- Antrean API (https://apijkn.bpjs-kesehatan.go.id/antreanrs)
- PCare API (https://apijkn.bpjs-kesehatan.go.id/pcare-rest)

**Risks:**
- API downtime or degradation
- API changes without notice
- Rate limiting
- Authentication failures
- Data quality issues

**Mitigation Strategies:**
- Implement retry logic with exponential backoff
- Cache reference data (diagnoses, polis, facilities)
- Queue failed requests for retry
- Monitor API performance and availability
- Comprehensive error handling and logging
- Maintain API version compatibility
- Regular testing with BPJS sandbox environment

#### SATUSEHAT Platform
**Dependencies:**
- FHIR R4 API (https://api-satusehat.kemkes.go.id/fhir-r4/v1)
- OAuth 2.0 authentication (https://api-satusehat.kemkes.go.id/oauth2/v1)
- Terminology services (ICD-10, LOINC, SNOMED CT)

**Risks:**
- Platform downtime or degradation
- API changes
- Authentication token expiration
- Resource validation errors
- Data submission failures

**Mitigation Strategies:**
- Auto-refresh OAuth tokens
- Queue failed submissions
- Implement comprehensive FHIR validation
- Monitor submission status
- Test in SATUSEHAT staging environment
- Maintain FHIR resource versioning

#### Ministry of Health APIs
**Dependencies:**
- SIRS (Sistem Informasi Rumah Sakit Terpadu)
- SISRUTE (Sistem Rujukan Terintegrasi)
- Other Kemenkes reporting systems

**Risks:**
- API availability
- Changing reporting requirements
- Data format changes
- Authentication issues

**Mitigation Strategies:**
- Flexible reporting module
- Parameterized report templates
- Automated report submission
- Monitoring and alerting
- Regular compliance reviews

---

### 10.2 Implementation Risks

#### Technical Risks

**Risk 1: Database Performance Degradation**
- **Impact:** High - System becomes unusable
- **Probability:** Medium
- **Mitigation:**
  - Proper indexing strategy
  - Query optimization
  - Database partitioning for large tables
  - Regular performance monitoring
  - Load testing before deployment

**Risk 2: Security Breach**
- **Impact:** Critical - Patient data compromised, legal penalties
- **Probability:** Low (with proper security)
- **Mitigation:**
  - Defense-in-depth security strategy
  - Regular security assessments
  - Penetration testing
  - Comprehensive audit logging
  - Encryption at multiple layers
  - Security training for staff

**Risk 3: Integration Failures**
- **Impact:** High - Cannot process BPJS claims, regulatory non-compliance
- **Probability:** Medium
- **Mitigation:**
  - Thorough testing with sandbox environments
  - Comprehensive error handling
  - Fallback procedures
  - Queue-based architecture for retries
  - Monitoring and alerting

**Risk 4: Poor Performance on Slow Networks**
- **Impact:** High - System unusable in remote areas
- **Probability:** Medium
- **Mitigation:**
  - Offline-first PWA architecture
  - Aggressive caching
  - Optimized bundle sizes
  - Progressive enhancement
  - Bandwidth optimization

**Risk 5: Data Loss**
- **Impact:** Critical - Loss of patient records, legal penalties
- **Probability:** Low (with proper backup)
- **Mitigation:**
  - Automated daily backups
  - Continuous WAL archiving
  - Off-site backup storage
  - Regular disaster recovery testing
  - Database replication

#### Operational Risks

**Risk 6: Low User Adoption**
- **Impact:** High - Project fails to deliver value
- **Probability:** Medium
- **Mitigation:**
  - Comprehensive user training
  - Intuitive user interface
  - Phased rollout
  - User feedback incorporation
  - Change management program
  - Support and superuser training

**Risk 7: Inadequate IT Infrastructure at Hospitals**
- **Impact:** High - System cannot run properly
- **Probability:** Medium
- **Mitigation:**
  - Clearly specify minimum requirements
  - Provide infrastructure assessment
  - Offer hardware procurement assistance
  - Optimize for limited resources
  - Cloud-hosted option for small facilities

**Risk 8: Staff Resistance**
- **Impact:** Medium - Slower adoption, decreased productivity
- **Probability:** High
- **Mitigation:**
  - Involve staff in design and testing
  - Comprehensive training program
  - Highlight benefits and time savings
  - Address concerns proactively
  - Provide excellent support during transition
  - Identify and empower champions

**Risk 9: Regulatory Changes**
- **Impact:** Medium - System becomes non-compliant
- **Probability:** Medium
- **Mitigation:**
  - Modular architecture for easy updates
  - Regulatory monitoring and alerting
  - Flexible data model
  - Strong relationship with regulators
  - Participation in regulatory working groups

**Risk 10: Budget Overruns**
- **Impact:** Medium - Project may not be completed
- **Probability:** Medium
- **Mitigation:**
  - Phased implementation (MVP first)
  - Prioritize critical features
  - Regular budget reviews
  - Scope management
  - Open-source components to reduce costs

---

### 10.3 Mitigation Strategies Summary

**Technical Mitigation:**
- Robust error handling and retry logic
- Comprehensive monitoring and alerting
- Offline-first architecture
- Security by design
- Performance optimization
- Regular testing and QA

**Operational Mitigation:**
- Phased rollout (pilot → expand)
- Comprehensive training program
- Strong change management
- Excellent user support
- Regular feedback collection
- Continuous improvement

**Financial Mitigation:**
- Phased implementation (manage cash flow)
- Open-source stack (reduce licensing costs)
- Cloud options (reduce capital expenditure)
- Pricing flexibility (tiered pricing)
- Government grants and funding

**Regulatory Mitigation:**
- Early engagement with regulators
- Participation in working groups
- Regular compliance reviews
- Flexible architecture for updates
- Comprehensive documentation

---

## 11. Roadmap

### 11.1 MVP Feature Set (Months 1-6)

#### Core Modules
1. **Patient Registration**
   - New patient registration
   - Returning patient registration
   - BPJS eligibility check
   - Queue management

2. **Medical Records**
   - Patient history
   - Problem list (ICD-10)
   - Allergy tracking
   - Clinical notes (SOAP)
   - Basic prescriptions

3. **Outpatient Management**
   - Doctor consultation
   - Prescription writing
   - Lab/radiology ordering
   - Basic reporting

4. **Inpatient Management**
   - Bed management
   - Admission/discharge/transfer
   - Basic nursing notes
   - Discharge planning

5. **Pharmacy**
   - Prescription processing
   - Basic inventory management
   - Drug dispensing
   - Drug interaction checking

6. **Billing**
   - Invoice generation
   - BPJS claim preparation
   - Payment processing
   - Basic financial reports

7. **Integration**
   - BPJS VClaim API
   - BPJS Antrean API
   - Basic SATUSEHAT integration (Patient, Encounter, Condition)

#### Non-Functional Requirements
- System uptime > 99%
- Response time < 500ms (p95)
- Offline support for core features
- Security (encryption, RBAC, audit logging)
- Docker Compose deployment

#### Deliverables
- Working MVP deployed to 3-5 pilot hospitals
- BPJS integration certified
- SATUSEHAT Level 1 certification
- User documentation
- Technical documentation

---

### 11.2 Phase 2 (Months 7-12)

#### Advanced Features
1. **Advanced Medical Records**
   - Structured templates
   - Clinical decision support
   - Digital signatures
   - Document management

2. **Advanced Inpatient**
   - Care plans
   - Medication administration (MAR)
   - Flow sheets
   - Interdisciplinary notes

3. **Laboratory**
   - Test ordering
   - Result entry
   - Quality control
   - Basic LIS integration

4. **Radiology**
   - Exam ordering
   - Result reporting
   - Basic PACS integration
   - Report templates

5. **Emergency Department**
   - Triage system
   - Emergency protocols
   - Rapid registration
   - Critical care documentation

6. **Advanced Integrations**
   - SATUSEHAT Level 2 certification
   - BPJS Aplicare integration
   - BPJS e-Claim
   - Kemenkes reporting (SIRS)

7. **Mobile Apps**
   - Patient app (appointments, results)
   - Doctor app (rounds, notifications)
   - Nurse app (bedside charting)

#### Deliverables
- Full hospital deployment (all core modules)
- SATUSEHAT Level 2 certification
- Mobile apps (iOS and Android)
- Advanced reporting and analytics
- Expanded to 20-30 hospitals

---

### 11.3 Phase 3 (Months 13-24)

#### Strategic Features
1. **Telemedicine**
   - Video consultations
   - Remote monitoring
   - Patient portal
   - Online prescriptions

2. **Advanced Analytics**
   - Business intelligence dashboards
   - Population health
   - Predictive analytics
   - Performance metrics

3. **AI Clinical Decision Support**
   - Diagnosis prediction
   - Drug interaction checking
   - Treatment recommendations
   - Alert fatigue reduction

4. **Advanced Integrations**
   - SATUSEHAT Level 3 certification
   - Additional insurance providers
   - Third-party systems (PACS, LIS)
   - Health information exchange

5. **Enterprise Features**
   - Multi-hospital deployments
   - Hospital networks
   - Centralized reporting
   - Shared services

6. **Advanced Automation**
   - Robotic process automation
   - Workflow automation
   - Intelligent scheduling
   - Resource optimization

#### Deliverables
- SATUSEHAT Level 3 certification
- Telemedicine platform
- Advanced analytics platform
- AI clinical decision support
- Multi-hospital deployments
- 50-100 hospitals deployed

---

### 11.4 Timeline Considerations

#### Critical Path
1. **Month 1-2:** Architecture and design
2. **Month 3-4:** Core modules development
3. **Month 5:** BPJS and SATUSEHAT integration
4. **Month 6:** Testing and certification
5. **Month 7:** Pilot deployments (3-5 hospitals)
6. **Month 8-9:** Feedback and iteration
7. **Month 10-12:** Expansion (20-30 hospitals)
8. **Month 13-24:** Advanced features and scale

#### Dependencies
- BPJS certification (must be obtained before go-live)
- SATUSEHAT certification (must be obtained before data submission)
- Hospital IT readiness (assessment before deployment)
- Staff training (must be completed before go-live)
- Hardware procurement (lead time 2-3 months)

#### Risk Mitigation in Timeline
- Buffer time for certification delays
- Parallel development tracks
- Early engagement with regulators
- Pilot with smaller hospitals first
- Phased rollout to manage risk

---

## 12. Success Criteria

### MVP Success Criteria (6 Months)
- [ ] 3-5 pilot hospitals live on system
- [ ] BPJS VClaim integration certified
- [ ] SATUSEHAT Level 1 certified
- [ ] >80% user adoption
- [ ] >99% uptime
- [ ] <500ms response time (p95)
- [ ] Offline capabilities functional
- [ ] Zero critical security breaches
- [ ] Positive user feedback (>4/5 satisfaction)

### Phase 2 Success Criteria (12 Months)
- [ ] 20-30 hospitals deployed
- [ ] All core modules functional
- [ ] SATUSEHAT Level 2 certified
- [ ] Mobile apps launched
- [ ] BPJS claim approval rate >95%
- [ ] Patient wait time reduced 30%
- [ ] Documentation complete

### Phase 3 Success Criteria (24 Months)
- [ ] 50-100 hospitals deployed
- [ ] SATUSEHAT Level 3 certified
- [ ] Telemedicine platform live
- [ ] Advanced analytics operational
- [ ] AI clinical decision support deployed
- [ ] Multi-hospital networks supported
- [ ] Proven clinical outcomes improvement

---

## Appendix A: Glossary

**BPJS:** Badan Penyelenggara Jaminan Sosial (Social Security Administrator)
**BPJS Kesehatan:** National health insurance implementation body
**Dinkes:** Dinas Kesehatan (District Health Office)
**Fasyankes:** Fasilitas Kesehatan (Healthcare Facility)
**FHIR:** Fast Healthcare Interoperability Resources
**ICD-10:** International Classification of Diseases, 10th Revision
**IGD:** Instalasi Gawat Darurat (Emergency Department)
**INA-CBG:** Indonesia Case Base Groups (DRG-like system)
**JKN:** Jaminan Kesehatan Nasional (National Health Insurance)
**Kemenkes:** Kementerian Kesehatan (Ministry of Health)
**LOINC:** Logical Observation Identifiers Names and Codes
**Puskesmas:** Pusat Kesehatan Masyarakat (Community Health Center)
**RM:** Rekam Medis (Medical Record)
**RS:** Rumah Sakit (Hospital)
**RSIA:** Rumah Sakit Bersalin (Maternity Hospital)
**RSJ:** Rumah Sakit Jiwa (Psychiatric Hospital)
**SEP:** Surat Eligibilitas Peserta (Participant Eligibility Letter)
**SIMRS:** Sistem Informasi Manajemen Rumah Sakit (Hospital Management Information System)
**SATUSEHAT:** Indonesia's national health data exchange platform

---

## Appendix B: References

### Regulatory Documents
1. Permenkes No. 82 Tahun 2013 - Sistem Informasi Manajemen Rumah Sakit
2. Permenkes No. 24 Tahun 2022 - Rekam Medis
3. UU No. 27 Tahun 2022 - Perlindungan Data Pribadi
4. UU No. 29 Tahun 2004 - Praktik Kedokteran
5. UU No. 11 Tahun 2008 - Informasi dan Transaksi Elektronik

### Integration Documentation
1. BPJS VClaim API Documentation
2. BPJS Antrean API Documentation
3. BPJS Aplicare API Documentation
4. SATUSEHAT FHIR R4 Implementation Guide
5. SATUSEHAT Integration Guides

### Technical References
1. PostgreSQL Documentation (https://www.postgresql.org/docs/)
2. FastAPI Documentation (https://fastapi.tiangolo.com/)
3. Next.js Documentation (https://nextjs.org/docs)
4. FHIR R4 Specification (https://hl7.org/fhir/)
5. Docker Documentation (https://docs.docker.com/)

### Medical Coding Standards
1. ICD-10-CM Indonesia (World Health Organization)
2. LOINC International (https://loinc.org/)
3. SNOMED CT (https://confluence.ihtsdotools.org/)
4. INA-CBG (Indonesia Case Base Groups)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-13
**Next Review:** 2026-02-13 (monthly during development phase)
**Status:** Draft - Pending Review and Approval
