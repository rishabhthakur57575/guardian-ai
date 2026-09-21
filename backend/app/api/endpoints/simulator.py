import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import EventModel
from typing import Optional
from backend.app.services.simulator_service import (
    advance_simulator_step, 
    reset_simulator, 
    SIMULATOR_STEPS,
    SCENARIOS,
    get_simulator_scenarios
)

logger = logging.getLogger("guardianai.api.simulator")
router = APIRouter()

@router.get(
    "/simulator/scenarios",
    summary="Get catalog of available test scenarios",
    description="Returns metadata for the 5 distinct simulation scenarios available for execution."
)
def list_simulator_scenarios():
    return get_simulator_scenarios()

@router.post(
    "/simulator/step",
    summary="Advance simulation to the next staged behavioural event",
    description="Advances the live threat simulation by injecting the next scripted behavioural event into the pipeline."
)
def trigger_simulator_step(
    session_id: str = Query("demo-session-live", description="Session ID to advance"),
    scenario_id: Optional[str] = Query(None, description="Scenario ID (e.g. coached_scam, family_assistance, legit_high_value, rapid_banking, scam_cancellation)"),
    db: Session = Depends(get_db)
):
    try:
        return advance_simulator_step(db, session_id, scenario_id=scenario_id)
    except Exception as exc:
        logger.error("Error advancing simulator step for session %s: %s", session_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while advancing simulation step."
        )

@router.post(
    "/simulator/reset",
    summary="Reset simulation session back to clean SAFE state",
    description="Clears all events and interventions for the target demo session, restoring it to a clean SAFE baseline."
)
def trigger_simulator_reset(
    session_id: str = Query("demo-session-live", description="Session ID to reset"),
    scenario_id: Optional[str] = Query(None, description="Scenario ID to reset"),
    db: Session = Depends(get_db)
):
    try:
        return reset_simulator(db, session_id, scenario_id=scenario_id)
    except Exception as exc:
        logger.error("Error resetting simulator session %s: %s", session_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while resetting simulation session."
        )

@router.get(
    "/simulator/state",
    summary="Get current simulator state and plan",
    description="Returns the current progression step and remaining steps in the scripted scam scenario."
)
def get_simulator_state(
    session_id: str = Query("demo-session-live", description="Session ID to inspect"),
    scenario_id: Optional[str] = Query(None, description="Scenario ID to inspect"),
    db: Session = Depends(get_db)
):
    try:
        events = (
            db.query(EventModel)
            .filter(EventModel.session_id == session_id)
            .order_by(EventModel.timestamp)
            .all()
        )
        sc_key = scenario_id if (scenario_id and scenario_id in SCENARIOS) else "coached_scam"
        scenario = SCENARIOS[sc_key]
        return {
            "session_id": session_id,
            "scenario_id": sc_key,
            "scenario_name": scenario["name"],
            "current_step": len(events),
            "total_steps": len(scenario["steps"]),
            "steps_catalog": scenario["steps"],
            "scenarios": get_simulator_scenarios()
        }
    except Exception as exc:
        logger.error("Error fetching simulator state for session %s: %s", session_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while retrieving simulation state."
        )
