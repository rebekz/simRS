# SIMRS QA Testing Command

Run comprehensive browser-based QA testing for SIMRS from multiple user perspectives.

## Usage

```bash
# Run all tests
/simrs-qa all

# Run specific role tests
/simrs-qa admin
/simrs-qa doctor
/simrs-qa nurse
/simrs-qa billing
/simrs-qa casemix
/simrs-qa pharmacy
/simrs-qa lab
/simrs-qa radiology
/simrs-qa portal
/simrs-qa finance

# Run specific scenario
/simrs-qa scenario ADMIN-001
/simrs-qa scenario DOCTOR-CONSULT-001

# Run with options
/simrs-qa admin --headed     # Watch browser
/simrs-qa admin --headless   # Background mode
/simrs-qa admin --report     # Generate report
```

## Arguments

- `$ARGUMENTS`: The test scope (role name, "all", or "scenario ID")
- Options:
  - `--headed`: Run in visible browser mode
  - `--headless`: Run in background (default)
  - `--report`: Generate detailed report after tests

## Workflow

1. Parse arguments to determine test scope
2. Load relevant test scenarios from `ai_review/user_stories/`
3. Initialize browser session
4. Execute test scenarios sequentially
5. Capture screenshots at each step
6. Log results (pass/fail)
7. Generate summary report

## Test Accounts

| Role | Username | Password |
|------|----------|----------|
| Super Admin | superadmin | SuperAdmin123! |
| Doctor | doctor1 | Doctor123! |
| Nurse | nurse1 | Nurse123! |
| Billing | billing1 | Billing123! |
| Casemix | casemix1 | Casemix123! |
| Pharmacy | pharmacist1 | Pharmacist123! |
| Lab Tech | labtech1 | LabTech123! |
| Radiology | radiology1 | Radiology123! |
| Finance | finance1 | Finance123! |
| Patient Portal | patient@example.com | Patient123! |

## Output

- Screenshots saved to `ai_review/screenshots/{role}/`
- Test report saved to `ai_review/reports/{date}-qa-report.md`

---

Execute the QA tests based on the arguments provided.

**Scope**: $ARGUMENTS

**Instructions**:

1. If scope is "all", run all role-based test suites in parallel using subagents
2. If scope is a role name, run tests from the corresponding YAML file
3. If scope is a scenario ID, run only that specific scenario
4. Use agent-browser CLI for browser automation
5. Capture screenshots at each verification step
6. Generate a summary report at the end
