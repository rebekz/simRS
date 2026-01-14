# SIMRS Web Application Epics

**Project:** SIMRS (Sistem Informasi Manajemen Rumah Sakit) - Web Frontend
**Date:** 2026-01-13
**Version:** 2.0 - Web-Specific Epics
**Tech Stack:** Next.js 15 + React 19 + TypeScript + TailwindCSS
**Backend:** FastAPI (Python)

---

## EPIC OVERVIEW

This document defines **5 epics** for the SIMRS web application frontend, organized by priority and dependencies. These epics leverage the new enhanced SIMRS component library created from Indonesian healthcare UX research.

| Epic ID | Epic Name | Stories | Priority | Duration | Dependencies |
|---------|-----------|---------|----------|----------|--------------|
| WEB-EPIC-1 | Component Library Foundation | 9 | CRITICAL | 2 weeks | None |
| WEB-EPIC-2 | BPJS Integration Suite | 5 | HIGH | 2 weeks | WEB-EPIC-1 |
| WEB-EPIC-3 | Patient Registration Redesign | 7 | HIGH | 2 weeks | WEB-EPIC-1, WEB-EPIC-2 |
| WEB-EPIC-4 | Doctor Consultation Workspace | 7 | MEDIUM | 2 weeks | WEB-EPIC-1, WEB-EPIC-3 |
| WEB-EPIC-5 | Emergency Triage System | 6 | CRITICAL | 1 week | WEB-EPIC-1 |

**Total:** 34 stories across 5 epics
**Total Timeline:** ~9 weeks to full MVP

---

## EPIC STRATEGY

### Design Philosophy: "Warm Professionalism"

Based on Indonesian SIMRS UX research (TeraMedik, Nextmedis, SIMRS-Khanza):
- **Medical Teal** (#0d9488) - Trust + Warmth
- **Coral** (#f97316) - Urgency without harsh red
- **BPJS Brand Colors** - Reflecting 78% patient reality
- **Role-Based Interfaces** - Optimized per user type
- **Minimal Click Philosophy** - 3-click max for common tasks
- **Offline-First** - For 22% Puskesmas with limited connectivity

### Target Deployment

**Primary:** RSUD (Rumah Sakit Umum Daerah) - Regional hospitals
**Secondary:** Puskesmas (Community health centers)
**Tertiary:** Private clinics

### MVP Strategy

**Modular incremental delivery:**
1. **Sprint 1:** Foundation (Component Library) - ALL modules depend on this
2. **Sprint 2:** BPJS + Registration (Patient-facing) - First user journey
3. **Sprint 3:** Doctor Workspace (Clinical) - Core clinical workflow
4. **Sprint 4:** Emergency Triage (Critical) - Life-saving workflows

---

## WEB-EPIC-1: Component Library Foundation

**Priority:** CRITICAL (BLOCKER)
**Duration:** 2 weeks
**Stories:** 9
**Dependencies:** None

### Business Value

The component library provides:
- **Consistent UI language** across all modules
- **Faster development** - reusable components
- **Design system documentation** - Storybook for developers
- **Accessibility compliance** - WCAG 2.1 AA
- **Indonesian localization** - Built-in fonts, colors, formats

### Epic Goal

Establish the foundational design system that all other epics depend on. Integrate the enhanced SIMRS component CSS (4000+ lines) into the Next.js application with proper TypeScript typing, Storybook documentation, and comprehensive testing.

### Success Criteria

- [ ] All components integrated into Next.js
- [ ] Storybook deployed with interactive examples
- [ ] 100% WCAG 2.1 AA compliance
- [ ] Mobile responsive (375px - 1440px)
- [ ] Unit test coverage >80%
- [ ] Visual regression tests passing
- [ ] Zero console errors/warnings

### Stories

| Story ID | Story Name | Focus |
|----------|------------|-------|
| WEB-S-1.1 | Design System Integration | CSS import, Tailwind config, fonts |
| WEB-S-1.2 | Base Layout Structure | Sidebar, Topbar, Layout wrapper |
| WEB-S-1.3 | Button Components | All variants, sizes, states |
| WEB-S-1.4 | Form Components | Inputs, selects, checkboxes, switches |
| WEB-S-1.5 | Card & Badge Components | Patient cards, BPJS badges, triage badges |
| WEB-S-1.6 | Alert & Notification Components | All alert types, toast system |
| WEB-S-1.7 | Table & Modal Components | Sortable tables, paginated, modals |
| WEB-S-1.8 | Storybook Documentation | Component stories, controls |
| WEB-S-1.9 | Component Usage Guidelines | When/how to use each component |

### Technical Notes

**Component Location:**
- `src/components/ui/` - Reusable UI components
- `src/components/layout/` - Layout components (Sidebar, Topbar)
- `src/app/globals.css` - Enhanced SIMRS components CSS import

**Dependencies to Add:**
```json
{
  "@storybook/react": "^8.0.0",
  "@storybook/addon-essentials": "^8.0.0",
  "@storybook/testing-library": "^0.2.0",
  "@testing-library/react": "^14.0.0",
  "@testing-library/user-event": "^14.0.0"
}
```

---

## WEB-EPIC-2: BPJS Integration Suite

**Priority:** HIGH
**Duration:** 2 weeks
**Stories:** 5
**Dependencies:** WEB-EPIC-1

### Business Value

BPJS (Badan Penyelenggara Jaminan Sosial) integration is CRITICAL because:
- **78% of Indonesian patients** use BPJS
- **Hospital revenue** depends on proper BPJS claims
- **Patient experience** - eligibility must be verified upfront
- **Regulatory compliance** - SEP (Surat Eligibility Peserta) mandatory

### Epic Goal

Implement a complete BPJS integration layer that provides real-time eligibility verification, SEP creation wizard, and status indicators throughout the application. Build frontend with mock data first, then integrate real BPJS VClaim API.

### Success Criteria

- [ ] BPJS card verification works with mock data
- [ ] BPJS VClaim API integrated (backend endpoints)
- [ ] SEP creation wizard complete with all steps
- [ ] Real-time status indicators working
- [ ] Error handling user-friendly (not API codes)
- [ ] BPJS interactions audited (existing audit log)
- [ ] Rate limiting implemented (BPJS API limits)

### Stories

| Story ID | Story Name | Focus |
|----------|------------|-------|
| WEB-S-2.1 | BPJS Eligibility Check | Real-time verification, auto-fill |
| WEB-S-2.2 | BPJS SEP Creation Wizard | Multi-step wizard (5 steps) |
| WEB-S-2.3 | BPJS Status Indicators | Badges, real-time updates |
| WEB-S-2.4 | BPJS Error Handling | User-friendly errors, retry |
| WEB-S-2.5 | BPJS History & Audit | Admin logs, success rates |

### Technical Architecture

**Backend Endpoints (to be built):**
```python
GET  /api/v1/bpjs/eligibility/{card_number}
POST /api/v1/bpjs/sep
GET  /api/v1/bpjs/rujukan/{rujukan_number}
GET  /api/v1/bpjs/history
```

**Frontend Components:**
- `BPJSVerificationCard` - Verification UI
- `SEPWizard` - Multi-step modal
- `BPJSBadge` - Status indicator
- `useBPJSEligibility` - React hook for polling

**Security:**
- BPJS API credentials in environment
- Request signing (BPJS requirement)
- Rate limiting (strict BPJS limits)
- All BPJS calls audited

---

## WEB-EPIC-3: Patient Registration Redesign

**Priority:** HIGH
**Duration:** 2 weeks
**Stories:** 7
**Dependencies:** WEB-EPIC-1, WEB-EPIC-2

### Business Value

Patient registration is the **FIRST touchpoint** for all patients. Key metrics:
- **3-click max** for common tasks (research finding)
- **<30 seconds** for returning patient check-in
- **60% faster** with BPJS-first design (auto-fill)
- **Queue management** reduces patient wait times

### Epic Goal

Create a streamlined, BPJS-first patient registration experience that minimizes clicks and wait times. Include new registration, quick check-in, queue management, digital display screens, online booking, and powerful search.

### Success Criteria

- [ ] New patient registration in ≤5 clicks (BPJS-first)
- [ ] Returning patient check-in in <30 seconds
- [ ] Queue dashboard shows real-time status
- [ ] Digital queue display screens working
- [ ] Online booking functional (SMS notifications)
- [ ] Patient search <5 seconds (fuzzy matching)
- [ ] Mobile responsive for tablet registration

### Stories

| Story ID | Story Name | Focus |
|----------|------------|-------|
| WEB-S-3.1 | BPJS-First New Patient Registration | Auto-fill from BPJS, <5 clicks |
| WEB-S-3.2 | Returning Patient Quick Check-In | <30 seconds, Ctrl+K shortcut |
| WEB-S-3.3 | Queue Management Dashboard | Real-time, department-wise |
| WEB-S-3.4 | Digital Queue Display Screens | TV-optimized, auto-refresh |
| WEB-S-3.5 | Online Appointment Booking | Public-facing, SMS alerts |
| WEB-S-3.6 | Patient Search & Lookup | Fuzzy search, multiple filters |
| WEB-S-3.7 | Mobile Responsive Registration | Tablet-optimized, offline support |

### User Journey

**New Patient (BPJS):**
1. Enter BPJS card number → Verify
2. Auto-fill data → Confirm/Edit
3. Add photo, emergency contact
4. Select department → Get queue number
5. **Total: ~2 minutes**

**Returning Patient:**
1. Search (Ctrl+K) → Select patient
2. Verify BPJS (auto) → Select department
3. Get queue number
4. **Total: ~20 seconds**

---

## WEB-EPIC-4: Doctor Consultation Workspace

**Priority:** MEDIUM
**Duration:** 2 weeks
**Stories:** 7
**Dependencies:** WEB-EPIC-1, WEB-EPIC-3

### Business Value

Doctors spend **80% of their time** in the consultation workspace. Key requirements:
- **Patient context always visible** (split-view design)
- **Minimal documentation burden** (SOAP templates, auto-save)
- **Quick diagnosis entry** (ICD-10 search)
- **Safe prescribing** (interaction checking)
- **Efficient ordering** (lab/radiology)

### Epic Goal

Build a split-view consultation workspace that keeps patient context always visible while enabling efficient clinical documentation, diagnosis, prescribing, and ordering. Implement SOAP notes with ICD-10 integration, electronic prescribing with interaction checking, and lab/radiology ordering.

### Success Criteria

- [ ] Split-view layout (patient context left, work right)
- [ ] SOAP notes editor with auto-save (30s)
- [ ] ICD-10 diagnosis search (<2 seconds)
- [ ] Electronic prescribing with interaction checking
- [ ] Lab/radiology ordering with test catalog
- [ ] Patient history timeline visualized
- [ ] Allergy/medication alerts prominent

### Stories

| Story ID | Story Name | Focus |
|----------|------------|-------|
| WEB-S-4.1 | Split-View Patient Context | Always-visible patient panel |
| WEB-S-4.2 | SOAP Notes Editor | Auto-save, templates |
| WEB-S-4.3 | ICD-10 Diagnosis Search | Autocomplete, favorites |
| WEB-S-4.4 | Electronic Prescription Writer | Drug search, dose, interactions |
| WEB-S-4.5 | Lab/Radiology Ordering | Test catalog, priority |
| WEB-S-4.6 | Patient History Timeline | Visual medical history |
| WEB-S-4.7 | Allergy & Medication Alerts | Critical safety alerts |

### Technical Architecture

**Split-View Layout:**
```tsx
<div className="consultation-workspace">
  <aside className="patient-context-panel">
    {/* Always visible - patient info, alerts, vitals */}
  </aside>
  <main className="consultation-main">
    {/* SOAP, prescriptions, orders */}
  </main>
</div>
```

**Key Components:**
- `PatientContextPanel` - Left sidebar
- `SOAPNotesEditor` - Clinical documentation
- `DiagnosisSearch` - ICD-10 with autocomplete
- `PrescriptionWriter` - Drug search + interactions
- `OrderForm` - Lab/radiology orders

**React Hooks:**
- `usePatientContext` - Fetch/manage patient data
- `useAutoSave` - Auto-save SOAP notes
- `useDiagnosisSearch` - ICD-10 search debounce
- `useDrugInteractions` - Check interactions

---

## WEB-EPIC-5: Emergency Triage System

**Priority:** CRITICAL (LIFE-SAVING)
**Duration:** 1 week
**Stories:** 6
**Dependencies:** WEB-EPIC-1

### Business Value

Emergency department (IGD) triage is **LIFE-SAVING critical**:
- **Triage must complete in <2 minutes** (research finding)
- **Color-coded system** (Merah/Kuning/Hijau) for rapid assessment
- **Auto-calculate** from vitals reduces errors
- **Emergency activation** (Kode Biru) must be prominent

### Epic Goal

Implement a rapid triage interface that enables <2 minute patient assessment with auto-calculated triage categories, one-tap chief complaints, and prominent emergency activation buttons.

### Success Criteria

- [ ] Triage completes in <2 minutes
- [ ] Auto-calculate triage from vitals (Merah/Kuning/Hijau)
- [ ] One-tap chief complaint quick-tags
- [ ] Triage result displayed with color-coded cards
- [ ] Emergency activation (Kode Biru) prominent
- [ ] Triage timer visible throughout
- [ ] Recommendations displayed per triage level

### Stories

| Story ID | Story Name | Focus |
|----------|------------|-------|
| WEB-S-5.1 | Rapid Vitals Entry | Compact form, <1 minute |
| WEB-S-5.2 | Chief Complaint Quick-Tags | One-tap common complaints |
| WEB-S-5.3 | Auto-Calculate Triage | Algorithm → Merah/Kuning/Hijau |
| WEB-S-5.4 | Triage Result Display | Color-coded, recommendations |
| WEB-S-5.5 | Emergency Activation | Kode Biru button, alerts |
| WEB-S-5.6 | Triage Timer | Prominent <2 minute timer |

### Triage Algorithm (Simplified)

```javascript
function calculateTriage(vitals) {
  let score = 0;

  if (vitals.bpSys < 90 || vitals.bpDia < 60) score += 3;
  if (vitals.pulse > 120 || vitals.pulse < 50) score += 2;
  if (vitals.rr > 24 || vitals.rr < 10) score += 2;
  if (vitals.spo2 < 90) score += 3;
  if (vitals.gcs < 14) score += 2;

  if (score >= 5) return 'MERAH';      // Gawat Darurat
  if (score >= 3) return 'KUNING';     // Semi-Urgent
  return 'HIJAU';                      // Non-Urgent
}
```

---

## IMPLEMENTATION ROADMAP

### Sprint 1: Foundation (Weeks 1-2)

**Epic:** WEB-EPIC-1 - Component Library Foundation
**Goal:** Establish design system, all modules depend on this
**Deliverables:**
- All 9 component stories completed
- Storybook deployed at :6006
- Component usage guide documented

**Definition of Done:**
- All components TypeScript-typed
- Unit tests passing (>80% coverage)
- Visual regression tests passing
- Mobile responsive validated
- Zero console errors

### Sprint 2: BPJS + Registration (Weeks 3-4)

**Epics:** WEB-EPIC-2 + WEB-EPIC-3 (parallel start)
**Goal:** Complete patient-facing journey
**Deliverables:**
- BPJS eligibility verification working
- SEP creation wizard functional
- New patient registration BPJS-first
- Quick check-in <30 seconds
- Queue dashboard real-time

**Definition of Done:**
- Mock data UI working
- BPJS API integrated
- Error scenarios tested
- Audit logging confirmed

### Sprint 3: Doctor Workspace (Weeks 5-6)

**Epic:** WEB-EPIC-4 - Doctor Consultation Workspace
**Goal:** Core clinical workflow
**Deliverables:**
- Split-view layout implemented
- SOAP notes with auto-save
- ICD-10 diagnosis search
- Electronic prescribing
- Lab/radiology ordering

**Definition of Done:**
- Patient context always visible
- Auto-save working (30s interval)
- Drug interaction checking functional
- Allergy alerts prominent

### Sprint 4: Emergency Triage (Weeks 7-8)

**Epic:** WEB-EPIC-5 - Emergency Triage System
**Goal:** Life-saving rapid assessment
**Deliverables:**
- Triage completes in <2 minutes
- Auto-calculate triage working
- Color-coded result display
- Emergency activation functional

**Definition of Done:**
- Triage algorithm validated
- Timer prominent throughout
- Kode Biru alerts working
- Medical review completed

### Sprint 5: Integration & Polish (Week 9)

**Goal:** End-to-end testing, bug fixes, deployment
**Deliverables:**
- All epics integrated
- E2E tests passing (Playwright)
- Performance optimized (<2s page loads)
- Security audit passed
- Production deployment ready

---

## CROSS-EPIC CONSIDERATIONS

### Accessibility (WCAG 2.1 AA)

All epics must comply with:
- [ ] Keyboard navigation (Tab, Enter, Escape)
- [ ] Screen reader support (ARIA labels)
- [ ] Color contrast ratio ≥4.5:1
- [ ] Focus visible indicators
- [ ] Error messages announced

### Performance Targets

- [ ] Initial page load: <2 seconds
- [ ] Time to interactive: <3 seconds
- [ ] First contentful paint: <1 second
- [ ] API response: <500ms (p95)

### Security Requirements

- [ ] All forms CSRF protected
- [ ] XSS prevention (React default + sanitization)
- [ ] Authentication on all pages
- [ ] Authorization checked per-component
- [ ] Audit logging for all data mutations

### Offline Support

For 22% Puskesmas with limited connectivity:
- [ ] Service worker for offline caching
- [ ] Queue actions when offline
- [ ] Sync when connection restored
- [ ] Clear offline/online indicators

### Indonesian Localization

- [ ] Date format: DD-MM-YYYY
- [ ] Currency: IDR (Rp 1.000.000)
- [ ] Language: Bahasa Indonesia (primary), English (secondary)
- [ ] ICD-10: Indonesian diagnosis names
- [ ] BPJS terms: Peserta, Faskes, SEP, Rujukan

---

## DEPENDENCIES

### Existing Backend Work (Completed)

These backend stories from previous sprints support the web epics:

| Story | Description | Web Epic Usage |
|-------|-------------|----------------|
| ST-002 | User Authentication & Authorization | All epics (auth, RBAC) |
| ST-003 | Audit Logging System | All epics (audit trail) |
| ST-004 | Automated Backup System | All epics (data safety) |
| ST-005 | System Monitoring & Alerting | All epics (observability) |

### Backend Work Needed (New)

These backend endpoints need to be built to support web epics:

| Endpoint | Method | Description | Epic |
|----------|--------|-------------|------|
| `/api/v1/bpjs/eligibility/{card_number}` | GET | BPJS eligibility check | WEB-EPIC-2 |
| `/api/v1/bpjs/sep` | POST | Create SEP | WEB-EPIC-2 |
| `/api/v1/bpjs/rujukan/{rujukan_number}` | GET | Fetch rujukan | WEB-EPIC-2 |
| `/api/v1/patients` | POST | Create patient | WEB-EPIC-3 |
| `/api/v1/patients/search` | GET | Search patients | WEB-EPIC-3 |
| `/api/v1/encounters` | POST | Start encounter | WEB-EPIC-3,4 |
| `/api/v1/diagnosis/search` | GET | ICD-10 search | WEB-EPIC-4 |
| `/api/v1/prescriptions` | POST | Create prescription | WEB-EPIC-4 |
| `/api/v1/triage` | POST | Create triage | WEB-EPIC-5 |

---

## TESTING STRATEGY

### Unit Tests (Jest + React Testing Library)

- Component rendering
- User interactions
- Hook behavior
- Utility functions

**Target:** >80% coverage

### Integration Tests (React Testing Library)

- Multi-component workflows
- Form submissions
- API mocking (MSW - Mock Service Worker)

### Visual Regression Tests (Chromatic)

- Component screenshots
- Cross-browser consistency
- Theme variations

### E2E Tests (Playwright)

- Complete user journeys
- Critical paths (registration, consultation)
- Cross-browser testing (Chrome, Firefox, Safari)

---

## DOCUMENTATION

### Component Documentation (Storybook)

- Live examples of all components
- Interactive props table
- Usage guidelines
- Accessibility notes

**URL:** http://localhost:6006

### API Documentation (OpenAPI/Swagger)

- All backend endpoints documented
- Request/response schemas
- Authentication requirements
- Error response formats

**URL:** http://localhost:8000/docs

### User Documentation (Markdown)

- Admin guides
- Training materials
- Video tutorials (TODO)

---

## METRICS & SUCCESS

### Development Metrics

- [ ] Velocity: Stories completed per sprint
- [ ] Cycle time: Story start → finish
- [ ] Defect rate: Bugs found post-release
- [ ] Test coverage: Unit + integration

### User Experience Metrics

- [ ] Task completion time (registration <2 min)
- [ ] Error rate (failed forms, API errors)
- [ ] User satisfaction (surveys)
- [ ] Adoption rate (active users)

### Technical Metrics

- [ ] Page load time: <2s (p95)
- [ ] API response time: <500ms (p95)
- [ ] Error rate: <0.1%
- [ ] Uptime: >99.9%

---

## CHANGELOG

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-01-13 | Initial web epics created from party mode discussion |
| 1.0 | 2026-01-12 | Original PRD/Architecture epics (backend-focused) |

---

## NEXT STEPS

1. ✅ Epics defined (this document)
2. ⏭️ Write detailed stories (see `web-stories.md`)
3. ⏭️ Create Sprint 1 backlog (WEB-EPIC-1 stories)
4. ⏭️ Set up Storybook for Epic 1
5. ⏭️ Begin implementation with Amelia (Dev)

---

**Document Status:** ✅ COMPLETE
**Next:** `web-stories.md` - Detailed story documentation with acceptance criteria
