from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import SessionModel, EventModel
from backend.app.schemas.schemas import RiskScoreRequest, RiskScoreResponse
from backend.app.services.risk_engine import evaluate_session_risk

router = APIRouter()

@router.post("/risk-score", response_model=RiskScoreResponse, summary="Compute or retrieve scam risk score")
def compute_risk_score(payload: RiskScoreRequest, db: Session = Depends(get_db)):
    events_data = []
    if payload.events:
        events_data = [{"event_type": e.event_type, "metadata": e.metadata} for e in payload.events]
    else:
        # Fetch from database
        db_events = db.query(EventModel).filter(EventModel.session_id == payload.session_id).order_by(EventModel.timestamp).all()
        events_data = [{"event_type": e.event_type, "metadata": e.event_metadata} for e in db_events]

    risk_evaluation = evaluate_session_risk(payload.session_id, events_data)

    # Sync with SessionModel if it exists
    sess = db.query(SessionModel).filter(SessionModel.session_id == payload.session_id).first()
    if sess:
        sess.risk_score = risk_evaluation.risk_score
        sess.risk_level = risk_evaluation.risk_level
        db.commit()

    return risk_evaluation
