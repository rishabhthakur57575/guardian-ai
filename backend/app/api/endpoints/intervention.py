import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.schemas import InterventionCreate, InterventionResponse
from backend.app.services.intervention_service import record_intervention as persist_intervention

logger = logging.getLogger("guardianai.api.intervention")
router = APIRouter()

@router.post(
    "/intervention",
    response_model=InterventionResponse,
    summary="Record user intervention action (Cancel or Trust)",
    description="Records a critical security intervention (warning modal shown, transaction halted) and updates session outcome based on user choice."
)
def record_intervention(payload: InterventionCreate, db: Session = Depends(get_db)):
    try:
        return persist_intervention(db, payload)
    except ValueError as ve:
        logger.warning("Intervention recording failed: %s", ve)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as exc:
        logger.error("Error recording intervention for session %s: %s", payload.session_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while recording intervention."
        )
