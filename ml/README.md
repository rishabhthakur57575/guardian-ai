# GuardianAI - ML Subsystem (Phase 2 Roadmap)

This directory is reserved for the behavioural Machine Learning model pipeline that will be integrated in Phase 2.

## Objectives
- Train a lightweight, on-device classifier (e.g. XGBoost / LightGBM / ONNX Runtime) to score scam risk in real-time.
- Process behavioural sequences without ingesting raw keystrokes, screen images, or sensitive text.

## Feature Extraction Specification
1. **Screen Share Persistence**: Duration of continuous screen mirroring session before banking app launch.
2. **App Transition Velocity**: Pacing between remote tool launch, banking app foregrounding, and payee addition.
3. **Clipboard / Rapid Input Ratio**: Automated or paste-based beneficiary field population.
4. **Amount Deviation Ratio**: Current transfer amount normalized against baseline transactional history.
5. **Touch & Navigation Cadence Anomaly**: Hesitation vs rapid script-guided tapping patterns.

## Planned Model Architecture
- **Inference Engine**: ONNX Runtime (Mobile / Edge optimized, <5ms inference latency).
- **Fallback**: Rule-based heuristic decision tree (already operational in Phase 1 `backend/app/services/risk_engine.py`).
