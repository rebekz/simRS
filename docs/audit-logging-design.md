# Audit Logging System Design

## Overview

Comprehensive audit logging system for SIMRS to comply with Indonesian regulations (UU 27/2022) requiring 6-year retention of patient data access logs.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FastAPI Request                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Audit Middleware                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Extract request info (user, IP, UA, path, method)  │   │
│  │ 2. Determine resource type and action from route       │   │
│  │ 3. Check if route requires audit logging              │   │
│  │ 4. Filter sensitive data (passwords, tokens)          │   │
│  │ 5. Queue async log entry                              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Background Task Queue                      │
│  (FastAPI BackgroundTasks - non-blocking)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Audit Log Processing                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Encrypt sensitive fields (request/response body)   │   │
│  │ 2. Write to audit_logs table                         │   │
│  │ 3. Check if sensitive operation → trigger alert      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Request → Middleware → Extract Info → Filter Sensitive Data
                                    ↓
                            Queue Background Task
                                    ↓
                            Process Async (non-blocking)
                                    ↓
                    Encrypt → Store → Check Alerts
```

## Endpoints to Audit

### High Priority (Patient Data)
- `POST /api/v1/patients` - Patient registration
- `GET /api/v1/patients/{id}` - Patient data access
- `PUT /api/v1/patients/{id}` - Patient data update
- `DELETE /api/v1/patients/{id}` - Patient deletion

### Medium Priority (Clinical Data)
- `POST /api/v1/encounters` - Create encounter
- `GET /api/v1/encounters/{id}` - View encounter
- `POST /api/v1/prescriptions` - Create prescription
- `POST /api/v1/diagnoses` - Add diagnosis

### Sensitive Operations (Alert Triggering)
- `POST /api/v1/export/*` - Data export
- `DELETE /api/v1/patients/bulk` - Bulk delete
- `PUT /api/v1/users/{id}/permissions` - Permission changes
- `POST /api/v1/system/config` - System configuration changes

## Audit Log Fields

### Captured Data
- `timestamp` - Auto-generated, indexed
- `user_id` - Foreign key to users table
- `username` - Denormalized for search
- `action` - CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT, etc.
- `resource_type` - Patient, User, Prescription, etc.
- `resource_id` - ID of affected resource
- `ip_address` - Client IP (IPv6 compatible)
- `user_agent` - Browser/client info
- `request_path` - Full request path
- `request_method` - HTTP method
- `success` - Boolean, indexed
- `failure_reason` - Error details if failed
- `request_body` - Encrypted request payload
- `response_body` - Encrypted response payload
- `changes` - Encrypted before/after diff for updates

### Sensitive Data Exclusions
The following fields are NEVER logged:
- Passwords (any field containing "password", "secret", "token")
- JWT tokens
- Credit card numbers
- Full medical diagnosis details (logged as resource_id only)

## Encryption Strategy

### Field-Level Encryption
- **Algorithm**: Fernet (AES-128-CBC + HMAC)
- **Key Storage**: Environment variable `AUDIT_LOG_ENCRYPTION_KEY`
- **Encrypted Fields**: request_body, response_body, changes
- **Key Rotation**: Manual process documented in ops runbook

### Encryption Flow
```
Plain Data → Fernet.encrypt() → Base64 → Database
Database → Base64 Decode → Fernet.decrypt() → Plain Data
```

## Performance Considerations

### Target Overhead: <50ms per request

### Strategies:
1. **Async Logging**: Use FastAPI BackgroundTasks
2. **Queue-Based**: Log writes happen after response
3. **Batch Writes**: Multiple logs committed together
4. **Connection Pooling**: Reuse DB connections
5. **Index Optimization**: Indexes on timestamp, user_id, action, resource_type

### Performance Monitoring
- Track log write duration
- Alert if >50ms threshold exceeded
- Monitor queue depth for backlogs

## Security Considerations

### Immutability
- No UPDATE operations on audit_logs table
- No DELETE operations (except retention cleanup)
- Application-level enforcement (middleware checks)

### Access Control
- RBAC: Only users with `audit:read` permission
- Admin-only: Only `admin` role can view logs
- No API access for regular users

### Retention Policy
- **Active**: 1 year in main table (audit_logs)
- **Archive**: Years 2-6 in archive table (audit_logs_archive)
- **Deletion**: Automatic cleanup after 6 years
- **Compliance**: UU 27/2022 (Indonesian data protection law)

## Alerting

### Sensitive Operation Triggers
1. **Data Export**: Any `/api/v1/export/*` endpoint
2. **Bulk Delete**: Operations affecting >100 records
3. **Permission Changes**: Role/permission modifications
4. **System Config**: Settings/environment changes
5. **Failed Auth**: 5+ failed login attempts from same IP

### Alert Delivery
- Real-time via WebSocket (admin dashboard)
- Email for critical alerts
- Stored in audit_alerts table
- Integrated with notification system

## API Design

### Query Endpoints
```
GET /api/v1/audit/logs
  Query params:
    - user_id: Optional[int]
    - action: Optional[str]
    - resource_type: Optional[str]
    - resource_id: Optional[str]
    - start_date: Optional[datetime]
    - end_date: Optional[datetime]
    - limit: int = 100
    - offset: int = 0

GET /api/v1/audit/logs/{id}
  Get single log entry by ID

GET /api/v1/audit/logs/stats
  Aggregate statistics

GET /api/v1/audit/logs/export
  Export to CSV/Excel (streaming)
```

### Admin-Only Access
All endpoints require `audit:read` permission
Only accessible to `admin`, `superuser` roles

## Database Schema

```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    user_id INTEGER REFERENCES users(id),
    username VARCHAR(100),
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_path VARCHAR(500),
    request_method VARCHAR(10),
    success BOOLEAN DEFAULT TRUE,
    failure_reason TEXT,
    request_body_encrypted TEXT,  -- Encrypted
    response_body_encrypted TEXT, -- Encrypted
    changes_encrypted TEXT,        -- Encrypted
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_success ON audit_logs(success);

-- Archive table (same structure)
CREATE TABLE audit_logs_archive (
    -- Same columns as audit_logs
);

-- Partitioning strategy (optional, for high volume)
-- Partition by year: audit_logs_2025, audit_logs_2026, etc.
```

## Implementation Tasks

1. ✅ Create encryption module (app/core/encryption.py)
2. ✅ Update audit log model with encrypted fields
3. ⏳ Create audit middleware (app/middleware/audit.py)
4. ⏳ Register middleware in FastAPI app
5. ⏳ Create audit log query endpoints (app/api/v1/endpoints/audit.py)
6. ⏳ Implement export functionality
7. ⏳ Create alert system for sensitive operations
8. ⏳ Implement retention cleanup job
9. ⏳ Create admin UI (frontend)
10. ⏳ Write tests

## Migration Plan

1. Add new encrypted fields to audit_logs table
2. Migrate existing data (encrypt additional_data)
3. Deploy new middleware
4. Monitor performance
5. Enable alerts after validation

## Rollback Plan

1. Disable middleware via feature flag
2. Continue logging via manual calls
3. Restore previous version if critical issues
