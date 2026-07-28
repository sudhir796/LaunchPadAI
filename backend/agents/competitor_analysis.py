# STUB - replace with real logic, see AGENTS.md section 4 for contract
import asyncio

async def run(input: dict) -> dict:
    await asyncio.sleep(1)
    return {
        "idea_id": input.get("idea_id", "test-id"),
        "competitors": [
            {
                "name": "IdeaCheck AI",
                "description": "A web app that provides simple scoring for startup ideas using ChatGPT.",
                "strengths": "Fast, cheap, easy to use.",
                "weaknesses": "Lacks deep market research and doesn't generate pitch decks.",
                "source_url": "https://ideacheck.ai.example"
            },
            {
                "name": "FounderBot",
                "description": "Telegram bot that asks founders questions to validate their ideas.",
                "strengths": "High engagement through chat interface.",
                "weaknesses": "Only provides generic advice, no data-backed research.",
                "source_url": "https://founderbot.example"
            }
        ],
        "differentiation_opportunities": "Focus on the end-to-end pipeline. While competitors only score ideas, LaunchPad AI can provide a full suite of patent search, market sizing, and an investor-ready pitch deck."
    }
