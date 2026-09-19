"""
GuardianAI - Synthetic Behavioural Telemetry Dataset Generator
==============================================================
Generates realistic behavioural sequences and aggregate telemetry records
representing:
  - Class 0: LEGITIMATE (solo banking, family assistance, video KYC, IT support)
  - Class 1: SUSPICIOUS (borderline anomalies, unusual pacing, unverified help)
  - Class 2: COACHED_SCAM (remote access screen mirroring, urgent coaching cadence,
                           untrusted assistant, rapid app switches, forced payee creation)

Implements realistic multi-dimensional feature distributions and non-linear
decision boundaries with statistical noise and real-world edge cases.
"""

import argparse
import os
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any

# Target classes mapping
CLASS_MAP = {
    0: "LEGITIMATE",
    1: "SUSPICIOUS",
    2: "COACHED_SCAM"
}

# Raw base features specification
BASE_FEATURES = [
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

RAW_FEATURES = BASE_FEATURES


def generate_legitimate_samples(n_samples: int, rng: np.random.Generator) -> pd.DataFrame:
    """
    Generates legitimate user telemetry:
    - 70% standard solo mobile banking
    - 20% legitimate assisted sessions (family tech assistance, bank RM / video KYC, corporate IT)
    - 10% elderly / tech-novice users (slower cadence, minor hesitation, but safe contacts)
    """
    records = []

    # Sub-cohort breakdown
    n_solo = int(n_samples * 0.70)
    n_assisted = int(n_samples * 0.20)
    n_novice = n_samples - n_solo - n_assisted

    # 1. Solo Banking Cohort
    for _ in range(n_solo):
        session_duration = float(rng.gamma(shape=3.5, scale=45.0) + 30.0) # ~120s - 400s
        screen_share_duration = 0.0
        banking_app_opened = 1 if rng.random() < 0.98 else 0
        new_beneficiary = 1 if rng.random() < 0.18 else 0
        
        # Amount: log-normal distribution with typical daily banking spend
        # Some legitimate transactions can be large (up to 250,000 INR)
        if rng.random() < 0.08:
            transaction_amount = float(rng.uniform(50000.0, 250000.0))
        elif rng.random() < 0.40:
            transaction_amount = float(rng.exponential(scale=4500.0) + 150.0)
        else:
            transaction_amount = float(rng.uniform(50.0, 3500.0))
        transaction_amount = round(min(transaction_amount, 500000.0), 2)

        app_switch_count = int(rng.poisson(lam=1.2))
        time_between_events = float(rng.normal(loc=3.8, scale=1.1))
        time_between_events = max(1.2, time_between_events)

        known_assistant = 0 # no assistant
        first_time_assistance = 0
        assistance_history = int(rng.choice([0, 1, 2], p=[0.85, 0.10, 0.05]))
        
        transaction_velocity = float(rng.exponential(scale=0.25) + 0.05)
        navigation_back_count = int(rng.poisson(lam=0.8))
        authentication_event = 1 if rng.random() < 0.95 else 0

        records.append({
            "screen_share_duration": screen_share_duration,
            "banking_app_opened": banking_app_opened,
            "new_beneficiary": new_beneficiary,
            "transaction_amount": transaction_amount,
            "app_switch_count": app_switch_count,
            "session_duration": round(session_duration, 1),
            "time_between_events": round(time_between_events, 2),
            "known_assistant": known_assistant,
            "first_time_assistance": first_time_assistance,
            "transaction_velocity": round(transaction_velocity, 2),
            "navigation_back_count": navigation_back_count,
            "authentication_event": authentication_event,
            "assistance_history": assistance_history,
            "label": 0
        })

    # 2. Legitimate Assisted Cohort (Family tech support, IT Helpdesk, Bank Video RM)
    for _ in range(n_assisted):
        session_duration = float(rng.gamma(shape=4.0, scale=70.0) + 90.0) # ~250s - 600s
        # Screen share is legitimately active
        screen_share_duration = float(min(session_duration * rng.uniform(0.5, 0.95), session_duration))
        banking_app_opened = 1
        new_beneficiary = 1 if rng.random() < 0.28 else 0
        
        # Can have high transaction amounts (e.g. paying college fees, family transfer)
        if rng.random() < 0.25:
            transaction_amount = float(rng.uniform(30000.0, 180000.0))
        else:
            transaction_amount = float(rng.uniform(500.0, 25000.0))
        transaction_amount = round(transaction_amount, 2)

        app_switch_count = int(rng.poisson(lam=2.5))
        time_between_events = float(rng.normal(loc=4.5, scale=1.4))
        time_between_events = max(1.8, time_between_events)

        known_assistant = 1 # Verified trusted assistant / contact
        first_time_assistance = 1 if rng.random() < 0.20 else 0
        assistance_history = int(rng.integers(1, 15)) if first_time_assistance == 0 else 0
        
        transaction_velocity = float(rng.uniform(0.1, 0.8))
        navigation_back_count = int(rng.poisson(lam=1.5))
        authentication_event = 1 if rng.random() < 0.92 else 0

        records.append({
            "screen_share_duration": round(screen_share_duration, 1),
            "banking_app_opened": banking_app_opened,
            "new_beneficiary": new_beneficiary,
            "transaction_amount": transaction_amount,
            "app_switch_count": app_switch_count,
            "session_duration": round(session_duration, 1),
            "time_between_events": round(time_between_events, 2),
            "known_assistant": known_assistant,
            "first_time_assistance": first_time_assistance,
            "transaction_velocity": round(transaction_velocity, 2),
            "navigation_back_count": navigation_back_count,
            "authentication_event": authentication_event,
            "assistance_history": assistance_history,
            "label": 0
        })

    # 3. Elderly / Novice Cohort
    for _ in range(n_novice):
        session_duration = float(rng.gamma(shape=5.0, scale=80.0) + 120.0)
        screen_share_duration = float(rng.choice([0.0, rng.uniform(40.0, session_duration * 0.7)], p=[0.70, 0.30]))
        banking_app_opened = 1
        new_beneficiary = 1 if rng.random() < 0.15 else 0
        transaction_amount = round(float(rng.uniform(100.0, 15000.0)), 2)
        
        app_switch_count = int(rng.poisson(lam=1.8))
        # Slower deliberation pace
        time_between_events = float(rng.normal(loc=6.2, scale=1.8))
        time_between_events = max(2.5, time_between_events)

        known_assistant = 1 if screen_share_duration > 0 else 0
        first_time_assistance = 1 if (screen_share_duration > 0 and rng.random() < 0.3) else 0
        assistance_history = int(rng.integers(1, 8)) if (screen_share_duration > 0 and first_time_assistance == 0) else 0
        
        transaction_velocity = float(rng.uniform(0.05, 0.4))
        navigation_back_count = int(rng.poisson(lam=3.2)) # High hesitation but harmless
        authentication_event = 1 if rng.random() < 0.88 else 0

        records.append({
            "screen_share_duration": round(screen_share_duration, 1),
            "banking_app_opened": banking_app_opened,
            "new_beneficiary": new_beneficiary,
            "transaction_amount": transaction_amount,
            "app_switch_count": app_switch_count,
            "session_duration": round(session_duration, 1),
            "time_between_events": round(time_between_events, 2),
            "known_assistant": known_assistant,
            "first_time_assistance": first_time_assistance,
            "transaction_velocity": round(transaction_velocity, 2),
            "navigation_back_count": navigation_back_count,
            "authentication_event": authentication_event,
            "assistance_history": assistance_history,
            "label": 0
        })

    return pd.DataFrame(records)


def generate_suspicious_samples(n_samples: int, rng: np.random.Generator) -> pd.DataFrame:
    """
    Generates suspicious / borderline user telemetry:
    - Unfamiliar assistance with low/moderate transaction
    - Sudden payee addition with elevated app switching
    - Erratic navigation patterns or high velocity with unverified credentials
    """
    records = []
    for _ in range(n_samples):
        scenario = rng.choice(["unverified_helper", "rapid_transfers", "erratic_navigation", "screen_share_alone"])
        session_duration = float(rng.gamma(shape=3.8, scale=60.0) + 60.0)

        if scenario == "unverified_helper":
            # Remote assistant not registered in known list, but transaction is moderate
            screen_share_duration = float(session_duration * rng.uniform(0.3, 0.75))
            banking_app_opened = 1
            new_beneficiary = 1 if rng.random() < 0.50 else 0
            transaction_amount = round(float(rng.uniform(1500.0, 35000.0)), 2)
            app_switch_count = int(rng.poisson(lam=4.0))
            time_between_events = float(rng.uniform(2.0, 4.8))
            known_assistant = 0
            first_time_assistance = 1
            assistance_history = 0
            transaction_velocity = float(rng.uniform(0.6, 1.8))
            navigation_back_count = int(rng.poisson(lam=2.8))
            authentication_event = 1 if rng.random() < 0.90 else 0

        elif scenario == "rapid_transfers":
            # Fast paced transaction without screen share
            screen_share_duration = 0.0
            banking_app_opened = 1
            new_beneficiary = 1 if rng.random() < 0.70 else 0
            transaction_amount = round(float(rng.uniform(20000.0, 95000.0)), 2)
            app_switch_count = int(rng.poisson(lam=5.5))
            time_between_events = float(rng.uniform(1.2, 2.6))
            known_assistant = 0
            first_time_assistance = 0
            assistance_history = 0
            transaction_velocity = float(rng.uniform(1.5, 3.2))
            navigation_back_count = int(rng.poisson(lam=3.5))
            authentication_event = 1 if rng.random() < 0.95 else 0

        elif scenario == "erratic_navigation":
            # High hesitation and rapid app swapping
            screen_share_duration = float(rng.choice([0.0, rng.uniform(30.0, 150.0)], p=[0.6, 0.4]))
            banking_app_opened = 1
            new_beneficiary = 1 if rng.random() < 0.40 else 0
            transaction_amount = round(float(rng.uniform(3000.0, 45000.0)), 2)
            app_switch_count = int(rng.poisson(lam=6.2))
            time_between_events = float(rng.uniform(1.5, 3.5))
            known_assistant = 1 if rng.random() < 0.3 else 0
            first_time_assistance = 1 if (known_assistant == 0 and rng.random() < 0.6) else 0
            assistance_history = int(rng.choice([0, 1]))
            transaction_velocity = float(rng.uniform(0.8, 2.0))
            navigation_back_count = int(rng.poisson(lam=5.2))
            authentication_event = 1 if rng.random() < 0.85 else 0

        else: # screen_share_alone
            # Screen share active, but transaction not yet committed or small test
            screen_share_duration = float(session_duration * rng.uniform(0.5, 0.9))
            banking_app_opened = 1 if rng.random() < 0.85 else 0
            new_beneficiary = 0
            transaction_amount = round(float(rng.uniform(0.0, 5000.0)), 2)
            app_switch_count = int(rng.poisson(lam=3.2))
            time_between_events = float(rng.uniform(2.5, 5.0))
            known_assistant = 0
            first_time_assistance = 1
            assistance_history = 0
            transaction_velocity = float(rng.uniform(0.2, 0.9))
            navigation_back_count = int(rng.poisson(lam=2.0))
            authentication_event = 1 if rng.random() < 0.80 else 0

        records.append({
            "screen_share_duration": round(screen_share_duration, 1),
            "banking_app_opened": banking_app_opened,
            "new_beneficiary": new_beneficiary,
            "transaction_amount": transaction_amount,
            "app_switch_count": app_switch_count,
            "session_duration": round(session_duration, 1),
            "time_between_events": round(time_between_events, 2),
            "known_assistant": known_assistant,
            "first_time_assistance": first_time_assistance,
            "transaction_velocity": round(transaction_velocity, 2),
            "navigation_back_count": navigation_back_count,
            "authentication_event": authentication_event,
            "assistance_history": assistance_history,
            "label": 1
        })

    return pd.DataFrame(records)


def generate_coached_scam_samples(n_samples: int, rng: np.random.Generator) -> pd.DataFrame:
    """
    Generates coached financial scam telemetry:
    - Scammer has victim on voice call + screen share (AnyDesk/TeamViewer/RustDesk/QuickSupport)
    - Coached cadence: Scammer commands immediate actions ("open bank app", "add payee", "transfer ₹95,000")
    - Key markers: unknown assistant, first-time assistance, active screen mirroring,
      new beneficiary addition, rapid app switching (WhatsApp/AnyDesk/Bank), high back/hesitation
      reversals under pressure, urgent velocity.
    - Realistic noise: Some scams do small test amounts (₹10 - ₹500), some victims are slow/hesitant,
      and some scammers coach without opening secondary apps.
    """
    records = []
    for _ in range(n_samples):
        session_duration = float(rng.gamma(shape=4.2, scale=75.0) + 120.0) # 250s - 800s
        
        # Extended screen sharing duration
        screen_share_duration = float(session_duration * rng.uniform(0.65, 0.98))
        banking_app_opened = 1 if rng.random() < 0.97 else 0
        new_beneficiary = 1 if rng.random() < 0.89 else 0
        
        # Transaction Amount:
        # 80% heavy drain (25,000 to 480,000 INR)
        # 15% medium fraud (5,000 to 25,000 INR)
        # 5% micro probe / verification scam (₹10 to ₹1,000)
        amt_roll = rng.random()
        if amt_roll < 0.80:
            transaction_amount = float(rng.uniform(25000.0, 480000.0))
        elif amt_roll < 0.95:
            transaction_amount = float(rng.uniform(5000.0, 25000.0))
        else:
            transaction_amount = float(rng.uniform(10.0, 1000.0))
        transaction_amount = round(transaction_amount, 2)

        # High app switching: checking OTP in SMS / WhatsApp while in banking app
        app_switch_count = int(rng.poisson(lam=7.8) + rng.integers(2, 8))
        
        # Pacing: either rapid dictated clicks (0.8s - 2.2s) or coached burst pauses
        if rng.random() < 0.75:
            time_between_events = float(rng.normal(loc=1.6, scale=0.45))
        else:
            time_between_events = float(rng.normal(loc=2.8, scale=0.7))
        time_between_events = max(0.4, time_between_events)

        # Untrusted remote identity
        # In rare 2% cases, scammer spoofed or registered as known contact
        known_assistant = 1 if rng.random() < 0.03 else 0
        first_time_assistance = 0 if known_assistant == 1 else (1 if rng.random() < 0.96 else 0)
        assistance_history = 0 if known_assistant == 0 else int(rng.choice([0, 1]))
        
        # High transaction velocity
        transaction_velocity = float(rng.uniform(1.4, 4.5))
        
        # High navigation backs due to victim confusion and scammer dictation
        navigation_back_count = int(rng.poisson(lam=5.5) + rng.integers(1, 6))
        authentication_event = 1 if rng.random() < 0.94 else 0

        records.append({
            "screen_share_duration": round(screen_share_duration, 1),
            "banking_app_opened": banking_app_opened,
            "new_beneficiary": new_beneficiary,
            "transaction_amount": transaction_amount,
            "app_switch_count": app_switch_count,
            "session_duration": round(session_duration, 1),
            "time_between_events": round(time_between_events, 2),
            "known_assistant": known_assistant,
            "first_time_assistance": first_time_assistance,
            "transaction_velocity": round(transaction_velocity, 2),
            "navigation_back_count": navigation_back_count,
            "authentication_event": authentication_event,
            "assistance_history": assistance_history,
            "label": 2
        })

    return pd.DataFrame(records)


def inject_realistic_noise(df: pd.DataFrame, noise_rate: float = 0.035, seed: int = 42) -> pd.DataFrame:
    """
    Injects realistic real-world noise and overlap:
    - Randomly perturbs 3-5% of samples across boundary regions
    - Prevents single-feature overfitting or trivial rule shortcuts
    """
    rng = np.random.default_rng(seed)
    df_noisy = df.copy()
    n_rows = len(df_noisy)
    n_noise = int(n_rows * noise_rate)

    noise_indices = rng.choice(n_rows, size=n_noise, replace=False)

    for idx in noise_indices:
        current_label = df_noisy.loc[idx, "label"]
        if current_label == 0:
            # Legitimate edge case marked as suspicious or borderline
            df_noisy.loc[idx, "label"] = rng.choice([0, 1], p=[0.4, 0.6])
            # Add some jitter to switch count or back count
            df_noisy.loc[idx, "app_switch_count"] += int(rng.integers(1, 4))
        elif current_label == 1:
            # Suspicious borderline resolves to legitimate or scam
            df_noisy.loc[idx, "label"] = rng.choice([0, 2], p=[0.5, 0.5])
        elif current_label == 2:
            # Scam with unusual benign attributes (e.g. smaller amount, quiet session)
            if rng.random() < 0.5:
                df_noisy.loc[idx, "label"] = 1 # boundary ambiguity
                df_noisy.loc[idx, "transaction_amount"] = round(float(rng.uniform(100.0, 5000.0)), 2)

    return df_noisy


def generate_dataset(
    n_samples: int = 25000,
    legit_ratio: float = 0.55,
    suspicious_ratio: float = 0.20,
    scam_ratio: float = 0.25,
    noise_rate: float = 0.035,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates the complete synthetic behavioural telemetry dataset.
    """
    rng = np.random.default_rng(seed)

    n_legit = int(n_samples * legit_ratio)
    n_suspicious = int(n_samples * suspicious_ratio)
    n_scam = n_samples - n_legit - n_suspicious

    print(f"[*] Generating {n_samples:,} synthetic samples:")
    print(f"    - Legitimate (0) : {n_legit:,}")
    print(f"    - Suspicious (1) : {n_suspicious:,}")
    print(f"    - Coached Scam (2): {n_scam:,}")

    df_legit = generate_legitimate_samples(n_legit, rng)
    df_suspicious = generate_suspicious_samples(n_suspicious, rng)
    df_scam = generate_coached_scam_samples(n_scam, rng)

    df_combined = pd.concat([df_legit, df_suspicious, df_scam], ignore_index=True)
    
    # Shuffle
    df_shuffled = df_combined.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    # Inject realistic noise & boundary overlap
    df_final = inject_realistic_noise(df_shuffled, noise_rate=noise_rate, seed=seed)

    # Add human-readable label column
    df_final["label_name"] = df_final["label"].map(CLASS_MAP)

    return df_final


def main():
    parser = argparse.ArgumentParser(description="GuardianAI Synthetic Dataset Generator")
    parser.add_argument("--samples", type=int, default=25000, help="Total number of samples (min 20,000)")
    parser.add_argument("--output", type=str, default="data/synthetic_behavioural_data.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--noise", type=float, default=0.035, help="Boundary noise rate")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    df = generate_dataset(
        n_samples=args.samples,
        noise_rate=args.noise,
        seed=args.seed
    )

    df.to_csv(args.output, index=False)
    print(f"[+] Successfully generated dataset saved to: {args.output}")
    print(f"[+] Total Rows: {len(df):,}, Total Columns: {len(df.columns)}")
    print("\n[+] Class Distribution:")
    print(df["label_name"].value_counts(normalize=False))
    print("\n[+] Class Percentage:")
    print(df["label_name"].value_counts(normalize=True) * 100)


if __name__ == "__main__":
    main()
