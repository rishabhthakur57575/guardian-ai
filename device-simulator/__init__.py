"""
GuardianAI - Device Event Simulator Package
"""
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

from events import (
    DeviceEventType,
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
from scenarios import (
    build_scenario_a_legitimate,
    build_scenario_b_coached_scam,
    get_scenario
)
from simulator import DeviceEventSimulator, SimulationStepResult
