"""
GuardianAI - Model Training Pipeline (XGBoost Classifier)
=========================================================
Trains a multi-class XGBoost classifier on behavioural telemetry to detect:
  - Class 0: LEGITIMATE
  - Class 1: SUSPICIOUS
  - Class 2: COACHED_SCAM

Saves trained model artifacts, preprocessor state, and metadata to ml/models/.
"""

import argparse
import json
import os
import sys
import time
from typing import Dict, Any
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score, log_loss

# Add project root to sys.path for direct script execution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.generate_data import CLASS_MAP
from ml.feature_engineering import ALL_MODEL_FEATURES
from ml.preprocessing import (
    load_dataset,
    prepare_data_splits,
    PreprocessingPipeline
)


def train_model(
    data_path: str = "data/synthetic_behavioural_data.csv",
    output_dir: str = "ml/models",
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Executes end-to-end model training workflow:
    1. Loads dataset
    2. Generates stratified train/validation/test splits
    3. Fits feature scaling pipeline
    4. Trains multi-class XGBoost classifier with early stopping
    5. Saves all serialized model artifacts and metadata
    """
    os.makedirs(output_dir, exist_ok=True)
    start_time = time.time()

    print(f"[*] Loading dataset from: {data_path}")
    df = load_dataset(data_path)
    print(f"[+] Loaded {len(df):,} total records.")

    # 1. Stratified Splits (70% Train, 15% Val, 15% Test)
    print("[*] Preparing feature engineering and stratified splits...")
    X_train_df, X_val_df, X_test_df, y_train, y_val, y_test = prepare_data_splits(
        df, test_size=0.15, val_size=0.15, random_state=random_state
    )

    print(f"    - Training samples   : {len(X_train_df):,}")
    print(f"    - Validation samples : {len(X_val_df):,}")
    print(f"    - Testing samples    : {len(X_test_df):,}")

    # 2. Fit Preprocessor
    print("[*] Fitting preprocessing pipeline...")
    preprocessor = PreprocessingPipeline()
    X_train_scaled = preprocessor.fit_transform(X_train_df)
    X_val_scaled = preprocessor.transform(X_val_df)
    X_test_scaled = preprocessor.transform(X_test_df)

    # 3. Model Training
    print("[*] Training XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=350,
        max_depth=5,
        learning_rate=0.04,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_weight=2,
        gamma=0.1,
        reg_alpha=0.05,
        reg_lambda=1.0,
        objective="multi:softprob",
        num_class=3,
        eval_metric=["mlogloss", "merror"],
        early_stopping_rounds=30,
        random_state=random_state,
        n_jobs=-1
    )

    model.fit(
        X_train_scaled,
        y_train,
        eval_set=[(X_train_scaled, y_train), (X_val_scaled, y_val)],
        verbose=50
    )

    training_duration = round(time.time() - start_time, 2)
    print(f"[+] Model training completed in {training_duration}s (Best iteration: {model.best_iteration})")

    # 4. Validation Metrics
    y_val_pred = model.predict(X_val_scaled)
    y_val_probs = model.predict_proba(X_val_scaled)
    
    val_acc = accuracy_score(y_val, y_val_pred)
    val_f1 = f1_score(y_val, y_val_pred, average="weighted")
    val_loss = log_loss(y_val, y_val_probs)

    print(f"[+] Validation Performance:")
    print(f"    - Accuracy : {val_acc:.4f}")
    print(f"    - F1-Score : {val_f1:.4f}")
    print(f"    - Log-Loss : {val_loss:.4f}")

    # 5. Feature Importances
    importances = model.feature_importances_
    feat_imp = sorted(zip(ALL_MODEL_FEATURES, importances), key=lambda x: x[1], reverse=True)
    print("\n[+] Top 10 High-Signal Behavioural Features:")
    for feat, imp in feat_imp[:10]:
        print(f"    - {feat:<28}: {imp*100:.2f}%")

    # 6. Save Artifacts
    model_json_path = os.path.join(output_dir, "xgboost_model.json")
    preprocessor_path = os.path.join(output_dir, "preprocessor.joblib")
    metadata_path = os.path.join(output_dir, "pipeline_metadata.json")

    # Save XGBoost native model
    model.save_model(model_json_path)
    print(f"[+] Saved XGBoost model artifact to: {model_json_path}")

    # Save Preprocessor
    preprocessor.save(preprocessor_path)
    print(f"[+] Saved Preprocessor artifact to: {preprocessor_path}")

    # Save Metadata
    metadata = {
        "model_type": "XGBClassifier",
        "xgb_version": xgb.__version__,
        "num_classes": 3,
        "class_mapping": CLASS_MAP,
        "feature_names": ALL_MODEL_FEATURES,
        "top_features": [{feat: float(imp)} for feat, imp in feat_imp],
        "training_duration_sec": training_duration,
        "best_iteration": int(model.best_iteration),
        "validation_metrics": {
            "accuracy": round(float(val_acc), 4),
            "f1_score_weighted": round(float(val_f1), 4),
            "log_loss": round(float(val_loss), 4)
        },
        "thresholds": {
            "low_risk_max": 30.0,
            "medium_risk_max": 70.0,
            "high_risk_min": 70.0
        }
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"[+] Saved pipeline metadata to: {metadata_path}")

    # Save test set for clean standalone evaluation in ml/evaluate.py
    test_set_path = os.path.join(output_dir, "test_data.npz")
    np.savez_compressed(
        test_set_path,
        X_test_scaled=X_test_scaled,
        y_test=y_test
    )
    print(f"[+] Saved test partition for standalone evaluation: {test_set_path}")

    return metadata


def main():
    parser = argparse.ArgumentParser(description="Train GuardianAI Behavioural Classifier")
    parser.add_argument("--data", type=str, default="data/synthetic_behavioural_data.csv", help="Dataset path")
    parser.add_argument("--output-dir", type=str, default="ml/models", help="Directory to save models")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    train_model(data_path=args.data, output_dir=args.output_dir, random_state=args.seed)


if __name__ == "__main__":
    main()
