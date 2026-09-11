from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health", summary="System Health Check")
def get_health():
    return {
        "status": "HEALTHY",
        "service": "GuardianAI Protection Engine",
        "version": "1.0.0-phase1",
        "active_telemetry": "BEHAVIOURAL_METADATA_ONLY",
        "timestamp": datetime.utcnow().isoformat(),
        "privacy_compliance": "NO_PII_STRICT"
    }
