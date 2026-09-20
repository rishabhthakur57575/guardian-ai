"""
GuardianAI - Device Event Simulator Engine
===========================================
Emits realistic behavioural event streams to POST /api/events.
Supports configurable timing pacing for live demonstrations and repeatable demo runs.
"""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Callable
import requests

import os
import sys

# Support direct execution and relative package import
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from events import DeviceEvent
from scenarios import (
    build_scenario_a_legitimate,
    build_scenario_b_coached_scam,
    get_scenario
)

logger = logging.getLogger("guardianai.simulator")


class SimulationStepResult:
    def __init__(
        self,
        event: DeviceEvent,
        status_code: int,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        self.event = event
        self.status_code = status_code
        self.response_data = response_data or {}
        self.error_message = error_message

    @property
    def success(self) -> bool:
        return 200 <= self.status_code < 300 and not self.error_message


class DeviceEventSimulator:
    """
    Orchestrates device behavioural event emissions to GuardianAI backend.
    """
    def __init__(
        self,
        api_base_url: str = "http://localhost:8000/api",
        timeout: float = 10.0
    ):
        self.api_base_url = api_base_url.rstrip("/")
        self.events_url = f"{self.api_base_url}/events"
        self.timeout = timeout
        self.session = requests.Session()

    def send_event(self, event: DeviceEvent) -> SimulationStepResult:
        """Transmits a single DeviceEvent to POST /api/events."""
        payload = event.to_api_payload()
        try:
            resp = self.session.post(
                self.events_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}

            return SimulationStepResult(
                event=event,
                status_code=resp.status_code,
                response_data=data,
                error_message=None if resp.ok else f"HTTP {resp.status_code}: {resp.text}"
            )
        except requests.RequestException as exc:
            return SimulationStepResult(
                event=event,
                status_code=0,
                error_message=f"Connection failure to {self.events_url}: {exc}"
            )

    def run_scenario(
        self,
        scenario_name: str,
        session_id: Optional[str] = None,
        delay_seconds: float = 0.5,
        on_step: Optional[Callable[[int, int, DeviceEvent, SimulationStepResult], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes a complete scenario against the ingestion API.

        Parameters:
        -----------
        scenario_name : 'legitimate' (Scenario A) or 'scam' (Scenario B)
        session_id : Optional unique session ID. If None, auto-generated.
        delay_seconds : Pause between event transmissions (useful for live presentations).
        on_step : Callback invoked after each step: on_step(index, total, event, result).

        Returns:
        --------
        Structured summary of the completed simulation run.
        """
        if not session_id:
            tag = "legit" if "legit" in scenario_name.lower() or scenario_name.lower() == "a" else "scam"
            session_id = f"sim-{tag}-{uuid.uuid4().hex[:8]}"

        events = get_scenario(scenario_name, session_id=session_id)
        total_events = len(events)
        step_results: List[SimulationStepResult] = []
        risk_score_history: List[float] = []
        risk_level_history: List[str] = []

        for idx, event in enumerate(events):
            result = self.send_event(event)
            step_results.append(result)

            if on_step:
                on_step(idx + 1, total_events, event, result)

            if delay_seconds > 0 and idx < total_events - 1:
                time.sleep(delay_seconds)

        # Query final session state from backend
        final_session_state = self._fetch_session_summary(session_id)

        return {
            "session_id": session_id,
            "scenario": scenario_name,
            "total_events_sent": total_events,
            "successful_events": sum(1 for r in step_results if r.success),
            "final_session_state": final_session_state,
            "step_results": step_results
        }

    def _fetch_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Fetches final risk score & status from GET /api/session/{session_id}."""
        url = f"{self.api_base_url}/session/{session_id}"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.ok:
                return resp.json()
        except Exception as e:
            logger.debug("Could not fetch session summary for %s: %s", session_id, e)
        return {}
