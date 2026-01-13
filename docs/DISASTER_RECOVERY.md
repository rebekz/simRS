# SIMRS Disaster Recovery Guide

## Overview

This document outlines the disaster recovery procedures for SIMRS (Sistem Informasi Manajemen Rumah Sakit).

### Recovery Objectives

- **RTO (Recovery Time Objective)**: <4 hours for critical systems
- **RPO (Recovery Point Objective)**: <15 minutes for critical data

### Backup Strategy

| Backup Type | Frequency | Retention | Location |
|-------------|-----------|-----------|----------|
| Full (pg_dump) | Daily (2 AM) | 30 days | Local + Off-site |
| Weekly Archive | Weekly (Sunday) | 12 months | Local + Off-site |
| Monthly Archive | Monthly (1st) | 7 years | Local + Off-site |
| WAL Archives | Continuous | 30 days | Local + Off-site |

### Backup Encryption

All backups are encrypted using **AES-256-GCM** with a unique encryption key.
- Encryption key: `BACKUP_ENCRYPTION_KEY` (stored in environment)
- Algorithm: Fernet (AES-128-CBC + HMAC)
- Key rotation: Recommended annually

---

## 1. Backup Procedures

### 1.1 Automated Daily Backups

Daily backups run automatically at 2 AM via cron job in the backup container.

**Location**: `/backup/daily/`

**Format**: `simrs_YYYYMMDD_HHMMSS.sql.gz.enc`

**Verification**: Backups are verified automatically at 4 AM.

### 1.2 Manual Backup Creation

To create a manual backup:

```bash
docker exec simrs-backup /scripts/backup_db.sh full
```

### 1.3 Listing Available Backups

```bash
docker exec simrs-backup /scripts/restore_db.sh --list
```

### 1.4 Backup Verification

To verify all backups:

```bash
docker exec simrs-backup /scripts/verify_backup.sh --all
```

To verify a specific backup:

```bash
docker exec simrs-backup /scripts/verify_backup.sh /backup/daily/simrs_20250113_020000.sql.gz.enc
```

---

## 2. Recovery Procedures

### 2.1 Complete Database Restoration

**Use case**: Complete data loss, database corruption, or migration to new server.

**Prerequisites**:
- Docker Compose installed
- Backup encryption key available
- Backup file accessible

**Steps**:

1. **Stop all services**:
   ```bash
   docker-compose down
   ```

2. **Remove old database volume** (WARNING: This deletes all data):
   ```bash
   docker volume rm simrs_postgres_data
   ```

3. **Start PostgreSQL container**:
   ```bash
   docker-compose up -d postgres
   ```

4. **Wait for database to be ready**:
   ```bash
   docker-compose logs -f postgres
   # Wait until "database system is ready to accept connections"
   ```

5. **Restore from backup**:
   ```bash
   docker exec simrs-backup /scripts/restore_db.sh /backup/daily/simrs_YYYYMMDD_HHMMSS.sql.gz.enc
   ```

6. **Start all services**:
   ```bash
   docker-compose up -d
   ```

7. **Verify restoration**:
   - Login to admin panel
   - Check patient records
   - Verify audit logs

### 2.2 Point-in-Time Recovery (PITR) using WAL

**Use case**: Recover to a specific point in time (e.g., before accidental deletion).

**Prerequisites**:
- WAL archiving enabled
- Base backup available
- WAL files available

**Steps**:

1. **Identify target time**:
   ```bash
   # Check audit logs to find the exact time
   grep "DELETE FROM patients" /backup/audit.log
   ```

2. **Restore base backup**:
   ```bash
   # Follow complete database restoration steps
   ```

3. **Create recovery.conf**:
   ```bash
   cat > /var/lib/postgresql/data/recovery.conf <<EOF
   restore_command = 'cp /backup/wal/%f %p'
   recovery_target_time = '2025-01-13 14:30:00'
   EOF
   ```

4. **Restart PostgreSQL**:
   ```bash
   docker-compose restart postgres
   ```

5. **Monitor recovery**:
   ```bash
   docker-compose logs -f postgres
   ```

### 2.3 Off-site Recovery

**Use case**: Primary data center unavailable, need to recover from off-site backup.

**AWS S3**:

```bash
# List backups in S3
aws s3 ls s3://your-bucket/simrs-backups/daily/ --recursive

# Download specific backup
aws s3 cp s3://your-bucket/simrs-backups/daily/simrs_20250113_020000.sql.gz.enc /backup/

# Restore
docker exec simrs-backup /scripts/restore_db.sh /backup/simrs_20250113_020000.sql.gz.enc
```

**Rsync**:

```bash
# Sync from remote server
rsync -avz backup-user@remote-server:/backups/simrs/daily/ /backup/daily/

# Restore latest
docker exec simrs-backup /scripts/restore_db.sh /backup/daily/simrs_$(ls -t /backup/daily/ | head -1)
```

---

## 3. Monitoring and Alerting

### 3.1 Backup Status Dashboard

Access backup statistics:

```bash
python3 -m backend.app.core.backup_monitor --backup-dir /backup --stats
```

### 3.2 Backup Health Checks

```bash
# Check for missing or failed backups
python3 -m backend.app.core.backup_monitor --backup-dir /backup --check
```

### 3.3 Email Alerts

Configure email alerts in `.env`:

```bash
BACKUP_ALERT_EMAIL=admin@hospital.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

Alert conditions:
- Daily backup missing (>26 hours old)
- Weekly backup missing (>8 days old)
- Disk space >80% (warning) or >90% (critical)
- WAL archiving stalled (>30 minutes)

---

## 4. Testing and Maintenance

### 4.1 Quarterly Backup Testing

**Frequency**: Every 3 months

**Procedure**:

1. **Select a random backup**:
   ```bash
   ls /backup/daily/*.sql.gz.enc | shuf -n 1
   ```

2. **Restore to test environment**:
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   docker exec simrs-test-backup /scripts/restore_db.sh /backup/daily/selected_backup.sql.gz.enc
   ```

3. **Verify data integrity**:
   - Check patient count matches production
   - Verify sensitive data encrypted
   - Test critical queries

4. **Document results**:
   ```bash
   echo "Backup test $(date): SUCCESS" >> /backup/test_log.txt
   ```

### 4.2 Encryption Key Rotation

**Frequency**: Annually

**Procedure**:

1. **Generate new key**:
   ```bash
   python3 -m backend.app.core.backup
   ```

2. **Re-encrypt existing backups**:
   ```bash
   for backup in /backup/daily/*.enc; do
     # Decrypt with old key
     # Encrypt with new key
     # Replace original file
   done
   ```

3. **Update environment**:
   ```bash
   BACKUP_ENCRYPTION_KEY=<new_key>
   ```

4. **Verify new backups**:
   ```bash
   /scripts/verify_backup.sh --all
   ```

### 4.3 Off-site Sync Testing

**Frequency**: Monthly

**Procedure**:

1. **List off-site backups**:
   ```bash
   aws s3 ls s3://your-bucket/simrs-backups/daily/ --recursive
   ```

2. **Compare with local**:
   ```bash
   ls -l /backup/daily/
   ```

3. **Test restore from off-site**:
   ```bash
   aws s3 cp s3://your-bucket/simrs-backups/daily/latest.sql.gz.enc - \
     | docker exec -i simrs-backup /scripts/restore_db.sh /dev/stdin
   ```

---

## 5. Common Issues and Solutions

### 5.1 Backup Fails with "No space left on device"

**Problem**: Disk full.

**Solution**:

```bash
# Check disk usage
df -h /backup

# Clean old backups (beyond retention policy)
docker exec simrs-backup /scripts/backup_db.sh rotate

# Off-site sync to free local space
docker exec simrs-backup /scripts/sync_offsite_backup.sh
```

### 5.2 Restore Fails with "Invalid checksum"

**Problem**: Backup corrupted or wrong encryption key.

**Solution**:

```bash
# Verify encryption key
echo $BACKUP_ENCRYPTION_KEY

# Try alternative backup
ls -lht /backup/daily/ | head -5

# If all backups corrupted, recover from off-site
aws s3 ls s3://your-bucket/simrs-backups/
```

### 5.3 WAL Archiving Stopped

**Problem**: WAL files not being archived.

**Solution**:

```bash
# Check PostgreSQL WAL settings
docker exec simrs-postgres psql -U simrs -c "SHOW archive_mode;"
docker exec simrs-postgres psql -U simrs -c "SHOW archive_command;"

# Check archive directory
docker exec simrs-backup ls -lh /backup/wal/

# Restart archiving
docker exec simrs-postgres psql -U simrs -c "SELECT pg_archive_restart();"
```

---

## 6. Contact and Escalation

### Primary Contact

**System Administrator**: admin@hospital.com
**On-Call**: +62 XXX XXXX XXXX

### Escalation Path

1. **Level 1**: System Administrator (1 hour response)
2. **Level 2**: IT Director (30 minute response for critical incidents)
3. **Level 3**: External Database Consultant (for complex recovery scenarios)

### Incident Reporting

All recovery operations should be documented in:

```bash
/backup/incident_log_$(date +%Y%m%d).txt
```

Include:
- Date and time
- Incident description
- Recovery steps taken
- Verification results
- Lessons learned

---

## 7. Compliance and Retention

### Regulatory Requirements

- **UU 27/2022 (PDP Law)**: Audit logs retained 6 years
- **Permenkes 82/2013**: Inpatient records retained 25 years
- **Permenkes 24/2022**: Outpatient records retained 10 years

### Backup Retention Policy

| Data Type | Retention Period |
|-----------|------------------|
| Daily backups | 30 days |
| Weekly backups | 12 months |
| Monthly backups | 7 years |
| WAL archives | 30 days |
| Audit logs | 6 years |

### Data Disposal

Expired backups are automatically removed by the backup rotation script.

For manual disposal:

```bash
# Shred sensitive backup files
shred -vfz -n 3 /backup/daily/old_backup.sql.gz.enc
```

---

## Appendix A: Environment Variables

```bash
# Database
POSTGRES_USER=simrs
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=simrs
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Backup
BACKUP_DIR=/backup
BACKUP_ENCRYPTION_KEY=<64-character hex string>

# Off-site (S3)
S3_BUCKET=your-backup-bucket
S3_PREFIX=simrs-backups/
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# Off-site (Rsync)
RSYNC_HOST=backup.example.com
RSYNC_USER=backup-user
RSYNC_PATH=/backups/simrs

# Alerts
BACKUP_ALERT_EMAIL=admin@hospital.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## Appendix B: Recovery Checklist

**Before Recovery**:
- [ ] Identify root cause of data loss
- [ ] Select appropriate backup source
- [ ] Verify encryption key available
- [ ] Notify stakeholders of downtime
- [ ] Document recovery plan

**During Recovery**:
- [ ] Stop all application services
- [ ] Backup current state (if possible)
- [ ] Restore database from backup
- [ ] Verify data integrity
- [ ] Run application health checks

**After Recovery**:
- [ ] Restart all services
- [ ] Verify critical functionality
- [ ] Monitor for errors
- [ ] Update incident log
- [ ] Conduct post-mortem
- [ ] Update procedures if needed
