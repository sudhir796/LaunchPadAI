import asyncio
from collections import defaultdict

# Mapping from idea_id to a list of asyncio.Queue
queues = defaultdict(list)

async def subscribe(idea_id: str):
    q = asyncio.Queue()
    queues[idea_id].append(q)
    try:
        while True:
            event = await q.get()
            yield event
            if event.get("status") == "error" or event.get("agent_name") == "investor_matching":
                break
    finally:
        queues[idea_id].remove(q)
        if not queues[idea_id]:
            del queues[idea_id]

def publish(idea_id: str, event: dict):
    if idea_id in queues:
        for q in queues[idea_id]:
            q.put_nowait(event)
