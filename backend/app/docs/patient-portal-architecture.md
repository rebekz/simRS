# Patient Portal Authentication Architecture

**Document Version:** 1.0
**Last Updated:** 2026-01-15
**Author:** SIMRS Architecture Team

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Account Creation Flow](#account-creation-flow)
4. [NIK/BPJS Card Linkage](#nikbpjs-card-linkage)
5. [Role-Based Access Control](#role-based-access-control)
6. [Security Requirements](#security-requirements)
7. [Database Schema](#database-schema)
8. [API Contract](#api-contract)
9. [Integration with Existing Authentication](#integration-with-existing-authentication)
10. [Audit Logging](#audit-logging)
11. [Deployment Considerations](#deployment-considerations)

---

## Overview

The Patient Portal Authentication system provides secure, self-service access for patients to manage their healthcare information while maintaining strict separation from internal staff authentication systems. This architecture is designed to:

- Enable patients to create and manage their own portal accounts
- Link portal accounts to existing patient medical records via NIK or BPJS card number
- Support caregiver/proxy access for minors and dependents
- Provide comprehensive audit logging for compliance with Indonesian UU 27/2022
- Maintain security best practices including MFA, session management, and rate limiting

### Key Features

1. **Self-Service Registration:** Email and mobile verification with step-by-step account creation
2. **Identity Verification:** NIK and BPJS card number validation against existing patient records
3. **Role-Based Access:** Patient-only access and caregiver/proxy access modes
4. **Enhanced Security:** Optional MFA, secure session management, comprehensive audit trails
5. **Regulatory Compliance:** Full audit logging, data encryption, consent management

---

## Design Principles

### Separation of Concerns

- **Separate Authentication Domain:** Patient portal accounts use `PatientPortalAccount` model, separate from internal `User` model
- **Independent Session Management:** Patient sessions tracked separately from staff sessions
- **Distinct Permission System:** Patient-specific permissions differ from staff RBAC

### Security First

- **Defense in Depth:** Multiple layers of security including verification tokens, rate limiting, MFA
- **Zero Trust:** Verify explicitly, use least privilege access, assume breach
- **Encryption at Rest and in Transit:** All sensitive data encrypted using existing encryption utilities

### Patient Experience

- **Frictionless Yet Secure:** Balance security with usability for patients of varying technical literacy
- **Clear Feedback:** Explicit error messages and guidance throughout registration flow
- **Accessibility Support:** WCAG 2.1 AA compliant interfaces

### Compliance

- **UU 27/2022:** Full audit logging of all patient data access
- **BPJS Integration:** Support for BPJS card validation
- **Data Residency:** All patient data stored within Indonesian data centers

---

## Account Creation Flow

### Registration Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PATIENT PORTAL REGISTRATION                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   STEP 1     │     │   STEP 2     │     │   STEP 3     │     │   STEP 4     │
│  Initiate    │────▶│  Verify      │────▶│  Complete    │────▶│  Link        │
│ Registration │     │  Identity    │     │  Profile     │     │  Medical     │
│              │     │              │     │              │     │  Record      │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
   Email/            Email/            Create             NIK/BPJS
   Mobile            Mobile            Password           Validation
   Input             Verification      & Security         Against
                     Code              Questions         Patient DB
```

### Detailed Registration Steps

#### Step 1: Initiate Registration

**Endpoint:** `POST /api/v1/patient-portal/register/initiate`

**Request:**
```json
{
  "email": "patient@example.com",
  "mobile_phone": "+6281234567890"
}
```

**Validation:**
- Email format validation
- Indonesian mobile number format (+62 or 08...)
- Check for existing accounts with email/mobile
- Rate limiting: Max 3 requests per hour per IP/email

**Response:**
```json
{
  "registration_id": "reg_abc123xyz",
  "expires_at": "2026-01-15T12:30:00Z",
  "message": "Verification codes sent to email and mobile"
}
```

**Background Actions:**
- Generate 6-digit email verification code (expires in 15 minutes)
- Generate 6-digit SMS verification code (expires in 10 minutes)
- Store codes in `PatientPortalVerificationToken` table
- Send verification emails and SMS
- Create audit log entry

#### Step 2: Verify Identity

**Endpoint:** `POST /api/v1/patient-portal/register/verify`

**Request:**
```json
{
  "registration_id": "reg_abc123xyz",
  "email_code": "123456",
  "sms_code": "654321"
}
```

**Validation:**
- Verify both codes match stored tokens
- Check expiration (soft delete expired tokens)
- Maximum 3 verification attempts
- Codes can be resent with rate limiting

**Response:**
```json
{
  "verification_token": "ver_xyz789abc",
  "expires_at": "2026-01-15T13:00:00Z",
  "next_step": "complete_profile"
}
```

**Security:**
- Consume verification tokens after use (mark as used)
- Log failed verification attempts
- Implement exponential backoff for failed attempts

#### Step 3: Complete Profile

**Endpoint:** `POST /api/v1/patient-portal/register/complete-profile`

**Request:**
```json
{
  "verification_token": "ver_xyz789abc",
  "full_name": "Budi Santoso",
  "password": "SecurePass123!@#",
  "security_questions": [
    {
      "question_id": 1,
      "answer": "Kucing"
    },
    {
      "question_id": 2,
      "answer": "Surabaya"
    }
  ],
  "accepted_terms": true,
  "privacy_consent": true
}
```

**Validation:**
- Password strength validation (12+ chars, mixed case, numbers, special chars)
- Security question answers hashed before storage
- Terms and privacy consent required
- Profile data validation

**Response:**
```json
{
  "account_id": "pa_123456",
  "status": "pending_medical_linkage",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 1800
}
```

**Background Actions:**
- Create `PatientPortalAccount` record
- Hash password using bcrypt
- Hash security question answers
- Generate JWT tokens
- Create session record
- Send welcome email

#### Step 4: Link Medical Record

**Endpoint:** `POST /api/v1/patient-portal/register/link-medical-record`

**Request:**
```json
{
  "account_id": "pa_123456",
  "linkage_method": "nik",
  "nik": "3201010101010001",
  "date_of_birth": "1980-05-15",
  "phone_verification": "+6281234567890"
}
```

**OR**

```json
{
  "account_id": "pa_123456",
  "linkage_method": "bpjs",
  "bpjs_card_number": "1234567890123",
  "date_of_birth": "1980-05-15",
  "phone_verification": "+6281234567890"
}
```

**Validation:**
- Query `patients` table by NIK or BPJS card number
- Verify DOB matches patient record
- Verify phone number matches patient record (or send SMS verification code)
- Handle multiple matches (rare, but possible due to data entry errors)

**Response:**
```json
{
  "patient_id": 12345,
  "medical_record_number": "RM-2024-001234",
  "linkage_status": "verified",
  "account_status": "active",
  "message": "Account successfully linked to medical record"
}
```

**Error Cases:**
- No match found: Offer manual verification pathway
- Multiple matches: Flag for manual review
- Data mismatch: Provide guidance to contact hospital administration

---

## NIK/BPJS Card Linkage

### Linkage Validation Process

#### Automated Verification

1. **Primary Method:** NIK matching
   - NIK is unique identifier in Indonesia
   - Match against `patients.nik` field
   - Require DOB verification as secondary proof

2. **Secondary Method:** BPJS Card Number
   - Match against `patients.bpjs_card_number` field
   - Require DOB and phone verification
   - Optional: Real-time validation with BPJS API (if available)

3. **Tertiary Verification:** Phone Number
   - Send SMS verification code to phone on record
   - Prevents account takeover via stolen NIK/BPJS info

#### Verification Fallback Pathways

**Pathway A: Manual Verification**

When automated verification fails:
1. Patient uploads ID card (KTP) or BPJS card
2. Hospital staff verifies in admin panel
3. Staff approves/rejects linkage
4. Patient notified of decision

**Pathway B: In-Person Verification**

Patient visits hospital with physical ID:
1. Receptionist verifies identity
2. Receptionist links account in admin system
3. Immediate activation

#### Linkage Security Considerations

- **Rate Limiting:** Max 5 linkage attempts per account per day
- **Cooldown Period:** 30-minute lockout after 3 failed attempts
- **Audit Trail:** Log all linkage attempts with metadata
- **Data Minimization:** Only store linkage, don't duplicate patient data
- **Tamper Detection:** Cryptographic hash of linked patient ID to detect unlinking attempts

---

## Role-Based Access Control

### Patient Portal Roles

#### 1. PATIENT_OWNER

**Description:** Primary account holder accessing their own medical information

**Permissions:**
- View own medical records
- View own prescriptions and medications
- Manage own appointments
- Access own billing and payment history
- Download own lab results and imaging
- Manage security settings (password, MFA)
- Grant/revoke caregiver access

**Data Scope:** All data where `patient_id = account.patient_id`

#### 2. CAREGIVER_PROXY

**Description:** Authorized caregiver/parent/guardian accessing dependent's information

**Permissions:**
- View dependent's medical records
- View dependent's prescriptions
- Manage dependent's appointments
- Access dependent's billing
- Receive notifications for dependent's care
- Cannot modify security settings
- Cannot grant additional caregivers

**Data Scope:** All data where `patient_id IN (account.patient_id, account.managed_patient_ids)`

**Constraints:**
- Maximum 2 caregivers per patient (exceptions by admin approval)
- Caregivers must be 18+ years old
- Caregiver relationship must be verified (parent, spouse, legal guardian)
- All caregiver actions attributed in audit logs with "Acting on behalf of: {patient_name}"

#### 3. DEPENDENT_MINOR

**Description:** Patient account for minor (under 18) managed by parent/guardian

**Permissions:**
- Limited view of own records (age-appropriate filtering)
- Cannot manage appointments without parental consent
- Cannot access billing information
- Cannot modify security settings

**Special Handling:**
- Automatically transitions to PATIENT_OWNER at 18
- Notifications sent to parent and child (age-appropriate)
- Privacy considerations for adolescent healthcare (varies by age)

### Permission Matrix

| Action | Patient Owner | Caregiver Proxy | Dependent Minor |
|--------|---------------|-----------------|-----------------|
| View Medical Records | Full | Full | Age-filtered |
| View Prescriptions | Full | Full | Age-filtered |
| Book Appointments | Full | Full | With Consent |
| Cancel Appointments | Full | Full | No |
| View Billing | Full | Full | No |
| Make Payments | Full | Full | No |
| Download Documents | Full | Full | Limited |
| Manage Security | Full | No | No |
| Grant Caregiver Access | Full | No | No |
| View Audit Log | Own | Dependent's | No |
| Email Subscriptions | Full | Full | Limited |

---

## Security Requirements

### Authentication Security

#### 1. Password Policy

**Requirements:**
- Minimum 12 characters
- Must include uppercase, lowercase, numbers, special characters
- Cannot contain common passwords or dictionary words
- Password history: Last 5 passwords cannot be reused
- Password expiration: 180 days (configurable)
- Force password change on first login

**Implementation:**
- Use existing `validate_password_strength()` function from `/backend/app/core/security.py`
- Store passwords using bcrypt (already implemented)
- Implement password history tracking in `PatientPortalSecurityEvent` table

#### 2. Multi-Factor Authentication (MFA)

**Optional MFA for Patients:**
- TOTP (Time-based One-Time Password) via authenticator app
- SMS-based OTP as fallback (for less tech-savvy patients)
- Email-based OTP as tertiary fallback

**MFA Triggers:**
- New device login
- Login from unusual location
- Password change
- Caregiver access grant
- Sensitive data download (full medical history)

**Implementation:**
- Reuse existing MFA functions from `/backend/app/core/security.py`:
  - `generate_mfa_secret()`
  - `verify_mfa_code()`
  - `get_mfa_totp_uri()`
- Store MFA secret in `PatientPortalAccount.mfa_secret`
- Backup codes for recovery (encrypted)

#### 3. Account Lockout Policy

**Lockout Triggers:**
- 5 failed login attempts
- 10 failed verification code attempts
- 3 failed linkage attempts within 24 hours

**Lockout Duration:**
- First lockout: 15 minutes
- Second lockout: 1 hour
- Third lockout: 24 hours
- Fourth+ lockout: Manual unlock required

**Unlock Mechanisms:**
- Automatic expiration after lockout period
- SMS verification unlock (send code to verified mobile)
- Email verification unlock
- Manual unlock by hospital staff (admin panel)

### Session Management

#### 1. Session Lifecycle

**Session Creation:**
- Generate on successful login
- Store session token hash (not plaintext)
- Associate with device fingerprint
- Set appropriate expiration

**Session Duration:**
- Default: 24 hours
- Remember me option: 30 days
- MFA-enabled sessions: 12 hours (stricter)
- Idle timeout: 2 hours of inactivity

**Session Revocation:**
- Explicit logout
- Password change
- MFA enable/disable
- Security event detection
- Admin-initiated revocation

#### 2. Device Management

**Device Fingerprinting:**
- User agent hash
- IP address (with tolerance for mobile networks)
- Device type (mobile, desktop, tablet)
- Geographic location (country, city level)

**Multi-Device Support:**
- Maximum 5 active devices
- Patients can view and revoke active sessions
- New device notifications (email/SMS)

#### 3. Token Security

**Access Token:**
- JWT with 30-minute expiration
- Includes: `account_id`, `patient_id`, `role`, `permissions`
- Signed using existing JWT infrastructure
- Refresh token rotation on every use

**Refresh Token:**
- Long-lived (30 days)
- Single-use (rotation on refresh)
- Stored hashed in database
- Bound to device fingerprint

### Rate Limiting

**Endpoint-Specific Limits:**

| Endpoint | Limit | Window | Penalty |
|----------|-------|--------|---------|
| POST /register/initiate | 3/hour | IP, Email | 1-hour lockout |
| POST /register/verify | 10/hour | Registration ID | 15-minute lockout |
| POST /login | 5/hour | IP, Account | Exponential backoff |
| POST /link-medical-record | 5/day | Account | 30-minute lockout |
| POST /resend-code | 3/hour | Account | 1-hour lockout |
| GET /medical-records | 60/hour | Account | Temporary throttle |

**Implementation:**
- Use Redis for distributed rate limiting
- Per-IP and per-account tracking
- Configurable limits via environment variables

### Data Protection

#### 1. Encryption at Rest

- Passwords: bcrypt (already implemented)
- Security question answers: bcrypt
- MFA secrets: encrypted with AES-256-GCM
- Refresh tokens: SHA-256 hash
- Verification tokens: SHA-256 hash
- Sensitive audit data: Use existing encryption from `/backend/app/core/encryption.py`

#### 2. Encryption in Transit

- All APIs require HTTPS (TLS 1.3)
- HSTS headers enabled
- Certificate pinning for mobile apps (future)

#### 3. Sensitive Data Handling

- DOB: Store normally (needed for clinical care)
- Phone: Last 4 digits masked in logs
- Email: Lowercase, normalized before storage
- NIK: One-way hash for linkage verification
- BPJS: Encrypted in database

---

## Database Schema

### Table: patient_portal_accounts

**Purpose:** Store patient portal authentication accounts separate from internal staff accounts

```sql
CREATE TABLE patient_portal_accounts (
    id SERIAL PRIMARY KEY,

    -- Authentication credentials
    email VARCHAR(255) UNIQUE NOT NULL,
    mobile_phone VARCHAR(20) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,

    -- Profile information
    full_name VARCHAR(255) NOT NULL,
    preferred_name VARCHAR(255),

    -- Status fields
    account_status VARCHAR(20) NOT NULL DEFAULT 'pending_medical_linkage',
    -- Options: pending_verification, pending_medical_linkage, active, suspended, deleted

    is_email_verified BOOLEAN DEFAULT FALSE,
    is_mobile_verified BOOLEAN DEFAULT FALSE,

    -- Security settings
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(32),
    mfa_backup_codes_encrypted TEXT,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,

    -- Security questions
    security_question_1_id INTEGER,
    security_question_1_answer_hash VARCHAR(255),
    security_question_2_id INTEGER,
    security_question_2_answer_hash VARCHAR(255),

    -- Role and permissions
    account_role VARCHAR(20) NOT NULL DEFAULT 'patient_owner',
    -- Options: patient_owner, caregiver_proxy, dependent_minor

    -- Linkage to patient record
    patient_id INTEGER REFERENCES patients(id),
    linkage_method VARCHAR(10),
    -- Options: nik, bpjs, manual
    linkage_verified_at TIMESTAMP WITH TIME ZONE,
    linkage_verified_by INTEGER REFERENCES users(id),

    -- Consent and terms
    accepted_terms_version VARCHAR(20),
    accepted_terms_at TIMESTAMP WITH TIME ZONE,
    privacy_consent_given BOOLEAN DEFAULT FALSE,
    privacy_consent_at TIMESTAMP WITH TIME ZONE,

    -- Communication preferences
    email_notifications_enabled BOOLEAN DEFAULT TRUE,
    sms_notifications_enabled BOOLEAN DEFAULT TRUE,
    notification_language VARCHAR(10) DEFAULT 'id',

    -- Caregiver access (if this account is a caregiver)
    managed_patient_ids INTEGER[],
    caregiver_relationship VARCHAR(50),
    caregiver_verification_status VARCHAR(20),
    -- Options: pending, verified, expired, revoked
    caregiver_expires_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_ip_address VARCHAR(45),
    user_agent TEXT,
    device_fingerprint VARCHAR(255)
);

-- Indexes
CREATE INDEX idx_patient_portal_accounts_email ON patient_portal_accounts(email);
CREATE INDEX idx_patient_portal_accounts_mobile ON patient_portal_accounts(mobile_phone);
CREATE INDEX idx_patient_portal_accounts_patient_id ON patient_portal_accounts(patient_id);
CREATE INDEX idx_patient_portal_accounts_status ON patient_portal_accounts(account_status);
CREATE UNIQUE INDEX idx_patient_portal_accounts_email_unique ON patient_portal_accounts(LOWER(email));
CREATE UNIQUE INDEX idx_patient_portal_accounts_mobile_unique ON patient_portal_accounts(mobile_phone);
```

### Table: patient_portal_verification_tokens

**Purpose:** Store email and SMS verification tokens for registration and other operations

```sql
CREATE TABLE patient_portal_verification_tokens (
    id SERIAL PRIMARY KEY,

    -- Token identification
    token_type VARCHAR(20) NOT NULL,
    -- Options: email_verification, sms_verification, password_reset, email_change, phone_change
    token_hash VARCHAR(255) UNIQUE NOT NULL,

    -- Associated account
    account_id INTEGER REFERENCES patient_portal_accounts(id),
    registration_id VARCHAR(50),

    -- Delivery details
    destination VARCHAR(255) NOT NULL,
    -- Email address or phone number

    -- Token data (for verification codes)
    verification_code VARCHAR(10),

    -- Expiration and status
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    is_used BOOLEAN DEFAULT FALSE,

    -- Tracking
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    delivery_status VARCHAR(20),
    -- Options: pending, sent, delivered, failed
    delivery_error TEXT,

    -- Rate limiting
    attempt_count INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP WITH TIME ZONE,

    -- Request metadata
    ip_address VARCHAR(45),
    user_agent TEXT
);

CREATE INDEX idx_verification_tokens_token_hash ON patient_portal_verification_tokens(token_hash);
CREATE INDEX idx_verification_tokens_account_id ON patient_portal_verification_tokens(account_id);
CREATE INDEX idx_verification_tokens_registration_id ON patient_portal_verification_tokens(registration_id);
CREATE INDEX idx_verification_tokens_expires_at ON patient_portal_verification_tokens(expires_at);
```

### Table: patient_portal_sessions

**Purpose:** Manage patient portal sessions separate from staff sessions

```sql
CREATE TABLE patient_portal_sessions (
    id SERIAL PRIMARY KEY,

    -- Account reference
    account_id INTEGER REFERENCES patient_portal_accounts(id) NOT NULL,

    -- Tokens
    access_token_hash VARCHAR(255) UNIQUE NOT NULL,
    refresh_token_hash VARCHAR(255) UNIQUE NOT NULL,

    -- Device and location
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_type VARCHAR(50),
    -- Options: desktop, mobile, tablet
    device_name VARCHAR(100),
    browser VARCHAR(100),
    location VARCHAR(100),
    device_fingerprint VARCHAR(255),

    -- Session metadata
    login_method VARCHAR(20),
    -- Options: password, sso (future), mfa

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Status
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoke_reason VARCHAR(100),

    -- MFA
    mfa_verified_at TIMESTAMP WITH TIME ZONE,
    mfa_method VARCHAR(20)
    -- Options: totp, sms, email
);

CREATE INDEX idx_portal_sessions_account_id ON patient_portal_sessions(account_id);
CREATE INDEX idx_portal_sessions_access_token ON patient_portal_sessions(access_token_hash);
CREATE INDEX idx_portal_sessions_refresh_token ON patient_portal_sessions(refresh_token_hash);
CREATE INDEX idx_portal_sessions_device_fingerprint ON patient_portal_sessions(device_fingerprint);
```

### Table: patient_portal_security_events

**Purpose:** Comprehensive audit log for patient portal security events (compliance with UU 27/2022)

```sql
CREATE TABLE patient_portal_security_events (
    id SERIAL PRIMARY KEY,

    -- Timestamp
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Account information
    account_id INTEGER REFERENCES patient_portal_accounts(id),
    account_email VARCHAR(255),

    -- Event details
    event_type VARCHAR(50) NOT NULL,
    -- Options: registration_initiated, registration_completed, login, logout, password_change,
    -- mfa_enabled, mfa_disabled, account_locked, account_unlocked, linkage_attempt,
    -- linkage_verified, caregiver_added, caregiver_removed, data_accessed, data_downloaded

    -- Resource information
    resource_type VARCHAR(50),
    -- Options: patient_account, medical_record, prescription, appointment, billing
    resource_id VARCHAR(100),

    -- Request metadata
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_path VARCHAR(500),
    request_method VARCHAR(10),

    -- Result
    success BOOLEAN DEFAULT TRUE,
    failure_reason TEXT,

    -- Additional context
    event_metadata JSONB,

    -- Caregiver context (if applicable)
    acting_on_behalf_of_patient_id INTEGER,
    acting_on_behalf_of_patient_name VARCHAR(255)
);

CREATE INDEX idx_portal_security_events_account_id ON patient_portal_security_events(account_id);
CREATE INDEX idx_portal_security_events_timestamp ON patient_portal_security_events(event_timestamp);
CREATE INDEX idx_portal_security_events_event_type ON patient_portal_security_events(event_type);
CREATE INDEX idx_portal_security_events_resource ON patient_portal_security_events(resource_type, resource_id);
```

### Table: patient_portal_password_reset_tokens

**Purpose:** Handle password reset for patient portal accounts

```sql
CREATE TABLE patient_portal_password_reset_tokens (
    id SERIAL PRIMARY KEY,

    account_id INTEGER REFERENCES patient_portal_accounts(id) NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,

    -- Tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    is_used BOOLEAN DEFAULT FALSE,

    -- Request metadata
    ip_address VARCHAR(45),
    user_agent TEXT,

    -- Delivery
    delivery_method VARCHAR(10),
    -- Options: email, sms
    delivery_status VARCHAR(20)
);

CREATE INDEX idx_portal_password_reset_token_hash ON patient_portal_password_reset_tokens(token_hash);
CREATE INDEX idx_portal_password_reset_account_id ON patient_portal_password_reset_tokens(account_id);
```

### Table: patient_portal_caregiver_consents

**Purpose:** Track caregiver access grants and consents

```sql
CREATE TABLE patient_portal_caregiver_consents (
    id SERIAL PRIMARY KEY,

    -- Patient (owner of the medical record)
    patient_account_id INTEGER REFERENCES patient_portal_accounts(id) NOT NULL,
    patient_id INTEGER REFERENCES patients(id) NOT NULL,

    -- Caregiver (proxy account)
    caregiver_account_id INTEGER REFERENCES patient_portal_accounts(id) NOT NULL,

    -- Relationship details
    relationship_type VARCHAR(50) NOT NULL,
    -- Options: parent, guardian, spouse, child, sibling, other
    relationship_description TEXT,

    -- Consent
    consent_given_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    consent_given_ip_address VARCHAR(45),
    access_level VARCHAR(20) DEFAULT 'full',
    -- Options: full, limited, view_only

    -- Status
    status VARCHAR(20) DEFAULT 'active',
    -- Options: active, suspended, revoked, expired

    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE,

    -- Revocation
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by INTEGER REFERENCES patient_portal_accounts(id),
    revoke_reason TEXT,

    -- Verification
    verification_method VARCHAR(20),
    -- Options: self_attested, document_upload, in_person

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(patient_account_id, caregiver_account_id, patient_id)
);

CREATE INDEX idx_caregiver_consents_patient ON patient_portal_caregiver_consents(patient_account_id);
CREATE INDEX idx_caregiver_consents_caregiver ON patient_portal_caregiver_consents(caregiver_account_id);
CREATE INDEX idx_caregiver_consents_status ON patient_portal_caregiver_consents(status);
```

### Table: patient_portal_security_questions

**Purpose:** Define available security questions for account recovery

```sql
CREATE TABLE patient_portal_security_questions (
    id SERIAL PRIMARY KEY,

    question_text TEXT NOT NULL,
    question_text_id TEXT NOT NULL,
    -- Indonesian translation

    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(question_text_id)
);

-- Seed data for security questions
INSERT INTO patient_portal_security_questions (question_text, question_text_id, display_order) VALUES
('What was the name of your first pet?', 'Siapa nama hewan peliharaan pertama Anda?', 1),
('What city were you born in?', 'Di kota mana Anda dilahirkan?', 2),
('What is your mother''s maiden name?', 'Apa nama gadis ibu Anda?', 3),
('What was the make of your first car?', 'Apa merek mobil pertama Anda?', 4),
('What elementary school did you attend?', 'SD mana yang pernah Anda tinggali?', 5);
```

### Foreign Key Relationships

```
patient_portal_accounts
├─── patient_id ────────────────> patients.id
├─── linkage_verified_by ───────> users.id
│
patient_portal_sessions
└─── account_id ────────────────> patient_portal_accounts.id
│
patient_portal_verification_tokens
├─── account_id ────────────────> patient_portal_accounts.id
│
patient_portal_security_events
├─── account_id ────────────────> patient_portal_accounts.id
├─── acting_on_behalf_of_patient_id ──> patients.id
│
patient_portal_password_reset_tokens
└─── account_id ────────────────> patient_portal_accounts.id
│
patient_portal_caregiver_consents
├─── patient_account_id ────────> patient_portal_accounts.id
├─── caregiver_account_id ──────> patient_portal_accounts.id
├─── patient_id ────────────────> patients.id
├─── revoked_by ────────────────> patient_portal_accounts.id
```

---

## API Contract

### Base URL

```
Production: https://api.hospital.com/api/v1/patient-portal
Staging: https://api-staging.hospital.com/api/v1/patient-portal
```

### Authentication

All authenticated endpoints require Bearer token:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Response Format

Success responses:
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Optional success message"
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* additional error context */ }
  }
}
```

### Endpoints

#### 1. Registration

##### POST /register/initiate

Initiate patient portal registration by sending verification codes.

**Request:**
```json
{
  "email": "patient@example.com",
  "mobile_phone": "+6281234567890"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "registration_id": "reg_abc123xyz",
    "email_masked": "p***@example.com",
    "mobile_masked": "+628******7890",
    "email_expires_at": "2026-01-15T12:30:00Z",
    "sms_expires_at": "2026-01-15T12:25:00Z"
  },
  "message": "Verification codes sent to email and mobile"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid email or phone format
- `429 Too Many Requests`: Too many registration attempts
- `409 Conflict`: Email or phone already registered

##### POST /register/resend-code

Resend verification code during registration.

**Request:**
```json
{
  "registration_id": "reg_abc123xyz",
  "code_type": "email"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "expires_at": "2026-01-15T12:30:00Z"
  },
  "message": "Verification code resent"
}
```

##### POST /register/verify

Verify email and SMS codes to proceed with registration.

**Request:**
```json
{
  "registration_id": "reg_abc123xyz",
  "email_code": "123456",
  "sms_code": "654321"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "verification_token": "ver_xyz789abc",
    "expires_at": "2026-01-15T13:00:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid or expired codes
- `429 Too Many Requests`: Too many verification attempts

##### POST /register/complete-profile

Complete registration by creating account with profile details.

**Request:**
```json
{
  "verification_token": "ver_xyz789abc",
  "full_name": "Budi Santoso",
  "password": "SecurePass123!@#",
  "security_questions": [
    {
      "question_id": 1,
      "answer": "Kucing"
    },
    {
      "question_id": 2,
      "answer": "Surabaya"
    }
  ],
  "accepted_terms": true,
  "privacy_consent": true,
  "notification_preferences": {
    "email_enabled": true,
    "sms_enabled": true,
    "language": "id"
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "account_id": "pa_123456",
    "email": "patient@example.com",
    "status": "pending_medical_linkage",
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 1800
  }
}
```

**Error Responses:**
- `400 Bad Request`: Weak password, missing required fields
- `401 Unauthorized`: Invalid or expired verification token
- `409 Conflict`: Account already exists

##### POST /register/link-medical-record

Link portal account to existing patient medical record.

**Request (NIK-based):**
```json
{
  "nik": "3201010101010001",
  "date_of_birth": "1980-05-15",
  "phone_verification_code": "123456"
}
```

**Request (BPJS-based):**
```json
{
  "bpjs_card_number": "1234567890123",
  "date_of_birth": "1980-05-15",
  "phone_verification_code": "123456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "patient_id": 12345,
    "medical_record_number": "RM-2024-001234",
    "linkage_status": "verified",
    "account_status": "active",
    "full_name": "Budi Santoso",
    "date_of_birth": "1980-05-15",
    "message": "Account successfully linked to medical record"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid NIK/BPJS format, DOB mismatch
- `404 Not Found`: No matching patient record found
- `409 Conflict`: Account already linked, or NIK linked to different account
- `429 Too Many Requests`: Too many linkage attempts

##### POST /register/request-manual-verification

Request manual verification when automatic linkage fails.

**Request:**
```json
{
  "full_name": "Budi Santoso",
  "nik": "3201010101010001",
  "reason": "Data mismatch in hospital records",
  "id_document_url": "https://uploads.example.com/ktp_abc123.jpg"
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "verification_request_id": "vr_123456",
    "status": "pending_review",
    "estimated_processing_hours": 24
  },
  "message": "Verification request submitted. You will be notified via email."
}
```

#### 2. Authentication

##### POST /auth/login

Authenticate with email/phone and password.

**Request:**
```json
{
  "login_identifier": "patient@example.com",
  "password": "SecurePass123!@#",
  "mfa_code": "123456",
  "device_fingerprint": "fp_abc123xyz"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 1800,
    "mfa_required": false,
    "account": {
      "account_id": "pa_123456",
      "email": "patient@example.com",
      "full_name": "Budi Santoso",
      "role": "patient_owner",
      "patient_id": 12345,
      "medical_record_number": "RM-2024-001234"
    }
  }
}
```

**MFA Required Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "mfa_required": true,
    "mfa_methods": ["totp", "sms"],
    "temporary_token": "temp_xyz123"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid credentials, account locked
- `403 Forbidden`: Account suspended or deleted
- `429 Too Many Requests`: Too many login attempts

##### POST /auth/refresh

Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "Bearer",
    "expires_in": 1800
  }
}
```

##### POST /auth/logout

Logout current session.

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response (204 No Content)**

##### POST /auth/logout-all

Logout from all devices.

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Response (204 No Content)**

#### 3. Password Management

##### POST /password-reset/request

Request password reset (sends email/SMS).

**Request:**
```json
{
  "email": "patient@example.com"
}
```

**Response (204 No Content)**
- Always returns 204 to prevent email enumeration

##### POST /password-reset/verify

Verify password reset code.

**Request:**
```json
{
  "token": "reset_abc123xyz"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "verified": true,
    "can_reset": true
  }
}
```

##### POST /password-reset/confirm

Confirm password reset with new password.

**Request:**
```json
{
  "token": "reset_abc123xyz",
  "new_password": "NewSecurePass456!@#"
}
```

**Response (204 No Content)**

##### POST /password/change

Change password (authenticated).

**Request:**
```json
{
  "current_password": "SecurePass123!@#",
  "new_password": "NewSecurePass456!@#"
}
```

**Response (204 No Content)**

#### 4. MFA Management

##### POST /mfa/setup

Initiate MFA setup (requires password verification).

**Request:**
```json
{
  "password": "SecurePass123!@#",
  "method": "totp"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "qr_code_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
    "backup_codes": ["ABCD1234", "EFGH5678", "IJKL9012"]
  }
}
```

##### POST /mfa/verify

Verify MFA code and enable MFA.

**Request:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "code": "123456"
}
```

**Response (204 No Content)**

##### POST /mfa/disable

Disable MFA (requires password verification).

**Request:**
```json
{
  "password": "SecurePass123!@#"
}
```

**Response (204 No Content)**

#### 5. Account Management

##### GET /account

Get current account information.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "account_id": "pa_123456",
    "email": "patient@example.com",
    "mobile_phone": "+6281234567890",
    "full_name": "Budi Santoso",
    "account_status": "active",
    "role": "patient_owner",
    "patient": {
      "patient_id": 12345,
      "medical_record_number": "RM-2024-001234",
      "date_of_birth": "1980-05-15",
      "gender": "male",
      "blood_type": "A"
    },
    "security": {
      "mfa_enabled": true,
      "password_changed_at": "2026-01-10T10:30:00Z",
      "failed_login_attempts": 0
    },
    "consent": {
      "accepted_terms_version": "1.0",
      "accepted_terms_at": "2026-01-01T09:00:00Z",
      "privacy_consent_given": true
    }
  }
}
```

##### PUT /account/profile

Update profile information.

**Request:**
```json
{
  "preferred_name": "Budi",
  "notification_preferences": {
    "email_enabled": true,
    "sms_enabled": false,
    "language": "id"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "account_id": "pa_123456",
    "updated_at": "2026-01-15T12:00:00Z"
  }
}
```

##### GET /account/sessions

Get all active sessions.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "sess_abc123",
        "device_type": "desktop",
        "device_name": "Chrome on macOS",
        "browser": "Chrome",
        "location": "Jakarta, Indonesia",
        "ip_address": "180.245.123.45",
        "created_at": "2026-01-15T10:00:00Z",
        "last_used_at": "2026-01-15T11:30:00Z",
        "is_current": true
      }
    ]
  }
}
```

##### DELETE /account/sessions/{session_id}

Revoke a specific session.

**Response (204 No Content)**

#### 6. Caregiver Management

##### POST /caregivers/invite

Invite a caregiver to access account.

**Request:**
```json
{
  "caregiver_email": "caregiver@example.com",
  "relationship_type": "spouse",
  "access_level": "full",
  "expires_at": "2027-01-15T00:00:00Z"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "invitation_id": "inv_xyz789",
    "invite_token": "invite_abc123",
    "expires_at": "2026-01-22T00:00:00Z",
    "message": "Invitation sent to caregiver email"
  }
}
```

##### POST /caregivers/accept

Accept caregiver invitation.

**Request:**
```json
{
  "invite_token": "invite_abc123",
  "account_id": "pa_789012"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "consent_id": "cg_12345",
    "patient_name": "Budi Santoso",
    "access_level": "full",
    "relationship_type": "spouse"
  }
}
```

##### GET /caregivers

Get list of caregivers for current account (or patients you care for).

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "my_caregivers": [
      {
        "consent_id": "cg_12345",
        "caregiver_name": "Siti Santoso",
        "caregiver_email": "caregiver@example.com",
        "relationship_type": "spouse",
        "access_level": "full",
        "status": "active",
        "created_at": "2026-01-01T10:00:00Z",
        "expires_at": "2027-01-15T00:00:00Z"
      }
    ],
    "patients_i_care_for": [
      {
        "consent_id": "cg_67890",
        "patient_name": "Ani Santoso",
        "patient_id": 67890,
        "medical_record_number": "RM-2024-005678",
        "relationship_type": "parent",
        "access_level": "full",
        "status": "active"
      }
    ]
  }
}
```

##### DELETE /caregivers/{consent_id}

Revoke caregiver access.

**Response (204 No Content)**

#### 7. Security & Audit

##### GET /security/activity

Get account security activity log.

**Query Parameters:**
- `limit`: Number of records (default: 20, max: 100)
- `offset`: Pagination offset
- `event_type`: Filter by event type

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "event_id": "evt_12345",
        "timestamp": "2026-01-15T10:30:00Z",
        "event_type": "login",
        "success": true,
        "ip_address": "180.245.123.45",
        "location": "Jakarta, Indonesia",
        "device": "Chrome on macOS",
        "details": {
          "login_method": "password",
          "mfa_verified": true
        }
      }
    ],
    "pagination": {
      "total": 50,
      "limit": 20,
      "offset": 0
    }
  }
}
```

##### GET /security/questions

Get available security questions.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": 1,
        "question_text_id": "Siapa nama hewan peliharaan pertama Anda?",
        "display_order": 1
      }
    ]
  }
}
```

##### POST /security/questions/verify

Verify security question answers (for account recovery).

**Request:**
```json
{
  "email": "patient@example.com",
  "answers": [
    {
      "question_id": 1,
      "answer": "Kucing"
    },
    {
      "question_id": 2,
      "answer": "Surabaya"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "verified": true,
    "reset_token": "reset_abc123xyz",
    "expires_at": "2026-01-15T13:00:00Z"
  }
}
```

### Error Codes Reference

| Code | Description |
|-----|-------------|
| `INVALID_REQUEST` | Malformed request body |
| `INVALID_CREDENTIALS` | Email/phone or password incorrect |
| `ACCOUNT_LOCKED` | Account locked due to failed attempts |
| `ACCOUNT_SUSPENDED` | Account suspended by admin |
| `ACCOUNT_NOT_FOUND` | Account does not exist |
| `ACCOUNT_PENDING_VERIFICATION` | Email/mobile not yet verified |
| `ACCOUNT_PENDING_LINKAGE` | Medical record not yet linked |
| `INVALID_VERIFICATION_CODE` | Email/SMS code incorrect or expired |
| `WEAK_PASSWORD` | Password does not meet security requirements |
| `PASSWORD_REUSED` | Password was used recently |
| `MFA_REQUIRED` | Multi-factor authentication required |
| `INVALID_MFA_CODE` | MFA code incorrect |
| `TOKEN_EXPIRED` | JWT or reset token expired |
| `TOKEN_INVALID` | Token signature invalid |
| `RATE_LIMIT_EXCEEDED` | Too many requests, try again later |
| `EMAIL_ALREADY_REGISTERED` | Email already in use |
| `PHONE_ALREADY_REGISTERED` | Phone number already in use |
| `PATIENT_NOT_FOUND` | No matching patient record |
| `PATIENT_ALREADY_LINKED` | Patient record already linked to another account |
| `DOB_MISMATCH` | Date of birth does not match |
| `CAREGIVER_LIMIT_REACHED` | Maximum caregivers reached |
| `INSUFFICIENT_PERMISSIONS` | Not authorized for this action |
| `RESOURCE_NOT_FOUND` | Requested resource does not exist |

---

## Integration with Existing Authentication

### Architecture Overview

The patient portal authentication system is designed as a **parallel authentication domain** that shares security infrastructure but maintains complete separation from staff authentication.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIMRS AUTHENTICATION LAYER                         │
└─────────────────────────────────────────────────────────────────────────────┘

                               ┌──────────────┐
                               │   SHARED     │
                               │  SECURITY    │
                               │ INFRASTRUCTURE│
                               └──────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
            ┌───────▼────────┐                 ┌────────▼──────┐
            │  STAFF AUTH    │                 │ PATIENT PORTAL│
            │  (Existing)    │                 │    AUTH       │
            └────────────────┘                 └───────────────┘
                    │                                   │
            ┌───────▼────────┐                 ┌────────▼──────┐
            │  User Model    │                 │ PatientPortal │
            │  - users       │                 │ Account Model │
            │  - sessions    │                 │ - portal_     │
            │  - audit_logs  │                 │   accounts    │
            │                │                 │ - portal_     │
            │  Roles:        │                 │   sessions    │
            │  - ADMIN       │                 │ - portal_     │
            │  - DOCTOR      │                 │   security_   │
            │  - NURSE       │                 │   events      │
            │  - etc.        │                 │               │
            └────────────────┘                 │ Roles:        │
                                               │ - PATIENT_    │
                                               │   OWNER       │
                                               │ - CAREGIVER_  │
                                               │   PROXY       │
                                               └───────────────┘
```

### Shared Components

The patient portal leverages existing security utilities from `/backend/app/core/security.py`:

1. **Password Hashing:**
   - Uses existing `pwd_context` (bcrypt)
   - Functions: `get_password_hash()`, `verify_password()`

2. **JWT Token Generation:**
   - Uses existing `create_access_token()`, `create_refresh_token()`
   - Same signing algorithm and secret key
   - Different token payload structure to distinguish patient vs staff

3. **MFA Functions:**
   - Uses existing `generate_mfa_secret()`, `verify_mfa_code()`
   - Uses existing `get_mfa_totp_uri()`, `generate_qr_code()`

4. **Encryption:**
   - Uses existing encryption from `/backend/app/core/encryption.py`
   - For sensitive data in verification tokens and audit logs

5. **Password Validation:**
   - Uses existing `validate_password_strength()`
   - Ensures consistent password policy across system

### Separate Components

The patient portal has completely separate:

1. **Database Tables:**
   - `patient_portal_accounts` (not `users`)
   - `patient_portal_sessions` (not `sessions`)
   - `patient_portal_security_events` (separate from `audit_logs`)
   - `patient_portal_verification_tokens`
   - `patient_portal_caregiver_consents`

2. **Authentication Dependencies:**
   - `get_current_patient_account()` (new dependency)
   - Separate token validation logic
   - Separate session management

3. **Permission System:**
   - Patient-specific permissions differ from staff RBAC
   - No overlap with staff permission tables

4. **API Routes:**
   - `/api/v1/patient-portal/*` (separate router)
   - No overlap with `/api/v1/auth/*`

### Token Payload Structure

**Staff Access Token:**
```json
{
  "sub": "123",
  "type": "access",
  "role": "doctor",
  "exp": 1705290600,
  "iat": 1705288800
}
```

**Patient Access Token:**
```json
{
  "sub": "456",
  "type": "access",
  "domain": "patient_portal",
  "role": "patient_owner",
  "patient_id": 789,
  "exp": 1705290600,
  "iat": 1705288800
}
```

The `domain` field distinguishes patient tokens from staff tokens, allowing middleware to route to appropriate authentication logic.

### Dependency Implementation

Create new dependency in `/backend/app/core/deps.py`:

```python
async def get_current_patient_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> PatientPortalAccount:
    """Get current authenticated patient portal account from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Verify token is for patient portal domain
    if payload.get("domain") != "patient_portal":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token domain",
        )

    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    account_id = payload.get("sub")
    if not account_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Fetch patient portal account
    result = await db.execute(
        select(PatientPortalAccount).filter(
            PatientPortalAccount.id == int(account_id)
        )
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Patient account not found",
        )

    if account.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {account.account_status}",
        )

    # Check session validity
    token_hash = hash_token(token)
    session = await db.execute(
        select(PatientPortalSession).filter(
            PatientPortalSession.account_id == account.id,
            PatientPortalSession.access_token_hash == token_hash,
            PatientPortalSession.is_revoked == False
        )
    )
    if not session.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )

    return account
```

---

## Audit Logging

### Audit Requirements (UU 27/2022 Compliance)

Indonesia's UU 27/2022 requires comprehensive logging of personal data access. The patient portal must log:

1. **All Authentication Events:** Login, logout, failed attempts, MFA challenges
2. **All Data Access:** Medical record views, downloads, API calls
3. **All Account Changes:** Profile updates, password changes, security settings
4. **All Caregiver Actions:** Access grants, revocations, data access on behalf of patient
5. **All Failed Operations:** Failed login attempts, failed linkage attempts

### Audit Log Schema

The `patient_portal_security_events` table captures all required audit data:

- **Who:** `account_id`, `account_email` (and `acting_on_behalf_of` for caregivers)
- **What:** `event_type`, `resource_type`, `resource_id`
- **When:** `event_timestamp`
- **Where:** `ip_address`, `location` (derived from IP)
- **How:** `user_agent`, `request_path`, `request_method`
- **Result:** `success`, `failure_reason`
- **Context:** `event_metadata` (JSONB for flexible additional data)

### Critical Events to Log

| Event Type | Description | Logged Fields |
|------------|-------------|---------------|
| `registration_initiated` | Registration started | email, mobile, ip_address |
| `registration_completed` | Account created | account_id, verification_method |
| `email_verified` | Email verification code verified | email, verification_method |
| `sms_verified` | SMS verification code verified | mobile, verification_method |
| `medical_record_linked` | Account linked to patient record | patient_id, linkage_method |
| `login` | Successful login | account_id, login_method, mfa_used |
| `login_failed` | Failed login attempt | account_id (if found), failure_reason |
| `logout` | Explicit logout | account_id, session_duration |
| `password_changed` | Password changed | account_id, change_method |
| `password_reset_requested` | Password reset initiated | account_id, delivery_method |
| `mfa_enabled` | MFA turned on | account_id, mfa_method |
| `mfa_disabled` | MFA turned off | account_id |
| `account_locked` | Account auto-locked | account_id, lock_reason |
| `account_unlocked` | Account unlocked | account_id, unlock_method |
| `medical_record_viewed` | Patient viewed own record | account_id, patient_id |
| `medical_record_downloaded` | Full record downloaded | account_id, patient_id, format |
| `prescription_viewed` | Prescription viewed | account_id, prescription_id |
| `appointment_booked` | Appointment created | account_id, appointment_id |
| `caregiver_granted` | Caregiver access granted | patient_account_id, caregiver_account_id |
| `caregiver_revoked` | Caregiver access revoked | patient_account_id, caregiver_account_id |
| `caregiver_viewed_record` | Caregiver accessed patient data | caregiver_account_id, patient_account_id, patient_id |
| `session_revoked` | Session terminated | account_id, session_id, revoke_reason |
| `suspicious_activity` | Potential security issue detected | account_id, detection_reason |

### Caregiver Audit Logging

When a caregiver accesses a patient's data, the audit log must clearly indicate:

```json
{
  "event_type": "medical_record_viewed",
  "account_id": 789,
  "account_email": "caregiver@example.com",
  "acting_on_behalf_of_patient_id": 123,
  "acting_on_behalf_of_patient_name": "Budi Santoso",
  "resource_type": "medical_record",
  "resource_id": "123",
  "event_metadata": {
    "relationship_type": "spouse",
    "consent_id": "cg_12345",
    "access_level": "full"
  }
}
```

### Audit Log Retention

- **Retention Period:** 10 years (compliance requirement)
- **Archival Strategy:** Move logs older than 1 year to cold storage
- **Access Control:** Only admin and compliance officers can view logs
- **Log Integrity:** Cryptographic hashes to detect tampering
- **Export Capability:** Generate CSV/PDF reports for compliance audits

### Audit Query API

##### GET /security/audit

Query audit logs (admin/compliance only).

**Query Parameters:**
- `account_id`: Filter by account
- `event_type`: Filter by event type
- `start_date`: Start of date range
- `end_date`: End of date range
- `include_caregiver_actions`: Include caregiver-on-behalf-of events

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "event_id": "evt_12345",
        "timestamp": "2026-01-15T10:30:00Z",
        "account_email": "patient@example.com",
        "event_type": "login",
        "resource_type": null,
        "resource_id": null,
        "ip_address": "180.245.123.45",
        "location": "Jakarta, Indonesia",
        "user_agent": "Mozilla/5.0...",
        "success": true,
        "metadata": {
          "login_method": "password",
          "mfa_verified": true
        }
      }
    ],
    "pagination": {
      "total": 1000,
      "page": 1,
      "per_page": 50
    }
  }
}
```

---

## Deployment Considerations

### Environment Variables

Add to `/backend/app/core/config.py`:

```python
# Patient Portal Configuration
PATIENT_PORTAL_ENABLED: bool = True
PATIENT_PORTAL_REGISTRATION_OPEN: bool = True
PATIENT_PORTAL_REQUIRE_MANUAL_VERIFICATION: bool = False
PATIENT_PORTAL_MAX_CAREGIVERS_PER_PATIENT: int = 2

# Patient Portal Session Settings
PATIENT_PORTAL_SESSION_EXPIRE_MINUTES: int = 1440  # 24 hours
PATIENT_PORTAL_REMEMBER_ME_DAYS: int = 30
PATIENT_PORTAL_IDLE_TIMEOUT_MINUTES: int = 120

# Patient Portal Security
PATIENT_PORTAL_MFA_OPTIONAL: bool = True
PATIENT_PORTAL_PASSWORD_EXPIRE_DAYS: int = 180
PATIENT_PORTAL_MAX_LOGIN_ATTEMPTS: int = 5
PATIENT_PORTAL_LOCKOUT_DURATION_MINUTES: int = 15
PATIENT_PORTAL_VERIFICATION_CODE_EXPIRE_MINUTES: int = 15

# Patient Portal Rate Limiting
PATIENT_PORTAL_RATE_LIMIT_ENABLED: bool = True
PATIENT_PORTAL_RATE_LIMIT_REDIS_URL: str = "redis://localhost:6379/1"

# Patient Portal Email/SMS
PATIENT_PORTAL_EMAIL_FROM: str = "noreply@hospital.com"
PATIENT_PORTAL_EMAIL_FROM_NAME: str = "SIMRS Patient Portal"
PATIENT_PORTAL_SMS_FROM: str = "SIMRS"

# Patient Portal URLs
PATIENT_PORTAL_FRONTEND_URL: str = "https://portal.hospital.com"
PATIENT_PORTAL_TERMS_URL: str = "https://portal.hospital.com/terms"
PATIENT_PORTAL_PRIVACY_URL: str = "https://portal.hospital.com/privacy"
```

### Database Migration

Create Alembic migration for new tables:

```bash
# Generate migration
alembic revision --autogenerate -m "Add patient portal authentication tables"

# Apply migration
alembic upgrade head
```

### Deployment Checklist

**Pre-Deployment:**
- [ ] Review and approve security architecture
- [ ] Complete security review/penetration testing
- [ ] Set up email and SMS delivery infrastructure
- [ ] Configure rate limiting (Redis)
- [ ] Set up monitoring and alerting
- [ ] Prepare documentation and training materials
- [ ] Configure backup and disaster recovery

**Deployment:**
- [ ] Run database migrations in staging
- [ ] Deploy backend API to staging
- [ ] Deploy frontend to staging
- [ ] Conduct end-to-end testing
- [ ] Load testing (simulated registration traffic)
- [ ] Security testing (attempt to bypass protections)

**Post-Deployment:**
- [ ] Monitor error rates and performance
- [ ] Review audit logs for anomalies
- [ ] Test failover mechanisms
- [ ] Validate email/SMS delivery rates
- [ ] Conduct security incident response drill

### Monitoring and Alerting

**Key Metrics to Monitor:**

1. **Registration Metrics:**
   - Registration initiation rate
   - Verification success rate
   - Linkage success rate
   - Time to complete registration

2. **Security Metrics:**
   - Failed login attempts (spikes indicate attacks)
   - Account lockouts
   - Suspicious activity detection triggers
   - MFA adoption rate

3. **Performance Metrics:**
   - API response times
   - Database query times
   - Email/SMS delivery latency
   - Session creation rate

4. **Business Metrics:**
   - Active patient accounts
   - Daily active users
   - Caregiver adoption
   - Feature usage patterns

**Alert Thresholds:**

- **Critical:** Error rate > 5%, database downtime, SMS delivery failure > 10%
- **Warning:** API latency > 1s, email delivery failure > 5%, unusual login patterns
- **Info:** New account milestones, feature usage changes

### Scaling Considerations

**Horizontal Scaling:**
- API servers: Stateless design allows horizontal scaling
- Session storage: Redis cluster for distributed session management
- Database: Read replicas for audit log queries

**Vertical Scaling:**
- Database connection pooling
- Caching frequently accessed data (patient records, security questions)
- Background job processing for email/SMS sending

**Caching Strategy:**
- Cache patient records for 5 minutes
- Cache security questions (static data)
- Do NOT cache authentication data (sessions, tokens)
- Invalidation on patient data updates

---

## Appendix

### A. Security Question Reference

Indonesian-localized security questions for account recovery:

1. "Siapa nama hewan peliharaan pertama Anda?" (What was the name of your first pet?)
2. "Di kota mana Anda dilahirkan?" (What city were you born in?)
3. "Apa nama gadis ibu Anda?" (What is your mother's maiden name?)
4. "Apa merek mobil pertama Anda?" (What was the make of your first car?)
5. "SD mana yang pernah Anda tinggali?" (What elementary school did you attend?)

### B. Error Message Reference (Indonesian)

| Error Code | English Message | Indonesian Message |
|------------|----------------|-------------------|
| INVALID_CREDENTIALS | Invalid email or password | Email atau kata sandi salah |
| ACCOUNT_LOCKED | Account locked due to too many failed attempts | Akun terkunci karena terlalu banyak percobaan gagal |
| WEAK_PASSWORD | Password does not meet security requirements | Kata sandi tidak memenuhi persyaratan keamanan |
| INVALID_VERIFICATION_CODE | Invalid or expired verification code | Kode verifikasi tidak valid atau kadaluarsa |
| PATIENT_NOT_FOUND | No matching patient record found | Tidak ditemukan rekam medis yang cocok |
| CAREGIVER_LIMIT_REACHED | Maximum number of caregivers reached | Jumlah pengampung maksimum telah tercapai |

### C. Email Templates

#### Verification Email (Indonesian)

```
Subject: Verifikasi Akun Portal Pasien SIMRS

Halo,

Terima kasih telah mendaftar untuk Portal Pasien SIMRS.

Kode verifikasi Anda: 123456

Kode ini akan kedaluwarsa dalam 15 menit.

Jika Anda tidak meminta kode ini, silakan abaikan email ini.

---
Hormat kami,
Tim SIMRS
Rumah Sakit [Nama Rumah Sakit]
```

#### Welcome Email (Indonesian)

```
Subject: Selamat Datang di Portal Pasien SIMRS

Halo Budi Santoso,

Selamat! Akun Portal Pasien Anda telah berhasil dibuat.

Dengan akun ini, Anda dapat:
- Melihat rekam medis Anda
- Mengelola janji temu
- Memeriksa resep dan obat
- Melihat tagihan dan pembayaran

Masuk ke: https://portal.hospital.com/login

Untuk keamanan, pertama kali Anda masuk akan diminta untuk menghubungkan akun
ke rekam medis Anda menggunakan NIK atau nomor kartu BPJS.

Jika Anda memiliki pertanyaan, hubungi kami di: support@hospital.com

---
Hormat kami,
Tim SIMRS
Rumah Sakit [Nama Rumah Sakit]
```

### D. SMS Templates

#### Verification SMS

```
SIMRS: Kode verifikasi Anda adalah 123456. Jangan bagikan kode ini kepada siapa pun. Kode kedaluwarsa dalam 10 menit.
```

#### Login Alert SMS

```
SIMRS: Login baru terdeteksi ke akun Portal Pasien Anda. Jika ini bukan Anda, segera ubah kata sandi atau hubungi kami.
```

### E. API Rate Limiting Headers

All rate-limited endpoints return these headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705288800
Retry-After: 3600
```

### F. Future Enhancements

**Phase 2 Features (Future):**
1. **SSO Integration:** Support for Indonesian national digital identity (electronic KTP)
2. **Biometric Authentication:** Fingerprint and face recognition for mobile apps
3. **Voice Authentication:** Voice print as additional MFA factor
4. **Blockchain Verification:** Immutable audit logs using blockchain technology
5. **AI Fraud Detection:** Machine learning models to detect anomalous access patterns
6. **Patient-Generated Data:** Integration with wearables and health apps
7. **Telehealth Integration:** Direct video consultation from portal
8. **Family Account Management:** Linked family accounts with hierarchical permissions

**Phase 3 Features (Future):**
1. **International Patients:** Support for international insurance and languages
2. **Health Data Export:** FHIR-compliant data export for patient portability
3. **Research Consent:** Opt-in for anonymized data research participation
4. **Digital Prescription Delivery:** Direct delivery to partner pharmacies
5. **AI Health Assistant:** Chatbot for basic health questions

---

## Document Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-15 | SIMRS Architecture Team | Initial architecture document |

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Chief Technology Officer | | | |
| Chief Information Security Officer | | | |
| Head of Medical Records | | | |
| Data Protection Officer | | | |
| Compliance Officer | | | |

---

**END OF DOCUMENT**
