# SIMRS Monitoring Setup Guide

## Overview

This guide explains how to set up and use the monitoring infrastructure for the SIMRS system.

## Architecture

The SIMRS monitoring stack consists of:

1. **Prometheus** - Metrics collection and storage
2. **Grafana** - Visualization and dashboards
3. **Alertmanager** - Alert routing and notification
4. **Loki** - Log aggregation
5. **Promtail** - Log collection
6. **Node Exporter** - System metrics
7. **cAdvisor** - Container metrics
8. **PostgreSQL Exporter** - Database metrics
9. **Redis Exporter** - Cache metrics

## Quick Start

### 1. Start Monitoring Services

```bash
# Start all services including monitoring
docker-compose up -d

# Or start only monitoring services
docker-compose up -d prometheus grafana alertmanager
```

### 2. Access Dashboards

- **Grafana:** http://localhost:3001
  - Default credentials: admin / admin (change on first login)
- **Prometheus:** http://localhost:9090
- **Alertmanager:** http://localhost:9093

### 3. Verify Metrics Collection

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# View application metrics
curl http://localhost:8000/metrics

# Check detailed health
curl http://localhost:8000/api/v1/health/detailed
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password
GRAFANA_PORT=3001

# Prometheus
PROMETHEUS_PORT=9090

# Alertmanager
ALERTMANAGER_PORT=9093

# SMTP for Alerts (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@simrs.local
SMTP_PASSWORD=your_app_password
SMTP_FROM=alerts@simrs.local

# Alert Recipients
DEFAULT_ALERT_EMAIL=admin@simrs.local
CRITICAL_ALERT_EMAIL=oncall@simrs.local
SECURITY_ALERT_EMAIL=security@simrs.local
INFRA_ALERT_EMAIL=infra@simrs.local
BACKEND_ALERT_EMAIL=backend@simrs.local
```

### Alert Configuration

Edit `monitoring/prometheus/alerts.yml` to customize alert thresholds.

Example: Change response time threshold
```yaml
- alert: HighResponseTime
  expr: |
    histogram_quantile(0.95,
      rate(simrs_http_request_duration_seconds_bucket[5m])
    ) > 1  # Change this value (in seconds)
```

### Email Alerts Setup

For Gmail:
1. Create an app-specific password
2. Update `.env` with:
   ```bash
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

For SendGrid:
```bash
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=YOUR_SENDGRID_API_KEY
```

## Metrics Reference

### Application Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `simrs_http_requests_total` | Counter | Total HTTP requests |
| `simrs_http_request_duration_seconds` | Histogram | HTTP request latency |
| `simrs_db_queries_total` | Counter | Database queries |
| `simrs_auth_attempts_total` | Counter | Authentication attempts |
| `simrs_patient_registrations_total` | Counter | Patient registrations |
| `simrs_backup_operations_total` | Counter | Backup operations |

### System Health Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `simrs_system_health_status` | Gauge | Service health status (0/1) |
| `simrs_db_connections_active` | Gauge | Active database connections |
| `simrs_auth_sessions_active` | Gauge | Active user sessions |
| `simrs_backup_last_success_timestamp` | Gauge | Last successful backup |

## Grafana Dashboards

### SIMRS Overview Dashboard

Auto-provisioned dashboard showing:
- System health status
- Request rate and response times
- Error rates
- Database, Redis, MinIO status
- Authentication activity
- Backup status

Access: http://localhost:3001/d/simrs-overview

### Creating Custom Dashboards

1. Login to Grafana
2. Click "+" → "Dashboard"
3. Add panels with Prometheus queries
4. Save dashboard

Example Queries:

**Request Rate:**
```
sum(rate(simrs_http_requests_total[5m]))
```

**Error Rate:**
```
sum(rate(simrs_http_requests_total{status=~"5.."}[5m])) / sum(rate(simrs_http_requests_total[5m])) * 100
```

**Response Time (p95):**
```
histogram_quantile(0.95, sum(rate(simrs_http_request_duration_seconds_bucket[5m])) by (le))
```

## Common Tasks

### Adding a New Alert

1. Edit `monitoring/prometheus/alerts.yml`
2. Add new alert rule:
   ```yaml
   - alert: MyCustomAlert
     expr: my_metric > threshold
     for: 5m
     labels:
       severity: warning
     annotations:
       summary: "Custom alert summary"
       description: "{{ $value }}"
   """
3. Reload Prometheus config:
   ```bash
   docker exec simrs-prometheus kill -HUP 1
   ```

### Testing Alerts

```bash
# Test alert endpoint
curl -X POST http://localhost:8000/api/v1/monitoring/test-alert \
  -H "Authorization: Bearer YOUR_TOKEN"

# Manually trigger a metric
docker exec simrs-backend python -c "
from app.core.metrics import errors_total
errors_total.labels(type='test', severity='warning').inc()
"
```

### Viewing Logs in Loki

1. Login to Grafana
2. Click "Explore" → Select Loki
3. Enter query:
   ```
   {job="backend"} |= "ERROR"
   ```
4. View logs with correlation to metrics

### Backup Monitoring Data

```bash
# Backup Prometheus data
docker exec simrs-prometheus tar -czf /tmp/prometheus-backup.tar.gz /prometheus
docker cp simrs-prometheus:/tmp/prometheus-backup.tar.gz ./prometheus-backup.tar.gz

# Backup Grafana data
docker exec simrs-grafana tar -czf /tmp/grafana-backup.tar.gz /var/lib/grafana
docker cp simrs-grafana:/tmp/grafana-backup.tar.gz ./grafana-backup.tar.gz
```

## Troubleshooting

### Metrics Not Appearing

```bash
# Check if metrics endpoint is accessible
curl http://localhost:8000/metrics

# Check if Prometheus is scraping targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job=="simrs-backend")'

# Check backend logs for errors
docker logs simrs-backend --tail 50
```

### Grafana Login Issues

```bash
# Reset admin password
docker exec simrs-grafana grafana-cli admin reset-admin-password newpassword

# Check Grafana logs
docker logs simrs-grafana --tail 50
```

### Alerts Not Firing

```bash
# Check Alertmanager configuration
curl http://localhost:9093/api/v1/status/config

# Check active alerts in Prometheus
curl http://localhost:9090/api/v1/alerts | jq '.'

# Test Alertmanager webhook
curl -X POST http://localhost:9093/api/v1/alerts -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning"
    },
    "annotations": {
      "description": "This is a test alert"
    }
  }
]'
```

### High Disk Usage

```bash
# Check Prometheus data size
docker exec simrs-prometheus du -sh /prometheus

# Reduce retention time (edit docker-compose.yml)
# --storage.tsdb.retention.time=15d

# Clean up old data
docker exec simrs-prometheus promtool tsdb delete-series \
  '{__name__=~".+"}' --start=2024-01-01T00:00:00Z --end=2024-02-01T00:00:00Z
```

## Performance Tuning

### Prometheus

**Increase Scraping Interval** (for large deployments):
```yaml
global:
  scrape_interval: 30s  # Default is 15s
```

**Increase Retention:**
```yaml
command:
  - '--storage.tsdb.retention.time=30d'  # Default is 15d
```

### Grafana

**Configure caching** (in grafana.ini):
```ini
[caching]
enabled = true
ttl = 5m
```

## External Monitoring

### UptimeRobot Setup

1. Create account at https://uptimerobot.com
2. Add monitors for:
   - http://your-domain.com/health
   - http://your-domain.com/api/v1/health/detailed
3. Configure alert notifications

### Statuspage Integration

For public status page:
1. Use hosted status page service (Statuspage.io, StatusBadger)
2. Configure health check endpoints
3. Customize incident communication

## Security Best Practices

1. **Change Default Credentials**
   ```bash
   # Update Grafana admin password
   docker exec simrs-grafana grafana-cli admin reset-admin-password NEW_PASSWORD
   ```

2. **Restrict Access**
   - Use nginx reverse proxy with authentication
   - Limit access to monitoring ports in production
   - Use firewall rules to restrict access

3. **Use HTTPS**
   - Configure SSL certificates for Grafana
   - Use secure connections for all monitoring endpoints

4. **Regular Updates**
   ```bash
   docker-compose pull prometheus grafana alertmanager
   docker-compose up -d prometheus grafana alertmanager
   ```

## Next Steps

1. Review [Monitoring Runbooks](monitoring-runbooks.md) for common procedures
2. Customize alert thresholds for your environment
3. Set up notification channels (email, SMS, Slack)
4. Create custom dashboards for your specific needs
5. Document team-specific procedures

## Support

For issues with:
- **Configuration:** Check this guide and runbook documentation
- **Metrics:** Review Prometheus targets and scrape configs
- **Alerts:** Check Alertmanager status and notification settings
- **Dashboards:** Review Grafana datasource configurations

## Additional Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Alertmanager Documentation](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
