### Epic 20: Staff Portal

**Epic ID**: EPIC-020
**Business Value**: Staff empowerment, reduced admin burden, improved HR efficiency, enhanced staff satisfaction and retention
**Complexity**: Medium-High
**Estimated Duration**: 4-5 weeks

#### Dependencies
- Epic 1 (Foundation & Security)
- Epic 14 (User Management & Training)
- Epic 15 (System Configuration & Master Data)

#### Key User Stories

1. As a staff member, I want to view and update my profile and contact information so that my records are always current
2. As a staff member, I want to view my shift schedule and request shift swaps so that I can manage my work-life balance
3. As a staff member, I want to submit leave and sick day requests online so that I don't need to fill out paper forms
4. As a staff member, I want to access my pay stubs and tax documents securely so that I can review my compensation
5. As a staff member, I want to access training modules and track my progress so that I can maintain my certifications
6. As a staff member, I want to view performance feedback and goals so that I can develop my career
7. As a staff member, I want to receive internal announcements and updates so that I stay informed about hospital news
8. As a healthcare professional, I want to track my credentials and certification expiry dates so that I maintain compliance
9. As a new staff member, I want to access onboarding checklists and resources so that I can get started effectively

#### Acceptance Criteria

**Self-Service Profile Management**:
- [ ] View complete staff profile (personal info, contact details, emergency contacts)
- [ ] Update personal information (address, phone, email, emergency contacts)
- [ ] Upload and update profile photo
- [ ] View employment details (position, department, hire date, employee ID)
- [ ] Update professional information (license numbers, specializations, education)
- [ ] Change password with security validation
- [ ] Configure notification preferences (email, SMS, in-app)
- [ ] View access history and login logs
- [ ] Update banking information for payroll
- [ ] All changes require approval for sensitive fields (position, salary data)
- [ ] Audit trail for all profile updates
- [ ] Data validation and sanitization

**Shift Scheduling & Swap Requests**:
- [ ] View personal shift calendar (daily, weekly, monthly views)
- [ ] View shift details (date, time, department, role, supervisor)
- [ ] Request shift swaps with colleagues
- [ ] Accept or decline shift swap requests
- [ ] View available shifts for pickup (open shifts)
- [ ] Request overtime assignments
- [ ] Submit availability preferences
- [ ] View upcoming shift assignments (next 7 days, next 30 days)
- [ ] Calendar sync with external calendars (Google Calendar, Outlook)
- [ ] Mobile-optimized shift view
- [ ] Shift change approval workflow
- [ ] Notifications for schedule changes
- [ ] Compliance with working hour regulations
- [ ] Prevent scheduling conflicts
- [ ] Track shift history and attendance

**Leave & Sick Day Request Workflows**:
- [ ] Submit leave requests online (annual leave, sick leave, personal leave, unpaid leave)
- [ ] Select leave type and dates from calendar
- [ ] Upload supporting documents (medical certificates for sick leave)
- [ ] View leave balance (annual, sick, personal, carried over)
- [ ] Check leave eligibility and accruals
- [ ] Multi-level approval workflow (supervisor, HR, department head)
- [ ] Track request status (pending, approved, rejected, cancelled)
- [ ] View leave history
- [ ] Cancel leave requests before approval
- [ ] Leave calendar (team leave overview, excludes sensitive details)
- [ ] Automatic leave balance calculation
- [ ] Compliance with Indonesian labor laws (UU Ketenagakerjaan)
- [ ] Notification for approval decisions
- [ ] Integration with payroll for leave deduction

**Pay Stub Access & Tax Documents**:
- [ ] View and download monthly pay stubs (slip gaji)
- [ ] Access historical pay records (up to 5 years)
- [ ] View earnings breakdown (basic salary, allowances, bonuses, overtime)
- [ ] View deductions (tax, BPJS Kesehatan, BPJS Ketenagakerjaan, other)
- [ ] Download tax documents (Form 1721, SPT Yearly)
- [ ] View tax summary and withheld tax (PPh 21)
- [ ] Access BPJS contribution details
- [ ] Download payslips in PDF format
- [ ] Secure document access (authentication required)
- [ ] Document watermarking for security
- [ ] Pay stub notification on payday
- [ ] Year-to-date earnings summary
- [ ] Reimbursement history and status

**Training Module Access & Progress Tracking**:
- [ ] View assigned training modules
- [ ] Access training materials (videos, documents, presentations)
- [ ] Complete online training courses
- [ ] Take quizzes and assessments
- [ ] Track training progress (completion percentage, remaining modules)
- [ ] View training history and certificates
- [ ] Download training completion certificates
- [ ] Set training reminders and deadlines
- [ ] Mandatory training alerts (compliance training, safety training)
- [ ] Competency tracking (clinical skills, technical skills)
- [ ] Continuing education credits tracking (SKP/SKPB)
- [ ] Training recommendation engine based on role
- [ ] Integration with HR learning management system
- [ ] Mobile-optimized training interface

**Performance Review & Feedback System**:
- [ ] View performance review schedule
- [ ] Access self-assessment forms
- [ ] Complete self-evaluation (rating, comments, achievements)
- [ ] View peer feedback requests
- [ ] Submit peer feedback
- [ ] View supervisor feedback and evaluations
- [ ] Track performance goals and OKRs
- [ ] Update goal progress
- [ ] View performance history
- [ ] Access performance improvement plans (if applicable)
- [ ] 360-degree feedback functionality
- [ ] Performance metrics dashboard
- [ ] Recognition and appreciation feed
- [ ] Career development planning tools
- [ ] Skill gap analysis

**Internal Communication & Announcements**:
- [ ] View hospital-wide announcements
- [ ] View department-specific announcements
- [ ] Filter announcements by category (HR, operations, events, policies)
- [ ] Push notifications for urgent announcements
- [ ] Announcement read receipts
- [ ] Search announcement history
- [ ] Subscribe to announcement categories
- [ ] Discussion forums for departments
- [ ] Direct messaging to colleagues and supervisors
- [ ] Group messaging for teams/units
- [ ] File sharing within messages
- [ ] Integration with hospital email system
- [ ] Mobile app notifications
- [ ] Archive and bookmark important announcements

**Credential & Certification Tracking**:
- [ ] View all professional credentials (SIP/STR, licenses, certifications)
- [ ] Track credential expiry dates
- [ ] Expiry alerts (30 days, 60 days, 90 days before)
- [ ] Upload renewed credentials
- [ ] Request credential renewal support
- [ ] View compliance status (compliant, at-risk, non-compliant)
- [ ] Mandatory training requirements tracking (Pelatihan K3, HIPERKES, PPRA)
- [ ] Competency assessment results
- [ ] Certification status dashboard
- [ ] Automated compliance reports for HR
- [ ] Integration with regulatory bodies (Kemenkes, MTI/KKI)
- [ ] Document storage for certificates
- [ ] Renewal workflow with reminders

**Onboarding Checklists for New Staff**:
- [ ] Access personalized onboarding dashboard
- [ ] View onboarding checklist by phase (pre-joining, day 1, week 1, month 1)
- [ ] Track completion of onboarding tasks
- [ ] Access required documents (employment contract, employee handbook, policies)
- [ ] Complete mandatory forms online (tax forms, BPJS enrollment, emergency contacts)
- [ ] View assigned buddy/mentor
- [ ] Schedule orientation sessions
- [ ] Access training modules for new hires
- [ ] Complete IT setup checklist (email, system access, equipment)
- [ ] Submit required documents (ID, diplomas, certificates)
- [ ] Progress tracking for managers
- [ ] Onboarding completion certificate
- [ ] Feedback survey after onboarding
- [ ] Integration with HR system

#### Technical Notes

**Portal Architecture**:
- Separate staff portal module with dedicated authentication
- Role-based access control for different staff types (doctors, nurses, admin, support)
- Mobile-responsive design (works on smartphones and tablets)
- Progressive web app (PWA) capabilities
- Single sign-on (SSO) integration with hospital systems
- Self-service password reset

**HR/Payroll System Integration**:
- REST API integration with HR management system
- Bi-directional data sync (profile data, leave balances, schedule)
- Secure file transfer for payslips and tax documents
- Real-time payroll data synchronization
- Employee master data sync
- Attendance system integration

**Security Considerations**:
- Multi-factor authentication for sensitive data access
- Data encryption for payroll and personal information
- Role-based document access control
- Audit logging for all portal activities
- Session timeout and secure session management
- GDPR/Personal Data Protection compliance (Indonesia's PDP Law)
- Secure file storage with access controls

**Notifications System**:
- Multi-channel notifications (email, SMS, in-app, push)
- Notification preferences management
- Digest notifications (daily, weekly summaries)
- Urgent alert system for critical announcements
- Notification history and tracking

**Reporting & Analytics**:
- Staff portal usage analytics
- Training completion reports
- Leave trend analysis
- Compliance status dashboard
- Staff satisfaction surveys
- Performance metrics aggregation
- Export to various formats (PDF, Excel, CSV)

**Scalability & Performance**:
- Caching for frequently accessed data (profile, schedules)
- Lazy loading for documents and training materials
- CDN for static assets
- Database indexing for fast queries
- Background job processing for notifications
- Load balancing for high-traffic periods

**Third-Party Integrations**:
- Calendar sync (Google Calendar, Microsoft Outlook)
- Payment gateway for staff purchases (cafeteria, pharmacy)
- Learning management system (LMS) integration
- Video conferencing integration (for training)
- E-signature for document approvals

---

**Epic Owner**: HR & IT Departments
**Business Stakeholders**: HR Director, Department Heads, Staff Representatives
**Technical Lead**: Backend + Frontend Teams
**Dependencies**: User management, security infrastructure, HR system integration
**Risk Level**: Medium (data privacy, integration complexity)
**Priority**: High (staff satisfaction, operational efficiency)
