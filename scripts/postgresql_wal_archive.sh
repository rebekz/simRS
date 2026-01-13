#!/bin/bash
#
# PostgreSQL WAL Archive Command
#
# This script is called by PostgreSQL to archive WAL files.
# Configure in postgresql.conf:
#   archive_mode = on
#   archive_command = '/scripts/postgresql_wal_archive.sh %p %f'
#
# Args:
#   %p - path to WAL file to archive
#   %f - name of WAL file
#

set -euo pipefail

WAL_FILE_PATH="$1"
WAL_FILE_NAME="$2"
WAL_ARCHIVE_DIR="${WAL_ARCHIVE_DIR:-/backup/wal}"

# Log file
LOG_FILE="${WAL_ARCHIVE_DIR}/archive.log"
mkdir -p "$(dirname "${LOG_FILE}")"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" >> "${LOG_FILE}"
}

# Create archive directory if it doesn't exist
mkdir -p "${WAL_ARCHIVE_DIR}"

# Check if WAL file exists
if [ ! -f "${WAL_FILE_PATH}" ]; then
    log "ERROR: WAL file not found: ${WAL_FILE_PATH}"
    exit 1
fi

# Copy WAL file to archive
cp "${WAL_FILE_PATH}" "${WAL_ARCHIVE_DIR}/${WAL_FILE_NAME}"

if [ $? -eq 0 ]; then
    log "Archived WAL file: ${WAL_FILE_NAME} ($(wc -c < "${WAL_ARCHIVE_DIR}/${WAL_FILE_NAME}") bytes)"
    exit 0
else
    log "ERROR: Failed to archive WAL file: ${WAL_FILE_NAME}"
    exit 1
fi
