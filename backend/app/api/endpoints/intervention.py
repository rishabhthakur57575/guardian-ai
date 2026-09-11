import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import SessionModel, InterventionModel
from backend.app.schemas.schemas import InterventionCreate, InterventionResponse

router = APIRouter()

@router.post("/intervention", response_model=InterventionResponse, summary="Record user intervention action (Cancel or Trust)")
def record_intervention(payload: InterventionCreate, db: Session = Depends(get_db)):
    sess = db.query(SessionModel).filter(SessionModel.session_id == payload.session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    intervention_id = f"int_{uuid.uuid4().hex[:12]}"
    inv = InterventionModel(
        intervention_id=intervention_id,
        session_id=payload.session_id,
        timestamp=datetime.utcnow(),
        risk_score=payload.risk_score,
        action=payload.action,
        user_response=payload.user_response
    )
    db.add(inv)

    if payload.user_response == "CANCEL_TRANSACTION":
        sess.final_outcome = "INTERRUPTED"
    elif payload.user_response == "TRUST_USER":
        sess.final_outcome = "ALLOWED"

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
