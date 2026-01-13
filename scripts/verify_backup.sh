#!/bin/bash
#
# SIMRS Backup Verification Script
#
# Verifies backup integrity by decrypting and validating checksums.
# Should be run periodically to ensure backups are restorable.
#
# Usage: ./verify_backup.sh [--all | <backup_file>]
#

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backup}"
BACKUP_ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

# Logging
LOG_FILE="${BACKUP_DIR}/verification.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "ERROR: $*"
    exit 1
}

verify_single_backup() {
    local encrypted_file="$1"
    local checksum_file="${encrypted_file}.sha256"

    log "Verifying: ${encrypted_file}"

    # Check if backup file exists
    if [ ! -f "${encrypted_file}" ]; then
        log "SKIP: File not found: ${encrypted_file}"
        return 1
    fi

    # Check if checksum file exists
    if [ ! -f "${checksum_file}" ]; then
        log "SKIP: Checksum file missing: ${checksum_file}"
        return 1
    fi

    # Verify checksum
    log "Validating checksum..."
    python3 -c "
import sys
sys.path.insert(0, '/app/backend/app')
from core.backup import BackupManager

with open('${checksum_file}', 'r') as f:
    expected_checksum = f.read().strip()

with open('${encrypted_file}', 'rb') as f:
    encrypted_data = f.read()

manager = BackupManager()
manager.validate_backup(encrypted_data, expected_checksum, encrypted=True, compressed=False)
print('OK: Checksum valid')
" 2>&1 || {
        log "FAILED: Checksum validation failed"
        return 1
    }

    # Attempt to decrypt
    log "Testing decryption..."
    python3 -c "
import sys
sys.path.insert(0, '/app/backend/app')
from core.backup import BackupManager

with open('${encrypted_file}', 'rb') as f:
    encrypted_data = f.read()

manager = BackupManager()
decrypted = manager.decrypt_backup(encrypted_data)
print(f'OK: Decrypted {len(decrypted)} bytes')
" 2>&1 || {
        log "FAILED: Decryption failed"
        return 1
    }

    log "SUCCESS: Backup is valid and restorable"
    return 0
}

verify_all_backups() {
    local total=0
    local passed=0
    local failed=0
    local skipped=0

    log "=========================================="
    log "Verifying all backups in ${BACKUP_DIR}"
    log "=========================================="

    # Verify daily backups
    if [ -d "${BACKUP_DIR}/daily" ]; then
        log ""
        log "--- Daily Backups ---"
        for backup in "${BACKUP_DIR}/daily"/*.sql.gz.enc; do
            if [ -f "${backup}" ]; then
                total=$((total + 1))
                if verify_single_backup "${backup}"; then
                    passed=$((passed + 1))
                else
                    failed=$((failed + 1))
                fi
            fi
        done
    fi

    # Verify weekly backups
    if [ -d "${BACKUP_DIR}/weekly" ]; then
        log ""
        log "--- Weekly Backups ---"
        for backup in "${BACKUP_DIR}/weekly"/*.sql.gz.enc; do
            if [ -f "${backup}" ]; then
                total=$((total + 1))
                if verify_single_backup "${backup}"; then
                    passed=$((passed + 1))
                else
                    failed=$((failed + 1))
                fi
            fi
        done
    fi

    # Verify monthly backups
    if [ -d "${BACKUP_DIR}/monthly" ]; then
        log ""
        log "--- Monthly Backups ---"
        for backup in "${BACKUP_DIR}/monthly"/*.sql.gz.enc; do
            if [ -f "${backup}" ]; then
                total=$((total + 1))
                if verify_single_backup "${backup}"; then
                    passed=$((passed + 1))
                else
                    failed=$((failed + 1))
                fi
            fi
        done
    fi

    # Summary
    log ""
    log "=========================================="
    log "Verification Summary"
    log "=========================================="
    log "Total backups:  ${total}"
    log "Passed:         ${passed}"
    log "Failed:         ${failed}"
    log "Skipped:        ${skipped}"
    log ""

    if [ ${failed} -gt 0 ]; then
        error "Verification failed for ${failed} backup(s)"
    fi

    log "All backups verified successfully!"
}

main() {
    local target="${1:---all}"

    log "=========================================="
    log "SIMRS Backup Verification"
    log "=========================================="

    # Check prerequisites
    if ! command -v python3 &> /dev/null; then
        error "python3 not found. Required for backup verification."
    fi

    if [ -z "${BACKUP_ENCRYPTION_KEY}" ]; then
        error "BACKUP_ENCRYPTION_KEY not set."
    fi

    # Run verification
    case "${target}" in
        --all)
            verify_all_backups
            ;;
        *)
            if [ -f "${target}" ]; then
                verify_single_backup "${target}"
            else
                error "Backup file not found: ${target}"
            fi
            ;;
    esac

    log "Verification completed at $(date)"
}

# Run main function
main "$@"
