# SIMRS UX Design System
**Sistem Informasi Manajemen Rumah Sakit**

---

## Design Philosophy

### Core Principles

**Clarity Over Complexity (Kesederhanaan)**
- Medical data must be instantly readable at a glance
- Critical information stands out with visual hierarchy
- Reduce cognitive load for tired healthcare workers

**Safety First (Keselamatan)**
- Clear warnings for critical actions
- Confirmations for irreversible operations
- Visual feedback for all system states

**Speed & Efficiency (Kecepatan)**
- Minimal clicks for common tasks
- Keyboard shortcuts for power users
- Optimized for slow hospital networks

**Trust & Reliability (Kepercayaan)**
- Consistent behavior across all modules
- Clear system status always visible
- Professional, trustworthy appearance

---

## Visual Identity

### Design Direction: "Modern Indonesian Healthcare"

A distinctive aesthetic that blends:
- **Professional cleanliness** of medical environments
- **Warmth of Indonesian hospitality** (ramah tamah)
- **Cultural sensitivity** to local context
- **Technological sophistication** without intimidation

**Color Strategy:**
- Dominant: Medical blue-teal (trust, calm, professionalism)
- Supporting: Warm coral accents (energy, urgency - not generic red)
- Neutrals: Warm grays (softer than stark black/white)
- Semantic: Context-aware colors (medical, not generic)

---

## Color Palette

### Primary Colors

```css
/* Medical Blue-Teal - Trust & Professionalism */
--simrs-blue-50:  #e0f2f1;
--simrs-blue-100: #b2dfdb;
--simrs-blue-200: #80cbc4;
--simrs-blue-300: #4db6ac;
--simrs-blue-400: #26a69a;
--simrs-blue-500: #009688; /* Primary brand color */
--simrs-blue-600: #00897b;
--simrs-blue-700: #00796b;
--simrs-blue-800: #00695c;
--simrs-blue-900: #004d40;

/* Warm Teal - Softer alternative */
--simrs-teal-50:  #e6fffa;
--simrs-teal-100: #b2f5ea;
--simrs-teal-200: #81e6d9;
--simrs-teal-300: #4fd1c5;
--simrs-teal-400: #38b2ac;
--simrs-teal-500: #319795; /* Secondary accent */
--simrs-teal-600: #2c7a7b;
--simrs-teal-700: #285e61;
--simrs-teal-800: #234e52;
--simrs-teal-900: #1d4044;
```

### Accent Colors

```css
/* Warm Coral - Urgency & Attention (replaces generic red) */
--simrs-coral-50:  #fff0ed;
--simrs-coral-100: #ffded5;
--simrs-coral-200: #ffcbb5;
--simrs-coral-300: #ffb895;
--simrs-coral-400: #ffa475;
--simrs-coral-500: #ff9155; /* Accent CTAs */
--simrs-coral-600: #f5763e;
--simrs-coral-700: #e85c26;
--simrs-coral-800: #cf4a18;
--simrs-coral-900: #b23d10;

/* Warm Amber - Warnings (replaces generic yellow) */
--simrs-amber-50:  #fff8e6;
--simrs-amber-100: #ffecb3;
--simrs-amber-200: #ffe082;
--simrs-amber-300: #ffd54f;
--simrs-amber-400: #ffca28;
--simrs-amber-500: #ffc107; /* Warnings */
--simrs-amber-600: #ffb300;
--simrs-amber-700: #ffa000;
--simrs-amber-800: #ff8f00;
--simrs-amber-900: #ff6f00;

/* Fresh Green - Success (medical, bright) */
--simrs-green-50:  #e8f5e9;
--simrs-green-100: #c8e6c9;
--simrs-green-200: #a5d6a7;
--simrs-green-300: #81c784;
--simrs-green-400: #66bb6a;
--simrs-green-500: #4caf50; /* Success states */
--simrs-green-600: #43a047;
--simrs-green-700: #388e3c;
--simrs-green-800: #2e7d32;
--simrs-green-900: #1b5e20;
```

### Semantic Colors

```css
/* Emergency - High urgency (IGD) */
--simrs-emergency: #d32f2f;
--simrs-emergency-light: #ffcdd2;
--simrs-emergency-dark: #b71c1c;

/* Critical - Lab values, alerts */
--simrs-critical: #c62828;
--simrs-critical-bg: #ffebee;

/* Warning - Pre-op, fasting */
--simrs-warning: #f57c00;
--simrs-warning-bg: #fff3e0;

/* Caution - Drug interactions */
--simrs-caution: #f9a825;
--simrs-caution-bg: #fffde7;

/* Info - BPJS status */
--simrs-info: #0277bd;
--simrs-info-bg: #e1f5fe;

/* Success - Vitals normal, saved */
--simrs-success: #2e7d32;
--simrs-success-bg: #e8f5e9;
```

### Neutral Colors (Warm Grays)

```css
/* Warm neutral base (not cold gray) */
--simrs-gray-50:  #fafafa; /* Lightest background */
--simrs-gray-100: #f5f5f5; /* Secondary backgrounds */
--simrs-gray-200: #eeeeee; /* Borders, dividers */
--simrs-gray-300: #e0e0e0; /* Disabled states */
--simrs-gray-400: #bdbdbd; /* Placeholder text */
--simrs-gray-500: #9e9e9e; /* Secondary text */
--simrs-gray-600: #757575; /* Body text */
--simrs-gray-700: #616161; /* Headings */
--simrs-gray-800: #424242; /* Primary text */
--simrs-gray-900: #212121; /* Darkest text */

/* Text colors */
--simrs-text-primary: #212121;
--simrs-text-secondary: #616161;
--simrs-text-disabled: #9e9e9e;
--simrs-text-inverse: #ffffff;

/* Background colors */
--simrs-bg-primary: #ffffff;
--simrs-bg-secondary: #f5f5f5;
--simrs-bg-tertiary: #fafafa;
--simrs-bg-elevated: #ffffff;
--simrs-bg-overlay: rgba(0, 0, 0, 0.5);
```

### Special Purpose Colors

```css
/* BPJS Brand Colors (integration context) */
--bpjs-blue: #1e3a8a;
--bpjs-light: #3b82f6;
--bpjs-bg: #eff6ff;

/* Triage Colors (IGD) */
--triage-merah: #d32f2f;    /* Emergency */
--triage-kuning: #f9a825;   /* Semi-urgent */
--triage-hijau: #388e3c;    /* Non-urgent */
--triage-hitam: #212121;    /* Deceased */

/* Medical status */
--status-inpatient: #009688;
--status-outpatient: #319795;
--status-emergency: #d32f2f;
--status-discharged: #616161;
```

---

## Typography

### Type System

**Primary Font Family:** `Plus Jakarta Sans` (Indonesian-designed, modern, highly readable)

```css
--font-primary: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont,
               'Segoe UI', Roboto, sans-serif;
```

**Why Plus Jakarta Sans?**
- Designed by Indonesian type foundry (Tokotype)
- Optimized for UI clarity
- Excellent Indonesian character support
- Modern yet professional
- Strong legibility at small sizes

**Monospace for Medical Data:** `IBM Plex Mono` (clinical precision)

```css
--font-mono: 'IBM Plex Mono', 'Courier New', monospace;
```

### Typography Scale

```css
/* Display - Hero sections, dashboards */
--text-display-xl: 4.5rem;    /* 72px - Dashboard titles */
--text-display-lg: 3.75rem;   /* 60px - Page headers */
--text-display-md: 3rem;      /* 48px - Section headers */
--text-display-sm: 2.25rem;   /* 36px - Subsections */

/* Heading - Content organization */
--text-h1: 2rem;      /* 32px - Main page title */
--text-h2: 1.75rem;   /* 28px - Section title */
--text-h3: 1.5rem;    /* 24px - Subsection */
--text-h4: 1.25rem;   /* 20px - Component title */
--text-h5: 1.125rem;  /* 18px - Small header */
--text-h6: 1rem;      /* 16px - Minor header */

/* Body - Reading content */
--text-xl: 1.25rem;   /* 20px - Emphasized body */
--text-lg: 1.125rem;  /* 18px - Large body */
--text-base: 1rem;    /* 16px - Default body */
--text-sm: 0.875rem;  /* 14px - Secondary text */
--text-xs: 0.75rem;   /* 12px - Captions, labels */

/* Medical Data - Monospace precision */
--medical-data-xl: 1.125rem;
--medical-data-lg: 1rem;
--medical-data-md: 0.875rem;
--medical-data-sm: 0.75rem;
```

### Font Weights

```css
--font-light: 300;    /* Subtle text, overlines */
--font-regular: 400;  /* Body text, forms */
--font-medium: 500;   /* Emphasized text, buttons */
--font-semibold: 600; /* Headings, important labels */
--font-bold: 700;     /* Page titles, CTAs */
--font-extrabold: 800;/* Hero text */
```

### Line Heights

```css
--leading-tight: 1.25;    /* Headings, compact */
--leading-snug: 1.375;   /* UI elements */
--leading-normal: 1.5;   /* Body text */
--leading-relaxed: 1.625;/* Long-form content */
--leading-loose: 2;      /* Special cases */
```

### Letter Spacing

```css
--tracking-tighter: -0.05em; /* All caps, compact */
--tracking-tight: -0.025em;  /* Headings */
--tracking-normal: 0;         /* Default */
--tracking-wide: 0.025em;     /* Emphasis */
--tracking-wider: 0.05em;     /* All caps labels */
--tracking-widest: 0.1em;     /* Special display */
```

---

## Spacing System

### Spacing Scale (8pt grid)

```css
--space-0: 0;
--space-1: 0.25rem;  /* 4px - Tight spacing */
--space-2: 0.5rem;   /* 8px - Compact */
--space-3: 0.75rem;  /* 12px - Small */
--space-4: 1rem;     /* 16px - Default */
--space-5: 1.25rem;  /* 20px - Medium */
--space-6: 1.5rem;   /* 24px - Comfortable */
--space-8: 2rem;     /* 32px - Spacious */
--space-10: 2.5rem;  /* 40px - Section spacing */
--space-12: 3rem;    /* 48px - Large sections */
--space-16: 4rem;    /* 64px - Major sections */
--space-20: 5rem;    /* 80px - Hero spacing */
--space-24: 6rem;    /* 96px - Extra large */
```

---

## Component Library

### Buttons (Tombol)

#### Primary Button

**Usage:** Main CTAs, save actions, confirmations

```css
/* Design */
.btn-primary {
  background: linear-gradient(135deg, var(--simrs-blue-500), var(--simrs-blue-600));
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: 8px;
  font-weight: var(--font-semibold);
  font-size: var(--text-base);
  border: none;
  box-shadow: 0 2px 8px rgba(0, 150, 136, 0.2);
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, var(--simrs-blue-600), var(--simrs-blue-700));
  box-shadow: 0 4px 12px rgba(0, 150, 136, 0.3);
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 150, 136, 0.2);
}

/* Disabled state */
.btn-primary:disabled {
  background: var(--simrs-gray-300);
  box-shadow: none;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Loading state */
.btn-primary.loading {
  position: relative;
  color: transparent;
}

.btn-primary.loading::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  top: 50%;
  left: 50%;
  margin: -8px 0 0 -8px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

**Sizes:**
- Small: `0.625rem` padding, `0.875rem` text
- Medium (default): `0.75rem` padding, `1rem` text
- Large: `1rem` padding, `1.125rem` text

**Examples:**
```html
<!-- Standard -->
<button class="btn-primary">Simpan Pasien</button>

<!-- With icon -->
<button class="btn-primary btn-with-icon">
  <svg class="icon-left" width="20" height="20">
    <path d="...save icon..."/>
  </svg>
  Simpan
</button>

<!-- Full width (mobile) -->
<button class="btn-primary btn-full">Daftar Pasien Baru</button>

<!-- Loading -->
<button class="btn-primary loading">Memproses...</button>
```

---

#### Secondary Button

**Usage:** Alternative actions, cancel, go back

```css
.btn-secondary {
  background: white;
  color: var(--simrs-blue-600);
  padding: var(--space-3) var(--space-6);
  border-radius: 8px;
  font-weight: var(--font-medium);
  font-size: var(--text-base);
  border: 2px solid var(--simrs-blue-200);
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--simrs-blue-50);
  border-color: var(--simrs-blue-300);
}
```

---

#### Coral Accent Button

**Usage:** Emergency actions, critical warnings

```css
.btn-coral {
  background: linear-gradient(135deg, var(--simrs-coral-500), var(--simrs-coral-600));
  color: white;
  padding: var(--space-3) var(--space-6);
  border-radius: 8px;
  font-weight: var(--font-semibold);
  border: none;
  box-shadow: 0 2px 8px rgba(255, 145, 85, 0.3);
}

.btn-coral:hover {
  background: linear-gradient(135deg, var(--simrs-coral-600), var(--simrs-coral-700));
  box-shadow: 0 4px 12px rgba(255, 145, 85, 0.4);
}
```

**Examples:**
```html
<!-- Emergency -->
<button class="btn-coral">PANGGIL KODE BIRU</button>

<!-- Critical action -->
<button class="btn-coral">
  <svg class="icon-left" width="20" height="20">
    <path d="...warning icon..."/>
  </svg>
  Hapus SEP
</button>
```

---

#### Ghost Button

**Usage:** Tertiary actions, less prominent options

```css
.btn-ghost {
  background: transparent;
  color: var(--simrs-text-secondary);
  padding: var(--space-3) var(--space-6);
  border-radius: 8px;
  font-weight: var(--font-medium);
  border: 1px solid var(--simrs-gray-300);
  transition: all 0.2s ease;
}

.btn-ghost:hover {
  background: var(--simrs-gray-100);
  border-color: var(--simrs-gray-400);
  color: var(--simrs-text-primary);
}
```

---

#### Icon Buttons

**Usage:** Toolbar actions, inline operations

```css
.btn-icon {
  background: transparent;
  color: var(--simrs-text-secondary);
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: var(--simrs-gray-200);
  color: var(--simrs-text-primary);
}

.btn-icon:active {
  background: var(--simrs-gray-300);
  transform: scale(0.95);
}

/* Primary icon button */
.btn-icon-primary {
  background: var(--simrs-blue-50);
  color: var(--simrs-blue-600);
}

.btn-icon-primary:hover {
  background: var(--simrs-blue-100);
}
```

**Examples:**
```html
<!-- Single icon -->
<button class="btn-icon" aria-label="Edit">
  <svg width="20" height="20">
    <path d="...edit icon..."/>
  </svg>
</button>

<!-- Icon group -->
<div class="btn-icon-group">
  <button class="btn-icon" aria-label="View">
    <svg width="20" height="20">...</svg>
  </button>
  <button class="btn-icon" aria-label="Edit">
    <svg width="20" height="20">...</svg>
  </button>
  <button class="btn-icon" aria-label="Delete">
    <svg width="20" height="20">...</svg>
  </button>
</div>
```

---

### Form Elements (Elemen Form)

#### Text Input

**Design:** Clean, focus-indicating, error-clear

```css
.input-text {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 2px solid var(--simrs-gray-300);
  border-radius: 8px;
  font-size: var(--text-base);
  font-family: var(--font-primary);
  color: var(--simrs-text-primary);
  background: white;
  transition: all 0.2s ease;
}

.input-text:hover {
  border-color: var(--simrs-gray-400);
}

.input-text:focus {
  outline: none;
  border-color: var(--simrs-blue-500);
  box-shadow: 0 0 0 3px var(--simrs-blue-100);
}

/* Error state */
.input-text.error {
  border-color: var(--simrs-coral-500);
}

.input-text.error:focus {
  box-shadow: 0 0 0 3px var(--simrs-coral-100);
}

/* Disabled state */
.input-text:disabled {
  background: var(--simrs-gray-100);
  color: var(--simrs-text-disabled);
  cursor: not-allowed;
}

/* Readonly state */
.input-text[readonly] {
  background: var(--simrs-gray-50);
  border-color: var(--simrs-gray-200);
  cursor: default;
}

/* Sizes */
.input-text-sm {
  padding: var(--space-2) var(--space-3);
  font-size: var(--text-sm);
}

.input-text-lg {
  padding: var(--space-4) var(--space-5);
  font-size: var(--text-lg);
}
```

**With Label:**
```html
<div class="form-group">
  <label class="form-label" for="nik">
    NIK <span class="required">*</span>
  </label>
  <input
    type="text"
    id="nik"
    class="input-text"
    placeholder="Masukkan 16 digit NIK"
    maxlength="16"
    required
  />
  <small class="form-help">Nomor Induk Kependudukan 16 digit</small>
  <div class="form-error">NIK harus 16 digit angka</div>
</div>
```

---

#### Search Input

```css
.input-search {
  position: relative;
}

.input-search input {
  padding-left: 40px;
}

.input-search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--simrs-text-disabled);
  pointer-events: none;
}

.input-search-clear {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: var(--simrs-gray-200);
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  cursor: pointer;
  color: var(--simrs-text-secondary);
  font-size: 12px;
  display: none;
}

.input-search-clear.visible {
  display: flex;
  align-items: center;
  justify-content: center;
}
```

**Example:**
```html
<div class="input-search">
  <svg class="input-search-icon" width="18" height="18">
    <path d="...search icon..."/>
  </svg>
  <input type="text" placeholder="Cari pasien (nama/No. RM/NIK)"/>
  <button class="input-search-clear" aria-label="Clear">✕</button>
</div>
```

---

#### Select Dropdown

```css
.select-wrapper {
  position: relative;
}

.select-wrapper::after {
  content: '';
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 5px solid var(--simrs-text-secondary);
  pointer-events: none;
}

select {
  appearance: none;
  width: 100%;
  padding: var(--space-3) var(--space-10) var(--space-3) var(--space-4);
  border: 2px solid var(--simrs-gray-300);
  border-radius: 8px;
  font-size: var(--text-base);
  font-family: var(--font-primary);
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

select:focus {
  outline: none;
  border-color: var(--simrs-blue-500);
  box-shadow: 0 0 0 3px var(--simrs-blue-100);
}
```

---

#### Date Picker (Indonesian Format)

```css
.input-date {
  position: relative;
}

.input-date input {
  padding-right: 40px;
}

.input-date-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--simrs-text-secondary);
  pointer-events: none;
}

/* Date format hint */
.input-date-hint {
  position: absolute;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
  font-size: var(--text-sm);
  color: var(--simrs-text-disabled);
  pointer-events: none;
}
```

**Example:**
```html
<div class="input-date">
  <input
    type="text"
    class="input-text"
    placeholder="DD-MM-YYYY"
    pattern="\d{2}-\d{2}-\d{4}"
  />
  <span class="input-date-hint">DD-MM-YYYY</span>
  <svg class="input-date-icon" width="18" height="18">
    <path d="...calendar icon..."/>
  </svg>
</div>
```

---

#### Checkbox (Indonesian: Kotak Centang)

```css
.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  user-select: none;
}

.checkbox-wrapper input[type="checkbox"] {
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid var(--simrs-gray-400);
  border-radius: 4px;
  background: white;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.checkbox-wrapper input[type="checkbox"]:hover {
  border-color: var(--simrs-blue-500);
}

.checkbox-wrapper input[type="checkbox"]:checked {
  background: var(--simrs-blue-500);
  border-color: var(--simrs-blue-500);
}

.checkbox-wrapper input[type="checkbox"]:checked::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 1px;
  width: 6px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-wrapper input[type="checkbox"]:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--simrs-blue-100);
}

/* Indeterminate state */
.checkbox-wrapper input[type="checkbox"]:indeterminate {
  background: var(--simrs-blue-500);
  border-color: var(--simrs-blue-500);
}

.checkbox-wrapper input[type="checkbox"]:indeterminate::after {
  content: '';
  position: absolute;
  left: 3px;
  top: 8px;
  width: 10px;
  height: 2px;
  background: white;
}
```

**Example:**
```html
<label class="checkbox-wrapper">
  <input type="checkbox" checked />
  <span>Pasien BPJS</span>
</label>

<label class="checkbox-wrapper">
  <input type="checkbox" />
  <span>Sepakat rawat inap</span>
</label>
```

---

#### Radio Button (Indonesian: Tombol Radio)

```css
.radio-wrapper {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  user-select: none;
}

.radio-wrapper input[type="radio"] {
  appearance: none;
  width: 20px;
  height: 20px;
  border: 2px solid var(--simrs-gray-400);
  border-radius: 50%;
  background: white;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.radio-wrapper input[type="radio"]:hover {
  border-color: var(--simrs-blue-500);
}

.radio-wrapper input[type="radio"]:checked {
  border-color: var(--simrs-blue-500);
}

.radio-wrapper input[type="radio"]:checked::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 10px;
  height: 10px;
  background: var(--simrs-blue-500);
  border-radius: 50%;
}

.radio-wrapper input[type="radio"]:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--simrs-blue-100);
}
```

**Example:**
```html
<div class="radio-group">
  <label class="radio-wrapper">
    <input type="radio" name="gender" value="male" checked />
    <span>Laki-laki</span>
  </label>
  <label class="radio-wrapper">
    <input type="radio" name="gender" value="female" />
    <span>Perempuan</span>
  </label>
</div>
```

---

#### Switch (Toggle)

```css
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.switch input {
  appearance: none;
  width: 100%;
  height: 100%;
  background: var(--simrs-gray-300);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.switch input:checked {
  background: var(--simrs-blue-500);
}

.switch input::after {
  content: '';
  position: absolute;
  left: 2px;
  top: 2px;
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.switch input:checked::after {
  left: 26px;
}

.switch input:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--simrs-blue-100);
}
```

**Example:**
```html
<label class="switch">
  <input type="checkbox" checked />
  <span>Aktif</span>
</label>
```

---

### Cards (Kartu)

#### Patient Card

```css
.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  padding: var(--space-6);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--simrs-gray-200);
}

.card-title {
  font-size: var(--text-h4);
  font-weight: var(--font-semibold);
  color: var(--simrs-text-primary);
}

.card-body {
  margin-bottom: var(--space-4);
}

.card-footer {
  display: flex;
  gap: var(--space-3);
  padding-top: var(--space-4);
  border-top: 1px solid var(--simrs-gray-200);
}

/* Patient card variant */
.card-patient {
  border-left: 4px solid var(--simrs-blue-500);
}

.card-patient.card-emergency {
  border-left-color: var(--simrs-emergency);
}

.card-patient.card-inpatient {
  border-left-color: var(--status-inpatient);
}

.card-patient.card-outpatient {
  border-left-color: var(--status-outpatient);
}
```

**Example:**
```html
<div class="card card-patient">
  <div class="card-header">
    <div>
      <h3 class="card-title">Budi Santoso</h3>
      <p class="text-sm text-secondary">No. RM: 2024-001234</p>
    </div>
    <span class="badge badge-info">BPJS</span>
  </div>
  <div class="card-body">
    <div class="patient-info-grid">
      <div class="info-item">
        <span class="info-label">NIK</span>
        <span class="info-value">3201010101010001</span>
      </div>
      <div class="info-item">
        <span class="info-label">Tanggal Lahir</span>
        <span class="info-value">01-01-1980 (45 th)</span>
      </div>
      <div class="info-item">
        <span class="info-label">Jenis Kelamin</span>
        <span class="info-value">Laki-laki</span>
      </div>
      <div class="info-item">
        <span class="info-label">Poli Tujuan</span>
        <span class="info-value">Penyakit Dalam</span>
      </div>
    </div>
  </div>
  <div class="card-footer">
    <button class="btn-secondary btn-sm">Detail</button>
    <button class="btn-primary btn-sm">Mulai Periksa</button>
  </div>
</div>
```

---

#### Dashboard Card

```css
.card-stat {
  background: white;
  border-radius: 12px;
  padding: var(--space-6);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.card-stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.card-stat-icon.blue {
  background: var(--simrs-blue-50);
  color: var(--simrs-blue-600);
}

.card-stat-icon.coral {
  background: var(--simrs-coral-50);
  color: var(--simrs-coral-600);
}

.card-stat-icon.green {
  background: var(--simrs-green-50);
  color: var(--simrs-green-600);
}

.card-stat-content {
  flex: 1;
}

.card-stat-value {
  font-size: var(--text-h3);
  font-weight: var(--font-bold);
  color: var(--simrs-text-primary);
  line-height: var(--leading-tight);
}

.card-stat-label {
  font-size: var(--text-sm);
  color: var(--simrs-text-secondary);
  margin-top: var(--space-1);
}

.card-stat-change {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  margin-top: var(--space-2);
}

.card-stat-change.positive {
  color: var(--simrs-green-600);
}

.card-stat-change.negative {
  color: var(--simrs-coral-600);
}
```

**Example:**
```html
<div class="card-stat">
  <div class="card-stat-icon blue">
    <svg width="24" height="24">
      <path d="...patients icon..."/>
    </svg>
  </div>
  <div class="card-stat-content">
    <div class="card-stat-value">127</div>
    <div class="card-stat-label">Pasien Hari Ini</div>
    <div class="card-stat-change positive">
      ↑ 12% dari kemarin
    </div>
  </div>
</div>
```

---

### Tables (Tabel)

#### Data Table

```css
.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table thead {
  background: var(--simrs-gray-50);
  border-bottom: 2px solid var(--simrs-gray-200);
}

.table th {
  padding: var(--space-4) var(--space-4);
  text-align: left;
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
  color: var(--simrs-text-secondary);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
}

.table tbody tr {
  border-bottom: 1px solid var(--simrs-gray-200);
  transition: background 0.15s ease;
}

.table tbody tr:hover {
  background: var(--simrs-blue-50);
}

.table tbody tr:last-child {
  border-bottom: none;
}

.table td {
  padding: var(--space-4) var(--space-4);
  font-size: var(--text-base);
  color: var(--simrs-text-primary);
}

/* Table cell variants */
.table-cell-numeric {
  font-family: var(--font-mono);
  text-align: right;
}

.table-cell-date {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.table-cell-status {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

/* Row actions */
.table-row-actions {
  display: flex;
  gap: var(--space-2);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.table tbody tr:hover .table-row-actions {
  opacity: 1;
}

/* Responsive table wrapper */
.table-responsive {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.table-responsive .table {
  min-width: 600px;
}
```

**Example:**
```html
<div class="table-container">
  <table class="table">
    <thead>
      <tr>
        <th>No. RM</th>
        <th>Nama Pasien</th>
        <th>Jenis Kelamin</th>
        <th>Umur</th>
        <th>Poli</th>
        <th>Status BPJS</th>
        <th>Aksi</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="table-cell-numeric">2024-001234</td>
        <td>
          <div class="patient-name">Budi Santoso</div>
          <div class="patient-nik text-sm text-secondary">
            NIK: 3201010101010001
          </div>
        </td>
        <td>Laki-laki</td>
        <td>45 th</td>
        <td>Penyakit Dalam</td>
        <td>
          <span class="badge badge-success">Aktif</span>
        </td>
        <td>
          <div class="table-row-actions">
            <button class="btn-icon btn-sm" aria-label="View">
              <svg width="16" height="16">...</svg>
            </button>
            <button class="btn-icon btn-sm" aria-label="Edit">
              <svg width="16" height="16">...</svg>
            </button>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

---

### Badges (Label)

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border-radius: 12px;
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: 1;
}

/* Status badges */
.badge-success {
  background: var(--simrs-success-bg);
  color: var(--simrs-success);
}

.badge-info {
  background: var(--simrs-info-bg);
  color: var(--simrs-info);
}

.badge-warning {
  background: var(--simrs-warning-bg);
  color: var(--simrs-warning);
}

.badge-error {
  background: var(--simrs-critical-bg);
  color: var(--simrs-critical);
}

/* BPJS badge */
.badge-bpjs {
  background: var(--bpjs-bg);
  color: var(--bpjs-blue);
  font-weight: var(--font-semibold);
}

/* Department badges */
.badge-inpatient {
  background: rgba(0, 150, 136, 0.1);
  color: var(--status-inpatient);
}

.badge-outpatient {
  background: rgba(49, 151, 149, 0.1);
  color: var(--status-outpatient);
}

.badge-emergency {
  background: rgba(211, 47, 47, 0.1);
  color: var(--status-emergency);
}

/* Triage badges */
.badge-triage-merah {
  background: var(--triage-merah);
  color: white;
}

.badge-triage-kuning {
  background: var(--triage-kuning);
  color: white;
}

.badge-triage-hijau {
  background: var(--triage-hijau);
  color: white;
}

/* Badge with icon */
.badge-icon {
  gap: var(--space-1);
}

.badge-icon::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
```

**Examples:**
```html
<!-- Status badges -->
<span class="badge badge-success">Aktif</span>
<span class="badge badge-warning">Proses</span>
<span class="badge badge-error">Gagal</span>

<!-- BPJS status -->
<span class="badge badge-bpjs">BPJS</span>

<!-- Department -->
<span class="badge badge-inpatient">Rawat Inap</span>
<span class="badge badge-outpatient">Rawat Jalan</span>
<span class="badge badge-emergency">IGD</span>

<!-- Triage -->
<span class="badge badge-triage-merah">MERAH</span>
<span class="badge badge-triage-kuning">KUNING</span>
<span class="badge badge-triage-hijau">HIJAU</span>
```

---

### Alerts (Peringatan)

```css
.alert {
  padding: var(--space-4) var(--space-5);
  border-radius: 8px;
  border-left: 4px solid;
  display: flex;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.alert-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  margin-top: 2px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: var(--font-semibold);
  margin-bottom: var(--space-1);
}

.alert-message {
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.alert-close {
  flex-shrink: 0;
  background: none;
  border: none;
  cursor: pointer;
  color: inherit;
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.alert-close:hover {
  opacity: 1;
}

/* Alert variants */
.alert-info {
  background: var(--simrs-info-bg);
  border-color: var(--simrs-info);
  color: var(--simrs-info);
}

.alert-success {
  background: var(--simrs-success-bg);
  border-color: var(--simrs-success);
  color: var(--simrs-success);
}

.alert-warning {
  background: var(--simrs-warning-bg);
  border-color: var(--simrs-warning);
  color: var(--simrs-warning);
}

.alert-error {
  background: var(--simrs-critical-bg);
  border-color: var(--simrs-critical);
  color: var(--simrs-critical);
}

/* Critical medical alert */
.alert-critical {
  background: #ffebee;
  border-color: var(--simrs-emergency);
  border-left-width: 6px;
  padding: var(--space-5);
}

.alert-critical .alert-title {
  font-size: var(--text-lg);
  font-weight: var(--font-bold);
  color: var(--simrs-emergency);
}
```

**Examples:**
```html
<!-- Info -->
<div class="alert alert-info">
  <svg class="alert-icon" width="20" height="20">
    <path d="...info icon..."/>
  </svg>
  <div class="alert-content">
    <div class="alert-title">Informasi BPJS</div>
    <div class="alert-message">
      Pasien telah terverifikasi eligibility-nya. SEP dapat dibuat.
    </div>
  </div>
  <button class="alert-close" aria-label="Close">✕</button>
</div>

<!-- Warning -->
<div class="alert alert-warning">
  <svg class="alert-icon" width="20" height="20">
    <path d="...warning icon..."/>
  </svg>
  <div class="alert-content">
    <div class="alert-title">Interaksi Obat</div>
    <div class="alert-message">
      Pasien memiliki alergi terhadap penisilin. Obat yang diresepkan
      mengandung amoxicillin (penisilin).
    </div>
  </div>
</div>

<!-- Critical medical alert -->
<div class="alert alert-critical">
  <svg class="alert-icon" width="24" height="24">
    <path d="...critical icon..."/>
  </svg>
  <div class="alert-content">
    <div class="alert-title">NILAI KRITIS - KALIUM</div>
    <div class="alert-message">
      K+ serum: 2.8 mmol/L (Normal: 3.5-5.0)
      Pasien: Budi Santoso (RM: 2024-001234)
      Segera hubungi dokter penanggung jawab.
    </div>
  </div>
</div>
```

---

### Modals (Modal)

```css
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--simrs-bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

.modal-sm {
  max-width: 400px;
}

.modal-md {
  max-width: 600px;
}

.modal-lg {
  max-width: 800px;
}

.modal-xl {
  max-width: 1200px;
}

.modal-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--simrs-gray-200);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: var(--text-h3);
  font-weight: var(--font-semibold);
  color: var(--simrs-text-primary);
}

.modal-close {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--simrs-text-secondary);
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--simrs-gray-200);
}

.modal-body {
  padding: var(--space-6);
  overflow-y: auto;
  max-height: calc(90vh - 160px);
}

.modal-footer {
  padding: var(--space-6);
  border-top: 1px solid var(--simrs-gray-200);
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Example:**
```html
<div class="modal-overlay">
  <div class="modal modal-md">
    <div class="modal-header">
      <h2 class="modal-title">Konfirmasi Pembuatan SEP</h2>
      <button class="modal-close" aria-label="Close">✕</button>
    </div>
    <div class="modal-body">
      <p>Anda akan membuat SEP untuk pasien berikut:</p>
      <div class="patient-summary">
        <strong>Budi Santoso</strong><br>
        No. BPJS: 0001R00101XXXX<br>
        Poli: Penyakit Dalam<br>
        Diagnosis: J18.9 - Pneumonia, unspecified
      </div>
      <p class="text-warning mt-4">
        Pastikan semua data sudah benar. SEP yang sudah dibuat tidak dapat dihapus.
      </p>
    </div>
    <div class="modal-footer">
      <button class="btn-secondary">Batal</button>
      <button class="btn-primary">Buat SEP</button>
    </div>
  </div>
</div>
```

---

### Navigation (Navigasi)

#### Sidebar Menu

```css
.sidebar {
  width: 260px;
  background: white;
  border-right: 1px solid var(--simrs-gray-200);
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  overflow-y: auto;
  z-index: 100;
}

.sidebar-header {
  padding: var(--space-6);
  border-bottom: 1px solid var(--simrs-gray-200);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.sidebar-logo {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--simrs-blue-500), var(--simrs-blue-600));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: var(--font-bold);
  font-size: 20px;
}

.sidebar-brand-name {
  font-size: var(--text-h4);
  font-weight: var(--font-bold);
  color: var(--simrs-blue-600);
}

.sidebar-nav {
  padding: var(--space-4);
}

.nav-section {
  margin-bottom: var(--space-6);
}

.nav-section-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--simrs-text-disabled);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wide);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-2);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: 8px;
  color: var(--simrs-text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
  margin-bottom: var(--space-1);
}

.nav-item:hover {
  background: var(--simrs-gray-100);
  color: var(--simrs-text-primary);
}

.nav-item.active {
  background: var(--simrs-blue-50);
  color: var(--simrs-blue-600);
  font-weight: var(--font-medium);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-label {
  flex: 1;
}

.nav-badge {
  background: var(--simrs-coral-500);
  color: white;
  font-size: var(--text-xs);
  padding: var(--space-1) var(--space-2);
  border-radius: 10px;
  font-weight: var(--font-medium);
}
```

**Example:**
```html
<aside class="sidebar">
  <div class="sidebar-header">
    <div class="sidebar-brand">
      <div class="sidebar-logo">S</div>
      <span class="sidebar-brand-name">SIMRS</span>
    </div>
  </div>
  <nav class="sidebar-nav">
    <div class="nav-section">
      <div class="nav-section-title">Pelayanan</div>
      <a href="/pendaftaran" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 20 20">
          <path d="...registration icon..."/>
        </svg>
        <span class="nav-label">Pendaftaran</span>
      </a>
      <a href="/poli" class="nav-item active">
        <svg class="nav-icon" viewBox="0 0 20 20">
          <path d="...clinic icon..."/>
        </svg>
        <span class="nav-label">Rawat Jalan</span>
      </a>
      <a href="/rawat-inap" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 20 20">
          <path d="...bed icon..."/>
        </svg>
        <span class="nav-label">Rawat Inap</span>
        <span class="nav-badge">5</span>
      </a>
      <a href="/igd" class="nav-item">
        <svg class="nav-icon" viewBox="0 0 20 20">
          <path d="...emergency icon..."/>
        </svg>
        <span class="nav-label">IGD</span>
      </a>
    </div>
  </nav>
</aside>
```

---

#### Top Navigation Bar

```css
.topbar {
  height: 64px;
  background: white;
  border-bottom: 1px solid var(--simrs-gray-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-6);
  position: sticky;
  top: 0;
  z-index: 50;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.topbar-search {
  width: 320px;
}

.topbar-menu-item {
  position: relative;
}

.topbar-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--simrs-blue-100);
  color: var(--simrs-blue-600);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-semibold);
  cursor: pointer;
  transition: all 0.2s ease;
}

.topbar-avatar:hover {
  background: var(--simrs-blue-200);
}

/* Notifications */
.topbar-notifications {
  position: relative;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 18px;
  height: 18px;
  background: var(--simrs-coral-500);
  color: white;
  border-radius: 50%;
  font-size: var(--text-xs);
  font-weight: var(--font-bold);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Offline indicator */
.offline-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--simrs-warning-bg);
  color: var(--simrs-warning);
  border-radius: 6px;
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.offline-dot {
  width: 8px;
  height: 8px;
  background: var(--simrs-warning);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

---

## Layout Patterns

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  Topbar (64px)                                          │
├──────────┬──────────────────────────────────────────────┤
│          │                                               │
│ Sidebar  │  Main Content Area                           │
│ (260px)  │                                               │
│          │  ┌───────────────────────────────────────┐   │
│          │  │ Page Header                          │   │
│          │  ├───────────────────────────────────────┤   │
│          │  │                                       │   │
│          │  │  Content                             │   │
│          │  │                                       │   │
│          │  │                                       │   │
│          │  └───────────────────────────────────────┘   │
│          │                                               │
└──────────┴──────────────────────────────────────────────┘
```

### Patient Registration Layout

```
┌─────────────────────────────────────────────────────────┐
│  Header: Pendaftaran Pasien Baru                       │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │ Form            │  │ BPJS Eligibility Check      │  │
│  │                 │  │                             │  │
│  │ • NIK           │  │ Status: Active ✓            │  │
│  │ • Nama          │  │Nama: Budi Santoso           │  │
│  │ • Tgl Lahir     │  │Jenis: PBI                   │  │
│  │ • Alamat        │  │Faskes: RSUD Sehat          │  │
│  │ • Kontak        │  │                             │  │
│  │ • BPJS (opt)    │  │ [Buat SEP]                 │  │
│  │                 │  └─────────────────────────────┘  │
│  │ [Simpan]        │                                   │
│  └─────────────────┘                                   │
└─────────────────────────────────────────────────────────┘
```

### Doctor Consultation Layout

```
┌─────────────────────────────────────────────────────────┐
│ Patient Banner: Budi Santoso | 45 th | Laki-laki        │
│ NIK: 3201010101010001 | BPJS: 0001R00101XXXX            │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌────────────────────────────────┐  │
│  │ Quick        │  │ SOAP Notes                      │  │
│  │ Actions      │  │                                 │  │
│  │              │  │ Subjective:                     │  │
│  │ [Riwayat]    │  │ [textarea]                      │  │
│  │ [Obat]       │  │                                 │  │
│  │ [Lab]        │  │ Objective:                      │  │
│  │ [Rad]        │  │ [textarea]                      │  │
│  │              │  │                                 │  │
│  │              │  │ Assessment (Diagnosa):          │  │
│  │              │  │ [ICD-10 search]                 │  │
│  │              │  │                                 │  │
│  │              │  │ Plan:                           │  │
│  │              │  │ [textarea]                      │  │
│  │              │  │                                 │  │
│  │              │  │ [Simpan] [Buat SEP] [Cetak]     │  │
│  └──────────────┘  └────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Key User Flows

### 1. Patient Registration Flow

**States:**
1. **Initial State** - Empty form, ready for input
2. **BPJS Check State** - Verifying eligibility (spinner)
3. **Duplicate Warning** - Potential match found
4. **Success State** - Patient registered

**Layout:**
```html
<div class="registration-flow">
  <!-- Progress indicator -->
  <div class="progress-steps">
    <div class="step active">1. Data Pasien</div>
    <div class="step">2. Verifikasi BPJS</div>
    <div class="step">3. Selesai</div>
  </div>

  <!-- Main form -->
  <div class="registration-form">
    <form id="patient-form">
      <!-- Section 1: Identitas -->
      <div class="form-section">
        <h3>Identitas Pasien</h3>
        <div class="form-row">
          <div class="form-col">
            <label>NIK *</label>
            <input type="text" id="nik" maxlength="16" />
          </div>
          <div class="form-col">
            <label>Nama Lengkap *</label>
            <input type="text" id="nama" />
          </div>
        </div>
        <!-- ... more fields ... -->
      </div>

      <!-- Section 2: Kontak -->
      <div class="form-section">
        <h3>Informasi Kontak</h3>
        <!-- ... contact fields ... -->
      </div>

      <!-- BPJS Section (conditional) -->
      <div class="form-section" id="bpjs-section">
        <h3>BPJS Kesehatan</h3>
        <button type="button" class="btn-secondary" onclick="checkBPJS()">
          Cek Eligibilitas BPJS
        </button>
        <div id="bpjs-result" class="hidden">
          <!-- BPJS info displays here -->
        </div>
      </div>

      <!-- Actions -->
      <div class="form-actions">
        <button type="button" class="btn-secondary">Batal</button>
        <button type="submit" class="btn-primary">
          Daftarkan Pasien
        </button>
      </div>
    </form>
  </div>
</div>
```

**Micro-interactions:**
- NIK input: Auto-format with spaces (xxxx xxxx xxxx xxxx)
- BPJS check: Loading spinner with "Mengecek eligibility BPJS..."
- Duplicate detection: Slide-in panel showing potential matches
- Success: Confetti animation + sound effect (subtle)

---

### 2. Doctor Consultation Flow

**Layout Strategy:** Split view - patient info always visible

```html
<div class="consultation-layout">
  <!-- Left sidebar - Patient summary -->
  <aside class="patient-sidebar">
    <div class="patient-header">
      <img src="patient-photo.jpg" class="patient-avatar" />
      <h3>Budi Santoso</h3>
      <p>45 th • Laki-laki</p>
      <div class="patient-badges">
        <span class="badge badge-bpjs">BPJS</span>
        <span class="badge badge-info">Rawat Jalan</span>
      </div>
    </div>

    <div class="patient-vitals">
      <h4>Vital Signs Terakhir</h4>
      <div class="vital-item">
        <span class="vital-label">TD</span>
        <span class="vital-value">130/80</span>
        <span class="vital-unit">mmHg</span>
      </div>
      <!-- ... more vitals ... -->
    </div>

    <div class="patient-alerts">
      <div class="alert alert-warning alert-sm">
        <strong>Alergi:</strong> Penisilin
      </div>
    </div>

    <nav class="quick-actions">
      <button class="btn-ghost btn-block">Riwayat Medis</button>
      <button class="btn-ghost btn-block">Obat Saat Ini</button>
      <button class="btn-ghost btn-block">Hasil Lab</button>
    </nav>
  </aside>

  <!-- Main content - Consultation -->
  <main class="consultation-main">
    <div class="consultation-tabs">
      <button class="tab active">SOAP Notes</button>
      <button class="tab">Resep</button>
      <button class="tab">Lab/Rad</button>
      <button class="tab">Rencana Kontrol</button>
    </div>

    <div class="tab-content active">
      <!-- SOAP form -->
      <form id="soap-form">
        <div class="form-group">
          <label>Subjective</label>
          <textarea rows="4" placeholder="Keluhan pasien..."></textarea>
        </div>

        <div class="form-group">
          <label>Objective</label>
          <textarea rows="4" placeholder="Hasil pemeriksaan fisik..."></textarea>
        </div>

        <div class="form-group">
          <label>Assessment (Diagnosa)</label>
          <div class="diagnosis-search">
            <input
              type="text"
              placeholder="Cari diagnosa (ICD-10)..."
              id="diagnosis-search"
            />
            <div class="search-results hidden">
              <!-- ICD-10 results -->
            </div>
          </div>
          <div class="selected-diagnoses">
            <!-- Selected diagnoses as chips -->
          </div>
        </div>

        <div class="form-group">
          <label>Plan</label>
          <textarea rows="4" placeholder="Rencana tatalaksana..."></textarea>
        </div>

        <div class="form-actions">
          <button type="button" class="btn-secondary">
            Simpan Draft
          </button>
          <button type="button" class="btn-secondary">
            Buat SEP
          </button>
          <button type="submit" class="btn-primary">
            Simpan & Selesai
          </button>
        </div>
      </form>
    </div>
  </main>
</div>
```

**Keyboard Shortcuts:**
- `Ctrl/Cmd + K`: Quick search (diagnosa, obat)
- `Ctrl/Cmd + S`: Save consultation
- `Ctrl/Cmd + Enter`: Complete & save
- `Ctrl/Cmd + R`: Open prescription
- `Ctrl/Cmd + L`: Open lab order

---

### 3. BPJS SEP Creation Flow

**Design Goal:** Make it foolproof with clear validation

```html
<div class="sep-wizard">
  <!-- Step indicators -->
  <div class="wizard-steps">
    <div class="step completed">1. Data Pasien</div>
    <div class="step active">2. Data SEP</div>
    <div class="step">3. Konfirmasi</div>
  </div>

  <!-- Step 2: SEP Data -->
  <div class="wizard-step active">
    <div class="alert alert-info">
      Pastikan semua data sesuai dengan kartu BPJS pasien.
    </div>

    <form id="sep-form">
      <div class="form-row">
        <div class="form-col">
          <label>No. Kartu BPJS *</label>
          <input
            type="text"
            value="0001R00101XXXX"
            readonly
            class="input-text-readonly"
          />
        </div>
        <div class="form-col">
          <label>Tgl. SEP *</label>
          <input
            type="date"
            id="tgl-sep"
            class="input-text"
            value="2026-01-13"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-col">
          <label>No. Rujukan *</label>
          <div class="input-group">
            <input type="text" id="no-rujukan" />
            <button
              type="button"
              class="btn-secondary"
              onclick="cariRujukan()"
            >
              Cari
            </button>
          </div>
          <small class="form-help">
            Nomor rujukan dari faskes tingkat 1 atau 2
          </small>
        </div>
        <div class="form-col">
          <label>Poli Tujuan *</label>
          <select id="poli-tujuan">
            <option value="">Pilih Poli</option>
            <option value="INT" selected>Penyakit Dalam</option>
            <option value="ANA">Anak</option>
            <!-- ... more polis ... -->
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Diagnosa Awal (ICD-10) *</label>
        <div class="diagnosis-picker">
          <input
            type="text"
            id="diagnosa-awal"
            placeholder="Cari diagnosa..."
            autocomplete="off"
          />
          <div class="diagnosa-dropdown hidden">
            <!-- Search results -->
          </div>
        </div>
        <div id="selected-diagnosa" class="diagnosa-chip hidden">
          <span class="code">J18.9</span>
          <span class="name">Pneumonia, unspecified</span>
          <button type="button" class="btn-remove">×</button>
        </div>
      </div>

      <div class="form-row">
        <div class="form-col">
          <label>Kelas Rawat *</label>
          <select id="kelas-rawat">
            <option value="3" selected>Kelas 3</option>
            <option value="2">Kelas 2</option>
            <option value="1">Kelas 1</option>
          </select>
        </div>
        <div class="form-col">
          <label>Jenis Pelayanan *</label>
          <select id="jns-pelayanan">
            <option value="2" selected>Rawat Jalan</option>
            <option value="1">Rawat Inap</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Catatan</label>
        <textarea
          id="catatan"
          rows="3"
          placeholder="Catatan tambahan (opsional)"
        ></textarea>
      </div>

      <!-- Validation summary -->
      <div class="validation-summary">
        <h4>Status Validasi:</h4>
        <ul>
          <li class="valid">Data pasien: Lengkap</li>
          <li class="valid">No. kartu BPJS: Valid</li>
          <li class="pending">No. rujukan: Belum diisi</li>
          <li class="valid">Diagnosa: J18.9</li>
        </ul>
      </div>

      <div class="form-actions">
        <button type="button" class="btn-secondary">
          Kembali
        </button>
        <button type="button" class="btn-primary" id="btn-next">
          Lanjut: Konfirmasi →
        </button>
      </div>
    </form>
  </div>
</div>
```

---

### 4. Emergency (IGD) Triage Flow

**Design Principle:** Speed and clarity above all

```html
<div class="triage-interface">
  <!-- Header with patient info -->
  <div class="triage-header emergency">
    <div class="patient-info">
      <h2>Pasien IGD: [Unknown Male]</h2>
      <p>Estimasi umur: 35-45 th</p>
    </div>
    <div class="triage-timer">
      <span class="label">Waktu di IGD:</span>
      <span class="timer">00:03:45</span>
    </div>
  </div>

  <!-- Vital signs capture (quick entry) -->
  <div class="vital-signs-quick">
    <h3>Tanda Vital (Skrining Awal)</h3>
    <div class="vitals-grid">
      <div class="vital-input">
        <label>Tekanan Darah</label>
        <div class="input-group">
          <input type="number" placeholder="Sistolik" id="td-sys" />
          <span>/</span>
          <input type="number" placeholder="Diastolik" id="td-dia" />
          <span class="unit">mmHg</span>
        </div>
      </div>

      <div class="vital-input">
        <label>Nadi</label>
        <div class="input-group">
          <input type="number" placeholder="60-100" id="nadi" />
          <span class="unit">x/menit</span>
        </div>
      </div>

      <div class="vital-input">
        <label>Pernapasan</label>
        <div class="input-group">
          <input type="number" placeholder="12-20" id="rr" />
          <span class="unit">x/menit</span>
        </div>
      </div>

      <div class="vital-input">
        <label>Suhu</label>
        <div class="input-group">
          <input type="number" placeholder="36-37" id="suhu" step="0.1" />
          <span class="unit">°C</span>
        </div>
      </div>

      <div class="vital-input">
        <label>SpO2</label>
        <div class="input-group">
          <input type="number" placeholder="95-100" id="spo2" />
          <span class="unit">%</span>
        </div>
      </div>

      <div class="vital-input">
        <label>Sadar</label>
        <select id="gcs">
          <option value="">Pilih</option>
          <option value="4">Alert (4)</option>
          <option value="3">Verbal (3)</option>
          <option value="2">Pain (2)</option>
          <option value="1">Unresponsive (1)</option>
        </select>
      </div>
    </div>

    <button type="button" class="btn-primary btn-lg" id="btn-auto-triage">
      Hitung Triage Otomatis
    </button>
  </div>

  <!-- Triage result -->
  <div id="triage-result" class="triage-result hidden">
    <h3>Hasil Triage</h3>
    <div class="triage-card triage-merah">
      <div class="triage-category">MERAH</div>
      <div class="triage-description">
        Gawat darurat - Segera tangani
      </div>
      <div class="triage-reasons">
        <ul>
          <li>Tekanan darah rendah (80/50)</li>
          <li>Nadi cepat (>120 x/menit)</li>
          <li>Sadar menurun (Pain)</li>
        </ul>
      </div>
    </div>

    <div class="triage-actions">
      <button class="btn-coral btn-lg">
        <svg class="icon" width="20" height="20">
          <path d="...emergency icon..."/>
        </svg>
        Aktivasi KODE BIRU
      </button>
      <button class="btn-primary btn-lg">
        Pasang di Resusitasi
      </button>
    </div>
  </div>
</div>
```

**Triage Color Cards:**
```css
.triage-card {
  padding: var(--space-6);
  border-radius: 12px;
  margin-bottom: var(--space-4);
}

.triage-merah {
  background: var(--triage-merah);
  color: white;
}

.triage-kuning {
  background: var(--triage-kuning);
  color: white;
}

.triage-hijau {
  background: var(--triage-hijau);
  color: white;
}

.triage-category {
  font-size: var(--text-h2);
  font-weight: var(--font-extrabold);
  margin-bottom: var(--space-2);
}
```

---

### 5. Pharmacy Dispensing Workflow

**Layout:** Three-column design for efficiency

```html
<div class="pharmacy-workstation">
  <!-- Column 1: Queue -->
  <div class="pharmacy-queue">
    <div class="queue-header">
      <h3>Antrean Resep</h3>
      <span class="badge badge-coral">5 antrian</span>
    </div>

    <div class="queue-list">
      <div class="queue-item active">
        <div class="queue-priority urgent">
          <span class="priority-label">URGENT</span>
        </div>
        <div class="queue-patient">
          <strong>Budi Santoso</strong>
          <br>
          <small>No. RM: 2024-001234</small>
        </div>
        <div class="queue-time">
          14:23
          <br>
          <small class="text-warning">+15 menit</small>
        </div>
      </div>

      <!-- More queue items... -->
    </div>
  </div>

  <!-- Column 2: Current prescription -->
  <div class="pharmacy-prescription">
    <div class="prescription-header">
      <h3>Resep #12345</h3>
      <div class="prescription-meta">
        <span class="badge badge-bpjs">BPJS</span>
        <span class="text-sm">Dr. Siti Sp.PD</span>
      </div>
    </div>

    <div class="patient-alerts">
      <div class="alert alert-warning alert-sm">
        <strong>Alergi:</strong> Penisilin
      </div>
    </div>

    <div class="prescription-items">
      <div class="prescription-item">
        <div class="item-header">
          <strong>Amoxicillin 500 mg</strong>
          <span class="badge badge-warning">INTERAKSI</span>
        </div>
        <div class="item-details">
          <p>3x sehari, selama 7 hari</p>
          <p class="text-secondary">
            Sig: 1 tablet, diminum sesudah makan
          </p>
        </div>
        <div class="interaction-alert">
          <strong>Peringatan Interaksi:</strong>
          Pasien memiliki alergi terhadap penisilin.
          Amoxicillin adalah penisilin.
        </div>
        <div class="item-actions">
          <button class="btn-ghost btn-sm">Tanya Dokter</button>
          <button class="btn-coral btn-sm">Kontraindikasi</button>
        </div>
      </div>

      <div class="prescription-item">
        <div class="item-header">
          <strong>Paracetamol 500 mg</strong>
          <span class="badge badge-success">OK</span>
        </div>
        <div class="item-details">
          <p>3x sehari, jika demam</p>
          <p class="text-secondary">
            Sig: 1 tablet, diminum saat demam
          </p>
        </div>
        <div class="item-status">
          <label>
            <input type="checkbox" />
            <span>Sudah disiapkan</span>
          </label>
        </div>
      </div>
    </div>
  </div>

  <!-- Column 3: Dispensing -->
  <div class="pharmacy-dispensing">
    <div class="dispensing-header">
      <h3>Penyiapan Obat</h3>
    </div>

    <div class="dispensing-form">
      <div class="form-group">
        <label>Scan Barcode Obat</label>
        <div class="scanner-input">
          <input
            type="text"
            id="barcode-scanner"
            placeholder="Scan barcode..."
            autofocus
          />
          <button class="btn-icon">
            <svg width="20" height="20">
              <path d="...barcode icon..."/>
            </svg>
          </button>
        </div>
      </div>

      <div class="scanned-item">
        <div class="item-match">
          <span class="success-icon">✓</span>
          <strong>Paracetamol 500 mg</strong>
        </div>
        <div class="item-qty">
          <label>Jumlah:</label>
          <input type="number" value="21" min="1" />
          <span>tablet</span>
        </div>
        <div class="item-batch">
          <label>No. Batch:</label>
          <input type="text" placeholder="Scan batch..." />
        </div>
        <div class="item-expiry">
          <label>Exp:</label>
          <input type="month" />
        </div>
      </div>

      <div class="dispensing-actions">
        <button class="btn-secondary">Konsultasi Apoteker</button>
        <button class="btn-primary">Selesai & Serahkan</button>
      </div>
    </div>
  </div>
</div>
```

---

## Offline-First UX Patterns

### Connection Status Indicator

```css
.connection-status {
  position: fixed;
  bottom: 20px;
  right: 20px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  animation: slideUp 0.3s ease;
}

.connection-status.online {
  background: var(--simrs-success-bg);
  color: var(--simrs-success);
}

.connection-status.offline {
  background: var(--simrs-warning-bg);
  color: var(--simrs-warning);
}

.connection-status.syncing {
  background: var(--simrs-info-bg);
  color: var(--simrs-info);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s ease-in-out infinite;
}

.status-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
```

**Examples:**
```html
<!-- Online -->
<div class="connection-status online">
  <div class="status-dot"></div>
  <span>Online - Sinkronisasi aktif</span>
</div>

<!-- Offline -->
<div class="connection-status offline">
  <div class="status-dot"></div>
  <span>Offline - Data tersimpan lokal</span>
</div>

<!-- Syncing -->
<div class="connection-status syncing">
  <div class="status-spinner"></div>
  <span>Menyinkronkan 3 perubahan...</span>
</div>
```

---

### Queued Actions Panel

```css
.queued-actions {
  background: white;
  border-radius: 12px;
  padding: var(--space-5);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.queued-actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.queued-actions-title {
  font-size: var(--text-h5);
  font-weight: var(--font-semibold);
}

.queued-count {
  background: var(--simrs-coral-500);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.queued-list {
  max-height: 300px;
  overflow-y: auto;
}

.queued-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: 8px;
  background: var(--simrs-gray-50);
  margin-bottom: var(--space-2);
}

.queued-item-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--simrs-warning-bg);
  color: var(--simrs-warning);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.queued-item-content {
  flex: 1;
}

.queued-item-title {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.queued-item-meta {
  font-size: var(--text-xs);
  color: var(--simrs-text-secondary);
}

.queued-item-action {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.queued-item:hover .queued-item-action {
  opacity: 1;
}

.sync-now-btn {
  width: 100%;
  margin-top: var(--space-4);
}
```

**Example:**
```html
<div class="queued-actions">
  <div class="queued-actions-header">
    <h3 class="queued-actions-title">
      Menunggu Sinkronisasi
    </h3>
    <span class="queued-count">3</span>
  </div>

  <div class="queued-list">
    <div class="queued-item">
      <div class="queued-item-icon">
        <svg width="16" height="16">
          <path d="...clock icon..."/>
        </svg>
      </div>
      <div class="queued-item-content">
        <div class="queued-item-title">Buat SEP</div>
        <div class="queued-item-meta">
          Pasien: Budi Santoso • 14:23
        </div>
      </div>
      <button class="queued-item-action btn-icon btn-sm" aria-label="Cancel">
        ×
      </button>
    </div>

    <div class="queued-item">
      <div class="queued-item-icon">
        <svg width="16" height="16">
          <path d="...clock icon..."/>
        </svg>
      </div>
      <div class="queued-item-content">
        <div class="queued-item-title">Kirim hasil lab</div>
        <div class="queued-item-meta">
          3 tes • 14:15
        </div>
      </div>
      <button class="queued-item-action btn-icon btn-sm" aria-label="Cancel">
        ×
      </button>
    </div>

    <div class="queued-item">
      <div class="queued-item-icon">
        <svg width="16" height="16">
          <path d="...clock icon..."/>
        </svg>
      </div>
      <div class="queued-item-content">
        <div class="queued-item-title">Update diagnosa</div>
        <div class="queued-item-meta">
          Encounter #1234 • 14:10
        </div>
      </div>
      <button class="queued-item-action btn-icon btn-sm" aria-label="Cancel">
        ×
      </button>
    </div>
  </div>

  <button class="btn-primary sync-now-btn">
    <svg class="icon-left" width="16" height="16">
      <path d="...sync icon..."/>
    </svg>
    Sinkronkan Sekarang
  </button>
</div>
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile First Approach */
/* Default: < 768px (Mobile) */

/* Tablet */
@media (min-width: 768px) {
  /* Tablet-specific styles */
}

/* Desktop */
@media (min-width: 1024px) {
  /* Desktop-specific styles */
}

/* Large Desktop */
@media (min-width: 1280px) {
  /* Large desktop styles */
}

/* Extra Large */
@media (min-width: 1536px) {
  /* Extra large styles */
}
```

### Mobile Adaptations

**Mobile Navigation (Bottom Tab Bar):**
```css
.mobile-tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: white;
  border-top: 1px solid var(--simrs-gray-200);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 100;
}

@media (min-width: 768px) {
  .mobile-tabbar {
    display: none;
  }
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--simrs-text-secondary);
  font-size: var(--text-xs);
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.tab-item.active {
  color: var(--simrs-blue-600);
}

.tab-icon {
  width: 24px;
  height: 24px;
}
```

**Mobile Card View:**
```css
/* On mobile, convert tables to cards */
@media (max-width: 767px) {
  .table {
    display: block;
  }

  .table thead {
    display: none;
  }

  .table tbody,
  .table tr,
  .table td {
    display: block;
    width: 100%;
  }

  .table tr {
    background: white;
    border-radius: 12px;
    padding: var(--space-4);
    margin-bottom: var(--space-3);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .table td {
    padding: var(--space-2) 0;
    text-align: left !important;
  }

  .table td::before {
    content: attr(data-label);
    font-weight: var(--font-semibold);
    color: var(--simrs-text-secondary);
    display: block;
    margin-bottom: var(--space-1);
  }
}
```

---

## Accessibility (WCAG 2.1 AA)

### Focus Management

```css
/* Visible focus indicators */
*:focus {
  outline: 2px solid var(--simrs-blue-500);
  outline-offset: 2px;
}

/* Skip to main content link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: var(--simrs-blue-600);
  color: white;
  padding: 8px 16px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

### Screen Reader Support

```html
<!-- Semantic HTML -->
<nav aria-label="Main navigation">
  <ul role="menubar">
    <li role="none">
      <a role="menuitem" href="/pendaftaran">Pendaftaran</a>
    </li>
  </ul>
</nav>

<!-- ARIA labels -->
<button aria-label="Close modal" class="modal-close">✕</button>

<!-- Live regions for dynamic updates -->
<div aria-live="polite" aria-atomic="true" class="status-message">
  Data berhasil disimpan
</div>

<!-- Alert regions -->
<div role="alert" class="alert alert-error">
  Gagal menyimpan data. Silakan coba lagi.
</div>
```

### Keyboard Navigation

```javascript
// Keyboard trap in modals
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeModal();
  }

  // Tab trap
  if (e.key === 'Tab') {
    const focusableElements = modal.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        lastElement.focus();
        e.preventDefault();
      }
    } else {
      if (document.activeElement === lastElement) {
        firstElement.focus();
        e.preventDefault();
      }
    }
  }
});
```

---

## Motion & Animation

### Animation Principles

1. **Purposeful**: Every animation serves a function
2. **Subtle**: Medical context requires restraint
3. **Smooth**: 60fps, no janky movements
4. **Respectful**: Honor `prefers-reduced-motion`

### Transition Timings

```css
/* Fast interactions */
--transition-fast: 150ms ease-out;

/* Standard transitions */
--transition-normal: 200ms ease-in-out;

/* Complex animations */
--transition-slow: 300ms ease-in-out;
```

### Key Animations

```css
/* Fade in */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Slide up (modals, toasts) */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale in (cards) */
@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Spinner (loading) */
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Pulse (alerts, notifications) */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Shake (error feedback) */
@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  20%, 60% {
    transform: translateX(-4px);
  }
  40%, 80% {
    transform: translateX(4px);
  }
}
```

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Icon System

### Icon Design Principles

- **Consistent**: 24×24px base, 2px stroke
- **Clear**: Readable at small sizes
- **Contextual**: Medical + UI icons
- **Accessible**: Proper aria-labels

### Icon Categories

**Medical Icons:**
- Patient (pasien)
- Doctor (dokter)
- Nurse (perawat)
- Pill (obat)
- Syringe (suntikan)
- Stethoscope (stetoskop)
- Heart (jantung)
- Pulse (nadi)
- Temperature (suhu)
- Blood drop (darah)
- Crutch (tongkat)
- Wheelchair (kursi roda)
- Ambulance
- Hospital (rumah sakit)
- Cross (palang merah)

**UI Icons:**
- Navigation arrows
- Checkmark (centang)
- Close (tutup)
- Search (cari)
- Add (tambah)
- Edit (ubah)
- Delete (hapus)
- Save (simpan)
- Print (cetak)
- Calendar (kalender)
- Clock (waktu)
- Alert/warning
- Info
- Success
- Error
- Menu (hamburger)
- Settings (pengaturan)
- Logout (keluar)

---

## Implementation Guidelines

### CSS Architecture

Use CSS custom properties (variables) for theming:

```css
/* Example: Component implementation */
.card {
  /* Spacing */
  padding: var(--space-6);
  gap: var(--space-4);

  /* Colors */
  background: var(--simrs-bg-primary);
  border: 1px solid var(--simrs-gray-200);
  border-radius: 12px;

  /* Typography */
  font-family: var(--font-primary);
  font-size: var(--text-base);

  /* Effects */
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all var(--transition-normal) ease;
}
```

### Component Structure

```html
<!-- BEM-like naming for clarity -->
<div class="card">
  <div class="card__header">
    <h3 class="card__title">Title</h3>
  </div>
  <div class="card__body">
    Content
  </div>
  <div class="card__footer">
    Actions
  </div>
</div>
```

---

## Design Tokens Reference

### Complete Token List

```css
/* Colors */
--simrs-blue-50 through --simrs-blue-900
--simrs-teal-50 through --simrs-teal-900
--simrs-coral-50 through --simrs-coral-900
--simrs-amber-50 through --simrs-amber-900
--simrs-green-50 through --simrs-green-900
--simrs-gray-50 through --simrs-gray-900

/* Semantic colors */
--simrs-emergency, --simrs-critical, --simrs-warning
--simrs-caution, --simrs-info, --simrs-success
--bpjs-blue, --bpjs-light, --bpjs-bg
--triage-merah, --triage-kuning, --triage-hijau, --triage-hitam

/* Typography */
--font-primary, --font-mono
--text-display-xl through --text-display-sm
--text-h1 through --text-h6
--text-xl through --text-xs
--medical-data-xl through --medical-data-sm
--font-light through --font-extrabold
--leading-tight through --leading-loose
--tracking-tighter through --tracking-widest

/* Spacing */
--space-0 through --space-24

/* Transitions */
--transition-fast, --transition-normal, --transition-slow

/* Border radius */
--radius-sm: 4px
--radius-md: 8px
--radius-lg: 12px
--radius-xl: 16px
--radius-full: 9999px

/* Shadows */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05)
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1)
--shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15)
```

---

## Conclusion

This design system provides a distinctive, professional, and culturally appropriate visual language for SIMRS. It balances:

- **Medical professionalism** with **Indonesian warmth**
- **Clarity** with **efficiency**
- **Accessibility** with **aesthetics**
- **Modern design** with **practical usability**

The system is built for real-world Indonesian hospitals, accounting for:
- Slow/poor internet connectivity
- Diverse user technical literacy
- Heavy workload patterns
- Critical nature of healthcare work
- BPJS and SATUSEHAT integration requirements
- Indonesian healthcare workflows and regulations

By following this design system, SIMRS will provide a trusted, efficient, and delightful experience for healthcare workers across Indonesia.

---

**Design System Version:** 1.0
**Last Updated:** 2026-01-13
**Maintained by:** SIMRS Product & Design Team
**License:** MIT (open source)
