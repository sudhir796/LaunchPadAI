"use client";

import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { PipelineState } from "../types/agentContracts";

interface PipelineContextProps {
  state: PipelineState;
  submitIdea: (title: string, description: string, market: string) => Promise<void>;
  resetPipeline: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const initialStates: PipelineState["agentStates"] = {
  1: "queued",
  2: "queued",
  3: "queued",
  4: "queued",
  5: "queued",
  6: "queued",
  7: "queued",
};

const defaultState: PipelineState = {
  idea_id: null,
  idea_title: "",
  idea_description: "",
  target_market: "",
  status: "idle",
  currentStage: 0,
  agentStates: initialStates,
  agentOutputs: {
    agent1: null,
    agent2: null,
    agent3: null,
    agent4: null,
    agent5: null,
    agent6: null,
    agent7: null,
  },
};

const AGENT_NAME_TO_STAGE: Record<
  string,
  { stageNum: number; key: keyof PipelineState["agentOutputs"] }
> = {
  idea_validator: { stageNum: 1, key: "agent1" },
  patent_search: { stageNum: 2, key: "agent2" },
  market_research: { stageNum: 3, key: "agent3" },
  competitor_analysis: { stageNum: 4, key: "agent4" },
  business_model: { stageNum: 5, key: "agent5" },
  pitch_deck: { stageNum: 6, key: "agent6" },
  investor_matching: { stageNum: 7, key: "agent7" },
};

const PipelineContext = createContext<PipelineContextProps | undefined>(undefined);

export const PipelineProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<PipelineState>(defaultState);
  const router = useRouter();
  const runRef = useRef<boolean>(false);

  const resetPipeline = () => {
    runRef.current = false;
    setState(defaultState);
  };

  const submitIdea = async (title: string, description: string, market: string) => {
    resetPipeline();
    runRef.current = true;

    // Set initial loading state
    setState({
      idea_id: null,
      idea_title: title,
      idea_description: description,
      target_market: market,
      status: "running",
      currentStage: 1,
      agentStates: {
        1: "running",
        2: "queued",
        3: "queued",
        4: "queued",
        5: "queued",
        6: "queued",
        7: "queued",
      },
      agentOutputs: {
        agent1: null,
        agent2: null,
        agent3: null,
        agent4: null,
        agent5: null,
        agent6: null,
        agent7: null,
      },
    });

    try {
      const response = await fetch(`${API_BASE_URL}/ideas/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title,
          description,
          target_market: market,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const realIdeaId = data.id;

      setState((prev) => ({
        ...prev,
        idea_id: realIdeaId,
      }));

      router.push("/pipeline");
    } catch (error) {
      console.error("[PipelineContext] Error submitting idea:", error);
      setState((prev) => ({
        ...prev,
        status: "failed",
        agentStates: { ...prev.agentStates, 1: "failed" },
      }));
    }
  };

  // Real-time backend progress polling & SSE event streaming
  useEffect(() => {
    if (!runRef.current || !state.idea_id || (state.status !== "running" && state.status !== "idle")) {
      return;
    }

    let isMounted = true;
    const ideaId = state.idea_id;

    const fetchLatestStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/ideas/${ideaId}`);
        if (!response.ok) return;

        const data = await response.json();
        if (!isMounted) return;

        const updatedOutputs = { ...state.agentOutputs };
        const updatedStates = { ...initialStates };

        let highestActiveStage = 1;
        let completedCount = 0;
        let hasError = false;

        if (data.agent_outputs && Array.isArray(data.agent_outputs)) {
          for (const item of data.agent_outputs) {
            const mapping = AGENT_NAME_TO_STAGE[item.agent_name];
            if (!mapping) continue;

            const { stageNum, key } = mapping;

            if (item.status === "done" && item.output_json) {
              updatedStates[stageNum] = "completed";
              updatedOutputs[key] = item.output_json as any;
              completedCount++;
              if (stageNum > highestActiveStage) highestActiveStage = stageNum;
            } else if (item.status === "running") {
              updatedStates[stageNum] = "running";
              if (stageNum > highestActiveStage) highestActiveStage = stageNum;
            } else if (item.status === "error") {
              updatedStates[stageNum] = "failed";
              hasError = true;
            }
          }
        }

        // Set next running stage indicator
        if (!hasError && completedCount < 7) {
          let runningFound = false;
          for (let i = 1; i <= 7; i++) {
            if (updatedStates[i] === "running") {
              runningFound = true;
              break;
            }
          }
          if (!runningFound) {
            for (let i = 1; i <= 7; i++) {
              if (updatedStates[i] === "queued") {
                updatedStates[i] = "running";
                highestActiveStage = i;
                break;
              }
            }
          }
        }

        let pipelineStatus: PipelineState["status"] = "running";
        if (data.status === "done" || completedCount === 7) {
          pipelineStatus = "completed";
          highestActiveStage = 7;
          runRef.current = false;
        } else if (data.status === "error" || hasError) {
          pipelineStatus = "failed";
          runRef.current = false;
        }

        setState((prev) => ({
          ...prev,
          status: pipelineStatus,
          currentStage: highestActiveStage,
          agentStates: updatedStates,
          agentOutputs: updatedOutputs,
        }));
      } catch (err) {
        console.error("[PipelineContext] Error fetching idea status:", err);
      }
    };

    // Initial poll immediately
    fetchLatestStatus();

    // Setup SSE listener for real-time push events from backend
    let eventSource: EventSource | null = null;
    try {
      eventSource = new EventSource(`${API_BASE_URL}/ideas/${ideaId}/stream`);

      eventSource.onmessage = () => {
        if (isMounted) {
          fetchLatestStatus();
        }
      };

      eventSource.onerror = () => {
        if (eventSource) {
          eventSource.close();
        }
      };
    } catch (e) {
      console.warn("[PipelineContext] EventSource not available or failed:", e);
    }

    // Polling fallback interval (every 1.5 seconds)
    const intervalId = setInterval(fetchLatestStatus, 1500);

    return () => {
      isMounted = false;
      if (eventSource) eventSource.close();
      clearInterval(intervalId);
    };
  }, [state.idea_id, state.status]);

  return (
    <PipelineContext.Provider value={{ state, submitIdea, resetPipeline }}>
      {children}
    </PipelineContext.Provider>
  );
};

export const usePipeline = () => {
  const context = useContext(PipelineContext);
  if (!context) {
    throw new Error("usePipeline must be used within a PipelineProvider");
  }
  return context;
};
