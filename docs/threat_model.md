# GuardianAI - Threat Model & Attack Taxonomy

## Problem Statement: Remote Screen Sharing Coached Scams
In coached financial fraud scenarios (targeting vulnerable demographics such as the elderly), attackers use deceptive phone calls (e.g. impostor bank manager, courier refund desk, electricity department official) to convince victims to:
1. Download a remote assistance tool (AnyDesk, TeamViewer, RustDesk, QuickSupport).
2. Open their mobile banking or UPI payment app while the remote session is running.
3. Add a fraudster-controlled bank account as a new beneficiary.
4. Execute an urgent transfer (e.g. ₹1,00,000+) under the guise of a "security test" or "instant refund reversal".

## Threat Scenarios Intercepted by GuardianAI

| Threat Vector | Indicator / Trigger Sequence | GuardianAI Countermeasure |
| :--- | :--- | :--- |
| **Remote Screen Mirroring** | Screen share active + banking foregrounded | Immediate elevated surveillance state |
| **Coached Beneficiary Setup** | Beneficiary added within 90s of remote connection | Flagged as critical anomaly |
| **High-Value Exfiltration** | Large amount initiated under active screen mirror | Scam Intervention Modal triggered; transfer halted |
| **Scripted Voice Coaching** | Rapid app switching cadence & paste events | Pattern signature correlation alert |
