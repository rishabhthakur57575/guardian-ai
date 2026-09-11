from datetime import datetime
import json
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class SessionModel(Base):
    __tablename__ = "sessions"

    session_id = Column(String(64), primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    risk_score = Column(Float, default=0.0, nullable=False)
    risk_level = Column(String(32), default="SAFE", nullable=False) # SAFE, MONITORING, THREAT_DETECTED
    final_outcome = Column(String(32), default="ACTIVE", nullable=False) # ACTIVE, INTERRUPTED, ALLOWED, COMPLETED

    events = relationship("EventModel", back_populates="session", cascade="all, delete-orphan", order_by="EventModel.timestamp")
    interventions = relationship("InterventionModel", back_populates="session", cascade="all, delete-orphan", order_by="InterventionModel.timestamp")

class EventModel(Base):
    __tablename__ = "events"

    event_id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_type = Column(String(64), nullable=False, index=True)
    # metadata stored as JSON string (privacy-first: only behavioural telemetry)
    metadata_json = Column(Text, default="{}", nullable=False)

    session = relationship("SessionModel", back_populates="events")

    @property
    def event_metadata(self):
        try:
            return json.loads(self.metadata_json)
        except Exception:
            return {}

    @event_metadata.setter
    def event_metadata(self, val):
        self.metadata_json = json.dumps(val)

class InterventionModel(Base):
    __tablename__ = "interventions"

    intervention_id = Column(String(64), primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    risk_score = Column(Float, default=0.0, nullable=False)
    action = Column(String(64), default="WARNING_DISPLAYED", nullable=False) # WARNING_DISPLAYED, TRANSACTION_HALTED
    user_response = Column(String(64), default="PENDING", nullable=False) # CANCEL_TRANSACTION, TRUST_USER, PENDING

    session = relationship("SessionModel", back_populates="interventions")
