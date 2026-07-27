# LaunchPad AI — Idea-to-Investor Multi-Agent Startup Accelerator

This file is the shared context document for this project. Every team member's Antigravity agent should read this file before starting work, so all three of you are building against the same architecture, data contracts, and conventions — even though you're working in separate branches/workspaces.

---

## 1. Problem Statement

Student entrepreneurs at innovation-driven institutions often have promising ideas but lack structured guidance to move from concept to a fundable venture. Validating an idea, understanding its market and competitive landscape, checking patentability, structuring a business model, and building an investor-ready pitch all require different expertise most students don't have access to — usually needing mentors, market reports, or paid tools. This fragmented, expertise-heavy process discourages students from pursuing viable ideas or leads to poorly validated startups reaching incubation. There's no single intelligent system that takes a raw idea and autonomously guides it through validation, research, and pitch-readiness.

**Goal:** A student submits a raw startup idea. A pipeline of 7 AI agents autonomously validates, researches, and packages it into an investor-ready pitch.

---

## 2. Team Ownership

| Area | Owner | Folder |
|---|---|---|
| Agent logic (all 7 agents) | You | `/agents/` |
| Backend, DB, orchestration, search integration | Teammate A | `/backend/` |
| Frontend UI, results display, demo prep | Teammate B | `/frontend/` |

**Rule:** Work only inside your own folder unless coordinating a shared interface change. If you need to change something outside your folder (e.g., the contract below), flag it to the team first — don't silently change a shape another agent depends on.

---

## 3. Pipeline / Data Flow

Agents run in this sequence. Each agent's output feeds into later agents as noted.

```
Idea Input
   -> Agent 1: Idea Validator
   -> Agent 2: Patent & Prior Art Search
   -> Agent 3: Market Research
   -> Agent 4: Competitor Analysis (uses Agent 3 output)
   -> Agent 5: Business Model Generator (uses Agent 3 + 4 output)
   -> Agent 6: Pitch Deck Generator (uses all prior outputs)
   -> Agent 7: Investor Matching (uses Agent 5 output)
   -> Final Report / Pitch Deck delivered to user
```

Every agent takes JSON in, returns JSON out. The backend is responsible for calling agents in order and passing prior outputs forward. The frontend displays each stage's result as it completes (sequential reveal, not one big wait).

---

## 4. Agent Contracts

### Agent 1 — Idea Validator Agent
**Domain:** NLP / Reasoning & Evaluation

Input:
```json
{
  "idea_id": "string",
  "idea_title": "string",
  "idea_description": "string",
  "target_market": "string (optional)"
}
```
Output:
```json
{
  "idea_id": "string",
  "validation_score": "number (0-100)",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "feasibility_notes": "string",
  "recommendation": "string"
}
```

### Agent 2 — Patent & Prior Art Search Agent
**Domain:** Information Retrieval / IP Research

Input:
```json
{
  "idea_id": "string",
  "idea_description": "string",
  "keywords": ["string"]
}
```
Output:
```json
{
  "idea_id": "string",
  "similar_patents": [
    { "title": "string", "summary": "string", "source_url": "string" }
  ],
  "risk_level": "string (low/medium/high)",
  "notes": "string"
}
```

### Agent 3 — Market Research Agent
**Domain:** Information Retrieval + Data Analytics

Input:
```json
{
  "idea_id": "string",
  "idea_description": "string",
  "target_market": "string",
  "region": "string (optional)"
}
```
Output:
```json
{
  "idea_id": "string",
  "market_size_estimate": "string",
  "growth_trends": "string",
  "target_demographics": "string",
  "sources": ["string (urls)"]
}
```

### Agent 4 — Competitor Analysis Agent
**Domain:** Information Retrieval + Comparative NLP Analysis

Input:
```json
{
  "idea_id": "string",
  "idea_description": "string",
  "market_research": "{ output object from Agent 3 }"
}
```
Output:
```json
{
  "idea_id": "string",
  "competitors": [
    { "name": "string", "description": "string", "strengths": "string", "weaknesses": "string", "source_url": "string" }
  ],
  "differentiation_opportunities": "string"
}
```

### Agent 5 — Business Model Generator Agent
**Domain:** NLP / Strategic Reasoning

Input:
```json
{
  "idea_id": "string",
  "idea_description": "string",
  "market_research": "{ output object from Agent 3 }",
  "competitor_analysis": "{ output object from Agent 4 }"
}
```
Output:
```json
{
  "idea_id": "string",
  "revenue_streams": ["string"],
  "cost_structure": ["string"],
  "value_proposition": "string",
  "customer_segments": ["string"],
  "channels": ["string"]
}
```

### Agent 6 — Pitch Deck Generator Agent
**Domain:** NLP + Generative Content Creation

Input:
```json
{
  "idea_id": "string",
  "idea_validation": "{ output object from Agent 1 }",
  "market_research": "{ output object from Agent 3 }",
  "competitor_analysis": "{ output object from Agent 4 }",
  "business_model": "{ output object from Agent 5 }"
}
```
Output:
```json
{
  "idea_id": "string",
  "slides": [
    { "title": "string", "content": "string" }
  ]
}
```

### Agent 7 — Investor Matching Agent
**Domain:** Information Retrieval + Recommendation Systems

Input:
```json
{
  "idea_id": "string",
  "sector": "string",
  "business_model": "{ output object from Agent 5 }"
}
```
Output:
```json
{
  "idea_id": "string",
  "matched_investors": [
    { "name": "string", "focus_area": "string", "reason": "string" }
  ]
}
```

---

## 5. Folder Structure (proposed)

```
/agents/
  idea_validator.py (or .js)
  patent_search.py
  market_research.py
  competitor_analysis.py
  business_model.py
  pitch_deck.py
  investor_matching.py
/backend/
  api routes, orchestration logic, database models
/frontend/
  submission form, sequential results display, pitch deck view
AGENTS.md   <- this file
```

*(Tech stack — language/framework for backend and frontend — to be finalized by the team; update this section once decided so Antigravity has an accurate reference.)*

---

## 6. Git Workflow

- `main` = stable, always demo-able
- Work happens on individual branches, e.g. `agents/idea-validator`, `backend/integration`, `frontend/ui`
- Open a PR into `main` when a piece works; merge after a quick check — never push directly to `main`
- Daily sync: pull all branches together once a day and test the full pipeline end-to-end

---

## 7. Notes for Agents 2, 3, 4, and 7

These four agents depend on real web/data retrieval to avoid hallucinated numbers (fake market sizes, fake competitor names). Wire these to actual search/API calls rather than pure LLM guessing — this is the highest-risk part of the build and should be tested early, not left to the last day.
