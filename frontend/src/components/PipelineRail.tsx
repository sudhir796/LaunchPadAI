"use client";

import React from "react";
import { usePipeline } from "@/context/PipelineContext";
import { Check, Loader2 } from "lucide-react";

interface Stage {
  number: number;
  id: string;
  name: string;
  domain: string;
}

const STAGES: Stage[] = [
  { number: 1, id: "agent1", name: "Idea Validator",      domain: "Reasoning & Evaluation" },
  { number: 2, id: "agent2", name: "Patent & Prior Art",  domain: "IP Research" },
  { number: 3, id: "agent3", name: "Market Research",     domain: "Information Retrieval" },
  { number: 4, id: "agent4", name: "Competitor Analysis", domain: "Comparative NLP" },
  { number: 5, id: "agent5", name: "Business Model",      domain: "Strategic Reasoning" },
  { number: 6, id: "agent6", name: "Pitch Deck",          domain: "Generative Content" },
  { number: 7, id: "agent7", name: "Investor Matching",   domain: "Recommendation" },
];

export const PipelineRail: React.FC = () => {
  const { state } = usePipeline();

  const completedCount = Object.values(state.agentStates).filter(s => s === "completed").length;

  const handleClick = (id: string, isCompleted: boolean) => {
    if (!isCompleted) return;
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <aside
      className="hidden md:flex w-72 shrink-0 flex-col sticky top-[69px] h-[calc(100vh-69px)] overflow-y-auto no-scrollbar"
      style={{
        background: "var(--surface)",
        borderRight: "1px solid var(--border-subtle)",
      }}
    >
      <div className="p-6 flex flex-col h-full">
        {/* Header */}
        <div className="mb-5">
          <p className="font-mono text-[9px] uppercase tracking-[0.2em] mb-1" style={{ color: "var(--text-muted)" }}>
            Deal Pipeline
          </p>
          <h3 className="font-serif text-base font-bold" style={{ color: "var(--text-primary)" }}>
            Analysis Checklist
          </h3>
        </div>

        {/* Stage list */}
        <div className="relative flex flex-col space-y-1 flex-grow">
          {/* Vertical timeline line */}
          <div
            className="absolute left-3.5 top-0 bottom-0 w-px"
            style={{ background: "var(--border-subtle)" }}
          />
          {/* Gold progress fill */}
          <div
            className="absolute left-3.5 top-0 w-px transition-all duration-700"
            style={{
              background: "linear-gradient(180deg, var(--accent-gold), rgba(212,168,67,0.3))",
              height: `${(completedCount / 7) * 100}%`,
              boxShadow: completedCount > 0 ? "0 0 6px rgba(212,168,67,0.5)" : "none",
            }}
          />

          {STAGES.map((stage) => {
            const status      = state.agentStates[stage.number];
            const isQueued    = status === "queued";
            const isRunning   = status === "running";
            const isCompleted = status === "completed";

            return (
              <button
                key={stage.number}
                onClick={() => handleClick(stage.id, isCompleted)}
                disabled={!isCompleted}
                className="relative flex items-start space-x-3.5 w-full text-left py-2.5 px-2 rounded-lg transition-all duration-300 group hover:translate-x-1 disabled:hover:translate-x-0"
                style={{
                  cursor: isCompleted ? "pointer" : "default",
                  background: isRunning ? "var(--accent-gold-dim)" : "transparent",
                }}
              >
                {/* Dot */}
                <div
                  className="relative z-10 flex items-center justify-center w-7 h-7 shrink-0 rounded-full text-[10px] font-mono font-bold transition-all duration-300"
                  style={
                    isCompleted ? {
                      background: "var(--accent-gold)",
                      color: "#06080f",
                      boxShadow: "0 0 0 3px rgba(212,168,67,0.2), 0 0 10px rgba(212,168,67,0.3)",
                    } : isRunning ? {
                      background: "var(--surface-elevated)",
                      border: "2px solid var(--accent-gold)",
                      color: "var(--accent-gold)",
                      boxShadow: "0 0 0 3px rgba(212,168,67,0.15)",
                    } : {
                      background: "var(--surface)",
                      border: "2px solid var(--border-medium)",
                      color: "var(--text-muted)",
                    }
                  }
                >
                  {isCompleted ? (
                    <Check className="w-3.5 h-3.5 stroke-[3px]" />
                  ) : isRunning ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    `0${stage.number}`
                  )}
                </div>

                {/* Text */}
                <div className="flex flex-col pt-0.5">
                  <span
                    className="font-semibold text-sm leading-tight transition-colors"
                    style={{
                      color: isCompleted
                        ? "var(--text-primary)"
                        : isRunning
                        ? "var(--accent-gold)"
                        : "var(--text-muted)",
                    }}
                  >
                    {stage.name}
                  </span>
                  <span className="font-mono text-[9px] uppercase tracking-widest mt-0.5" style={{ color: "var(--text-muted)" }}>
                    {stage.domain}
                  </span>
                  {isCompleted && (
                    <span
                      className="font-mono text-[9px] mt-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      style={{ color: "var(--accent-gold)" }}
                    >
                      ↑ Jump to section
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer stats */}
        <div className="mt-6 pt-5" style={{ borderTop: "1px solid var(--border-subtle)" }}>
          <div className="space-y-2.5">
            <div className="flex justify-between items-center">
              <span className="font-mono text-[9px] uppercase tracking-widest" style={{ color: "var(--text-muted)" }}>
                Status
              </span>
              <span
                className="font-mono text-[9px] uppercase tracking-widest font-bold"
                style={{
                  color: state.status === "completed"
                    ? "#4ade80"
                    : state.status === "running"
                    ? "var(--accent-gold)"
                    : "var(--text-muted)",
                }}
              >
                {state.status}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-mono text-[9px] uppercase tracking-widest" style={{ color: "var(--text-muted)" }}>
                Completed
              </span>
              <span className="font-mono text-[9px] font-bold" style={{ color: "var(--text-primary)" }}>
                {completedCount} / 7
              </span>
            </div>
            {/* Mini progress bar */}
            <div className="w-full rounded-full h-1 mt-1" style={{ background: "var(--border-subtle)" }}>
              <div
                className="h-1 rounded-full transition-all duration-700"
                style={{
                  width: `${(completedCount / 7) * 100}%`,
                  background: "linear-gradient(90deg, #b8891e, #f0c060)",
                  boxShadow: completedCount > 0 ? "0 0 6px rgba(212,168,67,0.5)" : "none",
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
