/**
 * SIMRS Enhanced Component Library - JavaScript
 * Interactive functionality for SIMRS UI components
 *
 * @version 1.0
 * @date 2026-01-13
 */

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Debounce function for search inputs
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
function generateId() {
  return 'simrs-' + Math.random().toString(36).substr(2, 9);
}

/**
 * Format date to Indonesian format (DD-MM-YYYY)
 * @param {Date|string} date - Date to format
 * @returns {string} Formatted date
 */
function formatDateIndo(date) {
  const d = new Date(date);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  return `${day}-${month}-${year}`;
}

/**
 * Format number with Indonesian thousands separator
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
function formatNumberIndo(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

/**
 * Calculate age from birth date
 * @param {Date|string} birthDate - Birth date
 * @returns {number} Age in years
 */
function calculateAge(birthDate) {
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }

  return age;
}

// ============================================
// BPJS VERIFICATION
// ============================================

/**
 * Verify BPJS eligibility
 * @param {string} cardNumber - BPJS card number
 * @returns {Promise<Object>} Verification result
 */
async function verifyBPJSEligibility(cardNumber) {
  // Show loading state
  const btn = document.querySelector('.btn-verify');
  const resultDiv = document.getElementById('bpjs-result');

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Mengecek...';
  }

  try {
    // Simulate API call (replace with actual BPJS API)
    const response = await fetch(`/api/bpjs/eligibility/${cardNumber}`);
    const data = await response.json();

    if (data.success) {
      displayBPJSResult(data);
      return data;
    } else {
      showNotification('error', 'No. kartu BPJS tidak ditemukan atau tidak aktif');
      return null;
    }
  } catch (error) {
    console.error('BPJS verification error:', error);
    showNotification('error', 'Gagal memverifikasi BPJS. Silakan coba lagi.');
    return null;
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg> Cek';
    }
  }
}

/**
 * Display BPJS verification result
 * @param {Object} data - BPJS data
 */
function displayBPJSResult(data) {
  const resultDiv = document.getElementById('bpjs-result');

  if (!resultDiv) return;

  resultDiv.innerHTML = `
    <div class="result-header success">
      <span class="result-icon">✓</span>
      <span>Pasien Aktif</span>
    </div>
    <div class="patient-details">
      <div class="detail-row">
        <span class="label">Nama:</span>
        <span class="value">${data.nama.toUpperCase()}</span>
      </div>
      <div class="detail-row">
        <span class="label">NIK:</span>
        <span class="value">${data.nik}</span>
      </div>
      <div class="detail-row">
        <span class="label">Jenis:</span>
        <span class="value">${data.jenisPeserta}</span>
      </div>
      <div class="detail-row">
        <span class="label">Faskes:</span>
        <span class="value">${data.faskes}</span>
      </div>
    </div>
    <button type="button" class="btn btn-primary btn-full" onclick="autoFillFromBPJS()">
      <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
      </svg>
      Gunakan Data BPJS
    </button>
  `;

  resultDiv.classList.remove('hidden');
}

/**
 * Auto-fill form from BPJS data
 */
function autoFillFromBPJS() {
  // Get BPJS data from result display
  const bpjsData = getBPJSData();

  if (!bpjsData) return;

  // Fill form fields
  const nikInput = document.getElementById('nik');
  const namaInput = document.getElementById('nama');
  const tglLahirInput = document.getElementById('tgl-lahir');

  if (nikInput) nikInput.value = bpjsData.nik;
  if (namaInput) namaInput.value = bpjsData.nama;
  if (tglLahirInput) tglLahirInput.value = bpjsData.tglLahir;

  showNotification('success', 'Data pasien terisi otomatis dari BPJS');
}

/**
 * Get BPJS data from result display
 * @returns {Object|null} BPJS data
 */
function getBPJSData() {
  const resultDiv = document.getElementById('bpjs-result');
  if (!resultDiv || resultDiv.classList.contains('hidden')) {
    return null;
  }

  // Extract data from displayed result
  // In real implementation, store in variable or data attribute
  return {
    nama: 'BUDI SANTOSO',
    nik: '3201010101010001',
    tglLahir: '1980-01-01',
    jenisPeserta: 'PBI',
    faskes: 'RSUD SEHAT'
  };
}

// ============================================
// DIAGNOSIS SEARCH (ICD-10)
// ============================================

/**
 * Search diagnosis (ICD-10)
 * @param {string} query - Search query
 * @returns {Promise<Array>} Search results
 */
const searchDiagnosis = debounce(async function(query) {
  const resultsDiv = document.getElementById('diagnosis-results');

  if (query.length < 2) {
    if (resultsDiv) resultsDiv.classList.add('hidden');
    return;
  }

  try {
    const response = await fetch(`/api/diagnosis/search?q=${encodeURIComponent(query)}`);
    const results = await response.json();

    displayDiagnosisResults(results);
  } catch (error) {
    console.error('Diagnosis search error:', error);
  }
}, 300);

/**
 * Display diagnosis search results
 * @param {Array} results - Search results
 */
function displayDiagnosisResults(results) {
  const resultsDiv = document.getElementById('diagnosis-results');

  if (!resultsDiv) return;

  if (results.length === 0) {
    resultsDiv.classList.add('hidden');
    return;
  }

  resultsDiv.innerHTML = results.map(item => `
    <div class="result-item" onclick="selectDiagnosis('${item.code}', '${item.name.replace(/'/g, "\\'")}')">
      <span class="code">${item.code}</span>
      <span class="name">${item.name}</span>
      ${item.frequent ? '<span class="freq">★</span>' : ''}
    </div>
  `).join('');

  resultsDiv.classList.remove('hidden');
}

/**
 * Select diagnosis from search results
 * @param {string} code - ICD-10 code
 * @param {string} name - Diagnosis name
 */
function selectDiagnosis(code, name) {
  const container = document.getElementById('selected-diagnoses');
  const searchInput = document.getElementById('diagnosis-search');
  const resultsDiv = document.getElementById('diagnosis-results');

  // Check if already selected
  const existingChip = container.querySelector(`[data-code="${code}"]`);
  if (existingChip) {
    existingChip.classList.add('highlight');
    setTimeout(() => existingChip.classList.remove('highlight'), 1000);
    return;
  }

  // Create new chip
  const chip = document.createElement('div');
  chip.className = 'diagnosis-chip';
  chip.setAttribute('data-code', code);
  chip.innerHTML = `
    <span class="chip-code primary">${code}</span>
    <span class="chip-name">${name}</span>
    <button class="chip-remove" onclick="removeDiagnosis('${code}')" type="button">×</button>
  `;
  container.appendChild(chip);

  // Clear search
  if (searchInput) searchInput.value = '';
  if (resultsDiv) resultsDiv.classList.add('hidden');

  // Update validation
  validateSEPForm();
}

/**
 * Remove selected diagnosis
 * @param {string} code - ICD-10 code to remove
 */
function removeDiagnosis(code) {
  const container = document.getElementById('selected-diagnoses');
  const chip = container.querySelector(`[data-code="${code}"]`);

  if (chip) {
    chip.remove();
    validateSEPForm();
  }
}

// ============================================
// TRIAGE CALCULATION
// ============================================

/**
 * Calculate triage category from vital signs
 * @returns {Object} Triage result
 */
function calculateTriage() {
  const bpSys = parseInt(document.getElementById('bp-sys')?.value) || 0;
  const bpDia = parseInt(document.getElementById('bp-dia')?.value) || 0;
  const pulse = parseInt(document.getElementById('pulse')?.value) || 0;
  const rr = parseInt(document.getElementById('rr')?.value) || 0;
  const spo2 = parseInt(document.getElementById('spo2')?.value) || 0;
  const gcs = parseInt(document.getElementById('gcs')?.value) || 15;

  let score = 0;
  let reasons = [];

  // Blood pressure check
  if (bpSys < 90 || bpDia < 60) {
    score += 3;
    reasons.push({ text: `Tekanan darah rendah (${bpSys}/${bpDia} mmHg)`, critical: true });
  }

  // Pulse check
  if (pulse > 120 || pulse < 50) {
    score += 2;
    reasons.push({ text: `Nadi abnormal (${pulse} x/mnt)`, critical: pulse > 120 });
  }

  // Respiratory rate check
  if (rr > 24 || rr < 10) {
    score += 2;
    reasons.push({ text: `Pernapasan abnormal (${rr} x/mnt)`, critical: rr < 10 });
  }

  // SpO2 check
  if (spo2 < 90) {
    score += 3;
    reasons.push({ text: `SpO2 rendah (${spo2}%)`, critical: true });
  } else if (spo2 < 95) {
    score += 1;
    reasons.push({ text: `SpO2 di bawah normal (${spo2}%)`, critical: false });
  }

  // GCS check
  if (gcs < 14) {
    score += 2;
    reasons.push({ text: `Kesadaran menurun (GCS: ${gcs})`, critical: gcs < 10 });
  }

  // Determine triage category
  let category, description, color;

  if (score >= 5) {
    category = 'MERAH';
    description = 'GAWAT DARURAT - Segera tangani';
    color = 'triage-merah';
  } else if (score >= 3) {
    category = 'KUNING';
    description = 'SEMI-URGENT - Perlu perhatian';
    color = 'triage-kuning';
  } else {
    category = 'HIJAU';
    description = 'NON-URGENT - Tunggu giliran';
    color = 'triage-hijau';
  }

  return {
    category,
    description,
    color,
    score,
    reasons
  };
}

/**
 * Display triage result
 */
function displayTriageResult() {
  const result = calculateTriage();
  const resultSection = document.getElementById('triage-result');
  const card = document.getElementById('triage-category-card');

  if (!resultSection || !card) return;

  // Update card
  card.className = `triage-card ${result.color}`;
  document.getElementById('triage-category').textContent = result.category;
  document.getElementById('triage-description').textContent = result.description;

  // Update reasons
  const reasonsList = document.getElementById('triage-reasons');
  if (result.reasons.length > 0) {
    reasonsList.querySelector('ul').innerHTML = result.reasons.map(r =>
      `<li class="${r.critical ? 'critical' : ''}">${r.critical ? '✗' : '⚠'} ${r.text}</li>`
    ).join('');
    reasonsList.classList.remove('hidden');
  } else {
    reasonsList.classList.add('hidden');
  }

  // Show result
  resultSection.classList.remove('hidden');

  // Scroll to result
  resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================
// SEP FORM VALIDATION
// ============================================

/**
 * Validate SEP form
 * @returns {boolean} Form validity
 */
function validateSEPForm() {
  let isValid = true;
  const validationList = document.querySelector('.validation-list');

  if (!validationList) return false;

  // Check each field
  const validations = [
    {
      selector: '#no-rujukan',
      label: 'No. rujukan',
      check: (val) => val.length > 0
    },
    {
      selector: '#poli-tujuan',
      label: 'Poli tujuan',
      check: (val) => val.length > 0
    },
    {
      selector: '#selected-diagnoses',
      label: 'Diagnosa',
      check: (el) => el.children.length > 0,
      isElement: true
    }
  ];

  validations.forEach(v => {
    const el = v.isElement
      ? document.querySelector(v.selector)
      : document.querySelector(v.selector);
    const valid = v.isElement
      ? v.check(el)
      : v.check(el?.value);

    updateValidationStatus(v.label, valid);
    if (!valid) isValid = false;
  });

  // Update submit button
  const submitBtn = document.getElementById('btn-next');
  if (submitBtn) {
    submitBtn.disabled = !isValid;
  }

  return isValid;
}

/**
 * Update validation status for a field
 * @param {string} label - Field label
 * @param {boolean} valid - Validation result
 */
function updateValidationStatus(label, valid) {
  const validationList = document.querySelector('.validation-list');
  if (!validationList) return;

  const existingItem = validationList.querySelector(`[data-label="${label}"]`);
  const newItem = document.createElement('div');
  newItem.className = `validation-item ${valid ? 'valid' : 'pending'}`;
  newItem.setAttribute('data-label', label);
  newItem.innerHTML = `
    <span class="validation-icon">${valid ? '✓' : '○'}</span>
    <span class="validation-text">${valid ? '' : 'Belum diisi - '}${label}</span>
  `;

  if (existingItem) {
    existingItem.replaceWith(newItem);
  } else {
    validationList.appendChild(newItem);
  }
}

// ============================================
// NOTIFICATIONS / TOASTS
// ============================================

/**
 * Show notification toast
 * @param {string} type - Notification type (success, error, warning, info)
 * @param {string} message - Notification message
 * @param {number} duration - Duration in milliseconds (default: 5000)
 */
function showNotification(type, message, duration = 5000) {
  // Create notification container if doesn't exist
  let container = document.getElementById('notification-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10000;
      display: flex;
      flex-direction: column;
      gap: 10px;
    `;
    document.body.appendChild(container);
  }

  // Create notification
  const notification = document.createElement('div');
  notification.className = `alert alert-${type}`;
  notification.style.cssText = `
    min-width: 300px;
    max-width: 400px;
    animation: slideIn 0.3s ease;
  `;

  const icons = {
    success: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>',
    error: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>',
    warning: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>',
    info: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'
  };

  notification.innerHTML = `
    <svg class="alert-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      ${icons[type] || icons.info}
    </svg>
    <div class="alert-content">
      <div class="alert-message">${message}</div>
    </div>
    <button type="button" class="notification-close" onclick="this.parentElement.remove()">✕</button>
  `;

  container.appendChild(notification);

  // Auto-remove after duration
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, duration);
}

// ============================================
// MODAL FUNCTIONS
// ============================================

/**
 * Open modal
 * @param {string} modalId - Modal element ID
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Focus first focusable element
    const focusable = modal.querySelector('button, input, select, textarea');
    if (focusable) focusable.focus();
  }
}

/**
 * Close modal
 * @param {string} modalId - Modal element ID
 */
function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  }
}

/**
 * Close all modals
 */
function closeAllModals() {
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.classList.add('hidden');
  });
  document.body.style.overflow = '';
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

/**
 * Setup global keyboard shortcuts
 */
function setupKeyboardShortcuts() {
  document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for quick search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchInput = document.getElementById('diagnosis-search') ||
                        document.getElementById('global-search');
      if (searchInput) searchInput.focus();
    }

    // Ctrl/Cmd + S to save (prevent default browser save)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      const saveBtn = document.querySelector('button[type="submit"]');
      if (saveBtn && !saveBtn.disabled) {
        saveBtn.click();
      }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
      closeAllModals();

      // Close dropdowns
      document.querySelectorAll('.search-results-dropdown').forEach(dropdown => {
        dropdown.classList.add('hidden');
      });
    }

    // Number shortcuts for quick actions
    if (e.key >= '1' && e.key <= '9' && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const activeElement = document.activeElement;
      // Only trigger if not in input field
      if (activeElement.tagName !== 'INPUT' &&
          activeElement.tagName !== 'TEXTAREA' &&
          !activeElement.isContentEditable) {
        triggerQuickAction(parseInt(e.key));
      }
    }
  });
}

/**
 * Trigger quick action by number
 * @param {number} num - Action number (1-9)
 */
function triggerQuickAction(num) {
  const actions = document.querySelectorAll('.quick-action-btn');
  if (actions[num - 1]) {
    actions[num - 1].click();
  }
}

// ============================================
// OFFLINE / CONNECTION STATUS
// ============================================

/**
 * Setup connection status monitoring
 */
function setupConnectionStatus() {
  const statusDiv = document.createElement('div');
  statusDiv.id = 'connection-status';
  statusDiv.className = 'connection-status online';
  statusDiv.innerHTML = `
    <div class="status-dot"></div>
    <span>Online</span>
  `;
  statusDiv.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 9999;
    transition: all 0.3s ease;
  `;
  document.body.appendChild(statusDiv);

  // Monitor connection
  window.addEventListener('online', updateConnectionStatus);
  window.addEventListener('offline', updateConnectionStatus);

  // Initial check
  updateConnectionStatus();
}

/**
 * Update connection status display
 */
function updateConnectionStatus() {
  const statusDiv = document.getElementById('connection-status');
  if (!statusDiv) return;

  if (navigator.onLine) {
    statusDiv.className = 'connection-status online';
    statusDiv.innerHTML = `
      <div class="status-dot"></div>
      <span>Online - Sinkronisasi aktif</span>
    `;
    statusDiv.style.background = 'var(--simrs-success-bg)';
    statusDiv.style.color = 'var(--simrs-success)';
  } else {
    statusDiv.className = 'connection-status offline';
    statusDiv.innerHTML = `
      <div class="status-dot"></div>
      <span>Offline - Data tersimpan lokal</span>
    `;
    statusDiv.style.background = 'var(--simrs-warning-bg)';
    statusDiv.style.color = 'var(--simrs-warning)';
  }
}

// ============================================
// INITIALIZATION
// ============================================

/**
 * Initialize SIMRS components when DOM is ready
 */
function initSIMRSComponents() {
  // Setup keyboard shortcuts
  setupKeyboardShortcuts();

  // Setup connection monitoring
  setupConnectionStatus();

  // Setup form validation for BPJS card input
  const bpjsInput = document.getElementById('bpjs-card');
  if (bpjsInput) {
    bpjsInput.addEventListener('input', function(e) {
      // Auto-format BPJS card number
      let value = e.target.value.replace(/\D/g, '');
      if (value.length > 13) value = value.slice(0, 13);

      // Add spaces for readability
      if (value.length > 4) {
        value = value.slice(0, 4) + ' ' + value.slice(4);
      }
      if (value.length > 9) {
        value = value.slice(0, 9) + ' ' + value.slice(9);
      }

      e.target.value = value;
    });
  }

  // Setup diagnosis search
  const diagnosisSearch = document.getElementById('diagnosis-search');
  if (diagnosisSearch) {
    diagnosisSearch.addEventListener('input', function(e) {
      searchDiagnosis(e.target.value);
    });
  }

  // Setup NIK input
  const nikInput = document.getElementById('nik');
  if (nikInput) {
    nikInput.addEventListener('input', function(e) {
      // Only allow numbers, max 16 digits
      let value = e.target.value.replace(/\D/g, '');
      if (value.length > 16) value = value.slice(0, 16);
      e.target.value = value;
    });
  }

  // Close search results when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.diagnosis-search-wrapper')) {
      document.querySelectorAll('.search-results-dropdown').forEach(dropdown => {
        dropdown.classList.add('hidden');
      });
    }
  });

  console.log('SIMRS Components initialized');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSIMRSComponents);
} else {
  initSIMRSComponents();
}

// Export functions for global access
window.SIMRS = {
  verifyBPJSEligibility,
  displayBPJSResult,
  autoFillFromBPJS,
  searchDiagnosis,
  selectDiagnosis,
  removeDiagnosis,
  calculateTriage,
  displayTriageResult,
  validateSEPForm,
  showNotification,
  openModal,
  closeModal,
  closeAllModals,
  formatDateIndo,
  formatNumberIndo,
  calculateAge
};
