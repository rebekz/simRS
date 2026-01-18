from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

from app.core.config import settings
from app.core.metrics import initialize_metrics
from app.api.v1.api import api_router
from app.db.session import engine
from app.db.base_class import Base

# Import all models to ensure they are registered with SQLAlchemy
# This must be done before metadata.create_all is called
from app.models import user, session, permission, audit_log, password_reset
from app.models import patient, encounter, appointments, admission
from app.models import lab_orders, lis_integration, radiology_orders
from app.models import prescription, dispensing, medication, inventory
from app.models import billing, discharge, queue, bed
from app.models import reporting, analytics
from app.models import bpjs_antrean, bpjs_claims, bpjs_sep, bpjs_eligibility
from app.models import daily_care, pharmacy_integration
from app.models import clinical_note, allergy, problem_list
from app.models import emr_integration, fhir, hl7
from app.models import pacs_integration, device_integration, integration_monitoring
from app.models import notifications, patient_portal, patient_portal_messaging
from app.models import backup, master_data, procedure_codes, icd10
from app.models import system_monitoring, system_alerts
from app.models import transformation, user_management

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: {settings.VERSION}")

    # Initialize Prometheus metrics
    try:
        initialize_metrics()
        logger.info("Prometheus metrics initialized")
    except Exception as e:
        logger.error(f"Error initializing metrics: {e}")

    # Create database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

    yield

    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Prometheus metrics
from app.middleware.metrics import setup_metrics
setup_metrics(app)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "SIMRS API",
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint for nginx
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
