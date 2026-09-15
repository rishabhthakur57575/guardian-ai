# GuardianAI - Behavioural Machine Learning Subsystem

GuardianAI's Machine Learning subsystem is an on-device, real-time behavioural anomaly detection engine designed to identify **remote-access screen-sharing scams and voice-coached financial fraud** while preserving frictionless experiences for legitimate users and safe remote assistance workflows (e.g., family tech support, video KYC, and enterprise IT helpdesk).

---

## 1. System Architecture

```
                                +-----------------------------------+
                                | Raw Telemetry / Session Events    |
                                +-----------------+-----------------+
                                                  |
                                                  v
                                +-----------------+-----------------+
                                | ml/feature_engineering.py         |
                                | (Domain-Specific Indicators)      |
                                +-----------------+-----------------+
                                                  |
                                                  v
                                +-----------------+-----------------+
                                | ml/preprocessing.py               |
                                | (RobustScaler + Feature Alignment)|
                                +-----------------+-----------------+
                                                  |
                                                  v
                                +-----------------+-----------------+
                                | ml/predict.py (XGBoost Engine)    |
                                | (Singleton Cached Predictor)      |
                                +-----------------+-----------------+
                                                  |
                     +----------------------------+----------------------------+
                     |                                                         |
                     v                                                         v
          Risk Score (0.0 - 100.0)                                Threat Signals & Explainability
          Risk Level: LOW / MEDIUM / HIGH                         ["Active remote screen mirroring...",
          Class Probs: {LEGIT, SUSP, SCAM}                         "Unverified remote assistant..."]
```

---

## 2. Dataset Specification

- **Total Samples**: 25,000 synthetic behavioural telemetry records
- **Class Breakdown**:
  - `0 = LEGITIMATE`: 13,547 samples (54.19%) — includes solo mobile banking, legitimate family tech assistance with screen sharing, elderly deliberation, and video KYC.
  - `1 = SUSPICIOUS`: 5,237 samples (20.95%) — borderline cases, high app switching, unverified helpers with low amounts, high hesitation.
  - `2 = COACHED_SCAM`: 6,216 samples (24.86%) — voice-guided remote access fraud, AnyDesk/TeamViewer screen mirroring, rapid dictated app switching, unverified helpers, new beneficiary additions.
- **Realistic Overlap & Noise**: A 3.5% boundary noise rate was injected to prevent simplistic deterministic shortcuts (e.g., legitimate users legitimately use screen sharing with verified contacts or transfer high amounts, while scammers occasionally test with micro-amounts).

### Input Features:
| Feature | Type | Description |
|---|---|---|
| `screen_share_duration` | `float` (seconds) | Cumulative duration of active remote screen mirroring |
| `banking_app_opened` | `binary` (0/1) | Whether a protected financial app was accessed |
| `new_beneficiary` | `binary` (0/1) | Whether a new payee/beneficiary was created during session |
| `transaction_amount` | `float` (INR) | Financial transaction value initiated during session |
| `app_switch_count` | `int` | Number of foreground app transitions (e.g. Bank <-> WhatsApp/SMS) |
| `session_duration` | `float` (seconds) | Total continuous telemetry recording duration |
| `time_between_events` | `float` (seconds) | Average time delta between user interaction events |
| `known_assistant` | `binary` (0/1) | Flag indicating if remote assistant is a verified safe contact |
| `first_time_assistance` | `binary` (0/1) | Flag indicating whether this is the first session with assistant |
| `transaction_velocity` | `float` | Rate of transaction progression per unit time |
| `navigation_back_count`| `int` | Count of navigation back button taps (hesitation indicator) |
| `authentication_event` | `binary` (0/1) | Biometric/PIN authentication triggered during workflow |
| `assistance_history` | `int` | Historical count of completed safe assisted sessions |

### Domain Engineered Features:
1. `screen_share_ratio`: Proportion of total session duration spent mirroring screen.
2. `untrusted_assistance`: Product of `(1 - known_assistant) * first_time_assistance`.
3. `coached_triad`: Concurrency indicator `(screen_share > 0) * banking_app_opened * new_beneficiary`.
4. `log_transaction_amount`: $\ln(1 + \text{transaction\_amount})$ for variance stabilization.
5. `app_switch_rate`: Normalized app switching frequency per minute.
6. `navigation_back_rate`: Hesitation reversal rate per minute.
7. `pacing_cadence_score`: Action spacing relative to overall session pacing density.
8. `assistance_trust_index`: Trust score weighting historical sessions against unverified access.
9. `high_value_new_payee`: Indicator for new payee transfers $\ge \text{INR } 25,000$.
10. `coached_pressure_index`: Composite acceleration index measuring rushed dictation pacing.

---

## 3. Measured Model Performance

The XGBoost multi-class classifier was evaluated on a strictly held-out test split ($N = 3,750$ records, 15% stratified test partition).

### Overall Metrics:
- **Test Accuracy**: **97.68%**
- **Weighted Precision**: **97.67%**
- **Weighted Recall**: **97.68%**
- **Weighted F1-Score**: **97.66%**
- **Multi-Class ROC-AUC (One-vs-Rest)**: **0.9892**
- **Legitimate False Alarm Rate**: **0.89%** ($< 1\%$ UX impact on safe users)

### Per-Class Performance Breakdown:
| Class | Precision | Recall | F1-Score | Test Support |
|---|---|---|---|---|
| `LEGITIMATE` (0) | 97.48% | 99.11% | **98.29%** | 2,032 |
| `SUSPICIOUS` (1) | 96.29% | 92.49% | **94.35%** | 786 |
| `COACHED_SCAM` (2) | **99.25%** | **98.93%** | **99.09%** | 932 |

### Confusion Matrix:
| Actual \ Predicted | `LEGITIMATE` | `SUSPICIOUS` | `COACHED_SCAM` |
|---|---|---|---|
| **LEGITIMATE** | **2,014** | 18 | 0 |
| **SUSPICIOUS** | 52 | **727** | 7 |
| **COACHED_SCAM** | 0 | 10 | **922** |

*Note: 0 coached scam sessions were misclassified as legitimate.*

---

## 4. Pipeline Execution & Commands

### 1. Generate Synthetic Telemetry Dataset:
```bash
python ml/generate_data.py --samples 25000 --output data/synthetic_behavioural_data.csv
```

### 2. Train Model and Export Artifacts:
```bash
python ml/train.py --data data/synthetic_behavioural_data.csv --output-dir ml/models
```

### 3. Evaluate Held-Out Performance:
```bash
python ml/evaluate.py --model-dir ml/models --data data/synthetic_behavioural_data.csv
```

### 4. Run Real-Time Prediction Test:
```bash
python ml/predict.py
```

### 5. Run Unit Tests:
```bash
pytest ml/test_ml.py
```

---

## 5. FastAPI Integration Guide

To consume the trained model in FastAPI routes without retraining or disk reload latency:

```python
from ml.predict import predict_risk

# Single session risk scoring
raw_telemetry = {
    "screen_share_duration": 340.0,
    "banking_app_opened": 1,
    "new_beneficiary": 1,
    "transaction_amount": 75000.0,
    "app_switch_count": 8,
    "session_duration": 400.0,
    "time_between_events": 1.5,
    "known_assistant": 0,
    "first_time_assistance": 1,
    "transaction_velocity": 2.5,
    "navigation_back_count": 5,
    "authentication_event": 1,
    "assistance_history": 0
}

response = predict_risk(raw_telemetry)
# Returns:
# {
#   "risk_score": 78.5,
#   "risk_level": "HIGH",
#   "predicted_class": "COACHED_SCAM",
#   "class_probabilities": {"LEGITIMATE": 0.012, "SUSPICIOUS": 0.083, "COACHED_SCAM": 0.905},
#   "detected_signals": [
#     "Extended remote screen mirroring active (340s duration)",
#     "Banking application accessed during active remote screen sharing session",
#     "Remote assistance initiated by unverified / first-time external identity",
#     "High-value transfer (INR 75,000) initiated to newly created payee",
#     "Elevated app switching cadence (8 switches, potential OTP/credential sharing)",
#     "Rapid action cadence matching scripted voice-coaching guidance"
#   ]
# }
```
