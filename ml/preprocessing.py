"""
GuardianAI - Preprocessing & Pipeline Utilities
===============================================
Handles data loading, validation, stratified splitting, feature scaling,
and artifact serialization.
"""

import os
import sys
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
import joblib

# Add project root to sys.path for direct script execution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.feature_engineering import (
    RAW_FEATURES,
    ALL_MODEL_FEATURES,
    compute_engineered_features,
    extract_features_from_dict
)

# Numeric continuous features that benefit from robust scaling
CONTINUOUS_FEATURES: List[str] = [
    "screen_share_duration",
    "transaction_amount",
    "app_switch_count",
    "session_duration",
    "time_between_events",
    "transaction_velocity",
    "navigation_back_count",
    "assistance_history",
    "screen_share_ratio",
    "log_transaction_amount",
    "app_switch_rate",
    "navigation_back_rate",
    "pacing_cadence_score",
    "assistance_trust_index",
    "coached_pressure_index"
]

# Discrete binary features (kept as is)
BINARY_FEATURES: List[str] = [
    "banking_app_opened",
    "new_beneficiary",
    "known_assistant",
    "first_time_assistance",
    "authentication_event",
    "untrusted_assistance",
    "coached_triad",
    "high_value_new_payee"
]


class PreprocessingPipeline:
    """
    GuardianAI Feature Preprocessing Pipeline.
    Manages robust scaling for continuous metrics while keeping binary indicators intact.
    """

    def __init__(self):
        self.scaler = RobustScaler()
        self.is_fitted = False
        self.feature_names = ALL_MODEL_FEATURES
        self.continuous_features = [f for f in CONTINUOUS_FEATURES if f in ALL_MODEL_FEATURES]
        self.binary_features = [f for f in BINARY_FEATURES if f in ALL_MODEL_FEATURES]

    def fit(self, X: pd.DataFrame) -> "PreprocessingPipeline":
        """Fits scaler on training set continuous features."""
        # Ensure all columns exist
        missing = [col for col in self.continuous_features if col not in X.columns]
        if missing:
            raise ValueError(f"Missing required continuous features: {missing}")

        self.scaler.fit(X[self.continuous_features])
        self.is_fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transforms features into scaled feature matrix matching ALL_MODEL_FEATURES order."""
        if not self.is_fitted:
            raise RuntimeError("PreprocessingPipeline must be fitted before transforming.")

        X_df = X.copy()
        # Scale continuous features
        scaled_cont = self.scaler.transform(X_df[self.continuous_features])
        scaled_cont_df = pd.DataFrame(scaled_cont, columns=self.continuous_features, index=X_df.index)

        # Merge with binary features
        transformed_df = pd.DataFrame(index=X_df.index)
        for col in self.feature_names:
            if col in self.continuous_features:
                transformed_df[col] = scaled_cont_df[col]
            else:
                transformed_df[col] = X_df[col].astype(float)

        return transformed_df.values

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """Fits and transforms feature DataFrame."""
        return self.fit(X).transform(X)

    def save(self, filepath: str) -> None:
        """Serializes pipeline state."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({
            "scaler": self.scaler,
            "is_fitted": self.is_fitted,
            "feature_names": self.feature_names,
            "continuous_features": self.continuous_features,
            "binary_features": self.binary_features
        }, filepath)

    @classmethod
    def load(cls, filepath: str) -> "PreprocessingPipeline":
        """Loads serialized pipeline state."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Pipeline artifact not found at: {filepath}")
        state = joblib.load(filepath)
        instance = cls()
        instance.scaler = state["scaler"]
        instance.is_fitted = state["is_fitted"]
        instance.feature_names = state["feature_names"]
        instance.continuous_features = state["continuous_features"]
        instance.binary_features = state["binary_features"]
        return instance


def load_dataset(csv_path: str) -> pd.DataFrame:
    """Loads CSV dataset and checks for required columns."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset file not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    
    # Check required raw features
    missing = [f for f in RAW_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Dataset missing required raw features: {missing}")

    # Remove any duplicate rows if present
    df = df.drop_duplicates().reset_index(drop=True)
    return df


def prepare_data_splits(
    df: pd.DataFrame,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    """
    Applies feature engineering and produces stratified Train, Validation, and Test splits.
    
    Returns:
    --------
    (X_train_df, X_val_df, X_test_df, y_train, y_val, y_test)
    """
    # 1. Feature Engineering
    df_engineered = compute_engineered_features(df)
    
    X = df_engineered[ALL_MODEL_FEATURES]
    y = df_engineered["label"].values

    # 2. First split: Train+Val vs Test
    X_train_val, X_test, y_train_val, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # 3. Second split: Train vs Val (relative proportion)
    val_relative = val_size / (1.0 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_val, y_train_val, test_size=val_relative, random_state=random_state, stratify=y_train_val
    )

    return (
        X_train.reset_index(drop=True),
        X_val.reset_index(drop=True),
        X_test.reset_index(drop=True),
        y_train,
        y_val,
        y_test
    )
