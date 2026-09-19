import uuid
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.db.models import EventModel
from backend.app.schemas.schemas import EventCreate, EventResponse, RiskScoreResponse
from backend.app.services.session_service import get_or_create_session, update_session_risk
from backend.app.services.feature_service import extract_features
from backend.app.services.risk_engine import predict_risk

logger = logging.getLogger("guardianai.events")

def ingest_event(db: Session, payload: EventCreate) -> EventResponse:
    """
    Ingests a single behavioural event into the pipeline:
    1. Ensures session existence in SQLite.
    2. Persists event telemetry.
    3. Runs feature extraction across session event history.
    4. Evaluates risk via modular risk engine.
    5. Syncs calculated risk score and level back to session.
    """
    sess = get_or_create_session(db, payload.session_id)

    event_id = f"ev_{uuid.uuid4().hex[:12]}"
    ev_timestamp = payload.timestamp or datetime.now(timezone.utc)

    db_event = EventModel(
        event_id=event_id,
        session_id=payload.session_id,
        timestamp=ev_timestamp,
        event_type=payload.event_type,
        metadata_json=json.dumps(payload.metadata)
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Fetch chronological history for this session
    all_events = (
        db.query(EventModel)
        .filter(EventModel.session_id == payload.session_id)
        .order_by(EventModel.timestamp)
        .all()
    )

    events_data = [
        {
            "event_type": e.event_type,
            "metadata": e.event_metadata,
            "timestamp": e.timestamp
        }
        for e in all_events
    ]

    # Pipeline Step 1: Feature Extraction
    features = extract_features(events_data)

    # Pipeline Step 2: Risk Scoring
    risk_evaluation: RiskScoreResponse = predict_risk(features, session_id=payload.session_id)

    # Pipeline Step 3: SQLite Session Sync
    old_risk_level = sess.risk_level
    update_session_risk(db, payload.session_id, risk_evaluation.risk_score, risk_evaluation.risk_level)

    if old_risk_level != risk_evaluation.risk_level:
        logger.warning(
            "Session %s risk transition: %s -> %s (Score: %.1f)",
            payload.session_id, old_risk_level, risk_evaluation.risk_level, risk_evaluation.risk_score
        )
    else:
        logger.info(
            "Event %s ingested for session %s (Type: %s, Current Score: %.1f)",
            event_id, payload.session_id, payload.event_type, risk_evaluation.risk_score
        )

    return EventResponse(
        event_id=db_event.event_id,
        session_id=db_event.session_id,
        timestamp=db_event.timestamp,
        event_type=db_event.event_type,
        metadata=db_event.event_metadata
    )

def get_events(db: Session, session_id: Optional[str] = None, limit: int = 50) -> List[EventResponse]:
    """Retrieves chronological events, optionally filtered by session ID."""
    query = db.query(EventModel)
    if session_id:
        query = query.filter(EventModel.session_id == session_id)
    events = query.order_by(EventModel.timestamp.desc()).limit(limit).all()

    return [
        EventResponse(
            event_id=e.event_id,
            session_id=e.session_id,
            timestamp=e.timestamp,
            event_type=e.event_type,
            metadata=e.event_metadata
        )
        for e in events
    ]
