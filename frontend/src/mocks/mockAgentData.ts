import {
  Agent1Output,
  Agent2Output,
  Agent3Output,
  Agent4Output,
  Agent5Output,
  Agent6Output,
  Agent7Output
} from '../types/agentContracts';

export const MOCK_PROJECT = {
  idea_id: "solargrid-001",
  idea_title: "SolarGrid",
  idea_description: "SolarGrid is a peer-to-peer neighborhood solar energy microgrid sharing platform that allows homeowners with solar panels to sell surplus energy directly to their neighbors using automated smart contracts, reducing dependency on central utility companies and optimizing local energy grids.",
  target_market: "Suburban residential neighborhoods with high solar panel adoption"
};

export const mockAgent1Data: Agent1Output = {
  idea_id: MOCK_PROJECT.idea_id,
  validation_score: 87,
  strengths: [
    "High incentive alignment for both solar producers (higher sell rates) and consumers (lower buy rates).",
    "Localized power distribution reduces grid transmission losses.",
    "Growing consumer interest in sustainable, community-backed green initiatives."
  ],
  weaknesses: [
    "Regulatory hurdles in utility franchising laws and grid-interconnection policies.",
    "Initial setup cost for hardware meters and local storage controllers.",
    "Dependence on regional solar density and weather patterns."
  ],
  feasibility_notes: "Strong technical feasibility but high political/regulatory risk. Net-metering laws vary widely by state and municipality. A sandbox test run in a cooperative-friendly utility state like Texas or Colorado is highly recommended before scale.",
  recommendation: "PROCEED WITH REGIONAL SANDBOX. Focus on establishing utility partnerships or targeting municipal-owned utilities where regulations are more flexible."
};

export const mockAgent2Data: Agent2Output = {
  idea_id: MOCK_PROJECT.idea_id,
  similar_patents: [
    {
      title: "System and method for peer-to-peer energy transaction",
      summary: "A system for peer-to-peer transactions of power among nodes on a grid, using distributed ledgers to settle accounts and dispatch energy flows based on smart contract rules.",
      source_url: "https://patents.google.com/patent/US1054321A1"
    },
    {
      title: "Decentralized power grid balancing network",
      summary: "An automated system using IoT endpoints to adjust local load consumption in response to micro-generation supply spikes across residential sub-stations.",
      source_url: "https://patents.google.com/patent/US1189423B2"
    }
  ],
  risk_level: "medium",
  notes: "While basic peer-to-peer energy transaction protocols are patented, SolarGrid's specific implementation of local neighbor-to-neighbor balancing with community storage prioritization represents patentable novelty. Ensure that smart contract implementation uses public domain protocols to avoid infringement."
};

export const mockAgent3Data: Agent3Output = {
  idea_id: MOCK_PROJECT.idea_id,
  market_size_estimate: "$14.2 Billion TAM by 2030",
  growth_trends: "The residential solar market is growing at a 15% annual rate, driven by federal tax credits (ITC) and net metering reductions. P2P energy sharing market is emerging as consumers seek energy independence in high-outage zones (18.4% CAGR).",
  target_demographics: "Middle-to-upper-class homeowners (aged 30-65) in high-solar states (CA, TX, AZ, FL, CO) who own solar setups or wish to buy local clean energy without installing panels.",
  sources: [
    "https://www.nrel.gov/docs/fy23osti/84511.pdf",
    "https://www.iea.org/reports/solar-pv",
    "https://www.ferc.gov/industries-data/electric"
  ]
};

export const mockAgent4Data: Agent4Output = {
  idea_id: MOCK_PROJECT.idea_id,
  competitors: [
    {
      name: "Power Ledger",
      description: "An established Australian company offering blockchain-based P2P energy trading software platforms to commercial utilities.",
      strengths: "Early market entry, global utility trials, robust software architecture.",
      weaknesses: "Primarily business-to-utility focus, low direct consumer brand equity, complex integration cycles.",
      source_url: "https://www.powerledger.io"
    },
    {
      name: "LO3 Energy",
      description: "Pioneered the Brooklyn Microgrid, developing software solutions that enable local community microgrids.",
      strengths: "First-mover consumer microgrid trials, strong community engagement.",
      weaknesses: "Slower global scale, high dependency on localized hardware deployments, closed partner network.",
      source_url: "https://lo3energy.com"
    }
  ],
  differentiation_opportunities: "SolarGrid can win by building a consumer-first utility app with zero upfront fee (take-rate on transaction spreads) and focusing on suburban community developers who can integrate microgrid setups directly into new real estate builds, bypassing legacy utilities."
};

export const mockAgent5Data: Agent5Output = {
  idea_id: MOCK_PROJECT.idea_id,
  revenue_streams: [
    "Transaction Fee: 3.5% fee on all energy trades facilitated between solar producers and consumers.",
    "Hardware Licensing: SaaS fee for smart-meter telemetry software licensed to real estate developers.",
    "Carbon Credit Brokerage: Aggregating community solar credits and selling to corporate offset buyers (10% brokerage commission)."
  ],
  cost_structure: [
    "Cloud server operations & telemetry data processing.",
    "Regulatory compliance, licensing legal counsel, and lobbying.",
    "Customer acquisition costs (CAC) for community onboarding."
  ],
  value_proposition: "Allows solar owners to monetize surplus energy at rates 20% higher than utility buyback programs, while giving non-solar neighbors access to clean power at 10-15% discounts compared to standard grid retail pricing.",
  customer_segments: [
    "Solar Producers: Green homeowners seeking faster ROI on solar panel installations.",
    "Clean Consumers: Environmentally conscious neighbors without roof space or budget for solar systems.",
    "Green Developers: Real estate builders seeking ESG marketing advantages for new subdivisions."
  ],
  channels: [
    "Partnerships with local solar installers (referral commissions).",
    "Direct-to-consumer digital campaigns in high-adoption neighborhoods.",
    "Real estate builder channels and homeowners associations (HOAs)."
  ]
};

export const mockAgent6Data: Agent6Output = {
  idea_id: MOCK_PROJECT.idea_id,
  slides: [
    {
      title: "SolarGrid",
      content: "Empowering Communities through Peer-to-Peer Clean Energy Sharing\n\nAdith & Team\nLaunchPad AI Accelerator 2026"
    },
    {
      title: "The Problem",
      content: "Centralized power grids are inefficient, prone to blackouts, and fossil-dependent. Homeowners with solar systems are forced to sell excess power back to utility monopolies at unfavorable 'wholesale' rates, while their neighbors pay inflated retail prices for carbon-heavy electricity."
    },
    {
      title: "The Solution",
      content: "A localized, peer-to-peer neighborhood microgrid. SolarGrid allows homes with solar installations to directly supply power to next-door neighbors via smart contract pricing. Clean energy stays local, grid load is balanced, and utility middle-men are bypassed."
    },
    {
      title: "Market Opportunity",
      content: "Total Addressable Market (TAM) is estimated at $14.2 Billion by 2030, growing at 18.4% CAGR. Initial target market focus is CA, TX, and CO, capturing high-solar residential nodes and master-planned green communities."
    },
    {
      title: "Competitive Advantage",
      content: "Unlike enterprise P2P software (Power Ledger) that targets slow-moving utilities, SolarGrid targets consumer HOAs and real estate developers. We integrate at the residential design phase, creating built-in communities with high switching costs."
    },
    {
      title: "Business Model",
      content: "A transactional take-rate model: 3.5% fee on all P2P energy sales. Supported by carbon offset aggregation brokerage (10% commission) and a hardware licensing SaaS model for smart-meter integrations."
    },
    {
      title: "Financial Roadmap",
      content: "• Year 1: 3 neighborhood trials (150 homes), proving platform stability.\n• Year 2: Scale to 50 communities via solar installer partnerships.\n• Year 3: $4.5M ARR with transaction volumes crossing 120 GWh."
    }
  ]
};

export const mockAgent7Data: Agent7Output = {
  idea_id: MOCK_PROJECT.idea_id,
  matched_investors: [
    {
      name: "Clean Energy Ventures",
      focus_area: "Seed-stage investments in decarbonization, clean tech, and smart grid software.",
      reason: "CEV has a portfolio dedicated to decentralized grids and has previously backed community solar projects. Their network of regulatory advisors is ideal for SolarGrid's state-by-state launch."
    },
    {
      name: "Congruent Ventures",
      focus_area: "Early-stage sustainability, energy transitions, and consumer-facing green tech.",
      reason: "Congruent focuses on early-stage solutions targeting energy transitions. Their experience with consumer-facing climate tech will help SolarGrid acquire local participants quickly."
    },
    {
      name: "Obvious Ventures",
      focus_area: "World Positive investing, including sustainable infrastructure and web3 smart grids.",
      reason: "Obvious prioritizes systemic resource efficiency. SolarGrid's local energy optimization aligns directly with their mission to scale clean-tech infrastructure."
    }
  ]
};

export const MOCK_AGENT_DELAY_MS = 2500; // Simulated delay for each agent step in the UI demo
