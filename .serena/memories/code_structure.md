# Code Structure

## Backend Structure (backend/)
```
backend/
├── app/
│   ├── api/v1/endpoints/   # API endpoints (100+ endpoints)
│   ├── core/               # Configuration & security
│   ├── db/                 # Database session & models
│   ├── models/             # SQLAlchemy models (50+ models)
│   ├── schemas/            # Pydantic schemas
│   ├── crud/               # Database operations
│   ├── services/           # Business logic services
│   ├── middleware/         # Request middleware
│   └── main.py             # FastAPI app entry point
├── tests/                  # Test files
├── alembic/               # Database migrations
└── scripts/               # Utility scripts
```

## Frontend Structure (frontend/src/)
```
frontend/src/
├── app/                   # Next.js 15 App Router pages
│   ├── demo/
│   ├── patients/
│   ├── portal/
│   ├── app/
│   ├── appointments/
│   └── admin/
├── components/            # React components
│   ├── ui/               # UI primitives
│   ├── patients/         # Patient components
│   ├── pharmacy/         # Pharmacy components
│   ├── billing/          # Billing components
│   ├── bpjs/             # BPJS integration
│   └── [20+ more dirs]
├── hooks/                 # Custom React hooks
├── lib/                   # Utilities
├── types/                 # TypeScript types
└── constants/             # Constants
```

## Key Models
- Patient, User, Permission, Hospital
- BPJS: Claims, SEP, Antrean, Eligibility
- Clinical: Encounter, ClinicalNote, Allergy, ProblemList
- Pharmacy: Medication, Prescription, Dispensing, Inventory
- Orders: LabOrders, RadiologyOrders
- Billing: Billing, Payments
- Integration: FHIR, HL7, LIS, PACS
