from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import SessionModel, EventModel, InterventionModel
from backend.app.schemas.schemas import SessionResponse, SessionSummary, EventResponse, InterventionResponse

router = APIRouter()

@router.get("/session/{session_id}", response_model=SessionResponse, summary="Get full session details with events and interventions")
def get_session_by_id(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    events = db.query(EventModel).filter(EventModel.session_id == session_id).order_by(EventModel.timestamp).all()
    interventions = db.query(InterventionModel).filter(InterventionModel.session_id == session_id).order_by(InterventionModel.timestamp).all()

    return SessionResponse(
        session_id=sess.session_id,
        start_time=sess.start_time,
        end_time=sess.end_time,
        risk_score=sess.risk_score,
        risk_level=sess.risk_level,
        final_outcome=sess.final_outcome,
        events=[
            EventResponse(
                event_id=e.event_id,
                session_id=e.session_id,
                timestamp=e.timestamp,
                event_type=e.event_type,
                metadata=e.event_metadata
            )
            for e in events
        ],
        interventions=[
            InterventionResponse(
                intervention_id=i.intervention_id,
                session_id=i.session_id,
                timestamp=i.timestamp,
                risk_score=i.risk_score,
                action=i.action,
                user_response=i.user_response
            )
            for i in interventions
        ]
    )

@router.get("/sessions", response_model=List[SessionSummary], summary="List all recent sessions")
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).order_by(SessionModel.start_time.desc()).limit(20).all()
    result = []
    for s in sessions:
        ev_count = db.query(EventModel).filter(EventModel.session_id == s.session_id).count()
        result.append(SessionSummary(
            session_id=s.session_id,
            start_time=s.start_time,
            end_time=s.end_time,
            risk_score=s.risk_score,
            risk_level=s.risk_level,
            final_outcome=s.final_outcome,
            event_count=ev_count
        ))
    return result
