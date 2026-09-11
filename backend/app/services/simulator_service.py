import uuid
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.db.models import SessionModel, EventModel, InterventionModel
from backend.app.services.risk_engine import evaluate_session_risk

SIMULATOR_STEPS = [
    {
        "step_index": 1,
        "event_type": "SCREEN_SHARING_STARTED",
        "description": "Screen sharing started",
        "metadata": {
            "tool_name": "AnyDesk Remote Support",
            "remote_host": "External Remote Client (Caller ID: Support-Desk)",
            "screen_sharing_active": True,
            "display_resolution": "1080x2400",
            "frame_rate_fps": 30
        }
    },
    {
        "step_index": 2,
        "event_type": "BANKING_APP_FOREGROUNDED",
        "description": "Banking app opened",
        "metadata": {
            "app_name": "HDFC Mobile Banking",
            "package_name": "com.snapwork.hdfc",
            "banking_app_active": True,
            "session_time_seconds": 12,
            "auth_method": "Biometric (Device-Local)"
        }
    },
    {
        "step_index": 3,
        "event_type": "NEW_BENEFICIARY_ADDED",
        "description": "New beneficiary added",
        "metadata": {
            "beneficiary_label": "Fast_Reversal_Desk_94",
            "creation_speed_ms": 3200,
            "paste_event_detected": True,
            "new_beneficiary": True
        }
    },
    {
        "step_index": 4,
        "event_type": "HIGH_VALUE_TRANSACTION_INITIATED",
        "description": "Large transaction initiated",
        "metadata": {
            "transaction_amount": 185000.0,
            "currency": "INR",
            "payment_rail": "IMPS_INSTANT",
            "target_nickname": "Fast_Reversal_Desk_94"
        }
    },
    {
        "step_index": 5,
        "event_type": "COACHED_BEHAVIOUR_TRIGGERED",
        "description": "Suspicious behaviour detected",
        "metadata": {
            "coached_sequence_detected": True,
            "pattern_signature": "REMOTE_COACHED_FINANCIAL_EXFILTRATION",
            "touch_cadence_variance_score": 0.88,
            "rapid_app_switch": True
        }
    },
    {
        "step_index": 6,
        "event_type": "INTERVENTION_TRIGGERED",
        "description": "Intervention triggered",
        "metadata": {
            "halt_transaction": True,
            "intervention_type": "HIGH_PRIORITY_ELDERLY_SAFE_MODAL",
            "urgency": "CRITICAL"
        }
    }
]

def get_or_create_active_session(db: Session, session_id: str = "demo-session-live") -> SessionModel:
    sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
    if not sess:
        sess = SessionModel(
            session_id=session_id,
            start_time=datetime.utcnow(),
            risk_score=0.0,
            risk_level="SAFE",
            final_outcome="ACTIVE"
        )
        db.add(sess)
        db.commit()
        db.refresh(sess)
    return sess

def advance_simulator_step(db: Session, session_id: str = "demo-session-live") -> dict:
    sess = get_or_create_active_session(db, session_id)
    existing_events = db.query(EventModel).filter(EventModel.session_id == session_id).order_by(EventModel.timestamp).all()
    current_step_count = len(existing_events)

    if current_step_count >= len(SIMULATOR_STEPS):
        # Already at max step, return current state
        risk_res = evaluate_session_risk(session_id, [{"event_type": e.event_type, "metadata": e.event_metadata} for e in existing_events])
        return {
            "status": "COMPLETED",
            "message": "Simulator reached final stage.",
            "current_step": current_step_count,
            "total_steps": len(SIMULATOR_STEPS),
            "risk": risk_res.model_dump()
        }

    next_step_data = SIMULATOR_STEPS[current_step_count]
    new_event = EventModel(
        event_id=f"ev_{uuid.uuid4().hex[:12]}",
        session_id=session_id,
        timestamp=datetime.utcnow(),
        event_type=next_step_data["event_type"],
        metadata_json=json.dumps(next_step_data["metadata"])
    )
    db.add(new_event)
    db.commit()

    # Re-evaluate all events for updated risk
    all_events = db.query(EventModel).filter(EventModel.session_id == session_id).order_by(EventModel.timestamp).all()
    events_payload = [{"event_type": e.event_type, "metadata": e.event_metadata} for e in all_events]
    risk_evaluation = evaluate_session_risk(session_id, events_payload)

    # Update session model
    sess.risk_score = risk_evaluation.risk_score
    sess.risk_level = risk_evaluation.risk_level

    # If step 6 reached, create intervention record
    if next_step_data["step_index"] == 6:
        intervention = InterventionModel(
            intervention_id=f"int_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            timestamp=datetime.utcnow(),
            risk_score=risk_evaluation.risk_score,
            action="TRANSACTION_HALTED",
            user_response="PENDING"
        )
        db.add(intervention)
        sess.final_outcome = "INTERRUPTED"

    db.commit()
    db.refresh(sess)

    return {
        "status": "STEP_ADVANCED",
        "current_step": current_step_count + 1,
        "total_steps": len(SIMULATOR_STEPS),
        "step_name": next_step_data["description"],
        "event_type": next_step_data["event_type"],
        "risk": risk_evaluation.model_dump()
    }

def reset_simulator(db: Session, session_id: str = "demo-session-live") -> dict:
    # Remove existing events and interventions for this session
    db.query(InterventionModel).filter(InterventionModel.session_id == session_id).delete()
    db.query(EventModel).filter(EventModel.session_id == session_id).delete()
    db.query(SessionModel).filter(SessionModel.session_id == session_id).delete()
    db.commit()

    # Recreate fresh session
    new_sess = SessionModel(
        session_id=session_id,
        start_time=datetime.utcnow(),
        risk_score=0.0,
        risk_level="SAFE",
        final_outcome="ACTIVE"
    )
    db.add(new_sess)
    db.commit()

    return {
        "status": "RESET_SUCCESSFUL",
        "session_id": session_id,
        "message": "Demo session reset to initial clean SAFE state."
    }

def seed_sample_historical_data(db: Session):
    # Check if sessions exist already
    count = db.query(SessionModel).count()
    if count > 1:
        return

    now = datetime.utcnow()
    sample_sessions = [
        {
            "session_id": "hist-sess-01",
            "start_time": now - timedelta(hours=3, minutes=15),
            "end_time": now - timedelta(hours=3, minutes=10),
            "risk_score": 94.0,
            "risk_level": "THREAT_DETECTED",
            "final_outcome": "INTERRUPTED",
            "events": [
                ("SCREEN_SHARING_STARTED", {"tool_name": "TeamViewer", "screen_sharing_active": True}, now - timedelta(hours=3, minutes=15)),
                ("BANKING_APP_FOREGROUNDED", {"app_name": "SBI YONO", "banking_app_active": True}, now - timedelta(hours=3, minutes=14)),
                ("NEW_BENEFICIARY_ADDED", {"beneficiary_label": "Kyc_Verification_Agent", "new_beneficiary": True}, now - timedelta(hours=3, minutes=13)),
                ("HIGH_VALUE_TRANSACTION_INITIATED", {"transaction_amount": 95000.0, "currency": "INR"}, now - timedelta(hours=3, minutes=12)),
                ("COACHED_BEHAVIOUR_TRIGGERED", {"coached_sequence_detected": True}, now - timedelta(hours=3, minutes=11))
            ],
            "intervention": {
                "risk_score": 94.0,
                "action": "TRANSACTION_HALTED",
                "user_response": "CANCEL_TRANSACTION"
            }
        },
        {
            "session_id": "hist-sess-02",
            "start_time": now - timedelta(hours=6, minutes=45),
            "end_time": now - timedelta(hours=6, minutes=30),
            "risk_score": 12.0,
            "risk_level": "SAFE",
            "final_outcome": "ALLOWED",
            "events": [
                ("BANKING_APP_FOREGROUNDED", {"app_name": "ICICI iMobile", "banking_app_active": True}, now - timedelta(hours=6, minutes=45)),
                ("HIGH_VALUE_TRANSACTION_INITIATED", {"transaction_amount": 4200.0, "currency": "INR"}, now - timedelta(hours=6, minutes=40))
            ],
            "intervention": None
        },
        {
            "session_id": "hist-sess-03",
            "start_time": now - timedelta(hours=10, minutes=20),
            "end_time": now - timedelta(hours=10, minutes=12),
            "risk_score": 88.0,
            "risk_level": "THREAT_DETECTED",
            "final_outcome": "INTERRUPTED",
            "events": [
                ("SCREEN_SHARING_STARTED", {"tool_name": "AnyDesk Remote", "screen_sharing_active": True}, now - timedelta(hours=10, minutes=20)),
                ("BANKING_APP_FOREGROUNDED", {"app_name": "Axis Mobile", "banking_app_active": True}, now - timedelta(hours=10, minutes=18)),
                ("NEW_BENEFICIARY_ADDED", {"beneficiary_label": "Electricity_Refund_Office", "new_beneficiary": True}, now - timedelta(hours=10, minutes=16)),
                ("HIGH_VALUE_TRANSACTION_INITIATED", {"transaction_amount": 145000.0, "currency": "INR"}, now - timedelta(hours=10, minutes=14))
            ],
            "intervention": {
                "risk_score": 88.0,
                "action": "TRANSACTION_HALTED",
                "user_response": "CANCEL_TRANSACTION"
            }
        }
    ]

    for s_data in sample_sessions:
        if db.query(SessionModel).filter(SessionModel.session_id == s_data["session_id"]).first():
            continue
        sess = SessionModel(
            session_id=s_data["session_id"],
            start_time=s_data["start_time"],
            end_time=s_data["end_time"],
            risk_score=s_data["risk_score"],
            risk_level=s_data["risk_level"],
            final_outcome=s_data["final_outcome"]
        )
        db.add(sess)
        for etype, meta, ts in s_data["events"]:
            ev = EventModel(
                event_id=f"ev_{uuid.uuid4().hex[:12]}",
                session_id=s_data["session_id"],
                timestamp=ts,
                event_type=etype,
                metadata_json=json.dumps(meta)
            )
            db.add(ev)
        if s_data["intervention"]:
            inv = InterventionModel(
                intervention_id=f"int_{uuid.uuid4().hex[:12]}",
                session_id=s_data["session_id"],
                timestamp=s_data["end_time"] or now,
                risk_score=s_data["intervention"]["risk_score"],
                action=s_data["intervention"]["action"],
                user_response=s_data["intervention"]["user_response"]
            )
            db.add(inv)

    db.commit()
