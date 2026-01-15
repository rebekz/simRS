# Epic 023: Notification System

**Epic ID**: EPIC-022
**Business Value**: Improves patient engagement, operational efficiency, and communication - critical for patient satisfaction and care quality
**Complexity**: Medium-High
**Estimated Duration**: 4-5 weeks

---

## Dependencies

- Epic 1 (Foundation & Security)
- Epic 2 (Patient Registration & Queue Management)
- Epic 4 (Outpatient Management)
- Epic 5 (Inpatient Management)
- Epic 6 (Pharmacy Management)
- Epic 7 (Laboratory Information System)
- Epic 9 (Billing, Finance & Claims)

---

## Business Value

The Notification System provides:

1. **Patient Engagement**: Timely reminders and updates improve appointment adherence and treatment compliance
2. **Operational Efficiency**: Automated notifications reduce staff workload and no-show rates
3. **Care Quality**: Critical value alerts and medication reminders improve patient safety
4. **Patient Satisfaction**: Proactive communication enhances patient experience
5. **Revenue Optimization**: Payment reminders and appointment confirmations reduce revenue leakage

---

## Key User Stories

1. As a patient, I want to receive appointment reminders via SMS/WhatsApp so that I don't miss my scheduled visits
2. As a patient, I want to receive medication reminders so that I adhere to my treatment plan
3. As a doctor, I want to receive critical lab value alerts immediately so that I can take urgent action
4. As a patient, I want to be notified when my lab results are ready so that I can view them promptly
5. As a hospital administrator, I want to configure system alerts for downtime and failures so that issues are resolved quickly
6. As a patient, I want to manage my notification preferences so that I receive only relevant communications
7. As a staff member, I want to receive queue status notifications so that I can manage workflow efficiently

---

## Detailed User Stories

### STORY-022-01: Multi-Channel Notification Delivery

**As a** System Architect
**I want to** implement a multi-channel notification delivery system
**So that** notifications reach patients through their preferred communication channels

**Acceptance Criteria**:

**Channel Support**:
- [ ] SMS gateway integration (multiple providers supported)
- [ ] Email delivery (SMTP, third-party email services)
- [ ] Push notifications (mobile apps)
- [ ] In-app notifications (web application)
- [ ] WhatsApp Business API integration
- [ ] Voice call capability (for critical alerts)

**Notification Engine**:
- [ ] Centralized notification service architecture
- [ ] Queue-based notification processing (Redis/RabbitMQ)
- [ ] Retry logic with exponential backoff
- [ ] Failed notification tracking and reporting
- [ ] Rate limiting per channel
- [ ] Bulk notification support (broadcasts)
- [ ] Scheduled notification delivery
- [ ] Priority queues (urgent vs routine)

**Delivery Management**:
- [ ] Delivery status tracking (sent, delivered, failed, pending)
- [ ] Delivery confirmation receipts
- [ ] Failed notification retry mechanism (up to 3 attempts)
- [ ] Blacklist management (opt-out handling)
- [ ] Notification history and audit log
- [ ] Real-time delivery monitoring
- [ ] Delivery analytics (success rate, failure rate, channel performance)

**Template Management**:
- [ ] Multi-language template support (Indonesian, English, regional)
- [ ] Dynamic variable substitution (patient name, date, time, location)
- [ ] Rich text formatting support
- [ ] Template versioning
- [ ] Template approval workflow
- [ ] A/B testing capability for templates

**Technical Notes**:
- Notification microservice architecture
- Provider abstraction layer for easy provider switching
- Message queue for async processing
- Database tables: notifications, notification_templates, notification_logs, notification_preferences
- API endpoints: /api/notifications/send, /api/notifications/status, /api/notifications/templates
- Webhook support for delivery receipts

---

### STORY-022-02: Appointment Reminders and Confirmations

**As a** Patient
**I want to** receive appointment reminders and confirmations
**So that** I don't miss my scheduled medical visits

**Acceptance Criteria**:

**Appointment Reminders**:
- [ ] Send reminders 24 hours before appointment
- [ ] Send reminders 2 hours before appointment
- [ ] Include appointment details (date, time, doctor, location, queue number)
- [ ] Include cancellation/rescheduling instructions
- [ ] Support multiple reminder frequencies (daily, weekly, custom)
- [ ] Automatic reminder scheduling upon appointment booking
- [ ] Stop reminders if appointment is cancelled

**Appointment Confirmations**:
- [ ] Send immediate confirmation upon booking
- [ ] Include appointment reference number
- [ ] Include preparation instructions (fasting, bring documents, etc.)
- [ ] Include estimated wait time
- [ ] Send rescheduling confirmation when changed
- [ ] Send cancellation confirmation

**Patient Response**:
- [ ] Support confirmation replies (YES to confirm)
- [ ] Support cancellation replies (CANCEL to cancel)
- [ ] Support rescheduling requests (RESCHEDULE)
- [ ] Process reply keywords in multiple languages
- [ ] Update appointment status based on patient response
- [ ] Send follow-up acknowledgment

**Channel Preferences**:
- [ ] Respect patient's preferred channel (SMS, WhatsApp, Email)
- [ ] Fallback to secondary channel if primary fails
- [ ] Allow patient to change preference via reply
- [ ] Do not send reminders if opted out

**Reporting**:
- [ ] Track reminder delivery status
- [ ] Track patient response rates
- [ ] Track no-show rates with vs without reminders
- [ ] Generate reminder effectiveness reports

**Technical Notes**:
- Triggered by Epic 2 (Patient Registration) appointment events
- Triggered by Epic 4 (Outpatient) scheduling events
- Integration with queue management system
- Cron jobs for reminder scheduling
- Reply processing webhook
- Database: appointment_reminders, reminder_logs

---

### STORY-022-03: Medication Reminders

**As a** Patient
**I want to** receive medication reminders
**So that** I adhere to my prescribed treatment plan

**Acceptance Criteria**:

**Reminder Scheduling**:
- [ ] Schedule based on prescription instructions
- [ ] Support multiple daily reminders (morning, afternoon, evening)
- [ ] Support frequency-based reminders (daily, weekly, monthly)
- [ ] Support PRN (as needed) reminders with minimum interval
- [ ] Include medication name and dosage
- [ ] Include special instructions (take with food, on empty stomach)
- [ ] Include quantity remaining
- [ ] Alert when medication refill is due

**Medication-Specific Alerts**:
- [ ] Antibiotic course completion reminders
- [ ] Critical medication alerts (do not stop without consulting doctor)
- [ ] Interaction warnings when new medications prescribed
- [ ] Allergy alerts re-notification
- [ ] Expiry date reminders (for patient-held medications)

**Refill Reminders**:
- [ ] Alert when medication supply is low (3 days remaining)
- [ ] Include pharmacy contact information
- [ ] Include prescription refill number
- [ ] Support electronic refill requests

**Adherence Tracking**:
- [ ] Track patient acknowledgment of reminders
- [ ] Calculate medication adherence rate
- [ ] Alert doctor if adherence drops below 80%
- [ ] Generate adherence reports for physicians
- [ ] Support caregiver notifications (for pediatric/elderly patients)

**Caregiver Notifications**:
- [ ] Allow designation of primary caregiver
- [ ] Send medication reminders to caregiver
- [ ] Support multiple caregivers (family members)
- [ ] Allow caregiver to confirm medication administration

**Technical Notes**:
- Triggered by Epic 4 (Outpatient) prescription events
- Triggered by Epic 6 (Pharmacy) dispensing events
- Medication schedule calculation engine
- Adherence calculation algorithms
- Database: medication_reminders, medication_schedules, adherence_logs

---

### STORY-022-04: Lab Result Notifications

**As a** Patient
**I want to** be notified when my lab results are ready
**So that** I can view them and take appropriate action

**Acceptance Criteria**:

**Result Ready Notifications**:
- [ ] Send notification when results are verified and released
- [ ] Include test name and completion date
- [ ] Include access instructions (patient portal link, app)
- [ ] Include doctor's contact for questions
- [ ] Support batch notifications (multiple tests)

**Critical Value Alerts**:
- [ ] Immediate notification for critical values to patient
- [ ] Include clear explanation of urgency
- [ ] Include recommended actions (contact doctor, go to emergency)
- [ ] Include doctor's contact information
- [ ] Send via all available channels simultaneously
- [ ] Require acknowledgment receipt
- [ ] Alert doctor that patient was notified

**Normal Result Notifications**:
- [ ] Send notification when normal results are available
- [ ] Include brief summary (all normal, see details)
- [ ] Include patient portal access link
- [ ] Send within 24 hours of result release

**Abnormal Result Notifications**:
- [ ] Highlight abnormal values in notification
- [ ] Include brief explanation in non-medical terms
- [ ] Recommend follow-up action
- [ ] Include scheduling link for follow-up

**Result Access**:
- [ ] Secure link to patient portal
- [ ] Authentication required
- [ ] Time-limited access links (24 hours)
- [ ] PDF download option
- [ ] Share with doctor option

**Privacy & Compliance**:
- [ ] Do not include sensitive details in notification
- [ ] Require secure access for full results
- [ ] Log all result views
- [ ] Support proxy access (parents, guardians)

**Technical Notes**:
- Triggered by Epic 7 (Laboratory) result verification events
- Critical value detection from Epic 7
- Integration with patient portal authentication
- Secure token generation for result access
- Database: lab_notifications, critical_value_alerts

---

### STORY-022-05: Critical Value Alerts to Physicians

**As a** Doctor
**I want to** receive immediate alerts for critical lab values
**So that** I can take urgent action to protect patient safety

**Acceptance Criteria**:

**Critical Value Detection**:
- [ ] Automatic detection of critical values
- [ ] Configurable critical value thresholds by test
- [ ] Support age- and gender-specific thresholds
- [ ] Support patient-specific thresholds (based on history)
- [ ] Flag life-threatening values (STAT)
- [ ] Flag panic values (require immediate attention)

**Alert Delivery**:
- [ ] Send within 1 minute of result verification
- [ ] Send to ordering physician
- [ ] Send to on-call physician if ordering unavailable
- [ ] Send to department head if no response in 15 minutes
- [ ] Send via multiple channels (SMS, in-app, email)
- [ ] Override silent/do-not-disturb settings
- [ ] Escalation hierarchy for unacknowledged alerts

**Alert Content**:
- [ ] Patient identifier (name, MRN)
- [ ] Critical value and test name
- [ ] Normal range for comparison
- [ ] Timestamp of result
- [ ] Ordering physician
- [ ] Patient location (if inpatient)
- [ ] Direct link to full result
- [ ] Recommended actions (call patient, order repeat test)

**Acknowldgment & Response**:
- [ ] Require physician acknowledgment
- [ ] Track acknowledgment time
- [ ] Record physician's response/action taken
- [ ] Alert if not acknowledged within 5 minutes
- [ ] Support delegation (acknowledge on behalf)
- [ ] Auto-escalate after timeout

**Documentation**:
- [ ] Automatic documentation in medical record
- [ ] Include alert sent time
- [ ] Include acknowledgment time
- [ ] Include action taken
- [ ] Audit trail for compliance

**Reporting**:
- [ ] Critical value response time reporting
- [ ] Alert acknowledgment rates
- [ ] Physician performance metrics
- [ ] Compliance reports (regulatory)

**Technical Notes**:
- Real-time integration with Epic 7 (Laboratory)
- Critical value definition engine
- Escalation workflow engine
- Physician on-call schedule integration
- Database: critical_alerts, alert_acknowledgments, escalation_rules

---

### STORY-022-06: System Alerts (Downtime, Failures)

**As a** System Administrator
**I want to** receive alerts for system issues
**So that** I can resolve problems before they impact operations

**Acceptance Criteria**:

**System Health Monitoring**:
- [ ] Database connectivity alerts
- [ ] API endpoint failure alerts
- [ ] High CPU/memory usage alerts (>80%)
- [ ] Disk space low alerts (<20% free)
- [ ] Backup failure alerts
- [ ] Service downtime alerts
- [ ] Network connectivity alerts

**External Integration Alerts**:
- [ ] BPJS API failure alerts
- [ ] SATUSEHAT sync failure alerts
- [ ] SMS gateway failure alerts
- [ ] Payment gateway failure alerts
- [ ] Email service failure alerts
- [ ] Third-party API rate limit alerts

**Error Rate Monitoring**:
- [ ] High error rate alerts (>5% error rate)
- [ ] Error spike detection (sudden increase)
- [ ] Timeout alerts (response time >5 seconds)
- [ ] Failed login alerts (potential security issue)
- [ ] Failed transaction alerts

**Severity Levels**:
- [ ] CRITICAL: System down, data loss risk
- [ ] HIGH: Degraded performance, partial outage
- [ ] MEDIUM: Non-critical failures
- [ ] LOW: Performance degradation
- [ ] INFO: Informational notifications

**Alert Routing**:
- [ ] Route based on severity
- [ ] Route based on system component
- [ ] Route to on-call administrator
- [ ] Escalation for unacknowledged alerts
- [ ] Support multiple recipients
- [ ] Support on-call rotation

**Response Workflow**:
- [ ] Alert acknowledgment
- [ ] Assign to team member
- [ ] Add comments and updates
- [ ] Track resolution time
- [ ] Auto-close when resolved
- [ ] Post-incident report generation

**Maintenance Windows**:
- [ ] Suppress alerts during scheduled maintenance
- [ ] Maintenance calendar integration
- [ ] Pre-maintenance notifications
- [ ] Post-maintenance summaries

**Technical Notes**:
- Integration with monitoring system (Prometheus, Nagios)
- Webhook-based alert integration
- Alert aggregation and deduplication
- On-call schedule management
- Database: system_alerts, alert_rules, maintenance_windows

---

### STORY-022-07: Queue Status Notifications

**As a** Patient
**I want to** receive queue status updates
**So that** I don't have to wait at the hospital unnecessarily

**Acceptance Criteria**:

**Queue Position Updates**:
- [ ] Notify current queue position
- [ ] Send when position changes
- [ ] Send when approaching turn (5 patients away)
- [ ] Send when next in queue
- [ ] Include estimated wait time
- [ ] Include counter/room number

**Real-Time Updates**:
- [ ] Send every 10-15 minutes if wait time >30 minutes
- [ ] Send when doctor arrives (if running late)
- [ ] Send when doctor on break
- [ ] Send when queue resumes
- [ ] Send if significant delay occurs (>30 minutes)

**Departure Notifications**:
- [ ] Alert when it's time to leave for hospital
- [ ] Based on current queue speed and travel time
- [ ] Account for traffic patterns
- [ ] Send 30 minutes before needed

**Multi-Department Support**:
- [ ] Support queue notifications for multiple departments
- [ ] Poli Rawat Jalan queue notifications
- [ ] Pharmacy queue notifications
- [ ] Laboratory queue notifications
- [ ] Radiology queue notifications
- [ ] Cashier queue notifications
- [ ] Support multiple concurrent queues

**Channel Preferences**:
- [ ] SMS queue position updates
- [ ] WhatsApp queue updates with rich formatting
- [ ] In-app real-time queue status
- [ ] Digital display board integration
- [ ] Web portal queue status

**Queue Completion**:
- [ ] Notify when patient is being served
- [ ] Notify when service is completed
- [ ] Provide next steps (go to pharmacy, go to cashier)
- [ ] Include next queue number if applicable

**No-Show Detection**:
- [ ] Alert if patient misses queue turn
- [ ] Notify staff to handle no-show
- [ ] Offer to reschedule
- [ ] Update queue automatically

**Technical Notes**:
- Real-time integration with Epic 2 (Queue Management)
- WebSocket for real-time updates (in-app)
- Queue position calculation engine
- Estimated wait time algorithm
- Database: queue_notifications, queue_status_logs

---

### STORY-022-08: Payment Due Reminders

**As a** Patient
**I want to** receive payment reminders
**So that** I avoid late fees and service disruptions

**Acceptance Criteria**:

**Payment Reminders**:
- [ ] Send reminder 7 days before due date
- [ ] Send reminder 3 days before due date
- [ ] Send reminder on due date
- [ ] Send overdue notification
- [ ] Include outstanding amount
- [ ] Include payment deadline
- [ ] Include payment options and links

**Invoice Delivery**:
- [ ] Send invoice immediately after service
- [ ] Include PDF attachment or link
- [ ] Include detailed breakdown
- [ ] Include payment instructions
- [ ] Support multiple formats (email, SMS, in-app)

**Payment Options**:
- [ ] Direct payment link in notification
- [ ] QR code for mobile payment
- [ ] Bank transfer details
- [ ] Payment gateway link
- [ ] In-person payment instructions

**Overdue Management**:
- [ ] Escalating reminder frequency
- [ ] Late fee notifications
- [ ] Service suspension warnings
- [ ] Debt collection escalation
- [ ] Support payment plan arrangements

**Payment Confirmation**:
- [ ] Send payment receipt immediately
- [ ] Include transaction reference
- [ ] Update outstanding balance
- [ ] Stop reminder series

**Insurance Claims**:
- [ ] Notify when BPJS claim submitted
- [ ] Notify when claim approved
- [ ] Notify when claim rejected (with reason)
- [ ] Notify patient responsibility amount
- [ ] Include appeal process for rejections

**Technical Notes**:
- Triggered by Epic 9 (Billing) invoice events
- Integration with payment gateway
- Payment link generation (secure tokens)
- Overdue calculation engine
- Database: payment_reminders, payment_notifications

---

### STORY-022-09: Notification Preference Management

**As a** Patient
**I want to** manage my notification preferences
**So that** I receive only relevant communications

**Acceptance Criteria**:

**Preference Management Interface**:
- [ ] Patient portal interface for preferences
- [ ] Mobile app preference settings
- [ ] Allow opt-in/opt-out for each notification type
- [ ] Allow channel selection per notification type
- [ ] Allow frequency customization
- [ ] Allow quiet hours configuration
- [ ] Allow language preference

**Notification Type Preferences**:
- [ ] Appointment reminders (on/off)
- [ ] Medication reminders (on/off)
- [ ] Lab result notifications (on/off)
- [ ] Payment reminders (on/off)
- [ ] Queue notifications (on/off)
- [ ] Marketing/promotional messages (on/off)
- [ ] System updates (on/off)

**Channel Preferences**:
- [ ] Primary channel selection (SMS/WhatsApp/Email/Push)
- [ ] Secondary channel (fallback)
- [ ] Channel preferences per notification type
- [ ] Do-not-contact registry
- [ ] Support multiple phone numbers and emails

**Frequency & Timing**:
- [ ] Quiet hours (no notifications)
- [ ] Emergency override (always deliver critical)
- [ ] Maximum reminders per day
- [ ] Batch digest option (daily summary)
- [ ] Timezone handling

**Consent Management**:
- [ ] Explicit consent required for marketing
- [ ] Implicit consent for care-related notifications
- [ ] Easy opt-out mechanism
- [ ] Consent expiration and renewal
- [ ] GDPR/privacy regulation compliance
- [ ] Audit trail of consent changes

**Caregiver Preferences**:
- [ ] Designate primary caregiver
- [ ] Set caregiver notification preferences
- [ ] Support multiple caregivers
- [ ] Allow temporary caregiver access
- [ ] Age-appropriate consent (pediatric patients)

**Staff Preferences**:
- [ ] Allow staff to manage notification preferences
- [ ] Department-level notification settings
- [ ] On-call rotation preferences
- [ ] Critical alert preferences
- [ ] Do-not-disturb settings

**Technical Notes**:
- Preference database schema
- Preference API endpoints
- Preference validation engine
- Consent tracking and audit
- Integration with patient registration (Epic 2)
- Database: notification_preferences, consent_logs

---

### STORY-022-10: Template Management System

**As a** Hospital Administrator
**I want to** manage notification templates
**So that** communications are consistent and professional

**Acceptance Criteria**:

**Template Management**:
- [ ] Create notification templates
- [ ] Edit existing templates
- [ ] Version control for templates
- [ ] Template approval workflow
- [ ] Activate/deactivate templates
- [ ] Archive old templates
- [ ] Clone templates for easy creation

**Template Categories**:
- [ ] Appointment reminders
- [ ] Medication reminders
- [ ] Lab results
- [ ] Payment notifications
- [ ] System alerts
- [ ] Marketing messages
- [ ] Custom categories

**Template Editor**:
- [ ] Rich text editor
- [ ] Variable substitution ({{patient_name}}, {{appointment_time}}, etc.)
- [ ] Conditional logic (show/hide based on conditions)
- [ ] Multi-language support
- [ ] Preview functionality
- [ ] Test send functionality
- [ ] Character count display

**Variable Support**:
- [ ] Patient demographics (name, age, gender)
- [ ] Appointment details (date, time, doctor, location)
- [ ] Medical information (test names, medications)
- [ ] Financial information (amounts, due dates)
- [ ] System information (links, codes)
- [ ] Custom variables

**Multi-Language**:
- [ ] Create templates in multiple languages
- [ ] Auto-detect patient language preference
- [ ] Template translation management
- [ ] Regional language support (Javanese, Sundanese, etc.)
- [ ] Language fallback logic

**Validation & Testing**:
- [ ] Validate required variables
- [ ] Validate character limits (SMS: 160 chars)
- [ ] Test send to test numbers
- [ ] Preview in different channels
- [ ] Check for broken variables
- [ ] Spell check

**Approval Workflow**:
- [ ] Draft → Review → Approved → Active
- [ ] Require approval for production templates
- [ ] Approval history tracking
- [ ] Rollback to previous versions
- [ ] A/B testing support

**Analytics**:
- [ ] Track template usage
- [ ] Track delivery rates by template
- [ ] Track engagement rates
- [ ] A/B test results
- [ ] Template performance reports

**Technical Notes**:
- Template database schema
- Template variable engine
- Template rendering service
- Version control system
- Approval workflow engine
- Database: notification_templates, template_versions, template_variables

---

## Technical Architecture

### System Components

1. **Notification Service** (Microservice)
   - Centralized notification processing
   - Channel provider abstraction
   - Queue-based delivery
   - Retry and error handling

2. **Notification Engine**
   - Template rendering
   - Variable substitution
   - Multi-language support
   - Personalization engine

3. **Channel Providers**
   - SMS Gateway (multiple providers: Twilio, Nexmo, local providers)
   - Email Service (SMTP, SendGrid, AWS SES)
   - Push Notification Service (Firebase Cloud Messaging, Apple Push Service)
   - WhatsApp Business API
   - In-App Notification System

4. **Message Queue**
   - Redis or RabbitMQ
   - Priority queues
   - Dead letter queue
   - Retry queue

5. **Notification Preferences Service**
   - Preference management
   - Consent tracking
   - Channel selection logic

6. **Template Management System**
   - Template CRUD operations
   - Version control
   - Approval workflow

### Database Schema

```sql
-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    recipient_id UUID NOT NULL,
    recipient_type VARCHAR(20), -- 'patient', 'staff', 'system'
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    status VARCHAR(20), -- 'pending', 'sent', 'delivered', 'failed'
    template_id UUID,
    content TEXT,
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    failed_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notification Templates
CREATE TABLE notification_templates (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    language VARCHAR(10),
    content TEXT NOT NULL,
    variables JSONB,
    status VARCHAR(20), -- 'draft', 'active', 'archived'
    version INTEGER,
    created_by UUID,
    approved_by UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notification Preferences
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    notification_type VARCHAR(50),
    channel_enabled JSONB, -- {'sms': true, 'email': false, 'whatsapp': true}
    frequency VARCHAR(20),
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    language VARCHAR(10),
    consent_given BOOLEAN,
    consent_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Notification Logs
CREATE TABLE notification_logs (
    id UUID PRIMARY KEY,
    notification_id UUID,
    event VARCHAR(50), -- 'created', 'sent', 'delivered', 'failed', 'opened', 'clicked'
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Critical Alerts
CREATE TABLE critical_alerts (
    id UUID PRIMARY KEY,
    patient_id UUID,
    lab_result_id UUID,
    critical_value TEXT,
    test_name VARCHAR(100),
    severity VARCHAR(20), -- 'critical', 'panic', 'stat'
    sent_to_physician UUID,
    sent_to_patient BOOLEAN,
    acknowledged BOOLEAN,
    acknowledged_at TIMESTAMP,
    action_taken TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### API Endpoints

```
POST   /api/notifications/send              - Send notification
POST   /api/notifications/broadcast         - Send bulk notification
GET    /api/notifications/status/:id        - Get notification status
GET    /api/notifications/history/:user_id  - Get notification history
GET    /api/notifications/preferences       - Get user preferences
PUT    /api/notifications/preferences       - Update preferences
GET    /api/notifications/templates         - List templates
POST   /api/notifications/templates         - Create template
PUT    /api/notifications/templates/:id     - Update template
GET    /api/notifications/templates/:id     - Get template details
DELETE /api/notifications/templates/:id     - Delete template
POST   /api/notifications/test              - Test notification
```

### Integration Points

1. **Epic 2 (Patient Registration)**
   - Appointment booking → Appointment confirmation
   - Queue updates → Queue notifications

2. **Epic 4 (Outpatient Management)**
   - Prescription created → Medication reminders
   - Follow-up scheduled → Appointment reminders

3. **Epic 5 (Inpatient Management)**
   - Discharge scheduled → Discharge instructions
   - Bed changes → Room update notifications

4. **Epic 6 (Pharmacy Management)**
   - Prescription dispensed → Pickup reminders
   - Medication low stock → Refill reminders

5. **Epic 7 (Laboratory)**
   - Results verified → Result notifications
   - Critical values → Critical alerts
   - Sample received → Sample tracking

6. **Epic 9 (Billing)**
   - Invoice generated → Invoice delivery
   - Payment due → Payment reminders
   - Payment received → Receipt delivery

### Security & Compliance

1. **Data Privacy**
   - No PHI in notification content (use references only)
   - Secure links for accessing sensitive information
   - Data encryption at rest and in transit
   - Audit logging for all notifications

2. **Consent Management**
   - Explicit opt-in for marketing
   - Easy opt-out mechanism
   - Consent expiration and renewal
   - Compliance with GDPR, PDPA, and Indonesian regulations

3. **Rate Limiting**
   - Prevent spam and abuse
   - Per-user rate limits
   - Per-channel rate limits
   - Burst protection

4. **Content Filtering**
   - Validate notification content
   - Prevent injection attacks
   - Sanitize user-generated content
   - URL validation

### Monitoring & Maintenance

1. **Delivery Monitoring**
   - Success rate monitoring per channel
   - Failure rate monitoring
   - Delivery time tracking
   - Cost tracking per channel

2. **Alerting**
   - High failure rate alerts
   - Provider outage alerts
   - Queue backlog alerts
   - Credit low alerts (for paid services)

3. **Reporting**
   - Daily delivery reports
   - Monthly usage reports
   - Cost analysis reports
   - Performance metrics

4. **Maintenance**
   - Template review and updates
   - Provider performance evaluation
   - Cost optimization
   - Feature enhancements

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Notification service architecture
- Database schema implementation
- Basic SMS gateway integration
- Email service integration
- Template management system
- Preference management interface

### Phase 2: Appointment & Queue Notifications (Week 2-3)
- Appointment reminder system
- Queue status notifications
- Appointment confirmations
- Integration with Epic 2 and Epic 4
- Patient portal integration

### Phase 3: Clinical Notifications (Week 3-4)
- Medication reminders
- Lab result notifications
- Critical value alerts to physicians
- Integration with Epic 6 and Epic 7
- Physician portal integration

### Phase 4: Financial & System Notifications (Week 4-5)
- Payment reminders
- Invoice delivery
- System alerts
- Integration with Epic 9
- Admin dashboard for monitoring

### Phase 5: Advanced Features (Week 5)
- WhatsApp Business API integration
- Push notifications for mobile apps
- Advanced template features (A/B testing)
- Analytics and reporting
- Performance optimization

---

## Success Criteria

- [ ] All notification types functional with 95%+ delivery rate
- [ ] Multi-channel delivery operational (SMS, Email, WhatsApp, Push)
- [ ] Patient preference management implemented
- [ ] Critical value alerts delivered within 1 minute
- [ ] Appointment reminders reduce no-show rate by 30%
- [ ] Medication reminders improve adherence by 25%
- [ ] Payment reminders reduce overdue accounts by 40%
- [ ] System average response time <2 seconds
- [ ] Template management system operational
- [ ] Compliance with consent regulations verified
- [ ] Cost per notification <IDR 100 for SMS, <IDR 50 for WhatsApp
- [ ] Patient satisfaction score >85% for notification system

---

## Risk Assessment

### High Risks
1. **SMS/WhatsApp Cost Overruns**: High volume can be expensive
   - Mitigation: Implement smart routing, batch notifications, prefer WhatsApp for cost savings

2. **Regulatory Compliance**: Consent management is critical
   - Mitigation: Implement robust consent tracking, easy opt-out, regular compliance audits

3. **Provider Reliability**: External service dependencies
   - Mitigation: Multi-provider setup, fallback mechanisms, SLA monitoring

### Medium Risks
1. **Alert Fatigue**: Too many notifications may be ignored
   - Mitigation: Smart frequency capping, preference management, A/B testing

2. **Integration Complexity**: Dependencies on 7+ other epics
   - Mitigation: Well-defined APIs, event-driven architecture, comprehensive testing

3. **Template Quality**: Poor templates can confuse patients
   - Mitigation: Approval workflow, A/B testing, regular review

---

**Document Version:** 1.0
**Created:** 2026-01-15
**Status:** Draft - Ready for Review
