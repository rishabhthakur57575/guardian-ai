import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import SessionModel, EventModel
from backend.app.schemas.schemas import EventCreate, EventResponse
from backend.app.services.risk_engine import evaluate_session_risk

router = APIRouter()

@router.post("/events", response_model=EventResponse, summary="Ingest device behavioural telemetry event")
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    # Verify or create session
    sess = db.query(SessionModel).filter(SessionModel.session_id == payload.session_id).first()
    if not sess:
        sess = SessionModel(
            session_id=payload.session_id,
            start_time=datetime.utcnow(),
            risk_score=0.0,
            risk_level="SAFE",
            final_outcome="ACTIVE"
        )
        db.add(sess)
        db.commit()
        db.refresh(sess)

    event_id = f"ev_{uuid.uuid4().hex[:12]}"
    ev_timestamp = payload.timestamp or datetime.utcnow()

    db_event = EventModel(
        event_id=event_id,
        session_id=payload.session_id,
        timestamp=ev_timestamp,
        event_type=payload.event_type,
        metadata_json=json.dumps(payload.metadata)
    )
    db.add(db_event)
    db.commit()

    # Recalculate session risk
    all_events = db.query(EventModel).filter(EventModel.session_id == payload.session_id).all()
    events_data = [{"event_type": e.event_type, "metadata": e.event_metadata} for e in all_events]
    risk_evaluation = evaluate_session_risk(payload.session_id, events_data)

    sess.risk_score = risk_evaluation.risk_score
    sess.risk_level = risk_evaluation.risk_level
    db.commit()

    return EventResponse(
        event_id=db_event.event_id,
        session_id=db_event.session_id,
        timestamp=db_event.timestamp,
        event_type=db_event.event_type,
        metadata=db_event.event_metadata
    )

@router.get("/events", response_model=List[EventResponse], summary="Get chronological events list")
def get_events(
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
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
