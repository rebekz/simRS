# SIMRS - Sistem Informasi Manajemen Rumah Sakit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)

Sistem Informasi Manajemen Rumah Sakit (Hospital Information Management System) designed for Indonesian healthcare facilities with full BPJS and SATUSEHAT integration.

## Features

- **Electronic Medical Records (Rekam Medis Elektronik)** - Compliant with Permenkes 24/2022
- **BPJS Integration** - VClaim, Antrean, Aplicare, and PCare APIs
- **SATUSEHAT Integration** - FHIR R4 compliant data exchange
- **Offline-First Architecture** - Works without internet connection
- **Modern UI/UX** - Built with Next.js 15 and React 19
- **Security** - UU 27/2022 compliant data protection
- **Mobile Responsive** - Works on tablets and smartphones

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 15 (React 19)
- **Database**: PostgreSQL 16 with pgcrypto
- **Cache**: Redis 7
- **Storage**: MinIO (S3-compatible)
- **Reverse Proxy**: Nginx with SSL/TLS
- **Containerization**: Docker Compose

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

## Quick Start

### One-Command Installation

```bash
./install.sh
```

The installation script will:
- Check prerequisites
- Create `.env` configuration
- Generate SSL certificates
- Build and start all services
- Run database migrations
- Prompt for admin user creation

### Access the Application

After installation:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **HTTPS**: https://localhost (self-signed)

## Documentation

- [Deployment Guide](docs/DEPLOYMENT.md) - Detailed deployment instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Product Requirements](docs/PRD.md) - Complete PRD
- [Architecture](docs/ARCHITECTURE.md) - System architecture
- [Epics & Stories](docs/EPICS.md) - Development roadmap

## Project Structure

```
simrs/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration & security
│   │   ├── db/             # Database session & models
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── crud/           # Database operations
│   ├── alembic/            # Database migrations
│   └── scripts/            # Utility scripts
├── frontend/               # Next.js frontend
│   └── src/
│       ├── app/            # App router pages
│       ├── components/     # React components
│       └── lib/            # Utilities
├── nginx/                  # Reverse proxy config
├── scripts/                # Installation scripts
├── docs/                   # Documentation
└── docker-compose.yml      # Service orchestration
```

## Development

### Start Services

```bash
docker compose up -d
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
```

### Run Migrations

```bash
docker compose exec backend alembic upgrade head
```

### Create Admin User

```bash
docker compose exec backend python scripts/create_admin.py
```

### Stop Services

```bash
docker compose down
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 3000 | Next.js web app |
| backend | 8000 | FastAPI REST API |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |
| minio | 9000 | Object storage |
| minio-console | 9001 | MinIO web UI |
| nginx | 80, 443 | Reverse proxy |

## Compliance

This system is designed to comply with:

- **UU 27/2022** - Perlindungan Data Pribadi (Personal Data Protection)
- **Permenkes 24/2022** - Rekam Medis Elektronik (Electronic Medical Records)
- **Permenkes 82/2013** - SIMRS Implementation Mandate
- **Permenkes 4/2024** - Standar Pelayanan Rumah Sakit

## Security

- JWT authentication with refresh tokens
- Role-based access control (RBAC)
- MFA support for remote access
- TLS 1.3 encryption
- Audit logging
- Password policies

## BPJS Integration

- VClaim API (SEP, Rencana Kontrol, Status Claim)
- Antrean API (Online queue management)
- Aplicare API (Bed availability)
- PCare API (Puskesmas integration)

## SATUSEHAT Integration

- FHIR R4 resources
- Patient data exchange
- Observation data
- Condition data
- Medication administration

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [API docs](http://localhost:8000/docs)

## Acknowledgments

- Kementerian Kesehatan RI for BPJS and SATUSEHAT standards
- The FastAPI and Next.js communities
- Open source contributors

---

**SIMRS** - Modern Healthcare Management for Indonesia 🇮🇩
