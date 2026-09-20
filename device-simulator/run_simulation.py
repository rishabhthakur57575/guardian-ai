"""
GuardianAI - Device Behavioral Event Simulator CLI Runner
==========================================================
Interactive command-line utility to simulate live on-device telemetry sequences
against the GuardianAI FastAPI backend.

Usage:
  python device-simulator/run_simulation.py --scenario legitimate
  python device-simulator/run_simulation.py --scenario scam
  python device-simulator/run_simulation.py --scenario both --delay 0.5
  python device-simulator/run_simulation.py --scenario scam --repeat 3
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, Any

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from events import DeviceEventType
from simulator import DeviceEventSimulator, SimulationStepResult
from scenarios import build_scenario_a_legitimate, build_scenario_b_coached_scam


# ANSI styling
BOLD = "\033[1m"
RESET = "\033[0m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
GRAY = "\033[90m"


def print_banner():
    print(f"""
{CYAN}========================================================================{RESET}
{BOLD}🛡️  GuardianAI — Device Behavioral Telemetry Simulator (Phase 2){RESET}
{GRAY}   Privacy-First On-Device Sentinel Simulation for Remote-Coached Scams{RESET}
{CYAN}========================================================================{RESET}
""")


def print_step_callback(step: int, total: int, event, result: SimulationStepResult):
    status_indicator = f"{GREEN}✓ HTTP {result.status_code}{RESET}" if result.success else f"{RED}✗ FAILED ({result.error_message}){RESET}"
    event_color = YELLOW if "BANKING" in event.event_type else (RED if "SCAM" in str(event.metadata) or event.metadata.get("transaction_amount", 0) > 25000 else CYAN)
    
    print(f"  [{step:02d}/{total:02d}] {event_color}{event.event_type:<24}{RESET} -> {status_indicator}")
    
    # Highlight key contextual metadata
    meta = event.metadata
    details = []
    if "tool_name" in meta:
        details.append(f"Tool: {meta['tool_name']}")
    if "app_name" in meta:
        details.append(f"App: {meta['app_name']}")
    if "beneficiary_label" in meta:
        details.append(f"Beneficiary: {meta['beneficiary_label']}")
    if "transaction_amount" in meta:
        details.append(f"Amount: INR {meta['transaction_amount']:,.0f}")
    if "from_app" in meta and "to_app" in meta:
        details.append(f"Switch: {meta['from_app']} -> {meta['to_app']}")
    if "navigation_back_count" in meta:
        details.append(f"Back clicks: {meta['navigation_back_count']}")
    if "reason" in meta:
        details.append(f"Resolution: {meta['reason']}")

    if details:
        print(f"         {GRAY}↳ {', '.join(details)}{RESET}")


def run_single(simulator: DeviceEventSimulator, scenario_name: str, delay: float, custom_session: str = None, save_trace: str = None):
    scen_title = "SCENARIO A: LEGITIMATE ASSISTANCE" if "legit" in scenario_name.lower() or scenario_name == "a" else "SCENARIO B: COACHED REMOTE SCAM"
    print(f"\n{BOLD}▶ Running: {scen_title}{RESET}")
    print(f"  Target Endpoint : {simulator.events_url}")
    print(f"  Inter-Step Delay: {delay}s\n")

    summary = simulator.run_scenario(
        scenario_name=scenario_name,
        session_id=custom_session,
        delay_seconds=delay,
        on_step=print_step_callback
    )

    final_state = summary.get("final_session_state", {})
    score = final_state.get("risk_score", "N/A")
    level = final_state.get("risk_level", "N/A")

    if level == "THREAT_DETECTED":
        badge = f"{RED}{BOLD}🚨 THREAT DETECTED (High Risk: {score}%){RESET}"
    elif level == "MONITORING":
        badge = f"{YELLOW}{BOLD}⚠️  MONITORING (Elevated Risk: {score}%){RESET}"
    else:
        badge = f"{GREEN}{BOLD}✅ SAFE BASELINE (Score: {score}%){RESET}"

    print(f"\n{BOLD}Session Conclusion:{RESET}")
    print(f"  Session ID   : {CYAN}{summary['session_id']}{RESET}")
    print(f"  Events Sent  : {summary['successful_events']}/{summary['total_events_sent']} successfully ingested")
    print(f"  Status Badge : {badge}")
    if final_state.get("events"):
        print(f"  Total DB Logs: {len(final_state['events'])} events persisted in SQLite")

    if save_trace:
        os.makedirs(os.path.dirname(os.path.abspath(save_trace)), exist_ok=True)
        trace_data = [r.event.to_api_payload() for r in summary["step_results"]]
        with open(save_trace, "w") as f:
            json.dump(trace_data, f, indent=2)
        print(f"  Trace Saved  : {save_trace}")

    return summary


def main():
    parser = argparse.ArgumentParser(description="GuardianAI Device Telemetry Simulator")
    parser.add_argument(
        "--scenario",
        type=str,
        default="scam",
        choices=["legitimate", "scam", "both", "a", "b"],
        help="Predefined scenario to execute ('legitimate', 'scam', or 'both')"
    )
    parser.add_argument(
        "--endpoint",
        type=str,
        default="http://localhost:8000/api",
        help="GuardianAI backend API root URL (default: http://localhost:8000/api)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.6,
        help="Delay in seconds between events for realistic demo visualization (default: 0.6s)"
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Custom session identifier (default: auto-generated)"
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=1,
        help="Number of times to run the simulation (default: 1)"
    )
    parser.add_argument(
        "--save-trace",
        type=str,
        default=None,
        help="Path to export the generated event trace JSON"
    )

    args = parser.parse_args()
    print_banner()

    simulator = DeviceEventSimulator(api_base_url=args.endpoint)

    for run_idx in range(1, args.repeat + 1):
        if args.repeat > 1:
            print(f"\n{BOLD}{CYAN}=== Simulation Iteration {run_idx}/{args.repeat} ==={RESET}")

        if args.scenario in ["both"]:
            run_single(simulator, "legitimate", delay=args.delay, save_trace=args.save_trace)
            time.sleep(1.0)
            run_single(simulator, "scam", delay=args.delay, save_trace=args.save_trace)
        else:
            run_single(
                simulator,
                args.scenario,
                delay=args.delay,
                custom_session=args.session_id,
                save_trace=args.save_trace
            )


if __name__ == "__main__":
    main()
