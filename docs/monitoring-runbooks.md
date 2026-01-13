# SIMRS Monitoring Runbooks

## Overview

This document contains runbooks for common alerts and monitoring scenarios in the SIMRS system.

## Table of Contents

1. [Critical Alerts](#critical-alerts)
2. [Warning Alerts](#warning-alerts)
3. [Performance Issues](#performance-issues)
4. [Security Incidents](#security-incidents)
5. [Maintenance Procedures](#maintenance-procedures)

---

## Critical Alerts

### ServiceDown

**Severity:** Critical
**Trigger:** A service has been down for more than 1 minute

**Diagnosis:**
```bash
# Check if service is running
docker ps | grep <service-name>

# Check service logs
docker logs simrs-<service-name> --tail 100

# Check service health
curl http://localhost:<port>/health
```

**Resolution:**
1. Identify which service is down
2. Check logs for error messages
3. Restart the service if needed:
   ```bash
   docker restart simrs-<service-name>
   ```
4. If restart fails, check for resource issues (CPU, memory, disk)
5. Verify database connectivity for backend services

**Prevention:**
- Monitor resource usage trends
- Set up proactive scaling thresholds
- Regular health checks

---

### DatabaseConnectionFailure

**Severity:** Critical
**Trigger:** PostgreSQL database has been unreachable for 1 minute

**Diagnosis:**
```bash
# Check PostgreSQL container
docker ps | grep postgres

# Check PostgreSQL logs
docker logs simrs-postgres --tail 100

# Test database connection
docker exec simrs-postgres pg_isready -U simrs

# Check database connections
docker exec simrs-postgres psql -U simrs -c "SELECT count(*) FROM pg_stat_activity;"
```

**Resolution:**
1. Restart PostgreSQL container:
   ```bash
   docker restart simrs-postgres
   ```
2. If restart fails, check disk space:
   ```bash
   df -h
   ```
3. Check PostgreSQL configuration limits in `docker-compose.yml`
4. Consider increasing max_connections if needed

**Prevention:**
- Monitor connection pool usage
- Implement connection pooling in application
- Regular vacuum and analyze operations

---

### SuspiciousLoginActivity

**Severity:** Critical
**Trigger:** 50+ failed logins per second detected

**Diagnosis:**
```bash
# Check audit logs for suspicious activity
docker exec simrs-backend python -c "
import asyncio
from app.db.session import SessionLocal
from app.crud.audit_log import get_failed_login_attempts

async def check():
    db = SessionLocal()
    attempts = await get_failed_login_attempts(db, None)
    print(f'Failed login attempts: {len(attempts)}')
    for attempt in attempts[:10]:
        print(f'{attempt.username} from {attempt.ip_address}')

asyncio.run(check())
"

# Check current login rate in Prometheus
curl 'http://localhost:9090/api/v1/query?query=rate(simrs_auth_attempts_total{status="failure"}[1m])'
```

**Resolution:**
1. Identify source IP addresses from audit logs
2. Block malicious IPs at firewall level:
   ```bash
   # Example using iptables
   iptables -A INPUT -s <malicious_ip> -j DROP
   ```
3. Consider enabling rate limiting at nginx level
4. Notify users whose accounts may be compromised
5. Implement CAPTCHA for repeated failed attempts

**Prevention:**
- Implement progressive delays after failed attempts
- Use WAF rules for brute force detection
- Enable IP-based rate limiting
- Monitor login patterns

---

### BackupStale

**Severity:** Critical
**Trigger:** Last successful backup was more than 36 hours ago

**Diagnosis:**
```bash
# Check backup container status
docker ps | grep backup

# Check backup logs
docker logs simrs-backup --tail 100

# List available backups
ls -lh /var/lib/docker/volumes/simrs_backup_data/_data/daily/

# Check backup encryption key
docker exec simrs-backup ls -la /backup/.encryption_key
```

**Resolution:**
1. Manual trigger of backup:
   ```bash
   docker exec simrs-backup /scripts/backup_db.sh full
   ```
2. Check for disk space issues
3. Verify database connectivity from backup container
4. Check backup destination accessibility (S3, rsync)
5. Review backup logs for specific errors

**Prevention:**
- Regular backup restoration tests
- Monitor backup job execution times
- Set up backup monitoring dashboards
- Document backup restoration procedures

---

## Warning Alerts

### HighErrorRate

**Severity:** Warning
**Trigger:** Error rate exceeds 5% for 5 minutes

**Diagnosis:**
```bash
# Check error metrics in Prometheus
# Navigate to Grafana: http://localhost:3001/d/simrs-overview

# Check backend logs
docker logs simrs-backend --tail 200 | grep ERROR

# Check database locks
docker exec simrs-postgres psql -U simrs -c "
SELECT * FROM pg_stat_activity WHERE state != 'idle';
"
```

**Resolution:**
1. Identify which endpoints are returning errors
2. Check application logs for stack traces
3. Verify database connectivity and performance
4. Check for recent code deployments
5. Monitor external dependencies (BPJS, SATUSEHAT)

**Prevention:**
- Implement comprehensive error logging
- Set up synthetic monitoring
- Test external integrations regularly
- Use circuit breakers for external APIs

---

### HighResponseTime

**Severity:** Warning
**Trigger:** 95th percentile response time exceeds 1 second

**Diagnosis:**
```bash
# Check slow queries in PostgreSQL
docker exec simrs-postgres psql -U simrs -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"

# Check system resources
docker stats

# Check Redis hit rate
docker exec simrs-redis redis-cli -a redis_password INFO stats
```

**Resolution:**
1. Identify slow database queries and optimize them
2. Add missing database indexes
3. Implement query result caching
4. Check for N+1 query problems
5. Review background job execution times

**Prevention:**
- Regular query performance reviews
- Database indexing strategy
- Implement query timeouts
- Use caching for frequently accessed data

---

### DiskSpaceLow

**Severity:** Warning
**Trigger:** Disk space below 20%

**Diagnosis:**
```bash
# Check disk usage
df -h

# Find large files
du -sh /var/lib/docker/volumes/* | sort -hr | head -20

# Check Docker system usage
docker system df
```

**Resolution:**
1. Clean up Docker resources:
   ```bash
   docker system prune -a --volumes
   ```
2. Remove old log files:
   ```bash
   docker exec simrs-backend find /app/logs -name "*.log" -mtime +30 -delete
   ```
3. Clean up old backups if retention policy allows
4. Expand disk volume if needed

**Prevention:**
- Implement log rotation
- Regular cleanup of temporary files
- Monitor disk usage trends
- Set up automated cleanup jobs

---

### BPJSAPIFailureRate

**Severity:** Warning
**Trigger:** BPJS API failure rate exceeds 20%

**Diagnosis:**
```bash
# Check BPJS API metrics
curl 'http://localhost:9090/api/v1/query?query=rate(simrs_bpjs_api_calls_total{status="failure"}[5m])'

# Check backend logs for BPJS errors
docker logs simrs-backend --tail 100 | grep -i bpjs

# Test BPJS API connectivity manually
docker exec simrs-backend python -c "
import httpx
print(httpx.get('https://apijkn.bpjs-kesehatan.go.id/').status_code)
"
```

**Resolution:**
1. Verify BPJS credentials are current
2. Check BPJS service status (they may have outages)
3. Review BPJS API documentation for changes
4. Implement retry logic with exponential backoff
5. Fallback to manual processes if needed

**Prevention:**
- Monitor BPJS API status page
- Implement circuit breaker pattern
- Cache BPJS responses where appropriate
- Have manual override procedures ready

---

## Performance Issues

### Slow Database Queries

**Symptoms:** High database query duration metric

**Diagnosis:**
```bash
# Enable query statistics if not already enabled
docker exec simrs-postgres psql -U simrs -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# Check slow queries
docker exec simrs-postgres psql -U simrs -c "
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
"
```

**Resolution:**
1. Add appropriate indexes
2. Rewrite queries for better performance
3. Update statistics: `ANALYZE;`
4. Consider partitioning for large tables
5. Review connection pool settings

---

### High Memory Usage

**Symptoms:** Memory usage alerts or OOM kills

**Diagnosis:**
```bash
# Check container memory usage
docker stats --no-stream

# Check Python memory profiling
docker exec simrs-backend python -m memory_profiler app/main.py
```

**Resolution:**
1. Increase container memory limits in docker-compose.yml
2. Check for memory leaks in application code
3. Optimize query result sets
4. Implement pagination for large result sets
5. Review caching strategy

---

## Security Incidents

### Brute Force Attack

**See:** SuspiciousLoginActivity above

### Unauthorized Data Access

**Symptoms:** Audit logs show unexpected data access patterns

**Diagnosis:**
```bash
# Review audit logs for unusual patterns
docker exec simrs-backend python -c "
import asyncio
from app.db.session import SessionLocal
from app.crud.audit_log import get_audit_logs

async def check():
    db = SessionLocal()
    logs = await get_audit_logs(db, limit=100)
    for log in logs:
        if log.action in ['READ', 'EXPORT', 'DOWNLOAD']:
            print(f'{log.username} accessed {log.resource_type}:{log.resource_id} from {log.ip_address}')

asyncio.run(check())
"
```

**Resolution:**
1. Identify compromised accounts
2. Reset passwords for affected users
3. Revoke suspicious sessions
4. Review access permissions
5. Notify security team and management

---

## Maintenance Procedures

### Regular Database Maintenance

**Weekly:**
```bash
# Vacuum and analyze database
docker exec simrs-postgres psql -U simrs -c "VACUUM ANALYZE;"

# Check table bloat
docker exec simrs-postgres psql -U simrs -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

**Monthly:**
```bash
# Reindex database
docker exec simrs-postgres psql -U simrs -c "REINDEX DATABASE simrs;"

# Review and clean up old data
docker exec simrs-postgres psql -U simrs -c "
-- Example: Clean up old audit logs based on retention policy
-- DELETE FROM audit_logs WHERE timestamp < NOW() - INTERVAL '6 years';
"
```

---

### Monitoring System Maintenance

**Daily:**
- Review Grafana dashboards for anomalies
- Check alert delivery is working
- Verify Prometheus targets are up

**Weekly:**
- Review alert rule effectiveness
- Update dashboards as needed
- Check disk usage for monitoring data

**Monthly:**
- Review and update alert thresholds
- Clean up old metrics data
- Test backup restoration procedures

---

### Backup Testing

**Monthly:**
```bash
# Test backup restoration
docker exec simrs-backup /scripts/restore_test.sh

# Verify backup integrity
docker exec simrs-backup python3 -c "
from app.core.backup import BackupManager
bm = BackupManager()
print(bm.verify_latest_backup())
"
```

---

## Contact Information

| Team | Email | On-Call |
|------|-------|---------|
| Infrastructure | infra@simrs.local | +62 xxx xxxx xxxx |
| Backend Team | backend@simrs.local | +62 xxx xxxx xxxx |
| Security Team | security@simrs.local | +62 xxx xxxx xxxx |

## Useful Links

- **Grafana:** http://localhost:3001
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/v1/health/detailed
