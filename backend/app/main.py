from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.api.router import api_router
from backend.app.services.simulator_service import seed_sample_historical_data

# Initialize DB tables
Base.metadata.create_all(bind=engine)

# Seed historical data
try:
    with SessionLocal() as db:
        seed_sample_historical_data(db)
except Exception as e:
    print(f"[GuardianAI DB Init] Warning during seeding: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Privacy-First Behavioural Monitoring Engine for Detecting Coached Financial Scams"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "GuardianAI Behavioral Threat Monitoring Engine Active",
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_STR
    }
