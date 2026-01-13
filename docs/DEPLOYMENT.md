# SIMRS Deployment Guide

## Overview

This guide covers deploying SIMRS (Sistem Informasi Manajemen Rumah Sakit) using Docker Compose. SIMRS is designed for one-command deployment with automatic configuration.

## Prerequisites

- **Docker** 20.10+ installed
- **Docker Compose** 2.0+ installed
- **Ports available**: 80, 443, 3000, 8000, 5432, 6379, 9000, 9001
- **Minimum resources**: 4GB RAM, 20GB disk space

## Quick Start

### 1. Clone and Install

```bash
# Navigate to project directory
cd simrs

# Run the installation script
./install.sh
```

The installation script will:
- Check prerequisites (Docker, Docker Compose)
- Create `.env` file from `.env.example`
- Generate self-signed SSL certificates
- Pull and build Docker images
- Start all services
- Run database migrations
- Prompt for admin user creation

### 2. Create Admin User

During installation, you'll be prompted to create an admin user. You can also create one later:

```bash
docker compose exec backend python scripts/create_admin.py
```

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **HTTPS (self-signed)**: https://localhost

## Manual Installation

If you prefer manual installation:

### 1. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

**Critical security settings**:
- `SECRET_KEY`: Generate a strong 32+ character random string
- `POSTGRES_PASSWORD`: Set a strong database password
- `REDIS_PASSWORD`: Set a strong Redis password
- `MINIO_ROOT_PASSWORD`: Set a strong MinIO password

### 2. Generate SSL Certificates

**Development (self-signed)**:
```bash
./scripts/generate-ssl.sh
```

**Production (Let's Encrypt)**:
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

# Set permissions
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem
```

### 3. Start Services

```bash
# Build and start
docker compose up -d --build

# Run migrations
docker compose exec backend alembic upgrade head

# Create admin user
docker compose exec backend python scripts/create_admin.py
```

## Services

The following services are started:

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | Next.js web application |
| backend | 8000 | FastAPI REST API |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache and session store |
| minio | 9000 | Object storage (S3-compatible) |
| minio-console | 9001 | MinIO web console |
| nginx | 80, 443 | Reverse proxy and SSL termination |

## Health Checks

Check service status:

```bash
# Check all services
docker compose ps

# Check backend health
curl http://localhost:8000/api/v1/health/

# Check detailed health
curl http://localhost:8000/api/v1/health/detailed

# Check nginx
curl http://localhost/health
```

## Logs

View logs for debugging:

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres

# Last 100 lines
docker compose logs --tail=100 backend
```

## Maintenance

### Restart Services

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart backend
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose up -d --build

# Run migrations
docker compose exec backend alembic upgrade head
```

### Backup

**Database backup**:
```bash
# Backup
docker compose exec postgres pg_dump -U simrs simrs > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U simrs simrs < backup_20240113.sql
```

**Volume backup**:
```bash
# Backup volumes
docker run --rm -v simrs_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .

docker run --rm -v simrs_redis_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

### Clean Up

```bash
# Stop services
docker compose down

# Remove volumes (WARNING: deletes data!)
docker compose down -v

# Clean up unused images
docker image prune -a
```

## Production Deployment

### Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate strong `SECRET_KEY` (32+ characters)
- [ ] Use proper SSL certificates (Let's Encrypt)
- [ ] Enable firewall (only allow 80, 443)
- [ ] Set up regular backups
- [ ] Configure log rotation
- [ ] Enable rate limiting (configured in nginx)
- [ ] Review and update CORS settings
- [ ] Configure BPJS credentials (if using)
- [ ] Configure SATUSEHAT credentials (if using)

### Performance Tuning

**PostgreSQL**:
```ini
# Add to postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
max_connections = 100
```

**Redis**:
```bash
# Add to redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

**Nginx**:
```nginx
# Add to nginx.conf
worker_processes auto;
worker_connections 2048;
```

### Monitoring

Consider setting up:
- **Prometheus + Grafana** for metrics
- **ELK Stack** for log aggregation
- **Uptime monitoring** (e.g., UptimeRobot)
- **Database monitoring** (pgAdmin)

## Troubleshooting

### Services won't start

```bash
# Check port conflicts
netstat -tulpn | grep -E ':(3000|8000|5432|6379|9000|9001|80|443)'

# Check logs
docker compose logs

# Remove volumes and start fresh
docker compose down -v
docker compose up -d
```

### Database connection errors

```bash
# Check if postgres is healthy
docker compose ps postgres

# Restart postgres
docker compose restart postgres

# Check logs
docker compose logs postgres
```

### SSL certificate errors

```bash
# Regenerate certificates
./scripts/generate-ssl.sh

# Restart nginx
docker compose restart nginx
```

### Migration errors

```bash
# Check current migration status
docker compose exec backend alembic current

# Force migration to specific version
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"
```

## Rollback Procedures

### Application Rollback

```bash
# List previous versions
git log --oneline -10

# Checkout previous version
git checkout <previous-commit-hash>

# Rebuild
docker compose up -d --build
```

### Database Rollback

```bash
# Check migrations
docker compose exec backend alembic history

# Rollback to specific migration
docker compose exec backend alembic downgrade <revision-hash>
```

## Support

For issues and questions:
- Check logs: `docker compose logs -f`
- Review health checks: `curl http://localhost:8000/api/v1/health/detailed`
- Check service status: `docker compose ps`

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
