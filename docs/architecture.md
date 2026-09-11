# GuardianAI - Architecture Specification

## 1. High-Level Architecture

GuardianAI operates as an on-device behavioural sentinel designed to identify social engineering and remote screen sharing scams in real-time.

```mermaid
graph TD
    subgraph Device Client & Telemetry
        SS[Remote Screen Share Detected] --> INGEST[Event Pipeline]
        BA[Banking App Opened] --> INGEST
        NB[Beneficiary Created] --> INGEST
        TX[Transfer Initiated] --> INGEST
    end

    subgraph Privacy & Sanitization
        INGEST --> SANITIZE[Zero-PII Privacy Filter]
    end

    subgraph Risk Scoring Engine
        SANITIZE --> RE[backend/app/services/risk_engine.py]
        RE --> CALC{Risk Threshold}
        CALC -->|Score >= 70%| THREAT[Threat Detected]
        CALC -->|Score 30-69%| MON[Active Monitoring]
        CALC -->|Score < 30%| SAFE[Safe Baseline]
    end

    subgraph Intervention UI
        THREAT --> MODAL[Elderly-Friendly High-Contrast Warning]
        MODAL --> CANCEL[User Cancels Transfer]
        MODAL --> TRUST[User Overrides Trust]
    end
```

## 2. Privacy-First Principles
- **No Keystroke Logging**: Only abstract speed metrics (e.g. typing cadence variance, paste detection).
- **No Screen Capture**: Screen contents, balances, and recipient account numbers are never photographed or transmitted.
- **No Credential Interception**: Passwords, MPINs, and OTPs remain strictly inaccessible.
- **Local / Edge Processing**: Behavioural evaluation operates locally without transmitting financial state to external cloud entities.
