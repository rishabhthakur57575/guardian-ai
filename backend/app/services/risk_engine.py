import importlib.util
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Protocol

from backend.app.schemas.schemas import RiskScoreResponse, RiskFactor
from backend.app.services.feature_service import extract_features

logger = logging.getLogger("guardianai.risk_engine")

class RiskPredictor(Protocol):
    """Clean interface for modular risk scoring engines (Heuristic or ML)."""
    def predict(self, features: Dict[str, Any], session_id: str = "") -> RiskScoreResponse:
        ...

class HeuristicRiskPredictor:
    """
    Phase 1 Rule-Based Behavioural Risk Scoring Engine.
    Evaluates 5 threat vectors based on extracted session features.
    """
    def predict(self, features: Dict[str, Any], session_id: str = "") -> RiskScoreResponse:
        score = 0.0
        reasons = []
        risk_factors: List[RiskFactor] = []

        screen_sharing = features.get("screen_sharing_active", False)
        screen_tool = features.get("screen_share_tool") or "Remote Access Tool"
        banking_opened = features.get("banking_app_opened", False)
        banking_app = features.get("banking_app_name") or "Banking Application"
        beneficiary_added = features.get("beneficiary_added", False)
        high_value = features.get("high_value_transfer", False)
        transfer_amt = float(features.get("transfer_amount", 0.0) or 0.0)
        rapid_switching = features.get("rapid_switching", False)
        coached_sequence = features.get("coached_sequence", False)

        # Rule 1: Active screen sharing
        if screen_sharing:
            score += 25.0
            risk_factors.append(RiskFactor(
                name="Remote Screen Sharing Active",
                severity="MEDIUM",
                description=f"Active screen mirroring session detected via {screen_tool}.",
                weight=25.0
            ))
            reasons.append(f"Active remote screen sharing ({screen_tool}).")

        # Rule 2: Banking app accessed during screen sharing
        if screen_sharing and banking_opened:
            score += 25.0
            risk_factors.append(RiskFactor(
                name="Banking Access Under Screen Share",
                severity="HIGH",
                description=f"Financial application {banking_app} opened while third party has screen visibility.",
                weight=25.0
            ))
            reasons.append("Banking app accessed during an active remote viewing session.")
        elif banking_opened and not screen_sharing:
            score += 5.0

        # Rule 3: Immediate beneficiary creation
        if beneficiary_added:
            added_weight = 20.0 if screen_sharing else 5.0
            score += added_weight
            risk_factors.append(RiskFactor(
                name="New Beneficiary Addition",
                severity="HIGH" if screen_sharing else "LOW",
                description="Newly created beneficiary recipient during current active workflow.",
                weight=added_weight
            ))
            reasons.append("New beneficiary created in rapid succession.")

        # Rule 4: High value transfer
        if high_value or transfer_amt >= 50000:
            added_weight = 20.0
            score += added_weight
            risk_factors.append(RiskFactor(
                name="High-Value Fund Transfer",
                severity="CRITICAL" if screen_sharing else "MEDIUM",
                description=f"Initiation of large transfer (₹{transfer_amt:,.0f}) exceeds typical safety threshold.",
                weight=added_weight
            ))
            reasons.append(f"Unusually high transaction amount (₹{transfer_amt:,.0f}).")

        # Rule 5: Rapid switching / Coached telemetry
        if rapid_switching or coached_sequence:
            score += 10.0
            risk_factors.append(RiskFactor(
                name="Coached Interaction Sequence",
                severity="MEDIUM",
                description="Cadence of app switching and paste events matches remote voice coaching patterns.",
                weight=10.0
            ))
            reasons.append("Interaction sequence matches scripted remote-coaching scam profile.")

        # Bound score between 0.0 and 100.0
        final_score = min(max(round(score, 1), 0.0), 100.0)

        # Determine categorical threat level
        if final_score >= 70.0:
            risk_level = "THREAT_DETECTED"
            recommended_action = "INTERVENE"
        elif final_score >= 30.0:
            risk_level = "MONITORING"
            recommended_action = "MONITOR"
        else:
            risk_level = "SAFE"
            recommended_action = "NONE"
        # Generate human explanation if possible
        human_exp = None
        try:
            from ml.human_explanation import generate_human_explanation
            human_exp = generate_human_explanation([r.lower() for r in reasons], context=features)
        except Exception:
            human_exp = {
                "headline": "Telemetry monitoring active." if final_score < 30 else "Potential suspicious behaviour detected.",
                "key_observations": reasons,
                "recommended_action": "No action required." if final_score < 30 else "Review ongoing activity carefully.",
                "provider_type": "HEURISTIC"
            }

        return RiskScoreResponse(
            session_id=session_id,
            risk_score=final_score,
            risk_level=risk_level,
            reasons=reasons,
            risk_factors=risk_factors,
            recommended_action=recommended_action,
            evaluated_at=datetime.now(timezone.utc),
            detected_signals=reasons,
            human_explanation=human_exp
        )

class MLRiskPredictor:
    """
    Adapter for Phase 2 ML Model Pipeline (ml/predict.py).
    Dynamically loads the ML inference function `predict_risk(features)` if available,
    gracefully falling back to HeuristicRiskPredictor if absent or uninitialized.
    """
    def __init__(self, fallback_predictor: Optional[RiskPredictor] = None):
        self.fallback = fallback_predictor or HeuristicRiskPredictor()
        self._ml_module = None
        self._load_ml_module()

    def _load_ml_module(self):
        # Look for ml/predict.py in the repository root
        repo_root = Path(__file__).resolve().parent.parent.parent.parent
        ml_predict_path = repo_root / "ml" / "predict.py"

        if ml_predict_path.exists():
            try:
                spec = importlib.util.spec_from_file_location("ml.predict", ml_predict_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "predict_risk"):
                        self._ml_module = module
                        logger.info("Loaded external ML model from %s", ml_predict_path)
            except Exception as exc:
                logger.warning("Failed to load ml/predict.py: %s. Using heuristic engine.", exc)

    def predict(self, features: Dict[str, Any], session_id: str = "") -> RiskScoreResponse:
        if self._ml_module and hasattr(self._ml_module, "predict_risk"):
            try:
                result = self._ml_module.predict_risk(features, session_id=session_id)
                if isinstance(result, RiskScoreResponse):
                    return result
                if isinstance(result, dict):
                    level_map = {
                        "HIGH": "THREAT_DETECTED",
                        "MEDIUM": "MONITORING",
                        "LOW": "SAFE",
                        "THREAT_DETECTED": "THREAT_DETECTED",
                        "MONITORING": "MONITORING",
                        "SAFE": "SAFE"
                    }
                    if "risk_level" in result:
                        result["risk_level"] = level_map.get(result["risk_level"], result["risk_level"])
                    if "session_id" not in result or not result["session_id"]:
                        result["session_id"] = session_id or "session-live"
                    return RiskScoreResponse(**result)
            except Exception as exc:
                logger.error("ML model inference failed (%s), falling back to heuristic.", exc)

        return self.fallback.predict(features, session_id=session_id)

# Singleton predictor instance
_active_predictor: RiskPredictor = MLRiskPredictor()

def get_risk_predictor() -> RiskPredictor:
    """Returns the current active risk predictor instance."""
    return _active_predictor

def set_risk_predictor(predictor: RiskPredictor) -> None:
    """Sets the active risk predictor (useful for testing or switching engines)."""
    global _active_predictor
    _active_predictor = predictor

def predict_risk(features: Dict[str, Any], session_id: str = "") -> RiskScoreResponse:
    """
    Clean interface for risk scoring:
    predict_risk(features) -> RiskScoreResponse
    """
    return get_risk_predictor().predict(features, session_id=session_id)

def evaluate_session_risk(session_id: str, events: List[Dict[str, Any]]) -> RiskScoreResponse:
    """
    High-level facade for end-to-end feature extraction and risk scoring:
    events -> extract_features -> predict_risk -> RiskScoreResponse
    """
    features = extract_features(events)
    return predict_risk(features, session_id=session_id)
