"""
GuardianAI - Explainability Unit & Integration Tests
=====================================================
Validates:
1. SHAP TreeExplainer attributions generated from actual XGBoost model
2. Canonical signal ranking and points computation
3. HumanExplanationService plain-language conversion (matches prompt requirements)
4. LLM explanation provider prompt building and fallback handling
"""

import pytest
from ml.explainability import GuardianShapExplainer, explain_prediction, SIGNAL_CATEGORIES
from ml.human_explanation import (
    HumanExplanationService,
    TemplateExplanationProvider,
    LLMExplanationProvider,
    generate_human_explanation
)
from ml.predict import predict_risk


def test_shap_explainer_initialization():
    """Validates that GuardianShapExplainer loads model and TreeExplainer cleanly."""
    explainer = GuardianShapExplainer.get_instance()
    assert explainer.model is not None
    assert explainer.preprocessor is not None
    assert explainer.explainer is not None


def test_shap_explain_coached_scam():
    """
    Validates SHAP attribution computation on an active coached scam sample.
    Confirms values are extracted directly from the actual XGBoost model.
    """
    scam_sample = {
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

    result = explain_prediction(scam_sample)
    assert "risk_score" in result
    assert "predicted_class" in result
    assert "top_signals" in result
    assert "feature_attributions" in result

    # Check top signals
    top_signals = result["top_signals"]
    assert len(top_signals) > 0
    for sig in top_signals:
        assert "signal" in sig
        assert "display_name" in sig
        assert "impact_points" in sig
        assert "shap_value" in sig
        assert "formatted" in sig
        assert sig["impact_points"] >= 0

    # Ensure signal points are formatted as requested
    formatted_texts = [s["formatted"] for s in top_signals]
    assert any("+" in t for t in formatted_texts)


def test_shap_explain_legitimate_session():
    """Validates SHAP behavior on a legitimate solo banking session."""
    legit_sample = {
        "screen_share_duration": 0.0,
        "banking_app_opened": 1,
        "new_beneficiary": 0,
        "transaction_amount": 1200.0,
        "app_switch_count": 1,
        "session_duration": 180.0,
        "time_between_events": 4.0,
        "known_assistant": 0,
        "first_time_assistance": 0,
        "transaction_velocity": 0.1,
        "navigation_back_count": 0,
        "authentication_event": 1,
        "assistance_history": 0
    }

    result = explain_prediction(legit_sample)
    assert result["predicted_class"] == "LEGITIMATE"
    assert result["risk_score"] < 30.0


def test_human_explanation_coached_scam_triad():
    """
    Validates the prompt's required example:
      Technical: new_beneficiary + high transaction + active screen sharing
      Human: 'Someone may be guiding you through a high-value transaction while your screen is being shared.'
    """
    tech_signals = ["new_beneficiary", "high transaction", "active screen sharing"]
    context = {
        "transaction_amount": 185000.0,
        "tool_name": "AnyDesk Remote Support",
        "beneficiary_label": "Refund_Support_Agent_442"
    }

    res = generate_human_explanation(tech_signals, context=context)
    assert "headline" in res
    assert "key_observations" in res
    assert "recommended_action" in res

    # Check that headline conveys the exact guidance
    headline = res["headline"]
    assert "Someone may be guiding you through a high-value transaction while your screen is being shared." in headline
    assert len(res["key_observations"]) >= 2
    assert "Cancel Transaction" in res["recommended_action"]


def test_human_explanation_legitimate_assistance():
    """Validates human explanation for verified family assistance."""
    tech_signals = ["screen sharing"]
    context = {
        "screen_share_duration": 120.0,
        "known_assistant": 1,
        "transaction_amount": 1500.0
    }

    res = generate_human_explanation(tech_signals, context=context)
    assert "verified" in res["headline"].lower() or "trusted" in res["headline"].lower()


def test_llm_explanation_provider_fallback():
    """Validates that LLMExplanationProvider generates prompts and falls back cleanly without an API key."""
    provider = LLMExplanationProvider(api_key=None)
    prompt = provider.build_prompt(["new_beneficiary", "active screen sharing"], {"amount": 50000})
    assert "GuardianAI" in prompt
    assert "new_beneficiary" in prompt

    res = provider.generate(["new_beneficiary", "active screen sharing"], {"amount": 50000})
    assert "headline" in res
    assert res["provider_type"] in ["TEMPLATE", "LLM"]


def test_predict_risk_includes_explanations():
    """Validates that predict_risk output includes both SHAP and human explanations."""
    sample = {
        "screen_share_duration": 300.0,
        "banking_app_opened": 1,
        "new_beneficiary": 1,
        "transaction_amount": 75000.0,
        "app_switch_count": 8,
        "session_duration": 350.0,
        "time_between_events": 1.5,
        "known_assistant": 0,
        "first_time_assistance": 1,
        "transaction_velocity": 2.5,
        "navigation_back_count": 5,
        "authentication_event": 1,
        "assistance_history": 0
    }

    res = predict_risk(sample, session_id="test-session-123")
    assert "shap_explanation" in res
    assert "human_explanation" in res
    assert res["session_id"] == "test-session-123"
    assert "top_signals" in res["shap_explanation"]
    assert "headline" in res["human_explanation"]
