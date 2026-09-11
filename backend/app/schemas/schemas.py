from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

FORBIDDEN_PRIVACY_KEYS = {
    "password", "otp", "pin", "cvv", "pan", "aadhar", "account_number",
    "card_number", "screenshot", "image_data", "raw_keystrokes",
    "secret", "token", "auth_header"
}

class EventBase(BaseModel):
    event_type: str = Field(..., description="Type of behavioural telemetry event")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Behavioural metadata strictly without PII")

    @field_validator("metadata")
    def validate_privacy(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        lowered_keys = {k.lower() for k in v.keys()}
        violation = lowered_keys.intersection(FORBIDDEN_PRIVACY_KEYS)
        if violation:
            raise ValueError(f"Privacy violation: sensitive keys prohibited: {list(violation)}")
        return v

class EventCreate(EventBase):
    session_id: str = Field(..., description="Session identifier")
    timestamp: Optional[datetime] = None

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: str
    session_id: str
    timestamp: datetime
    event_type: str
    metadata: Dict[str, Any]

class RiskScoreRequest(BaseModel):
    session_id: str
    events: Optional[List[EventBase]] = None

class RiskFactor(BaseModel):
    name: str
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    weight: float

class RiskScoreResponse(BaseModel):
    session_id: str
    risk_score: float = Field(..., description="Risk score between 0.0 and 100.0")
    risk_level: str = Field(..., description="SAFE, MONITORING, THREAT_DETECTED")
    reasons: List[str]
    risk_factors: List[RiskFactor]
    recommended_action: str # NONE, MONITOR, INTERVENE
    evaluated_at: datetime

class InterventionCreate(BaseModel):
    session_id: str
    risk_score: float
    action: str = "WARNING_DISPLAYED"
    user_response: str = "PENDING" # CANCEL_TRANSACTION, TRUST_USER, PENDING

class InterventionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    intervention_id: str
    session_id: str
    timestamp: datetime
    risk_score: float
    action: str
    user_response: str

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    risk_score: float
    risk_level: str
    final_outcome: str
    events: List[EventResponse] = []
    interventions: List[InterventionResponse] = []

class SessionSummary(BaseModel):
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    risk_score: float
    risk_level: str
    final_outcome: str
    event_count: int

class AnalyticsMetrics(BaseModel):
    today_protected_sessions: int
    threats_detected: int
    transactions_interrupted: int
    total_interrupted_amount_inr: float
    average_risk_score: float
    system_status: str

class PatternFrequency(BaseModel):
    pattern_name: str
    count: int
    percentage: float

class RiskDistribution(BaseModel):
    range: str # e.g. "0-20", "21-40", etc.
    count: int

class AnalyticsResponse(BaseModel):
    metrics: AnalyticsMetrics
    protected_sessions_timeline: List[Dict[str, Any]]
    scam_pattern_frequencies: List[PatternFrequency]
    risk_distribution: List[RiskDistribution]
    intervention_outcomes: Dict[str, int]
