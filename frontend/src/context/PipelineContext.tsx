"use client";

import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  PipelineState,
  Agent1Output,
  Agent2Output,
  Agent3Output,
  Agent4Output,
  Agent5Output,
  Agent6Output,
  Agent7Output
} from "../types/agentContracts";
import {
  mockAgent1Data,
  mockAgent2Data,
  mockAgent3Data,
  mockAgent4Data,
  mockAgent5Data,
  mockAgent6Data,
  mockAgent7Data,
  MOCK_AGENT_DELAY_MS
} from "../mocks/mockAgentData";

interface PipelineContextProps {
  state: PipelineState;
  submitIdea: (title: string, description: string, market: string) => void;
  resetPipeline: () => void;
}

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

const PipelineContext = createContext<PipelineContextProps | undefined>(undefined);

export const PipelineProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useState<PipelineState>(defaultState);
  const router = useRouter();
  const runRef = useRef<boolean>(false);

  const resetPipeline = () => {
    runRef.current = false;
    setState(defaultState);
  };

  const submitIdea = (title: string, description: string, market: string) => {
    resetPipeline();
    setState({
      idea_id: "solargrid-001",
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
    runRef.current = true;
    router.push("/pipeline");
  };

  // Run the simulation if status is running
  useEffect(() => {
    if (!runRef.current || state.status !== "running") return;

    const runStage = async (stage: number) => {
      // Simulate API call processing delay
      await new Promise((resolve) => setTimeout(resolve, MOCK_AGENT_DELAY_MS));

      if (!runRef.current) return;

      setState((prev) => {
        const nextStates = { ...prev.agentStates };
        nextStates[stage] = "completed";

        const nextOutputs = { ...prev.agentOutputs };
        let nextStage = stage + 1;
        let nextStatus = prev.status;

        // Populate outputs and set next stage state
        if (stage === 1) nextOutputs.agent1 = mockAgent1Data;
        else if (stage === 2) nextOutputs.agent2 = mockAgent2Data;
        else if (stage === 3) nextOutputs.agent3 = mockAgent3Data;
        else if (stage === 4) nextOutputs.agent4 = mockAgent4Data;
        else if (stage === 5) nextOutputs.agent5 = mockAgent5Data;
        else if (stage === 6) nextOutputs.agent6 = mockAgent6Data;
        else if (stage === 7) {
          nextOutputs.agent7 = mockAgent7Data;
          nextStage = 7;
          nextStatus = "completed";
        }

        if (nextStage <= 7 && nextStatus === "running") {
          nextStates[nextStage] = "running";
        }

        return {
          ...prev,
          status: nextStatus,
          currentStage: nextStage,
          agentStates: nextStates,
          agentOutputs: nextOutputs,
        };
      });
    };

    const current = state.currentStage;
    if (current >= 1 && current <= 7 && state.agentStates[current] === "running") {
      runStage(current);
    }
  }, [state.currentStage, state.status, state.agentStates]);

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
