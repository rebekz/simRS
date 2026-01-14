# SIMRS Web Application Stories

**Project:** SIMRS (Sistem Informasi Manajemen Rumah Sakit) - Web Frontend
**Date:** 2026-01-13
**Version:** 2.0 - Web-Specific Stories
**Tech Stack:** Next.js 15 + React 19 + TypeScript + TailwindCSS
**Backend:** FastAPI (Python)

---

## STORY OVERVIEW

This document contains **34 developer-ready stories** organized by epic. Each story includes:
- User story format (As a... I want... So that...)
- Detailed acceptance criteria with AC IDs
- Technical implementation notes
- Testing requirements
- Definition of done

**Total Stories:** 34 across 5 epics
**Estimated Duration:** 9 weeks to MVP

---

## WEB-EPIC-1: COMPONENT LIBRARY FOUNDATION STORIES

---

### WEB-S-1.1: Design System Integration

**As a** developer,
**I want to** integrate the enhanced SIMRS component library into Next.js,
**So that** all pages share consistent styling and design tokens.

**Priority:** CRITICAL
**Estimate:** 2 days
**Dependencies:** None

---

#### Acceptance Criteria

**AC-1.1.1:** Import enhanced-simrs-components.css in globals.css
```css
/* src/app/globals.css */
@import '../styles/enhanced-simrs-components.css';
```

**AC-1.1.2:** CSS variables (design tokens) accessible via Tailwind config

```javascript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        // Map CSS variables to Tailwind
        primary: 'var(--simrs-primary-600)',
        coral: 'var(--simrs-coral-500)',
        // ... all design tokens
      }
    }
  }
}
```

**AC-1.1.3:** Plus Jakarta Sans font configured in next.config.js

```javascript
// next.config.js
module.exports = {
  fonts: {
    sans: ['Plus Jakarta Sans', 'sans-serif'],
    mono: ['IBM Plex Mono', 'monospace'],
  }
}
```

**AC-1.1.4:** Color palette working (medical-teal, coral, BPJS colors)
- Primary: #0d9488 (medical teal)
- Coral: #f97316
- BPJS Blue: #1e3a8a
- Triage Merah: #dc2626
- Triage Kuning: #f59e0b
- Triage Hijau: #059669

**AC-1.1.5:** All utility classes responsive (mobile/tablet/desktop)
- Test at 375px (mobile)
- Test at 768px (tablet)
- Test at 1024px (desktop)
- Test at 1440px (large desktop)

---

#### Technical Implementation

**Files to Modify:**
- `src/app/globals.css` - Import component CSS
- `tailwind.config.ts` - Extend theme with CSS variables
- `next.config.js` - Font configuration
- `src/app/layout.tsx` - Root layout with fonts

**CSS Variables to Map:**
```css
:root {
  --simrs-primary-600: #0d9488;
  --simrs-coral-500: #f97316;
  --bpjs-blue: #1e3a8a;
  /* ... all design tokens */
}
```

---

#### Testing

**Unit Tests:**
- [ ] CSS variables accessible in component
- [ ] Tailwind classes use design tokens
- [ ] Font loads correctly

**Visual Tests:**
- [ ] Color swatches match design
- [ ] Responsive breakpoints work

---

#### Definition of Done

- [x] AC-1.1.1: CSS imported
- [x] AC-1.1.2: Tailwind config updated
- [x] AC-1.1.3: Fonts configured
- [x] AC-1.1.4: Colors working
- [x] AC-1.1.5: Responsive classes working
- [ ] No console errors about missing CSS
- [ ] Fonts loading without flash

---

### WEB-S-1.2: Base Layout Structure

**As a** developer,
**I want to** create base layout components (sidebar, topbar),
**So that** every page has consistent navigation.

**Priority:** CRITICAL
**Estimate:** 3 days
**Dependencies:** WEB-S-1.1

---

#### Acceptance Criteria

**AC-1.2.1:** Sidebar component with role-based menu items
```tsx
<Sidebar>
  <Logo />
  <NavSection title="Menu Utama">
    <NavItem icon="dashboard" label="Dashboard" href="/" />
    <NavItem icon="patients" label="Pasien" href="/patients" />
    {/* Role-based items shown based on user.role */}
  </NavSection>
</Sidebar>
```

**AC-1.2.2:** Topbar component with user avatar and search
```tsx
<Topbar>
  <SearchBar placeholder="Cari pasien... (Ctrl+K)" />
  <NotificationBell />
  <UserAvatar name="Dr. Budi" />
</Topbar>
```

**AC-1.2.3:** Mobile-responsive hamburger menu
- Sidebar hidden on mobile (<768px)
- Hamburger button in topbar
- Slide-in drawer on mobile
- Backdrop overlay
- Close on escape or backdrop click

**AC-1.2.4:** Layout component wrapping sidebar + topbar + content
```tsx
<Layout>
  <Sidebar />
  <div className="main">
    <Topbar />
    <main>{children}</main>
  </div>
</Layout>
```

**AC-1.2.5:** Active route highlighting in sidebar
- Current route highlighted with background
- Parent routes expanded when child active
- Breadcrumb navigation

---

#### Technical Implementation

**Component Structure:**
```
src/components/layout/
├── Layout.tsx          # Main layout wrapper
├── Sidebar.tsx         # Left navigation
├── Topbar.tsx          # Top header
├── NavSection.tsx      # Navigation section
├── NavItem.tsx         # Navigation item
├── SearchBar.tsx       # Global search
└── UserAvatar.tsx      # User menu
```

**Props Interfaces:**
```typescript
interface SidebarProps {
  role: UserRole;
  menuItems: MenuItem[];
  collapsed?: boolean;
}

interface TopbarProps {
  user: User;
  notifications: number;
  onSearch: (query: string) => void;
}
```

---

#### Testing

**Unit Tests:**
- [ ] Sidebar renders with correct menu items for role
- [ ] Topbar displays user info
- [ ] Layout wraps children correctly

**Integration Tests:**
- [ ] Mobile hamburger opens sidebar
- [ ] Sidebar closes on backdrop click
- [ ] Active route highlighted

**Visual Tests:**
- [ ] Desktop: Sidebar always visible
- [ ] Mobile: Sidebar hidden, hamburger visible
- [ ] Active state styling

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] Screen reader announces navigation
- [ ] Mobile responsive validated
- [ ] Active route always highlighted
- [ ] Role-based menu filtering works

---

### WEB-S-1.3: Button Components

**As a** developer,
**I want to** reusable button components with all variants,
**So that** I don't repeat button code across pages.

**Priority:** CRITICAL
**Estimate:** 2 days
**Dependencies:** WEB-S-1.1

---

#### Acceptance Criteria

**AC-1.3.1:** Button component (primary, secondary, coral, ghost, icon)
```tsx
<Button variant="primary">Simpan</Button>
<Button variant="secondary">Batal</Button>
<Button variant="coral">Kode Biru</Button>
<Button variant="ghost">Tutup</Button>
<Button icon={<EditIcon />} />
```

**AC-1.3.2:** Size variants (sm, default, lg)
```tsx
<Button size="sm">Small</Button>
<Button>Default</Button>
<Button size="lg">Large</Button>
```

**AC-1.3.3:** Icon support with SVG integration
```tsx
<Button>
  <SaveIcon />
  Simpan Data
</Button>
```

**AC-1.3.4:** Disabled state styling
```tsx
<Button disabled>Cannot Click</Button>
```

**AC-1.3.5:** Loading state with spinner
```tsx
<Button loading>
  <Spinner />
  Menyimpan...
</Button>
```

**AC-1.3.6:** TypeScript props properly typed
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'coral' | 'ghost' | 'icon';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  children?: React.ReactNode;
  onClick?: () => void;
}
```

---

#### Technical Implementation

**Component File:** `src/components/ui/Button.tsx`

```tsx
export const Button = ({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon,
  children,
  onClick,
}: ButtonProps) => {
  return (
    <button
      className={cn(
        'btn',
        `btn-${variant}`,
        `btn-${size}`,
        disabled && 'opacity-50 cursor-not-allowed',
        loading && 'flex items-center gap-2'
      )}
      disabled={disabled || loading}
      onClick={onClick}
    >
      {loading && <Spinner className="w-4 h-4" />}
      {icon && <span className="icon">{icon}</span>}
      {children}
    </button>
  );
};
```

---

#### Testing

**Unit Tests:**
- [ ] All variants render correctly
- [ ] Size classes applied properly
- [ ] Disabled button not clickable
- [ ] Loading state shows spinner
- [ ] Icon renders with correct spacing

**Interaction Tests:**
- [ ] onClick handler called
- [ ] Disabled onClick not called
- [ ] Loading onClick not called

**Visual Tests:**
- [ ] All variants match design
- [ ] Hover states work
- [ ] Focus states visible
- [ ] Active states shown

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Storybook stories for all variants
- [ ] Keyboard navigation (Tab, Enter, Space)
- [ ] ARIA labels correct
- [ ] Focus rings visible
- [ ] Disabled state has reduced opacity

---

### WEB-S-1.4: Form Components

**As a** developer,
**I want to** reusable form components (inputs, selects, checkboxes),
**So that** forms are consistent and accessible.

**Priority:** CRITICAL
**Estimate:** 4 days
**Dependencies:** WEB-S-1.1

---

#### Acceptance Criteria

**AC-1.4.1:** FormInput component with label, hint, error
```tsx
<FormInput
  label="Nama Lengkap"
  hint="Sesuai kartu identitas"
  error={errors.nama}
  required
/>
```

**AC-1.4.2:** FormSelect component with custom dropdown
```tsx
<FormSelect
  label="Poli Tujuan"
  options={poliOptions}
  placeholder="Pilih poli"
/>
```

**AC-1.4.3:** FormCheckbox and FormRadio components
```tsx
<FormCheckbox label="Pasien BPJS" />
<FormRadio name="gender" value="male" label="Laki-laki" />
```

**AC-1.4.4:** FormSwitch component (toggle)
```tsx
<FormSwitch label="Aktifkan BPJS" checked={enableBPJS} />
```

**AC-1.4.5:** FormTextarea component with auto-resize
```tsx
<FormTextarea
  label="Catatan"
  rows={4}
  autoResize
/>
```

**AC-1.4.6:** All components WCAG 2.1 AA compliant
- Labels associated with inputs
- Error messages announced by screen reader
- Required fields indicated
- Focus states visible
- Color contrast ≥4.5:1

---

#### Technical Implementation

**Component Files:**
```
src/components/ui/form/
├── FormInput.tsx
├── FormSelect.tsx
├── FormCheckbox.tsx
├── FormRadio.tsx
├── FormSwitch.tsx
└── FormTextarea.tsx
```

**Props Interface:**
```typescript
interface FormInputProps {
  label: string;
  hint?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  type?: 'text' | 'email' | 'number' | 'tel';
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
}
```

---

#### Testing

**Unit Tests:**
- [ ] All form components render
- [ ] Labels associate with inputs
- [ ] Error messages display
- [ ] Required fields show asterisk
- [ ] Disabled state works

**Accessibility Tests:**
- [ ] ARIA labels present
- [ ] Screen reader announces errors
- [ ] Keyboard navigation works
- [ ] Focus management correct

**Visual Tests:**
- [ ] Error state has red border
- [ ] Focus ring visible
- [ ] Disabled state grayed out

---

#### Definition of Done

- [x] All AC criteria met
- [ ] React Hook Form integration tested
- [ ] Zod validation working
- [ ] Error states tested
- [ ] Accessibility audit passed
- [ ] Storybook stories for all components

---

### WEB-S-1.5: Card & Badge Components

**As a** developer,
**I want to** card and badge components for information display,
**So that** patient data is consistently presented.

**Priority:** HIGH
**Estimate:** 2 days
**Dependencies:** WEB-S-1.1

---

#### Acceptance Criteria

**AC-1.5.1:** Card component (default, interactive, elevated variants)
```tsx
<Card variant="default">Content</Card>
<Card variant="interactive" onClick={handleClick}>Clickable</Card>
<Card variant="elevated">Important</Card>
```

**AC-1.5.2:** PatientCard component with BPJS badge
```tsx
<PatientCard
  name="Budi Santoso"
  rmNumber="2024-001234"
  bpjsStatus="active"
  photo="/photos/2024-001234.jpg"
/>
```

**AC-1.5.3:** Badge component (all colors: primary, success, warning, error, info)
```tsx
<Badge variant="primary">Primary</Badge>
<Badge variant="success">Aktif</Badge>
<Badge variant="warning">Proses</Badge>
<Badge variant="error">Gagal</Badge>
```

**AC-1.5.4:** BPJS-specific badge (with dot variant)
```tsx
<BPJSBadge status="active" />
<BPJSBadge status="inactive" dot />
```

**AC-1.5.5:** Triage badges (Merah, Kuning, Hijau)
```tsx
<TriageBadge level="merah" />  {/* Gawat Darurat */}
<TriageBadge level="kuning" /> {/* Semi-Urgent */}
<TriageBadge level="hijau" />  {/* Non-Urgent */}
```

---

#### Technical Implementation

**Component Files:**
```
src/components/ui/
├── Card.tsx
├── PatientCard.tsx
├── Badge.tsx
├── BPJSBadge.tsx
└── TriageBadge.tsx
```

**Design Tokens:**
```typescript
const triageColors = {
  merah: '#dc2626',
  kuning: '#f59e0b',
  hijau: '#059669',
};
```

---

#### Testing

**Unit Tests:**
- [ ] All card variants render
- [ ] PatientCard displays all fields
- [ ] All badge colors correct
- [ ] BPJS badge shows correct status
- [ ] Triage badges match design

**Visual Tests:**
- [ ] Card hover effects work
- [ ] Badge colors accessible
- [ ] PatientCard photo crops correctly

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Storybook stories created
- [ ] Color contrast validated
- [ ] PatientCard handles missing photo
- [ ] Badges work in all contexts

---

### WEB-S-1.6: Alert & Notification Components

**As a** developer,
**I want to** alert and notification components for user feedback,
**So that** users know what's happening.

**Priority:** HIGH
**Estimate:** 2 days
**Dependencies:** WEB-S-1.1

---

#### Acceptance Criteria

**AC-1.6.1:** Alert component (info, success, warning, error)
```tsx
<Alert variant="info">Informasi</Alert>
<Alert variant="success">Berhasil disimpan</Alert>
<Alert variant="warning">Peringatan</Alert>
<Alert variant="error">Gagal</Alert>
```

**AC-1.6.2:** CriticalAlert component for medical emergencies
```tsx
<CriticalAlert>
  NILAI KRITIS - KALIUM RENDAH
  Segera hubungi dokter!
</CriticalAlert>
```

**AC-1.6.3:** Toast/Notification system with auto-dismiss
```tsx
toast.success('Data berhasil disimpan');
toast.error('Gagal menyimpan data');
toast.info('Informasi BPJS');
```

**AC-1.6.4:** Dismissible close button on alerts
```tsx
<Alert dismissible onDismiss={() => setOpen(false)}>
  Content
</Alert>
```

---

#### Technical Implementation

**Component Files:**
```
src/components/ui/
├── Alert.tsx
├── CriticalAlert.tsx
└── toast.ts (toast system)
```

**Toast System:**
```typescript
interface Toast {
  id: string;
  variant: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
}

export const toast = {
  success: (message: string) => {},
  error: (message: string) => {},
  info: (message: string) => {},
  warning: (message: string) => {},
};
```

---

#### Testing

**Unit Tests:**
- [ ] All alert variants render
- [ ] CriticalAlert has correct styling
- [ ] Toast creates notification
- [ ] Toast auto-dismisses after duration
- [ ] Dismissible alert closes on button click

**Integration Tests:**
- [ ] Multiple toasts stack correctly
- [ ] Toast removes after timeout
- [ ] Alert callback fires on dismiss

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Toast system documented
- [ ] Storybook stories created
- [ ] CriticalAlert has distinctive styling
- [ ] Dismissible alerts accessible

---

### WEB-S-1.7: Table & Modal Components

**As a** developer,
**I want to** table and modal components for complex data,
**So that** I can show lists and confirm actions.

**Priority:** HIGH
**Estimate:** 3 days
**Dependencies:** WEB-S-1.1

---

#### Acceptance Criteria

**AC-1.7.1:** Table component with sortable headers
```tsx
<Table
  data={patients}
  columns={columns}
  sortable
  onSort={(column) => handleSort(column)}
/>
```

**AC-1.7.2:** Pagination component for large datasets
```tsx
<Pagination
  total={100}
  pageSize={10}
  currentPage={1}
  onPageChange={(page) => setPage(page)}
/>
```

**AC-1.7.3:** Modal component with overlay and close
```tsx
<Modal isOpen={open} onClose={() => setOpen(false)}>
  <ModalHeader>Title</ModalHeader>
  <ModalBody>Content</ModalBody>
  <ModalFooter>Actions</ModalFooter>
</Modal>
```

**AC-1.7.4:** Modal sizes (sm, md, lg, xl)
```tsx
<Modal size="sm">Small modal</Modal>
<Modal size="md">Medium modal</Modal>
<Modal size="lg">Large modal</Modal>
<Modal size="xl">Extra large modal</Modal>
```

**AC-1.7.5:** Escape key closes modal
- Modal closes when Escape pressed
- Focus returns to triggering element
- Backdrop click closes modal

---

#### Technical Implementation

**Component Files:**
```
src/components/ui/
├── Table.tsx
├── Pagination.tsx
├── Modal.tsx
├── ModalHeader.tsx
├── ModalBody.tsx
└── ModalFooter.tsx
```

**Table Props:**
```typescript
interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  sortable?: boolean;
  onSort?: (column: string) => void;
}
```

**Modal Props:**
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
}
```

---

#### Testing

**Unit Tests:**
- [ ] Table renders with data
- [ ] Sorting triggers callback
- [ ] Pagination changes page
- [ ] Modal opens/closes
- [ ] Modal sizes correct

**Accessibility Tests:**
- [ ] Table headers sortable via keyboard
- [ ] Modal trap focus inside
- [ ] Escape key closes modal
- [ ] Focus returns on close

**Visual Tests:**
- [ ] Table rows alternate color
- [ ] Sort indicators visible
- [ ] Modal backdrop dims content
- [ ] Modal sizes match design

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Storybook stories created
- [ ] Keyboard navigation tested
- [ ] Focus trap validated
- [ ] Modal animations smooth

---

### WEB-S-1.8: Storybook Documentation

**As a** developer,
**I want to** Storybook stories for all components,
**So that** I can see and test components in isolation.

**Priority:** HIGH
**Estimate:** 3 days
**Dependencies:** WEB-S-1.1 through WEB-S-1.7

---

#### Acceptance Criteria

**AC-1.8.1:** Storybook configured for Next.js
```bash
# .storybook/main.ts
import type { StorybookConfig } from '@storybook/nextjs';

const config: StorybookConfig = {
  stories: ['../src/components/**/*.stories.tsx'],
  addons: ['@storybook/addon-essentials'],
  framework: {
    name: '@storybook/nextjs',
    options: {},
  },
};
export default config;
```

**AC-1.8.2:** Stories for all button variants
```tsx
// Button.stories.tsx
export default { component: Button };
export const Primary = { args: { variant: 'primary' } };
export const Secondary = { args: { variant: 'secondary' } };
export const Coral = { args: { variant: 'coral' } };
export const Ghost = { args: { variant: 'ghost' } };
```

**AC-1.8.3:** Stories for all form components**
- FormInput with all states
- FormSelect with options
- FormCheckbox, FormRadio, FormSwitch
- FormTextarea with auto-resize

**AC-1.8.4:** Stories for card and badge variants**
- All card variants
- All badge colors
- PatientCard with sample data
- Triage badges (Merah, Kuning, Hijau)

**AC-1.8.5:** Interactive stories with controls**
- ArgsTable for props
- Interactive controls panel
- Live editing of props

**AC-1.8.6:** Storybook deployed at :6006**
```bash
npm run storybook
# Opens http://localhost:6006
```

---

#### Technical Implementation

**Storybook Structure:**
```
.storybook/
├── main.ts
└── preview.ts

src/components/
├── ui/
│   ├── Button.tsx
│   ├── Button.stories.tsx
│   ├── Card.tsx
│   └── Card.stories.tsx
└── layout/
    ├── Sidebar.tsx
    └── Sidebar.stories.tsx
```

**Storybook Addons:**
```json
{
  "@storybook/addon-essentials": "^8.0.0",
  "@storybook/addon-interactions": "^8.0.0",
  "@storybook/testing-library": "^0.2.0"
}
```

---

#### Testing

**Manual Tests:**
- [ ] All stories render without errors
- [ ] Controls panel works
- [ ] Actions panel logs events
- [ ] Interactive controls functional

**Automated Tests:**
- [ ] Storybook tests pass
- [ ] Visual regression tests pass
- [ ] Accessibility tests pass

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Every component has Storybook story
- [ ] Controls documented
- [ ] Interactive examples working
- [ ] Storybook builds successfully
- [ ] Deployed to Chromatic (optional)

---

### WEB-S-1.9: Component Usage Guidelines

**As a** developer,
**I want to** clear documentation on when/how to use each component,
**So that** I make consistent UI decisions.

**Priority:** MEDIUM
**Estimate:** 2 days
**Dependencies:** WEB-S-1.1 through WEB-S-1.8

---

#### Acceptance Criteria

**AC-1.9.1:** Button usage guide (primary vs secondary vs coral)
```markdown
# Button Usage

## Primary Button
Use for: Main actions (Save, Submit, Confirm)
When: User's primary goal on the page
Don't: Use for destructive actions (use coral)

## Secondary Button
Use for: Alternative actions (Cancel, Back)
When: User wants to exit or undo
Don't: Use for main action (use primary)

## Coral Button
Use for: Urgent or destructive actions
When: Emergency activation, delete, critical warnings
Don't: Overuse - loses impact

## Ghost Button
Use for: Low-emphasis actions
When: Tertiary options, view-only actions
Don't: Use for primary workflow
```

**AC-1.9.2:** Alert placement patterns (success, warning, error)
```markdown
# Alert Placement

## Success Alerts
Place: Top of form after successful submission
Duration: Auto-dismiss after 5 seconds

## Warning Alerts
Place: Near relevant field or top of page
Duration: Persistent until user acknowledges

## Error Alerts
Place: Top of form with field-level errors
Duration: Persistent until errors fixed

## Critical Alerts
Place: Top of page with distinctive styling
Duration: Persistent with manual dismiss
```

**AC-1.9.3:** Form validation patterns (inline, summary)
```markdown
# Form Validation

## Inline Validation
Use: For individual field errors
Show: Red border + error text below field
When: Field loses focus (onBlur)

## Validation Summary
Use: For multiple form errors
Show: List of errors at top of form
When: User attempts to submit with errors

## Validation Timing
- On blur: Show inline errors
- On change: Clear inline errors
- On submit: Show summary if errors exist
```

**AC-1.9.4:** Color usage guide (triage, BPJS, semantic colors)
```markdown
# Color Usage

## Triage Colors
Merah (#dc2626): Gawat darurat - segera tangani
Kuning (#f59e0b): Semi-urgent - perlu perhatian
Hijau (#059669): Non-urgent - tunggu giliran

## BPJS Colors
Blue (#1e3a8a): Primary BPJS branding
Light Blue (#3b82f6): BPJS status indicators
Background (#eff6ff): BPJS card backgrounds

## Semantic Colors
Success (#059669): Active, confirmed, successful
Warning (#f59e0b): Pending, caution, review needed
Error (#dc2626): Inactive, failed, critical
Info (#0284c7): Information, neutral
```

**AC-1.9.5:** Accessibility checklist for each component
```markdown
# Accessibility Checklist

## All Components
- [ ] Keyboard navigable (Tab, Enter, Escape)
- [ ] Focus indicator visible
- [ ] ARIA labels correct
- [ ] Color contrast ≥4.5:1
- [ ] Screen reader announces purpose

## Forms
- [ ] All inputs have labels
- [ ] Required fields indicated
- [ ] Error messages announced
- [ ] Instructions available

## Interactive Elements
- [ ] Click target ≥44x44px (mobile)
- [ ] Disabled states obvious
- [ ] Loading states announced
```

**AC-1.9.6:** Do's and don'ts with visual examples
```markdown
# Do's and Don'ts

## Button Usage
✓ DO: Use primary for main action
✗ DON'T: Multiple primary buttons competing

✓ DO: Group related buttons
✗ DON'T: Scattered buttons everywhere

## Form Layout
✓ DO: Single column on mobile
✗ DON'T: Side-by-side on small screens

✓ DO: Show one field error at a time
✗ DON'T: Overwhelm with all errors at once

## Alert Placement
✓ DO: Place alerts consistently
✗ DON'T: Move alerts around
```

---

#### Technical Implementation

**Documentation File:** `src/docs/COMPONENT_GUIDELINES.md`

**Documentation Structure:**
```markdown
# SIMRS Component Usage Guidelines

1. Button Usage
2. Form Validation
3. Alert Placement
4. Color Usage
5. Accessibility
6. Common Patterns
7. Do's and Don'ts

Appendix:
- Design Tokens Reference
- Component Props Reference
- Accessibility Checklist
```

---

#### Testing

**Review Tests:**
- [ ] Guidelines reviewed by UX team
- [ ] Examples tested for accuracy
- [ ] Screenshots captured
- [ ] Do's/don't validated

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Documentation comprehensive
- [ ] Examples working
- [ ] Screenshots included
- [ ] Accessibility checklist validated

---

## WEB-EPIC-2: BPJS INTEGRATION SUITE STORIES

---

### WEB-S-2.1: BPJS Eligibility Check

**As a** registration staff,
**I want to** verify BPJS eligibility in real-time,
**So that** I know if patient's BPJS is active before registration.

**Priority:** HIGH
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-1

---

#### Acceptance Criteria

**AC-2.1.1:** BPJS card number input with formatting
```tsx
<BPJSVerificationCard>
  <Input
    label="No. Kartu BPJS"
    placeholder="0001R00101XXXX"
    format="####R########XX"  // Auto-format
  />
  <Button onClick={verifyBPJS}>Cek Eligibility</Button>
</BPJSVerificationCard>
```

**AC-2.1.2:** Real-time eligibility API call (VClaim)
```typescript
// API Call
const verifyBPJS = async (cardNumber: string) => {
  const response = await fetch(
    `/api/v1/bpjs/eligibility/${cardNumber}`
  );
  const data = await response.json();
  return data;
};
```

**AC-2.1.3:** Success state shows: name, NIK, jenis peserta, faskes
```tsx
{status === 'success' && (
  <BPJSResult>
    <ResultHeader success>
      <Icon>✓</Icon>
      <span>Pasien Aktif</span>
    </ResultHeader>
    <PatientDetails>
      <Detail label="Nama" value={data.nama} />
      <Detail label="NIK" value={data.nik} />
      <Detail label="Jenis" value={data.jenisPeserta} />
      <Detail label="Faskes" value={data.faskes} />
    </PatientDetails>
    <Button onClick={autoFill}>
      Gunakan Data BPJS
    </Button>
  </BPJSResult>
)}
```

**AC-2.1.4:** Error state shows clear failure reason
```tsx
{status === 'error' && (
  <Alert variant="error">
    No. kartu BPJS tidak ditemukan atau tidak aktif.
    <Button onClick={retry}>Coba Lagi</Button>
  </Alert>
)}
```

**AC-2.1.5:** Loading state with spinner during API call
```tsx
{status === 'loading' && (
  <Button disabled loading>
    <Spinner />
    Mengecek...
  </Button>
)}
```

**AC-2.1.6:** Auto-fill patient data from BPJS response
```typescript
const autoFillFromBPJS = () => {
  setFieldValue('nik', bpjsData.nik);
  setFieldValue('nama', bpjsData.nama);
  setFieldValue('tglLahir', bpjsData.tglLahir);
  toast.success('Data terisi otomatis dari BPJS');
};
```

---

#### Technical Implementation

**Component:** `src/components/bpjs/BPJSVerificationCard.tsx`

**API Endpoint (Backend):**
```python
@router.get("/bpjs/eligibility/{card_number}")
async def check_eligibility(card_number: str):
    # Call BPJS VClaim API
    # Return patient data or error
    pass
```

---

#### Testing

**Unit Tests:**
- [ ] Component renders correctly
- [ ] Input formats card number
- [ ] Loading state shows
- [ ] Success state displays data
- [ ] Error state shows message

**Integration Tests:**
- [ ] Mock API returns data
- [ ] Auto-fill populates fields
- [ ] Error handling works
- [ ] Retry button re-calls API

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Mock data working for development
- [ ] Real BPJS API integrated
- [ ] Error scenarios tested
- [ ] Auto-fill functional
- [ ] Audit logging (ST-003) confirmed

---

### WEB-S-2.2: BPJS SEP Creation Wizard

**As a** registration staff,
**I want to** a guided wizard to create SEP,
**So that** all required BPJS data is captured correctly.

**Priority:** HIGH
**Estimate:** 5 days
**Dependencies:** WEB-S-2.1

---

#### Acceptance Criteria

**AC-2.2.1:** Multi-step wizard (data → poli → diagnosa → confirm)
```tsx
<SEPWizard currentStep={step}>
  <Step 1>Data Pasien</Step>
  <Step 2>Data Rujukan</Step>
  <Step 3>Poli & Diagnosa</Step>
  <Step 4>Konfirmasi</Step>
</SEPWizard>
```

**AC-2.2.2:** Step progress indicator
```tsx
<StepProgress
  steps={['Data', 'Rujukan', 'Poli', 'Konfirmasi']}
  currentStep={2}
  completed={[1]}
/>
```

**AC-2.2.3:** Rujukan number validation with BPJS API
```tsx
<RujukanInput>
  <Input
    label="No. Rujukan"
    placeholder="Nomor rujukan dari faskes tingkat 1/2"
    onBlur={validateRujukan}
  />
  {rujukanData && (
    <RujukanResult>
      <Detail label="Faskes Asal" value={rujukanData.faskes} />
      <Detail label="Diagnosa" value={rujukanData.diagnosa} />
      <Detail label="Poli Rujukan" value={rujukanData.poli} />
    </RujukanResult>
  )}
</RujukanInput>
```

**AC-2.2.4:** Poli selection dropdown
```tsx
<Select
  label="Poli Tujuan"
  options={[
    { value: 'INT', label: 'Penyakit Dalam' },
    { value: 'ANA', label: 'Anak' },
    { value: 'BED', label: 'Bedah' },
    { value: 'OBG', label: 'Obgyn' },
  ]}
/>
```

**AC-2.2.5:** ICD-10 diagnosis search
```tsx
<DiagnosisSearch
  placeholder="Cari diagnosa ICD-10..."
  onSelect={(diagnosis) => addDiagnosis(diagnosis)}
/>
<SelectedDiagnoses>
  {diagnoses.map(d => (
    <DiagnosisChip code={d.code} name={d.name} />
  ))}
</SelectedDiagnoses>
```

**AC-2.2.6:** Kelas rawat selection (1/2/3)
```tsx
<KelasRawatSelection>
  <Radio value="1" label="Kelas 1" surcharge="Naik kelas (tambah biaya)" />
  <Radio value="2" label="Kelas 2" surcharge="Naik kelas (tambah biaya)" />
  <Radio value="3" label="Kelas 3" checked default />
</KelasRawatSelection>
```

**AC-2.2.7:** Real-time validation panel
```tsx
<ValidationPanel>
  <ValidationItem valid label="Data pasien lengkap" />
  <ValidationItem valid label="No. kartu BPJS valid" />
  <ValidationItem valid label="Eligibility aktif" />
  <ValidationItem pending label="No. rujukan belum diisi" />
  <ValidationItem valid label="Diagnosa: J18.9" />
</ValidationPanel>
```

**AC-2.2.8:** Confirmation summary before submission
```tsx
<ConfirmationSummary>
  <PatientInfo name="BUDI SANTOSO" bpjs="0001R00101XXXX" />
  <RujukanInfo no="123456789" faskes="Puskesmas Sehat" />
  <PoliInfo poli="Penyakit Dalam" />
  <DiagnosaInfo code="J18.9" name="Pneumonia" />
  <KelasInfo kelas="3" />
</ConfirmationSummary>
```

---

#### Technical Implementation

**Component:** `src/components/bpjs/SEPWizard.tsx`

**Wizard State Management:**
```typescript
interface SEPWizardState {
  step: 1 | 2 | 3 | 4;
  patientData: PatientData;
  rujukanData: RujukanData | null;
  poliTujuan: string;
  diagnoses: Diagnosis[];
  kelasRawat: 1 | 2 | 3;
}
```

**API Endpoint (Backend):**
```python
@router.post("/bpjs/sep")
async def create_sep(sep_data: SEPCreate):
    # Call BPJS VClaim API to create SEP
    # Return SEP number and data
    pass
```

---

#### Testing

**Integration Tests:**
- [ ] Wizard navigation works (next/back)
- [ ] Step progress updates
- [ ] Rujukan validation works
- [ ] Diagnosis search functional
- [ ] Validation panel updates
- [ ] Confirmation displays all data
- [ ] Submit creates SEP

---

#### Definition of Done

- [x] All AC criteria met
- [ ] All 4 wizard steps working
- [ ] Validation panel accurate
- [ ] BPJS API integrated
- [ ] SEP number generated
- [ ] Error handling complete

---

### WEB-S-2.3: BPJS Status Indicators

**As a** ANY USER,
**I want to** see BPJS status prominently throughout the UI,
**So that** I know patient's insurance status at a glance.

**Priority:** MEDIUM
**Estimate:** 2 days
**Dependencies:** WEB-S-2.1

---

#### Acceptance Criteria

**AC-2.3.1:** BPJS badge on patient cards
```tsx
<PatientCard>
  {patient.bpjs && <BPJSBadge status={patient.bpjsStatus} />}
  <PatientName>{patient.name}</PatientName>
</PatientCard>
```

**AC-2.3.2:** Color-coded status (active = green, inactive = red)
```tsx
<BPJSBadge
  status={status}
  color={status === 'active' ? 'green' : 'red'}
/>
```

**AC-2.3.3:** Status shows peserta type (PBI, Non-PBI)
```tsx
<BPJSBadge>
  {jenisPeserta} - {status}
</BPJSBadge>
```

**AC-2.3.4:** Faskes eligibility indicator
```tsx
<FaskesIndicator
  eligible={faskesMatches}
  currentFaskes={currentFaskes}
/>
```

**AC-2.3.5:** Status updates in real-time (polling)
```typescript
// Poll for BPJS status updates
useEffect(() => {
  const interval = setInterval(async () => {
    const status = await fetchBPJSStatus(cardNumber);
    setBPJSStatus(status);
  }, 60000); // Every minute
  return () => clearInterval(interval);
}, [cardNumber]);
```

---

#### Technical Implementation

**Component:** `src/components/bpjs/BPJSBadge.tsx`

**Polling Hook:**
```typescript
const useBPJSStatus = (cardNumber: string) => {
  const [status, setStatus] = useState<BPJSStatus>(null);

  useEffect(() => {
    // Poll every 60 seconds
    const interval = setInterval(() => {
      fetchStatus();
    }, 60000);
    return () => clearInterval(interval);
  }, [cardNumber]);

  return status;
};
```

---

#### Testing

**Unit Tests:**
- [ ] Badge displays correct color
- [ ] Status text accurate
- [ ] Peserta type shown
- [ ] Faskes indicator works

**Integration Tests:**
- [ ] Polling updates status
- [ ] Status changes trigger re-render
- [ ] Error handling works

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Badges work in all contexts
- [ ] Polling functional
- [ ] Status updates visible
- [ ] Error states handled

---

### WEB-S-2.4: BPJS Error Handling

**As a** registration staff,
**I want to** clear error messages when BPJS calls fail,
**So that** I can troubleshoot and help patients.

**Priority:** MEDIUM
**Estimate:** 2 days
**Dependencies:** WEB-S-2.1

---

#### Acceptance Criteria

**AC-2.4.1:** User-friendly error messages (not API codes)
```tsx
{error && (
  <Alert variant="error">
    {getErrorMessage(error.code)}
    {/* NOT: "VClaim API Error 404" */}
    {/* YES: "No. kartu BPJS tidak ditemukan" */}
  </Alert>
)}
```

**AC-2.4.2:** Retry button on failures
```tsx
<Button onClick={retryBPJS}>
  <RefreshIcon />
  Coba Lagi
</Button>
```

**AC-2.4.3:** Fallback to manual BPJS entry
```tsx
{apiFailed && (
  <ManualEntry>
    <Alert variant="warning">
      BPJS API tidak dapat diakses. Silakan masukkan data manual.
    </Alert>
    <Form {...manualFormProps} />
  </ManualEntry>
)}
```

**AC-2.4.4:** Error logging to audit system
```typescript
const logBPJSError = (error: BPJSError) => {
  auditLog.create({
    action: 'BPJS_ERROR',
    resource: `BPJS:${error.cardNumber}`,
    details: {
      code: error.code,
      message: error.message,
      timestamp: new Date(),
    },
  });
};
```

---

#### Technical Implementation

**Error Mapping:**
```typescript
const errorMessages: Record<string, string> = {
  'CARD_NOT_FOUND': 'No. kartu BPJS tidak ditemukan',
  'INACTIVE': 'Keanggotaan BPJS tidak aktif',
  'EXPIRED': 'Keanggotaan BPJS telah kadaluarsa',
  'API_ERROR': 'Sistem BPJS sedang sibuk, coba lagi',
  'NETWORK_ERROR': 'Tidak dapat terhubung ke BPJS',
};
```

---

#### Testing

**Unit Tests:**
- [ ] Error codes map to messages
- [ ] Retry button re-calls API
- [ ] Manual entry works
- [ ] Audit log created

---

#### Definition of Done

- [x] All AC criteria met
- [ ] All error scenarios tested
- [ ] User-friendly messages validated
- [ ] Audit logging confirmed
- [ ] Manual entry functional

---

### WEB-S-2.5: BPJS History & Audit

**As an** admin,
**I want to** see BPJS interaction history,
**So that** I can troubleshoot and audit.

**Priority:** LOW
**Estimate:** 2 days
**Dependencies:** WEB-S-2.1

---

#### Acceptance Criteria

**AC-2.5.1:** BPJS eligibility check log
```tsx
<BPJSHistoryLog>
  <LogEntry timestamp="2026-01-13 14:30" action="ELIGIBILITY_CHECK" success />
  <LogEntry timestamp="2026-01-13 14:25" action="SEP_CREATE" success />
  <LogEntry timestamp="2026-01-13 14:20" action="ELIGIBILITY_CHECK" failed />
</BPJSHistoryLog>
```

**AC-2.5.2:** SEP creation history
```tsx
<SEPHistory patientId={patientId}>
  {seps.map(sep => (
    <SEPItem sep={sep} />
  ))}
</SEPHistory>
```

**AC-2.5.3:** API call success/failure rates
```tsx
<BPJSStatistics>
  <Stat label="Success Rate" value="98.5%" />
  <Stat label="Total Calls" value="1,234" />
  <Stat label="Failed Calls" value="18" />
  <Stat label="Avg Response Time" value="450ms" />
</BPJSStatistics>
```

**AC-2.5.4:** Export to CSV (admin only)
```tsx
<Button onClick={exportToCSV} disabled={!isAdmin}>
  <DownloadIcon />
  Export History
</Button>
```

---

#### Technical Implementation

**Component:** `src/components/admin/BPJSHistory.tsx`

**API Endpoint:**
```python
@router.get("/bpjs/history")
async def get_bpjs_history(
    start_date: date,
    end_date: date,
    admin_only: True
):
    # Return BPJS interaction logs
    pass
```

---

#### Testing

**Unit Tests:**
- [ ] Log entries display
- [ ] Filters work
- [ ] Statistics calculate
- [ ] Export generates CSV

**Authorization Tests:**
- [ ] Non-admin cannot access
- [ ] Admin-only check enforced

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Admin-only access enforced
- [ ] Export functional
- [ ] Statistics accurate
- [ ] Audit log integration working

---

## WEB-EPIC-3: PATIENT REGISTRATION REDESIGN STORIES

---

### WEB-S-3.1: BPJS-First New Patient Registration

**As a** registration staff,
**I want to** a BPJS-first registration flow,
**So that** new patients register quickly with auto-filled data.

**Priority:** HIGH
**Estimate:** 4 days
**Dependencies:** WEB-S-EPIC-1, WEB-S-EPIC-2

---

#### Acceptance Criteria

**AC-3.1.1:** BPJS card number is PRIMARY input (prominent)
```tsx
<RegistrationForm>
  <BPJSVerificationCard featured>
    <Input
      label="No. Kartu BPJS"
      placeholder="0001R00101XXXX"
      autoFocus
    />
    <Button primary onClick={verifyBPJS}>
      Cek Eligibility
    </Button>
  </BPJSVerificationCard>

  <Divider>ATAU</Divider>

  <Button secondary onClick={showManualForm}>
    Daftar Tanpa BPJS
  </Button>
</RegistrationForm>
```

**AC-3.1.2:** Verify BPJS button with loading state
```tsx
{verifying && (
  <Button disabled loading>
    <Spinner />
    Mengecek...
  </Button>
)}
```

**AC-3.1.3:** Auto-fill patient data from BPJS (name, NIK, DOB)
```tsx
{bpjsData && (
  <Alert success>
    Data BPJS ditemukan!
    <Button onClick={autoFillFromBPJS}>
      Gunakan Data BPJS
    </Button>
  </Alert>
)}
```

**AC-3.1.4:** Manual registration as secondary option (below BPJS)
```tsx
{showManual && (
  <ManualRegistrationForm>
    <Input label="Nama Lengkap" required />
    <Input label="NIK" required />
    <Input label="Tanggal Lahir" type="date" required />
    {/* Manual fields */}
  </ManualRegistrationForm>
)}
```

**AC-3.1.5:** Photo upload (optional, with camera capture)
```tsx
<PhotoUpload optional>
  <CameraCapture onCapture={handlePhoto} />
  <FileUpload onUpload={handlePhoto} />
  <Preview src={photo} />
</PhotoUpload>
```

**AC-3.1.6:** Emergency contact section
```tsx
<EmergencyContact>
  <Input label="Nama Kontak Darurat" required />
  <Input label="Hubungan" required />
  <Input label="Telepon" required />
</EmergencyContact>
```

**AC-3.1.7:** Insurance selection (BPJS/Asuransi/Umum)
```tsx
<InsuranceSelection>
  <Radio name="insurance" value="bpjs" label="BPJS" checked />
  <Radio name="insurance" value="asuransi" label="Asuransi Swasta" />
  <Radio name="insurance" value="umum" label="Umum/Biaya Pribadi" />
</InsuranceSelection>
```

**AC-3.1.8:** Validation: required fields highlighted
```tsx
{errors && (
  <ValidationSummary>
    {Object.keys(errors).map(field => (
      <Error key={field}>{errors[field]}</Error>
    ))}
  </ValidationSummary>
)}
```

**AC-3.1.9:** Success message with auto-generated RM number
```tsx
{success && (
  <SuccessMessage>
    <h2>Pendaftaran Berhasil!</h2>
    <p>No. Rekam Medis: {rmNumber}</p>
    <p>No. Antrian: {queueNumber}</p>
  </SuccessMessage>
)}
```

**AC-3.1.10:** Total clicks: ≤5 from start to submit
- Step 1: Verify BPJS (1 click)
- Step 2: Auto-fill data (1 click)
- Step 3: Add emergency contact (enter data)
- Step 4: Select department (1 click)
- Step 5: Submit (1 click)

---

#### Technical Implementation

**Component:** `src/components/registration/NewPatientForm.tsx`

**Form State:**
```typescript
interface RegistrationFormState {
  bpjsCardNumber: string;
  bpjsVerified: boolean;
  bpjsData: BPJSData | null;
  manualMode: boolean;
  patientData: PatientData;
  emergencyContact: EmergencyContact;
  insuranceType: 'bpjs' | 'asuransi' | 'umum';
  photo: string | null;
}
```

---

#### Testing

**E2E Tests:**
- [ ] Complete BPJS registration flow
- [ ] Complete manual registration flow
- [ ] Auto-fill populates correctly
- [ ] Validation prevents submission
- [ ] Success message displays RM number

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Click count validated (≤5)
- [ ] BPJS flow tested
- [ ] Manual flow tested
- [ ] Photo upload working
- [ ] RM number generation confirmed

---

### WEB-S-3.2: Returning Patient Quick Check-In

**As a** registration staff,
**I want to** a quick check-in for returning patients,
**So that** registered patients can start visits in <30 seconds.

**Priority:** HIGH
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-1, WEB-S-EPIC-3.1

---

#### Acceptance Criteria

**AC-3.2.1:** Patient search bar (by RM, BPJS, NIK, name, phone)
```tsx
<QuickCheckIn>
  <GlobalSearch
    placeholder="Cari pasien... (Ctrl+K)"
    onSearch={handleSearch}
    searchableFields={['rm', 'bpjs', 'nik', 'nama', 'telepon']}
  />
</QuickCheckIn>
```

**AC-3.2.2:** Keyboard shortcut (Ctrl+K / Cmd+K)
```typescript
useEffect(() => {
  const handleShortcut = (e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInputRef.current?.focus();
    }
  };
  document.addEventListener('keydown', handleShortcut);
  return () => document.removeEventListener('keydown', handleShortcut);
}, []);
```

**AC-3.2.3:** Search results show: name, RM, last visit, BPJS status
```tsx
<SearchResults>
  {results.map(patient => (
    <ResultItem key={patient.id}>
      <PatientName>{patient.name}</PatientName>
      <PatientRM>RM: {patient.rmNumber}</PatientRM>
      <LastVisit>Terakhir: {patient.lastVisit}</LastVisit>
      <BPJSBadge status={patient.bpjsStatus} />
      <Button onClick={() => selectPatient(patient)}>
        Pilih Pasien
      </Button>
    </ResultItem>
  ))}
</SearchResults>
```

**AC-3.2.4:** Click patient → quick check-in modal
```tsx
<QuickCheckInModal isOpen={isOpen} onClose={closeModal}>
  <PatientInfo patient={selectedPatient} />
  <CheckInForm onSubmit={handleCheckIn}>
    <DatePicker label="Tanggal Kunjungan" defaultValue={today} />
    <Select label="Poli Tujuan" options={poliOptions} />
    <Button type="submit">Check-In</Button>
  </CheckInForm>
</QuickCheckInModal>
```

**AC-3.2.5:** Pre-fill: today's date, default department
```tsx
<CheckInForm
  defaultValues={{
    tanggalKunjungan: new Date(),
    poliTujuan: defaultPoli,
  }}
/>
```

**AC-3.2.6:** Select: poli tujuan (dropdown)
```tsx
<PoliSelect
  label="Poli Tujuan"
  options={[
    { value: 'INT', label: 'Penyakit Dalam' },
    { value: 'ANA', label: 'Anak' },
    { value: 'BED', label: 'Bedah' },
  ]}
  required
/>
```

**AC-3.2.7:** BPJS eligibility check runs automatically
```typescript
useEffect(() => {
  if (selectedPatient?.bpjsCardNumber) {
    checkEligibility(selectedPatient.bpjsCardNumber);
  }
}, [selectedPatient]);
```

**AC-3.2.8:** Queue number assigned
```tsx
{checkInSuccess && (
  <QueueTicket>
    <h2>No. Antrian: {queueNumber}</h2>
    <p>Poli: {poliTujuan}</p>
    <p>Estimasi: {estimatedWaitTime}</p>
  </QueueTicket>
)}
```

**AC-3.2.9:** Success: queue ticket displayed
```tsx
<QueueTicketDisplay>
  <LargeNumber>A-001</LargeNumber>
  <Poliname>Penyakit Dalam</Poliname>
  <Instructions>Silakan menunggu di ruang tunggu</Instructions>
</QueueTicketDisplay>
```

**AC-3.2.10:** Total time: <30 seconds
- Search: 5 seconds
- Select patient: 2 seconds
- Poli selection: 5 seconds
- BPJS check: 10 seconds (async)
- Queue assignment: 3 seconds
- **Total: ~25 seconds**

---

#### Technical Implementation

**Component:** `src/components/registration/QuickCheckIn.tsx`

**Performance Target:**
- Search: <2 seconds response
- BPJS check: async (non-blocking)
- Total flow: <30 seconds

---

#### Testing

**Performance Tests:**
- [ ] Search completes in <2 seconds
- [ ] Check-in flow completes in <30 seconds
- [ ] BPJS check doesn't block UI

**E2E Tests:**
- [ ] Complete check-in flow
- [ ] Queue number assigned
- [ ] Ticket displays correctly

---

#### Definition of Done

- [x] All AC criteria met
- [ ] 30-second target validated
- [ ] Keyboard shortcut working
- [ ] BPJS check async
- [ ] Queue assignment functional
- [ ] Ticket displays correctly

---

### WEB-S-3.3: Queue Management Dashboard

**As a** registration staff,
**I want to** a real-time queue dashboard,
**So that** I can monitor and manage patient flow.

**Priority:** MEDIUM
**Estimate:** 4 days
**Dependencies:** WEB-S-EPIC-1, WEB-S-EPIC-3.2

---

#### Acceptance Criteria

**AC-3.3.1:** Queue list by department
```tsx
<QueueDashboard>
  <DepartmentTabs>
    <Tab label="Poli Anak" count={12} />
    <Tab label="Penyakit Dalam" count={8} />
    <Tab label="Bedah" count={5} />
    <Tab label="IGD" count={3} priority />
  </DepartmentTabs>
</QueueDashboard>
```

**AC-3.3.2:** Patient details: name, RM, queue number, wait time
```tsx
<QueueList department="Poli Anak">
  {queue.map(patient => (
    <QueueItem key={patient.id}>
      <QueueNumber>{patient.queueNumber}</QueueNumber>
      <PatientName>{patient.name}</PatientName>
      <PatientRM>RM: {patient.rmNumber}</PatientRM>
      <WaitTime>{patient.waitTime}</WaitTime>
      <StatusBadge status={patient.status} />
    </QueueItem>
  ))}
</QueueList>
```

**AC-3.3.3:** Status badges: waiting, in-service, completed
```tsx
<StatusBadge variant="waiting">Menunggu</StatusBadge>
<StatusBadge variant="in-service">Sedang Diperiksa</StatusBadge>
<StatusBadge variant="completed">Selesai</StatusBadge>
```

**AC-3.3.4:** Priority queue indicators (elderly, pregnant, disabled)
```tsx
<QueueItem>
  {patient.isElderly && <PriorityBadge icon="elderly">Lansia</PriorityBadge>}
  {patient.isPregnant && <PriorityBadge icon="pregnant">Hamil</PriorityBadge>}
  {patient.isDisabled && <PriorityBadge icon="disabled">Disabilitas</PriorityBadge>}
</QueueItem>
```

**AC-3.3.5:** Emergency queue (IGD) - always top priority
```tsx
<EmergencyQueue>
  {emergencyPatients.map(patient => (
    <EmergencyPatient priority="critical">
      <TriageBadge level={patient.triageLevel} />
      <PatientName>{patient.name}</PatientName>
      <Timer>{timeInQueue}</Timer>
    </EmergencyPatient>
  ))}
</EmergencyQueue>
```

**AC-3.3.6:** Queue statistics: total waiting, avg wait time
```tsx
<QueueStatistics>
  <Stat label="Menunggu" value={waitingCount} />
  <Stat label="Sedang Diperiksa" value={inServiceCount} />
  <Stat label="Selesai" value={completedCount} />
  <Stat label="Rata-rata Tunggu" value={avgWaitTime} />
</QueueStatistics>
```

**AC-3.3.7:** Call next patient button
```tsx
<ActionBar>
  <Button primary onClick={callNextPatient}>
    <BellIcon />
    Panggil Berikutnya
  </Button>
  <Button onClick={skipPatient}>Lewati</Button>
</ActionBar>
```

**AC-3.3.8:** Move to completed status
```tsx
<PatientActions>
  <Button onClick={() => updateStatus('in-service')}>
    Mulai Pemeriksaan
  </Button>
  <Button onClick={() => updateStatus('completed')}>
    Selesai
  </Button>
</PatientActions>
```

**AC-3.3.9:** Export queue list (PDF for display screens)
```tsx
<Button onClick={exportQueuePDF}>
  <DownloadIcon />
  Export untuk Layar Tunggu
</Button>
```

---

#### Technical Implementation

**Component:** `src/components/registration/QueueDashboard.tsx`

**Real-time Updates:**
```typescript
// WebSocket or polling for real-time updates
useQueueUpdates(department, (queue) => {
  setQueueData(queue);
});
```

---

#### Testing

**Integration Tests:**
- [ ] Queue list displays correctly
- [ ] Status updates work
- [ ] Priority indicators show
- [ ] Statistics calculate correctly
- [ ] Export generates PDF

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Real-time updates working
- [ ] All queue operations functional
- [ ] Statistics accurate
- [ ] Export functional

---

### WEB-S-3.4: Digital Queue Display Screens

**As a** patient,
**I want to** see queue status on TV screens,
**So that** I know my position and estimated wait time.

**Priority:** MEDIUM
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-3.3

---

#### Acceptance Criteria

**AC-3.4.1:** Full-screen TV-optimized layout
```tsx
<QueueDisplayTV mode="fullscreen">
  <Header>Hospital Name</Header>
  <Department>Poliklinik Penyakit Dalam</Department>
  <CurrentQueue>A-001</CurrentQueue>
</QueueDisplayTV>
```

**AC-3.4.2:** Department tabs (auto-rotate every 30s)
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    setCurrentDepartment(prev => {
      const idx = departments.indexOf(prev);
      return departments[(idx + 1) % departments.length];
    });
  }, 30000);
  return () => clearInterval(interval);
}, [departments]);
```

**AC-3.4.3:** Current queue number (LARGE, prominent)
```tsx
<CurrentQueueNumber size="huge">
  A-001
</CurrentQueueNumber>
```

**AC-3.4.4:** Next 5 patients in queue
```tsx
<UpcomingQueue>
  <QueueItem>A-002 - Budi Santoso</QueueItem>
  <QueueItem>A-003 - Siti Rahayu</QueueItem>
  <QueueItem>A-004 - Ahmad Wijaya</QueueItem>
  <QueueItem>A-005 - Dewi Lestari</QueueItem>
  <QueueItem>A-006 - Eko Prasetyo</QueueItem>
</UpcomingQueue>
```

**AC-3.4.5:** Estimated wait time
```tsx
<EstimatedWait>
  Estimasi Tunggu: 15 menit
</EstimatedWait>
```

**AC-3.4.6:** Hospital branding with SIMRS colors
```tsx
<QueueDisplay>
  <BrandHeader colors={simrsColors} />
  <Logo hospital={hospitalName} />
</QueueDisplay>
```

**AC-3.4.7:** Auto-refresh every 10 seconds
```typescript
useEffect(() => {
  const refreshInterval = setInterval(() => {
    fetchQueueData();
  }, 10000);
  return () => clearInterval(refreshInterval);
}, []);
```

**AC-3.4.8:** Marquee for announcements
```tsx
<Marquee>
  Selamat datang di RSUD Sehat. Mohon datang 15 menit sebelum jadwal.
  Bersedia menunggu jika dokter terlambat karena pemeriksaan darurat.
</Marquee>
```

**AC-3.4.9:** Audio alert when queue number changes
```tsx
useEffect(() => {
  if (queueChanged) {
    playAudio('queue-notification.mp3');
    announce(`Nomor antrian ${currentQueue}, poli ${department}`);
  }
}, [queueChanged, currentQueue, department]);
```

**AC-3.4.10:** Responsive to TV aspect ratios (16:9)
```css
@media (aspect-ratio: 16/9) {
  .queue-display {
    /* Full-screen layout optimized for TV */
  }
}
```

---

#### Technical Implementation

**Component:** `src/components/registration/QueueDisplayTV.tsx`

**TV Mode:**
```typescript
// Full-screen, no scrolling, large text
const TVMode = {
  fontSize: 'xxx-large',
  padding: '2rem',
  overflow: 'hidden',
};
```

---

#### Testing

**Visual Tests:**
- [ ] Layout works on 1920x1080 (Full HD)
- [ ] Layout works on 1280x720 (HD)
- [ ] Auto-rotate smooth
- [ ] Audio plays correctly

---

#### Definition of Done

- [x] All AC criteria met
- [ ] TV-optimized layout
- [ ] Auto-rotate working
- [ ] Audio notifications working
- [ ] Marquee scrolling
- [ ] Hospital branding applied

---

### WEB-S-3.5: Online Appointment Booking

**As a** patient,
**I want to** book appointments online,
**So that** I don't have to wait in long queues.

**Priority:** LOW
**Estimate:** 5 days
**Dependencies:** WEB-S-EPIC-3.3

---

#### Acceptance Criteria

**AC-3.5.1:** Public-facing booking page (no auth required)
```tsx
<PublicBookingPage>
  <Header>Booking Janji Temu Online</Header>
  <BookingForm onSubmit={handleBooking}>
    {/* No authentication required */}
  </BookingForm>
</PublicBookingPage>
```

**AC-3.5.2:** Select: department, doctor, date, time slot
```tsx
<BookingForm>
  <DepartmentSelect options={departments} />
  <DoctorSelect options={doctors} />
  <DatePicker label="Tanggal" minDate={today} />
  <TimeSlotSelect options={availableSlots} />
</BookingForm>
```

**AC-3.5.3:** Patient details form (name, phone, BPJS optional)
```tsx
<PatientDetails>
  <Input label="Nama Lengkap" required />
  <Input label="Nomor Telepon" required />
  <Input label="No. BPJS (Opsional)" />
  <Checkbox label="Saya ingin mengingatkan jadwal ini" />
</PatientDetails>
```

**AC-3.5.4:** Booking confirmation with queue number
```tsx
{bookingSuccess && (
  <BookingConfirmation>
    <h2>Booking Berhasil!</h2>
    <ConfirmationDetails>
      <Detail label="No. Booking" value={bookingNumber} />
      <Detail label="Nama" value={patientName} />
      <Detail label="Dokter" value={doctorName} />
      <Detail label="Tanggal" value={appointmentDate} />
      <Detail label="Jam" value={appointmentTime} />
      <Detail label="No. Antrian" value={queueNumber} />
    </ConfirmationDetails>
  </BookingConfirmation>
)}
```

**AC-3.5.5:** SMS notification (if phone provided)
```typescript
if (phoneNumber && smsEnabled) {
  await sendSMS({
    to: phoneNumber,
    message: `Booking Anda: ${bookingNumber} pada ${date} jam ${time}`,
  });
}
```

**AC-3.5.6:** Appointment reminder (24h before via SMS)
```typescript
// Scheduled task to send reminders
scheduleReminder({
  when: '24 hours before',
  action: () => sendSMSReminder(appointment),
});
```

**AC-3.5.7:** Cancel/reschedule option
```tsx
<AppointmentActions bookingId={bookingId}>
  <Button onClick={reschedule}>Ubah Jadwal</Button>
  <Button onClick={cancel}>Batalkan</Button>
</AppointmentActions>
```

**AC-3.5.8:** Admin view: all appointments by date
```tsx
<AppointmentAdminView date={date}>
  <AppointmentList>
    {appointments.map(appt => (
      <AppointmentItem appointment={appt} />
    ))}
  </AppointmentList>
</AppointmentAdminView>
```

**AC-3.5.9:** Sync with queue system (appointment = pre-queued)
```typescript
// When appointment time arrives, auto-add to queue
const syncAppointmentToQueue = async (appointment) => {
  await queue.create({
    patientId: appointment.patientId,
    department: appointment.department,
    appointmentId: appointment.id,
    preQueued: true,
  });
};
```

---

#### Technical Implementation

**Public Route:** `src/app/booking/page.tsx`

**API Endpoints:**
```python
@router.post("/public/appointments")
async def create_appointment(data: BookingData):
    # Create appointment, queue number
    pass

@router.get("/appointments/{date}")
async def get_appointments(date: date):
    # Return all appointments for date
    pass
```

---

#### Testing

**E2E Tests:**
- [ ] Complete booking flow
- [ ] Confirmation displays
- [ ] SMS sent (test mode)
- [ ] Cancel works
- [ ] Reschedule works

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Public booking functional
- [ ] SMS notifications working
- [ ] Reminders scheduled
- [ ] Cancel/reschedule working
- [ ] Queue sync confirmed

---

### WEB-S-3.6: Patient Search & Lookup

**As a** registration staff,
**I want to** powerful patient search,
**So that** I can find any patient in <5 seconds.

**Priority:** HIGH
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-1

---

#### Acceptance Criteria

**AC-3.6.1:** Search by: RM number, BPJS number, NIK
```tsx
<PatientSearch>
  <SearchBar
    placeholder="Cari by RM, BPJS, NIK..."
    onSearch={handleSearch}
  />
</PatientSearch>
```

**AC-3.6.2:** Search by: name + DOB combination
```tsx
<AdvancedSearch>
  <Input name="nama" label="Nama Pasien" />
  <Input name="tglLahir" label="Tanggal Lahir" type="date" />
  <Button onClick={searchByNameDOB}>Cari</Button>
</AdvancedSearch>
```

**AC-3.6.3:** Search by: phone number
```tsx
<PhoneSearch>
  <Input label="Nomor Telepon" type="tel" />
  <Button onClick={searchByPhone}>Cari</Button>
</PhoneSearch>
```

**AC-3.6.4:** Fuzzy search for names (typos tolerated)
```typescript
const fuzzySearch = (query: string, patients: Patient[]) => {
  return fuse.search(query, {
    threshold: 0.3, // Tolerant of typos
    keys: ['nama', 'namaAlias'],
  });
};
```

**AC-3.6.5:** Search results show: photo, name, RM, BPJS status
```tsx
<SearchResults>
  {results.map(patient => (
    <PatientCard key={patient.id}>
      <PatientPhoto src={patient.photo} />
      <PatientName>{patient.name}</PatientName>
      <PatientRM>RM: {patient.rmNumber}</PatientRM>
      <BPJSBadge status={patient.bpjsStatus} />
      <Button onClick={() => viewProfile(patient)}>Lihat Profil</Button>
    </PatientCard>
  ))}
</SearchResults>
```

**AC-3.6.6:** Click result → full patient profile
```tsx
{selectedPatient && (
  <PatientProfileModal patient={selectedPatient}>
    <PatientInfo />
    <MedicalHistory />
    <LastVisits />
    <Actions>
      <Button onClick={startEncounter}>Mulai Kunjungan</Button>
      <Button onClick={editProfile}>Edit Profil</Button>
    </Actions>
  </PatientProfileModal>
)}
```

**AC-3.6.7:** Search history (recent searches)
```tsx
<SearchHistory>
  <HistoryLabel>Pencarian Terakhir:</HistoryLabel>
  {history.map(item => (
    <HistoryItem
      key={item.id}
      query={item.query}
      onClick={() => repeatSearch(item.query)}
    />
  ))}
</SearchHistory>
```

**AC-3.6.8:** Advanced filters: registration date range, department
```tsx
<AdvancedFilters>
  <DateRange
    label="Tanggal Registrasi"
    start={startDate}
    end={endDate}
  />
  <DepartmentMultiSelect departments={allDepartments} />
  <Button onClick={applyFilters}>Filter</Button>
</AdvancedFilters>
```

**AC-3.6.9:** Export search results (CSV)
```tsx
<Button onClick={exportToCSV}>
  <DownloadIcon />
  Export Hasil Pencarian
</Button>
```

---

#### Technical Implementation

**Component:** `src/components/patients/PatientSearch.tsx`

**Search API:**
```python
@router.get("/patients/search")
async def search_patients(
    query: str,
    search_type: SearchType,  # rm, bpjs, nik, name, phone
    filters: SearchFilters
):
    # Fuzzy search with filters
    pass
```

---

#### Testing

**Performance Tests:**
- [ ] Search completes in <2 seconds
- [ ] Fuzzy matching works
- [ ] Filters apply correctly
- [ ] Export generates CSV

---

#### Definition of Done

- [x] All AC criteria met
- [ ] All search types working
- [ ] Fuzzy search functional
- [ ] Search history saved
- [ ] Filters working
- [ ] Export functional

---

### WEB-S-3.7: Mobile Responsive Registration

**As a** registration staff using tablet,
**I want to** the registration interface to work on mobile,
**So that** I can register patients bedside or at entrance.

**Priority:** MEDIUM
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-3.1

---

#### Acceptance Criteria

**AC-3.7.1:** Mobile-optimized layout (375px breakpoint)
```css
@media (max-width: 375px) {
  .registration-form {
    padding: 1rem;
    font-size: 14px;
  }
}
```

**AC-3.7.2:** Touch-friendly buttons (minimum 44x44px)
```css
@media (max-width: 768px) {
  .btn {
    min-height: 44px;
    min-width: 44px;
    padding: 12px 20px;
  }
}
```

**AC-3.7.3:** Camera integration for photo capture
```tsx
<CameraCapture>
  <video ref={videoRef} autoPlay playsInline />
  <canvas ref={canvasRef} style={{ display: 'none' }} />
  <Button onClick={capturePhoto}>
    <CameraIcon />
    Ambil Foto
  </Button>
</CameraCapture>
```

**AC-3.7.4:** Swipe gestures for form navigation
```typescript
const swipeHandlers = useSwipeable({
  onSwipedLeft: () => nextField(),
  onSwipedRight: () => previousField(),
});
```

**AC-3.7.5:** Offline support - data queued until connection
```typescript
const offlineQueue = useOfflineStorage({
  key: 'registration_queue',
  onOnline: () => syncQueue(),
});
```

**AC-3.7.6:** Sync when connection restored
```tsx
<SyncIndicator>
  {isOnline ? (
    <Status online>Online - Sinkronisasi aktif</Status>
  ) : (
    <Status offline>Offline - Data tersimpan lokal</Status>
  )}
</SyncIndicator>
```

**AC-3.7.7:** Progress indicator during sync
```tsx
{syncing && (
  <SyncProgress>
    <ProgressBar value={syncProgress} />
    <Message>Menyinkronkan {syncCount} data...</Message>
  </SyncProgress>
)}
```

---

#### Technical Implementation

**Mobile-First CSS:**
```css
/* Base: Mobile */
.form-field {
  width: 100%;
  margin-bottom: 1rem;
}

/* Tablet+ */
@media (min-width: 768px) {
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
}
```

**Service Worker:**
```typescript
// sw.js - Offline caching
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
```

---

#### Testing

**Device Tests:**
- [ ] Works on iPhone SE (375px)
- [ ] Works on iPad (768px)
- [ ] Camera capture works
- [ ] Swipe gestures work
- [ ] Offline mode functional

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Mobile responsive validated
- [ ] Camera integration working
- [ ] Swipe gestures working
- [ ] Offline queue functional
- [ ] Sync mechanism confirmed

---

## WEB-EPIC-4: DOCTOR CONSULTATION WORKSPACE STORIES

---

### WEB-S-4.1: Split-View Patient Context

**As a** doctor,
**I want to** split-view layout with persistent patient context,
**So that** patient information is always visible during consultation.

**Priority:** HIGH
**Estimate:** 4 days
**Dependencies:** WEB-S-EPIC-1, WEB-S-EPIC-3

---

#### Acceptance Criteria

**AC-4.1.1:** Left panel shows patient context (always visible)
```tsx
<ConsultationWorkspace>
  <PatientContextPanel>
    {/* Always visible - scrollable if needed */}
  </PatientContextPanel>
  <ConsultationMain>
    {/* Working area */}
  </ConsultationMain>
</ConsultationWorkspace>
```

**AC-4.1.2:** Patient header with photo, name, identifiers
```tsx
<PatientHeader>
  <PatientPhoto src={patient.photo} />
  <PatientInfo>
    <h3>{patient.name}</h3>
    <Identifiers>
      <Identifier label="RM" value={patient.rmNumber} />
      <Identifier label="BPJS" value={patient.bpjsNumber} />
      <Age age={patient.age} gender={patient.gender} />
    </Identifiers>
  </PatientInfo>
</PatientHeader>
```

**AC-4.1.3:** Critical alerts (allergies, comorbidities)
```tsx
<PatientAlerts>
  {patient.allergies.map(allergy => (
    <Alert critical>
      <AllergyIcon />
     ALERGI {allergy.allergen} - {allergy.reaction}
    </Alert>
  ))}
  {patient.comorbidities.map(comorbidity => (
    <Alert warning>
      <ComorbidIcon />
      {comorbidity.condition}
    </Alert>
  ))}
</PatientAlerts>
```

**AC-4.1.4:** Latest vitals with color-coded status
```tsx
<VitalsCard>
  <VitalsGrid>
    <VitalItem label="TD" value="130/80" unit="mmHg" status="normal" />
    <VitalItem label="HR" value="102" unit="x/mnt" status="warning" />
    <VitalItem label="RR" value="18" unit="x/mnt" status="normal" />
    <VitalItem label="SpO2" value="98" unit="%" status="normal" />
    <VitalItem label="Temp" value="36.8" unit="°C" status="normal" />
    <VitalItem label="GCS" value="15" unit="E4V5M6" status="normal" />
  </VitalsGrid>
</VitalsCard>
```

**AC-4.1.5:** Quick actions (history, medications, labs)
```tsx
<QuickActionsNav>
  <ActionButton icon="history" onClick={showHistory}>
    Riwayat Medis
  </ActionButton>
  <ActionButton icon="medication" onClick={showMedications}>
    Obat Saat Ini
  </ActionButton>
  <ActionButton icon="lab" onClick={showLabs}>
    Hasil Lab
  </ActionButton>
  <ActionButton icon="xray" onClick={showRadiology}>
    Radiologi
  </ActionButton>
</QuickActionsNav>
```

---

#### Technical Implementation

**Component:** `src/components/consultation/ConsultationWorkspace.tsx`

**Layout:**
```css
.consultation-workspace {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  height: calc(100vh - 64px);
}

@media (max-width: 1024px) {
  .consultation-workspace {
    grid-template-columns: 1fr;
  }
}
```

---

#### Testing

**Layout Tests:**
- [ ] Split view works on desktop
- [ ] Left panel always visible
- [ ] Responsive on tablet/mobile
- [ ] Alerts display correctly
- [ ] Vitals color-coded

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Split view functional
- [ ] Patient context complete
- [ ] Alerts prominent
- [ ] Quick actions working
- [ ] Responsive validated

---

### WEB-S-4.2: SOAP Notes Editor

**As a** doctor,
**I want to** SOAP notes editor with auto-save,
**So that** clinical documentation is saved and organized.

**Priority:** HIGH
**Estimate:** 4 days
**Dependencies:** WEB-S-EPIC-4.1

---

#### Acceptance Criteria

**AC-4.2.1:** SOAP sections (Subjective, Objective, Assessment, Plan)
```tsx
<SOAPNotesEditor>
  <Section label="Subjective (S)">
    <Textarea
      placeholder="Keluhan pasien menurut pasien sendiri"
      value={subjective}
      onChange={setSubjective}
    />
  </Section>
  <Section label="Objective (O)">
    <Textarea
      placeholder="Pemeriksaan fisik dan penunjang"
      value={objective}
      onChange={setObjective}
    />
  </Section>
  <Section label="Assessment (A)">
    <DiagnosisSearch onSelect={addDiagnosis} />
    <SelectedDiagnoses />
  </Section>
  <Section label="Plan (P)">
    <Textarea
      placeholder="Rencana tatalaksana"
      value={plan}
      onChange={setPlan}
    />
  </Section>
</SOAPNotesEditor>
```

**AC-4.2.2:** Auto-save every 30 seconds
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    autoSaveSOAP({ subjective, objective, assessment, plan });
  }, 30000);
  return () => clearInterval(interval);
}, [subjective, objective, assessment, plan]);
```

**AC-4.2.3:** Templates for common cases
```tsx
<Templates>
  <Template name="UMUM" onClick={loadTemplate('umum')} />
  <Template name="DEMAM" onClick={loadTemplate('demam')} />
  <Template name="BATUK" onClick={loadTemplate('batuk')} />
</Templates>
```

**AC-4.2.4:** Rich text formatting (bold, italic, list)
```tsx
<RichTextEditor value={plan} onChange={setPlan}>
  <Toolbar>
    <Button onClick={format('bold')}><BoldIcon /></Button>
    <Button onClick={format('italic')}><ItalicIcon /></Button>
    <Button onClick={format('list')}><ListIcon /></Button>
  </Toolbar>
</RichTextEditor>
```

**AC-4.2.5:** Character counter for each section
```tsx
<SectionFooter>
  <CharacterCount>{subjective.length} karakter</CharacterCount>
  <LastSaved>{lastSavedTime}</LastSaved>
</SectionFooter>
```

**AC-4.2.6:** Digital signature required
```tsx
<SOAPActions>
  <Button onClick={saveDraft}>Simpan Draft</Button>
  <Button onClick={signSOAP}>
    <SignatureIcon />
    Tandatangan & Simpan
  </Button>
</SOAPActions>
```

**AC-4.2.7:** Version control with audit trail
```tsx
<SOAPVersions>
  {versions.map(version => (
    <VersionItem>
      <VersionNumber>{version.number}</VersionNumber>
      <Timestamp>{version.timestamp}</Timestamp>
      <Author>{version.doctor}</Author>
    </VersionItem>
  ))}
</SOAPVersions>
```

---

#### Technical Implementation

**Component:** `src/components/consultation/SOAPNotesEditor.tsx`

**Auto-save Hook:**
```typescript
const useAutoSave = (data: SOAPData) => {
  const [lastSaved, setLastSaved] = useState<Date>();

  const save = useCallback(debounce(async (data) => {
    await api.saveSOAP(data);
    setLastSaved(new Date());
  }, 1000), []);

  useEffect(() => { save(data); }, [data, save]);

  return lastSaved;
};
```

---

#### Testing

**Integration Tests:**
- [ ] Auto-save works (30s interval)
- [ ] Templates load correctly
- [ ] Rich text formatting works
- [ ] Digital signature functional
- [ ] Version history shows

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Auto-save functional
- [ ] Templates working
- [ ] Rich text editor working
- [ ] Digital signature confirmed
- [ ] Version control validated

---

### WEB-S-4.3: ICD-10 Diagnosis Search

**As a** doctor,
**I want to** quick ICD-10 diagnosis entry,
**So that** I can document diagnoses efficiently.

**Priority:** HIGH
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-4.2

---

#### Acceptance Criteria

**AC-4.3.1:** Autocomplete search with <2 second response
```tsx
<DiagnosisSearch>
  <SearchInput
    placeholder="Cari diagnosa ICD-10... (Ctrl+K)"
    onInput={handleSearch}
  />
  <SearchResults>
    {results.map(diagnosis => (
      <ResultItem
        key={diagnosis.code}
        onClick={() => selectDiagnosis(diagnosis)}
      >
        <DiagnosisCode>{diagnosis.code}</DiagnosisCode>
        <DiagnosisName>{diagnosis.name}</DiagnosisName>
        <FrequentStar show={diagnosis.frequent} />
      </ResultItem>
    ))}
  </SearchResults>
</DiagnosisSearch>
```

**AC-4.3.2:** Keyboard shortcut (Ctrl+K)
```typescript
// Focus search on Ctrl+K
useKeyboardShortcut(['ctrl', 'k'], () => {
  searchInputRef.current?.focus();
});
```

**AC-4.3.3:** Favorites (frequently used diagnoses)
```tsx
<FavoriteDiagnoses>
  <SectionLabel>Sering Digunakan</SectionLabel>
  {favorites.map(diagnosis => (
    <FavoriteChip
      key={diagnosis.code}
      onClick={() => addDiagnosis(diagnosis)}
    >
      {diagnosis.code} - {diagnosis.name}
    </FavoriteChip>
  ))}
</FavoriteDiagnoses>
```

**AC-4.3.4:** Recently used diagnoses
```tsx
<RecentDiagnoses>
  <SectionLabel>Baru Saja Digunakan</SectionLabel>
  {recent.map(diagnosis => (
    <RecentChip
      key={diagnosis.code}
      onClick={() => addDiagnosis(diagnosis)}
    >
      {diagnosis.code} - {diagnosis.name}
    </RecentChip>
  ))}
</RecentDiagnoses>
```

**AC-4.3.5:** Diagnosis chips with remove button
```tsx
<SelectedDiagnoses>
  {diagnoses.map(diagnosis => (
    <DiagnosisChip key={diagnosis.code}>
      <Code>{diagnosis.code}</Code>
      <Name>{diagnosis.name}</Name>
      <RemoveButton onClick={() => remove(diagnosis.code)}>×</RemoveButton>
    </DiagnosisChip>
  ))}
</SelectedDiagnoses>
```

**AC-4.3.6:** Primary vs secondary diagnosis designation
```tsx
<DiagnosisChip>
  <Radio name="primary" checked={diagnosis.isPrimary} />
  <Code>{diagnosis.code}</Code>
  <Label>{diagnosis.name}</Label>
</DiagnosisChip>
```

---

#### Technical Implementation

**Component:** `src/components/consultation/DiagnosisSearch.tsx`

**Search API:**
```python
@router.get("/diagnosis/search")
async def search_diagnosis(query: str, limit: int = 10):
    # Fuzzy search ICD-10 database
    pass
```

**Debounced Search:**
```typescript
const searchDiagnosis = debounce(async (query: string) => {
  if (query.length < 2) return;
  const results = await api.searchDiagnosis(query);
  setResults(results);
}, 300);
```

---

#### Testing

**Performance Tests:**
- [ ] Search <2 seconds (p95)
- [ ] Debounce working
- [ ] Keyboard shortcut works
- [ ] Favorites load correctly

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Search <2 seconds validated
- [ ] Favorites functional
- [ ] Recent diagnoses working
- [ ] Primary designation working
- [ ] Remove button functional

---

### WEB-S-4.4: Electronic Prescription Writer

**As a** doctor,
**I want to** electronic prescription writing,
**So that** prescriptions are accurate and checked for interactions.

**Priority:** HIGH
**Estimate:** 5 days
**Dependencies:** WEB-S-EPIC-4.2

---

#### Acceptance Criteria

**AC-4.4.1:** Drug search (generic and brand) with auto-complete
```tsx
<PrescriptionWriter>
  <DrugSearch
    placeholder="Cari obat (generic atau brand)..."
    onSearch={handleDrugSearch}
  />
  <SearchResults>
    {results.map(drug => (
      <DrugResult key={drug.id}>
        <DrugName>{drug.genericName}</DrugName>
        <BrandNames>{drug.brandNames.join(', ')}</BrandNames>
        <Stock stock={drug.stock} />
        <Button onClick={() => addDrug(drug)}>Tambah</Button>
      </DrugResult>
    ))}
  </SearchResults>
</PrescriptionWriter>
```

**AC-4.4.2:** Dose and frequency selection
```tsx
<PrescriptionItem>
  <DrugName>{drug.name}</DrugName>
  <DoseSelect
    options={[5, 10, 20, 50, 100, 250, 500]}
    unit="mg"
  />
  <FrequencySelect
    options={[
      { value: 'od', label: 'Sekali sehari' },
      { value: 'bid', label: '2x sehari' },
      { value: 'tid', label: '3x sehari' },
      { value: 'qid', label: '4x sehari' },
    ]}
  />
  <Duration type="number" unit="hari" />
</PrescriptionItem>
```

**AC-4.4.3:** Drug interaction checking
```tsx
<InteractionChecker>
  {interactions.map(interaction => (
    <InteractionAlert severity={interaction.severity}>
      <InteractionIcon />
      {interaction.description}
      <Detail>
        {interaction.drug1} ↔ {interaction.drug2}: {interaction.effect}
      </Detail>
    </InteractionAlert>
  ))}
</InteractionChecker>
```

**AC-4.4.4:** Drug-disease interaction checking
```tsx
<DiseaseInteractionChecker patient={patient}>
  {diseaseInteractions.map(interaction => (
    <Alert warning>
      {interaction.drug} kontraindikasi untuk {interaction.condition}
    </Alert>
  ))}
</DiseaseInteractionChecker>
```

**AC-4.4.5:** Drug-allergy interaction checking
```tsx
<AllergyInteractionChecker patient={patient}>
  {allergyInteractions.map(interaction => (
    <Alert critical>
      <AllergyIcon />
      PASIEN ALERGI {interaction.allergen}!
      {interaction.drug} mengandung {interaction.allergen}
    </Alert>
  ))}
</AllergyInteractionChecker>
```

**AC-4.4.6:** BPJS formulary checking (coverage status)
```tsx
<FormularyStatus drug={drug}>
  {formulary.covered ? (
    <Badge success>Tercover BPJS</Badge>
  ) : (
    <Badge warning>Tidak Tercover - Pasien Bayar</Badge>
  )}
  {formulary.priorAuthRequired && (
    <Alert warning>Memerlukan Otorisasi Sebelumnya</Alert>
  )}
</FormularyStatus>
```

**AC-4.4.7:** Prescription printing with barcode
```tsx
<PrescriptionPreview>
  <PrescriptionHeader>
    <HospitalName>{hospital}</HospitalName>
    <PrescriptionNumber>{number}</PrescriptionNumber>
  </PrescriptionHeader>
  <PatientInfo>{patient}</PatientInfo>
  <MedicationsList>
    {medications.map(med => (
      <MedicationItem>{med}</MedicationItem>
    ))}
  </MedicationsList>
  <Barcode value={prescriptionNumber} />
  <DoctorSignature>{doctor}</DoctorSignature>
</PrescriptionPreview>
```

**AC-4.4.8:** Electronic prescription to pharmacy
```tsx
<PrescriptionActions>
  <Button onClick={printPrescription}>Cetak Resep</Button>
  <Button primary onClick={sendToPharmacy}>
    <SendIcon />
    Kirim ke Apotek
  </Button>
</PrescriptionActions>
```

---

#### Technical Implementation

**Component:** `src/components/consultation/PrescriptionWriter.tsx`

**Interaction Checking API:**
```python
@router.post("/prescriptions/check-interactions")
async def check_interactions(medications: List[Medication]):
    # Return drug-drug, drug-disease, drug-allergy interactions
    pass
```

---

#### Testing

**Integration Tests:**
- [ ] Drug search works
- [ ] All interaction types checked
- [ ] Formulary status displays
- [ ] Barcode generates
- [ ] Send to pharmacy works

---

#### Definition of Done

- [x] All AC criteria met
- [ ] All interaction checks working
- [ ] Formulary checking functional
- [ ] Barcode generation confirmed
- [ ] Pharmacy send working
- [ ] Print functional

---

### WEB-S-4.5: Lab/Radiology Ordering

**As a** doctor,
**I want to** lab/radiology electronic ordering,
**So that** tests are ordered efficiently and tracked.

**Priority:** MEDIUM
**Estimate:** 4 days
**Dependencies:** WEB-S-EPIC-4.2

---

#### Acceptance Criteria

**AC-4.5.1:** Test catalog search and package selection
```tsx
<TestOrdering type="lab">
  <TestCatalogSearch onSearch={handleSearch} />
  <TestCategory>
    <CategoryHeader>Hematologi Lengkap</CategoryHeader>
    <TestPackage name="Hemoglobin" />
    <TestPackage name="Leukosit" />
    <TestPackage name="Trombosit" />
    <TestPackage name="Hematokrit" />
  </TestCategory>
</TestOrdering>
```

**AC-4.5.2:** Priority assignment (routine, urgent, STAT)
```tsx
<TestPriority>
  <Radio name="priority" value="routine" label="Routine" default />
  <Radio name="priority" value="urgent" label="Urgent" />
  <Radio name="priority" value="stat" label="STAT (Segera)" />
</TestPriority>
```

**AC-4.5.3:** Clinical indication (required for some tests)
```tsx
<ClinicalIndication required={test.requiresIndication}>
  <Textarea
    label="Indikasi Klinis"
    placeholder="Jelaskan indikasi pemeriksaan..."
  />
</ClinicalIndication>
```

**AC-4.5.4:** Insurance pre-authorization
```tsx
<PreAuthorization test={test} insurance={patient.insurance}>
  {test.requiresPriorAuth && (
    <PriorAuthAlert>
      Pemeriksaan ini memerlukan otorisasi BPJS sebelum dilakukan.
      <Button onClick={requestAuth}>Request Otorisasi</Button>
    </PriorAuthAlert>
  )}
</PreAuthorization>
```

**AC-4.5.5:** BPJS SEP automatic creation/update
```typescript
const orderTests = async (tests: Test[]) => {
  const order = await api.createLabOrder({ tests, patientId });

  // Auto-update SEP if needed
  if (requiresSEPUpdate(order)) {
    await api.updateSEP({ sepNumber: patient.sepNumber, tests });
  }

  return order;
};
```

**AC-4.5.6:** Order tracking (pending, in-progress, completed)
```tsx
<OrderTracking orderId={orderId}>
  <OrderStatus status={order.status}>
    {order.status === 'pending' && 'Menunggu Sampel'}
    {order.status === 'in-progress' && 'Sedang Diperiksa'}
    {order.status === 'completed' && 'Selesai'}
  </OrderStatus>
  <EstimatedTime>Estimasi: {order.estimatedTime}</EstimatedTime>
</OrderTracking>
```

**AC-4.5.7:** Result viewing and attachment to encounter
```tsx
<LabResults orderId={orderId}>
  {results.map(result => (
    <ResultItem>
      <TestName>{result.testName}</TestName>
      <ResultValue value={result.value} unit={result.unit} />
      <ReferenceRange range={result.referenceRange} />
      <AbnormalFlag abnormal={result.abnormal} />
      <AttachmentButton onClick={() => attachToEncounter(result)} />
    </ResultItem>
  ))}
</LabResults>
```

---

#### Technical Implementation

**Component:** `src/components/consultation/TestOrdering.tsx`

**API Endpoints:**
```python
@router.post("/lab/orders")
async def create_lab_order(order: LabOrderCreate):
    pass

@router.get("/lab/orders/{order_id}/results")
async def get_lab_results(order_id: str):
    pass
```

---

#### Testing

**Integration Tests:**
- [ ] Test catalog search works
- [ ] Priority assignment works
- [ ] Prior auth flow functional
- [ ] Order tracking updates
- [ ] Result viewing works

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Lab ordering functional
- [ ] Radiology ordering functional
- [ ] Prior auth working
- [ ] Order tracking confirmed
- [ ] Result viewing working

---

### WEB-S-4.6: Patient History Timeline

**As a** doctor,
**I want to** patient history timeline visualized,
**So that** I can see medical history chronologically.

**Priority:** MEDIUM
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-4.1

---

#### Acceptance Criteria

**AC-4.6.1:** Timeline showing visits, hospitalizations, surgeries
```tsx
<PatientTimeline patientId={patientId}>
  <Timeline>
    {events.map(event => (
      <TimelineEvent key={event.id} date={event.date}>
        <EventIcon type={event.type} />
        <EventContent>
          <EventTitle>{event.title}</EventTitle>
          <EventDate>{event.date}</EventDate>
          <EventDetails>{event.details}</EventDetails>
        </EventContent>
      </TimelineEvent>
    ))}
  </Timeline>
</PatientTimeline>
```

**AC-4.6.2:** Allergies timeline (when diagnosed, reactions)
```tsx
<AllergiesTimeline>
  {allergies.map(allergy => (
    <AllergyEvent allergy={allergy}>
      <Allergen>{allergy.allergen}</Allergen>
      <Reaction>{allergy.reaction}</Reaction>
      <Severity level={allergy.severity} />
      <DiagnosedDate>{allergy.diagnosedDate}</DiagnosedDate>
    </AllergyEvent>
  ))}
</AllergiesTimeline>
```

**AC-4.6.3:** Chronic conditions tracking
```tsx
<ChronicConditions>
  {conditions.map(condition => (
    <ConditionTracking condition={condition}>
      <ConditionName>{condition.name}</ConditionName>
      <DiagnosisDate>{condition.diagnosedDate}</DiagnosisDate>
      <Status status={condition.status} />
      <Treatments>
        {condition.medications.map(med => (
          <Medication>{med}</Medication>
        ))}
      </Treatments>
    </ConditionTracking>
  ))}
</ChronicConditions>
```

**AC-4.6.4:** Medication history visualization
```tsx
<MedicationTimeline>
  {medications.map(med => (
    <MedicationEvent medication={med}>
      <DrugName>{med.drug}</DrugName>
      <Dose>{med.dose}</Dose>
      <Period>{med.startDate} - {med.endDate || 'Sekarang'}</Period>
      <Prescriber>{med.doctor}</Prescriber>
    </MedicationEvent>
  ))}
</MedicationTimeline>
```

**AC-4.6.5:** Discontinuation tracking
```tsx
<DiscontinuedMedications>
  {discontinued.map(med => (
    <DiscontinuedMedication medication={med}>
      <DrugName>{med.drug}</DrugName>
      <DiscontinuationDate>{med.discontinuedDate}</DiscontinuationDate>
      <Reason>{med.reason}</Reason>
    </DiscontinuedMedication>
  ))}
</DiscontinuedMedications>
```

---

#### Technical Implementation

**Component:** `src/components/consultation/PatientTimeline.tsx`

**Timeline Visualization:**
```tsx
const TimelineEvent = ({ type, date, children }) => (
  <div className="timeline-event">
    <div className={`timeline-icon ${type}`}>{getIcon(type)}</div>
    <div className="timeline-content">
      <div className="timeline-date">{formatDate(date)}</div>
      {children}
    </div>
  </div>
);
```

---

#### Testing

**Visual Tests:**
- [ ] Timeline displays correctly
- [ ] Events ordered chronologically
- [ ] Icons match event types
- [ ] Filtering works (by type, date range)

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Timeline visualization working
- [ ] All event types showing
- [ ] Filtering functional
- [ ] Discontinuation tracked
- [ ] Visual clarity validated

---

### WEB-S-4.7: Allergy & Medication Alerts

**As a** doctor,
**I want to** allergy and medication alerts prominent,
**So that** patient safety is prioritized.

**Priority:** CRITICAL
**Estimate:** 2 days
**Dependencies:** WEB-S-EPIC-4.1, WEB-S-EPIC-4.4

---

#### Acceptance Criteria

**AC-4.7.1:** Prominent allergy alerts (cannot be dismissed)
```tsx
<AllergyAlerts patient={patient}>
  {patient.allergies.map(allergy => (
    <Alert critical permanent>
      <AllergyIcon />
      <strong>ALERGI {allergy.allergen.toUpperCase()}</strong>
      <Reaktion>{allergy.reaction}</Reaktion>
      <Severity>Severity: {allergy.severity}</Severity>
    </Alert>
  ))}
</AllergyAlerts>
```

**AC-4.7.2:** Medication interaction warnings (require confirmation)
```tsx
<InteractionWarnings>
  {interactions.map(interaction => (
    <InteractionAlert warning>
      <WarningIcon />
      <strong>Interaksi Obat:</strong>
      {interaction.drug1} ↔ {interaction.drug2}
      <Effect>{interaction.effect}</Effect>
      <Checkbox
        label="Saya memahami risiko dan ingin melanjutkan"
        required
        onChange={setAcknowledged}
      />
    </InteractionAlert>
  ))}
</InteractionWarnings>
```

**AC-4.7.3:** Duplicate therapy warnings
```tsx
<DuplicateTherapyChecker>
  {duplicates.map(dup => (
    <Alert warning>
      <WarningIcon />
      Duplikat Terapi: {dup.drug} ada di {dup.count} obat
    </Alert>
  ))}
</DuplicateTherapyChecker>
```

**AC-4.7.4:** Contraindication alerts (drug-disease)
```tsx
<ContraindicationAlerts>
  {contraindications.map(contra => (
    <Alert critical>
      <StopIcon />
      <strong>KONTRAINDIKASI:</strong>
      {contra.drug} tidak boleh digunakan untuk {contra.condition}
    </Alert>
  ))}
</ContraindicationAlerts>
```

**AC-4.7.5:** Dose adjustment alerts (renal/hepatic impairment)
```tsx
<DoseAdjustmentAlerts patient={patient}>
  {patient.renalImpairment && (
    <Alert warning>
      Dose {drug} perlu disesuaikan untuk gangguan ginjal
      <Recommendation>{recommendedDose}</Recommendation>
    </Alert>
  )}
</DoseAdjustmentAlerts>
```

**AC-4.7.6:** Alerts block prescription submission until acknowledged
```tsx
<PrescriptionSubmit
  disabled={hasUnacknowledgedAlerts}
  onBlocked={() => showAlertDialog()}
>
  {hasUnacknowledgedAlerts ? (
    <Alert error>
      Mohon konfirmasi semua peringatan interaksi obat
    </Alert>
  ) : (
    <Button onClick={submitPrescription}>Kirim Resep</Button>
  )}
</PrescriptionSubmit>
```

---

#### Technical Implementation

**Component:** `src/components/consultation/SafetyAlerts.tsx`

**Alert State Management:**
```typescript
const [alerts, setAlerts] = useState<SafetyAlert[]>([]);
const [acknowledged, setAcknowledged] = useState<Set<string>>(new Set());

const acknowledgeAlert = (alertId: string) => {
  setAcknowledged(prev => new Set(prev).add(alertId));
};

const canSubmit = alerts.every(alert => acknowledged.has(alert.id));
```

---

#### Testing

**Integration Tests:**
- [ ] Allergy alerts always show
- [ ] Interaction warnings require acknowledgment
- [ ] Duplicate therapy detected
- [ ] Contraindications block prescription
- [ ] Dose adjustments recommended

---

#### Definition of Done

- [x] All AC criteria met
- [ ] All alert types working
- [ ] Acknowledgment functional
- [ ] Blocking confirmed
- [ ] Safety validated (medical review)

---

## WEB-EPIC-5: EMERGENCY TRIAGE SYSTEM STORIES

---

### WEB-S-5.1: Rapid Vitals Entry

**As a** triage nurse,
**I want to** compact form for <1 minute vitals entry,
**So that** triage completes quickly.

**Priority:** HIGH
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-1

---

#### Acceptance Criteria

**AC-5.1.1:** Compact vitals grid (TD, Pulse, RR, SpO2, Temp, GCS)
```tsx
<VitalsGrid compact>
  <VitalInput label="TD" placeholder="Sys/Dia" />
  <VitalInput label="Nadi" placeholder="x/mnt" />
  <VitalInput label="RR" placeholder="x/mnt" />
  <VitalInput label="SpO2" placeholder="%" />
  <VitalInput label="Temp" placeholder="°C" />
  <VitalSelect label="GCS" options={gcsOptions} />
</VitalsGrid>
```

**AC-5.1.2:** Large touch targets for tablet use
```css
@media (max-width: 768px) {
  .vital-input {
    min-height: 48px;
    font-size: 18px;
  }
}
```

**AC-5.1.3:** Auto-focus and tab flow optimization
```tsx
<VitalsForm>
  <VitalInput name="bpSys" autoFocus nextField="pulse" />
  <VitalInput name="pulse" nextField="rr" />
  {/* Tab moves to next field automatically */}
</VitalsForm>
```

**AC-5.1.4:** Abnormal value highlighting
```tsx
<VitalInput
  value={systolic}
  status={getStatus('bp', systolic)}  // normal, warning, critical
/>
{getStatus('bp', systolic) === 'critical' && (
  <CriticalAlert>TEKANAN DARAH RENDAH!</CriticalAlert>
)}
```

**AC-5.1.5:** Quick pain scale (emoji-based)
```tsx
<PainScale>
  <PainOption level="0" emoji="😊" label="0 - Tidak Nyeri" />
  <PainOption level="3" emoji="🙂" label="1-3 - Ringan" />
  <PainOption level="6" emoji="😐" label="4-6 - Sedang" />
  <PainOption level="9" emoji="😣" label="7-10 - Berat" />
</PainScale>
```

---

#### Technical Implementation

**Component:** `src/components/triage/RapidVitalsEntry.tsx`

---

#### Testing

**Performance Tests:**
- [ ] Vitals entry <60 seconds
- [ ] Tab flow works
- [ ] Touch targets validated
- [ ] Abnormal highlighting correct

---

#### Definition of Done

- [x] All AC criteria met
- [ ] 60-second target validated
- [ ] Touch-friendly on tablet
- [ ] Tab flow smooth
- [ ] Abnormal highlighting working

---

### WEB-S-5.2: Chief Complaint Quick-Tags

**As a** triage nurse,
**I want to** one-tap chief complaint quick-tags,
**So that** common complaints are captured instantly.

**Priority:** HIGH
**Estimate:** 2 days
**Dependencies:** WEB-S-EPIC-5.1

---

#### Acceptance Criteria

**AC-5.2.1:** One-tap common emergency complaints
```tsx
<ChiefComplaintQuickTags>
  <ComplaintTag emoji="😮" label="Sesak Napas" />
  <ComplaintTag emoji="💔" label="Nyeri Dada" />
  <ComplaintTag emoji="😵" label="Pingsan" />
  <ComplaintTag emoji="🩹" label="Trauma/Luka" />
  <ComplaintTag emoji="🤒" label="Demam Tinggi" />
  <ComplaintTag emoji="⚡" label="Kejang" />
</ChiefComplaintQuickTags>
```

**AC-5.2.2:** Tags populate chief complaint field
```tsx
<ComplaintTags>
  {complaintTags.map(tag => (
    <TagButton onClick={() => addComplaint(tag.label)}>
      {tag.emoji} {tag.label}
    </TagButton>
  ))}
</ComplaintTags>

<SelectedComplaints>
  {complaints.map(comp => (
    <ComplaintChip>{comp}</ComplaintChip>
  ))}
</SelectedComplaints>
```

**AC-5.2.3:** Custom complaint input (additional detail)
```tsx
<CustomComplaint>
  <Textarea
    label="Keluhan Tambahan"
    placeholder="Jelaskan keluhan lain..."
  />
</CustomComplaint>
```

---

#### Technical Implementation

**Component:** `src/components/triage/ChiefComplaintTags.tsx`

---

#### Testing

**Interaction Tests:**
- [ ] Taps add complaints
- [ ] Multiple tags can be selected
- [ ] Custom field works
- [ ] Clear all button functional

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Quick-tags functional
- [ ] Custom input working
- [ ] Touch-friendly
- [ ] Clear all working

---

### WEB-S-5.3: Auto-Calculate Triage

**As a** triage nurse,
**I want to** auto-calculate triage from vitals,
**So that** triage category is determined objectively.

**Priority:** HIGH
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-5.1

---

#### Acceptance Criteria

**AC-5.3.1:** Algorithm from vitals → Merah/Kuning/Hijau
```typescript
const calculateTriage = (vitals: Vitals) => {
  let score = 0;

  if (vitals.bpSys < 90 || vitals.bpDia < 60) score += 3;
  if (vitals.pulse > 120 || vitals.pulse < 50) score += 2;
  if (vitals.rr > 24 || vitals.rr < 10) score += 2;
  if (vitals.spo2 < 90) score += 3;
  if (vitals.gcs < 14) score += 2;

  if (score >= 5) return 'MERAH';
  if (score >= 3) return 'KUNING';
  return 'HIJAU';
};
```

**AC-5.3.2:** Display color-coded result immediately
```tsx
<TriageResult level={triageLevel}>
  {triageLevel === 'MERAH' && (
    <TriageMerah>
      <h3>MERAH</h3>
      <p>GAWAT DARURAT - Segera tangani</p>
    </TriageMerah>
  )}
  {triageLevel === 'KUNING' && (
    <TriageKuning>
      <h3>KUNING</h3>
      <p>SEMI-URGENT - Perlu perhatian</p>
    </TriageKuning>
  )}
  {triageLevel === 'HIJAU' && (
    <TriageHijau>
      <h3>HIJAU</h3>
      <p>NON-URGENT - Tunggu giliran</p>
    </TriageHijau>
  )}
</TriageResult>
```

**AC-5.3.3:** Show reasons for triage assignment
```tsx
<TriageReasons>
  <h4>Alasan:</h4>
  <ul>
    {reasons.map(r => (
      <li className={r.critical ? 'critical' : ''}>
        {r.critical ? '✗' : '⚠'} {r.text}
      </li>
    ))}
  </ul>
</TriageReasons>
```

**AC-5.3.4:** Manual override option
```tsx
<ManualOverride>
  <Checkbox label="Tentukan triage manual" />
  {override && (
    <TriageSelect>
      <Option value="merah">MERAH</Option>
      <Option value="kuning">KUNING</Option>
      <Option value="hijau">HIJAU</Option>
    </TriageSelect>
  )}
</ManualOverride>
```

**AC-5.3.5:** Recalculate on vitals change
```typescript
useEffect(() => {
  const newTriage = calculateTriage(vitals);
  setTriageLevel(newTriage);
}, [vitals]);
```

---

#### Technical Implementation

**Component:** `src/components/triage/TriageCalculator.tsx`

---

#### Testing

**Algorithm Tests:**
- [ ] All critical combinations → Merah
- [ ] Warning combinations → Kuning
- [ ] Normal combinations → Hijau
- [ ] Override works
- [ ] Recalculate on change

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Algorithm validated
- [ ] Colors correct
- [ ] Reasons displayed
- [ ] Override working
- [ ] Real-time calculation

---

### WEB-S-5.4: Triage Result Display

**As a** triage nurse,
**I want to** triage result displayed with color-coded cards,
**So that** category is immediately recognizable.

**Priority:** HIGH
**Estimate:** 2 days
**Dependencies:** WEB-S-EPIC-5.3

---

#### Acceptance Criteria

**AC-5.4.1:** Large, color-coded triage card
```tsx
<TriageCard level={triageLevel} size="large">
  <TriageLevel level={triageLevel}>
    {triageLevel.toUpperCase()}
  </TriageLevel>
  <Description>{getTriageDescription(triageLevel)}</Description>
</TriageCard>
```

**AC-5.4.2:** Action recommendations per triage level
```tsx
<TriageRecommendations level={triageLevel}>
  {triageLevel === 'MERAH' && (
    <>
      <Recommendation priority="critical">
        <Icon>🚨</Icon>
        Pasang di Resusitasi
      </Recommendation>
      <Recommendation priority="critical">
        <Icon>❤️</Icon>
        Pantau ECG Kontinyu
      </Recommendation>
      <Recommendation priority="critical">
        <Icon>💉</Icon>
        Akses IV Tambah
      </Recommendation>
    </>
  )}
  </TriageRecommendations>
```

**AC-5.4.3:** Estimated wait time per triage level
```tsx
<EstimatedWait level={triageLevel}>
  {triageLevel === 'MERAH' && 'Segera (0 menit)'}
  {triageLevel === 'KUNING' && '<15 menit'}
  {triageLevel === 'HIJAU' && '30-60 menit'}
</EstimatedWait>
```

**AC-5.4.4:** Quick action buttons
```tsx
<QuickActions>
  {triageLevel === 'MERAH' && (
    <Button variant="coral" onClick={activateCodeBlue}>
      <EmergencyIcon />
      AKTIVASI KODE BIRU
    </Button>
  )}
  <Button onClick={assignToBed}>
    Pasang di {getRecommendedLocation(triageLevel)}
  </Button>
</QuickActions>
```

**AC-5.4.5:** Print triage ticket
```tsx
<TriageTicket>
  <HospitalName>{hospital}</HospitalName>
  <TriageLevel level={triageLevel}>{patient.name}</TriageLevel>
  <QueueNumber>{queueNumber}</QueueNumber>
  <Timestamp>{now}</Timestamp>
  <Barcode value={triageId} />
</TriageTicket>
```

---

#### Technical Implementation

**Component:** `src/components/triage/TriageResultCard.tsx`

---

#### Testing

**Visual Tests:**
- [ ] All triage levels display correctly
- [ ] Colors match design tokens
- [ ] Recommendations accurate
- [ ] Print ticket formatted

---

#### Definition of Done

- [x] All AC criteria met
- [ ] All triage levels working
- [ ] Recommendations accurate
- [ ] Wait times estimated
- [ ] Actions functional
- [ ] Print working

---

### WEB-S-5.5: Emergency Activation

**As a** triage nurse,
**I want to** "Kode Biru" button with alerts,
**So that** emergency team is activated immediately.

**Priority:** CRITICAL
**Estimate:** 3 days
**Dependencies:** WEB-S-EPIC-5.4

---

#### Acceptance Criteria

**AC-5.5.1:** Prominent "Kode Biru" activation button
```tsx
<EmergencyActivation>
  <CodeBlueButton
    variant="coral"
    size="lg"
    onClick={activateCodeBlue}
  >
    <EmergencyIcon />
    AKTIVASI KODE BIRU
  </CodeBlueButton>
</EmergencyActivation>
```

**AC-5.5.2:** Confirmation dialog (prevent accidental activation)
```tsx
<ConfirmDialog isOpen={showConfirm}>
  <DialogHeader>
    <AlertIcon />
    Konfirmasi Kode Biru
  </DialogHeader>
  <DialogContent>
    <p>Anda akan mengaktifkan KODE BIRU.</p>
    <p>Pasien: {patient.name}</p>
    <p>Lokasi: {location}</p>
    <Warning>Tim resusitasi akan dipanggil!</Warning>
  </DialogContent>
  <DialogActions>
    <Button onClick={cancel}>Batal</Button>
    <Button variant="coral" onClick={confirm}>
      Ya, Aktifkan Kode Biru
    </Button>
  </DialogActions>
</ConfirmDialog>
```

**AC-5.5.3:** Visual and audio alerts throughout hospital
```tsx
<CodeBlueAlert active={codeBlueActive}>
  <FlashMessage>KODE BIRU - IGD</FlashMessage>
  <AudioAlert src="/sounds/code-blue.mp3" loop />
  <Location>{location}</Location>
  <PatientInfo>{patient.name}</PatientInfo>
</CodeBlueAlert>
```

**AC-5.5.4:** Team notification (resusitasi, doctor, nurse)
```tsx
<TeamNotification>
  <Notification sentTo="resusitasi">
    Kode Biru di IGD - Pasien: {patient.name}
  </Notification>
  <Notification sentTo="doctor-on-call">
    Kode Biru di IGD - Segera ke lokasi!
  </Notification>
  <Notification sentTo="igd-nurses">
    Kode Biru diaktifkan - Siapkan resusitasi!
  </Notification>
</TeamNotification>
```

**AC-5.5.5:** Code Blue deactivation (after resolved)
```tsx
<CodeBlueActive active={codeBlueActive}>
  <PatientInfo>Pasien: {patient.name}</PatientInfo>
  <Timer active={true}>{elapsedTime}</Timer>
  <Button variant="coral" onClick={deactivateCodeBlue}>
    Nonaktifkan Kode Biru (Pasien Stabil)
  </Button>
</CodeBlueActive>
```

**AC-5.5.6:** Code Blue log (for quality improvement)
```tsx
<CodeBlueLog>
  <LogEntry timestamp={start}>
    Kode Biru diaktifkan: {patient.name} di {location}
  </LogEntry>
  <LogEntry timestamp={end}>
    Kode Biru dinonaktifkan setelah {duration}
  </LogEntry>
  <LogEntry>Outcome: {outcome}</LogEntry>
</CodeBlueLog>
```

---

#### Technical Implementation

**Component:** `src/components/triage/EmergencyActivation.tsx`

**WebSocket Broadcast:**
```typescript
const broadcastCodeBlue = async (data: CodeBlueData) => {
  await websocket.broadcast({
    type: 'CODE_BLUE',
    data: {
      active: true,
      patient: data.patient,
      location: data.location,
      timestamp: new Date(),
    },
    to: ['igd', 'resusitasi', 'doctor-on-call'],
  });
};
```

---

#### Testing

**Integration Tests:**
- [ ] Confirmation dialog shows
- [ ] Accidental activation prevented
- [ ] Visual alerts broadcast
- [ ] Audio plays on loop
- [ ] Team notifications sent
- [ ] Deactivation works
- [ ] Log created

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Confirmation dialog working
- [ ] Alerts broadcast hospital-wide
- [ ] Audio notifications working
- [ ] Team notifications sent
- [ ] Deactivation functional
- [ ] Logging confirmed

---

### WEB-S-5.6: Triage Timer

**As a** triage nurse,
**I want to** prominent <2 minute timer,
**So that** I track triage completion time.

**Priority:** HIGH
**Estimate:** 1 day
**Dependencies:** WEB-S-EPIC-5.1

---

#### Acceptance Criteria

**AC-5.6.1:** Prominent timer display
```tsx
<TriageTimer>
  <TimerLabel>Waktu Triase:</TimerLabel>
  <TimerValue
    value={elapsedTime}
    warningAt={90}  // Yellow at 90 seconds
    criticalAt={110}  // Red at 110 seconds
  />
  <TimerUnit>detik</TimerUnit>
</TriageTimer>
```

**AC-5.6.2:** Color-coded urgency (green → yellow → red)
```tsx
<TimerDisplay seconds={elapsedTime}>
  {elapsedTime < 60 && <TimerGreen>{formatTime(elapsedTime)}</TimerGreen>}
  {elapsedTime >= 60 && elapsedTime < 110 && <TimerYellow>{formatTime(elapsedTime)}</TimerYellow>}
  {elapsedTime >= 110 && <TimerRed>{formatTime(elapsedTime)}</TimerRed>}
</TimerDisplay>
```

**AC-5.6.3:** Auto-start on first vital entry
```typescript
useEffect(() => {
  if (firstVitalEntered && !timerStarted) {
    startTimer();
    setTimerStarted(true);
  }
}, [firstVitalEntered]);
```

**AC-5.6.4:** Auto-stop on triage completion
```typescript
const stopTimerOnComplete = () => {
  if (triageComplete) {
    stopTimer();
    logTriageTime(elapsedTime);
  }
};
```

**AC-5.6.5:** Visual countdown animation
```tsx
<TimerCountdown>
  <CircleProgress value={elapsedTime} max={120}>
    <TimerText>{120 - elapsedTime}s</TimerText>
  </CircleProgress>
</TimerCountdown>
```

---

#### Technical Implementation

**Component:** `src/components/triage/TriageTimer.tsx`

**Timer Hook:**
```typescript
const useTriageTimer = (maxSeconds: number = 120) => {
  const [elapsed, setElapsed] = useState(0);
  const [running, setRunning] = useState(false);

  const start = () => setRunning(true);
  const stop = () => setRunning(false);

  useEffect(() => {
    if (!running) return;
    const interval = setInterval(() => {
      setElapsed(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [running]);

  return { elapsed, running, start, stop };
};
```

---

#### Testing

**Functional Tests:**
- [ ] Timer starts on first entry
- [ ] Timer stops on complete
- [ ] Color changes correctly
- [ ] Countdown animation works
- [ ] Time logged on stop

---

#### Definition of Done

- [x] All AC criteria met
- [ ] Timer functional
- [ ] Color coding working
- [ ] Auto-start confirmed
- [ ] Auto-stop confirmed
- [ ] Animation smooth

---

## DOCUMENT STATUS

**Last Updated:** 2026-01-13
**Version:** 2.0
**Status:** COMPLETE

**Stories Summary:**
- WEB-EPIC-1: 9 stories (Component Library) ✅
- WEB-EPIC-2: 5 stories (BPJS Integration) ✅
- WEB-EPIC-3: 7 stories (Patient Registration) ✅
- WEB-EPIC-4: 7 stories (Doctor Workspace) ✅
- WEB-EPIC-5: 6 stories (Emergency Triage) ✅

**Total:** 34 stories fully documented

---

**NEXT STEPS:**
1. ✅ Epics documented (`web-epics.md`)
2. ✅ Stories documented (`web-stories.md`)
3. ⏭️ Create Sprint 1 backlog
4. ⏭️ Begin implementation

---

**Document maintained by:** BMAD Product Team
**Questions?** Contact: Fitra (Project Owner)
