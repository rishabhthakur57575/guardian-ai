"""
GuardianAI - Behavioral Telemetry Scenarios
============================================
Predefined behavioral event sequences for repeatable demo runs and integration tests.

SCENARIO A — LEGITIMATE ASSISTANCE
- Screen sharing with verified helper (e.g., family caregiver)
- Banking app opened
- Routine transaction (e.g., ₹1,800 utility payment)
- Low risk score (< 30)

SCENARIO B — COACHED SCAM
- Screen sharing with unverified external identity
- Rapid multitasking / app switching
- Banking app accessed under screen mirroring
- Immediate new beneficiary setup (paste event)
- Rapid navigation reversals / hesitations
- High-value transfer (₹1,85,000)
- High risk score (>= 75 - 95+)
"""

from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import os
import sys

# Support direct execution and relative package import
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from events import (
    DeviceEvent,
    create_screen_share_started,
    create_screen_share_ended,
    create_banking_app_opened,
    create_banking_app_closed,
    create_new_beneficiary,
    create_app_switch,
    create_navigation_back,
    create_transaction_started,
    create_authentication_event,
    create_transaction_completed,
    create_transaction_cancelled
)


def build_scenario_a_legitimate(
    session_id: str,
    base_time: datetime = None
) -> List[DeviceEvent]:
    """
    Builds SCENARIO A: Legitimate Family/Caregiver Remote Assistance
    Expected Outcome: SAFE baseline, risk score < 30%.
    """
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    events: List[DeviceEvent] = []

    # Step 1: Screen share started with verified family contact
    ev1 = create_screen_share_started(
        session_id=session_id,
        tool_name="Google Meet / TeamViewer Family",
        known_assistant=True,
        first_time_assistance=False,
        assistant_history=7,
        assistant_label="Son (Rahul - Verified Caregiver)"
    )
    ev1.timestamp = base_time + timedelta(seconds=0)
    events.append(ev1)

    # Step 2: Calm app switch from WhatsApp to Banking App
    ev2 = create_app_switch(
        session_id=session_id,
        from_app="com.whatsapp",
        to_app="com.snapwork.hdfc",
        switch_count=1
    )
    ev2.timestamp = base_time + timedelta(seconds=12)
    events.append(ev2)

    # Step 3: Banking app opened
    ev3 = create_banking_app_opened(
        session_id=session_id,
        app_name="HDFC MobileBanking",
        package_name="com.snapwork.hdfc"
    )
    ev3.timestamp = base_time + timedelta(seconds=15)
    events.append(ev3)

    # Step 4: Normal single back navigation (menu navigation)
    ev4 = create_navigation_back(
        session_id=session_id,
        screen_name="AccountSummaryScreen",
        back_count=1
    )
    ev4.timestamp = base_time + timedelta(seconds=35)
    events.append(ev4)

    # Step 5: Routine utility bill payment to established payee
    ev5 = create_transaction_started(
        session_id=session_id,
        amount=1850.0,
        currency="INR",
        recipient_type="EXISTING_BILLER"
    )
    ev5.timestamp = base_time + timedelta(seconds=55)
    events.append(ev5)

    # Step 6: Calm biometric authentication
    ev6 = create_authentication_event(
        session_id=session_id,
        auth_method="BIOMETRIC_FINGERPRINT",
        success=True
    )
    ev6.timestamp = base_time + timedelta(seconds=68)
    events.append(ev6)

    # Step 7: Transaction completes safely
    ev7 = create_transaction_completed(
        session_id=session_id,
        amount=1850.0,
        reference_id="TXN_HDFC_891273"
    )
    ev7.timestamp = base_time + timedelta(seconds=75)
    events.append(ev7)

    # Step 8: Banking app closed
    ev8 = create_banking_app_closed(
        session_id=session_id,
        app_name="HDFC MobileBanking"
    )
    ev8.timestamp = base_time + timedelta(seconds=90)
    events.append(ev8)

    # Step 9: Screen sharing ended
    ev9 = create_screen_share_ended(
        session_id=session_id,
        tool_name="Google Meet / TeamViewer Family",
        duration_seconds=105.0
    )
    ev9.timestamp = base_time + timedelta(seconds=105)
    events.append(ev9)

    return events


def build_scenario_b_coached_scam(
    session_id: str,
    base_time: datetime = None
) -> List[DeviceEvent]:
    """
    Builds SCENARIO B: Coached Remote Screen-Sharing Scam
    Expected Outcome: THREAT_DETECTED, risk score >= 75 - 95%.
    """
    if base_time is None:
        base_time = datetime.now(timezone.utc)

    events: List[DeviceEvent] = []

    # Step 1: Screen share initiated via AnyDesk with unknown helper
    ev1 = create_screen_share_started(
        session_id=session_id,
        tool_name="AnyDesk Remote Support",
        known_assistant=False,
        first_time_assistance=True,
        assistant_history=0,
        assistant_label="Caller claiming Bank Refund Executive"
    )
    ev1.timestamp = base_time + timedelta(seconds=0)
    events.append(ev1)

    # Step 2: Rapid dictated app switches (SMS -> AnyDesk -> WhatsApp)
    ev2 = create_app_switch(
        session_id=session_id,
        from_app="com.anydesk.anydeskandroid",
        to_app="com.google.android.apps.messaging",
        switch_count=3
    )
    ev2.timestamp = base_time + timedelta(seconds=8)
    events.append(ev2)

    # Step 3: Banking app opened while screen mirror is active
    ev3 = create_banking_app_opened(
        session_id=session_id,
        app_name="HDFC MobileBanking",
        package_name="com.snapwork.hdfc"
    )
    ev3.timestamp = base_time + timedelta(seconds=14)
    events.append(ev3)

    # Step 4: Rapid multitasking back to WhatsApp for dictated payee details
    ev4 = create_app_switch(
        session_id=session_id,
        from_app="com.snapwork.hdfc",
        to_app="com.whatsapp",
        switch_count=6
    )
    ev4.timestamp = base_time + timedelta(seconds=22)
    events.append(ev4)

    # Step 5: Return to banking app and add new beneficiary with clipboard paste
    ev5 = create_new_beneficiary(
        session_id=session_id,
        beneficiary_label="RefundDesk_Agent_Verification_8892",
        paste_detected=True
    )
    ev5.timestamp = base_time + timedelta(seconds=30)
    events.append(ev5)

    # Step 6: Multiple rapid navigation back button clicks (coaching hesitation & dictation correction)
    ev6 = create_navigation_back(
        session_id=session_id,
        screen_name="AddPayeeFormScreen",
        back_count=4
    )
    ev6.timestamp = base_time + timedelta(seconds=38)
    events.append(ev6)

    # Step 7: High-value transaction initiated under dictation
    ev7 = create_transaction_started(
        session_id=session_id,
        amount=185000.0,
        currency="INR",
        recipient_type="NEW_BENEFICIARY"
    )
    ev7.timestamp = base_time + timedelta(seconds=46)
    events.append(ev7)

    # Step 8: Prompt biometric or PIN authentication
    ev8 = create_authentication_event(
        session_id=session_id,
        auth_method="BIOMETRIC_FINGERPRINT",
        success=True
    )
    ev8.timestamp = base_time + timedelta(seconds=54)
    events.append(ev8)

    # Step 9: GuardianAI Elderly Intervention Triggers -> User Cancels Transaction!
    ev9 = create_transaction_cancelled(
        session_id=session_id,
        amount=185000.0,
        reason="GUARDIANAI_INTERVENTION_HALTED_COACHED_FRAUD"
    )
    ev9.timestamp = base_time + timedelta(seconds=62)
    events.append(ev9)

    # Step 10: Screen sharing abruptly terminated
    ev10 = create_screen_share_ended(
        session_id=session_id,
        tool_name="AnyDesk Remote Support",
        duration_seconds=70.0
    )
    ev10.timestamp = base_time + timedelta(seconds=70)
    events.append(ev10)

    # Step 11: Banking app closed
    ev11 = create_banking_app_closed(
        session_id=session_id,
        app_name="HDFC MobileBanking"
    )
    ev11.timestamp = base_time + timedelta(seconds=75)
    events.append(ev11)

    return events


def get_scenario(name: str, session_id: str) -> List[DeviceEvent]:
    """Factory helper to fetch scenario events by keyword."""
    normalized = name.strip().lower()
    if "legit" in normalized or "normal" in normalized or normalized == "a":
        return build_scenario_a_legitimate(session_id)
    elif "scam" in normalized or "fraud" in normalized or normalized == "b":
        return build_scenario_b_coached_scam(session_id)
    else:
        raise ValueError(f"Unknown scenario name: '{name}'. Choose 'legitimate' or 'scam'.")
