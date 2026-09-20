"""
GuardianAI - Real-Time Risk Prediction Interface
================================================
Exposes lightweight, zero-retraining inference for FastAPI backend and edge monitors.

Provides:
  - predict_risk(features: Dict[str, Any]) -> Dict[str, Any]
"""

import os
import sys
from typing import Dict, Any, List, Union, Optional
import numpy as np
import pandas as pd
import xgboost as xgb

# Add project root to sys.path for direct script execution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from datetime import datetime, timezone
from ml.feature_engineering import (
    RAW_FEATURES,
    ALL_MODEL_FEATURES,
    extract_features_from_dict
)
from ml.preprocessing import PreprocessingPipeline
from ml.explainability import explain_prediction
from ml.human_explanation import generate_human_explanation


class GuardianRiskPredictor:
    """
    Singleton / Cached Inference Engine for GuardianAI.
    Loads trained XGBoost model and preprocessor once into memory for sub-millisecond execution.
    """
    _instance: Optional["GuardianRiskPredictor"] = None

    def __init__(self, model_dir: Optional[str] = None):
        if model_dir is None:
            # Default to ml/models relative to project root or current module
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_dir = os.path.join(base_dir, "models")

        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, "xgboost_model.json")
        self.preprocessor_path = os.path.join(model_dir, "preprocessor.joblib")

        self.model: Optional[xgb.XGBClassifier] = None
        self.preprocessor: Optional[PreprocessingPipeline] = None
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Loads serialized model and preprocessing state from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Model weights not found at {self.model_path}. "
                "Please run `python ml/train.py` first."
            )
        if not os.path.exists(self.preprocessor_path):
            raise FileNotFoundError(
                f"Preprocessor not found at {self.preprocessor_path}. "
                "Please run `python ml/train.py` first."
            )

        # Load XGBoost model
        self.model = xgb.XGBClassifier()
        self.model.load_model(self.model_path)

        # Load Preprocessing pipeline
        self.preprocessor = PreprocessingPipeline.load(self.preprocessor_path)

    @classmethod
    def get_instance(cls, model_dir: Optional[str] = None) -> "GuardianRiskPredictor":
        """Returns or initializes singleton predictor instance."""
        if cls._instance is None:
            cls._instance = cls(model_dir=model_dir)
        return cls._instance

    def _extract_detected_signals(self, raw_features: Dict[str, Any], probs: np.ndarray) -> List[str]:
        """
        Generates explainable, human-readable security signals and threat indicators
        based on active behavioural telemetry and model risk factors.
        """
        signals: List[str] = []

        screen_share = float(raw_features.get("screen_share_duration", 0.0))
        banking_app = int(raw_features.get("banking_app_opened", 0))
        new_payee = int(raw_features.get("new_beneficiary", 0))
        amount = float(raw_features.get("transaction_amount", 0.0))
        known_helper = int(raw_features.get("known_assistant", 0))
        first_time = int(raw_features.get("first_time_assistance", 0))
        app_switches = int(raw_features.get("app_switch_count", 0))
        time_spacing = float(raw_features.get("time_between_events", 3.0))
        back_count = int(raw_features.get("navigation_back_count", 0))
        history = int(raw_features.get("assistance_history", 0))

        # Signal 1: Active Remote Screen Sharing
        if screen_share > 0:
            if screen_share >= 120:
                signals.append(f"Extended remote screen mirroring active ({screen_share:.0f}s duration)")
            else:
                signals.append(f"Remote screen sharing detected ({screen_share:.0f}s)")

        # Signal 2: Screen Sharing with Banking App
        if screen_share > 0 and banking_app:
            signals.append("Banking application accessed during active remote screen sharing session")

        # Signal 3: Untrusted / Unfamiliar Remote Assistant
        if screen_share > 0 and not known_helper and first_time:
            signals.append("Remote assistance initiated by unverified / first-time external identity")
        elif screen_share > 0 and known_helper:
            signals.append(f"Remote assistant is verified contact (historical safe sessions: {history})")

        # Signal 4: Newly Added Beneficiary
        if new_payee:
            if amount >= 25000:
                signals.append(f"High-value transfer (INR {amount:,.0f}) initiated to newly created payee")
            else:
                signals.append(f"Transfer initiated to recently added beneficiary (INR {amount:,.0f})")
        elif amount >= 50000:
            signals.append(f"Elevated transfer amount (INR {amount:,.0f}) exceeding standard baseline")

        # Signal 5: Rapid App Switching / OTP Exposure
        if app_switches >= 6:
            signals.append(f"Elevated app switching cadence ({app_switches} switches, potential OTP/credential sharing)")
        elif app_switches >= 3:
            signals.append(f"Moderate multitasking across background apps ({app_switches} switches)")

        # Signal 6: Dictated Pacing & Pressure Telemetry
        if time_spacing <= 1.8 and app_switches >= 4:
            signals.append("Rapid action cadence matching scripted voice-coaching guidance")
        elif back_count >= 4:
            signals.append(f"Abnormal navigation reversal count ({back_count} back navigations, hesitation marker)")

        # Default fallback signal if clean
        if not signals:
            signals.append("Behavioural telemetry conforms to safe baseline profile")

        return signals

    def predict_one(self, raw_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes real-time inference on a single session's feature dictionary.
        """
        # 1. Feature Engineering
        features_df = extract_features_from_dict(raw_features)

        # 2. Preprocessing
        features_scaled = self.preprocessor.transform(features_df)

        # 3. Model Inference (Probabilities)
        probs = self.model.predict_proba(features_scaled)[0] # [p_legit, p_suspicious, p_scam]
        p_legit = float(probs[0])
        p_suspicious = float(probs[1])
        p_scam = float(probs[2])

        # 4. Calibrated Risk Score (0.0 to 100.0)
        # Weighted risk contribution: suspicious has 50% weight, scam has 100% weight
        raw_risk_score = (p_suspicious * 50.0) + (p_scam * 100.0)
        risk_score = round(min(max(raw_risk_score, 0.0), 100.0), 1)

        # 5. Risk Level Categorization
        if risk_score >= 70.0:
            risk_level = "HIGH"
            predicted_class = "COACHED_SCAM"
        elif risk_score >= 30.0:
            risk_level = "MEDIUM"
            predicted_class = "SUSPICIOUS"
        else:
            risk_level = "LOW"
            predicted_class = "LEGITIMATE"

        # 6. Extract Threat Signals
        detected_signals = self._extract_detected_signals(raw_features, probs)

        # 7. Compute SHAP-based Explainability
        try:
            shap_explanation = explain_prediction(raw_features, risk_score=risk_score)
        except Exception as exc:
            shap_explanation = {"error": f"SHAP calculation unavailable: {exc}"}

        # 8. Compute Human-Friendly Plain-Language Explanation
        try:
            tech_signals = []
            if isinstance(shap_explanation, dict) and "top_signals" in shap_explanation:
                tech_signals = [s["signal"] for s in shap_explanation["top_signals"]]
            if not tech_signals:
                tech_signals = [s.lower() for s in detected_signals]

            human_explanation = generate_human_explanation(tech_signals, context=raw_features)
        except Exception as exc:
            human_explanation = {
                "headline": "Potential risk detected during session.",
                "key_observations": detected_signals,
                "recommended_action": "Verify the recipient and caller identity.",
                "provider_type": "FALLBACK"
            }

        # 9. Format structured risk factors
        risk_factors = []
        if isinstance(shap_explanation, dict) and "top_signals" in shap_explanation:
            for s in shap_explanation["top_signals"]:
                pts = s.get("impact_points", 0)
                if pts > 0:
                    risk_factors.append({
                        "name": s["display_name"],
                        "severity": "CRITICAL" if pts >= 25 else ("HIGH" if pts >= 15 else ("MEDIUM" if pts >= 8 else "LOW")),
                        "description": s.get("description", s["display_name"]),
                        "weight": float(pts)
                    })

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "predicted_class": predicted_class,
            "class_probabilities": {
                "LEGITIMATE": round(p_legit, 4),
                "SUSPICIOUS": round(p_suspicious, 4),
                "COACHED_SCAM": round(p_scam, 4)
            },
            "detected_signals": detected_signals,
            "reasons": detected_signals,
            "risk_factors": risk_factors,
            "recommended_action": "INTERVENE" if risk_score >= 70.0 else ("MONITOR" if risk_score >= 30.0 else "NONE"),
            "evaluated_at": datetime.now(timezone.utc),
            "shap_explanation": shap_explanation,
            "human_explanation": human_explanation
        }


def predict_risk(
    features: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
    session_id: str = ""
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Main clean interface for risk prediction with built-in SHAP & human explanations.
    Accepts raw feature dictionary (or list of dicts) and returns formatted risk assessments.
    """
    predictor = GuardianRiskPredictor.get_instance()

    if isinstance(features, dict):
        # If this is a Phase 1 heuristic feature dictionary (lacking ML raw telemetry features like screen_share_duration)
        # raise ValueError so MLRiskPredictor falls back gracefully to HeuristicRiskPredictor without breaking Phase 1.
        if ("banking_under_screen_share" in features or "screen_sharing_active" in features) and (
            "screen_share_duration" not in features and "session_duration" not in features
        ):
            raise ValueError(
                "Input features conform to Phase 1 heuristic schema; fallback to HeuristicRiskPredictor required."
            )

        res = predictor.predict_one(features)
        if session_id:
            res["session_id"] = session_id
        return res
    elif isinstance(features, list):
        return [predictor.predict_one(f) for f in features]
    elif isinstance(features, pd.DataFrame):
        records = features.to_dict(orient="records")
        return [predictor.predict_one(r) for r in records]
    else:
        raise TypeError(f"Unsupported features type: {type(features)}. Expected Dict or List[Dict].")


if __name__ == "__main__":
    print("[*] Testing GuardianAI Risk Predictor...\n")

    # Test Case 1: Standard Legitimate User
    legit_test = {
        "screen_share_duration": 0.0,
        "banking_app_opened": 1,
        "new_beneficiary": 0,
        "transaction_amount": 1200.0,
        "app_switch_count": 1,
        "session_duration": 180.0,
        "time_between_events": 3.8,
        "known_assistant": 0,
        "first_time_assistance": 0,
        "transaction_velocity": 0.1,
        "navigation_back_count": 1,
        "authentication_event": 1,
        "assistance_history": 0
    }
    res1 = predict_risk(legit_test)
    print("Test 1 (Legitimate Solo Banking):")
    print(f"Risk Score : {res1['risk_score']} | Risk Level: {res1['risk_level']}")
    print(f"Signals    : {res1['detected_signals']}")
    print(f"Probabilities: {res1['class_probabilities']}\n")

    # Test Case 2: Legitimate Family Assisted Banking
    family_test = {
        "screen_share_duration": 250.0,
        "banking_app_opened": 1,
        "new_beneficiary": 1,
        "transaction_amount": 35000.0,
        "app_switch_count": 2,
        "session_duration": 300.0,
        "time_between_events": 4.5,
        "known_assistant": 1,
        "first_time_assistance": 0,
        "transaction_velocity": 0.2,
        "navigation_back_count": 1,
        "authentication_event": 1,
        "assistance_history": 6
    }
    res2 = predict_risk(family_test)
    print("Test 2 (Legitimate Family Assistance):")
    print(f"Risk Score : {res2['risk_score']} | Risk Level: {res2['risk_level']}")
    print(f"Signals    : {res2['detected_signals']}")
    print(f"Probabilities: {res2['class_probabilities']}\n")

    # Test Case 3: Active Coached Scam
    scam_test = {
        "screen_share_duration": 480.0,
        "banking_app_opened": 1,
        "new_beneficiary": 1,
        "transaction_amount": 95000.0,
        "app_switch_count": 9,
        "session_duration": 520.0,
        "time_between_events": 1.4,
        "known_assistant": 0,
        "first_time_assistance": 1,
        "transaction_velocity": 2.8,
        "navigation_back_count": 7,
        "authentication_event": 1,
        "assistance_history": 0
    }
    res3 = predict_risk(scam_test)
    print("Test 3 (Active Coached Scam):")
    print(f"Risk Score : {res3['risk_score']} | Risk Level: {res3['risk_level']}")
    print(f"Signals    : {res3['detected_signals']}")
    print(f"Probabilities: {res3['class_probabilities']}\n")
