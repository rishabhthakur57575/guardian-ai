import uuid
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.db.models import SessionModel, EventModel, InterventionModel
from backend.app.services.session_service import get_or_create_session, update_session_risk
from backend.app.services.risk_engine import evaluate_session_risk

logger = logging.getLogger("guardianai.simulator")

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

SCENARIOS: Dict[str, Dict[str, Any]] = {
    "coached_scam": {
        "id": "coached_scam",
        "name": "Coached Remote-Support Scam",
        "category": "HIGH RISK THREAT",
        "description": "Unverified remote screen share, banking login, rapid beneficiary creation, and guided transfer.",
        "expected_risk": "THREAT_DETECTED",
        "steps": SIMULATOR_STEPS
    },
    "family_assistance": {
        "id": "family_assistance",
        "name": "Legitimate Family Remote Assistance",
        "category": "SAFE / VERIFIED",
        "description": "Screen sharing with verified caregiver/family member for routine utility assistance.",
        "expected_risk": "SAFE",
        "steps": [
            {
                "step_index": 1,
                "event_type": "SCREEN_SHARING_STARTED",
                "description": "Screen sharing with verified caregiver",
                "metadata": {
                    "tool_name": "Google Meet / Caregiver Support",
                    "screen_sharing_active": True,
                    "known_assistant": 1,
                    "first_time_assistance": 0,
                    "assistance_history": 7,
                    "assistant_label": "Son (Rahul - Verified Caregiver)",
                    "screen_share_duration": 105.0
                }
            },
            {
                "step_index": 2,
                "event_type": "APP_SWITCH",
                "description": "Switch to mobile banking app",
                "metadata": {
                    "from_app": "com.whatsapp",
                    "to_app": "com.snapwork.hdfc",
                    "app_switch_count": 1,
                    "rapid_app_switch": False
                }
            },
            {
                "step_index": 3,
                "event_type": "BANKING_APP_FOREGROUNDED",
                "description": "Banking app opened",
                "metadata": {
                    "app_name": "HDFC Mobile Banking",
                    "package_name": "com.snapwork.hdfc",
                    "banking_app_active": True,
                    "session_time_seconds": 15
                }
            },
            {
                "step_index": 4,
                "event_type": "NAVIGATION_BACK",
                "description": "Normal account navigation",
                "metadata": {
                    "screen_name": "AccountSummaryScreen",
                    "navigation_back_count": 1,
                    "hesitation_indicator": False
                }
            },
            {
                "step_index": 5,
                "event_type": "HIGH_VALUE_TRANSACTION_INITIATED",
                "description": "Routine utility bill payment",
                "metadata": {
                    "transaction_amount": 1850.0,
                    "currency": "INR",
                    "payment_rail": "UPI",
                    "recipient_type": "EXISTING_BILLER",
                    "target_nickname": "Electricity Board"
                }
            },
            {
                "step_index": 6,
                "event_type": "AUTHENTICATION_EVENT",
                "description": "Biometric authentication verified",
                "metadata": {
                    "auth_method": "BIOMETRIC_FINGERPRINT",
                    "success": True,
                    "authentication_event": 1
                }
            },
            {
                "step_index": 7,
                "event_type": "TRANSACTION_COMPLETED",
                "description": "Transaction safely completed",
                "metadata": {
                    "transaction_completed": True,
                    "transaction_amount": 1850.0,
                    "reference_id": "TXN_HDFC_891273"
                }
            },
            {
                "step_index": 8,
                "event_type": "SCREEN_SHARING_ENDED",
                "description": "Screen sharing session concluded",
                "metadata": {
                    "screen_sharing_active": False,
                    "tool_name": "Google Meet / Caregiver Support",
                    "duration_seconds": 105.0,
                    "screen_share_duration": 105.0
                }
            }
        ]
    },
    "legit_high_value": {
        "id": "legit_high_value",
        "name": "Legitimate High-Value Bank Transfer",
        "category": "SAFE / UNCOACHED",
        "description": "Direct user high-value transfer without screen sharing or external coaching.",
        "expected_risk": "SAFE",
        "steps": [
            {
                "step_index": 1,
                "event_type": "BANKING_APP_FOREGROUNDED",
                "description": "Banking app opened directly",
                "metadata": {
                    "app_name": "ICICI iMobile",
                    "package_name": "com.icicibank.mobile",
                    "banking_app_active": True,
                    "screen_sharing_active": False
                }
            },
            {
                "step_index": 2,
                "event_type": "NAVIGATION_BACK",
                "description": "Standard payee selection",
                "metadata": {
                    "screen_name": "SavedBeneficiaryScreen",
                    "navigation_back_count": 1,
                    "hesitation_indicator": False
                }
            },
            {
                "step_index": 3,
                "event_type": "HIGH_VALUE_TRANSACTION_INITIATED",
                "description": "High-value transfer to established payee",
                "metadata": {
                    "transaction_amount": 150000.0,
                    "currency": "INR",
                    "payment_rail": "NEFT",
                    "recipient_type": "SAVED_BENEFICIARY",
                    "target_nickname": "College Tuition Deposit",
                    "high_value_transfer": True
                }
            },
            {
                "step_index": 4,
                "event_type": "AUTHENTICATION_EVENT",
                "description": "Biometric / MPIN verification",
                "metadata": {
                    "auth_method": "BIOMETRIC_FINGERPRINT",
                    "success": True,
                    "authentication_event": 1
                }
            },
            {
                "step_index": 5,
                "event_type": "TRANSACTION_COMPLETED",
                "description": "Transfer executed successfully",
                "metadata": {
                    "transaction_completed": True,
                    "transaction_amount": 150000.0,
                    "reference_id": "TXN_ICICI_654219"
                }
            },
            {
                "step_index": 6,
                "event_type": "BANKING_APP_CLOSED",
                "description": "Banking session exited",
                "metadata": {
                    "banking_app_active": False,
                    "app_name": "ICICI iMobile"
                }
            }
        ]
    },
    "rapid_banking": {
        "id": "rapid_banking",
        "name": "Suspicious Rapid Banking Actions",
        "category": "SUSPICIOUS ACTIVITY",
        "description": "No screen sharing, but rapid app switching, rapid payee paste, and rapid navigation reversals.",
        "expected_risk": "MONITORING",
        "steps": [
            {
                "step_index": 1,
                "event_type": "BANKING_APP_FOREGROUNDED",
                "description": "Banking app opened",
                "metadata": {
                    "app_name": "SBI YONO",
                    "banking_app_active": True,
                    "package_name": "com.sbi.lotusintouch"
                }
            },
            {
                "step_index": 2,
                "event_type": "APP_SWITCH",
                "description": "Elevated rapid app switching",
                "metadata": {
                    "from_app": "com.google.android.apps.messaging",
                    "to_app": "com.sbi.lotusintouch",
                    "app_switch_count": 7,
                    "rapid_app_switch": True
                }
            },
            {
                "step_index": 3,
                "event_type": "NAVIGATION_BACK",
                "description": "Frequent navigation reversals (hesitation)",
                "metadata": {
                    "screen_name": "TransferPayeeScreen",
                    "navigation_back_count": 5,
                    "hesitation_indicator": True
                }
            },
            {
                "step_index": 4,
                "event_type": "NEW_BENEFICIARY_ADDED",
                "description": "Rapid beneficiary added via clipboard paste",
                "metadata": {
                    "beneficiary_label": "Fast_Wire_Desk_88",
                    "paste_event_detected": True,
                    "new_beneficiary": True,
                    "creation_speed_ms": 1800
                }
            },
            {
                "step_index": 5,
                "event_type": "HIGH_VALUE_TRANSACTION_INITIATED",
                "description": "Urgent transfer initiated",
                "metadata": {
                    "transaction_amount": 48000.0,
                    "currency": "INR",
                    "payment_rail": "IMPS_INSTANT",
                    "target_nickname": "Fast_Wire_Desk_88"
                }
            }
        ]
    },
    "scam_cancellation": {
        "id": "scam_cancellation",
        "name": "High-Risk Scam Intercepted & Cancelled",
        "category": "SCAM INTERCEPTION",
        "description": "Coached scam where GuardianAI warning triggers and user cancels transaction safely.",
        "expected_risk": "THREAT_DETECTED",
        "steps": [
            {
                "step_index": 1,
                "event_type": "SCREEN_SHARING_STARTED",
                "description": "Screen sharing started (AnyDesk)",
                "metadata": {
                    "tool_name": "AnyDesk Remote Support",
                    "screen_sharing_active": True,
                    "known_assistant": 0,
                    "first_time_assistance": 1,
                    "remote_host": "External Remote Client (Claiming Electricity Refund Desk)"
                }
            },
            {
                "step_index": 2,
                "event_type": "BANKING_APP_FOREGROUNDED",
                "description": "Banking app opened under screen mirror",
                "metadata": {
                    "app_name": "HDFC Mobile Banking",
                    "banking_app_active": True,
                    "package_name": "com.snapwork.hdfc"
                }
            },
            {
                "step_index": 3,
                "event_type": "NEW_BENEFICIARY_ADDED",
                "description": "New beneficiary added via clipboard paste",
                "metadata": {
                    "beneficiary_label": "Electricity_Refund_Office",
                    "new_beneficiary": True,
                    "paste_event_detected": True,
                    "creation_speed_ms": 2800
                }
            },
            {
                "step_index": 4,
                "event_type": "HIGH_VALUE_TRANSACTION_INITIATED",
                "description": "High-value transfer initiated under dictation",
                "metadata": {
                    "transaction_amount": 120000.0,
                    "currency": "INR",
                    "payment_rail": "IMPS_INSTANT",
                    "target_nickname": "Electricity_Refund_Office"
                }
            },
            {
                "step_index": 5,
                "event_type": "COACHED_BEHAVIOUR_TRIGGERED",
                "description": "Suspicious coaching cadence flagged",
                "metadata": {
                    "coached_sequence_detected": True,
                    "rapid_app_switch": True,
                    "touch_cadence_variance_score": 0.92,
                    "pattern_signature": "REMOTE_COACHED_FINANCIAL_EXFILTRATION"
                }
            },
            {
                "step_index": 6,
                "event_type": "INTERVENTION_TRIGGERED",
                "description": "GuardianAI Emergency Scam Warning displayed",
                "metadata": {
                    "halt_transaction": True,
                    "intervention_type": "HIGH_PRIORITY_ELDERLY_SAFE_MODAL",
                    "urgency": "CRITICAL"
                }
            },
            {
                "step_index": 7,
                "event_type": "TRANSACTION_CANCELLED",
                "description": "Simulated action: User cancelled transaction upon scam warning",
                "metadata": {
                    "transaction_cancelled": True,
                    "simulated_action": True,
                    "reason": "USER_CANCELLED_AFTER_SCAM_WARNING",
                    "transaction_amount": 120000.0,
                    "disclaimer": "Simulated action: User cancelled transfer upon warning. No real banking transfer executed or blocked."
                }
            }
        ]
    }
}

def get_simulator_scenarios() -> List[Dict[str, Any]]:
    """Returns catalog of all available simulator scenarios."""
    return [
        {
            "id": sc["id"],
            "name": sc["name"],
            "category": sc["category"],
            "description": sc["description"],
            "expected_risk": sc.get("expected_risk", "SAFE"),
            "total_steps": len(sc["steps"])
        }
        for sc in SCENARIOS.values()
    ]

def get_or_create_active_session(db: Session, session_id: str = "demo-session-live") -> SessionModel:
    return get_or_create_session(db, session_id)

def advance_simulator_step(
    db: Session,
    session_id: str = "demo-session-live",
    scenario_id: Optional[str] = None
) -> Dict[str, Any]:
    sess = get_or_create_active_session(db, session_id)

    # Determine scenario step sequence
    sc_key = scenario_id if (scenario_id and scenario_id in SCENARIOS) else "coached_scam"
    scenario = SCENARIOS[sc_key]
    steps = scenario["steps"]

    existing_events = (
        db.query(EventModel)
        .filter(EventModel.session_id == session_id)
        .order_by(EventModel.timestamp)
        .all()
    )
    current_step_count = len(existing_events)

    if current_step_count >= len(steps):
        risk_res = evaluate_session_risk(
            session_id,
            [{"event_type": e.event_type, "metadata": e.event_metadata, "timestamp": e.timestamp} for e in existing_events]
        )
        return {
            "status": "COMPLETED",
            "message": f"Scenario '{scenario['name']}' reached final stage.",
            "current_step": current_step_count,
            "total_steps": len(steps),
            "scenario_id": sc_key,
            "scenario_name": scenario["name"],
            "risk": risk_res.model_dump()
        }

    next_step_data = steps[current_step_count]
    now = datetime.now(timezone.utc)

    new_event = EventModel(
        event_id=f"ev_{uuid.uuid4().hex[:12]}",
        session_id=session_id,
        timestamp=now,
        event_type=next_step_data["event_type"],
        metadata_json=json.dumps(next_step_data["metadata"])
    )
    db.add(new_event)
    db.commit()

    # Re-evaluate all events for updated risk
    all_events = (
        db.query(EventModel)
        .filter(EventModel.session_id == session_id)
        .order_by(EventModel.timestamp)
        .all()
    )
    events_payload = [
        {"event_type": e.event_type, "metadata": e.event_metadata, "timestamp": e.timestamp}
        for e in all_events
    ]
    risk_evaluation = evaluate_session_risk(session_id, events_payload)

    sess.risk_score = risk_evaluation.risk_score
    sess.risk_level = risk_evaluation.risk_level

    # Handle intervention creation on INTERVENTION_TRIGGERED
    if next_step_data["event_type"] == "INTERVENTION_TRIGGERED":
        intervention = InterventionModel(
            intervention_id=f"int_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            timestamp=now,
            risk_score=risk_evaluation.risk_score,
            action="TRANSACTION_HALTED",
            user_response="PENDING"
        )
        db.add(intervention)
        sess.final_outcome = "INTERRUPTED"

    # Handle cancellation step in cancellation scenario
    if next_step_data["event_type"] == "TRANSACTION_CANCELLED":
        # Ensure intervention record exists and is marked CANCEL_TRANSACTION
        existing_inv = (
            db.query(InterventionModel)
            .filter(InterventionModel.session_id == session_id)
            .order_by(InterventionModel.timestamp.desc())
            .first()
        )
        if existing_inv:
            existing_inv.user_response = "CANCEL_TRANSACTION"
        else:
            inv = InterventionModel(
                intervention_id=f"int_{uuid.uuid4().hex[:12]}",
                session_id=session_id,
                timestamp=now,
                risk_score=risk_evaluation.risk_score,
                action="TRANSACTION_HALTED",
                user_response="CANCEL_TRANSACTION"
            )
            db.add(inv)
        sess.final_outcome = "INTERRUPTED"

    # If scenario reached end and final_outcome is still ACTIVE, finalize it
    if current_step_count + 1 >= len(steps):
        if sess.final_outcome == "ACTIVE":
            sess.final_outcome = "ALLOWED" if risk_evaluation.risk_score < 70.0 else "INTERRUPTED"

    db.commit()
    db.refresh(sess)

    logger.info("Simulator advanced to step %d/%d (%s) for session %s", current_step_count + 1, len(steps), sc_key, session_id)

    return {
        "status": "STEP_ADVANCED",
        "current_step": current_step_count + 1,
        "total_steps": len(steps),
        "step_name": next_step_data["description"],
        "event_type": next_step_data["event_type"],
        "scenario_id": sc_key,
        "scenario_name": scenario["name"],
        "risk": risk_evaluation.model_dump()
    }

def reset_simulator(
    db: Session,
    session_id: str = "demo-session-live",
    scenario_id: Optional[str] = None
) -> Dict[str, Any]:
    db.query(InterventionModel).filter(InterventionModel.session_id == session_id).delete()
    db.query(EventModel).filter(EventModel.session_id == session_id).delete()
    db.query(SessionModel).filter(SessionModel.session_id == session_id).delete()
    db.commit()

    new_sess = SessionModel(
        session_id=session_id,
        start_time=datetime.now(timezone.utc),
        risk_score=0.0,
        risk_level="SAFE",
        final_outcome="ACTIVE"
    )
    db.add(new_sess)
    db.commit()

    sc_key = scenario_id if (scenario_id and scenario_id in SCENARIOS) else "coached_scam"
    logger.info("Reset simulator session %s (scenario: %s) to SAFE state", session_id, sc_key)

    return {
        "status": "RESET_SUCCESSFUL",
        "session_id": session_id,
        "scenario_id": sc_key,
        "message": f"Session '{session_id}' reset to initial clean SAFE state."
    }

def seed_sample_historical_data(db: Session):
    count = db.query(SessionModel).count()
    if count > 1:
        return

    now = datetime.now(timezone.utc)
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
    logger.info("Sample historical telemetry seeded successfully.")
