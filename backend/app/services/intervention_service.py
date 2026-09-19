import uuid
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.db.models import SessionModel, InterventionModel
from backend.app.schemas.schemas import InterventionCreate, InterventionResponse

logger = logging.getLogger("guardianai.intervention")

def record_intervention(db: Session, payload: InterventionCreate) -> InterventionResponse:
    """
    Records a user intervention event (warning displayed, transaction halted)
    and updates session outcome based on user response.
    """
    sess = db.query(SessionModel).filter(SessionModel.session_id == payload.session_id).first()
    if not sess:
        raise ValueError(f"Session '{payload.session_id}' not found")

    intervention_id = f"int_{uuid.uuid4().hex[:12]}"
    inv = InterventionModel(
        intervention_id=intervention_id,
        session_id=payload.session_id,
        timestamp=datetime.now(timezone.utc),
        risk_score=payload.risk_score,
        action=payload.action,
        user_response=payload.user_response
    )
    db.add(inv)

    if payload.user_response == "CANCEL_TRANSACTION":
        sess.final_outcome = "INTERRUPTED"
        logger.info("User halted transaction for session %s - outcome: INTERRUPTED", payload.session_id)
    elif payload.user_response == "TRUST_USER":
        sess.final_outcome = "ALLOWED"
        logger.info("User trusted transfer for session %s - outcome: ALLOWED", payload.session_id)

    db.commit()
    db.refresh(inv)

    return InterventionResponse(
        intervention_id=inv.intervention_id,
        session_id=inv.session_id,
        timestamp=inv.timestamp,
        risk_score=inv.risk_score,
        action=inv.action,
        user_response=inv.user_response
    )
