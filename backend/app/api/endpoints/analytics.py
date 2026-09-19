import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.schemas import AnalyticsResponse
from backend.app.services.analytics_service import get_analytics_summary

logger = logging.getLogger("guardianai.api.analytics")
router = APIRouter()

@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    summary="Retrieve cybersecurity monitoring analytics",
    description="Returns aggregated system telemetry, protected sessions count, prevented monetary losses, threat pattern frequencies, and risk score distributions."
)
def get_analytics(db: Session = Depends(get_db)):
    try:
        return get_analytics_summary(db)
    except Exception as exc:
        logger.error("Error retrieving analytics metrics: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while computing monitoring analytics."
        )
