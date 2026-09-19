import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.db.models import SessionModel, EventModel, InterventionModel
from backend.app.schemas.schemas import SessionResponse, SessionSummary, EventResponse, InterventionResponse

logger = logging.getLogger("guardianai.sessions")

def get_or_create_session(db: Session, session_id: str) -> SessionModel:
    """Retrieves an existing session or creates a new active session."""
    sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not sess:
        sess = SessionModel(
            session_id=session_id,
            start_time=datetime.now(timezone.utc),
            risk_score=0.0,
            risk_level="SAFE",
            final_outcome="ACTIVE"
        )
        db.add(sess)
        db.commit()
        db.refresh(sess)
        logger.info("Created new session: %s", session_id)
    return sess

def get_session_by_id(db: Session, session_id: str) -> Optional[SessionModel]:
    """Retrieves a session by ID."""
    return db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

def get_session_details(db: Session, session_id: str) -> Optional[SessionResponse]:
    """Retrieves complete session details including events and interventions."""
    sess = get_session_by_id(db, session_id)
    if not sess:
        return None

    events = (
        db.query(EventModel)
        .filter(EventModel.session_id == session_id)
        .order_by(EventModel.timestamp)
        .all()
    )
    interventions = (
        db.query(InterventionModel)
        .filter(InterventionModel.session_id == session_id)
        .order_by(InterventionModel.timestamp)
        .all()
    )

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

def list_sessions(db: Session, limit: int = 20) -> List[SessionSummary]:
    """Lists recent sessions ordered by start time descending."""
    sessions = (
        db.query(SessionModel)
        .order_by(SessionModel.start_time.desc())
        .limit(limit)
        .all()
    )
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

def update_session_risk(db: Session, session_id: str, risk_score: float, risk_level: str) -> Optional[SessionModel]:
    """Updates the calculated risk score and level of an active session."""
    sess = get_session_by_id(db, session_id)
    if sess:
        sess.risk_score = risk_score
        sess.risk_level = risk_level
        db.commit()
        db.refresh(sess)
    return sess

def update_session_outcome(db: Session, session_id: str, outcome: str) -> Optional[SessionModel]:
    """Updates the final outcome of a session."""
    sess = get_session_by_id(db, session_id)
    if sess:
        sess.final_outcome = outcome
        db.commit()
        db.refresh(sess)
        logger.info("Session %s outcome updated to %s", session_id, outcome)
    return sess
