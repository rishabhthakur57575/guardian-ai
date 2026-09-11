import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert data["privacy_compliance"] == "NO_PII_STRICT"

def test_privacy_validation():
    # Attempt to send forbidden PII key (e.g. otp / password)
    forbidden_payload = {
        "session_id": "test-privacy-violation",
        "event_type": "SUSPICIOUS_LOGIN",
        "metadata": {
            "otp": "123456",
            "screen_sharing_active": True
        }
    }
    res = client.post("/api/events", json=forbidden_payload)
    assert res.status_code == 422 # Pydantic privacy validator rejection

def test_event_ingestion_and_risk_scoring():
    session_id = "test-session-flow"
    
    # Ingest event 1: Screen sharing
    ev1 = {
        "session_id": session_id,
        "event_type": "SCREEN_SHARING_STARTED",
        "metadata": {"tool_name": "AnyDesk", "screen_sharing_active": True}
    }
    r1 = client.post("/api/events", json=ev1)
    assert r1.status_code == 200

    # Ingest event 2: Banking app
    ev2 = {
        "session_id": session_id,
        "event_type": "BANKING_APP_FOREGROUNDED",
        "metadata": {"app_name": "HDFC Mobile", "banking_app_active": True}
    }
    r2 = client.post("/api/events", json=ev2)
    assert r2.status_code == 200

    # Check risk score
    risk_res = client.post("/api/risk-score", json={"session_id": session_id})
    assert risk_res.status_code == 200
    risk_data = risk_res.json()
    assert risk_data["risk_score"] >= 50.0

def test_intervention_recording():
    session_id = "test-session-flow"
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

def test_analytics():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "scam_pattern_frequencies" in data
    assert "risk_distribution" in data

def test_simulator_cycle():
    session_id = "test-sim-cycle"
    # Reset
    res_reset = client.post(f"/api/simulator/reset?session_id={session_id}")
    assert res_reset.status_code == 200

    # Advance 1 step
    res_step = client.post(f"/api/simulator/step?session_id={session_id}")
    assert res_step.status_code == 200
    assert res_step.json()["current_step"] == 1
