import urllib.request
import json
import time

base_url = "http://localhost:8000/ideas/"
payload = {
    "title": "Autonomous Drone Delivery",
    "description": "Drones that deliver coffee to developers autonomously",
    "target_market": "Tech Offices",
    "region": "US",
    "sector": "Logistics"
}

req = urllib.request.Request(
    base_url, 
    data=json.dumps(payload).encode('utf-8'), 
    headers={'Content-Type': 'application/json'}
)

print("Starting pipeline test...")
with urllib.request.urlopen(req) as response:
    post_res = json.loads(response.read().decode('utf-8'))
    idea_id = post_res['id']
    print(f"Created Idea ID: {idea_id}")

done = False
while not done:
    time.sleep(1.5) # Polling interval
    with urllib.request.urlopen(base_url + idea_id) as response:
        idea = json.loads(response.read().decode('utf-8'))
        
        print(f"\nIdea Status: {idea['status']}")
        
        all_agents_done = True
        for agent in idea.get('agent_outputs', []):
            print(f"  - {agent['agent_name']}: {agent['status']}")
            if agent['status'] != 'done':
                all_agents_done = False
                
        if idea['status'] in ['done', 'error']:
            done = True
            print("\nPipeline finished!")
            break
