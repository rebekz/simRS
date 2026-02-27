# SIMRS QA Testing Skill

Comprehensive browser-based QA testing for SIMRS (Sistem Informasi Manajemen Rumah Sakit) - Hospital Information Management System.

## Overview

This skill provides structured browser testing for all SIMRS functionalities from multiple user perspectives including:
- **Administrator** - System administration and user management
- **Doctor** - Clinical consultations and medical records
- **Nurse** - Patient care and vitals monitoring
- **Pharmacist** - Prescription management and dispensing
- **Laboratory** - Lab orders and results
- **Radiology** - Imaging orders and results
- **Casemix** - BPJS coding and INA-CBG classification
- **Finance** - Financial reporting and reconciliation
- **Billing** - Invoice creation and payment processing
- **Registration** - Patient registration and check-in
- **Patient Portal** - Patient self-service access

## Prerequisites

```bash
# Ensure agent-browser is installed
command -v agent-browser >/dev/null 2>&1 || npm install -g agent-browser

# Ensure SIMRS services are running
docker ps | grep simrs
```

## Test Accounts

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Super Admin | superadmin | SuperAdmin123! | Full system access |
| Admin | admin | Admin123! | Administrative access |
| Doctor | doctor1 | Doctor123! | Clinical access |
| Nurse | nurse1 | Nurse123! | Nursing access |
| Pharmacist | pharmacist1 | Pharmacist123! | Pharmacy access |
| Lab Tech | labtech1 | LabTech123! | Laboratory access |
| Radiology | radiology1 | Radiology123! | Radiology access |
| Casemix | casemix1 | Casemix123! | Coding access |
| Finance | finance1 | Finance123! | Financial access |
| Billing | billing1 | Billing123! | Billing access |
| Registration | registration1 | Registration123! | Registration access |

## Commands

### Run All Tests
```bash
# Run comprehensive QA suite
agent-browser open "http://localhost:3000" --test-suite=all
```

### Run by Role
```bash
# Admin tests
/simrs-qa admin

# Doctor tests
/simrs-qa doctor

# Billing tests
/simrs-qa billing

# Patient portal tests
/simrs-qa portal
```

### Run Specific Scenario
```bash
/simrs-qa scenario AUTH-001
/simrs-qa scenario PATIENT-001
/simrs-qa scenario BILLING-001
```

## Test Categories

### 1. Authentication (AUTH-*)
- Login/logout flows
- Session management
- Password reset
- MFA setup
- Role-based access control

### 2. Patient Management (PATIENT-*)
- Patient registration
- Patient search
- Medical records
- Patient history
- BPJS verification

### 3. Clinical Workflows (CLINICAL-*)
- Consultations
- Prescriptions
- Lab orders
- Radiology orders
- Medical certificates

### 4. Administrative (ADMIN-*)
- User management
- Role assignment
- Audit logs
- System settings

### 5. Financial (FINANCE-*, BILLING-*)
- Invoice creation
- Payment processing
- Insurance claims
- BPJS billing
- Financial reports

### 6. Casemix (CASEMIX-*)
- ICD-10 coding
- INA-CBG grouping
- BPJS claim submission
- Code validation

### 7. Patient Portal (PORTAL-*)
- Patient login
- Appointment booking
- Medical records view
- Prescription refill requests
- Bill payment

## Workflow

1. **Initialize Test Session**
   - Start browser
   - Navigate to SIMRS
   - Verify application is accessible

2. **Execute Test Scenario**
   - Login as appropriate role
   - Navigate to target page
   - Perform test actions
   - Verify results
   - Capture screenshots

3. **Report Results**
   - Log pass/fail status
   - Capture evidence
   - Document issues

4. **Cleanup**
   - Logout
   - Close browser session

## Screenshot Storage

Screenshots are saved to:
```
ai_review/screenshots/
├── admin/
├── doctor/
├── nurse/
├── pharmacy/
├── laboratory/
├── radiology/
├── casemix/
├── finance/
├── billing/
├── registration/
└── portal/
```

## Integration with Bowser

This skill follows the Bowser architecture pattern:
- **Layer 1 (Skill):** Browser automation via agent-browser CLI
- **Layer 2 (Subagent):** Parallel test execution by role
- **Layer 3 (Command):** Orchestration of test suites
- **Layer 4 (Justfile):** One-command test execution

## Example Usage

```bash
# Quick smoke test
/simrs-qa smoke

# Full regression
/simrs-qa regression

# Role-specific tests
/simrs-qa admin --headed
/simrs-qa doctor --headed
/simrs-qa billing --headed

# Generate report
/simrs-qa report
```
