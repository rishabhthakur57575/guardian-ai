from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

"""
Feature Extraction Service
--------------------------
Transforms raw behavioural telemetry events into normalized, high-level
behavioural risk indicators suitable for rule-based and ML inference models.
Zero PII is processed or stored.
"""

def extract_features(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extracts high-level risk features from a chronological sequence of session events.
    
    Returns:
        dict containing boolean flags, tool names, timing cadences, and financial amounts.
    """
    features: Dict[str, Any] = {
        "screen_sharing_active": False,
        "screen_share_tool": None,
        "screen_share_start_time": None,
        "banking_app_opened": False,
        "banking_app_name": None,
        "banking_open_time": None,
        "beneficiary_added": False,
        "beneficiary_label": None,
        "high_value_transfer": False,
        "transfer_amount": 0.0,
        "rapid_switching": False,
        "coached_sequence": False,
        "paste_event_detected": False,
        "touch_cadence_variance": 0.0,
        "event_count": len(events),
        "banking_under_screen_share": False,
        "rapid_beneficiary_addition": False,
    }

    if not events:
        return features

    for ev in events:
        etype = str(ev.get("event_type", "")).upper()
        meta = ev.get("metadata", {}) or {}
        ts = ev.get("timestamp")

        # 1. Screen sharing detection
        if "SCREEN_SHARING" in etype or meta.get("screen_sharing_active"):
            features["screen_sharing_active"] = True
            features["screen_share_tool"] = meta.get("tool_name", features["screen_share_tool"] or "Remote Access Tool")
            if not features["screen_share_start_time"] and ts:
                features["screen_share_start_time"] = ts

        # 2. Financial / Banking application detection
        if "BANKING_APP" in etype or meta.get("banking_app_active"):
            features["banking_app_opened"] = True
            features["banking_app_name"] = meta.get("app_name", features["banking_app_name"] or "Banking Application")
            if not features["banking_open_time"] and ts:
                features["banking_open_time"] = ts

        # 3. Payee / Beneficiary creation
        if "BENEFICIARY_ADDED" in etype or meta.get("new_beneficiary"):
            features["beneficiary_added"] = True
            features["beneficiary_label"] = meta.get("beneficiary_label", "Unknown Beneficiary")
            if meta.get("paste_event_detected"):
                features["paste_event_detected"] = True

        # 4. Monetary transfers
        if "TRANSACTION" in etype or meta.get("transaction_amount"):
            amt = float(meta.get("transaction_amount", 0.0) or 0.0)
            if amt > 0:
                features["transfer_amount"] = max(features["transfer_amount"], amt)
                if amt >= 25000:
                    features["high_value_transfer"] = True

        # 5. Scripted/coached telemetry signals
        if "RAPID_SWITCH" in etype or meta.get("rapid_app_switch"):
            features["rapid_switching"] = True

        if "COACHED_BEHAVIOUR" in etype or meta.get("coached_sequence_detected"):
            features["coached_sequence"] = True
            features["rapid_switching"] = True
            features["high_value_transfer"] = True

        if "touch_cadence_variance_score" in meta:
            features["touch_cadence_variance"] = float(meta["touch_cadence_variance_score"])

    # Composite contextual indicators
    if features["screen_sharing_active"] and features["banking_app_opened"]:
        features["banking_under_screen_share"] = True

    if features["screen_sharing_active"] and features["beneficiary_added"]:
        features["rapid_beneficiary_addition"] = True

    # ML Pipeline Raw Telemetry Features
    app_switch_count = 0
    nav_back_count = 0
    auth_event = 0
    known_assistant = 0
    first_time_assistance = 0
    assistance_history = 0
    screen_share_duration = 0.0

    timestamps = []
    for ev in events:
        meta = ev.get("metadata", {}) or {}
        etype = str(ev.get("event_type", "")).upper()
        ts = ev.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                ts = None
        if ts:
            timestamps.append(ts)

        if "APP_SWITCH" in etype or meta.get("app_switch_count") or meta.get("rapid_app_switch"):
            app_switch_count += int(meta.get("app_switch_count", 1))

        if "NAVIGATION_BACK" in etype or meta.get("navigation_back_count"):
            nav_back_count += int(meta.get("navigation_back_count", 1))

        if "AUTHENTICATION" in etype or meta.get("authentication_event") or meta.get("auth_method"):
            auth_event = 1

        if "known_assistant" in meta:
            known_assistant = int(meta["known_assistant"])
        if "first_time_assistance" in meta:
            first_time_assistance = int(meta["first_time_assistance"])
        if "assistance_history" in meta:
            assistance_history = int(meta["assistance_history"])

        if "screen_share_duration" in meta:
            screen_share_duration = max(screen_share_duration, float(meta["screen_share_duration"]))

    session_duration = 60.0
    time_between_events = 3.0
    if len(timestamps) >= 2:
        timestamps.sort()
        delta = (timestamps[-1] - timestamps[0]).total_seconds()
        session_duration = max(float(delta), 30.0)
        time_between_events = max(float(delta) / max(len(timestamps) - 1, 1), 0.5)

    if features["screen_sharing_active"] and screen_share_duration == 0.0:
        screen_share_duration = min(session_duration, 180.0)

    # If first_time_assistance was not set explicitly but screen sharing is active and known_assistant is False
    if features["screen_sharing_active"] and not known_assistant and first_time_assistance == 0 and assistance_history == 0:
        first_time_assistance = 1

    features["banking_app_opened"] = bool(features["banking_app_opened"])
    features["screen_sharing_active"] = bool(features["screen_sharing_active"])
    features["beneficiary_added"] = bool(features["beneficiary_added"])

    has_ml_telemetry = any(
        "screen_share_duration" in (ev.get("metadata") or {})
        or "use_ml_inference" in (ev.get("metadata") or {})
        or "known_assistant" in (ev.get("metadata") or {})
        for ev in events
    )

    if has_ml_telemetry:
        features["screen_share_duration"] = float(screen_share_duration)
        features["session_duration"] = float(session_duration)
        features["time_between_events"] = float(time_between_events)
        features["new_beneficiary"] = 1 if features["beneficiary_added"] else 0
        features["transaction_amount"] = float(features["transfer_amount"])
        features["app_switch_count"] = int(app_switch_count)
        features["known_assistant"] = int(known_assistant)
        features["first_time_assistance"] = int(first_time_assistance)
        features["transaction_velocity"] = round(features["transaction_amount"] / (session_duration + 1.0), 4)
        features["navigation_back_count"] = int(nav_back_count)
        features["authentication_event"] = int(auth_event)
        features["assistance_history"] = int(assistance_history)

    return features
