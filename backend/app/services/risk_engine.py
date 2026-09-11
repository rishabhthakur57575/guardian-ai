from datetime import datetime
from typing import List, Dict, Any, Tuple
from backend.app.schemas.schemas import RiskScoreResponse, RiskFactor

"""
Risk Engine Service (Phase 1: Rule-based Heuristic Engine)
-----------------------------------------------------------
NOTE FOR PHASE 2 ML INTEGRATION:
In Phase 2, replace the heuristic scoring function `evaluate_session_risk`
with the ONNX / PyTorch / XGBoost behavioural inference model pipeline.
The function signature and output structure `RiskScoreResponse` will remain stable.
"""

def evaluate_session_risk(session_id: str, events: List[Dict[str, Any]]) -> RiskScoreResponse:
    score = 0.0
    reasons = []
    risk_factors: List[RiskFactor] = []

    screen_sharing_active = False
    screen_share_tool = None
    banking_opened = False
    banking_app_name = None
    beneficiary_added = False
    high_value_transfer = False
    transfer_amount = 0.0
    rapid_switching = False

    for ev in events:
        etype = ev.get("event_type", "").upper()
        meta = ev.get("metadata", {}) or {}

        if "SCREEN_SHARING" in etype or meta.get("screen_sharing_active"):
            screen_sharing_active = True
            screen_share_tool = meta.get("tool_name", "Remote Access Tool")

        if "BANKING_APP" in etype or meta.get("banking_app_active"):
            banking_opened = True
            banking_app_name = meta.get("app_name", "Banking Application")

        if "BENEFICIARY_ADDED" in etype or meta.get("new_beneficiary"):
            beneficiary_added = True

        if "TRANSACTION" in etype or meta.get("transaction_amount"):
            amt = float(meta.get("transaction_amount", 0.0) or 0.0)
            if amt > 0:
                transfer_amount = max(transfer_amount, amt)
                if amt >= 25000:
                    high_value_transfer = True

        if "RAPID_SWITCH" in etype or meta.get("rapid_app_switch"):
            rapid_switching = True

        if "COACHED_BEHAVIOUR" in etype or meta.get("coached_sequence_detected"):
            rapid_switching = True
            high_value_transfer = True

    # Rule 1: Active screen sharing
    if screen_sharing_active:
        score += 25.0
        risk_factors.append(RiskFactor(
            name="Remote Screen Sharing Active",
            severity="MEDIUM",
            description=f"Active screen mirroring session detected via {screen_share_tool or 'Remote Tool'}.",
            weight=25.0
        ))
        reasons.append(f"Active remote screen sharing ({screen_share_tool or 'Remote Assistant'}).")

    # Rule 2: Banking app accessed during screen sharing
    if screen_sharing_active and banking_opened:
        score += 25.0
        risk_factors.append(RiskFactor(
            name="Banking Access Under Screen Share",
            severity="HIGH",
            description=f"Financial application {banking_app_name or ''} opened while third party has screen visibility.",
            weight=25.0
        ))
        reasons.append("Banking app accessed during an active remote viewing session.")
    elif banking_opened and not screen_sharing_active:
        score += 5.0

    # Rule 3: Immediate beneficiary creation
    if beneficiary_added:
        added_weight = 20.0 if screen_sharing_active else 5.0
        score += added_weight
        risk_factors.append(RiskFactor(
            name="New Beneficiary Addition",
            severity="HIGH" if screen_sharing_active else "LOW",
            description="Newly created beneficiary recipient during current active workflow.",
            weight=added_weight
        ))
        reasons.append("New beneficiary created in rapid succession.")

    # Rule 4: High value transfer
    if high_value_transfer or transfer_amount >= 50000:
        added_weight = 20.0
        score += added_weight
        risk_factors.append(RiskFactor(
            name="High-Value Fund Transfer",
            severity="CRITICAL" if screen_sharing_active else "MEDIUM",
            description=f"Initiation of large transfer (₹{transfer_amount:,.0f}) exceeds typical safety threshold.",
            weight=added_weight
        ))
        reasons.append(f"Unusually high transaction amount (₹{transfer_amount:,.0f}).")

    # Rule 5: Rapid switching / Coached telemetry
    if rapid_switching:
        score += 10.0
        risk_factors.append(RiskFactor(
            name="Coached Interaction Sequence",
            severity="MEDIUM",
            description="Cadence of app switching and paste events matches remote voice coaching patterns.",
            weight=10.0
        ))
        reasons.append("Interaction sequence matches scripted remote-coaching scam profile.")

    # Bound score between 0 and 100
    final_score = min(max(round(score, 1), 0.0), 100.0)

    # Determine risk level
    if final_score >= 70.0:
        risk_level = "THREAT_DETECTED"
        recommended_action = "INTERVENE"
    elif final_score >= 30.0:
        risk_level = "MONITORING"
        recommended_action = "MONITOR"
    else:
        risk_level = "SAFE"
        recommended_action = "NONE"
        if not reasons:
            reasons.append("Normal device behavioural baseline maintained.")

    return RiskScoreResponse(
        session_id=session_id,
        risk_score=final_score,
        risk_level=risk_level,
        reasons=reasons,
        risk_factors=risk_factors,
        recommended_action=recommended_action,
        evaluated_at=datetime.utcnow()
    )
