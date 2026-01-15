# Epic 025: Integration Hub - HL7/FHIR Gateway

**Epic ID**: EPIC-025
**Business Value**: Enables seamless interoperability with third-party healthcare systems, future-proofs the platform for ecosystem integration, and positions SIMRS as a connected healthcare platform
**Complexity**: High
**Estimated Duration**: 6-8 weeks

---

## Dependencies

- Epic 1 (Foundation & Security Infrastructure)
- Epic 3 (Medical Records & Clinical Documentation)
- Epic 10 (BPJS Kesehatan Integration)
- Epic 11 (SATUSEHAT FHIR R4 Integration)
- Epic 7 (Laboratory Information System) - for LIS integration
- Epic 8 (Radiology Information System) - for RIS/PACS integration

---

## Business Value

The Integration Hub provides:

1. **Interoperability**: Standards-based messaging (HL7 v2.x, FHIR R4) enables communication with diverse healthcare systems
2. **Future-Proofing**: Extensible architecture supports emerging healthcare data standards and new integrations
3. **Ecosystem Integration**: Connects with laboratory systems, radiology systems, EMR/EHR systems, payment gateways, and government systems
4. **Operational Efficiency**: Automated data exchange reduces manual data entry and improves data accuracy
5. **Regulatory Compliance**: Supports SATUSEHAT Level 2/3 requirements and future healthcare data exchange mandates
6. **Competitive Advantage**: Positions SIMRS as a modern, connected platform attractive to hospitals with existing IT investments

---

## Key User Stories

1. As a hospital IT director, I want to integrate with our existing LIS so that lab results flow automatically into SIMRS
2. As a hospital IT director, I want to integrate with our RIS/PACS so that radiology orders and reports are synchronized
3. As a system administrator, I want to transform HL7 messages to FHIR resources so that we can modernize our integrations
4. As a developer, I want to monitor all integration messages so that I can troubleshoot issues quickly
5. As a hospital administrator, I want to integrate with insurance verification systems so that eligibility is automatic
6. As a system, I want to support identification system integrations (KTP-el, BPJS) so that patient registration is streamlined
7. As a system, I want to integrate with payment gateways so that patients can pay online
8. As a developer, I want a message transformation engine so that we can map data between different formats

---

## Detailed User Stories

### STORY-025-01: HL7 v2.x Message Parsing and Routing

**As a** System Integrator
**I want to** parse and route HL7 v2.x messages
**So that** we can exchange data with legacy healthcare systems

**Acceptance Criteria**:

**Message Parsing**:
- [ ] Support HL7 v2.5, v2.5.1, and v2.6 standards
- [ ] Parse ADT^A04 (Patient Registration) messages
- [ ] Parse ADT^A08 (Patient Update) messages
- [ ] Parse ORM^O01 (Order Entry) messages
- [ ] Parse ORU^R01 (Observation Results) messages
- [ ] Parse DFT^P03 (Billing/Charge) messages
- [ ] Handle MSH segment (message header, routing info)
- [ ] Handle PID segment (patient identification)
- [ ] Handle PV1 segment (patient visit)
- [ ] Handle ORC segment (order control)
- [ ] Handle OBR segment (observation request)
- [ ] Handle OBX segment (observation/result)
- [ ] Validate message structure and required fields
- [ ] Handle custom Z-segments (extensions)
- [ ] Support multiple delimiters and encoding characters

**Message Routing**:
- [ ] Route messages based on message type (trigger event)
- [ ] Route based on sending facility/application
- [ ] Route based on receiving facility/application
- [ ] Support routing rules configuration
- [ ] Broadcast messages to multiple destinations
- [ ] Filter messages based on content
- [ ] Support message acknowledgment (ACK/NAK)
- [ ] Handle message sequence numbering
- [ ] Support message batching

**Error Handling**:
- [ ] Generate NAK (negative acknowledgment) for invalid messages
- [ ] Log parsing errors with detailed diagnostics
- [ ] Continue processing batch messages with individual failures
- [ ] Retry failed message delivery
- [ ] Alert on high error rates
- [ ] Quarantine problematic messages
- [ ] Support message reprocessing

**Message Validation**:
- [ ] Validate required segments and fields
- [ ] Validate data types and formats
- [ ] Validate value sets (where applicable)
- [ ] Check for message duplications
- [ ] Validate message sequence integrity
- [ ] Support custom validation rules

**Technical Notes**:
- Use Python-HL7 or similar HL7 parsing library
- Implement HL7/MLLP protocol for message transport
- Database tables: hl7_messages, hl7_acknowledgments, hl7_errors, hl7_routing_rules
- API endpoints: /api/hl7/send, /api/hl7/acknowledge, /api/hl7/status
- Message queue for async processing
- Support for TCP/IP and HTTP bindings

---

### STORY-025-02: FHIR R4 Server Implementation

**As a** System Architect
**I want to** implement a FHIR R4 server
**So that** we can exchange healthcare data using modern RESTful standards

**Acceptance Criteria**:

**FHIR Resources Support**:
- [ ] Patient resource (read, create, update, search)
- [ ] Encounter resource (read, create, update, search)
- [ ] Condition resource (read, create, update, search)
- [ ] Observation resource (read, create, update, search)
- [ ] ServiceRequest resource (read, create, update, search)
- [ ] MedicationRequest resource (read, create, update, search)
- [ ] MedicationAdministration resource (read, create, update, search)
- [ ] DiagnosticReport resource (read, create, update, search)
- [ ] Practitioner resource (read, create, update, search)
- [ ] Organization resource (read, create, update, search)
- [ ] Location resource (read, create, update, search)
- [ ] Immunization resource (read, create, update, search)
- [ ] DocumentReference resource (read, create, update, search)

**RESTful Operations**:
- [ ] Read operation (GET /Resource/:id)
- [ ] Create operation (POST /Resource)
- [ ] Update operation (PUT /Resource/:id)
- [ ] Delete operation (DELETE /Resource/:id)
- [ ] Search operation (GET /Resource?parameter=value)
- [ ] Search with multiple parameters
- [ ] Search with chaining
- [ ] Search with reverse chaining
- [ ] Search with modifiers (contains, exact, etc.)
- [ ] Pagination (offset, _count, _sort)
- [ ] Include and revinclude parameters
- [ ] OperationOutcome for error responses

**FHIR Search Parameters**:
- [ ] Patient: identifier, name, birthdate, gender, phone, email
- [ ] Encounter: patient, date, location, status, type
- [ ] Condition: patient, code, clinical-status, onset-date
- [ ] Observation: patient, code, date, value-concept, status
- [ ] ServiceRequest: patient, code, status, authored-on
- [ ] MedicationRequest: patient, medication, status, authored-on
- [ ] DiagnosticReport: patient, code, date, status

**Security & Authentication**:
- [ ] OAuth 2.0 / SMART on FHIR profiles
- [ ] JWT token validation
- [ ] Scope-based authorization
- [ ] Patient compartment access control
- [ ] Audit logging for all access
- [ ] CORS support for web clients

**FHIR Validation**:
- [ ] Validate resource structure against FHIR schemas
- [ ] Validate required fields
- [ ] Validate value sets and terminologies
- [ ] Validate reference integrity
- [ ] Return OperationOutcome with validation errors
- [ ] Support for FHIR Validation operations

**Technical Notes**:
- Use FHIR API for Python (fhir.resources) or similar
- Implement REST endpoints following FHIR specification
- Database tables mapped to FHIR resources
- API endpoints follow FHIR pattern: /fhir/{ResourceType}/{id}
- Support for JSON and XML formats
- Integration with Epic 11 (SATUSEHAT) for FHIR resources
- Support for FHIR bulk data export (Phase 2)
- Support for FHIR subscriptions (Phase 2)

---

### STORY-025-03: LIS (Laboratory Information System) Integration

**As a** Laboratory Manager
**I want to** integrate with external LIS systems
**So that** lab orders and results flow seamlessly between systems

**Acceptance Criteria**:

**Order Transmission**:
- [ ] Send lab orders to LIS via HL7 ORM^O01 messages
- [ ] Include patient demographics (PID segment)
- [ ] Include ordering physician and location
- [ ] Include test codes and descriptions
- [ ] Include priority (routine, urgent, STAT)
- [ ] Include clinical indications
- [ ] Track order status in SIMRS
- [ ] Update order status based on LIS acknowledgments

**Result Reception**:
- [ ] Receive lab results via HL7 ORU^R01 messages
- [ ] Parse result values (OBX segments)
- [ ] Parse units of measure
- [ ] Parse reference ranges
- [ ] Parse abnormal flags
- [ ] Parse critical value flags
- [ ] Store results in SIMRS database
- [ ] Update lab order status to completed
- [ ] Trigger critical value alerts (Epic 23)

**Sample Tracking**:
- [ ] Receive sample status updates from LIS
- [ ] Track sample: received, in progress, completed
- [ ] Track sample location
- [ ] Handle sample rejection notifications
- [ ] Update sample status in SIMRS

**Quality Control Data**:
- [ ] Receive QC results from LIS
- [ ] Parse QC lot information
- [ ] Parse QC value and range
- [ ] Store QC results for quality reporting
- [ ] Support QC review and verification

**Order Cancellation/Modification**:
- [ ] Send order cancellations via HL7 ORM^O01 (ORC status)
- [ ] Send order modifications
- [ ] Handle cancellation confirmations from LIS
- [ ] Update order status in SIMRS

**Error Handling**:
- [ ] Handle rejected orders from LIS
- [ ] Log transmission errors
- [ ] Retry failed message transmission
- [ ] Alert on repeated failures
- [ ] Support manual message resend

**Mapping & Configuration**:
- [ ] Map SIMRS test codes to LIS test codes
- [ ] Map SIMRS locations to LIS locations
- [ ] Map SIMRS physicians to LIS physicians
- [ ] Configure connection settings (host, port)
- [ ] Configure message formatting preferences
- [ ] Test connectivity with LIS

**Technical Notes**:
- Integration with Epic 7 (Laboratory Information System)
- HL7/MLLP protocol for LIS communication
- Database tables: lis_orders, lis_results, lis_mapping, lis_errors
- Message queue for async processing
- Retry logic with exponential backoff
- Monitoring dashboard for LIS integration health

---

### STORY-025-04: RIS (Radiology Information System) Integration

**As a** Radiology Manager
**I want to** integrate with RIS systems
**So that** radiology orders and reports are synchronized

**Acceptance Criteria**:

**Order Transmission**:
- [ ] Send radiology orders to RIS via HL7 ORM^O01 messages
- [ ] Include patient demographics and visit information
- [ ] Include exam type and procedure codes
- [ ] Include clinical history and indications
- [ ] Include priority and scheduling preferences
- [ ] Include ordering physician
- [ ] Track order status in SIMRS
- [ ] Update order status based on RIS acknowledgments

**Modality Worklist Sync**:
- [ ] Receive modality worklist updates from RIS
- [ ] Sync scheduled exams with imaging equipment
- [ ] Support DICOM MWL (Modality Worklist) integration
- [ ] Update exam status from RIS
- [ ] Handle exam cancellations and rescheduling

**Report Reception**:
- [ ] Receive radiology reports via HL7 ORU^R01 messages
- [ ] Parse report findings and impressions
- [ ] Parse report status (preliminary, final)
- [ ] Parse report attachments (images, PDFs)
- [ ] Store reports in SIMRS database
- [ ] Link reports to imaging studies in PACS
- [ ] Notify ordering physician when report available

**Image References**:
- [ ] Receive PACS image references from RIS
- [ ] Store SOP Instance UIDs for study access
- [ ] Generate PACS viewer links
- [ ] Support DICOM web viewer integration
- [ ] Handle image availability confirmations

**Exam Status Tracking**:
- [ ] Receive exam status updates from RIS
- [ ] Track: scheduled, in progress, completed, cancelled
- [ ] Track exam protocols and contrast usage
- [ ] Track radiation dose information
- [ ] Update exam status in SIMRS

**Order Cancellation/Modification**:
- [ ] Send order cancellations to RIS
- [ ] Send order modifications
- [ ] Handle cancellation confirmations
- [ ] Update order status in SIMRS

**Critical Findings**:
- [ ] Receive critical finding alerts from RIS
- [ ] Alert ordering physician (Epic 23)
- [ ] Flag critical findings prominently
- [ ] Track critical finding acknowledgment

**Error Handling**:
- [ ] Handle rejected orders from RIS
- [ ] Log transmission errors
- [ ] Retry failed message transmission
- [ ] Alert on repeated failures
- [ ] Support manual message resend

**Technical Notes**:
- Integration with Epic 8 (Radiology Information System)
- HL7/MLLP protocol for RIS communication
- DICOM MWL integration for modality worklist
- Database tables: ris_orders, ris_reports, ris_mapping, ris_errors
- Message queue for async processing
- Integration with PACS for image access

---

### STORY-025-05: PACS (Picture Archiving and Communication System) Integration

**As a** Radiologist
**I want to** integrate with PACS systems
**So that** medical images are accessible from SIMRS

**Acceptance Criteria**:

**DICOM Query/Retrieve**:
- [ ] Query PACS for patient studies (C-FIND)
- [ ] Query by patient ID, name, study date, study type
- [ ] Retrieve study metadata (series, instances)
- [ ] Display study list in SIMRS
- [ ] Support DICOM QR (Query/Retrieve) service class

**Image Viewing Integration**:
- [ ] Embed DICOM web viewer in SIMRS
- [ ] Support common viewers (Weasis, Oviyam, Orthanc)
- [ ] Single sign-on to PACS viewer
- [ ] Pass patient context to viewer
- [ ] Support image manipulation (zoom, pan, window/level)
- [ ] Support measurement tools
- [ ] Support multi-planar reconstruction (MPR)

**Study Links**:
- [ ] Generate direct links to PACS studies
- [ ] Embed PACS viewer in reports
- [ ] Share study links with patients (via portal)
- [ ] Secure link access with authentication
- [ ] Time-limited access tokens

**Image Import**:
- [ ] Receive DICOM images from modalities (optional)
- [ ] Store images temporarily or forward to PACS
- [ ] Support DICOM C-STORE for image receiving
- [ ] Validate DICOM conformance
- [ ] Forward to external PACS if needed

**Metadata Synchronization**:
- [ ] Sync study metadata from PACS to SIMRS
- [ ] Sync series and instance counts
- [ ] Sync study descriptions and comments
- [ ] Update report links in SIMRS

**Access Control**:
- [ ] Respect PACS access control rules
- [ ] Filter studies based on user permissions
- [ ] Log all image access attempts
- [ ] Support patient privacy (de-identification)

**Performance**:
- [ ] Study list load time <3 seconds
- [ ] Image viewer load time <5 seconds
- [ ] Support lazy loading for large studies
- [ ] Cache study metadata

**Technical Notes**:
- DICOM protocol support (DICOMweb, DICOM QR)
- Integration with Epic 8 (Radiology)
- Database tables: pacs_studies, pacs_series, pacs_mappings
- DICOMweb or DICOM QR client library
- Integration with existing hospital PACS
- Support for DICOMweb WADO-RS for image retrieval
- Support for STOW-RS for image upload (optional)

---

### STORY-025-06: EMR/EHR System Integration (Bidirectional)

**As a** Hospital IT Director
**I want to** integrate with external EMR/EHR systems
**So that** patient data can be exchanged with referring facilities

**Acceptance Criteria**:

**Patient Data Exchange**:
- [ ] Export patient demographics via FHIR Patient resources
- [ ] Import patient demographics from external EMR
- [ ] Merge patient records on match
- [ ] Handle patient identifier conflicts
- [ ] Support patient data reconciliation

**Clinical Data Exchange**:
- [ ] Export encounter data via FHIR Encounter resources
- [ ] Export conditions/diagnoses via FHIR Condition resources
- [ ] Import conditions from external EMR
- [ ] Export medications via FHIR MedicationRequest resources
- [ ] Import medications from external EMR
- [ ] Export allergies via FHIR AllergyIntolerance resources
- [ ] Import allergies from external EMR

**Lab Results Exchange**:
- [ ] Export lab results via FHIR Observation resources
- [ ] Import lab results from external EMR
- [ ] Map LOINC codes between systems
- [ ] Handle result formatting differences
- [ ] Display external results in SIMRS

**Radiology Reports Exchange**:
- [ ] Export radiology reports via FHIR DiagnosticReport resources
- [ ] Import radiology reports from external EMR
- [ ] Link to external PACS studies
- [ ] Display external reports in SIMRS

**Document Exchange**:
- [ ] Export clinical documents via FHIR DocumentReference resources
- [ ] Import documents from external EMR
- [ ] Support PDF, CDA, and other formats
- [ ] Handle document size limits
- [ ] Secure document access

**Referral Management**:
- [ ] Send referrals to external facilities
- [ ] Receive referrals from external facilities
- [ ] Track referral status
- [ ] Include relevant clinical data with referrals

**Continuity of Care Documents (CCD)**:
- [ ] Generate CCD documents for export
- [ ] Import CCD documents from external EMR
- [ ] Parse CCD content into SIMRS
- [ ] Validate CCD structure
- [ ] Support CDA R2 standards

**Data Transformation**:
- [ ] Map SIMRS data model to FHIR resources
- [ ] Map external FHIR to SIMRS data model
- [ ] Handle terminology mapping (ICD-10, LOINC, SNOMED)
- [ ] Handle unit conversions
- [ ] Handle data type conversions

**Security & Privacy**:
- [ ] Authenticate with external EMR systems
- [ ] OAuth 2.0 / SMART on FHIR authentication
- [ ] Patient consent verification
- [ ] Data access logging
- [ ] Support patient privacy (de-identification)

**Technical Notes**:
- FHIR R4 REST API for data exchange
- Integration with Epic 3 (Medical Records)
- Integration with Epic 11 (SATUSEHAT)
- Database tables: emr_integrations, emr_data_exchange, emr_mappings
- Support for HL7 FHIR and CDA standards
- Support for IHE profiles (XDS, XDR)
- Bulk data export/import capability

---

### STORY-025-07: Insurance Verification System Integration

**As a** Registration Clerk
**I want to** automatically verify insurance eligibility
**So that** we avoid claim rejections and inform patients of coverage

**Acceptance Criteria**:

**BPJS Integration** (existing - Epic 10):
- [ ] Integrate with existing BPJS VClaim API
- [ ] Verify BPJS eligibility through Integration Hub
- [ ] Standardize eligibility response format
- [ ] Cache eligibility results

**Private Insurance Verification**:
- [ ] Integrate with major private insurance APIs
- [ ] Verify patient eligibility in real-time
- [ ] Check coverage status (active, suspended, terminated)
- [ ] Check coverage limits (inpatient, outpatient, annual)
- [ ] Check pre-authorization requirements
- [ ] Check co-pay and deductible information
- [ ] Display coverage details to registration staff

**Pre-Authorization Requests**:
- [ ] Submit pre-auth requests to insurance
- [ ] Include diagnosis and procedure codes
- [ ] Include estimated costs
- [ ] Track pre-auth request status
- [ ] Receive pre-auth approval/denial
- [ ] Store pre-auth reference numbers
- [ ] Alert on pre-auth expirations

**Claim Status Checking**:
- [ ] Check claim status with insurance
- [ ] Track claim submission date
- [ ] Track claim processing status
- [ ] Receive claim approval/denial notifications
- [ ] Track payment status
- [ ] Update SIMRS billing records

**Coverage Calculation**:
- [ ] Calculate patient responsibility based on coverage
- [ ] Calculate insurance responsibility
- [ ] Display cost estimates to patients
- [ ] Handle out-of-network calculations
- [ ] Handle exclusion logic

**Insurance Master Data**:
- [ ] Maintain insurance company directory
- [ ] Store insurance API endpoints
- [ ] Store authentication credentials
- [ ] Update coverage rules
- [ ] Maintain formulary lists (covered drugs/tests)

**Error Handling**:
- [ ] Handle API failures gracefully
- [ ] Log all verification attempts
- [ ] Retry failed verifications
- [ ] Alert on repeated failures
- [ ] Support manual verification entry

**Technical Notes**:
- Integration with Epic 10 (BPJS)
- Integration with Epic 9 (Billing)
- REST API calls to insurance systems
- Database tables: insurance_verifications, pre_authorizations, insurance_master
- Eligibility verification API endpoints
- Pre-auth workflow engine

---

### STORY-025-08: Payment Gateway Integration

**As a** Patient
**I want to** pay bills online through payment gateways
**So that** I can pay conveniently without visiting the hospital

**Acceptance Criteria**:

**Payment Gateway Support**:
- [ ] Integrate with major Indonesian payment gateways (Midtrans, Xendit, DOKU)
- [ ] Support credit/debit card payments
- [ ] Support virtual account payments
- [ ] Support e-wallet payments (GoPay, OVO, Dana, LinkAja)
- [ ] Support bank transfer
- [ ] Support QRIS payments
- [ ] Support convenience store payments (Alfamart, Indomaret)
- [ ] Support paylater options

**Payment Processing**:
- [ ] Generate payment requests from invoices
- [ ] Create unique payment references
- [ ] Redirect to payment gateway
- [ ] Handle payment success callbacks
- [ ] Handle payment failure
- [ ] Handle payment pending/awaiting
- [ ] Update invoice status after payment
- [ ] Generate payment receipts

**Payment Status Tracking**:
- [ ] Track payment status in real-time
- [ ] Check payment status with gateway
- [ ] Handle payment expiration
- [ ] Retry status checks for pending payments
- [ ] Auto-cancel expired payments

**Reconciliation**:
- [ ] Reconcile payments with bank statements
- [ ] Match payments to invoices
- [ ] Handle payment discrepancies
- [ ] Generate reconciliation reports
- [ ] Flag unmatched payments

**Refund Processing**:
- [ ] Process refunds through gateway
- [ ] Validate refund eligibility
- [ ] Handle partial refunds
- [ ] Handle full refunds
- [ ] Track refund status
- [ ] Update invoice after refund

**Payment Scheduling**:
- [ ] Support scheduled payments
- [ ] Support payment installments
- [ ] Send payment reminders
- [ ] Auto-process scheduled payments
- [ ] Notify payment success/failure

**Security & Compliance**:
- [ ] PCI DSS compliance for card payments
- [ ] Tokenization for saved payment methods
- [ ] 3D Secure authentication
- [ ] Fraud detection
- [ ] Secure payment data handling
- [ ] Audit logging for all payments

**Technical Notes**:
- Integration with Epic 9 (Billing)
- Integration with Epic 23 (Notifications)
- REST API integration with payment gateways
- Database tables: payment_transactions, payment_gateway_logs, payment_reconciliations
- Webhook handling for payment callbacks
- Payment link generation (secure tokens)

---

### STORY-025-09: Identification System Integration (KTP-el, BPJS)

**As a** Registration Clerk
**I want to** verify patient identity through government systems
**So that** patient data is accurate and fraud is prevented

**Acceptance Criteria**:

**KTP-el (Electronic ID) Integration**:
- [ ] Verify NIK (National ID) with Dukcapil database
- [ ] Validate NIK format (16 digits)
- [ ] Retrieve patient demographic data from KTP-el
- [ ] Auto-populate registration form with KTP-el data
- [ ] Verify NIK validity (active, not deceased)
- [ ] Retrieve family关系 data (KK)
- [ ] Validate address information
- [ ] Handle API rate limits

**BPJS Card Validation**:
- [ ] Validate BPJS card number format
- [ ] Verify BPJS membership status
- [ ] Retrieve BPJS membership tier (Kelas)
- [ ] Check BPJS membership expiration
- [ ] Verify BPJS card holder name matches NIK
- [ ] Retrieve BPJS family dependency data
- [ ] Check BPJS contribution payment status

**Face Recognition (Optional)**:
- [ ] Integrate with face recognition systems
- [ ] Match patient photo with ID photo
- [ ] Verify identity for critical transactions
- [ ] Support liveness detection
- [ ] Handle match/no-match results

**Biometric Integration (Optional)**:
- [ ] Support fingerprint verification
- [ ] Support iris scan verification
- [ ] Match with government biometric databases
- [ ] Handle biometric device integration

**Data Auto-Population**:
- [ ] Auto-fill patient registration from KTP-el
- [ ] Auto-fill BPJS information from BPJS database
- [ ] Reduce manual data entry
- [ ] Improve data accuracy
- [ ] Allow manual override/correction

**Error Handling**:
- [ ] Handle Dukcapil API failures gracefully
- [ ] Handle BPJS API failures gracefully
- [ ] Cache verification results (with expiration)
- [ ] Retry failed verifications
- [ ] Log all verification attempts
- [ ] Support manual verification fallback

**Privacy & Compliance**:
- [ ] Obtain patient consent for ID verification
- [ ] Log data access from government systems
- [ ] Secure handling of government data
- [ ] Comply with data protection regulations
- [ ] Implement data retention policies

**Technical Notes**:
- Integration with Epic 2 (Patient Registration)
- REST API integration with Dukcapil KTP-el
- Integration with Epic 10 (BPJS)
- Database tables: id_verifications, ktp_data_cache, bpjs_card_validations
- Secure API credentials management
- Rate limiting and quota management

---

### STORY-025-10: Message Transformation and Mapping Engine

**As a** System Integrator
**I want to** transform messages between different formats
**So that** systems with different standards can communicate

**Acceptance Criteria**:

**HL7 to FHIR Transformation**:
- [ ] Transform HL7 v2.x ADT messages to FHIR Patient resources
- [ ] Transform HL7 v2.x ORM messages to FHIR ServiceRequest resources
- [ ] Transform HL7 v2.x ORU messages to FHIR Observation and DiagnosticReport resources
- [ ] Transform HL7 v2.x DFT messages to FHIR Account/Claim resources
- [ ] Map HL7 segments to FHIR resource elements
- [ ] Map HL7 data types to FHIR data types
- [ ] Handle HL7 Z-segments (extensions to FHIR extensions)

**FHIR to HL7 Transformation**:
- [ ] Transform FHIR Patient resources to HL7 ADT messages
- [ ] Transform FHIR ServiceRequest resources to HL7 ORM messages
- [ ] Transform FHIR Observation resources to HL7 ORU messages
- [ ] Map FHIR resource elements to HL7 segments
- [ ] Generate proper HL7 message structure

**Custom Field Mapping**:
- [ ] Define source to target field mappings
- [ ] Support complex transformations (concatenation, conditional)
- [ ] Support lookup tables for value mapping
- [ ] Support default values
- [ ] Support data type conversions
- [ ] Support unit conversions
- [ ] Support date/time format conversions

**Terminology Mapping**:
- [ ] Map ICD-9 to ICD-10 codes
- [ ] Map local codes to standard terminologies (LOINC, SNOMED)
- [ ] Map drug codes to standard formulary
- [ ] Support bidirectional terminology mapping
- [ ] Maintain terminology mapping tables
- [ ] Support custom code systems

**Validation Rules**:
- [ ] Define validation rules for transformations
- [ ] Validate required fields
- [ ] Validate data formats
- [ ] Validate value ranges
- [ ] Validate reference integrity
- [ ] Report transformation errors

**Transformation Testing**:
- [ ] Test transformations with sample messages
- [ ] Compare input and output messages
- [ ] Validate transformed messages against schemas
- [ ] Support test data sets
- [ ] Report transformation statistics

**Configuration Management**:
- [ ] Create and edit transformation mappings
- [ ] Version control for transformation rules
- [ ] Activate/deactivate transformations
- [ ] Import/export transformation configurations
- [ ] Test transformations before deployment

**Performance**:
- [ ] Transform messages in <1 second
- [ ] Support batch transformation
- [ ] Cache transformation rules
- [ ] Optimize complex transformations
- [ ] Monitor transformation performance

**Technical Notes**:
- Python-based transformation engine
- Use of mapping libraries (JSONPath, XPath)
- Database tables: transformation_rules, field_mappings, terminology_mappings, transformation_logs
- API endpoints: /api/transform/hl7-to-fhir, /api/transform/fhir-to-hl7
- Transformation testing endpoints

---

### STORY-025-11: Integration Monitoring and Error Handling

**As a** System Administrator
**I want to** monitor all integrations and handle errors
**So that** integration issues are detected and resolved quickly

**Acceptance Criteria**:

**Real-Time Monitoring**:
- [ ] Display status of all integration endpoints
- [ ] Show connection health (connected, disconnected, error)
- [ ] Show message throughput (messages per minute/hour)
- [ ] Show error rates
- [ ] Show average response times
- [ ] Show queue depths
- [ ] Auto-refresh dashboard

**Message Logging**:
- [ ] Log all incoming messages (HL7, FHIR)
- [ ] Log all outgoing messages
- [ ] Log message timestamps
- [ ] Log message sources and destinations
- [ ] Log message processing status
- [ ] Store full message content for debugging
- [ ] Searchable message log

**Error Tracking**:
- [ ] Capture all message errors
- [ ] Categorize errors (parsing, validation, transformation, transmission)
- [ ] Error severity levels (warning, error, critical)
- [ ] Error counts and trends
- [ ] Error alerting
- [ ] Error escalation rules

**Alerting**:
- [ ] Alert on endpoint disconnection
- [ ] Alert on high error rates (>5%)
- [ ] Alert on message queue backlog
- [ ] Alert on slow response times (>10 seconds)
- [ ] Alert on critical transformation failures
- [ ] Alert via email, SMS, in-app
- [ ] Escalation for unacknowledged alerts

**Error Recovery**:
- [ ] Retry failed message transmission
- [ ] Manual message resend capability
- [ ] Message reprocessing from error queue
- [ ] Message correction and resubmit
- [ ] Bulk message reprocessing
- [ ] Track recovery actions

**Performance Metrics**:
- [ ] Message volume by integration
- [ ] Message volume by type
- [ ] Average processing time
- [ ] Peak throughput
- [ ] Uptime percentage
- [ ] Response time percentiles (p50, p95, p99)

**Reporting**:
- [ ] Daily integration summary reports
- [ ] Error rate reports
- [ ] Performance trend reports
- [ ] Volume reports
- [ ] Export reports (PDF, CSV)
- [ ] Schedule automated reports

**Diagnostic Tools**:
- [ ] View individual message details
- [ ] Trace message flow through system
- [ ] View transformation errors with context
- [ ] Test endpoint connectivity
- [ ] Send test messages
- [ ] View endpoint logs

**Configuration**:
- [ ] Configure alert thresholds
- [ ] Configure monitoring intervals
- [ ] Configure retention policies
- [ ] Configure notification preferences
- [ ] Configure endpoint health checks

**Technical Notes**:
- Integration monitoring dashboard
- Database tables: integration_endpoints, integration_logs, integration_errors, integration_metrics
- Background jobs for health checks
- Integration with Epic 23 (Notifications) for alerts
- Time-series database for metrics (optional)
- Log aggregation system (optional)

---

## Technical Architecture

### System Components

1. **Integration Gateway**
   - Central point for all external integrations
   - Protocol adapters (HL7, FHIR, HTTP, DICOM)
   - Message routing and transformation
   - Error handling and retry logic

2. **HL7 Processor**
   - HL7 v2.x message parsing and generation
   - MLLP protocol support
   - Message validation
   - ACK/NAK handling

3. **FHIR Server**
   - RESTful FHIR R4 API
   - Resource storage and retrieval
   - FHIR operations support
   - SMART on FHIR authentication

4. **Message Transformation Engine**
   - HL7 to FHIR transformation
   - FHIR to HL7 transformation
   - Custom field mapping
   - Terminology mapping

5. **Integration Connectors**
   - LIS connector (HL7)
   - RIS connector (HL7)
   - PACS connector (DICOM)
   - EMR/EHR connector (FHIR)
   - Payment gateway connector (REST)
   - Insurance verification connector (REST)
   - ID verification connector (REST)

6. **Monitoring Service**
   - Real-time monitoring dashboard
   - Message logging and tracking
   - Error detection and alerting
   - Performance metrics collection

### Database Schema

```sql
-- HL7 Messages
CREATE TABLE hl7_messages (
    id UUID PRIMARY KEY,
    message_type VARCHAR(10) NOT NULL, -- 'ADT', 'ORM', 'ORU', 'DFT'
    trigger_event VARCHAR(10) NOT NULL, -- 'A04', 'O01', 'R01', 'P03'
    message_control_id VARCHAR(50),
    processing_id VARCHAR(10),
    version_id VARCHAR(10),
    sending_application VARCHAR(100),
    sending_facility VARCHAR(100),
    receiving_application VARCHAR(100),
    receiving_facility VARCHAR(100),
    message_content TEXT NOT NULL,
    status VARCHAR(20), -- 'received', 'processed', 'error'
    processed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- HL7 Acknowledgments
CREATE TABLE hl7_acknowledgments (
    id UUID PRIMARY KEY,
    hl7_message_id UUID REFERENCES hl7_messages(id),
    ack_code VARCHAR(5), -- 'AA', 'AE', 'AR'
    ack_message TEXT,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- FHIR Resources
CREATE TABLE fhir_resources (
    id UUID PRIMARY KEY,
    resource_type VARCHAR(50) NOT NULL, -- 'Patient', 'Encounter', etc.
    resource_id VARCHAR(50) NOT NULL, -- FHIR logical ID
    resource_version INTEGER,
    resource_content JSONB NOT NULL,
    source_system VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(resource_type, resource_id)
);

-- Integration Endpoints
CREATE TABLE integration_endpoints (
    id UUID PRIMARY KEY,
    endpoint_name VARCHAR(100) NOT NULL,
    endpoint_type VARCHAR(50) NOT NULL, -- 'HL7', 'FHIR', 'DICOM', 'REST'
    endpoint_url VARCHAR(500),
    endpoint_config JSONB, -- Connection settings, credentials
    status VARCHAR(20), -- 'active', 'inactive', 'error'
    last_health_check TIMESTAMP,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Integration Logs
CREATE TABLE integration_logs (
    id UUID PRIMARY KEY,
    endpoint_id UUID REFERENCES integration_endpoints(id),
    direction VARCHAR(10), -- 'inbound', 'outbound'
    message_type VARCHAR(50),
    message_content TEXT,
    message_id VARCHAR(100),
    correlation_id VARCHAR(100),
    status VARCHAR(20), -- 'success', 'error', 'pending'
    status_code INTEGER,
    response_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transformation Rules
CREATE TABLE transformation_rules (
    id UUID PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    source_format VARCHAR(20) NOT NULL, -- 'HL7', 'FHIR'
    target_format VARCHAR(20) NOT NULL, -- 'HL7', 'FHIR'
    message_type VARCHAR(50),
    transformation_config JSONB NOT NULL, -- Mapping definitions
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Field Mappings
CREATE TABLE field_mappings (
    id UUID PRIMARY KEY,
    transformation_rule_id UUID REFERENCES transformation_rules(id),
    source_path VARCHAR(200) NOT NULL, -- e.g., 'PID.5.1'
    target_path VARCHAR(200) NOT NULL, -- e.g., 'Patient.name[0].family'
    transformation_type VARCHAR(50), -- 'direct', 'lookup', 'custom'
    transformation_config JSONB,
    default_value TEXT,
    is_required BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Termination Mappings
CREATE TABLE terminology_mappings (
    id UUID PRIMARY KEY,
    source_code_system VARCHAR(50) NOT NULL,
    target_code_system VARCHAR(50) NOT NULL,
    source_code VARCHAR(50) NOT NULL,
    target_code VARCHAR(50) NOT NULL,
    source_display TEXT,
    target_display TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Integration Errors
CREATE TABLE integration_errors (
    id UUID PRIMARY KEY,
    endpoint_id UUID REFERENCES integration_endpoints(id),
    log_id UUID REFERENCES integration_logs(id),
    error_type VARCHAR(50), -- 'parsing', 'validation', 'transformation', 'transmission'
    error_code VARCHAR(50),
    error_message TEXT NOT NULL,
    error_details JSONB,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Message Queue (for retry)
CREATE TABLE message_queue (
    id UUID PRIMARY KEY,
    endpoint_id UUID REFERENCES integration_endpoints(id),
    message_type VARCHAR(50),
    message_content TEXT NOT NULL,
    priority INTEGER DEFAULT 5,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    next_retry_at TIMESTAMP,
    status VARCHAR(20), -- 'pending', 'processing', 'failed', 'success'
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

```
# HL7 Endpoints
POST   /api/integration/hl7/send              - Send HL7 message
GET    /api/integration/hl7/messages          - List HL7 messages
GET    /api/integration/hl7/messages/:id      - Get HL7 message details

# FHIR Endpoints
GET    /fhir/{ResourceType}                  - Read FHIR resources
GET    /fhir/{ResourceType}/:id              - Read specific resource
POST   /fhir/{ResourceType}                  - Create FHIR resource
PUT    /fhir/{ResourceType}/:id              - Update FHIR resource
DELETE /fhir/{ResourceType}/:id              - Delete FHIR resource

# Transformation Endpoints
POST   /api/integration/transform/hl7-to-fhir - Transform HL7 to FHIR
POST   /api/integration/transform/fhir-to-hl7 - Transform FHIR to HL7
GET    /api/integration/transform/rules      - List transformation rules
POST   /api/integration/transform/rules      - Create transformation rule

# Monitoring Endpoints
GET    /api/integration/monitoring/status    - Get all endpoint statuses
GET    /api/integration/monitoring/logs      - Get integration logs
GET    /api/integration/monitoring/errors    - Get integration errors
GET    /api/integration/monitoring/metrics   - Get performance metrics
POST   /api/integration/monitoring/test      - Test endpoint connectivity

# Endpoint Management
GET    /api/integration/endpoints            - List endpoints
POST   /api/integration/endpoints            - Create endpoint
PUT    /api/integration/endpoints/:id        - Update endpoint
DELETE /api/integration/endpoints/:id        - Delete endpoint
POST   /api/integration/endpoints/:id/test   - Test endpoint
```

### Integration Points

1. **Epic 10 (BPJS Integration)**
   - Integration Hub standardizes BPJS API calls
   - Provides unified interface for BPJS operations
   - Handles BPJS-specific message formats

2. **Epic 11 (SATUSEHAT Integration)**
   - FHIR R4 server implementation
   - Supports SATUSEHAT Level 2/3 requirements
   - Terminology mapping (ICD-10, LOINC)

3. **Epic 7 (Laboratory Information System)**
   - LIS connector for HL7 message exchange
   - Order transmission and result reception
   - Sample tracking

4. **Epic 8 (Radiology Information System)**
   - RIS connector for HL7 message exchange
   - Report reception and order transmission
   - PACS integration for image access

5. **Epic 9 (Billing, Finance & Claims)**
   - Payment gateway integration
   - Insurance verification integration
   - Claims data exchange

6. **Epic 2 (Patient Registration)**
   - ID verification integration (KTP-el, BPJS)
   - Insurance eligibility verification
   - Data auto-population from external systems

### Security & Compliance

1. **Authentication & Authorization**
   - OAuth 2.0 for FHIR server (SMART on FHIR)
   - API key authentication for external systems
   - Mutual TLS for sensitive integrations
   - Role-based access control for management APIs

2. **Data Privacy**
   - No PHI in log files (use references only)
   - Data encryption in transit (TLS 1.3)
   - Pseudonymization for testing/development
   - Audit logging for all data access

3. **Message Security**
   - HL7 message validation
   - FHIR resource validation
   - Input sanitization
   - Protection against injection attacks

4. **Compliance**
   - Support Indonesian healthcare data regulations
   - Audit trails for all integrations
   - Data retention policies
   - Patient consent management

### Monitoring & Maintenance

1. **Health Monitoring**
   - Endpoint health checks (every 30 seconds)
   - Connection status monitoring
   - Message queue depth monitoring
   - Error rate monitoring

2. **Performance Monitoring**
   - Message throughput metrics
   - Response time tracking
   - Transformation performance
   - System resource usage

3. **Alerting**
   - Endpoint disconnection alerts
   - High error rate alerts
   - Performance degradation alerts
   - Security alerts

4. **Maintenance**
   - Regular endpoint testing
   - Transformation rule updates
   - Terminology mapping updates
   - Security patching

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Integration Gateway architecture setup
- Database schema implementation
- HL7 message parser implementation
- FHIR R4 server basic implementation
- Core FHIR resources (Patient, Encounter, Condition)
- Monitoring framework setup

### Phase 2: HL7 & FHIR Core (Week 2-4)
- Complete HL7 v2.x parsing (ADT, ORM, ORU, DFT)
- Complete FHIR R4 server (all required resources)
- HL7 to FHIR transformation engine
- FHIR to HL7 transformation engine
- Field mapping configuration
- Terminology mapping setup

### Phase 3: Healthcare System Integrations (Week 4-6)
- LIS integration (HL7)
- RIS integration (HL7)
- PACS integration (DICOMweb)
- Integration testing with vendor systems
- Error handling and recovery

### Phase 4: External System Integrations (Week 6-7)
- Insurance verification integrations
- Payment gateway integrations
- ID verification integrations (KTP-el, BPJS)
- EMR/EHR integration capabilities
- CCD/CDA document exchange

### Phase 5: Monitoring & Polish (Week 7-8)
- Integration monitoring dashboard
- Error tracking and alerting
- Performance optimization
- Security hardening
- Documentation and training
- Testing and validation

---

## Success Criteria

- [ ] HL7 v2.x message parsing operational (ADT, ORM, ORU, DFT)
- [ ] FHIR R4 server functional for all required resources
- [ ] Message transformation engine operational (HL7 ↔ FHIR)
- [ ] LIS integration implemented and tested
- [ ] RIS integration implemented and tested
- [ ] PACS integration implemented and tested
- [ ] EMR/EHR integration capability demonstrated
- [ ] Insurance verification integrated with at least 2 providers
- [ ] Payment gateway integrated with at least 2 providers
- [ ] ID verification (KTP-el, BPJS) operational
- [ ] Integration monitoring dashboard functional
- [ ] Error rate <2% for all integrations
- [ ] Message transformation time <1 second
- [ ] FHIR API response time <500ms
- [ ] HL7 message processing time <500ms
- [ ] System uptime >99.5%
- [ ] Documentation complete
- [ ] Staff training completed

---

## Risk Assessment

### High Risks
1. **Integration Complexity**: Multiple standards and protocols
   - Mitigation: Phased implementation, vendor testing, comprehensive documentation

2. **Third-Party Dependencies**: External system availability
   - Mitigation: Robust error handling, retry logic, fallback mechanisms

3. **Data Mapping Challenges**: Different data models and terminologies
   - Mitigation: Flexible transformation engine, configurable mappings, testing

### Medium Risks
1. **Performance**: High message volume may impact performance
   - Mitigation: Async processing, message queuing, load testing

2. **Security**: PHI exposure through integrations
   - Mitigation: Encryption, authentication, audit logging, security testing

3. **Maintenance**: Ongoing maintenance of multiple integrations
   - Mitigation: Monitoring, alerting, documentation, training

### Low Risks
1. **Vendor Cooperation**: External vendors may not support testing
   - Mitigation: Use sandbox environments, simulation, contract requirements

2. **Standards Evolution**: HL7/FHIR standards may change
   - Mitigation: Version support, backward compatibility, regular updates

---

## Future Enhancements

### Phase 2+ Features
- FHIR Subscriptions for real-time data push
- FHIR Bulk Data Export for analytics
- Additional DICOM services (PRINT, STORAGE COMMIT)
- IHE profile support (XDS, XDR, PIX/PDQ)
- Machine learning for message anomaly detection
- Advanced analytics for integration optimization
- Blockchain for health data exchange (exploratory)
- IoT device integration for medical devices

---

**Document Version:** 1.0
**Created:** 2026-01-15
**Status:** Draft - Ready for Review
**Dependencies:** Epic 1, Epic 3, Epic 10, Epic 11, Epic 7, Epic 8
**Prerequisites:** Foundation infrastructure, BPJS integration, SATUSEHAT integration, Laboratory and Radiology systems
