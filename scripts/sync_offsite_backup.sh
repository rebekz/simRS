#!/bin/bash
#
# SIMRS Off-site Backup Sync Script
#
# Syncs encrypted backups to off-site storage (S3, rsync, or other).
# Run weekly to ensure disaster recovery capability.
#
# Usage: ./sync_offsite_backup.sh [s3|rsync]
#

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backup}"
OFFSITE_TYPE="${OFFSITE_TYPE:-s3}"

# S3 Configuration
S3_BUCKET="${S3_BUCKET:-}"
S3_PREFIX="${S3_PREFIX:-simrs-backups/}"

# Rsync Configuration
RSYNC_HOST="${RSYNC_HOST:-}"
RSYNC_USER="${RSYNC_USER:-}"
RSYNC_PATH="${RSYNC_PATH:-/backups/simrs}"

# Logging
LOG_FILE="${BACKUP_DIR}/offsite_sync.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "ERROR: $*"
    exit 1
}

sync_to_s3() {
    log "Syncing backups to S3..."

    # Check if AWS CLI is available
    if ! command -v aws &> /dev/null; then
        error "AWS CLI not found. Install with: pip install awscli"
    fi

    # Check S3 configuration
    if [ -z "${S3_BUCKET}" ]; then
        error "S3_BUCKET environment variable not set"
    fi

    # Sync daily backups
    log "Syncing daily backups..."
    aws s3 sync "${BACKUP_DIR}/daily/" "s3://${S3_BUCKET}/${S3_PREFIX}daily/" \
        --storage-class STANDARD_IA \
        --only-show-errors || error "Failed to sync daily backups to S3"

    # Sync weekly backups
    log "Syncing weekly backups..."
    aws s3 sync "${BACKUP_DIR}/weekly/" "s3://${S3_BUCKET}/${S3_PREFIX}weekly/" \
        --storage-class GLACIER \
        --only-show-errors || error "Failed to sync weekly backups to S3"

    # Sync monthly backups
    log "Syncing monthly backups..."
    aws s3 sync "${BACKUP_DIR}/monthly/" "s3://${S3_BUCKET}/${S3_PREFIX}monthly/" \
        --storage-class GLACIER \
        --only-show-errors || error "Failed to sync monthly backups to S3"

    # Sync WAL archives
    if [ -d "${BACKUP_DIR}/wal" ]; then
        log "Syncing WAL archives..."
        aws s3 sync "${BACKUP_DIR}/wal/" "s3://${S3_BUCKET}/${S3_PREFIX}wal/" \
            --storage-class STANDARD_IA \
            --only-show-errors || error "Failed to sync WAL archives to S3"
    fi

    log "S3 sync completed successfully"
}

sync_to_rsync() {
    log "Syncing backups via rsync..."

    # Check if rsync is available
    if ! command -v rsync &> /dev/null; then
        error "rsync not found. Install with system package manager"
    fi

    # Check rsync configuration
    if [ -z "${RSYNC_HOST}" ]; then
        error "RSYNC_HOST environment variable not set"
    fi

    local remote_path="${RSYNC_USER}@${RSYNC_HOST}:${RSYNC_PATH}"

    # Sync daily backups
    log "Syncing daily backups..."
    rsync -avz --delete "${BACKUP_DIR}/daily/" "${remote_path}/daily/" \
        || error "Failed to sync daily backups via rsync"

    # Sync weekly backups
    log "Syncing weekly backups..."
    rsync -avz --delete "${BACKUP_DIR}/weekly/" "${remote_path}/weekly/" \
        || error "Failed to sync weekly backups via rsync"

    # Sync monthly backups
    log "Syncing monthly backups..."
    rsync -avz --delete "${BACKUP_DIR}/monthly/" "${remote_path}/monthly/" \
        || error "Failed to sync monthly backups via rsync"

    # Sync WAL archives
    if [ -d "${BACKUP_DIR}/wal" ]; then
        log "Syncing WAL archives..."
        rsync -avz --delete "${BACKUP_DIR}/wal/" "${remote_path}/wal/" \
            || error "Failed to sync WAL archives via rsync"
    fi

    log "rsync completed successfully"
}

verify_offsite_backup() {
    log "Verifying off-site backup..."

    case "${OFFSITE_TYPE}" in
        s3)
            # List files in S3
            log "S3 backup contents:"
            aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}" --recursive --human-readable
            ;;
        rsync)
            # List files on remote server
            log "Remote backup contents:"
            ssh "${RSYNC_USER}@${RSYNC_HOST}" "ls -lhR ${RSYNC_PATH}"
            ;;
    esac

    log "Off-site backup verification completed"
}

send_alert() {
    local status=$1
    local message=$2

    log "ALERT [${status}]: ${message}"

    # TODO: Implement email/Slack/SMS alerts
}

main() {
    local sync_type="${1:-${OFFSITE_TYPE}}"

    log "=========================================="
    log "SIMRS Off-site Backup Sync - ${sync_type}"
    log "=========================================="

    # Sync backups
    case "${sync_type}" in
        s3)
            sync_to_s3
            ;;
        rsync)
            sync_to_rsync
            ;;
        *)
            error "Unknown sync type: ${sync_type}. Use 's3' or 'rsync'"
            ;;
    esac

    # Verify off-site backup
    verify_offsite_backup

    # Send success alert
    send_alert "SUCCESS" "Off-site backup sync completed successfully"

    log "Off-site sync job completed at $(date)"
}

# Run main function
main "$@"
