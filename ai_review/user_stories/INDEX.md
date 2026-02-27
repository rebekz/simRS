# SIMRS QA Test Scenarios Index

## Overview

This directory contains comprehensive browser-based QA test scenarios for the SIMRS (Sistem Informasi Manajemen Rumah Sakit) application.

## Test Scenario Files

| File | Role | Priority | Scenarios |
|------|------|----------|-----------|
| [01-admin.yaml](./01-admin.yaml) | Administrator | Critical | User management, audit logs, system settings |
| [02-doctor.yaml](./02-doctor.yaml) | Doctor | Critical | Consultations, prescriptions, lab orders, medical records |
| [03-nurse.yaml](./03-nurse.yaml) | Nurse | High | Patient care, vitals, admission, discharge, queue management |
| [04-billing.yaml](./04-billing.yaml) | Billing Staff | Critical | Invoice management, payment processing, BPJS/Insurance billing |
| [05-casemix.yaml](./05-casemix.yaml) | Casemix/Coder | Critical | ICD-10 coding, INA-CBG grouping, BPJS claims, SEP management |
| [06-pharmacy.yaml](./06-pharmacy.yaml) | Pharmacist | High | Prescription processing, dispensing, inventory |
| [07-laboratory.yaml](./07-laboratory.yaml) | Lab Technician | Critical | Lab orders, results entry, report verification |
| [08-radiology.yaml](./08-radiology.yaml) | Radiology Tech | High | Radiology orders, image upload, report entry |
| [09-patient-portal.yaml](./09-patient-portal.yaml) | Patient | High | Registration, appointments, medical records, billing |
| [10-finance.yaml](./10-finance.yaml) | Finance Staff | High | Revenue reports, reconciliation, cash flow |

## Test Statistics

| Category | Total Scenarios |
|----------|-----------------|
| Authentication | 10 |
| Patient Management | 15 |
| Clinical Workflows | 30 |
| Administrative | 12 |
| Financial/Billing | 20 |
| Casemix/BPJS | 15 |
| Patient Portal | 25 |
| **Total** | **127+** |

## Running Tests

### Using the Command

```bash
# Run all tests
/simrs-qa all

# Run specific role tests
/simrs-qa admin
/simrs-qa doctor
/simrs-qa billing

# Run specific scenario
/simrs-qa scenario ADMIN-001
```

### Using the Skill

```bash
# Initialize browser testing
/simrs-qa

# Run with visible browser
/simrs-qa admin --headed
```

## Test Accounts

| Role | Username | Password | Notes |
|------|----------|----------|-------|
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
| Patient Portal | patient@example.com | Patient123! | Self-service access |

## Scenario Format

Each scenario follows this structure:

```yaml
- id: ROLE-CATEGORY-001
  title: "Scenario Title"
  category: Category Name
  priority: critical|high|medium|low
  tags: [tag1, tag2, tag3]
  preconditions: [OTHER-SCENARIO-ID]
  steps:
    - action: navigate|fill|click|verify|wait|screenshot|select|upload
      target: "CSS selector"
      value: "Value to fill/select"
      description: "Human-readable description"
```

## Action Types

| Action | Description | Required Fields |
|--------|-------------|-----------------|
| `navigate` | Go to URL | `target` (URL) |
| `fill` | Fill input field | `target`, `value` |
| `click` | Click element | `target` |
| `select` | Select dropdown option | `target`, `value` |
| `verify` | Check content/elements | `target`, `expect_contains` |
| `wait` | Pause execution | `duration` (ms) |
| `screenshot` | Capture screenshot | `filename` |
| `upload` | Upload file | `target`, `file` |

## Output Locations

- **Screenshots**: `ai_review/screenshots/{role}/`
- **Reports**: `ai_review/reports/`
- **Logs**: `ai_review/logs/`

## Integration with Bowser

These scenarios follow the Bowser architecture pattern:
- **Layer 1**: Browser automation via agent-browser CLI
- **Layer 2**: QA agents execute scenarios in isolation
- **Layer 3**: `/simrs-qa` command orchestrates test runs
- **Layer 4**: Justfile recipes for CI/CD integration

## Contributing

To add new test scenarios:

1. Identify the appropriate role file (or create new one)
2. Add scenario with unique ID following the pattern `ROLE-CATEGORY-NNN`
3. Include all required fields
4. Test manually before committing
5. Update this index with new scenario count
