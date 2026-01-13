#!/bin/bash
#
# SIMRS Automated Database Backup Script
#
# Performs automated PostgreSQL backups with:
# - Full database dump using pg_dump
# - Compression with gzip
# - Encryption using AES-256-GCM
# - Checksum verification
# - Automated retention policy
#
# Usage: ./backup_db.sh [full|incremental]
#

set -euo pipefail

# Configuration from environment
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-simrs}"
DB_USER="${DB_USER:-simrs}"
DB_PASSWORD="${DB_PASSWORD:-simrs_password}"

BACKUP_DIR="${BACKUP_DIR:-/backup}"
BACKUP_ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

# Retention policy
DAILY_RETENTION_DAYS="${DAILY_RETENTION_DAYS:-30}"
WEEKLY_RETENTION_MONTHS="${WEEKLY_RETENTION_MONTHS:-12}"
MONTHLY_RETENTION_YEARS="${MONTHLY_RETENTION_YEARS:-7}"

# Logging
LOG_FILE="${BACKUP_DIR}/backup.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

# Functions
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "ERROR: $*"
    exit 1
}

check_prerequisites() {
    log "Checking prerequisites..."

    # Check if pg_dump is available
    if ! command -v pg_dump &> /dev/null; then
        error "pg_dump not found. Install PostgreSQL client tools."
    fi

    # Check if Python is available for encryption
    if ! command -v python3 &> /dev/null; then
        error "python3 not found. Required for backup encryption."
    fi

    # Check backup directory
    if [ ! -d "${BACKUP_DIR}" ]; then
        log "Creating backup directory: ${BACKUP_DIR}"
        mkdir -p "${BACKUP_DIR}/daily"
        mkdir -p "${BACKUP_DIR}/weekly"
        mkdir -p "${BACKUP_DIR}/monthly"
    fi

    # Check encryption key
    if [ -z "${BACKUP_ENCRYPTION_KEY}" ]; then
        error "BACKUP_ENCRYPTION_KEY not set. Backups must be encrypted."
    fi

    log "Prerequisites check passed."
}

create_full_backup() {
    log "Starting full database backup..."

    local timestamp=$(date +'%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_DIR}/daily/simrs_${timestamp}.sql.gz"
    local encrypted_file="${backup_file}.enc"
    local checksum_file="${backup_file}.sha256"

    # Set PostgreSQL password environment variable
    export PGPASSWORD="${DB_PASSWORD}"

    # Create database dump with pg_dump
    log "Running pg_dump on ${DB_NAME}..."

    if ! pg_dump -h "${DB_HOST}" \
                -p "${DB_PORT}" \
                -U "${DB_USER}" \
                -d "${DB_NAME}" \
                --format=plain \
                --no-owner \
                --no-acl \
                --verbose \
                2>&1 | gzip > "${backup_file}"; then
        error "pg_dump failed. Check database connectivity and permissions."
    fi

    local original_size=$(wc -c < "${backup_file}")
    log "Database dump created: ${backup_file} (${original_size} bytes)"

    # Encrypt the backup
    log "Encrypting backup..."

    python3 -c "
import sys
sys.path.insert(0, '/app/backend/app')
from core.backup import BackupManager

with open('${backup_file}', 'rb') as f:
    data = f.read()

manager = BackupManager()
encrypted, checksum = manager.create_backup(data, compress=False, encrypt=True)

with open('${encrypted_file}', 'wb') as f:
    f.write(encrypted)

with open('${checksum_file}', 'w') as f:
    f.write(checksum)

print(f'Encrypted backup size: {len(encrypted)} bytes')
print(f'Checksum: {checksum}')
    " || error "Backup encryption failed."

    local encrypted_size=$(wc -c < "${encrypted_file}")
    log "Backup encrypted: ${encrypted_file} (${encrypted_size} bytes)"

    # Verify the backup
    log "Verifying backup integrity..."

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
print('Backup verification successful')
    " || error "Backup verification failed."

    # Remove unencrypted backup
    rm -f "${backup_file}"
    log "Removed unencrypted backup file"

    log "Full backup completed successfully: ${encrypted_file}"
    echo "${encrypted_file}"
}

create_incremental_backup() {
    log "Incremental backups use WAL archiving (see postgresql.conf)"
    log "WAL files should be continuously archived to ${BACKUP_DIR}/wal/"
    log "No additional action needed for incremental backup."
}

rotate_backups() {
    log "Rotating old backups..."

    # Daily backups - keep last N days
    log "Cleaning daily backups (keep ${DAILY_RETENTION_DAYS} days)..."
    find "${BACKUP_DIR}/daily" -name "simrs_*.sql.gz.enc" -mtime +${DAILY_RETENTION_DAYS} -delete

    # Weekly backups - keep last N months
    log "Cleaning weekly backups (keep ${WEEKLY_RETENTION_MONTHS} months)..."
    find "${BACKUP_DIR}/weekly" -name "simrs_*.sql.gz.enc" -mtime +$((WEEKLY_RETENTION_MONTHS * 30)) -delete

    # Monthly backups - keep last N years
    log "Cleaning monthly backups (keep ${MONTHLY_RETENTION_YEARS} years)..."
    find "${BACKUP_DIR}/monthly" -name "simrs_*.sql.gz.enc" -mtime +$((MONTHLY_RETENTION_YEARS * 365)) -delete

    # Count remaining backups
    local daily_count=$(find "${BACKUP_DIR}/daily" -name "simrs_*.sql.gz.enc" | wc -l)
    local weekly_count=$(find "${BACKUP_DIR}/weekly" -name "simrs_*.sql.gz.enc" | wc -l)
    local monthly_count=$(find "${BACKUP_DIR}/monthly" -name "simrs_*.sql.gz.enc" | wc -l)

    log "Remaining backups: ${daily_count} daily, ${weekly_count} weekly, ${monthly_count} monthly"
}

promote_to_weekly() {
    # Run on Sundays (day 0)
    local day_of_week=$(date +%u)
    if [ ${day_of_week} -eq 7 ]; then
        log "Promoting backup to weekly..."
        local latest_backup=$(ls -t "${BACKUP_DIR}/daily/simrs_"*.sql.gz.enc 2>/dev/null | head -1)
        if [ -n "${latest_backup}" ]; then
            local weekly_name=$(basename "${latest_backup}")
            cp "${latest_backup}" "${BACKUP_DIR}/weekly/${weekly_name}"
            log "Weekly backup created: ${weekly_name}"
        fi
    fi
}

promote_to_monthly() {
    # Run on first day of month
    local day_of_month=$(date +%d)
    if [ "${day_of_month}" = "01" ]; then
        log "Promoting backup to monthly..."
        local latest_backup=$(ls -t "${BACKUP_DIR}/daily/simrs_"*.sql.gz.enc 2>/dev/null | head -1)
        if [ -n "${latest_backup}" ]; then
            local monthly_name=$(basename "${latest_backup}")
            cp "${latest_backup}" "${BACKUP_DIR}/monthly/${monthly_name}"
            log "Monthly backup created: ${monthly_name}"
        fi
    fi
}

send_alert() {
    local status=$1
    local message=$2

    log "ALERT [${status}]: ${message}"

    # TODO: Implement email/Slack/SMS alerts
    # For now, just log
}

main() {
    local backup_type="${1:-full}"

    log "=========================================="
    log "SIMRS Database Backup - ${backup_type}"
    log "=========================================="

    check_prerequisites

    case "${backup_type}" in
        full)
            create_full_backup
            promote_to_weekly
            promote_to_monthly
            rotate_backups
            send_alert "SUCCESS" "Full backup completed successfully"
            ;;
        incremental)
            create_incremental_backup
            ;;
        rotate)
            rotate_backups
            ;;
        *)
            error "Unknown backup type: ${backup_type}. Use 'full' or 'incremental'"
            ;;
    esac

    log "Backup job completed at $(date)"
}

# Run main function
main "$@"
