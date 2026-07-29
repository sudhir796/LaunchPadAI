export interface BaseAgentInput {
  idea_id: string;
}

// ==========================================
// Agent 1: Idea Validator
// ==========================================
export interface Agent1Input extends BaseAgentInput {
  idea_title: string;
  idea_description: string;
  target_market?: string;
}

export interface Agent1Output extends BaseAgentInput {
  validation_score: number; // 0-100
  strengths: string[];
  weaknesses: string[];
  feasibility_notes: string;
  recommendation: string;
}

// ==========================================
// Agent 2: Patent & Prior Art Search
// ==========================================
export interface Agent2Input extends BaseAgentInput {
  idea_description: string;
  keywords: string[];
}

export interface SimilarPatent {
  title: string;
  summary: string;
  source_url: string;
}

export interface Agent2Output extends BaseAgentInput {
  similar_patents: SimilarPatent[];
  risk_level: 'low' | 'medium' | 'high' | string;
  notes: string;
  sources?: string[];
}

// ==========================================
// Agent 3: Market Research
// ==========================================
export interface Agent3Input extends BaseAgentInput {
  idea_description: string;
  target_market: string;
  region?: string;
}

export interface Agent3Output extends BaseAgentInput {
  market_size_estimate: string;
  growth_trends: string;
  target_demographics: string;
  sources: string[];
}

// ==========================================
// Agent 4: Competitor Analysis
// ==========================================
export interface Agent4Input extends BaseAgentInput {
  idea_description: string;
  market_research: Agent3Output;
}

export interface Competitor {
  name: string;
  description: string;
  strengths: string;
  weaknesses: string;
  source_url: string;
}

export interface Agent4Output extends BaseAgentInput {
  competitors: Competitor[];
  differentiation_opportunities: string;
  sources?: string[];
}

// ==========================================
// Agent 5: Business Model Generator
// ==========================================
export interface Agent5Input extends BaseAgentInput {
  idea_description: string;
  market_research: Agent3Output;
  competitor_analysis: Agent4Output;
}

export interface Agent5Output extends BaseAgentInput {
  revenue_streams: string[];
  cost_structure: string[];
  value_proposition: string;
  customer_segments: string[];
  channels: string[];
  sources?: string[];
}

// ==========================================
// Agent 6: Pitch Deck Generator
// ==========================================
export interface Agent6Input extends BaseAgentInput {
  idea_validation: Agent1Output;
  market_research: Agent3Output;
  competitor_analysis: Agent4Output;
  business_model: Agent5Output;
}

export interface PitchSlide {
  title: string;
  content: string;
}

export interface Agent6Output extends BaseAgentInput {
  slides: PitchSlide[];
  sources?: string[];
}

// ==========================================
// Agent 7: Investor Matching
// ==========================================
export interface Agent7Input extends BaseAgentInput {
  sector: string;
  business_model: Agent5Output;
}

export interface MatchedInvestor {
  name: string;
  focus_area: string;
  reason: string;
}

export interface Agent7Output extends BaseAgentInput {
  matched_investors: MatchedInvestor[];
  sources?: string[];
  investor_readiness_score?: number;
  star_rating?: number;
}

// ==========================================
// Pipeline Combined State
// ==========================================
export interface PipelineState {
  idea_id: string | null;
  idea_title: string;
  idea_description: string;
  target_market: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  currentStage: number; // 0 to 7
  agentStates: {
    [key: number]: 'queued' | 'running' | 'completed' | 'failed';
  };
  agentOutputs: {
    agent1: Agent1Output | null;
    agent2: Agent2Output | null;
    agent3: Agent3Output | null;
    agent4: Agent4Output | null;
    agent5: Agent5Output | null;
    agent6: Agent6Output | null;
    agent7: Agent7Output | null;
  };
}
