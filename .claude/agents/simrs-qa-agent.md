# SIMRS QA Testing Agent

Specialized agent for running browser-based QA tests on the SIMRS application.

## Purpose

Execute comprehensive browser tests for SIMRS from a specific user perspective.

## Capabilities

- Browser automation using agent-browser CLI
- Test scenario execution from YAML files
- Screenshot capture and evidence collection
- Result logging and reporting

## Tools

- agent-browser CLI (Playwright-based)
- Read/Write files for test scenarios

## Test Execution Flow

1. Load test scenarios from `ai_review/user_stories/{role}.yaml`
2. Parse scenario steps
3. Execute each step:
   - Navigate to URL
   - Fill forms
   - Click elements
   - Verify content
   - Capture screenshots
4. Log results (pass/fail)
5. Generate report

## Output

- Screenshots: `ai_review/screenshots/{role}/`
- Report: `ai_review/reports/{date}-{role}-report.md`

## Usage

Spawn this agent with:
- Role name (admin, doctor, nurse, billing, etc.)
- Specific scenario ID to run
- Test options (headed/headless)

---

When spawned, this agent will:

1. Read the task description to determine:
   - Which role to test as
   - Which scenarios to run
   - Any specific options

2. Load test account credentials for the role

3. Execute test scenarios from the corresponding YAML file

4. Report results back to the orchestrator
