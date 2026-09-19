import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import EventModel
from backend.app.schemas.schemas import RiskScoreRequest, RiskScoreResponse
from backend.app.services.session_service import update_session_risk, get_session_by_id
from backend.app.services.risk_engine import evaluate_session_risk

logger = logging.getLogger("guardianai.api.risk")
router = APIRouter()

@router.post(
    "/risk-score",
    response_model=RiskScoreResponse,
    summary="Compute or retrieve scam risk score",
    description="Evaluates fraud risk score and threat level for a session based either on the provided event sequence or stored historical events in SQLite."
)
def compute_risk_score(payload: RiskScoreRequest, db: Session = Depends(get_db)):
    try:
        events_data = []
        if payload.events:
            events_data = [{"event_type": e.event_type, "metadata": e.metadata} for e in payload.events]
        else:
            # Fetch chronological events from database
            db_events = (
                db.query(EventModel)
                .filter(EventModel.session_id == payload.session_id)
                .order_by(EventModel.timestamp)
                .all()
            )
            events_data = [
                {"event_type": e.event_type, "metadata": e.event_metadata, "timestamp": e.timestamp}
                for e in db_events
            ]

        risk_evaluation = evaluate_session_risk(payload.session_id, events_data)

        # Sync session model if session exists
        sess = get_session_by_id(db, payload.session_id)
        if sess:
            update_session_risk(db, payload.session_id, risk_evaluation.risk_score, risk_evaluation.risk_level)

        logger.info(
            "Computed risk score for session %s: %.1f (%s)",
            payload.session_id, risk_evaluation.risk_score, risk_evaluation.risk_level
        )

        return risk_evaluation

    except Exception as exc:
        logger.error("Error computing risk score for session %s: %s", payload.session_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while computing scam risk evaluation."
        )
