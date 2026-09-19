import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.db.models import SessionModel, EventModel, InterventionModel
from backend.app.services.risk_engine import (
    predict_risk,
    get_risk_predictor,
    set_risk_predictor,
    HeuristicRiskPredictor
)
from backend.app.services.feature_service import extract_features

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["privacy_compliance"] == "NO_PII_STRICT"
    assert "timestamp" in data
    assert "version" in data

def test_root():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "GuardianAI" in data["message"]
    assert data["api_prefix"] == "/api"

def test_privacy_validation():
    # Attempt to send forbidden PII key (e.g. otp / password / cvv)
    forbidden_payload = {
        "session_id": f"test-privacy-{uuid.uuid4().hex[:8]}",
        "event_type": "SUSPICIOUS_LOGIN",
        "metadata": {
            "otp": "123456",
            "screen_sharing_active": True
        }
    }
    res = client.post("/api/events", json=forbidden_payload)
    assert res.status_code == 422
    assert "detail" in res.json()

def test_event_to_api_to_db_to_risk_engine_pipeline():
    """
    Verifies the end-to-end pipeline:
    event -> API -> database -> feature extraction -> risk engine -> API response
    """
    session_id = f"test-e2e-pipeline-{uuid.uuid4().hex[:8]}"


    # Step 1: Ingest Screen Sharing event
    ev1 = {
        "session_id": session_id,
        "event_type": "SCREEN_SHARING_STARTED",
        "metadata": {
            "tool_name": "AnyDesk Remote Support",
            "screen_sharing_active": True
        }
    }
    r1 = client.post("/api/events", json=ev1)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["event_type"] == "SCREEN_SHARING_STARTED"
    assert d1["session_id"] == session_id

    # Step 2: Ingest Banking App Foregrounded event
    ev2 = {
        "session_id": session_id,
        "event_type": "BANKING_APP_FOREGROUNDED",
        "metadata": {
            "app_name": "HDFC Mobile Banking",
            "banking_app_active": True
        }
    }
    r2 = client.post("/api/events", json=ev2)
    assert r2.status_code == 200

    # Step 3: Verify SQLite Database Persistence directly
    with SessionLocal() as db:
        db_sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert db_sess is not None
        assert db_sess.risk_score >= 50.0  # Screen share (25) + Banking under screen share (25)
        assert db_sess.risk_level == "MONITORING"

        db_events = db.query(EventModel).filter(EventModel.session_id == session_id).all()
        assert len(db_events) == 2

    # Step 4: Ingest Beneficiary Addition & High Value Transaction
    ev3 = {
        "session_id": session_id,
        "event_type": "NEW_BENEFICIARY_ADDED",
        "metadata": {
            "beneficiary_label": "Refund_Agent_99",
            "new_beneficiary": True
        }
    }
    r3 = client.post("/api/events", json=ev3)
    assert r3.status_code == 200

    ev4 = {
        "session_id": session_id,
        "event_type": "HIGH_VALUE_TRANSACTION_INITIATED",
        "metadata": {
            "transaction_amount": 125000.0,
            "currency": "INR"
        }
    }
    r4 = client.post("/api/events", json=ev4)
    assert r4.status_code == 200

    # Verify session risk escalated to THREAT_DETECTED in database
    with SessionLocal() as db:
        db_sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert db_sess.risk_score >= 70.0
        assert db_sess.risk_level == "THREAT_DETECTED"

def test_get_events():
    session_id = f"test-get-events-{uuid.uuid4().hex[:8]}"
    client.post("/api/events", json={
        "session_id": session_id,
        "event_type": "SCREEN_SHARING_STARTED",
        "metadata": {"screen_sharing_active": True}
    })

    # Query with session_id filter
    res = client.get(f"/api/events?session_id={session_id}")
    assert res.status_code == 200
    events = res.json()
    assert len(events) >= 1
    assert events[0]["session_id"] == session_id

def test_risk_score_endpoint():
    session_id = f"test-risk-score-{uuid.uuid4().hex[:8]}"

    # Ingest event into DB
    client.post("/api/events", json={
        "session_id": session_id,
        "event_type": "SCREEN_SHARING_STARTED",
        "metadata": {"screen_sharing_active": True, "tool_name": "TeamViewer"}
    })

    # Test 1: Compute risk from DB events
    res_db = client.post("/api/risk-score", json={"session_id": session_id})
    assert res_db.status_code == 200
    data_db = res_db.json()
    assert data_db["session_id"] == session_id
    assert data_db["risk_score"] == 25.0
    assert data_db["risk_level"] == "SAFE"

    # Test 2: Compute risk from explicit event payload in request
    res_payload = client.post("/api/risk-score", json={
        "session_id": session_id,
        "events": [
            {"event_type": "SCREEN_SHARING_STARTED", "metadata": {"screen_sharing_active": True}},
            {"event_type": "BANKING_APP_FOREGROUNDED", "metadata": {"banking_app_active": True}},
            {"event_type": "NEW_BENEFICIARY_ADDED", "metadata": {"new_beneficiary": True}},
            {"event_type": "HIGH_VALUE_TRANSACTION_INITIATED", "metadata": {"transaction_amount": 75000.0}}
        ]
    })
    assert res_payload.status_code == 200
    data_payload = res_payload.json()
    assert data_payload["risk_score"] >= 70.0
    assert data_payload["risk_level"] == "THREAT_DETECTED"
    assert data_payload["recommended_action"] == "INTERVENE"

def test_session_endpoints():
    session_id = f"test-session-details-{uuid.uuid4().hex[:8]}"
    client.post("/api/events", json={
        "session_id": session_id,
        "event_type": "BANKING_APP_FOREGROUNDED",
        "metadata": {"banking_app_active": True}
    })

    # GET session by ID
    res = client.get(f"/api/session/{session_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == session_id
    assert len(data["events"]) >= 1

    # GET non-existent session
    res_404 = client.get("/api/session/non-existent-session-id-404")
    assert res_404.status_code == 404

    # GET list sessions
    res_list = client.get("/api/sessions")
    assert res_list.status_code == 200
    assert isinstance(res_list.json(), list)
    assert len(res_list.json()) > 0

def test_intervention_recording():
    session_id = f"test-intervention-{uuid.uuid4().hex[:8]}"
    # Ensure session exists
    client.post("/api/events", json={
        "session_id": session_id,
        "event_type": "SCREEN_SHARING_STARTED",
        "metadata": {"screen_sharing_active": True}
    })

    # Record CANCEL_TRANSACTION intervention
    inv_payload = {
        "session_id": session_id,
        "risk_score": 85.0,
        "action": "TRANSACTION_HALTED",
        "user_response": "CANCEL_TRANSACTION"
    }
    res = client.post("/api/intervention", json=inv_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["user_response"] == "CANCEL_TRANSACTION"

    # Verify session outcome was updated to INTERRUPTED
    sess_res = client.get(f"/api/session/{session_id}")
    assert sess_res.status_code == 200
    assert sess_res.json()["final_outcome"] == "INTERRUPTED"

    # Record intervention for invalid session -> 404
    inv_invalid = {
        "session_id": f"invalid-session-{uuid.uuid4().hex[:8]}",
        "risk_score": 90.0,
        "action": "WARNING_DISPLAYED",
        "user_response": "PENDING"
    }
    res_invalid = client.post("/api/intervention", json=inv_invalid)
    assert res_invalid.status_code == 404


def test_analytics():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "protected_sessions_timeline" in data
    assert "scam_pattern_frequencies" in data
    assert "risk_distribution" in data
    assert "intervention_outcomes" in data
    assert data["metrics"]["system_status"] == "ACTIVE_SHIELD_ONLINE"

def test_simulator_cycle():
    session_id = "test-sim-cycle"
    # Reset
    res_reset = client.post(f"/api/simulator/reset?session_id={session_id}")
    assert res_reset.status_code == 200
    assert res_reset.json()["status"] == "RESET_SUCCESSFUL"

    # Advance 1 step
    res_step = client.post(f"/api/simulator/step?session_id={session_id}")
    assert res_step.status_code == 200
    assert res_step.json()["current_step"] == 1

    # Check simulator state
    res_state = client.get(f"/api/simulator/state?session_id={session_id}")
    assert res_state.status_code == 200
    assert res_state.json()["current_step"] == 1

def test_modular_ml_predictor_interface():
    """
    Validates Task 6:
    Clean interface: predict_risk(features) and modular pluggability.
    """
    raw_events = [
        {"event_type": "SCREEN_SHARING_STARTED", "metadata": {"screen_sharing_active": True, "tool_name": "AnyDesk"}},
        {"event_type": "BANKING_APP_FOREGROUNDED", "metadata": {"banking_app_active": True, "app_name": "SBI"}},
    ]

    features = extract_features(raw_events)
    assert features["screen_sharing_active"] is True
    assert features["banking_app_opened"] is True
    assert features["banking_under_screen_share"] is True

    # Test predict_risk function interface directly
    result = predict_risk(features, session_id="test-modular-predictor")
    assert result.risk_score >= 50.0
    assert result.risk_level == "MONITORING"

    # Verify custom predictor can be swapped modularly
    original_predictor = get_risk_predictor()
    try:
        class MockCustomPredictor:
            def predict(self, feats, session_id=""):
                from backend.app.schemas.schemas import RiskScoreResponse
                from datetime import datetime, timezone
                return RiskScoreResponse(
                    session_id=session_id,
                    risk_score=99.9,
                    risk_level="THREAT_DETECTED",
                    reasons=["Custom ML model prediction"],
                    risk_factors=[],
                    recommended_action="INTERVENE",
                    evaluated_at=datetime.now(timezone.utc)
                )

        set_risk_predictor(MockCustomPredictor())
        mock_result = predict_risk(features, session_id="test-modular-predictor")
        assert mock_result.risk_score == 99.9
        assert mock_result.risk_level == "THREAT_DETECTED"
    finally:
        set_risk_predictor(original_predictor)
