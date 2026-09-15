"""
GuardianAI - Model Evaluation Module
====================================
Computes comprehensive evaluation metrics on held-out test data:
  - Accuracy
  - Precision (Macro, Weighted, Per-Class)
  - Recall (Macro, Weighted, Per-Class)
  - F1-Score (Macro, Weighted, Per-Class)
  - Multi-class Confusion Matrix
  - False Positive Rate (FPR) across individual and combined risk classes
  - ROC-AUC (One-vs-Rest)
Saves results to ml/models/evaluation_results.json.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score
)

# Add project root to sys.path for direct script execution
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.generate_data import CLASS_MAP
from ml.preprocessing import (
    load_dataset,
    prepare_data_splits,
    PreprocessingPipeline
)


def compute_false_positive_rates(cm: np.ndarray, class_names: list) -> Dict[str, float]:
    """
    Calculates False Positive Rate (FPR = FP / (FP + TN)) for each class
    in a One-vs-Rest formulation.
    """
    fpr_dict = {}
    total_samples = np.sum(cm)

    for i, name in enumerate(class_names):
        tp = cm[i, i]
        fn = np.sum(cm[i, :]) - tp
        fp = np.sum(cm[:, i]) - tp
        tn = total_samples - (tp + fn + fp)

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fpr_dict[f"fpr_{name.lower()}"] = round(float(fpr), 5)

    # Specific Security Metric: Legitimate Users falsely flagged as Risk (Suspicious or Scam)
    # Legitimate is Class 0
    legit_total = np.sum(cm[0, :])
    legit_false_alarms = np.sum(cm[0, 1:]) # Flagged as Class 1 or Class 2
    fpr_security_alarm = legit_false_alarms / legit_total if legit_total > 0 else 0.0
    fpr_dict["fpr_legitimate_false_alarm_rate"] = round(float(fpr_security_alarm), 5)

    return fpr_dict


def evaluate_model(
    model_dir: str = "ml/models",
    data_path: str = "data/synthetic_behavioural_data.csv",
    output_json: str = "ml/models/evaluation_results.json"
) -> Dict[str, Any]:
    """
    Evaluates the trained model against the held-out test dataset.
    """
    model_path = os.path.join(model_dir, "xgboost_model.json")
    preprocessor_path = os.path.join(model_dir, "preprocessor.joblib")
    test_npz_path = os.path.join(model_dir, "test_data.npz")

    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        raise FileNotFoundError(f"Model artifacts not found in {model_dir}. Please run train.py first.")

    # 1. Load Model
    model = xgb.XGBClassifier()
    model.load_model(model_path)

    # 2. Load Test Partition (or re-split deterministically if npz missing)
    if os.path.exists(test_npz_path):
        data = np.load(test_npz_path)
        X_test_scaled = data["X_test_scaled"]
        y_test = data["y_test"]
    else:
        df = load_dataset(data_path)
        _, _, X_test_df, _, _, y_test = prepare_data_splits(df, test_size=0.15, val_size=0.15, random_state=42)
        preprocessor = PreprocessingPipeline.load(preprocessor_path)
        X_test_scaled = preprocessor.transform(X_test_df)

    # 3. Model Predictions & Probability Outputs
    y_pred = model.predict(X_test_scaled)
    y_probs = model.predict_proba(X_test_scaled)

    class_names = [CLASS_MAP[i] for i in sorted(CLASS_MAP.keys())]

    # 4. Core Metrics
    accuracy = float(accuracy_score(y_test, y_pred))
    precision_macro = float(precision_score(y_test, y_pred, average="macro"))
    precision_weighted = float(precision_score(y_test, y_pred, average="weighted"))
    recall_macro = float(recall_score(y_test, y_pred, average="macro"))
    recall_weighted = float(recall_score(y_test, y_pred, average="weighted"))
    f1_macro = float(f1_score(y_test, y_pred, average="macro"))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted"))

    # Per-Class Metrics
    precision_per_class = precision_score(y_test, y_pred, average=None)
    recall_per_class = recall_score(y_test, y_pred, average=None)
    f1_per_class = f1_score(y_test, y_pred, average=None)

    # Multi-class ROC-AUC (One-vs-Rest)
    try:
        roc_auc_ovr_macro = float(roc_auc_score(y_test, y_probs, multi_class="ovr", average="macro"))
        roc_auc_ovr_weighted = float(roc_auc_score(y_test, y_probs, multi_class="ovr", average="weighted"))
    except Exception:
        roc_auc_ovr_macro = None
        roc_auc_ovr_weighted = None

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    fpr_metrics = compute_false_positive_rates(cm, class_names)

    # Structure Report
    results: Dict[str, Any] = {
        "evaluation_dataset_size": int(len(y_test)),
        "metrics": {
            "accuracy": round(accuracy, 5),
            "precision_macro": round(precision_macro, 5),
            "precision_weighted": round(precision_weighted, 5),
            "recall_macro": round(recall_macro, 5),
            "recall_weighted": round(recall_weighted, 5),
            "f1_macro": round(f1_macro, 5),
            "f1_weighted": round(f1_weighted, 5),
            "roc_auc_macro": round(roc_auc_ovr_macro, 5) if roc_auc_ovr_macro else None,
            "roc_auc_weighted": round(roc_auc_ovr_weighted, 5) if roc_auc_ovr_weighted else None
        },
        "per_class_metrics": {
            class_names[i]: {
                "precision": round(float(precision_per_class[i]), 5),
                "recall": round(float(recall_per_class[i]), 5),
                "f1_score": round(float(f1_per_class[i]), 5),
                "sample_count": int(np.sum(y_test == i))
            }
            for i in range(len(class_names))
        },
        "false_positive_rates": fpr_metrics,
        "confusion_matrix": {
            "matrix": cm.tolist(),
            "labels": class_names
        }
    }

    # Print Formatted Evaluation Summary
    print("\n" + "="*65)
    print("        GUARDIAN-AI MODEL EVALUATION PERFORMANCE SUMMARY")
    print("="*65)
    print(f"Total Held-Out Test Samples : {len(y_test):,}")
    print(f"Overall Accuracy            : {accuracy * 100:.2f}%")
    print(f"Weighted Precision          : {precision_weighted * 100:.2f}%")
    print(f"Weighted Recall             : {recall_weighted * 100:.2f}%")
    print(f"Weighted F1-Score           : {f1_weighted * 100:.2f}%")
    if roc_auc_ovr_macro:
        print(f"Multi-class ROC-AUC (OvR)   : {roc_auc_ovr_macro:.4f}")
    print(f"Legitimate False Alarm Rate : {fpr_metrics['fpr_legitimate_false_alarm_rate'] * 100:.2f}%")
    
    print("\n[+] Per-Class Breakdown:")
    print(f"{'Class':<16} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<8}")
    print("-" * 60)
    for name in class_names:
        stats = results["per_class_metrics"][name]
        print(f"{name:<16} {stats['precision']*100:>6.2f}%     {stats['recall']*100:>6.2f}%     {stats['f1_score']*100:>6.2f}%     {stats['sample_count']:>7,}")

    print("\n[+] Confusion Matrix:")
    print(f"{'Actual \\ Predicted':<20} " + " ".join([f"{name:>14}" for name in class_names]))
    for i, row_name in enumerate(class_names):
        row_str = " ".join([f"{cm[i, j]:>14,}" for j in range(len(class_names))])
        print(f"{row_name:<20} {row_str}")

    print("="*65)

    # Save to JSON
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Detailed evaluation metrics saved to: {output_json}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Evaluate GuardianAI Behavioural Classifier")
    parser.add_argument("--model-dir", type=str, default="ml/models", help="Directory containing model artifacts")
    parser.add_argument("--data", type=str, default="data/synthetic_behavioural_data.csv", help="Dataset path")
    parser.add_argument("--output", type=str, default="ml/models/evaluation_results.json", help="Output JSON path")
    args = parser.parse_args()

    evaluate_model(model_dir=args.model_dir, data_path=args.data, output_json=args.output)


if __name__ == "__main__":
    main()
