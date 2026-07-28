# STUB - replace with real logic, see AGENTS.md section 4 for contract
import asyncio

async def run(input: dict) -> dict:
    await asyncio.sleep(1)
    return {
        "idea_id": input.get("idea_id", "test-id"),
        "similar_patents": [
            {
                "title": "System and method for automated startup validation",
                "summary": "A system that uses NLP to validate business ideas and generate reports.",
                "source_url": "https://patents.google.com/patent/US2020123456A1"
            },
            {
                "title": "Machine learning based market analysis tool",
                "summary": "Generates market demographic data and competitor analysis automatically from text inputs.",
                "source_url": "https://patents.google.com/patent/US2019987654B2"
            }
        ],
        "risk_level": "medium",
        "notes": "There are some existing patents in the automated business intelligence space, but the specific pipeline approach appears novel. A freedom-to-operate analysis is recommended before commercialization."
    }
