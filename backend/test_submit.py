import urllib.request
import json

body = json.dumps({
    "title": "EcoTrack",
    "description": "An AI-powered app that tracks personal carbon footprint from daily activities and suggests eco-friendly alternatives",
    "target_market": "Climate-conscious consumers",
    "region": "India",
    "sector": "CleanTech"
}).encode()

req = urllib.request.Request(
    "http://127.0.0.1:8000/ideas/",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST"
)
r = urllib.request.urlopen(req)
data = json.loads(r.read())
print(json.dumps(data, indent=2))
print(f"\nIDEA_ID = {data['id']}")
