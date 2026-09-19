import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.schemas import SessionResponse, SessionSummary
from backend.app.services.session_service import get_session_details, list_sessions as fetch_sessions

logger = logging.getLogger("guardianai.api.sessions")
router = APIRouter()

@router.get(
    "/session/{session_id}",
    response_model=SessionResponse,
    summary="Get full session details with events and interventions",
    description="Retrieves active session state, current risk score, final outcome, and full chronological timeline of events and interventions."
)
def get_session_by_id(session_id: str, db: Session = Depends(get_db)):
    sess_details = get_session_details(db, session_id)
    if not sess_details:
        logger.warning("Session lookup failed: '%s' not found", session_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )
    return sess_details

@router.get(
    "/sessions",
    response_model=List[SessionSummary],
    summary="List all recent sessions",
    description="Returns a list of recent monitored sessions along with event counts and risk levels."
)
def list_sessions(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of sessions to return"),
    db: Session = Depends(get_db)
):
    try:
        return fetch_sessions(db, limit=limit)
    except Exception as exc:
        logger.error("Failed to list sessions: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while listing monitored sessions."
        )
