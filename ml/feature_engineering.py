"""
GuardianAI - Behavioural Feature Engineering Module
===================================================
Transforms raw telemetry and session aggregates into high-signal behavioural features
optimized for XGBoost tabular classification and real-time edge inference.
"""

from typing import List, Dict, Any, Union
import numpy as np
import pandas as pd

# List of input raw features expected in raw data
RAW_FEATURES: List[str] = [
    "screen_share_duration",
    "banking_app_opened",
    "new_beneficiary",
    "transaction_amount",
    "app_switch_count",
    "session_duration",
    "time_between_events",
    "known_assistant",
    "first_time_assistance",
    "transaction_velocity",
    "navigation_back_count",
    "authentication_event",
    "assistance_history"
]

# Engineered feature names added during transformation
ENGINEERED_FEATURE_NAMES: List[str] = [
    "screen_share_ratio",
    "untrusted_assistance",
    "coached_triad",
    "log_transaction_amount",
    "app_switch_rate",
    "navigation_back_rate",
    "pacing_cadence_score",
    "assistance_trust_index",
    "high_value_new_payee",
    "coached_pressure_index"
]

# Final complete feature set used by the ML model
ALL_MODEL_FEATURES: List[str] = RAW_FEATURES + ENGINEERED_FEATURE_NAMES


def compute_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes domain-specific interaction features from raw behavioural telemetry.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame containing all raw base features.

    Returns:
    --------
    pd.DataFrame:
        DataFrame enriched with engineered features.
    """
    df = df.copy()

    # 1. Screen share persistence ratio (percentage of session under remote visibility)
    df["screen_share_ratio"] = np.clip(
        df["screen_share_duration"] / (df["session_duration"] + 1e-5), 0.0, 1.0
    )

    # 2. Untrusted assistance flag (unfamiliar + first time remote connection)
    df["untrusted_assistance"] = (
        (1 - df["known_assistant"].astype(int)) * df["first_time_assistance"].astype(int)
    ).astype(float)

    # 3. Coached triad: screen sharing active + banking app active + new beneficiary added
    has_screen_share = (df["screen_share_duration"] > 0).astype(int)
    df["coached_triad"] = (
        has_screen_share * df["banking_app_opened"].astype(int) * df["new_beneficiary"].astype(int)
    ).astype(float)

    # 4. Log-transformed transaction amount for normality
    df["log_transaction_amount"] = np.log1p(np.maximum(df["transaction_amount"].astype(float), 0.0))

    # 5. App switch rate per minute (multitasking / OTP checking cadence)
    session_minutes = (df["session_duration"] / 60.0) + 0.1
    df["app_switch_rate"] = df["app_switch_count"] / session_minutes

    # 6. Navigation back rate per minute (hesitation / scammer dictation corrections)
    df["navigation_back_rate"] = df["navigation_back_count"] / session_minutes

    # 7. Pacing Cadence Score: ratio of inter-event spacing to total event density
    total_actions = df["app_switch_count"] + df["navigation_back_count"] + 1.0
    action_spacing = df["session_duration"] / total_actions
    df["pacing_cadence_score"] = df["time_between_events"] / (action_spacing + 1e-5)

    # 8. Assistance Trust Index: positive for verified frequent helpers, negative for unverified
    df["assistance_trust_index"] = (
        df["known_assistant"].astype(float) * np.log1p(df["assistance_history"].astype(float) + 1.0)
        - (df["first_time_assistance"].astype(float) * (1.0 - df["known_assistant"].astype(float)) * 2.0)
    )

    # 9. High-Value transfer with newly created beneficiary (>= ₹25,000 threshold)
    df["high_value_new_payee"] = (
        df["new_beneficiary"].astype(int) * (df["transaction_amount"] >= 25000.0).astype(int)
    ).astype(float)

    # 10. Coached Pressure Index: composite acceleration metric under remote dictation
    df["coached_pressure_index"] = (
        df["transaction_velocity"] * (df["app_switch_count"] + df["navigation_back_count"] + 1.0)
    ) / (df["time_between_events"] + 0.1)

    return df


def extract_features_from_dict(raw_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Parses a single dictionary of raw telemetry into a structured DataFrame
    with all required raw and engineered features.
    Fills missing values with sensible defaults.
    """
    defaults: Dict[str, Any] = {
        "screen_share_duration": 0.0,
        "banking_app_opened": 0,
        "new_beneficiary": 0,
        "transaction_amount": 0.0,
        "app_switch_count": 0,
        "session_duration": 60.0,
        "time_between_events": 3.0,
        "known_assistant": 0,
        "first_time_assistance": 0,
        "transaction_velocity": 0.1,
        "navigation_back_count": 0,
        "authentication_event": 1,
        "assistance_history": 0
    }

    cleaned: Dict[str, Any] = {}
    for feature in RAW_FEATURES:
        cleaned[feature] = raw_data.get(feature, defaults[feature])
        # Type coercion
        if feature in ["banking_app_opened", "new_beneficiary", "known_assistant", 
                        "first_time_assistance", "authentication_event", 
                        "app_switch_count", "navigation_back_count", "assistance_history"]:
            cleaned[feature] = int(cleaned[feature])
        else:
            cleaned[feature] = float(cleaned[feature])

    df = pd.DataFrame([cleaned])
    df_engineered = compute_engineered_features(df)
    return df_engineered[ALL_MODEL_FEATURES]


def get_all_feature_names() -> List[str]:
    """Returns list of all final model feature names."""
    return list(ALL_MODEL_FEATURES)
