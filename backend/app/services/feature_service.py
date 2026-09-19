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

    return features
