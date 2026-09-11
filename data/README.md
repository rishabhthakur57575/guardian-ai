# GuardianAI - Data Engineering & Synthetic Datasets

This directory contains privacy-safe synthetic datasets and schema definitions for behavioural scam detection modeling.

## Synthetic Dataset Generation Plan
To respect user privacy and avoid training on real financial records, Phase 2 will generate synthetic behavioural traces modeling:
1. **Legitimate Workflows**: Routine banking transfers, bill payments, multi-tasking without screen sharing.
2. **Benign Screen Sharing**: Tech support sessions, presentation sharing, gaming streams without banking activity.
3. **Coached Scam Scenarios**:
   - AnyDesk / TeamViewer download prompted by phone caller.
   - Immediate navigation to banking portals / UPI apps.
   - Rapid addition of unknown payee accounts.
   - High-value emergency transfers (impostor tax refund, electricity bill disconnection threat, fake police KYC).

## Zero-PII Guarantee
All synthetic and telemetry records adhere to the schema in [`schema.json`](./schema.json) with strict omission of PII, OTPs, credentials, and screen images.
