from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ==========================================
# Database Record Schemas
# ==========================================

class IdeaBase(BaseModel):
    title: str
    description: str
    target_market: Optional[str] = None
    region: Optional[str] = None
    sector: Optional[str] = None

class IdeaCreate(IdeaBase):
    pass

class IdeaResponse(IdeaBase):
    id: str
    status: str
    created_at: datetime
    investor_readiness_score: Optional[float] = None
    star_rating: Optional[int] = None
    
    class Config:
        from_attributes = True

class AgentOutputResponse(BaseModel):
    id: str
    idea_id: str
    agent_name: str
    output_json: Optional[Dict[str, Any]] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IdeaDetailResponse(IdeaResponse):
    agent_outputs: List[AgentOutputResponse] = []

# ==========================================
# Agent Contract Schemas (from AGENTS.md)
# ==========================================

# --- Agent 1: Idea Validator ---
class IdeaValidatorInput(BaseModel):
    idea_id: str
    idea_title: str
    idea_description: str
    target_market: Optional[str] = None

class IdeaValidatorOutput(BaseModel):
    idea_id: str
    validation_score: float = Field(..., ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    feasibility_notes: str
    recommendation: str

# --- Agent 2: Patent & Prior Art Search ---
class PatentInfo(BaseModel):
    title: str
    summary: str
    source_url: str

class PatentSearchInput(BaseModel):
    idea_id: str
    idea_description: str
    keywords: List[str]

class PatentSearchOutput(BaseModel):
    idea_id: str
    similar_patents: List[PatentInfo]
    risk_level: str
    notes: str

# --- Agent 3: Market Research ---
class MarketResearchInput(BaseModel):
    idea_id: str
    idea_description: str
    target_market: str
    region: Optional[str] = None

class MarketResearchOutput(BaseModel):
    idea_id: str
    market_size_estimate: str
    growth_trends: str
    target_demographics: str
    sources: List[str]

# --- Agent 4: Competitor Analysis ---
class CompetitorInfo(BaseModel):
    name: str
    description: str
    strengths: str
    weaknesses: str
    source_url: str

class CompetitorAnalysisInput(BaseModel):
    idea_id: str
    idea_description: str
    market_research: MarketResearchOutput

class CompetitorAnalysisOutput(BaseModel):
    idea_id: str
    competitors: List[CompetitorInfo]
    differentiation_opportunities: str

# --- Agent 5: Business Model Generator ---
class BusinessModelInput(BaseModel):
    idea_id: str
    idea_description: str
    market_research: MarketResearchOutput
    competitor_analysis: CompetitorAnalysisOutput

class BusinessModelOutput(BaseModel):
    idea_id: str
    revenue_streams: List[str]
    cost_structure: List[str]
    value_proposition: str
    customer_segments: List[str]
    channels: List[str]

# --- Agent 6: Pitch Deck Generator ---
class Slide(BaseModel):
    title: str
    content: str

class PitchDeckInput(BaseModel):
    idea_id: str
    idea_validation: IdeaValidatorOutput
    market_research: MarketResearchOutput
    competitor_analysis: CompetitorAnalysisOutput
    business_model: BusinessModelOutput

class PitchDeckOutput(BaseModel):
    idea_id: str
    slides: List[Slide]

# --- Agent 7: Investor Matching ---
class InvestorInfo(BaseModel):
    name: str
    focus_area: str
    reason: str

class InvestorMatchingInput(BaseModel):
    idea_id: str
    sector: str
    business_model: BusinessModelOutput

class InvestorMatchingOutput(BaseModel):
    idea_id: str
    matched_investors: List[InvestorInfo]
    investor_readiness_score: Optional[float] = None
    star_rating: Optional[int] = None
