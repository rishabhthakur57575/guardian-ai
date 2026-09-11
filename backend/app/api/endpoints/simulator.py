from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import SessionModel, EventModel
from backend.app.services.simulator_service import advance_simulator_step, reset_simulator, SIMULATOR_STEPS

router = APIRouter()

@router.post("/simulator/step", summary="Advance simulation to the next staged behavioural event")
def trigger_simulator_step(
    session_id: str = Query("demo-session-live", description="Session to advance"),
    db: Session = Depends(get_db)
):
    return advance_simulator_step(db, session_id)

@router.post("/simulator/reset", summary="Reset simulation session back to clean SAFE state")
def trigger_simulator_reset(
    session_id: str = Query("demo-session-live", description="Session to reset"),
    db: Session = Depends(get_db)
):
    return reset_simulator(db, session_id)

@router.get("/simulator/state", summary="Get current simulator state and plan")
def get_simulator_state(
    session_id: str = Query("demo-session-live", description="Session ID"),
    db: Session = Depends(get_db)
):
    events = db.query(EventModel).filter(EventModel.session_id == session_id).order_by(EventModel.timestamp).all()
    return {
        "session_id": session_id,
        "current_step": len(events),
        "total_steps": len(SIMULATOR_STEPS),
        "steps_catalog": SIMULATOR_STEPS
    }
