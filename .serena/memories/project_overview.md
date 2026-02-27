# SIMRS - Sistem Informasi Manajemen Rumah Sakit

## Purpose
Hospital Information Management System for Indonesian healthcare facilities with full BPJS and SATUSEHAT integration.

## Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Next.js 15 (React 19)
- **Database**: PostgreSQL 16 with pgcrypto
- **Cache**: Redis 7
- **Storage**: MinIO (S3-compatible)
- **Reverse Proxy**: Nginx with SSL/TLS
- **Containerization**: Docker Compose

## Key Features
- Electronic Medical Records (EMR)
- BPJS Integration (VClaim, Antrean, Aplicare, PCare)
- SATUSEHAT Integration (FHIR R4)
- Offline-First Architecture
- Mobile Responsive UI

## Compliance
- UU 27/2022 (Personal Data Protection)
- Permenkes 24/2022 (Electronic Medical Records)
- Permenkes 82/2013 (SIMRS Implementation)
- Permenkes 4/2024 (Hospital Service Standards)
