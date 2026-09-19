# GuardianAI - Synthetic Behavioural Telemetry Dataset

This directory hosts the behavioural telemetry schema and synthetic dataset for GuardianAI's scam and assisted banking risk engine.

## Files
- `synthetic_behavioural_data.csv`: 25,000 generated interaction sequences with realistic non-linear distributions and boundary noise.
- `schema.json`: JSON Schema defining the real-time event streaming telemetry protocol.

## Dataset Structure
- Total Rows: 25,000
- Total Columns: 15 (13 base features + `label` + `label_name`)

### Class Proportions:
- `LEGITIMATE` (Class 0): ~54.2% (13,547 rows)
- `SUSPICIOUS` (Class 1): ~20.9% (5,237 rows)
- `COACHED_SCAM` (Class 2): ~24.9% (6,216 rows)

## Generation Script
To regenerate with custom seeds or sample volumes:
```bash
python ml/generate_data.py --samples 25000 --output data/synthetic_behavioural_data.csv --seed 42 --noise 0.035
```
