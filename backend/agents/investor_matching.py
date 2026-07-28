# STUB - replace with real logic, see AGENTS.md section 4 for contract
import asyncio

async def run(input: dict) -> dict:
    await asyncio.sleep(1)
    return {
        "idea_id": input.get("idea_id", "test-id"),
        "matched_investors": [
            {
                "name": "Sequoia Capital (Seed Fund)",
                "focus_area": "Early-stage AI and B2B SaaS",
                "reason": "Strong track record of funding AI productivity tools and startup infrastructure."
            },
            {
                "name": "Y Combinator",
                "focus_area": "Agnostic, early-stage startups",
                "reason": "Perfect fit for tools that accelerate founder productivity and validate ideas."
            },
            {
                "name": "Dorm Room Fund",
                "focus_area": "Student-led startups",
                "reason": "Directly aligned with the target demographic of student entrepreneurs."
            }
        ]
    }
