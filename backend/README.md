# LaunchPad AI - Backend

This is the FastAPI backend for the LaunchPad AI multi-agent pipeline. It handles the orchestration of the 7 validation agents, maintains pipeline state in a SQLite database, and provides real-time streaming updates to the frontend via Server-Sent Events (SSE).

## 🚀 Getting Started

### 1. Environment Variables
Create a `.env` file in the `/backend/` directory with the following keys:
```env
# Search API Key (used for web & patent search)
TAVILY_API_KEY=your_tavily_api_key

# LLM API Keys (used for synthesizing search data)
GEMINI_API_KEY=your_gemini_api_key
```

### 2. Run the Server Locally
Ensure you have the required dependencies installed (FastAPI, Uvicorn, SQLAlchemy, httpx, google-genai, etc.).
Run the server using Uvicorn:
```bash
python -m uvicorn main:app --port 8000 --reload
```
The API will be available at `http://127.0.0.1:8000`.

---

## 📜 Agent Data Contracts

**IMPORTANT:** The source of truth for all JSON data contracts (what each agent expects as input and what it must output) is located in **`AGENTS.md` (Section 4)** in the root folder. 
If you modify an agent's structure, you MUST coordinate with the frontend team and update `AGENTS.md`.

---

## 🌐 API Endpoints

### 1. Submit a New Idea
Starts the multi-agent validation pipeline in the background.
```bash
curl -X POST "http://127.0.0.1:8000/ideas/" \
     -H "Content-Type: application/json" \
     -d '{"title": "Handloom Global", "description": "AI platform connecting weavers to global buyers", "target_market": "Textiles", "region": "India"}'
```
**Response:**
```json
{
  "id": "4198fcc1-3c0a-499d-9cb4-2413fbd27e74",
  "title": "Handloom Global",
  "status": "pending",
  "created_at": "2026-07-27T17:38:00Z"
}
```

### 2. Stream Live Pipeline Updates (SSE)
Connect to this endpoint to receive real-time Server-Sent Events as each agent completes its work.
```bash
curl -N "http://127.0.0.1:8000/ideas/4198fcc1-3c0a-499d-9cb4-2413fbd27e74/stream"
```
**Response Stream:**
```text
data: {"agent_name": "market_research", "status": "done", "output": {"market_size_estimate": "...", ...}}
```

### 3. Get Idea Status
Check the high-level status of the pipeline (pending, running, done, error).
```bash
curl "http://127.0.0.1:8000/ideas/4198fcc1-3c0a-499d-9cb4-2413fbd27e74"
```

### 4. Get Specific Agent Output
Retrieve the JSON output of a specific completed agent.
```bash
curl "http://127.0.0.1:8000/ideas/4198fcc1-3c0a-499d-9cb4-2413fbd27e74/agents/market_research"
```
**Response:**
```json
{
  "id": "ec2aa0ca-80b2-4871-842a-98ad133224ba",
  "idea_id": "4198fcc1-3c0a-499d-9cb4-2413fbd27e74",
  "agent_name": "market_research",
  "status": "done",
  "output_json": { ... }
}
```

### 5. Retry a Failed Agent
If an external API goes down and triggers fallback data, you can selectively re-run that single agent later without restarting the whole pipeline.
```bash
curl -X POST "http://127.0.0.1:8000/ideas/4198fcc1-3c0a-499d-9cb4-2413fbd27e74/retry/market_research"
```
**Response:**
```json
{
  "status": "retry_started",
  "idea_id": "4198fcc1-3c0a-499d-9cb4-2413fbd27e74",
  "agent_name": "market_research"
}
```
