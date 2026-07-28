import urllib.request
import json

base_url = "http://localhost:8000/ideas/"
payload = {
    "title": "AI Startup",
    "description": "An AI that builds AI",
    "target_market": "Developers",
    "region": "Global",
    "sector": "Tech"
}

req = urllib.request.Request(
    base_url, 
    data=json.dumps(payload).encode('utf-8'), 
    headers={'Content-Type': 'application/json'}
)

print("--- POST /ideas output ---")
try:
    with urllib.request.urlopen(req) as response:
        post_res = json.loads(response.read().decode('utf-8'))
        print(json.dumps(post_res, indent=2))
        idea_id = post_res['id']
except Exception as e:
    print(e)

print("\n--- GET /ideas output ---")
try:
    with urllib.request.urlopen(base_url) as response:
        print(json.dumps(json.loads(response.read().decode('utf-8')), indent=2))
except Exception as e:
    print(e)

print("\n--- GET /ideas/{idea_id} output ---")
try:
    with urllib.request.urlopen(base_url + idea_id) as response:
        print(json.dumps(json.loads(response.read().decode('utf-8')), indent=2))
except Exception as e:
    print(e)

print("\n--- GET /ideas/{idea_id}/agents/idea_validator output ---")
try:
    with urllib.request.urlopen(base_url + idea_id + "/agents/idea_validator") as response:
        print(json.dumps(json.loads(response.read().decode('utf-8')), indent=2))
except Exception as e:
    print(e)
