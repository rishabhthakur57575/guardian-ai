import urllib.request
import json

BASE = 'http://127.0.0.1:8000/api'

def post_json(url, data=None):
    req = urllib.request.Request(url, method='POST')
    if data is not None:
        req.add_header('Content-Type', 'application/json')
        body = json.dumps(data).encode('utf-8')
        req.data = body
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_json(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode('utf-8'))

print("=== 1. Health ===")
print(get_json(f"{BASE}/health"))

print("=== 2. Reset Simulator ===")
print(post_json(f"{BASE}/simulator/reset?session_id=demo-session-live"))

print("=== 3. Advancing 6 Steps ===")
for i in range(1, 7):
    res = post_json(f"{BASE}/simulator/step?session_id=demo-session-live")
    step_num = res.get('current_step')
    step_name = res.get('step_name')
    risk_info = res.get('risk', {})
    print(f"Step {step_num}/6: {step_name} -> Risk Score: {risk_info.get('risk_score')}% ({risk_info.get('risk_level')})")

print("=== 4. Posting Intervention Cancel ===")
inv_res = post_json(f"{BASE}/intervention", {
    "session_id": "demo-session-live",
    "risk_score": 94.0,
    "action": "TRANSACTION_HALTED",
    "user_response": "CANCEL_TRANSACTION"
})
print("Intervention Response:", inv_res)

print("=== 5. Verifying Final Session State ===")
sess_res = get_json(f"{BASE}/session/demo-session-live")
print(f"Session: {sess_res['session_id']}, Final Outcome: {sess_res['final_outcome']}, Risk: {sess_res['risk_score']}%, Events: {len(sess_res['events'])}")

print("=== 6. Resetting Simulator for Live UI Demo ===")
reset_res = post_json(f"{BASE}/simulator/reset?session_id=demo-session-live")
print(reset_res)
