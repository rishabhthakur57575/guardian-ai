import logging
import sys
from datetime import datetime, timezone
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.api.router import api_router
from backend.app.services.simulator_service import seed_sample_historical_data

# Configure structured application logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("guardianai.main")

# Initialize DB tables
Base.metadata.create_all(bind=engine)

# Seed historical data on startup
try:
    with SessionLocal() as db:
        seed_sample_historical_data(db)
except Exception as e:
    logger.warning("DB initialization warning during seeding: %s", e)

openapi_tags = [
    {"name": "Health", "description": "Sentinel engine status and privacy compliance check."},
    {"name": "Events", "description": "Ingest device behavioural events and query chronological telemetry."},
    {"name": "Risk Scoring", "description": "Real-time scam risk inference and threat factor breakdown."},
    {"name": "Sessions", "description": "Monitored user sessions and comprehensive security timelines."},
    {"name": "Interventions", "description": "Security intervention triggers and user decision recording."},
    {"name": "Analytics", "description": "Cybersecurity telemetry aggregation and threat pattern trends."},
    {"name": "Simulator", "description": "Interactive multi-step scam attack simulator."},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Privacy-First Behavioural Monitoring Engine for Detecting Coached Financial Scams",
    openapi_tags=openapi_tags
)

# CORS configuration for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning("HTTP %d error on %s: %s", exc.status_code, request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": f"HTTP_{exc.status_code}"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation failure on %s: %s", request.url.path, exc.errors())
    status_code = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY)
    return JSONResponse(
        status_code=status_code,
        content={"detail": jsonable_encoder(exc.errors()), "error_code": "VALIDATION_ERROR"}
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception on %s: %s", request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred.", "error_code": "INTERNAL_SERVER_ERROR"}
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", summary="Root Endpoint")
def root():
    return {
        "message": "GuardianAI Behavioral Threat Monitoring Engine Active",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_prefix": settings.API_V1_STR,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
