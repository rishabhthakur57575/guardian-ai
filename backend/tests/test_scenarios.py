import uuid
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.db.models import SessionModel, EventModel, InterventionModel
from backend.app.services.simulator_service import SCENARIOS

client = TestClient(app)

def test_simulator_scenarios_catalog():
    """Verifies that all 5 required test scenarios exist in the catalog."""
    res = client.get("/api/simulator/scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) == 5

    scenario_ids = {s["id"] for s in scenarios}
    expected_ids = {
        "family_assistance",
        "legit_high_value",
        "coached_scam",
        "rapid_banking",
        "scam_cancellation"
    }
    assert expected_ids == scenario_ids

    # Check that each scenario has required metadata fields
    for s in scenarios:
        assert "name" in s
        assert "category" in s
        assert "description" in s
        assert "total_steps" in s
        assert s["total_steps"] > 0

def test_scenario_1_family_assistance_execution():
    """Scenario 1: Legitimate family remote assistance -> SAFE baseline, ALLOWED outcome."""
    session_id = f"test-sc1-{uuid.uuid4().hex[:8]}"

    # Reset session
    r_reset = client.post(f"/api/simulator/reset?session_id={session_id}&scenario_id=family_assistance")
    assert r_reset.status_code == 200

    # Advance all steps
    total_steps = len(SCENARIOS["family_assistance"]["steps"])
    last_res = None
    for i in range(total_steps):
        r_step = client.post(f"/api/simulator/step?session_id={session_id}&scenario_id=family_assistance")
        assert r_step.status_code == 200
        last_res = r_step.json()
        assert last_res["current_step"] == i + 1

    # Final step outcome verification
    assert last_res["status"] in ["STEP_ADVANCED", "COMPLETED"]
    assert last_res["risk"]["risk_score"] < 30.0
    assert last_res["risk"]["risk_level"] == "SAFE"

    # Verify database session state
    with SessionLocal() as db:
        sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert sess is not None
        assert sess.risk_level == "SAFE"
        assert sess.final_outcome == "ALLOWED"
        events = db.query(EventModel).filter(EventModel.session_id == session_id).all()
        assert len(events) == total_steps

def test_scenario_2_legit_high_value_execution():
    """Scenario 2: Legitimate high-value bank transfer without suspicious coaching -> SAFE baseline."""
    session_id = f"test-sc2-{uuid.uuid4().hex[:8]}"

    # Reset session
    r_reset = client.post(f"/api/simulator/reset?session_id={session_id}&scenario_id=legit_high_value")
    assert r_reset.status_code == 200

    total_steps = len(SCENARIOS["legit_high_value"]["steps"])
    last_res = None
    for i in range(total_steps):
        r_step = client.post(f"/api/simulator/step?session_id={session_id}&scenario_id=legit_high_value")
        assert r_step.status_code == 200
        last_res = r_step.json()

    assert last_res["risk"]["risk_score"] < 30.0
    assert last_res["risk"]["risk_level"] == "SAFE"

    with SessionLocal() as db:
        sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert sess is not None
        assert sess.final_outcome == "ALLOWED"
        assert sess.risk_level == "SAFE"

def test_scenario_3_coached_scam_execution():
    """Scenario 3: Coached remote-support scam -> THREAT_DETECTED, intervention triggered."""
    session_id = f"test-sc3-{uuid.uuid4().hex[:8]}"

    r_reset = client.post(f"/api/simulator/reset?session_id={session_id}&scenario_id=coached_scam")
    assert r_reset.status_code == 200

    total_steps = len(SCENARIOS["coached_scam"]["steps"])
    for i in range(total_steps):
        r_step = client.post(f"/api/simulator/step?session_id={session_id}&scenario_id=coached_scam")
        assert r_step.status_code == 200
        data = r_step.json()
        if data["event_type"] == "INTERVENTION_TRIGGERED":
            assert data["risk"]["risk_level"] == "THREAT_DETECTED"
            assert data["risk"]["risk_score"] >= 70.0

    with SessionLocal() as db:
        sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert sess.risk_level == "THREAT_DETECTED"
        assert sess.final_outcome == "INTERRUPTED"
        inv = db.query(InterventionModel).filter(InterventionModel.session_id == session_id).first()
        assert inv is not None
        assert inv.action == "TRANSACTION_HALTED"

def test_scenario_4_rapid_banking_execution():
    """Scenario 4: Suspicious rapid banking actions -> Elevated MONITORING risk."""
    session_id = f"test-sc4-{uuid.uuid4().hex[:8]}"

    client.post(f"/api/simulator/reset?session_id={session_id}&scenario_id=rapid_banking")

    total_steps = len(SCENARIOS["rapid_banking"]["steps"])
    last_res = None
    for i in range(total_steps):
        r_step = client.post(f"/api/simulator/step?session_id={session_id}&scenario_id=rapid_banking")
        assert r_step.status_code == 200
        last_res = r_step.json()

    # Risk should be elevated due to rapid switching, paste, reversals
    assert last_res["risk"]["risk_score"] >= 30.0

def test_scenario_5_scam_cancellation_persistence():
    """
    Scenario 5: High-risk scam scenario where the user cancels after receiving a warning.
    Verifies that cancellation is recorded as a simulated action and persists properly.
    """
    session_id = f"test-sc5-{uuid.uuid4().hex[:8]}"

    client.post(f"/api/simulator/reset?session_id={session_id}&scenario_id=scam_cancellation")

    total_steps = len(SCENARIOS["scam_cancellation"]["steps"])
    last_res = None
    for i in range(total_steps):
        r_step = client.post(f"/api/simulator/step?session_id={session_id}&scenario_id=scam_cancellation")
        assert r_step.status_code == 200
        last_res = r_step.json()

    # Step 7 is TRANSACTION_CANCELLED
    assert last_res["event_type"] == "TRANSACTION_CANCELLED"

    with SessionLocal() as db:
        sess = db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        assert sess is not None
        assert sess.final_outcome == "INTERRUPTED"

        # Verify simulated action disclaimer in event metadata
        cancel_event = (
            db.query(EventModel)
            .filter(EventModel.session_id == session_id, EventModel.event_type == "TRANSACTION_CANCELLED")
            .first()
        )
        assert cancel_event is not None
        meta = cancel_event.event_metadata
        assert meta.get("simulated_action") is True
        assert "USER_CANCELLED_AFTER_SCAM_WARNING" in meta.get("reason", "")
        assert "no real banking transfer" in meta.get("disclaimer", "").lower()

        # Verify intervention record updated to CANCEL_TRANSACTION
        inv = db.query(InterventionModel).filter(InterventionModel.session_id == session_id).first()
        assert inv is not None
        assert inv.user_response == "CANCEL_TRANSACTION"

def test_session_isolation():
    """Verifies that events and risk scores across different session IDs are completely isolated."""
    sess_a = f"test-iso-a-{uuid.uuid4().hex[:8]}"
    sess_b = f"test-iso-b-{uuid.uuid4().hex[:8]}"

    # Reset both
    client.post(f"/api/simulator/reset?session_id={sess_a}&scenario_id=family_assistance")
    client.post(f"/api/simulator/reset?session_id={sess_b}&scenario_id=coached_scam")

    # Ingest 3 events into Session A (family assistance)
    for _ in range(3):
        client.post(f"/api/simulator/step?session_id={sess_a}&scenario_id=family_assistance")

    # Ingest 5 events into Session B (coached scam)
    for _ in range(5):
        client.post(f"/api/simulator/step?session_id={sess_b}&scenario_id=coached_scam")

    # Verify Session A
    res_a = client.get(f"/api/session/{sess_a}")
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert len(data_a["events"]) == 3
    assert data_a["risk_score"] < 30.0

    # Verify Session B
    res_b = client.get(f"/api/session/{sess_b}")
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert len(data_b["events"]) == 5
    assert data_b["risk_score"] >= 70.0

def test_reset_behavior():
    """Verifies that reset clears events and risk without polluting other active sessions."""
    sess_target = f"test-rst-tgt-{uuid.uuid4().hex[:8]}"
    sess_other = f"test-rst-oth-{uuid.uuid4().hex[:8]}"

    client.post(f"/api/simulator/step?session_id={sess_target}&scenario_id=coached_scam")
    client.post(f"/api/simulator/step?session_id={sess_other}&scenario_id=coached_scam")

    # Reset only target session
    r_rst = client.post(f"/api/simulator/reset?session_id={sess_target}&scenario_id=coached_scam")
    assert r_rst.status_code == 200
    assert r_rst.json()["status"] == "RESET_SUCCESSFUL"

    # Target session should have 0 events and SAFE risk
    res_tgt = client.get(f"/api/session/{sess_target}")
    assert res_tgt.status_code == 200
    assert len(res_tgt.json()["events"]) == 0
    assert res_tgt.json()["risk_score"] == 0.0

    # Other session should retain its event
    res_oth = client.get(f"/api/session/{sess_other}")
    assert res_oth.status_code == 200
    assert len(res_oth.json()["events"]) == 1

def test_trust_override_does_not_whitelist_helper():
    """
    Requirement 11: Do not automatically trust or whitelist a helper based only on a user clicking a trust button.
    Verifies that TRUST_USER allows the transaction for that session but creates no persistent whitelist.
    """
    session_id = f"test-trust-{uuid.uuid4().hex[:8]}"

    # Ingest event
    client.post("/api/events", json={
        "session_id": session_id,
        "event_type": "SCREEN_SHARING_STARTED",
        "metadata": {"screen_sharing_active": True, "tool_name": "AnyDesk"}
    })

    # Post intervention with TRUST_USER
    r_inv = client.post("/api/intervention", json={
        "session_id": session_id,
        "risk_score": 85.0,
        "action": "TRANSACTION_HALTED",
        "user_response": "TRUST_USER"
    })
    assert r_inv.status_code == 200

    # Session outcome is ALLOWED
    sess_res = client.get(f"/api/session/{session_id}")
    assert sess_res.status_code == 200
    assert sess_res.json()["final_outcome"] == "ALLOWED"

    # A subsequent new session with an unverified AnyDesk connection remains unverified
    new_sess = f"test-trust-new-{uuid.uuid4().hex[:8]}"
    r_new = client.post("/api/events", json={
        "session_id": new_sess,
        "event_type": "SCREEN_SHARING_STARTED",
        "metadata": {"screen_sharing_active": True, "tool_name": "AnyDesk"}
    })
    assert r_new.status_code == 200
    risk_res = client.post("/api/risk-score", json={"session_id": new_sess})
    assert risk_res.status_code == 200
    # AnyDesk connection still flagged as active screen sharing (not whitelisted)
    assert risk_res.json()["risk_score"] >= 25.0

def test_backward_compatibility_simulator_endpoints():
    """Verifies that calling simulator endpoints without scenario_id defaults to coached_scam."""
    session_id = "test-compat-live"

    r_reset = client.post(f"/api/simulator/reset?session_id={session_id}")
    assert r_reset.status_code == 200

    r_step = client.post(f"/api/simulator/step?session_id={session_id}")
    assert r_step.status_code == 200
    data = r_step.json()
    assert data["scenario_id"] == "coached_scam"
    assert data["current_step"] == 1
    assert data["total_steps"] == 6

    r_state = client.get(f"/api/simulator/state?session_id={session_id}")
    assert r_state.status_code == 200
    state_data = r_state.json()
    assert state_data["total_steps"] == 6
    assert state_data["scenario_id"] == "coached_scam"
