### Epic 22: Patient Portal

**Epic ID**: EPIC-022
**Business Value**: Patient engagement, satisfaction, reduced workload, improved patient outcomes, enhanced patient experience, better care coordination
**Complexity**: High
**Estimated Duration**: 5-6 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration & Queue Management)
- Epic 3 (Medical Records & Clinical Documentation)
- Epic 4 (Outpatient Management)
- Epic 5 (Inpatient Management)
- Epic 6 (Pharmacy Management)
- Epic 7 (Laboratory Information System)
- Epic 8 (Radiology Information System)
- Epic 9 (Billing, Finance & Claims)

#### Key User Stories

1. As a new patient, I want to register and create a secure account so that I can access the portal from home
2. As a patient, I want to view my complete health record (demographics, medical history, allergies, medications) so that I can stay informed about my health
3. As a patient, I want to schedule and manage appointments online so that I don't have to call the hospital
4. As a patient, I want to request prescription refills electronically so that I can avoid trips to the pharmacy
5. As a patient, I want to view my laboratory and radiology results with explanations so that I can understand my health status
6. As a patient, I want to send secure messages to my healthcare providers so that I can ask questions without visiting
7. As a patient, I want to view and pay my bills online so that I can manage my healthcare expenses conveniently
8. As a patient, I want to upload documents (insurance cards, ID, medical reports) so that my records are complete
9. As a patient, I want to view my vaccination records and immunization history so that I can track my vaccinations
10. As a patient, I want to access educational materials relevant to my conditions so that I can better manage my health
11. As a family member, I want to access my child's or elderly parent's health information as a caregiver so that I can help manage their care

#### Acceptance Criteria

**Secure Patient Registration & Onboarding**:
- [ ] Self-registration portal with email verification
- [ ] Mobile number verification with OTP
- [ ] NIK validation and linkage to existing hospital records
- [ ] BPJS card number linkage
- [ ] Medical record number (MRN) lookup
- [ ] Identity verification (upload KTP or selfie verification)
- [ ] Account activation workflow
- [ ] Terms of service and privacy policy acceptance
- [ ] Password strength requirements (12+ chars, complexity)
- [ ] Multi-factor authentication setup (optional but recommended)
- [ ] Security questions setup for account recovery
- [ ] Welcome email with getting started guide
- [ ] Onboarding tutorial (optional guided tour)
- [ ] Account creation time <5 minutes
- [ ] Prevent duplicate accounts (by NIK, email, phone)
- [ ] Account verification before full access

**Personal Health Record Access**:
- [ ] View complete patient demographics (name, NIK, DOB, address, contact)
- [ ] Update personal information (address, phone, email with approval workflow)
- [ ] View medical history (past visits, hospitalizations, surgeries, procedures)
- [ ] View active and resolved diagnoses (ICD-10 with patient-friendly descriptions)
- [ ] View allergy list with severity and reactions
- [ ] View current medications (drug names, dosages, frequency, prescriber)
- [ ] View medication history
- [ ] View vital signs history (blood pressure, weight, height, temperature)
- [ ] View family medical history
- [ ] View social history (smoking, alcohol, occupation)
- [ ] Timeline view of all health events
- [ ] Search health records by date or keyword
- [ ] Export health records to PDF
- [ ] Data accuracy verification flag
- [ ] Last update timestamp on all records

**Appointment Scheduling & Management**:
- [ ] View available appointment slots by doctor and polyclinic
- [ ] Book new appointments online
- [ ] Select appointment type (consultation, follow-up, procedure, vaccination)
- [ ] Select preferred doctor or specialist
- [ ] Select appointment date and time from available slots
- [ ] Specify appointment reason (chief complaint)
- [ ] Upload relevant documents or photos before appointment
- [ ] Receive booking confirmation (email, SMS, WhatsApp)
- [ ] Add appointment to personal calendar (Google, Outlook)
- [ ] View upcoming appointments
- [ ] View past appointments
- [ ] Reschedule appointments (with applicable policies)
- [ ] Cancel appointments (with cancellation policy enforcement)
- [ ] Appointment reminders (24 hours, 2 hours before)
- [ ] Waitlist option for fully booked slots
- [ ] Telemedicine appointment booking (if available)
- [ ] Pre-appointment checklist (fasting required, bring documents, arrive early)
- [ ] Queue number notification on appointment day
- [ ] Real-time appointment status updates
- [ ] Average wait time display
- [ ] Book appointments for family members (caregiver access)

**Prescription Refill Requests**:
- [ ] View current and past prescriptions
- [ ] Request prescription refills for eligible medications
- [ ] Select pharmacy for pickup (hospital pharmacy or network pharmacy)
- [ ] Specify quantity needed
- [ ] Provide reason for refill request
- [ ] Track refill request status (pending, approved, rejected, ready for pickup)
- [ ] Receive notifications when prescription is ready
- [ ] View prescription history
- [ ] View medication information (drug name, dosage, instructions, warnings)
- [ ] View drug interaction warnings
- [ ] Request renewal before prescription expires
- [ ] Auto-refill option for chronic medications
- [ ] Electronic prescription to pharmacy integration
- [ ] Refill approval workflow (doctor review)
- [ ] Track refill requests in dashboard
- [ ] Refill eligibility checking (BPJS formulary compliance)

**Lab Results Viewing with Explanations**:
- [ ] View laboratory results as soon as they are released by doctor
- [ ] Display results in patient-friendly format
- [ ] Show reference ranges and flag abnormal values
- [ ] Provide explanations for each test (what the test measures, what results mean)
- [ ] Show test history and trends (for monitoring chronic conditions)
- [ ] Graphical visualization for trending values (HbA1c, cholesterol, etc.)
- [ ] Compare results with previous results
- [ ] View specimen collection date and time
- [ ] View ordering doctor and test date
- [ ] Download lab reports in PDF
- [ ] Email lab reports (to patient or another doctor)
- [ ] Critical value alert notification
- [ ] Link to educational resources for abnormal results
- [ ] Hide sensitive results with additional verification (HIV, genetic tests)
- [ ] Results release policy (doctor approves before patient sees results)
- [ ] Multi-language support (Indonesian and English)
- [ ] Integration with Epic 7 (Laboratory Information System)

**Secure Messaging with Providers**:
- [ ] Send secure messages to doctors and care team
- [ ] Select message recipient from care team list
- [ ] Choose message category (medical question, appointment question, billing question, prescription question)
- [ ] Attach documents or images to messages
- [ ] Receive notifications for new messages
- [ ] View message history (threaded conversation)
- [ ] Search messages by date or keyword
- [ ] Star important messages
- [ ] Message response time indicators
- [ ] Auto-acknowledgment of message receipt
- [ ] Secure messaging (encrypted, HIPAA-compliant)
- [ ] Prevent sharing sensitive PHI in unencrypted channels
- [ ] Message retention policy (e.g., 3 years)
- [ ] File attachment size limits and virus scanning
- [ ] Block/unblock messaging from specific providers
- [ ] Template messages for common requests
- [ ] Message categorization and folders
- [ ] Read receipts

**Bill Viewing & Online Payments**:
- [ ] View current and past bills/invoices
- [ ] View bill details (services, charges, insurance coverage, patient responsibility)
- [ ] Filter bills by date, status (paid, unpaid, overdue)
- [ ] Download bills in PDF format
- [ ] View payment history
- [ ] Make online payments securely
- [ ] Support multiple payment methods (credit/debit cards, bank transfer, virtual account, e-wallet, QRIS)
- [ ] Payment gateway integration (Midtrans, Xendit, or similar)
- [ ] Real-time payment confirmation
- [ ] Payment receipt generation
- [ ] Auto-receipt via email
- [ ] View BPJS claim status
- [ ] View insurance explanation of benefits (EOB)
- [ ] View outstanding balance
- [ ] View payment plans (installment options)
- [ ] Set up payment reminders
- [ ] Pre-payment for scheduled procedures
- [ ] Refund request functionality
- [ ] Integration with Epic 9 (Billing, Finance & Claims)
- [ ] Secure payment processing (PCI-DSS compliant)

**Document Upload (Insurance Cards, ID, Medical Reports)**:
- [ ] Upload insurance cards (BPJS, private insurance)
- [ ] Upload ID documents (KTP, passport, driver's license)
- [ ] Upload medical reports from other facilities
- [ ] Upload diagnostic images (X-ray, MRI, CT - with size limits)
- [ ] Upload vaccination certificates
- [ ] Upload disability or special needs documentation
- [ ] Document preview before upload
- [ ] Document categorization (insurance, ID, medical reports, other)
- [ ] Document status tracking (pending review, approved, rejected)
- [ ] Expiry notifications for insurance cards
- [ ] Replace outdated documents
- [ ] Secure document storage (encrypted at rest)
- [ ] Document access logs
- [ ] File type validation (PDF, JPG, PNG)
- [ ] File size limits (e.g., 10MB per file)
- [ ] Virus scanning for uploaded files
- [ ] Bulk document upload
- [ ] Document sharing with care team (with consent)
- [ ] Integration with Epic 3 (Medical Records)

**Vaccination Records & Immunization History**:
- [ ] View complete vaccination record
- [ ] View vaccination history from childhood to present
- [ ] Display vaccine name, date, dose, batch number, administering facility
- [ ] View upcoming required vaccinations
- [ ] Vaccination status indicators (complete, incomplete, overdue)
- [ ] Upload vaccination certificates from external sources
- [ ] Sync with SATUSEHAT immunization records (if available)
- [ ] View vaccination schedule (recommended vaccines by age)
- [ ] Set vaccination reminders
- [ ] Download vaccination certificate/sertificate imunisasi
- [ ] View COVID-19 vaccination status and certificate
- [ ] Integration with national immunization database (if available)
- [ ] Vaccination history for school/travel requirements
- [ ] Export vaccination record to PDF

**Patient Education Materials**:
- [ ] Access educational content library
- [ ] View content relevant to patient's conditions and medications
- [ ] Condition-specific educational materials (diabetes, hypertension, asthma, etc.)
- [ ] Medication-specific information and instructions
- [ ] Procedure preparation guides (fasting, pre-procedure instructions)
- [ ] Post-procedure care instructions
- [ ] Healthy lifestyle content (diet, exercise, smoking cessation)
- [ ] Mental health resources
- [ ] Preventive care guidelines (screening schedules, vaccinations)
- [ ] Videos, infographics, articles
- [ ] Search education library by keyword or category
- [ ] Bookmark/favorite useful content
- [ ] Share content with family members
- [ ] Multi-language support (Indonesian and English)
- [ ] Content vetted by medical professionals
- [ ] Regular content updates
- [ ] Accessibility features (text-to-speech, font size adjustment)

**Caregiver/Proxy Access for Family Members**:
- [ ] Add family members to caregiver account
- [ ] Request proxy access for child, elderly parent, or dependent
- [ ] Proxy access levels (full access, limited access, billing only)
- [ ] Verification process for proxy access (document upload, consent)
- [ ] View caregiver profile and linked patients
- [ ] Switch between patient views easily
- [ ] Receive notifications for linked patients
- [ ] Manage appointments for linked patients
- [ ] View health records for linked patients
- [ ] Send messages on behalf of linked patients
- [ ] Pay bills for linked patients
- [ ] Proxy access expiration and renewal
- [ ] Revoke proxy access
- [ ] Audit log of proxy activities
- [ ] Separate authentication for proxy access
- [ ] Legal guardian verification
- [ ] Caregiver consent documentation

#### Technical Notes

**Portal Architecture**:
- Separate patient portal module with dedicated authentication
- Mobile-responsive design (works on smartphones, tablets, desktop)
- Progressive web app (PWA) capabilities
- Single sign-on (SSO) integration (if hospital uses SSO)
- RESTful API for all portal functions
- Stateless authentication with JWT tokens
- Session management with timeout (30 minutes)
- Secure cookie handling
- CORS configuration for API access

**Security & Privacy**:
- Multi-factor authentication (optional but recommended)
- OAuth 2.0 / OpenID Connect for third-party integrations
- End-to-end encryption for messaging
- Data encryption at rest (AES-256) and in transit (TLS 1.3)
- Role-based access control (patient only, caregiver, proxy)
- Audit logging for all data access and changes
- Data minimization (only display necessary PHI)
- Compliance with Indonesian Personal Data Protection Law (PDP Law)
- HIPAA-inspired privacy practices (even if not legally required in Indonesia)
- Regular security audits and penetration testing
- Secure file upload with validation and virus scanning
- Password policies and account lockout after failed attempts
- CAPTCHA for account registration and login attempts

**API Integration**:
- Integration with Epic 1 (Foundation & Security) - Authentication
- Integration with Epic 2 (Patient Registration) - Patient lookup, BPJS eligibility
- Integration with Epic 3 (Medical Records) - Health record data, diagnoses, allergies, medications
- Integration with Epic 4 (Outpatient Management) - Appointment scheduling, prescriptions
- Integration with Epic 5 (Inpatient Management) - Inpatient records, discharge summaries
- Integration with Epic 6 (Pharmacy) - Prescription refills, drug information
- Integration with Epic 7 (Laboratory) - Lab results, test history
- Integration with Epic 8 (Radiology) - Radiology reports, images
- Integration with Epic 9 (Billing) - Bills, payments, insurance claims
- Integration with Epic 10 (BPJS) - Eligibility, claims status
- Integration with Epic 11 (SATUSEHAT) - Immunization records (FHIR Immunization resources)
- Payment gateway API integration (Midtrans, Xendit, or similar)
- SMS gateway API for OTP and notifications
- Email service API for transactional emails

**User Experience**:
- Clean, intuitive interface
- Accessibility (WCAG 2.1 AA compliance)
- Multi-language support (Indonesian, English)
- Responsive design for all screen sizes
- Fast page loads (<2 seconds)
- Offline mode for viewing cached data
- Push notifications (mobile app)
- Guided onboarding for first-time users
- Context-sensitive help and tooltips
- Search functionality throughout the portal
- Dashboard with personalized overview

**Scalability & Performance**:
- Caching for frequently accessed data (profile, appointments)
- CDN for static assets (images, documents, educational content)
- Database indexing for fast queries
- Background job processing for notifications
- Asynchronous processing for file uploads
- Load balancing for high-traffic periods
- Rate limiting to prevent abuse
- Database connection pooling
- Lazy loading for large datasets

**Notifications System**:
- Multi-channel notifications (email, SMS, in-app, push)
- Notification preferences management
- Digest notifications (daily, weekly summaries)
- Urgent alert system (critical lab values, appointment reminders)
- Notification history and tracking
- Unsubscribe options for non-critical notifications
- SMS template management
- Email template management

**Content Management**:
- CMS for patient education materials
- Content categorization and tagging
- Content approval workflow
- Content expiration and archiving
- Multi-language content management
- Content search functionality
- Content analytics (most viewed, helpfulness ratings)

**Testing & Quality Assurance**:
- Comprehensive security testing (OWASP Top 10)
- Usability testing with actual patients
- Accessibility testing (screen readers, keyboard navigation)
- Performance testing (load testing, stress testing)
- Cross-browser and cross-device testing
- Integration testing with all backend systems
- End-to-end testing of critical user journeys
- Patient data privacy testing

**Analytics & Monitoring**:
- Portal usage analytics (active users, feature usage)
- Patient engagement metrics
- Appointment no-show tracking
- Payment conversion rates
- Patient satisfaction surveys
- A/B testing capability for UX improvements
- Error tracking and monitoring
- Performance monitoring (response times, uptime)
- Security event monitoring

**Deployment & DevOps**:
- CI/CD pipeline for portal deployments
- Blue-green deployment for zero-downtime updates
- Automated testing in deployment pipeline
- Database migration scripts
- Configuration management
- Log aggregation and analysis
- Backup and disaster recovery procedures
- SSL/TLS certificate management
- Web application firewall (WAF)
- DDoS protection

---

**Epic Owner**: Patient Experience & IT Departments
**Business Stakeholders**: Hospital Director, Patient Experience Manager, Medical Director, Compliance Officer
**Technical Lead**: Full-Stack Team (Frontend + Backend + Security)
**Dependencies**: Patient registration, medical records, appointments, pharmacy, lab, radiology, billing systems
**Risk Level**: High (patient data privacy, security compliance, integration complexity)
**Priority**: High (patient satisfaction, operational efficiency, competitive advantage)
