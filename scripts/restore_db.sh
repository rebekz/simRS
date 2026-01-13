#!/bin/bash
#
# SIMRS Database Restore Script
#
# Restores PostgreSQL database from encrypted backup.
#
# Usage: ./restore_db.sh <backup_file>
#

set -euo pipefail

# Configuration from environment
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-simrs}"
DB_USER="${DB_USER:-simrs}"
DB_PASSWORD="${DB_PASSWORD:-simrs_password}"

BACKUP_ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $*${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $*${NC}" >&2
    exit 1
}

check_prerequisites() {
    log "Checking prerequisites..."

    # Check if psql is available
    if ! command -v psql &> /dev/null; then
        error "psql not found. Install PostgreSQL client tools."
    fi

    # Check if Python is available for decryption
    if ! command -v python3 &> /dev/null; then
        error "python3 not found. Required for backup decryption."
    fi

    # Check encryption key
    if [ -z "${BACKUP_ENCRYPTION_KEY}" ]; then
        error "BACKUP_ENCRYPTION_KEY not set. Cannot decrypt backup."
    fi

    log "Prerequisites check passed."
}

list_backups() {
    local backup_dir="${BACKUP_DIR:-/backup}"

    log "Available backups:"
    echo ""

    # Daily backups
    if [ -d "${backup_dir}/daily" ]; then
        echo "=== Daily Backups ==="
        ls -lh "${backup_dir}/daily"/*.sql.gz.enc 2>/dev/null || echo "No daily backups found"
        echo ""
    fi

    # Weekly backups
    if [ -d "${backup_dir}/weekly" ]; then
        echo "=== Weekly Backups ==="
        ls -lh "${backup_dir}/weekly"/*.sql.gz.enc 2>/dev/null || echo "No weekly backups found"
        echo ""
    fi

    # Monthly backups
    if [ -d "${backup_dir}/monthly" ]; then
        echo "=== Monthly Backups ==="
        ls -lh "${backup_dir}/monthly"/*.sql.gz.enc 2>/dev/null || echo "No monthly backups found"
        echo ""
    fi
}

verify_backup() {
    local encrypted_file="$1"
    local checksum_file="${encrypted_file}.sha256"

    log "Verifying backup: ${encrypted_file}"

    if [ ! -f "${checksum_file}" ]; then
        warn "Checksum file not found: ${checksum_file}"
        read -p "Continue without verification? (y/N): " confirm
        if [ "${confirm}" != "y" ] && [ "${confirm}" != "Y" ]; then
            error "Restore cancelled by user."
        fi
        return 0
    fi

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

    log "Backup verified successfully."
}

decrypt_backup() {
    local encrypted_file="$1"
    local output_file="$2"

    log "Decrypting backup..."

    python3 -c "
import sys
sys.path.insert(0, '/app/backend/app')
from core.backup import BackupManager

with open('${encrypted_file}', 'rb') as f:
    encrypted_data = f.read()

manager = BackupManager()
decrypted = manager.decrypt_backup(encrypted_data)

with open('${output_file}', 'wb') as f:
    f.write(decrypted)

print(f'Decrypted: {len(decrypted)} bytes')
" || error "Backup decryption failed."

    log "Backup decrypted to: ${output_file}"
}

restore_database() {
    local backup_file="$1"

    # Set PostgreSQL password environment variable
    export PGPASSWORD="${DB_PASSWORD}"

    # Drop existing database (with confirmation)
    log "Checking if database exists..."

    if psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -lqt | cut -d \| -f 1 | grep -qw "${DB_NAME}"; then
        warn "Database '${DB_NAME}' already exists."
        warn "This will DELETE all existing data!"
        read -p "Continue with restore? (yes/no): " confirm

        if [ "${confirm}" != "yes" ]; then
            error "Restore cancelled by user."
        fi

        log "Dropping existing database..."
        psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -c "DROP DATABASE ${DB_NAME};"
    fi

    # Create new database
    log "Creating database: ${DB_NAME}"
    psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME};"

    # Restore from backup
    log "Restoring database from backup..."

    gunzip -c "${backup_file}" | psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}"

    if [ $? -eq 0 ]; then
        log "Database restored successfully!"
    else
        error "Database restore failed!"
    fi
}

main() {
    local backup_file="$1"

    if [ -z "${backup_file}" ]; then
        error "Usage: $0 <backup_file>"
    fi

    if [ "${backup_file}" = "--list" ]; then
        list_backups
        exit 0
    fi

    log "=========================================="
    log "SIMRS Database Restore"
    log "=========================================="
    log ""
    log "Backup file: ${backup_file}"
    log "Target database: ${DB_NAME}"
    log ""

    check_prerequisites

    # Check if backup file exists
    if [ ! -f "${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
    fi

    # Verify backup
    verify_backup "${backup_file}"

    # Decrypt backup
    local decrypted_file="${backup_file%.enc}"
    decrypt_backup "${backup_file}" "${decrypted_file}"

    # Confirm restore
    warn ""
    warn "Ready to restore database!"
    warn "All existing data will be LOST."
    read -p "Type 'yes' to proceed: " confirm

    if [ "${confirm}" != "yes" ]; then
        log "Restore cancelled by user."
        rm -f "${decrypted_file}"
        exit 0
    fi

    # Restore database
    restore_database "${decrypted_file}"

    # Clean up decrypted file
    rm -f "${decrypted_file}"
    log "Cleaned up temporary files."

    log ""
    log "=========================================="
    log "Restore completed successfully!"
    log "=========================================="
}

# Run main function
main "$@"
