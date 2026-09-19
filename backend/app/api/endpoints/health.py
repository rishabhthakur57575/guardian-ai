from datetime import datetime, timezone
from fastapi import APIRouter
from backend.app.core.config import settings

router = APIRouter()

@router.get(
    "/health",
    summary="System Health Check",
    description="Returns backend sentinel health, privacy compliance assertion, and version metadata."
)
def get_health():
    return {
        "status": "HEALTHY",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "active_telemetry": "BEHAVIOURAL_METADATA_ONLY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "privacy_compliance": "NO_PII_STRICT"
    }
