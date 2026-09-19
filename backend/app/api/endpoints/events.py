import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.schemas import EventCreate, EventResponse
from backend.app.services.event_service import ingest_event, get_events as fetch_events

logger = logging.getLogger("guardianai.api.events")
router = APIRouter()

@router.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest behavioural telemetry event",
    description="Ingests a privacy-sanitized behavioural event, triggers feature extraction & risk scoring, updates session risk level, and returns the persisted event record."
)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    try:
        return ingest_event(db, payload)
    except ValueError as ve:
        logger.warning("Event validation error: %s", ve)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        logger.error("Failed to ingest event for session %s: %s", payload.session_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while processing behavioural event telemetry."
        )

@router.get(
    "/events",
    response_model=List[EventResponse],
    summary="Get chronological events list",
    description="Fetches a list of privacy-sanitized behavioural events in descending chronological order, optionally filtered by session_id."
)
def get_events(
    session_id: Optional[str] = Query(None, description="Filter events by active session ID"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of events to return"),
    db: Session = Depends(get_db)
):
    try:
        return fetch_events(db, session_id=session_id, limit=limit)
    except Exception as exc:
        logger.error("Failed to fetch events: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while retrieving event history."
        )
