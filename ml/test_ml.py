"""
GuardianAI - ML Pipeline Integration and Unit Tests
"""

import os
import pytest
import numpy as np
import pandas as pd

from ml.generate_data import generate_dataset, RAW_FEATURES, CLASS_MAP
from ml.feature_engineering import compute_engineered_features, extract_features_from_dict, ALL_MODEL_FEATURES
from ml.preprocessing import PreprocessingPipeline, prepare_data_splits
from ml.predict import predict_risk, GuardianRiskPredictor


def test_data_generation():
    """Validates data generator generates expected shape, columns, and realistic classes."""
    df = generate_dataset(n_samples=500, seed=123)
    assert len(df) == 500
    for col in RAW_FEATURES:
        assert col in df.columns
    assert set(df["label"].unique()) == {0, 1, 2}
    assert (df["transaction_amount"] >= 0).all()
    assert (df["session_duration"] > 0).all()


def test_feature_engineering():
    """Validates engineered features computation and dict extraction."""
    sample = {
        "screen_share_duration": 120.0,
        "banking_app_opened": 1,
        "new_beneficiary": 1,
        "transaction_amount": 50000.0,
        "app_switch_count": 5,
        "session_duration": 200.0,
        "time_between_events": 2.0,
        "known_assistant": 0,
        "first_time_assistance": 1,
        "transaction_velocity": 1.5,
        "navigation_back_count": 3,
        "authentication_event": 1,
        "assistance_history": 0
    }
    df = extract_features_from_dict(sample)
    assert df.shape == (1, len(ALL_MODEL_FEATURES))
    assert "screen_share_ratio" in df.columns
    assert "coached_triad" in df.columns
    assert df["coached_triad"].iloc[0] == 1.0
    assert df["untrusted_assistance"].iloc[0] == 1.0


def test_model_inference():
    """Validates that predict_risk produces expected schema and scores."""
    sample = {
        "screen_share_duration": 0.0,
        "banking_app_opened": 1,
        "new_beneficiary": 0,
        "transaction_amount": 1000.0,
        "app_switch_count": 0,
        "session_duration": 120.0,
        "time_between_events": 4.0,
        "known_assistant": 0,
        "first_time_assistance": 0,
        "transaction_velocity": 0.1,
        "navigation_back_count": 0,
        "authentication_event": 1,
        "assistance_history": 0
    }
    result = predict_risk(sample)
    assert "risk_score" in result
    assert "risk_level" in result
    assert "detected_signals" in result
    assert isinstance(result["risk_score"], (int, float))
    assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert isinstance(result["detected_signals"], list)
    assert len(result["detected_signals"]) > 0


def test_batch_inference():
    """Validates batch prediction handling."""
    samples = [
        {
            "screen_share_duration": 0.0,
            "banking_app_opened": 1,
            "new_beneficiary": 0,
            "transaction_amount": 500.0,
            "app_switch_count": 0,
            "session_duration": 60.0,
            "time_between_events": 3.0,
            "known_assistant": 0,
            "first_time_assistance": 0,
            "transaction_velocity": 0.1,
            "navigation_back_count": 0,
            "authentication_event": 1,
            "assistance_history": 0
        },
        {
            "screen_share_duration": 500.0,
            "banking_app_opened": 1,
            "new_beneficiary": 1,
            "transaction_amount": 150000.0,
            "app_switch_count": 10,
            "session_duration": 550.0,
            "time_between_events": 1.2,
            "known_assistant": 0,
            "first_time_assistance": 1,
            "transaction_velocity": 3.0,
            "navigation_back_count": 6,
            "authentication_event": 1,
            "assistance_history": 0
        }
    ]
    results = predict_risk(samples)
    assert len(results) == 2
    assert results[0]["risk_level"] == "LOW"
    assert results[1]["risk_level"] == "HIGH"
