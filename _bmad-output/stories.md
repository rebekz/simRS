# SIMRS - User Stories Document

**Version:** 1.0
**Date:** 2026-01-13
**Status:** Draft
**Based on:** Epics v1.0, PRD v1.0

---

## Table of Contents
1. [Stories by Epic](#stories-by-epic)
2. [MVP Stories (Phase 1)](#mvp-stories-phase-1)
3. [Story Template](#story-template)
4. [Definition of Done](#definition-of-done)
5. [Story Dependencies](#story-dependencies)
6. [Priority Matrix](#priority-matrix)

---

## Story Template

Each user story in this document follows this structure:

- **Story ID**: Unique identifier (e.g., STORY-001)
- **Title**: Brief descriptive title
- **Epic**: Parent epic ID and name
- **User Role**: Primary user persona
- **Action**: What the user wants to do
- **Benefit**: Value received
- **Acceptance Criteria**: AC-001, AC-002, etc.
- **Tasks/Subtasks**: Implementation breakdown
- **Dependencies**: Other stories or epics
- **Priority**: Must Have / Should Have / Could Have
- **Story Points**: Effort estimate (Fibonacci scale: 1, 2, 3, 5, 8, 13, 21)
- **Definition of Done Checklist**: Verification items

---

## Definition of Done

All stories must meet these criteria before being marked complete:

### Code Quality
- [ ] Code follows project coding standards
- [ ] Code reviewed and approved by at least one peer
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests written and passing
- [ ] No critical or high-severity security vulnerabilities
- [ ] Performance benchmarks met (response time <500ms)

### Functionality
- [ ] All acceptance criteria met
- [ ] Feature works in offline mode (if applicable)
- [ ] Feature works in online mode
- [ ] Error handling implemented and tested
- [ ] Edge cases covered

### Documentation
- [ ] API documentation updated (if applicable)
- [ ] User documentation updated
- [ ] Database migrations documented
- [ ] Technical documentation updated
- [ ] Changelog updated

### Testing
- [ ] QA testing completed
- [ ] User acceptance testing (UAT) passed
- [ ] BPJS/SATUSEHAT integration tested (if applicable)
- [ ] Cross-browser testing completed
- [ ] Mobile responsiveness verified

### Deployment
- [ ] Deployed to staging environment
- [ ] Smoke tests passed on staging
- [ ] Deployment runbook created
- [ ] Rollback plan documented
- [ ] Monitoring and alerting configured

---

## MVP Stories (Phase 1)

### Epic 1: Foundation & Security Infrastructure (EPIC-001)

---

#### STORY-001: System Deployment

**Epic**: EPIC-001 - Foundation & Security Infrastructure

**As a** System Administrator
**I want** to deploy the SIMRS system with a single command
**So that** I can set up the hospital quickly without complex installation procedures

**Acceptance Criteria**:
- AC-001: Docker Compose setup completes successfully with single command `docker-compose up -d`
- AC-002: All required services start correctly (backend, frontend, database, redis, minio)
- AC-003: Database migrations run automatically on startup
- AC-004: Health check endpoints return 200 OK for all services
- AC-005: System is accessible via HTTPS with valid SSL certificate
- AC-006: Default admin user can be created via CLI command
- AC-007: System logs are properly configured and accessible
- AC-008: Environment variables are properly documented in .env.example

**Tasks**:
1. Create Docker Compose configuration with all services
2. Configure health check endpoints for each service
3. Set up automated database migration on startup
4. Create SSL certificate generation/renewal scripts
5. Create CLI script for admin user creation
6. Configure centralized logging (ELK or similar)
7. Create comprehensive .env.example with all configuration options
8. Write deployment documentation
9. Test deployment on fresh server
10. Create rollback procedures

**Dependencies**: None

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Docker Compose deploys all services successfully
- [ ] Automated deployment tested on multiple OS (Ubuntu, CentOS)
- [ ] Deployment documentation complete with screenshots
- [ ] Health checks functional for all services
- [ ] SSL/TLS properly configured
- [ ] Default admin creation tested
- [ ] Deployment time <15 minutes on standard hardware
- [ ] Rollback procedure tested and documented

---

#### STORY-002: User Authentication & Authorization

**Epic**: EPIC-001 - Foundation & Security Infrastructure

**As a** System Administrator
**I want** to manage user authentication and role-based access control
**So that** staff have appropriate access to patient data and system functions

**Acceptance Criteria**:
- AC-001: Users can log in with username and password
- AC-002: Session timeout occurs after 30 minutes of inactivity
- AC-003: Multi-factor authentication (MFA) is enforced for remote access
- AC-004: Password policies enforced (12+ chars, complexity, 90-day expiration)
- AC-005: Role-based access control (RBAC) supports resource and action permissions
- AC-006: JWT tokens with refresh token rotation implemented
- AC-007: Failed login attempts are logged and monitored
- AC-008: Password reset flow works via email/SMS
- AC-009: User can view their own login history
- AC-010: Session management allows users to logout from all devices

**Tasks**:
1. Design user authentication database schema
2. Implement JWT token generation and validation
3. Create refresh token rotation logic
4. Build login/logout API endpoints
5. Implement MFA using TOTP (Time-based One-Time Password)
6. Create password policy validation
7. Build password reset workflow with email/SMS
8. Implement RBAC permission checking middleware
9. Create session management endpoints
10. Build audit logging for authentication events
11. Write unit tests for auth logic
12. Write integration tests for login flows

**Dependencies**: STORY-001 (System Deployment)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] All authentication flows tested and working
- [ ] MFA setup and verification working
- [ ] Password policies enforced
- [ ] JWT tokens properly secured
- [ ] RBAC permissions checked on all protected endpoints
- [ ] Audit logs capture all auth events
- [ ] Security review completed
- [ ] Performance: Login completes in <2 seconds

---

#### STORY-003: Audit Logging System

**Epic**: EPIC-001 - Foundation & Security Infrastructure

**As a** Security Officer
**I want** all patient data access and system changes logged
**So that** we can comply with Indonesian regulations (UU 27/2022) and track data access

**Acceptance Criteria**:
- AC-001: All CRUD operations on patient data are logged
- AC-002: Audit logs include: timestamp, user ID, action, resource ID, IP address, user agent
- AC-003: Audit logs are immutable (cannot be modified or deleted)
- AC-004: Audit logs are retained for 6 years in database
- AC-005: Audit logs can be queried by user, date range, resource type, action
- AC-006: Sensitive operations (data export, bulk delete, permission changes) trigger alerts
- AC-007: Audit log data is encrypted at rest
- AC-008: Admin can export audit logs to CSV/Excel
- AC-009: Failed authentication attempts are logged
- AC-010: Audit logs cannot be accessed by regular users (admin-only)

**Tasks**:
1. Design audit log database schema with encryption
2. Create audit middleware for FastAPI to intercept all requests
3. Implement structured logging (JSON format)
4. Create audit log query API with filters
5. Build audit log export functionality
6. Implement alerting for sensitive operations
7. Set up database archival for old audit logs
8. Create audit log retention cleanup job
9. Build admin UI for viewing audit logs
10. Write unit tests for audit middleware
11. Test audit log immutability
12. Performance test audit logging (<50ms overhead)

**Dependencies**: STORY-002 (User Authentication)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] All patient data operations logged
- [ ] Audit log query API working
- [ ] Audit logs encrypted and immutable
- [ ] Export functionality tested
- [ ] Alerting configured for sensitive operations
- [ ] Retention policy implemented and tested
- [ ] Security audit confirms compliance with UU 27/2022
- [ ] Performance impact <50ms per request

---

#### STORY-004: Automated Backup System

**Epic**: EPIC-001 - Foundation & Security Infrastructure

**As a** System Administrator
**I want** automated daily backups of all data
**So that** patient data is never lost and we can recover from disasters

**Acceptance Criteria**:
- AC-001: Automated daily backups run at 2 AM (configurable time)
- AC-002: Full database backup (pg_dump) completes successfully
- AC-003: WAL (Write-Ahead Log) archiving is continuous
- AC-004: Backups are encrypted before storage
- AC-005: Backup retention policy implemented (30 days daily, 12 months weekly, 7 years monthly)
- AC-006: Off-site backup copy is created weekly
- AC-007: Backup restoration procedure is tested and documented
- AC-008: Backup failure sends alert notification
- AC-009: Recovery Time Objective (RTO) <4 hours for critical systems
- AC-010: Recovery Point Objective (RPO) <15 minutes for critical data

**Tasks**:
1. Create backup script using pg_dump
2. Configure continuous WAL archiving
3. Implement backup encryption (AES-256)
4. Create backup retention policy script
5. Set up off-site backup sync (rsync or cloud storage)
6. Build backup monitoring and alerting
7. Create backup restoration script
8. Document disaster recovery procedures
9. Test backup restoration quarterly
10. Create backup verification script (corruption check)
11. Set up automated backup testing
12. Create backup dashboard showing status

**Dependencies**: STORY-001 (System Deployment)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Daily backups automated and tested
- [ ] WAL archiving continuous
- [ ] Backups encrypted
- [ ] Retention policy implemented
- [ ] Off-site backup working
- [ ] Restoration tested and documented
- [ ] RTO and RPO targets met
- [ ] Backup monitoring dashboard functional
- [ ] Disaster recovery tested at least once

---

#### STORY-005: System Monitoring & Alerting

**Epic**: EPIC-001 - Foundation & Security Infrastructure

**As a** IT Administrator
**I want** to monitor system health and performance
**So that** I can detect and resolve issues before they impact users

**Acceptance Criteria**:
- AC-001: System health metrics collected (CPU, memory, disk, network)
- AC-002: Application metrics collected (response time, request rate, error rate)
- AC-003: Database metrics collected (connections, query performance, locks)
- AC-004: Dashboard shows real-time system status
- AC-005: Alerts sent for critical failures (service down, disk full, high error rate)
- AC-006: API rate limit monitoring configured
- AC-007: Log aggregation configured (all services in one place)
- AC-008: Uptime monitoring configured with external service
- AC-009: Performance baseline established and monitored
- AC-010: Alerting channels: Email, SMS, WhatsApp (for critical alerts)

**Tasks**:
1. Set up Prometheus for metrics collection
2. Configure Grafana dashboards
3. Create application metrics in FastAPI
4. Set up database metrics exporter
5. Configure alerting rules in Prometheus Alertmanager
6. Set up log aggregation (ELK or similar)
7. Configure external uptime monitoring (UptimeRobot or similar)
8. Create runbooks for common alerts
9. Document monitoring procedures
10. Test all alerting channels
11. Establish performance baselines
12. Create monitoring documentation

**Dependencies**: STORY-001 (System Deployment)

**Priority**: Should Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] All metrics collected and displayed
- [ ] Dashboards created and customized
- [ ] Alerts tested and working
- [ ] Log aggregation functional
- [ ] Uptime monitoring configured
- [ ] Runbooks created for common issues
- [ ] Team trained on monitoring tools
- [ ] Performance baselines documented

---

### Epic 2: Patient Registration & Queue Management (EPIC-002)

---

#### STORY-006: New Patient Registration

**Epic**: EPIC-002 - Patient Registration & Queue Management

**As a** Petugas Pendaftaran (Registration Clerk)
**I want** to register new patients quickly and accurately
**So that** patients can receive care without long wait times

**Acceptance Criteria**:
- AC-001: Registration form captures all required demographics (NIK, nama, tanggal lahir, alamat, telepon)
- AC-002: NIK validation (16 digits) with format checking
- AC-003: Duplicate patient detection by NIK or name+DOB
- AC-004: Auto-generate unique medical record number (no. RM)
- AC-005: BPJS eligibility check via VClaim API completes in <5 seconds
- AC-006: Registration time <3 minutes per patient
- AC-007: Emergency contact information captured
- AC-008: Insurance information captured (BPJS, Asuransi, Umum)
- AC-009: Patient photo capture (optional)
- AC-010: Registration works offline (syncs when online)

**Tasks**:
1. Design patient database schema
2. Build patient registration form UI
3. Implement NIK validation logic
4. Create duplicate patient detection algorithm
5. Build medical record number generator
6. Integrate BPJS VClaim API for eligibility check
7. Implement offline-first data storage (IndexedDB)
8. Create data synchronization logic
9. Build registration confirmation print
10. Write unit tests for validation logic
11. Test registration with slow/no internet
12. Performance test: Registration <3 minutes

**Dependencies**: STORY-002 (User Authentication)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Registration form complete and validated
- [ ] BPJS integration working
- [ ] Duplicate detection working
- [ ] Offline registration tested
- [ ] Performance target met (<3 min)
- [ ] NIK validation tested with edge cases
- [ ] Patient photo capture tested
- [ ] Cross-browser testing completed

---

#### STORY-007: Returning Patient Check-in

**Epic**: EPIC-002 - Patient Registration & Queue Management

**As a** Petugas Pendaftaran (Registration Clerk)
**I want** to quickly find and check-in returning patients
**So that** patients don't have to provide information again

**Acceptance Criteria**:
- AC-001: Patient lookup time <10 seconds
- AC-002: Support multiple search methods (MRN, BPJS number, NIK, name+DOB, phone)
- AC-003: Display last visit date and diagnoses
- AC-004: Highlight changes in patient information since last visit
- AC-005: Quick check-in functionality (single click)
- AC-006: Verify current insurance status
- AC-007: Allow patient information updates
- AC-008: Generate queue number automatically
- AC-009: Lookup works offline for existing patients
- AC-010: Display patient allergy warnings prominently

**Tasks**:
1. Build patient search UI with multiple filters
2. Create optimized database queries for fast search
3. Implement search indexing on patient table
4. Build patient summary view (last visit, diagnoses, allergies)
5. Create check-in workflow
6. Implement insurance status verification
7. Build patient update form
8. Integrate with queue management system
9. Add offline patient caching
10. Performance test: Search <10 seconds
11. Test with various search methods
12. Write unit tests for search logic

**Dependencies**: STORY-006 (New Patient Registration)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] All search methods working
- [ ] Performance target met (<10 sec)
- [ ] Patient summary displayed correctly
- [ ] Check-in workflow tested
- [ ] Insurance verification working
- [ ] Offline search tested
- [ ] Allergy warnings displayed
- [ ] User feedback from registration staff

---

#### STORY-008: BPJS Eligibility Verification

**Epic**: EPIC-002 - Patient Registration & Queue Management

**As a** Petugas Pendaftaran (Registration Clerk)
**I want** to instantly verify BPJS membership status
**So that** we avoid claim rejections and patients know their coverage

**Acceptance Criteria**:
- AC-001: BPJS eligibility check via VClaim API completes in <5 seconds
- AC-002: Display BPJS membership status (Aktif, Tidak Aktif, etc.)
- AC-003: Validate BPJS card number format
- AC-004: Display member information (nama, faskes, kelas)
- AC-005: Handle BPJS API failures gracefully with fallback
- AC-006: Cache eligibility results for 24 hours (with expiration)
- AC-007: Show eligibility history (previous checks)
- AC-008: Support manual override if API is down (with reason)
- AC-009: Log all BPJS API calls for audit
- AC-010: Display error messages in Indonesian

**Tasks**:
1. Create BPJS VClaim API client library
2. Implement eligibility check endpoint
3. Build BPJS card validation logic
4. Create result caching mechanism (Redis)
5. Implement error handling and retry logic
6. Build eligibility status display UI
7. Create manual override workflow with approval
8. Add audit logging for API calls
9. Write API integration tests
10. Test with BPJS sandbox environment
11. Test API failure scenarios
12. Document BPJS error codes

**Dependencies**: STORY-006 (New Patient Registration), STORY-022 (BPJS VClaim API)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] BPJS API integration working
- [ ] Performance target met (<5 sec)
- [ ] Error handling tested
- [ ] Caching working correctly
- [ ] Audit logging functional
- [ ] Manual override workflow tested
- [ ] Indonesian error messages verified
- [ ] BPJS sandbox testing completed

---

#### STORY-009: Online Appointment Booking

**Epic**: EPIC-002 - Patient Registration & Queue Management

**As a** Pasien (Patient)
**I want** to book appointments online through my phone
**So that** I don't have to wait in long queues at the hospital

**Acceptance Criteria**:
- AC-001: Patient self-service booking portal accessible via web
- AC-002: Display available appointment slots in real-time
- AC-003: Select doctor and polyclinic for appointment
- AC-004: Send booking confirmation via SMS/WhatsApp
- AC-005: Cancel or reschedule appointments
- AC-006: Mobile JKN API integration for BPJS patients
- AC-007: Prevent double-booking of time slots
- AC-008: Queue number reserved upon booking
- AC-009: Display estimated wait time
- AC-010: Booking works on mobile browsers

**Tasks**:
1. Design appointment database schema
2. Build appointment booking UI
3. Create real-time slot availability display
4. Integrate SMS/WhatsApp API for notifications
5. Implement appointment cancellation/reschedule
6. Integrate BPJS Mobile JKN API
7. Build slot reservation logic (prevent double-booking)
8. Create queue management integration
9. Implement mobile-responsive design
10. Test booking flow end-to-end
11. Test with mobile devices
12. Load test for concurrent bookings

**Dependencies**: STORY-006 (New Patient Registration), STORY-023 (BPJS Antrean API)

**Priority**: Should Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Booking portal functional
- [ ] Real-time availability working
- [ ] SMS/WhatsApp notifications tested
- [ ] Mobile JKN integration working
- [ ] Double-booking prevention tested
- [ ] Mobile responsiveness verified
- [ ] Cancellation/reschedule tested
- [ ] User testing with patients

---

#### STORY-010: Queue Management System

**Epic**: EPIC-002 - Patient Registration & Queue Management

**As a** Petugas Pendaftaran (Registration Clerk)
**I want** to manage patient queues across all departments
**So that** patients know when they will be served and wait times are reduced

**Acceptance Criteria**:
- AC-001: Queue number generation per department (Poli, Farmasi, Lab, Radiologi, Kasir)
- AC-002: Digital queue display screens (web-based)
- AC-003: SMS queue notifications (when your turn is approaching)
- AC-004: Queue status viewable via mobile web
- AC-005: Priority queue management (lansia, ibu hamil, difabel, emergency)
- AC-006: Average wait time display
- AC-007: BPJS Antrean API integration
- AC-008: Queue statistics dashboard for administrators
- AC-009: Recall queue number (call next patient)
- AC-010: Queue numbers work offline (sync when online)

**Tasks**:
1. Design queue database schema
2. Build queue number generation logic
3. Create digital queue display UI
4. Integrate SMS API for notifications
5. Build mobile web queue status view
6. Implement priority queue logic
7. Calculate average wait times
8. Integrate BPJS Antrean API
9. Build queue statistics dashboard
10. Create queue recall functionality
11. Implement offline queue operation
12. Test queue flow end-to-end

**Dependencies**: STORY-006 (New Patient Registration), STORY-023 (BPJS Antrean API)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Queue generation working for all departments
- [ ] Digital displays functional
- [ ] SMS notifications tested
- [ ] Mobile view tested
- [ ] Priority queues working
- [ ] BPJS API integration tested
- [ ] Statistics dashboard accurate
- [ ] Offline queue operation tested
- [ ] Wait time calculations accurate

---

### Epic 3: Medical Records & Clinical Documentation (EPIC-003)

---

#### STORY-011: Patient History View

**Epic**: EPIC-003 - Medical Records & Clinical Documentation

**As a** Dokter (Doctor)
**I want** to view complete patient history instantly
**So that** I can make informed clinical decisions

**Acceptance Criteria**:
- AC-001: Display complete history in single view
- AC-002: Timeline visualization of past encounters
- AC-003: Quick access to recent visits (last 5)
- AC-004: Search by date range
- AC-005: Export to PDF (patient copy)
- AC-006: Include demographics, contacts, insurance, emergency contacts
- AC-007: Medical history: visits, hospitalizations, surgeries, allergies, chronic conditions
- AC-008: Family medical history
- AC-009: Social history (smoking, alcohol, occupation)
- AC-010: Immunization records
- AC-011: History view works offline

**Tasks**:
1. Design patient history database schema
2. Build patient history aggregation API
3. Create timeline visualization component
4. Build patient history summary view
5. Implement date range filtering
6. Create PDF export functionality
7. Add offline data caching (IndexedDB)
8. Optimize queries for fast loading (<3 seconds)
9. Test with patients with extensive history
10. Test PDF export layout
11. Test offline functionality
12. User acceptance testing with doctors

**Dependencies**: STORY-006 (New Patient Registration), STORY-007 (Returning Patient Check-in)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] All history sections displayed
- [ ] Timeline visualization working
- [ ] Performance target met (<3 sec load)
- [ ] PDF export tested
- [ ] Offline viewing tested
- [ ] Doctor feedback positive
- [ ] Cross-browser tested
- [ ] Mobile responsive tested

---

#### STORY-012: ICD-10 Problem List

**Epic**: EPIC-003 - Medical Records & Clinical Documentation

**As a** Dokter (Doctor)
**I want** to maintain a problem list with ICD-10 codes
**So that** I can track patient conditions over time

**Acceptance Criteria**:
- AC-001: ICD-10 code lookup <5 seconds
- AC-002: Search by code or description (Indonesian)
- AC-003: Display Indonesian descriptions
- AC-004: Maintain active problem list
- AC-005: Problem status tracking (Active, Resolved, Chronic, Acute)
- AC-006: Onset date recording
- AC-007: Recorder attribution (who diagnosed)
- AC-008: Link problems to encounters
- AC-009: Show problem history
- AC-010: Common codes favorites
- AC-011: Offline ICD-10 lookup available

**Tasks**:
1. Import ICD-10-CM Indonesia database
2. Create ICD-10 search API with indexing
3. Build ICD-10 code selection UI
4. Implement problem list management
5. Create problem status workflow
6. Build problem history view
7. Add favorites functionality
8. Implement offline ICD-10 database (IndexedDB)
9. Optimize search performance
10. Test with various search terms
11. User testing with doctors
12. Sync with SATUSEHAT FHIR Condition

**Dependencies**: STORY-011 (Patient History View)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] ICD-10 database imported
- [ ] Search performance <5 seconds
- [ ] Problem list functional
- [ ] Status tracking working
- [ ] Offline lookup tested
- [ ] SATUSEHAT sync working
- [ ] Doctor feedback positive
- [ ] Indonesian descriptions verified

---

#### STORY-013: Allergy Tracking

**Epic**: EPIC-003 - Medical Records & Clinical Documentation

**As a** Perawat (Nurse)
**I want** to see allergy alerts prominently
**So that** I can prevent adverse reactions

**Acceptance Criteria**:
- AC-001: Allergy alerts always visible in patient banner
- AC-002: Drug allergy recording (allergen, reaction, severity, onset date, source)
- AC-003: Food allergy recording
- AC-004: Environmental allergy recording
- AC-005: Alert during prescription writing
- AC-006: Warning before administering medication
- AC-007: Prevent prescribing allergens (requires override)
- AC-008: Document allergy source (patient-reported, tested)
- AC-009: "No Known Allergies" (NKA) option
- AC-010: Support multiple allergies

**Tasks**:
1. Design allergy database schema
2. Build allergy recording UI
3. Create allergy alert system
4. Implement allergy checking in prescription workflow
5. Create allergy severity classification
6. Build "No Known Allergies" workflow
7. Add allergy alerts to patient banner
8. Implement allergy override with reason
9. Test allergy alerting
10. User testing with nurses and doctors
11. Test with multiple allergies
12. Document allergy override reasons

**Dependencies**: STORY-011 (Patient History View)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Allergy recording functional
- [ ] Alerts always visible
- [ ] Prescription checking working
- [ ] Override with reason implemented
- [ ] NKA option tested
- [ ] Multiple allergies supported
- [ ] Clinical workflow tested
- [ ] Safety review completed

---

#### STORY-014: Medication List

**Epic**: EPIC-003 - Medical Records & Clinical Documentation

**As a** Dokter (Doctor)
**I want** to view patient's current and past medications
**So that** I can avoid drug interactions and duplicate therapies

**Acceptance Criteria**:
- AC-001: Show active medications prominently
- AC-002: Current medication list (drug name, dose, frequency, route, start date, prescriber)
- AC-003: Medication history (discontinued medications)
- AC-004: Discontinued medications with reason
- AC-005: Drug interaction checking
- AC-006: Duplicate therapy warnings
- AC-007: Medication reconciliation on admission
- AC-008: Indication (reason for use)
- AC-009: Medication list exportable
- AC-010: View medication details (manufacturer, batch number)

**Tasks**:
1. Design medication database schema
2. Build medication list UI
3. Create medication history view
4. Implement drug interaction checking API
5. Create duplicate therapy detection
6. Build medication reconciliation workflow
7. Add indication field to prescriptions
8. Create medication export functionality
9. Integrate with drug interaction database
10. Test interaction checking performance
11. User testing with doctors
12. Test medication reconciliation workflow

**Dependencies**: STORY-011 (Patient History View), STORY-027 (Drug Interaction Database)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Medication list accurate
- [ ] Drug interactions checked
- [ ] Duplicate therapy detection working
- [ ] Reconciliation workflow tested
- [ ] Performance acceptable
- [ ] Doctor feedback positive
- [ ] Export functionality tested
- [ ] Clinical safety reviewed

---

#### STORY-015: Clinical Notes (SOAP)

**Epic**: EPIC-003 - Medical Records & Clinical Documentation

**As a** Dokter (Doctor)
**I want** to document patient encounters using SOAP notes
**So that** I can focus on patients instead of paperwork

**Acceptance Criteria**:
- AC-001: Auto-save every 30 seconds
- AC-002: Require digital signature for attestation
- AC-003: Track all changes with audit trail
- AC-004: Support structured templates (SOAP, admission, progress, discharge)
- AC-005: Free text option with auto-save
- AC-006: Version control with audit trail
- AC-007: Note sharing (with patient consent)
- AC-008: Export to PDF
- AC-009: Create notes offline
- AC-010: Sync notes when online

**Tasks**:
1. Design clinical notes database schema with versioning
2. Build SOAP note template UI
3. Implement auto-save functionality
4. Create digital signature workflow
5. Implement audit trail for changes
6. Create note templates (SOAP, admission, etc.)
7. Build free text editor with auto-save
8. Create PDF export
9. Implement offline note creation
10. Add data synchronization
11. Test with clinical workflows
12. User acceptance testing with doctors

**Dependencies**: STORY-011 (Patient History View)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] SOAP notes functional
- [ ] Auto-save working
- [ ] Digital signature implemented
- [ ] Audit trail complete
- [ ] Templates tested
- [ ] Offline creation tested
- [ ] PDF export working
- [ ] Doctor feedback positive
- [ ] Sync tested with poor connectivity

---

### Epic 4: Outpatient Management (EPIC-004)

---

#### STORY-016: Doctor Consultation Workflow

**Epic**: EPIC-004 - Outpatient Management (Poli Rawat Jalan)

**As a** Dokter (Doctor)
**I want** to start and complete patient consultations efficiently
**So that** I can see more patients and provide quality care

**Acceptance Criteria**:
- AC-001: Start consultation in <5 seconds
- AC-002: Display patient summary (demographics, vital signs, history)
- AC-003: Auto-populate common templates
- AC-004: Save progress automatically
- AC-005: Complete encounter in <10 minutes (excluding patient time)
- AC-006: Clinical documentation: chief complaint, HPI, physical exam, assessment, treatment plan
- AC-007: Quick diagnosis entry (ICD-10 codes)
- AC-008: Prescription writing integration
- AC-009: Lab/radiology ordering integration
- AC-010: Return appointment scheduling
- AC-011: Patient education materials
- AC-012: Consultation works offline

**Tasks**:
1. Design encounter database schema
2. Build consultation start UI
3. Create patient summary display
4. Implement common template auto-population
5. Build clinical documentation forms
6. Integrate ICD-10 diagnosis entry
7. Integrate prescription writing (from STORY-017)
8. Integrate lab/radiology ordering
9. Create appointment scheduling integration
10. Add patient education materials library
11. Implement offline consultation mode
12. Test complete consultation flow

**Dependencies**: STORY-011 (Patient History), STORY-012 (ICD-10), STORY-015 (Clinical Notes)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Consultation flow tested end-to-end
- [ ] Performance targets met
- [ ] Templates working
- [ ] All integrations functional
- [ ] Offline mode tested
- [ ] Doctor feedback positive
- [ ] Clinical workflow validated
- [ ] Auto-save working

---

#### STORY-017: Electronic Prescriptions

**Epic**: EPIC-004 - Outpatient Management (Poli Rawat Jalan)

**As a** Dokter (Doctor)
**I want** to write prescriptions electronically with drug interaction checks
**So that** patient safety is ensured and errors are prevented

**Acceptance Criteria**:
- AC-001: Electronic prescribing interface
- AC-002: Drug search (generic and brand) with auto-complete
- AC-003: Dose and frequency selection
- AC-004: Quantity calculation
- AC-005: Route of administration
- AC-006: Special instructions
- AC-007: Check interactions in <3 seconds
- AC-008: Alert for all drug-drug, drug-disease, drug-allergy interactions
- AC-009: Display BPJS coverage status
- AC-010: Print prescriptions with barcode
- AC-011: Support compound prescriptions (racikan)
- AC-012: Electronic prescription to pharmacy

**Tasks**:
1. Create drug database with BPJS codes
2. Build drug search API with auto-complete
3. Create prescription writing UI
4. Implement dose calculation helper
5. Integrate drug interaction checking
6. Create interaction alert display
7. Build BPJS coverage status check
8. Create prescription printing with barcode
9. Implement compound prescription workflow
10. Build electronic prescription transmission to pharmacy
11. Test interaction checking performance
12. User acceptance testing with doctors

**Dependencies**: STORY-014 (Medication List), STORY-027 (Drug Interaction Database)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Prescription UI complete
- [ ] Drug search fast and accurate
- [ ] Interaction checking working
- [ ] BPJS status displayed
- [ ] Barcode printing tested
- [ ] Compound prescriptions tested
- [ ] Electronic transmission to pharmacy working
- [ ] Doctor feedback positive
- [ ] Safety review completed

---

#### STORY-018: Lab/Radiology Ordering

**Epic**: EPIC-004 - Outpatient Management (Poli Rawat Jalan)

**As a** Dokter (Doctor)
**I want** to order lab and radiology tests electronically
**So that** results are tracked and I can view them when ready

**Acceptance Criteria**:
- AC-001: Complete order in <2 minutes
- AC-002: Test catalog search
- AC-003: Package selection (panel)
- AC-004: Clinical indication
- AC-005: Priority selection (routine, urgent, STAT)
- AC-006: Auto-select LOINC codes (lab)
- AC-007: Procedure codes (radiology)
- AC-008: Check insurance coverage
- AC-009: Track order status
- AC-010: Alert when results ready
- AC-011: FHIR ServiceRequest integration for SATUSEHAT

**Tasks**:
1. Import LOINC database for lab tests
2. Create test catalog database
3. Build lab/radiology order UI
4. Implement package/panel selection
5. Create priority selection workflow
6. Auto-assign LOINC codes
7. Create procedure code mapping
8. Implement insurance coverage check
9. Build order status tracking
10. Create result notification system
11. Integrate with SATUSEHAT FHIR ServiceRequest
12. Test order flow end-to-end

**Dependencies**: STORY-016 (Doctor Consultation), STORY-032 (SATUSEHAT Integration)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Order UI complete
- [ ] LOINC codes assigned
- [ ] Insurance check working
- [ ] Status tracking functional
- [ ] Notifications tested
- [ ] SATUSEHAT sync working
- [ ] Performance target met (<2 min)
- [ ] Doctor feedback positive

---

#### STORY-019: BPJS SEP Generation

**Epic**: EPIC-004 - Outpatient Management (Poli Rawat Jalan)

**As a** Dokter (Doctor)
**I want** to generate BPJS SEP automatically during consultation
**So that** claims are not rejected due to missing SEP

**Acceptance Criteria**:
- AC-001: Generate SEP in <10 seconds
- AC-002: Automatic SEP creation (patient eligibility verified, diagnosis populated, poli mapped, doctor assigned)
- AC-003: Validate all required fields
- AC-004: SEP updates (room changes, diagnosis updates, policy changes)
- AC-005: SEP cancellation
- AC-006: SEP history tracking
- AC-007: Handle BPJS API failures gracefully
- AC-008: Display SEP status
- AC-009: Create SEP offline (sync when online)
- AC-010: Display SEP to patient

**Tasks**:
1. Create BPJS SEP API client
2. Build SEP generation logic
3. Implement automatic field population
4. Create SEP validation rules
5. Build SEP update workflow
6. Implement SEP cancellation
7. Create SEP history view
8. Add offline SEP creation
9. Build SEP display UI
10. Integrate with consultation workflow
11. Test with BPJS sandbox
12. Error handling and retry logic

**Dependencies**: STORY-016 (Doctor Consultation), STORY-022 (BPJS VClaim API)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] SEP generation working
- [ ] Automatic population tested
- [ ] Validation working
- [ ] Update/cancellation tested
- [ ] Offline mode tested
- [ ] BPJS API integration tested
- [ ] Error handling robust
- [ ] Doctor workflow tested

---

### Epic 5: Inpatient Management (EPIC-005)

---

#### STORY-020: Bed Management

**Epic**: EPIC-005 - Inpatient Management (Rawat Inap)

**As a** Perawat (Nurse)
**I want** to view bed availability in real-time
**So that** I can assign patients efficiently

**Acceptance Criteria**:
- AC-001: Real-time bed availability dashboard
- AC-002: Total beds per room (occupied, available, maintenance)
- AC-003: Assign bed in <30 seconds
- AC-004: Prevent double-booking
- AC-005: View bed by ward/room
- AC-006: Filter by class (VVIP, VIP, 1, 2, 3)
- AC-007: Filter by gender (male/female/mixed)
- AC-008: Assign patient to bed
- AC-009: Transfer patient between beds
- AC-010: Room status (clean/soiled, maintenance, isolation)
- AC-011: Bed request workflow (request, approve, assign, notify)
- AC-012: Sync with BPJS Aplicare (real-time bed reporting)

**Tasks**:
1. Design bed management database schema
2. Build bed availability dashboard
3. Create bed assignment UI
4. Implement double-booking prevention
5. Create bed filtering and search
6. Build bed transfer workflow
7. Implement room status management
8. Create bed request workflow
9. Integrate BPJS Aplicare API
10. Implement real-time updates (WebSocket)
11. Test bed assignment flow
12. Test Aplicare integration

**Dependencies**: STORY-006 (Patient Registration), STORY-024 (BPJS Aplicare API)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Dashboard displays real-time data
- [ ] Bed assignment working
- [ ] Double-booking prevented
- [ ] Filtering functional
- [ ] Room status tracked
- [ ] BPJS sync working
- [ ] Performance target met (<30 sec)
- [ ] Nurse feedback positive

---

#### STORY-021: Admission Workflow

**Epic**: EPIC-005 - Inpatient Management (Rawat Inap)

**As a** Dokter (Doctor)
**I want** to admit patients quickly to the hospital
**So that** care is not delayed

**Acceptance Criteria**:
- AC-001: Complete admission in <5 minutes
- AC-002: Verify doctor's admission order
- AC-003: Check bed availability
- AC-004: Select room and bed
- AC-005: Update BPJS SEP automatically
- AC-006: Generate admission papers
- AC-007: Room transfer workflow (initiate, approve, update bed, update SEP)
- AC-008: Track all bed changes
- AC-009: Prevent room conflicts
- AC-010: Estimated discharge date
- AC-011: Discharge criteria tracking

**Tasks**:
1. Design admission workflow
2. Build admission order verification
3. Create bed selection UI
4. Implement BPJS SEP update for admission
5. Generate admission document templates
6. Build room transfer workflow
7. Create bed change tracking
8. Implement conflict prevention
9. Add estimated discharge date calculation
10. Create discharge criteria checklist
11. Test admission flow end-to-end
12. User acceptance testing

**Dependencies**: STORY-019 (BPJS SEP Generation), STORY-020 (Bed Management)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Admission flow complete
- [ ] BPJS SEP updated
- [ ] Papers generated
- [ ] Transfer workflow tested
- [ ] Conflicts prevented
- [ ] Performance target met
- [ ] Doctor and nurse feedback positive
- [ ] Clinical workflow validated

---

#### STORY-022: Daily Care Documentation

**Epic**: EPIC-005 - Inpatient Management (Rawat Inap)

**As a** Perawat (Nurse)
**I want** to document daily care at bedside
**So that** records are accurate and up-to-date

**Acceptance Criteria**:
- AC-001: Document care in real-time
- AC-002: Auto-save documentation
- AC-003: Require digital signature
- AC-004: Nursing documentation (flow sheets, narrative notes, care plans, patient education)
- AC-005: Physician progress notes (daily rounds, assessment and plan, orders)
- AC-006: Interdisciplinary notes (respiratory therapy, physical therapy, nutrition, social work)
- AC-007: Shift documentation (shift handoff, change of shift report)
- AC-008: Template-based and free text
- AC-009: Support care plans
- AC-010: Export to discharge summary
- AC-011: Mobile-optimized for bedside documentation

**Tasks**:
1. Design care documentation database schema
2. Build nursing documentation forms
3. Create physician progress note forms
4. Implement interdisciplinary note templates
5. Build shift handoff workflow
6. Create care plan templates
7. Implement digital signature
8. Add auto-save functionality
9. Create mobile-optimized UI
10. Build discharge summary export
11. Test bedside documentation
12. User acceptance testing with nurses

**Dependencies**: STORY-021 (Admission Workflow), STORY-015 (Clinical Notes)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] All documentation forms working
- [ ] Auto-save functional
- [ ] Digital signature implemented
- [ ] Templates complete
- [ ] Mobile UI tested
- [ ] Discharge export working
- [ ] Nurse feedback positive
- [ ] Bedside workflow tested

---

#### STORY-023: Discharge Planning

**Epic**: EPIC-005 - Inpatient Management (Rawat Inap)

**As a** Dokter (Doctor)
**I want** to prepare and complete patient discharges efficiently
**So that** beds are available for new patients

**Acceptance Criteria**:
- AC-001: Complete discharge in <30 minutes
- AC-002: Discharge readiness assessment (clinical stability, medication reconciliation, education completed, follow-up scheduled)
- AC-003: Discharge orders (medications, instructions, activity restrictions, diet, follow-up)
- AC-004: Generate discharge summary automatically (admission diagnosis, procedures, treatment, discharge diagnosis, medications, follow-up)
- AC-005: Reconcile medications
- AC-006: Schedule follow-up appointments
- AC-007: Finalize BPJS claim
- AC-008: Update BPJS SEP (close SEP on discharge)
- AC-009: Discharge criteria checklist
- AC-010: Discharge instructions for patient

**Tasks**:
1. Create discharge readiness assessment
2. Build discharge orders form
3. Implement automatic discharge summary generation
4. Create medication reconciliation workflow
5. Integrate follow-up appointment scheduling
6. Build BPJS claim finalization
7. Implement SEP closure
8. Create discharge criteria checklist
9. Generate patient discharge instructions
10. Test discharge flow end-to-end
11. User acceptance testing
12. Test BPJS claim finalization

**Dependencies**: STORY-021 (Admission Workflow), STORY-019 (BPJS SEP Generation), STORY-030 (BPJS Claims)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Discharge flow complete
- [ ] Summary generated automatically
- [ ] Medication reconciliation tested
- [ ] Follow-up scheduled
- [ ] BPJS claim finalized
- [ ] SEP closed
- [ ] Performance target met
- [ ] Doctor feedback positive

---

### Epic 6: Pharmacy Management (EPIC-006)

---

#### STORY-024: Pharmacy Inventory Management

**Epic**: EPIC-006 - Pharmacy Management

**As a** Apoteker (Pharmacist)
**I want** to track drug stock levels and expiry dates
**So that** we never run out of essential drugs and don't dispense expired medications

**Acceptance Criteria**:
- AC-001: Drug master file (generic name, brand names, dosage forms, BPJS codes, e-Katalog codes, manufacturer)
- AC-002: Real-time stock updates
- AC-003: Current stock levels, bin locations, expiry dates, batch numbers
- AC-004: Stock transactions (purchase orders, goods received, adjustments, transfers, returns)
- AC-005: Near-expiry alerts (3 months)
- AC-006: Expired drug quarantine
- AC-007: Prevent dispensing expired drugs
- AC-008: First-in-first-out (FIFO) dispensing
- AC-009: Minimum stock levels and reorder point alerts
- AC-010: Auto-generate purchase orders

**Tasks**:
1. Design drug master database
2. Build inventory tracking system
3. Create stock transaction recording
4. Implement expiry date tracking
5. Build near-expiry alerting
6. Create expired drug quarantine workflow
7. Implement FIFO logic
8. Set up reorder point alerts
9. Create purchase order generation
10. Build inventory dashboard
11. Test inventory workflows
12. User acceptance testing

**Dependencies**: STORY-002 (User Authentication)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Drug master populated
- [ ] Stock tracking accurate
- [ ] Expiry alerts working
- [ ] Expired drugs quarantined
- [ ] FIFO logic tested
- [ ] Reorder alerts functional
- [ ] PO generation tested
- [ ] Pharmacist feedback positive

---

#### STORY-025: Prescription Dispensing

**Epic**: EPIC-006 - Pharmacy Management

**As a** Apoteker (Pharmacist)
**I want** to process prescriptions quickly with barcode scanning
**So that** patients don't wait long and errors are prevented

**Acceptance Criteria**:
- AC-001: Process prescription in <5 minutes
- AC-002: Receive prescriptions electronically
- AC-003: Queue by priority
- AC-004: Barcode patient verification
- AC-005: Verify prescription
- AC-006: Check drug interactions
- AC-007: Check stock availability
- AC-008: Barcode scan all drugs (verify correct drug and dose, prevent errors)
- AC-009: Count/package medication
- AC-010: Label generation
- AC-011: Pharmacist verification
- AC-012: Document counseling
- AC-013: Dispensing history

**Tasks**:
1. Build electronic prescription receiving
2. Create dispensing queue with priorities
3. Implement barcode patient verification
4. Build prescription verification UI
5. Integrate drug interaction checking
6. Create stock availability check
7. Implement barcode drug scanning
8. Build label generation
9. Create pharmacist verification workflow
10. Add counseling documentation
11. Create dispensing history view
12. Test dispensing workflow end-to-end

**Dependencies**: STORY-017 (Electronic Prescriptions), STORY-027 (Drug Interaction Database), STORY-024 (Inventory)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Prescription receiving working
- [ ] Queue prioritization tested
- [ ] Barcode scanning accurate
- [ ] Interaction checking functional
- [ ] Label generation tested
- [ ] Verification workflow tested
- [ ] Performance target met
- [ ] Pharmacist feedback positive

---

#### STORY-026: Drug Interaction Database Integration

**Epic**: EPIC-006 - Pharmacy Management

**As a** Developer
**I want** to integrate a comprehensive drug interaction database
**So that** the system can automatically check for interactions

**Acceptance Criteria**:
- AC-001: Check interactions in <3 seconds
- AC-002: Alert for all interactions (drug-drug, drug-disease, drug-allergy, drug-food, therapeutic duplications)
- AC-003: Display severity levels (contraindicated, severe, moderate, mild)
- AC-004: Display recommendations
- AC-005: Require override reason
- AC-006: Alert at prescribing and dispensing
- AC-007: Document resolution
- AC-008: Update interaction database regularly
- AC-009: Custom interaction rules
- AC-010: Offline interaction checking available

**Tasks**:
1. Select/integrate drug interaction database API
2. Create interaction checking service
3. Implement severity classification
4. Build alert display UI
5. Create override workflow with reason
6. Integrate into prescription writing
7. Integrate into dispensing workflow
8. Add offline interaction database
9. Create custom rule configuration
10. Set up automated database updates
11. Performance test interaction checking
12. Test with known interaction cases

**Dependencies**: STORY-017 (Electronic Prescriptions)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Interaction database integrated
- [ ] Checking performance <3 seconds
- [ ] All interaction types covered
- [ ] Severity levels accurate
- [ ] Override workflow tested
- [ ] Offline checking working
- [ ] Custom rules tested
- [ ] Clinical validation completed

---

### Epic 9: Billing, Finance & Claims (EPIC-009)

---

#### STORY-027: Invoice Generation

**Epic**: EPIC-009 - Billing, Finance & Claims

**As a** Staff Keuangan (Billing Staff)
**I want** to generate accurate invoices automatically
**So that** billing errors are reduced and patients are charged correctly

**Acceptance Criteria**:
- AC-001: Capture all charges (professional fees, hotel services, drugs, lab, radiology, procedures, supplies)
- AC-002: Apply correct billing rules
- AC-003: Generate accurate invoices
- AC-004: Support multiple payers (BPJS, Asuransi, Umum)
- AC-005: Package rates (BPJS INA-CBG)
- AC-006: Fee-for-service (private insurance)
- AC-007: Discount rules
- AC-008: Co-payment calculations
- AC-009: Invoice approval workflow
- AC-010: Approve invoices before discharge

**Tasks**:
1. Design billing database schema
2. Create charge capture system
3. Build billing rules engine
4. Implement invoice generation logic
5. Create BPJS INA-CBG package rate calculation
6. Build fee-for-service calculation
7. Implement discount rules
8. Create co-payment calculation
9. Build invoice approval workflow
10. Create invoice templates (PDF)
11. Test billing calculations
12. User acceptance testing

**Dependencies**: STORY-016 (Doctor Consultation), STORY-021 (Admission Workflow)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] All charges captured
- [ ] Billing rules accurate
- [ ] Invoice generation tested
- [ ] Multiple payers supported
- [ ] Package rates calculated correctly
- [ ] Approval workflow tested
- [ ] PDF generation working
- [ ] Billing staff feedback positive

---

#### STORY-028: Payment Processing

**Epic**: EPIC-009 - Billing, Finance & Claims

**As a** Kasir (Cashier)
**I want** to process payments efficiently
**So that** patient checkout is fast and accurate

**Acceptance Criteria**:
- AC-001: Process payments accurately
- AC-002: Support multiple payment methods (cash, credit/debit cards, bank transfer, virtual account, payment gateway)
- AC-003: Generate receipts
- AC-004: Allocate payments to invoices
- AC-005: Payment reconciliation
- AC-006: Track patient deposits
- AC-007: Manage accounts receivable
- AC-008: Payment reminders
- AC-009: Collections management
- AC-010: Financial reports (revenue, aging, payments)

**Tasks**:
1. Create payment processing API
2. Integrate payment gateway (Midtrans/Xendit)
3. Build payment recording UI
4. Create receipt generation
5. Implement payment allocation logic
6. Build deposit tracking
7. Create accounts receivable management
8. Implement payment reminder system
9. Build financial reports
10. Test payment processing
11. Test payment gateway integration
12. User acceptance testing

**Dependencies**: STORY-027 (Invoice Generation)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Payment processing working
- [ ] Multiple methods supported
- [ ] Receipt generation tested
- [ ] Payment gateway integrated
- [ ] Reconciliation accurate
- [ ] Deposits tracked
- [ ] Reports generated
- [ ] Cashier feedback positive

---

#### STORY-029: BPJS Claims Preparation

**Epic**: EPIC-009 - Billing, Finance & Claims

**As a** Staff BPJS (Insurance Specialist)
**I want** to prepare BPJS claim data automatically
**So that** claims are accurate and submitted on time

**Acceptance Criteria**:
- AC-001: Generate e-Claim files automatically
- AC-002: Validate claim data
- AC-003: Group by INA-CBG
- AC-004: Calculate package rate
- AC-005: Submit claims within BPJS deadline (21 days after discharge)
- AC-006: Submit to BPJS gateway
- AC-007: Track submission status
- AC-008: Handle submission errors
- AC-009: Respond to verification queries
- AC-010: Submit additional documents

**Tasks**:
1. Create e-Claim data generation
2. Implement claim validation rules
3. Build INA-CBG grouping logic
4. Calculate package rates
5. Integrate BPJS e-Claim API
6. Create submission status tracking
7. Build error handling and retry
8. Create verification response workflow
9. Implement document upload
10. Test claim submission
11. Test with BPJS sandbox
12. User acceptance testing

**Dependencies**: STORY-019 (BPJS SEP Generation), STORY-023 (Discharge Planning), STORY-027 (Invoice Generation)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] e-Claim generation working
- [ ] Validation complete
- [ ] INA-CBG grouping accurate
- [ ] API integration tested
- [ ] Status tracking functional
- [ ] Error handling robust
- [ ] Submission tested
- [ ] BPJS staff feedback positive

---

### Epic 10: BPJS Kesehatan Integration (EPIC-010)

---

#### STORY-030: BPJS VClaim API Integration

**Epic**: EPIC-010 - BPJS Kesehatan Integration

**As a** Developer
**I want** to integrate BPJS VClaim API
**So that** the system can verify eligibility, create SEPs, and check claims

**Acceptance Criteria**:
- AC-001: Patient eligibility checking
- AC-002: SEP creation, update, deletion
- AC-003: Referral (rujukan) information
- AC-004: Diagnosis/procedure lookup
- AC-005: Facility and provider lookup
- AC-006: Claim status monitoring
- AC-007: Summary of bill (SRB)
- AC-008: All VClaim endpoints functional
- AC-009: Handle API failures gracefully
- AC-010: Retry failed requests
- AC-011: Log all API calls
- AC-012: Monitor API performance

**Tasks**:
1. Create BPJS VClaim API client library
2. Implement authentication (Cons-ID, Secret Key)
3. Build eligibility check endpoint
4. Implement SEP CRUD operations
5. Create referral lookup
6. Build diagnosis/procedure reference
7. Implement facility lookup
8. Create claim status monitoring
9. Build SRB generation
10. Implement retry logic with exponential backoff
11. Add comprehensive logging
12. Create API monitoring dashboard

**Dependencies**: STORY-002 (User Authentication)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] All endpoints implemented
- [ ] Authentication working
- [ ] Error handling robust
- [ ] Retry logic tested
- [ ] Logging comprehensive
- [ ] Monitoring functional
- [ ] BPJS sandbox tested
- [ ] API performance acceptable

---

#### STORY-031: BPJS Antrean API Integration

**Epic**: EPIC-010 - BPJS Kesehatan Integration

**As a** Developer
**I want** to integrate BPJS Antrean API
**So that** patients can book appointments and check queue status via Mobile JKN

**Acceptance Criteria**:
- AC-001: Online booking integration
- AC-002: Queue management
- AC-003: Queue status updates
- AC-004: Queue list publication
- AC-005: Real-time sync
- AC-006: Handle API failures gracefully
- AC-007: Retry failed requests
- AC-008: Log all API calls

**Tasks**:
1. Create BPJS Antrean API client
2. Implement booking endpoint
3. Build queue management sync
4. Create status update endpoint
5. Implement queue list publication
6. Add real-time synchronization
7. Implement error handling
8. Add retry logic
9. Add logging
10. Test with BPJS sandbox
11. Integration testing
12. Performance testing

**Dependencies**: STORY-009 (Online Appointment Booking), STORY-010 (Queue Management)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] All endpoints implemented
- [ ] Real-time sync working
- [ ] Error handling robust
- [ ] Retry logic tested
- [ ] Logging functional
- [ ] BPJS sandbox tested
- [ ] Integration with queue system tested

---

#### STORY-032: BPJS Aplicare API Integration

**Epic**: EPIC-010 - BPJS Kesehatan Integration

**As a** Developer
**I want** to integrate BPJS Aplicare API
**So that** bed availability is reported in real-time

**Acceptance Criteria**:
- AC-001: Bed availability reporting
- AC-002: Real-time bed updates
- AC-003: Room class information
- AC-004: Automatic sync (every update)
- AC-005: Handle API failures gracefully
- AC-006: Retry failed requests
- AC-007: Log all API calls

**Tasks**:
1. Create BPJS Aplicare API client
2. Implement bed availability reporting
3. Build real-time sync on bed changes
4. Add room class information
5. Implement automatic synchronization
6. Add error handling
7. Implement retry logic
8. Add logging
9. Test with BPJS sandbox
10. Integration testing with bed management
11. Performance testing
12. Monitoring dashboard

**Dependencies**: STORY-020 (Bed Management)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Bed reporting working
- [ ] Real-time sync tested
- [ ] Room class info accurate
- [ ] Automatic sync functional
- [ ] Error handling robust
- [ ] BPJS sandbox tested
- [ ] Bed management integration verified

---

### Epic 11: SATUSEHAT FHIR R4 Integration (EPIC-011)

---

#### STORY-033: SATUSEHAT Organization Registration

**Epic**: EPIC-011 - SATUSEHAT FHIR R4 Integration

**As a** Administrator Rumah Sakit (Hospital Administrator)
**I want** to register our facility with SATUSEHAT
**So that** we are compliant with Ministry of Health regulations

**Acceptance Criteria**:
- AC-001: Organization registration completed
- AC-002: Facility data submitted
- AC-003: OAuth 2.0 authentication working
- AC-004: Client credentials configured
- AC-005: Basic connectivity verified
- AC-006: Access token obtained
- AC-007: Facility profile created

**Tasks**:
1. Register hospital with SATUSEHAT portal
2. Obtain OAuth client credentials
3. Create OAuth authentication flow
4. Implement token refresh logic
5. Build facility data submission
6. Create organization profile
7. Test connectivity with SATUSEHAT staging
8. Verify access token
9. Document registration process
10. Create configuration UI for credentials
11. Test token refresh
12. Security review of credential storage

**Dependencies**: STORY-002 (User Authentication)

**Priority**: Must Have

**Story Points**: 5

**Definition of Done Checklist**:
- [ ] Hospital registered
- [ ] OAuth credentials obtained
- [ ] Authentication working
- [ ] Token refresh tested
- [ ] Facility data submitted
- [ ] Connectivity verified
- [ ] Staging environment tested
- [ ] Documentation complete

---

#### STORY-034: SATUSEHAT Patient Data Sync

**Epic**: EPIC-011 - SATUSEHAT FHIR R4 Integration

**As a** System
**I want** to sync patient demographics automatically with SATUSEHAT
**So that** data is consistent across the national health system

**Acceptance Criteria**:
- AC-001: Create FHIR Patient resources
- AC-002: Submit patient demographics to SATUSEHAT
- AC-003: Validate FHIR Patient resources
- AC-004: Handle SATUSEHAT API errors
- AC-005: Sync patient data within 24 hours
- AC-006: Queue failed submissions for retry
- AC-007: Monitor submission status
- AC-008: Auto-sync on patient creation/update

**Tasks**:
1. Create FHIR Patient resource builder
2. Implement patient data validation
3. Build submission API endpoint
4. Create retry queue for failed submissions
5. Implement monitoring dashboard
6. Add auto-sync triggers
7. Test FHIR resource validation
8. Test with SATUSEHAT staging
9. Error handling and logging
10. Performance testing
11. Security review
12. Documentation

**Dependencies**: STORY-033 (Organization Registration), STORY-006 (New Patient Registration)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] FHIR Patient resources created
- [ ] Submission working
- [ ] Validation complete
- [ ] Error handling robust
- [ ] Auto-sync tested
- [ ] 24-hour SLA met
- [ ] Staging tested
- [ ] Monitoring functional

---

#### STORY-035: SATUSEHAT Encounter Data Sync

**Epic**: EPIC-011 - SATUSEHAT FHIR R4 Integration

**As a** System
**I want** to submit encounter data to SATUSEHAT
**So that** visit documentation is reported nationally

**Acceptance Criteria**:
- AC-001: Create FHIR Encounter resources
- AC-002: Submit encounter data for outpatient visits
- AC-003: Submit encounter data for inpatient admissions
- AC-004: Validate FHIR Encounter resources
- AC-005: Handle SATUSEHAT API errors
- AC-006: Sync encounters within 24 hours
- AC-007: Queue failed submissions for retry
- AC-008: Monitor submission status

**Tasks**:
1. Create FHIR Encounter resource builder
2. Implement encounter data validation
3. Build submission API endpoint
4. Create retry queue for failed submissions
5. Implement monitoring dashboard
6. Add auto-sync triggers
7. Test FHIR resource validation
8. Test with SATUSEHAT staging
9. Error handling and logging
10. Performance testing
11. Documentation

**Dependencies**: STORY-034 (Patient Data Sync), STORY-016 (Doctor Consultation), STORY-021 (Admission Workflow)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] FHIR Encounter resources created
- [ ] Submission working
- [ ] Validation complete
- [ ] Error handling robust
- [ ] Auto-sync tested
- [ ] 24-hour SLA met
- [ ] Staging tested
- [ ] Monitoring functional

---

#### STORY-036: SATUSEHAT Condition (Diagnosis) Sync

**Epic**: EPIC-011 - SATUSEHAT FHIR R4 Integration

**As a** System
**I want** to submit diagnosis data with ICD-10 codes to SATUSEHAT
**So that** epidemiological reporting is accurate

**Acceptance Criteria**:
- AC-001: Create FHIR Condition resources
- AC-002: Submit diagnoses with ICD-10 codes
- AC-003: Validate FHIR Condition resources
- AC-004: Handle SATUSEHAT API errors
- AC-005: Sync diagnoses within 24 hours
- AC-006: Queue failed submissions for retry
- AC-007: Monitor submission status

**Tasks**:
1. Create FHIR Condition resource builder
2. Implement ICD-10 code mapping
3. Build submission API endpoint
4. Create retry queue for failed submissions
5. Implement monitoring dashboard
6. Add auto-sync triggers
7. Test FHIR resource validation
8. Test with SATUSEHAT staging
9. Error handling and logging
10. Documentation

**Dependencies**: STORY-035 (Encounter Data Sync), STORY-012 (ICD-10 Problem List)

**Priority**: Must Have

**Story Points**: 5

**Definition of Done Checklist**:
- [ ] FHIR Condition resources created
- [ ] ICD-10 codes mapped
- [ ] Submission working
- [ ] Validation complete
- [ ] Auto-sync tested
- [ ] 24-hour SLA met
- [ ] Staging tested

---

### Epic 14: User Management & Training (EPIC-014)

---

#### STORY-037: User Management Interface

**Epic**: EPIC-014 - User Management & Training

**As a** IT Administrator
**I want** to manage users and roles easily
**So that** staff have appropriate access to the system

**Acceptance Criteria**:
- AC-001: Create, update, deactivate users
- AC-002: Assign roles and permissions
- AC-003: Department-based access
- AC-004: User profile management
- AC-005: Bulk user import
- AC-006: User access request workflow
- AC-007: Password reset functionality
- AC-008: User activity logs

**Tasks**:
1. Build user management UI
2. Create role assignment interface
3. Implement department-based access
4. Build user profile forms
5. Create bulk import functionality (CSV)
6. Implement access request workflow
7. Add password reset admin function
8. Create activity log viewer
9. Test user management workflows
10. Security review
11. Documentation
12. User acceptance testing

**Dependencies**: STORY-002 (User Authentication)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] User management UI complete
- [ ] Role assignment working
- [ ] Bulk import tested
- [ ] Access workflow tested
- [ ] Password reset functional
- [ ] Activity logs accessible
- [ ] Security review passed
- [ ] Admin feedback positive

---

#### STORY-038: Training Management System

**Epic**: EPIC-014 - User Management & Training

**As a** Koordinator Pelatihan (Training Coordinator)
**I want** to track training completion for all staff
**So that** compliance is ensured and staff are prepared to use the system

**Acceptance Criteria**:
- AC-001: Training module assignment
- AC-002: Training progress tracking
- AC-003: Training completion reporting
- AC-004: Training materials repository
- AC-005: User guides and manuals
- AC-006: Video tutorials
- AC-007: Interactive tutorials
- AC-008: Training completion >90%

**Tasks**:
1. Design training database schema
2. Build training assignment system
3. Create progress tracking UI
4. Build completion reports
5. Create materials repository
6. Develop user guides
7. Create video tutorials
8. Build interactive tutorials
9. Launch training program
10. Track completion rates
11. Send reminders for incomplete training
12. Generate compliance reports

**Dependencies**: STORY-037 (User Management)

**Priority**: Should Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] Training system functional
- [ ] All modules created
- [ ] Progress tracking working
- [ ] Reports generated
- [ ] 90% completion target met
- [ ] Materials accessible
- [ ] User feedback positive
- [ ] Compliance requirements met

---

### Epic 15: System Configuration & Master Data (EPIC-015)

---

#### STORY-039: Hospital Configuration

**Epic**: EPIC-015 - System Configuration & Master Data

**As a** System Administrator
**I want** to configure hospital information and settings
**So that** the system is branded correctly and works for our hospital

**Acceptance Criteria**:
- AC-001: Hospital profile (name, address, contact, license, BPJS PPK code)
- AC-002: Department structure (wards, polyclinics, units)
- AC-003: Room and bed configuration
- AC-004: Doctor and staff directory
- AC-005: Working hours and shifts
- AC-006: Hospital branding (logo, letterhead)

**Tasks**:
1. Create hospital configuration UI
2. Build department management
3. Create room/bed configuration
4. Build staff directory
5. Implement shift configuration
6. Add branding customization
7. Create configuration validation
8. Test configuration changes
9. Documentation
10. User acceptance testing

**Dependencies**: STORY-002 (User Authentication)

**Priority**: Must Have

**Story Points**: 8

**Definition of Done Checklist**:
- [ ] Hospital profile configured
- [ ] Departments created
- [ ] Rooms/beds set up
- [ ] Staff directory populated
- [ ] Shifts configured
- [ ] Branding applied
- [ ] Validation working
- [ ] Admin feedback positive

---

#### STORY-040: Master Data Management

**Epic**: EPIC-015 - System Configuration & Master Data

**As a** System Administrator
**I want** to manage master data (ICD-10, LOINC, drugs)
**So that** clinical decisions are accurate

**Acceptance Criteria**:
- AC-001: ICD-10-CM Indonesia database import
- AC-002: LOINC database import
- AC-003: Drug formulary (generic and brand names)
- AC-004: BPJS drug codes
- AC-005: Procedure codes
- AC-006: Room classes and rates
- AC-007: Insurance companies and plans
- AC-008: Reference data management

**Tasks**:
1. Import ICD-10-CM Indonesia database
2. Import LOINC database
3. Create drug formulary management
4. Add BPJS drug code mapping
5. Import procedure codes
6. Create room class configuration
7. Build insurance master management
8. Create reference data sync
9. Data validation
10. Performance optimization
11. Documentation
12. Testing

**Dependencies**: STORY-039 (Hospital Configuration)

**Priority**: Must Have

**Story Points**: 13

**Definition of Done Checklist**:
- [ ] ICD-10 database imported
- [ ] LOINC database imported
- [ ] Drug formulary complete
- [ ] BPJS codes mapped
- [ ] Procedure codes loaded
- [ ] Insurance master configured
- [ ] Data validation passed
- [ ] Performance acceptable

---

## Story Dependencies

### Critical Path Dependencies

The following stories must be completed in order:

1. **Foundation Layer**:
   - STORY-001 (System Deployment) → All other stories
   - STORY-002 (User Authentication) → All stories requiring authentication

2. **Registration Layer**:
   - STORY-006 (New Patient Registration) → All patient-dependent stories
   - STORY-007 (Returning Patient Check-in) → STORY-011 (Patient History)

3. **Medical Records Layer**:
   - STORY-011 (Patient History) → STORY-012, STORY-013, STORY-014, STORY-015
   - STORY-012 (ICD-10) → STORY-016 (Doctor Consultation)

4. **Clinical Layer**:
   - STORY-015 (Clinical Notes) → STORY-016 (Doctor Consultation)
   - STORY-016 → STORY-017 (Prescriptions), STORY-018 (Lab/Radiology), STORY-019 (SEP)

5. **Integration Layer**:
   - STORY-022 (BPJS VClaim) → STORY-008 (Eligibility), STORY-019 (SEP), STORY-029 (Claims)
   - STORY-033 (SATUSEHAT Org) → STORY-034 (Patient Sync) → STORY-035 (Encounter Sync)

### Parallel Development Opportunities

These stories can be developed in parallel:

- **Group 1**: STORY-003 (Audit Logging), STORY-004 (Backup), STORY-005 (Monitoring)
- **Group 2**: STORY-009 (Online Booking), STORY-010 (Queue Management)
- **Group 3**: STORY-020 (Bed Management), STORY-024 (Pharmacy Inventory)
- **Group 4**: STORY-027 (Invoice Generation), STORY-030 (BPJS VClaim), STORY-033 (SATUSEHAT)
- **Group 5**: STORY-037 (User Management), STORY-038 (Training), STORY-039 (Hospital Config)

---

## Priority Matrix

### Must Have (MVP Critical)

These stories are essential for MVP deployment:

**Foundation** (5 stories):
- STORY-001: System Deployment
- STORY-002: User Authentication & Authorization
- STORY-003: Audit Logging System
- STORY-004: Automated Backup System

**Registration** (5 stories):
- STORY-006: New Patient Registration
- STORY-007: Returning Patient Check-in
- STORY-008: BPJS Eligibility Verification
- STORY-010: Queue Management System

**Medical Records** (5 stories):
- STORY-011: Patient History View
- STORY-012: ICD-10 Problem List
- STORY-013: Allergy Tracking
- STORY-014: Medication List
- STORY-015: Clinical Notes (SOAP)

**Outpatient** (4 stories):
- STORY-016: Doctor Consultation Workflow
- STORY-017: Electronic Prescriptions
- STORY-018: Lab/Radiology Ordering
- STORY-019: BPJS SEP Generation

**Inpatient** (4 stories):
- STORY-020: Bed Management
- STORY-021: Admission Workflow
- STORY-022: Daily Care Documentation
- STORY-023: Discharge Planning

**Pharmacy** (3 stories):
- STORY-024: Pharmacy Inventory Management
- STORY-025: Prescription Dispensing
- STORY-026: Drug Interaction Database Integration

**Billing** (3 stories):
- STORY-027: Invoice Generation
- STORY-028: Payment Processing
- STORY-029: BPJS Claims Preparation

**Integrations** (6 stories):
- STORY-030: BPJS VClaim API Integration
- STORY-031: BPJS Antrean API Integration
- STORY-032: BPJS Aplicare API Integration
- STORY-033: SATUSEHAT Organization Registration
- STORY-034: SATUSEHAT Patient Data Sync
- STORY-035: SATUSEHAT Encounter Data Sync
- STORY-036: SATUSEHAT Condition Sync

**Configuration** (3 stories):
- STORY-037: User Management Interface
- STORY-039: Hospital Configuration
- STORY-040: Master Data Management

**Total Must Have Stories**: 40 stories

### Should Have (Important for MVP)

These stories enhance MVP but are not blockers:

- STORY-005: System Monitoring & Alerting
- STORY-009: Online Appointment Booking
- STORY-038: Training Management System

**Total Should Have Stories**: 3 stories

### Could Have (Phase 2)

Deferred to Phase 2 implementation:

- Advanced analytics
- Mobile apps
- Telemedicine
- AI clinical decision support

---

## Story Point Summary

### By Epic

| Epic ID | Epic Name | Stories | Total Points |
|---------|-----------|---------|--------------|
| EPIC-001 | Foundation & Security | 5 | 50 |
| EPIC-002 | Patient Registration | 5 | 55 |
| EPIC-003 | Medical Records | 5 | 55 |
| EPIC-004 | Outpatient Management | 4 | 42 |
| EPIC-005 | Inpatient Management | 4 | 42 |
| EPIC-006 | Pharmacy Management | 3 | 39 |
| EPIC-009 | Billing & Finance | 3 | 39 |
| EPIC-010 | BPJS Integration | 3 | 29 |
| EPIC-011 | SATUSEHAT Integration | 4 | 26 |
| EPIC-014 | User Management | 2 | 21 |
| EPIC-015 | System Configuration | 2 | 21 |
| **Total** | **MVP Stories** | **40** | **419** |

### Story Point Distribution

- **1 point**: 0 stories (0%)
- **2 point**: 0 stories (0%)
- **3 point**: 0 stories (0%)
- **5 point**: 2 stories (5%)
- **8 point**: 22 stories (55%)
- **13 point**: 16 stories (40%)
- **21 point**: 0 stories (0%)

**Average Story Points**: 10.5 points per story

**Estimated Velocity**:
- Assuming 2-week sprint with 2 developers: ~40-50 points/sprint
- Total MVP effort: 419 points ÷ 45 points/sprint = ~9.3 sprints
- With 1 sprint = 2 weeks: ~18.6 weeks (~4.5 months)

**Note**: This is a rough estimate. Actual velocity will depend on team size, experience, and complexity encountered during implementation.

---

## Implementation Recommendations

### Sprint 0: Foundation (Weeks 1-2)
- STORY-001: System Deployment (13 points)
- STORY-002: User Authentication & Authorization (13 points)
- STORY-004: Automated Backup System (8 points)

**Total**: 34 points

### Sprint 1: Core Infrastructure (Weeks 3-4)
- STORY-003: Audit Logging System (8 points)
- STORY-037: User Management Interface (8 points)
- STORY-039: Hospital Configuration (8 points)
- STORY-040: Master Data Management (13 points)

**Total**: 37 points

### Sprint 2: Registration (Weeks 5-6)
- STORY-006: New Patient Registration (13 points)
- STORY-007: Returning Patient Check-in (8 points)
- STORY-010: Queue Management System (13 points)

**Total**: 34 points

### Sprint 3: BPJS Integration - Part 1 (Weeks 7-8)
- STORY-022: BPJS VClaim API Integration (13 points)
- STORY-008: BPJS Eligibility Verification (8 points)
- STORY-032: BPJS Aplicare API Integration (8 points)

**Total**: 29 points

### Sprint 4: Medical Records - Part 1 (Weeks 9-10)
- STORY-011: Patient History View (13 points)
- STORY-013: Allergy Tracking (8 points)
- STORY-014: Medication List (8 points)

**Total**: 29 points

### Sprint 5: Medical Records - Part 2 (Weeks 11-12)
- STORY-012: ICD-10 Problem List (13 points)
- STORY-015: Clinical Notes (SOAP) (13 points)

**Total**: 26 points

### Sprint 6: SATUSEHAT Integration - Part 1 (Weeks 13-14)
- STORY-033: SATUSEHAT Organization Registration (5 points)
- STORY-034: SATUSEHAT Patient Data Sync (8 points)
- STORY-031: BPJS Antrean API Integration (8 points)
- STORY-009: Online Appointment Booking (13 points)

**Total**: 34 points

### Sprint 7: Outpatient Management (Weeks 15-16)
- STORY-016: Doctor Consultation Workflow (13 points)
- STORY-019: BPJS SEP Generation (8 points)

**Total**: 21 points

### Sprint 8: Pharmacy & Prescriptions (Weeks 17-18)
- STORY-017: Electronic Prescriptions (13 points)
- STORY-026: Drug Interaction Database Integration (8 points)
- STORY-024: Pharmacy Inventory Management (13 points)

**Total**: 34 points

### Sprint 9: Pharmacy & Lab Orders (Weeks 19-20)
- STORY-018: Lab/Radiology Ordering (8 points)
- STORY-025: Prescription Dispensing (13 points)
- STORY-035: SATUSEHAT Encounter Data Sync (8 points)

**Total**: 29 points

### Sprint 10: Inpatient Management - Part 1 (Weeks 21-22)
- STORY-020: Bed Management (13 points)
- STORY-021: Admission Workflow (8 points)

**Total**: 21 points

### Sprint 11: Inpatient Management - Part 2 (Weeks 23-24)
- STORY-022: Daily Care Documentation (13 points)
- STORY-023: Discharge Planning (8 points)
- STORY-036: SATUSEHAT Condition Sync (5 points)

**Total**: 26 points

### Sprint 12: Billing - Part 1 (Weeks 25-26)
- STORY-027: Invoice Generation (13 points)
- STORY-028: Payment Processing (13 points)

**Total**: 26 points

### Sprint 13: Billing - Part 2 & Completion (Weeks 27-28)
- STORY-029: BPJS Claims Preparation (13 points)
- STORY-005: System Monitoring & Alerting (8 points)
- STORY-038: Training Management System (13 points)

**Total**: 34 points

**Total Duration**: 28 weeks (~7 months) for MVP completion

---

## Risk Mitigation

### High-Risk Stories

These stories have high complexity or external dependencies:

1. **STORY-022: BPJS VClaim API Integration** (13 points)
   - **Risk**: External API changes, certification delays
   - **Mitigation**: Start early, test with sandbox, maintain flexibility

2. **STORY-017: Electronic Prescriptions** (13 points)
   - **Risk**: Clinical safety, drug interaction complexity
   - **Mitigation**: Thorough testing, clinical review, pharmacists involved

3. **STORY-016: Doctor Consultation Workflow** (13 points)
   - **Risk**: Complex clinical workflows, user adoption
   - **Mitigation**: Involve doctors early, iterative feedback

4. **STORY-020: Bed Management** (13 points)
   - **Risk**: Real-time updates, concurrency issues
   - **Mitigation**: Robust testing, WebSocket implementation

5. **STORY-015: Clinical Notes (SOAP)** (13 points)
   - **Risk**: Complex versioning, audit requirements
   - **Mitigation**: Careful architecture, compliance review

### Technical Debt Prevention

- Allocate 20% of each sprint for refactoring and testing
- Conduct regular code reviews
- Maintain test coverage >80%
- Document architectural decisions
- Regular security audits

---

## Glossary

**BPJS**: Badan Penyelenggara Jaminan Sosial (Social Security Administrator)
**FHIR**: Fast Healthcare Interoperability Resources
**ICD-10**: International Classification of Diseases, 10th Revision
**LOINC**: Logical Observation Identifiers Names and Codes
**INA-CBG**: Indonesia Case Base Groups (DRG-like system)
**SEP**: Surat Eligibilitas Peserta (Participant Eligibility Letter)
**SATUSEHAT**: Indonesia's national health data exchange platform
**SOAP**: Subjective, Objective, Assessment, Plan (clinical documentation format)
**JWT**: JSON Web Token (authentication)
**RBAC**: Role-Based Access Control
**TAT**: Turnaround Time
**NIK**: Nomor Induk Kependudukan (Indonesian ID number)
**MRN**: Medical Record Number (No. RM)

---

## Appendix: Story Acceptance Sign-off

Each story requires sign-off from:

1. **Developer**: Implementation complete, tested, documented
2. **QA**: All acceptance criteria met, no critical bugs
3. **Product Owner**: User value delivered, requirements met
4. **Clinical Stakeholder** (if applicable): Clinical workflow validated
5. **Security Officer** (if applicable): Security requirements met

**Sign-off Template**:

```
Story: STORY-XXX - [Story Title]
Developer: _________________ Date: ______
QA: _________________ Date: ______
Product Owner: _________________ Date: ______
Clinical Stakeholder: _________________ Date: ______
Security Officer: _________________ Date: ______
```

---

**Document Version:** 1.0
**Last Updated:** 2026-01-13
**Status:** Draft - Ready for Sprint Planning
**Total Stories**: 40
**Total Story Points**: 419
**Estimated Duration**: 28 weeks (7 months)

