"""
GuardianAI - Device Event Definitions & Telemetry Schema
=========================================================
Defines behavioural telemetry events emitted by device-level monitors
(e.g., Android Accessibility / Knox Telemetry Service).

Guaranteed Zero-PII:
- No passwords, PINs, OTPs, CVVs, PAN, account numbers
- No raw keystrokes or screen captures
"""

import enum
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class DeviceEventType(str, enum.Enum):
    SCREEN_SHARE_STARTED = "SCREEN_SHARE_STARTED"
    SCREEN_SHARE_ENDED = "SCREEN_SHARE_ENDED"
    BANKING_APP_OPENED = "BANKING_APP_OPENED"
    BANKING_APP_CLOSED = "BANKING_APP_CLOSED"
    NEW_BENEFICIARY = "NEW_BENEFICIARY"
    APP_SWITCH = "APP_SWITCH"
    NAVIGATION_BACK = "NAVIGATION_BACK"
    TRANSACTION_STARTED = "TRANSACTION_STARTED"
    AUTHENTICATION_EVENT = "AUTHENTICATION_EVENT"
    TRANSACTION_COMPLETED = "TRANSACTION_COMPLETED"
    TRANSACTION_CANCELLED = "TRANSACTION_CANCELLED"


FORBIDDEN_PRIVACY_KEYS = {
    "password", "otp", "pin", "cvv", "pan", "aadhar", "account_number",
    "card_number", "screenshot", "image_data", "raw_keystrokes",
    "secret", "token", "auth_header"
}


class DeviceEvent(BaseModel):
    """
    Standard device-side event payload sent to POST /api/events.
    """
    session_id: str = Field(..., description="Unique session identifier for device telemetry")
    event_type: str = Field(..., description="DeviceEventType string")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("metadata")
    def validate_zero_pii(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        lowered_keys = {str(k).lower() for k in v.keys()}
        violation = lowered_keys.intersection(FORBIDDEN_PRIVACY_KEYS)
        if violation:
            raise ValueError(f"Privacy violation: sensitive keys prohibited: {sorted(list(violation))}")
        return v

    def to_api_payload(self) -> Dict[str, Any]:
        """Serializes event for POST /api/events."""
        return {
            "session_id": self.session_id,
            "event_type": self.event_type,
            "timestamp": (self.timestamp or datetime.now(timezone.utc)).isoformat(),
            "metadata": self.metadata
        }


# ==============================================================================
# Event Helper Constructors with Standardized Behavioral Metadata
# ==============================================================================

def create_screen_share_started(
    session_id: str,
    tool_name: str = "AnyDesk Remote Support",
    known_assistant: bool = False,
    first_time_assistance: bool = True,
    assistant_history: int = 0,
    assistant_label: Optional[str] = None
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.SCREEN_SHARE_STARTED.value,
        metadata={
            "screen_sharing_active": True,
            "tool_name": tool_name,
            "known_assistant": int(known_assistant),
            "first_time_assistance": int(first_time_assistance),
            "assistance_history": assistant_history,
            "assistant_label": assistant_label or ("Verified Family Contact" if known_assistant else "Unverified External Helper")
        }
    )


def create_screen_share_ended(
    session_id: str,
    tool_name: str = "AnyDesk Remote Support",
    duration_seconds: float = 60.0
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.SCREEN_SHARE_ENDED.value,
        metadata={
            "screen_sharing_active": False,
            "tool_name": tool_name,
            "screen_share_duration": float(duration_seconds)
        }
    )


def create_banking_app_opened(
    session_id: str,
    app_name: str = "HDFC MobileBanking",
    package_name: str = "com.snapwork.hdfc"
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.BANKING_APP_OPENED.value,
        metadata={
            "banking_app_active": True,
            "app_name": app_name,
            "package_name": package_name
        }
    )


def create_banking_app_closed(
    session_id: str,
    app_name: str = "HDFC MobileBanking"
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.BANKING_APP_CLOSED.value,
        metadata={
            "banking_app_active": False,
            "app_name": app_name
        }
    )


def create_new_beneficiary(
    session_id: str,
    beneficiary_label: str = "Unknown Beneficiary",
    paste_detected: bool = False
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.NEW_BENEFICIARY.value,
        metadata={
            "new_beneficiary": True,
            "beneficiary_label": beneficiary_label,
            "paste_event_detected": paste_detected
        }
    )


def create_app_switch(
    session_id: str,
    from_app: str,
    to_app: str,
    switch_count: int = 1
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.APP_SWITCH.value,
        metadata={
            "from_app": from_app,
            "to_app": to_app,
            "app_switch_count": switch_count,
            "rapid_app_switch": switch_count >= 5
        }
    )


def create_navigation_back(
    session_id: str,
    screen_name: str = "TransferConfirmationScreen",
    back_count: int = 1
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.NAVIGATION_BACK.value,
        metadata={
            "screen_name": screen_name,
            "navigation_back_count": back_count,
            "hesitation_indicator": back_count >= 3
        }
    )


def create_transaction_started(
    session_id: str,
    amount: float,
    currency: str = "INR",
    recipient_type: str = "BENEFICIARY"
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.TRANSACTION_STARTED.value,
        metadata={
            "transaction_amount": float(amount),
            "currency": currency,
            "recipient_type": recipient_type,
            "high_value_transfer": amount >= 25000.0
        }
    )


def create_authentication_event(
    session_id: str,
    auth_method: str = "BIOMETRIC_FINGERPRINT",
    success: bool = True
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.AUTHENTICATION_EVENT.value,
        metadata={
            "authentication_event": 1 if success else 0,
            "auth_method": auth_method,
            "success": success
        }
    )


def create_transaction_completed(
    session_id: str,
    amount: float,
    reference_id: Optional[str] = None
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.TRANSACTION_COMPLETED.value,
        metadata={
            "transaction_completed": True,
            "transaction_amount": float(amount),
            "reference_id": reference_id or "TXN_OK"
        }
    )


def create_transaction_cancelled(
    session_id: str,
    amount: float,
    reason: str = "SECURITY_INTERVENTION_CANCELLED"
) -> DeviceEvent:
    return DeviceEvent(
        session_id=session_id,
        event_type=DeviceEventType.TRANSACTION_CANCELLED.value,
        metadata={
            "transaction_cancelled": True,
            "transaction_amount": float(amount),
            "reason": reason
        }
    )
