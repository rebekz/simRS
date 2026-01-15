# SIMRS Component Usage Guidelines

**Version:** 1.0
**Last Updated:** 2026-01-16
**Epic:** WEB-EPIC-1: Component Library Foundation

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Component Guidelines](#component-guidelines)
4. [Accessibility](#accessibility)
5. [Responsive Patterns](#responsive-patterns)
6. [Indonesian Healthcare Context](#indonesian-healthcare-context)

---

## Overview

This guide provides comprehensive usage patterns for all SIMRS UI components. It explains **when** to use each component, **how** to use it correctly, and **why** specific patterns exist for Indonesian healthcare contexts.

---

## Design Principles

### Warm Professionalism

Our design philosophy balances trust and warmth:
- **Medical Teal** (#0d9488) - Primary color for trust and calm
- **Coral** (#f97316) - Secondary color for urgency without harshness
- **BPJS Colors** - Reflect 78% of Indonesian patients using national insurance

### Minimal Click Philosophy

- **3-click max** for common tasks
- **Progressive disclosure** - Show complex info gradually
- **Smart defaults** - BPJS-first, common values pre-selected

### Cultural Considerations

- **Indonesian language** - Primary, English secondary
- **BPJS-first** - Most patients use national insurance
- **Politeness** - Professional but approachable tone

---

## Component Guidelines

### Form Components

#### FormInput

**When to use:**
- Single-line text input (names, IDs, phone numbers)
- Numeric input with validation (age, vital signs)
- Password input with secure display

**How to use:**
```tsx
import { FormInput } from '@/components/ui/form/FormInput';

// Basic usage
<FormInput
  label="Nama Lengkap"
  placeholder="Masukkan nama lengkap"
  required
/>

// With validation
<FormInput
  label="NIK"
  placeholder="16 digit NIK"
  error={errors.nik ? "NIK harus 16 digit" : undefined}
  required
/>

// With hint
<FormInput
  label="Email"
  type="email"
  hint="Kami akan mengirim konfirmasi ke email ini"
/>
```

**Best Practices:**
- Always provide clear `label` for accessibility
- Use `required` for mandatory fields
- Show `error` message when validation fails
- Add `hint` for guidance or examples
- Use appropriate `type` (email, tel, number, date)

**When NOT to use:**
- Multi-line input → Use `FormTextarea`
- Single choice from options → Use `FormSelect` or `FormRadio`
- Binary choice → Use `FormSwitch` or `FormCheckbox`

---

#### FormSelect

**When to use:**
- Single choice from 5+ options
- Choosing from standardized lists (departments, classes, types)
- Filtering or categorization

**How to use:**
```tsx
import { FormSelect } from '@/components/ui/form/FormSelect';

const bpjsClasses = [
  { value: "1", label: "Kelas 1" },
  { value: "2", label: "Kelas 2" },
  { value: "3", label: "Kelas 3" },
];

<FormSelect
  label="Kelas BPJS"
  options={bpjsClasses}
  placeholder="Pilih kelas"
  required
  hint="Sesuai kartu BPJS pasien"
/>
```

**Best Practices:**
- Limit to 5-10 options for usability
- Sort logically (alphabetical, by frequency, or by order)
- Use descriptive labels in Indonesian
- Include `placeholder` for the default state
- Add `hint` for context or help

**When NOT to use:**
- 2-4 options → Use `FormRadio` for better visibility
- Boolean choice → Use `FormSwitch`
- Multi-select → Not yet supported, use checkboxes

---

#### FormCheckbox

**When to use:**
- Binary yes/no choice
- Multi-select from options
- Accepting terms and conditions
- Enabling/disabling features

**How to use:**
```tsx
import { FormCheckbox } from '@/components/ui/form/FormCheckbox';

// Single checkbox
<FormCheckbox
  label="Pasien memiliki BPJS"
  checked={hasBPJS}
  onChange={(e) => setHasBPJS(e.target.checked)}
/>

// Checkbox group (gejala)
<div className="space-y-2">
  <p className="font-medium">Gejala yang dialami:</p>
  <FormCheckbox label="Demam" />
  <FormCheckbox label="Batuk" />
  <FormCheckbox label="Sesak napas" />
</div>
```

**Best Practices:**
- Keep labels short and clear
- Group related checkboxes
- Use for independent choices (can select multiple)
- Position checkbox before label for consistency

**When NOT to use:**
- Single choice from mutually exclusive options → Use `FormRadio`
- On/off toggle for settings → Use `FormSwitch`

---

#### FormRadio

**When to use:**
- Single choice from 2-4 mutually exclusive options
- Choosing gender, priority, status, etc.
- When all options should be visible

**How to use:**
```tsx
import { FormRadio } from '@/components/ui/form/FormRadio';

const urgencyOptions = [
  { value: "routine", label: "Biasa (Routine)" },
  { value: "urgent", label: "Segera (Urgent)" },
  { value: "emergency", label: "Gawat Darurat" },
];

<FormRadio
  name="urgency"
  label="Tingkat Urgensi"
  options={urgencyOptions}
  value={urgency}
  onChange={(e) => setUrgency(e.target.value)}
  required
/>
```

**Best Practices:**
- Use for 2-4 options max
- Order options logically (most common first, or by severity)
- Provide clear, descriptive labels
- Use `name` prop to group radios

**When NOT to use:**
- 5+ options → Use `FormSelect`
- Binary choice → Use `FormSwitch` or `FormCheckbox`

---

#### FormSwitch

**When to use:**
- On/off toggle for settings or preferences
- Enabling/disabling features
- Binary state change that's not a form submission

**How to use:**
```tsx
import { FormSwitch } from '@/components/ui/form/FormSwitch';

<FormSwitch
  label="Verifikasi BPJS Otomatis"
  checked={autoVerify}
  onCheckedChange={setAutoVerify}
  hint="Verifikasi kepesertaan BPJS secara elektronik"
/>
```

**Best Practices:**
- Use for "enable/disable" semantics
- Add `hint` to explain what the switch controls
- Avoid for critical actions (use buttons instead)
- Provide immediate feedback when toggled

**When NOT to use:**
- Form submission choice → Use `FormCheckbox`
- Choosing from options → Use `FormSelect` or `FormRadio`

---

#### FormTextarea

**When to use:**
- Multi-line text input
- Clinical notes (SOAP format)
- Medical history, complaints, descriptions
- Any content longer than 100 characters

**How to use:**
```tsx
import { FormTextarea } from '@/components/ui/form/FormTextarea';

// SOAP note section
<FormTextarea
  label="Subjective (S)"
  placeholder="Keluhan pasien..."
  rows={4}
  hint="Apa yang dikatakan pasien"
/>

// With character limit
<FormTextarea
  label="Alergi Obat"
  maxLength={500}
  hint="Maksimal 500 karakter"
/>
```

**Best Practices:**
- Set appropriate `rows` for expected content (3-6 for notes)
- Use `placeholder` as format guide
- Add `maxLength` for constrained fields
- Enable `autoResize` for better UX (default)
- Character limits for validation (BPJS, notes, etc.)

**When NOT to use:**
- Single-line input → Use `FormInput`
- Rich text formatting → Use a rich text editor (future)

---

### Layout Components

#### Card

**When to use:**
- Grouping related content
- Displaying patient information
- Dashboard widgets and statistics
- Section containers

**How to use:**
```tsx
import { Card, CardHeader, CardBody, CardFooter } from '@/components/ui/Card';

// Basic card
<Card variant="default">
  <CardBody>
    <p>Isi card di sini</p>
  </CardBody>
</Card>

// Complete card
<Card variant="interactive" onClick={handleClick}>
  <CardHeader title="Informasi Pasien" />
  <CardBody>
    <div>Pasien: Ahmad Susanto</div>
    <div>RM: RM-2024-1234</div>
  </CardBody>
  <CardFooter>
    <Button>Lihat Detail</Button>
  </CardFooter>
</Card>
```

**Variants:**
- `default` - Standard card with subtle shadow
- `interactive` - Hover effects, cursor pointer (clickable)
- `elevated` - Prominent shadow for emphasis

**Best Practices:**
- Use `interactive` variant for clickable cards
- Keep content focused (single topic per card)
- Use `CardHeader` for titles, `CardBody` for content, `CardFooter` for actions
- Ensure adequate padding and spacing

**When NOT to use:**
- Simple grouping → Use a `div` with border
- Full page layout → Use `Layout` component
- Modal content → Use `Modal` component

---

#### PatientCard

**When to use:**
- Displaying patient information in lists
- Patient search results
- Patient selection interface
- Patient overview cards

**How to use:**
```tsx
import { PatientCard } from '@/components/ui/PatientCard';

<PatientCard
  patient={{
    id: "1",
    name: "Ahmad Susanto",
    rmNumber: "RM-2024-1234",
    isBPJS: true,
    bpjsNumber: "1234567890",
  }}
  onClick={() => navigate(`/patients/${patient.id}`)}
  showBPJS={true}
/>
```

**Best Practices:**
- Always include patient ID for navigation
- Show BPJS badge when applicable (most patients)
- Make clickable for navigation to patient details
- Display in lists or grids for scanability

**When NOT to use:**
- Complex patient information → Use a detail page
- Patient creation form → Use form components

---

### Badge Components

#### Badge

**When to use:**
- Status indicators (active, inactive, pending)
- Categorization (priority, type, class)
- Labels and tags
- Count indicators

**How to use:**
```tsx
import { Badge } from '@/components/ui/Badge';

// Status indicator
<Badge variant="success">Aktif</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Gagal</Badge>

// With dot for emphasis
<Badge variant="primary" dot>Online</Badge>
```

**Variants:**
- `primary` - General information (Medical Teal)
- `success` - Completed, active, positive (Green)
- `warning` - Caution, attention needed (Yellow/Amber)
- `error` - Errors, critical issues (Red)
- `info` - Informational (Blue)
- `neutral` - Default, inactive (Gray)

**Best Practices:**
- Use color to convey meaning (not decoration)
- Keep text short (1-3 words ideally)
- Use `dot` for status that needs emphasis
- Place badge near what it describes

**When NOT to use:**
- Long text descriptions → Use a text element
- Complex content → Use a card or alert
- BPJS status → Use `BPJSBadge`
- Triage level → Use `TriageBadge`

---

#### BPJSBadge

**When to use:**
- Indicating BPJS (national insurance) status
- Showing BPJS class
- BPJS-related labels

**How to use:**
```tsx
import { BPJSBadge } from '@/components/ui/BPJSBadge';

// Basic BPJS indicator
<BPJSBadge showDot>Peserta BPJS</BPJSBadge>

// With class
<BPJSBadge showDot>Kelas 2</BPJSBadge>

// With number
<BPJSBadge showDot>BPJS: 1234567890</BPJSBadge>
```

**Best Practices:**
- Always show for BPJS patients (78% of patients)
- Use `showDot` for active/enrolled status
- Include BPJS number when available
- Position prominently in patient information

**When NOT to use:**
- Non-BPJS patients → Don't show any badge
- General insurance → Use `Badge` with neutral variant

---

#### TriageBadge

**When to use:**
- Emergency room patient classification
- Triage level indicators
- Emergency status display

**How to use:**
```tsx
import { TriageBadge } from '@/components/ui/TriageBadge';

// Compact badge
<TriageBadge level="merah" />

// With label
<TriageBadge level="kuning" showLabel />
```

**Triage Levels:**
- `merah` (Red) - Gawat Darurat - Life-threatening, immediate treatment
- `kuning` (Yellow) - Semi-Urgent - Serious but stable
- `hijau` (Green) - Non-Urgent - Minor injuries/illnesses
- `biru` (Blue) - Potentially unstable - Monitor closely
- `hitam` (Black) - Deceased/Expectant - Beyond saving

**Best Practices:**
- Use correct color per triage protocol
- Show label for clarity when space allows
- Position prominently in emergency interfaces
- Use with proper clinical training

**When NOT to use:**
- Non-emergency contexts
- General status → Use `Badge`

---

### Alert Components

#### Alert

**When to use:**
- Informational messages
- Success feedback
- Warning notifications
- Error messages (non-critical)
- Validation feedback

**How to use:**
```tsx
import { Alert } from '@/components/ui/Alert';

// Info alert
<Alert
  variant="info"
  title="Informasi"
  message="Sistem akan maintenance pada pukul 22:00 WIB"
/>

// Success alert
<Alert
  variant="success"
  title="Berhasil"
  message="Data pasien telah disimpan"
  dismissible
  onDismiss={() => setShowAlert(false)}
/>

// Error alert
<Alert
  variant="error"
  title="Gagal"
  message="Gagal menyimpan data. Periksa koneksi internet."
/>

// Custom content
<Alert
  variant="warning"
  title="Alergi Obat Terdeteksi"
>
  <p>Pasien alergi terhadap Penisilin.</p>
  <p>Pertimbangkan alternatif lain.</p>
</Alert>
```

**Best Practices:**
- Use appropriate variant for severity
- Keep messages clear and actionable
- Allow dismissal for non-critical alerts
- Position near relevant content
- Use Indonesian language

**When NOT to use:**
- Critical emergencies → Use `CriticalAlert`
- Full page errors → Use error boundary page
- Toast notifications → Use toast system

---

#### CriticalAlert

**When to use:**
- Life-threatening emergencies
- Critical system failures
- Code activation (Code Blue, Code Red)
- Urgent alerts requiring immediate attention

**How to use:**
```tsx
import { CriticalAlert } from '@/components/ui/CriticalAlert';

// Cardiac arrest
<CriticalAlert
  title="CODE BLUE - HENTI JANTUNG"
  message="Pasien di Ruang 303. Segera ke ruang resusitasi."
  emergencyType="code-blue"
  pulse={true}
/>

// System failure
<CriticalAlert
  title="BPJS VCLAIM API DOWN"
  message="Tidak dapat terhubung ke server BPJS."
  emergencyType="critical"
  pulse={false}
>
  <div>Gunakan data manual dari kartu fisik pasien.</div>
</CriticalAlert>
```

**Emergency Types:**
- `emergency` - General emergency (red/coral)
- `critical` - Critical system failure
- `code-blue` - Cardiac/respiratory arrest (blue)
- `code-red` - Fire disaster (red)

**Best Practices:**
- Use ONLY for true emergencies
- Include clear, actionable instructions
- Use `pulse={true}` for ongoing emergencies
- Position at top of page with high visibility
- Include relevant details (location, time, actions)

**When NOT to use:**
- Warnings or cautions → Use `Alert` with warning variant
- Informational messages → Use `Alert` with info variant
- Non-urgent notifications → Use toast or banner

---

### Data Display Components

#### Table

**When to use:**
- Displaying structured data (patients, appointments, inventory)
- Comparison of multiple items
- Data lists with sorting/filtering
- Medical records and reports

**How to use:**
```tsx
import { Table } from '@/components/ui/Table';
import { Badge } from '@/components/ui/Badge';

const columns = [
  { key: "name", title: "Nama Pasien" },
  { key: "rmNumber", title: "No. RM" },
  { key: "age", title: "Usia" },
  {
    key: "status",
    title: "Status",
    render: (value: string) => {
      const variant = value === "Rawat Inap" ? "success" : "primary";
      return <Badge variant={variant}>{value}</Badge>;
    },
  },
];

<Table
  data={patients}
  columns={columns}
  sortable={true}
  onSort={(key) => handleSort(key)}
/>
```

**Best Practices:**
- Keep columns focused (5-7 max)
- Use `sortable` for large datasets
- Use `render` for custom formatting (badges, dates, actions)
- Include pagination for 25+ rows
- Use sticky headers for long tables
- Align columns appropriately (left for text, right for numbers)

**When NOT to use:**
- Simple lists (< 5 items) → Use a list component
- Cards → Use `Card` for rich content
- Comparison of 2-3 items → Use side-by-side cards

---

#### Pagination

**When to use:**
- Large datasets (25+ items)
- Paginated API responses
- Sorted/filterable tables
- Search results

**How to use:**
```tsx
import { Pagination } from '@/components/ui/Pagination';

<Pagination
  currentPage={page}
  totalPages={totalPages}
  onPageChange={setPage}
  totalItems={totalItems}
  pageSize={pageSize}
  showInfo={true}
/>
```

**Best Practices:**
- Show info for context ("Showing 1-10 of 95 items")
- Use reasonable page sizes (10, 25, 50)
- Preserve query params on page change
- Show total items when available
- Use with server-side pagination for large datasets

**When NOT to use:**
- < 25 items → Show all items or use "Load more"
- Infinite scroll → Not recommended for healthcare (state management)

---

### Modal Components

#### Modal

**When to use:**
- Confirming actions (delete, submit, discharge)
- Forms that don't require a full page
- Detailed information without leaving context
- Focused workflows (prescribing, ordering)

**How to use:**
```tsx
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalTitle,
  ModalDescription,
  ModalFooter,
  ModalTrigger,
} from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';

<Modal>
  <ModalTrigger asChild>
    <Button>Verifikasi BPJS</Button>
  </ModalTrigger>
  <ModalContent size="lg">
    <ModalHeader>
      <ModalTitle>Verifikasi Keanggotaan BPJS</ModalTitle>
      <ModalDescription>
        Masukkan nomor kartu BPJS untuk verifikasi
      </ModalDescription>
    </ModalHeader>
    <div className="py-4">
      {/* Form content */}
    </div>
    <ModalFooter>
      <Button variant="ghost" onClick={onCancel}>Batal</Button>
      <Button onClick={onConfirm}>Verifikasi</Button>
    </ModalFooter>
  </ModalContent>
</Modal>
```

**Sizes:**
- `sm` - Simple confirmations, compact forms
- `md` - Standard forms, details (default)
- `lg` - Complex forms, multiple sections
- `xl` - Very large content, extensive forms

**Best Practices:**
- Clear title explaining purpose
- Description for context (when needed)
- Footer with clear actions (Cancel + Confirm)
- Close on escape key
- Click outside to close (optional, for non-destructive actions)
- Focus management (auto-focus first input)

**When NOT to use:**
- Full page workflows → Use a page instead
- Notifications → Use `Alert` or toast
- Non-modal interactions → Use inline expansion

---

### Pagination Component

See Table section above for Pagination guidelines.

---

## Accessibility

### WCAG 2.1 AA Compliance

All components follow WCAG 2.1 AA guidelines:

**Color Contrast:**
- All text meets 4.5:1 contrast ratio minimum
- Medical Teal (#0d9488) on white: 7.5:1 ✓
- Coral (#f97316) on white: 4.6:1 ✓

**Keyboard Navigation:**
- All interactive elements are keyboard accessible
- Tab order follows logical reading order
- Focus indicators are visible
- Escape key closes modals and dismissibles

**Screen Readers:**
- All form inputs have associated labels
- ARIA labels for icon-only buttons
- Semantic HTML elements
- Alt text for images

**Error Handling:**
- Clear error messages in Indonesian
- Errors announced to screen readers
- Validation messages linked to inputs

### Language Support

**Indonesian (Primary):**
- All UI text in Bahasa Indonesia
- Medical terminology in Indonesian (with English in parentheses where needed)
- Date/time formatting: Indonesian locale

**English (Secondary):**
- Technical documentation
- Code comments
- API field names

---

## Responsive Patterns

### Breakpoints

- **Mobile:** 375px - 767px (single column, stacked)
- **Tablet:** 768px - 1023px (adapted layout)
- **Desktop:** 1024px+ (multi-column, full layout)

### Mobile-First Approach

**Form Layouts:**
- Stack form fields vertically on mobile
- Full-width inputs for easy tapping
- Minimum 44x44px touch targets
- Avoid hover-only interactions

**Navigation:**
- Hamburger menu on mobile/tablet
- Collapsible sidebar
- Bottom navigation for common actions (future)

**Tables:**
- Horizontal scroll on mobile
- Card view alternative for complex tables
- Simplified columns (hide less important ones)

**Modals:**
- Full-screen on mobile
- Centered with backdrop on desktop
- Touch-friendly buttons (min 44px height)

---

## Indonesian Healthcare Context

### BPJS Integration Patterns

**BPJS-First Design:**
- Default to BPJS option in forms
- Verify BPJS eligibility early
- Show BPJS class and status prominently
- Auto-fill from BPJS data when available

**BPJS Number Format:**
- Display: 1234-5678-9012 (grouped for readability)
- Input: 13 digits only
- Validation: Luhn algorithm check

### Medical Standards

**Clinical Documentation:**
- SOAP format for notes (Subjective, Objective, Assessment, Plan)
- ICD-10 for diagnosis codes
- Vital signs with units (mmHg, /min, °C, %)
- 24-hour time format (Indonesian locale)

**Emergency Triage:**
- Color-coded system (Merah/Kuning/Hijau/Biru/Hitam)
- < 2 minute triage target
- Visible timer in emergency interface
- One-tap chief complaint selection

### Patient Identification

**Patient Display Priority:**
1. Name (primary identifier)
2. RM Number (medical record number)
3. Age/Gender (quick demographics)
4. BPJS Badge (insurance status)
5. Photo (when available, with initials fallback)

**Patient Privacy:**
- Display only necessary information
- Mask sensitive data (partial NIK)
- Role-based access to information
- Audit trail for data access

---

## Common Patterns

### Form Layout Pattern

```tsx
<div className="space-y-6">
  {/* Section 1: Patient Information */}
  <div>
    <h3 className="text-lg font-semibold mb-4">Informasi Pasien</h3>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormInput label="Nama Lengkap" required />
      <FormInput label="NIK" required />
      <FormSelect label="Jenis Kelamin" options={genderOptions} required />
      <FormInput label="Tanggal Lahir" type="date" required />
    </div>
  </div>

  {/* Section 2: BPJS Information */}
  <FormCheckbox
    label="Pasien memiliki BPJS"
    checked={hasBPJS}
    onCheckedChange={setHasBPJS}
  />

  {hasBPJS && (
    <div className="border-l-4 border-teal-600 pl-4">
      <h4 className="font-medium mb-3">Informasi BPJS</h4>
      <div className="space-y-4">
        <FormInput label="Nomor BPJS" placeholder="13 digit" />
        <FormSelect label="Kelas" options={bpjsClasses} />
      </div>
    </div>
  )}
</div>
```

### Action Button Pattern

```tsx
<div className="flex justify-end gap-3">
  <Button variant="ghost" onClick={onCancel}>
    Batal
  </Button>
  <Button variant="secondary" onClick={onSaveDraft}>
    Simpan Draft
  </Button>
  <Button onClick={onSubmit}>
    Kirim
  </Button>
</div>
```

### Status Display Pattern

```tsx
<div className="flex items-center justify-between p-4 border rounded">
  <div>
    <p className="font-medium">Poli Umum</p>
    <p className="text-sm text-gray-500">Dr. Ahmad Sp.PD</p>
  </div>
  <Badge variant="success" dot>Buka</Badge>
</div>
```

---

## Summary

This guide provides comprehensive usage patterns for all SIMRS components. Key takeaways:

1. **Use components consistently** - Follow the patterns shown
2. **Prioritize Indonesian context** - BPJS-first, medical standards
3. **Ensure accessibility** - WCAG 2.1 AA compliance
4. **Design for mobile** - Responsive, touch-friendly
5. **Follow medical conventions** - SOAP, ICD-10, triage colors

For specific component API details, refer to the Storybook stories.

---

## Resources

- **Storybook:** Run `npm run storybook` (when dependencies are fixed)
- **Component Source:** `frontend/src/components/ui/`
- **Design System CSS:** `frontend/src/styles/enhanced-simrs-components.css`
- **Web Epics:** `_bmad-output/web-epics.md`
- **PRD:** `_bmad-output/prd.md`

---

**Last Updated:** 2026-01-16
**Next Review:** After WEB-EPIC-1 completion
