"use client";

import React, { useState, useEffect, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { usePipeline } from "@/context/PipelineContext";
import { Header } from "@/components/Header";
import { PipelineRail } from "@/components/PipelineRail";

import { Agent1Validator }    from "@/components/agents/Agent1Validator";
import { Agent2Patent }       from "@/components/agents/Agent2Patent";
import { Agent3Market }       from "@/components/agents/Agent3Market";
import { Agent4Competitors }  from "@/components/agents/Agent4Competitors";
import { Agent5BusinessModel }from "@/components/agents/Agent5BusinessModel";
import { Agent6PitchDeck }    from "@/components/agents/Agent6PitchDeck";
import { Agent7Investors }    from "@/components/agents/Agent7Investors";

import { Loader2, HelpCircle, ArrowLeft, Clock, CheckCircle2, Download, ChevronLeft, ChevronRight } from "lucide-react";
import Link from "next/link";

const STAGE_META: Record<number, { name: string; domain: string }> = {
  1: { name: "Idea Validator",      domain: "Reasoning & Evaluation" },
  2: { name: "Patent & Prior Art",  domain: "IP Research" },
  3: { name: "Market Research",     domain: "Information Retrieval" },
  4: { name: "Competitor Analysis", domain: "Comparative NLP" },
  5: { name: "Business Model",      domain: "Strategic Reasoning" },
  6: { name: "Pitch Deck",          domain: "Generative Content" },
  7: { name: "Investor Matching",   domain: "Recommendation" },
};

function PipelinePageContent() {
  const searchParams = useSearchParams();
  const queryIdeaId = searchParams.get("idea_id");

  const { state, loadIdea, resetPipeline } = usePipeline();
  const router = useRouter();

  const [activeStage, setActiveStage] = useState<number>(1);
  const userOverrodeStage = useRef<boolean>(false);
  const prevHighestStage = useRef<number>(1);

  useEffect(() => {
    if (queryIdeaId && state.idea_id !== queryIdeaId) {
      loadIdea(queryIdeaId);
    } else if (!queryIdeaId && !state.idea_title && state.status === "idle") {
      router.push("/");
    }
  }, [queryIdeaId, state.idea_id, state.idea_title, state.status, loadIdea, router]);

  useEffect(() => {
    const currentRunningOrLatest = state.currentStage || 1;

    if (!userOverrodeStage.current) {
      setActiveStage(currentRunningOrLatest);
    } else if (activeStage === prevHighestStage.current && currentRunningOrLatest > prevHighestStage.current) {
      setActiveStage(currentRunningOrLatest);
    }

    prevHighestStage.current = currentRunningOrLatest;
  }, [state.currentStage, activeStage]);

  const handleSelectStage = (stageNum: number) => {
    userOverrodeStage.current = true;
    setActiveStage(stageNum);
  };

  if (!state.idea_title) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--background)" }}>
        <div className="flex flex-col items-center space-y-4 text-center">
          <Loader2 className="h-7 w-7 animate-spin" style={{ color: "var(--accent-gold)" }} />
          <span className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--text-muted)" }}>
            Redirecting to submission panel...
          </span>
        </div>
      </div>
    );
  }

  const completedCount = Object.values(state.agentStates).filter(s => s === "completed").length;
  const progress = Math.round((completedCount / 7) * 100);

  const readinessScore = state.agentOutputs.agent7?.investor_readiness_score;
  const starRating = state.agentOutputs.agent7?.star_rating ?? (typeof readinessScore === "number" ? (readinessScore >= 80 ? 5 : readinessScore >= 65 ? 4 : readinessScore >= 50 ? 3 : 2) : undefined);

  const renderAgentCard = (stageNum: number) => {
    const status = state.agentStates[stageNum];
    const meta   = STAGE_META[stageNum];

    if (status === "queued") {
      return (
        <div
          className="bg-white border border-[#E2E8F0] p-8 md:p-12 text-center rounded-xl animate-fade-in shadow-sm"
        >
          <div className="font-mono text-[10px] text-[#C9A227] uppercase tracking-widest mb-2 font-bold">
            Stage 0{stageNum} — Queued
          </div>
          <h3 className="font-serif text-2xl font-bold text-[#0B1220] mb-2">
            {meta.name}
          </h3>
          <p className="text-xs text-slate-500 font-sans max-w-md mx-auto mb-6">
            This analysis stage is queued and waiting for prior agent outputs to finish processing...
          </p>
          <div className="inline-flex items-center space-x-2 font-mono text-xs text-slate-500 bg-[#F7F8FA] border border-[#E2E8F0] px-4 py-2 rounded-full">
            <Clock className="h-4 w-4 text-slate-400" />
            <span>Awaiting Stage 0{stageNum} Execution</span>
          </div>
        </div>
      );
    }

    if (status === "running") {
      return (
        <div
          id={`agent${stageNum}`}
          className="rounded-xl p-8 relative overflow-hidden bg-white border border-[#E2E8F0] shadow-sm animate-fade-in"
        >
          {/* Animated top bar */}
          <div className="absolute top-0 left-0 h-1 w-full">
            <div className="h-full animate-pulse" style={{ background: "linear-gradient(90deg, transparent, var(--accent-gold), transparent)" }} />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <span className="h-2 w-2 rounded-full animate-ping" style={{ background: "var(--accent-gold)" }} />
                <span className="stage-badge font-bold">Stage 0{stageNum} — Processing</span>
              </div>
              <h4 className="font-serif text-2xl font-bold text-[#0B1220]">
                {meta.name}
              </h4>
              <p className="text-xs mt-1.5 font-mono text-slate-500">
                {meta.domain} — compiling intelligence...
              </p>
            </div>
            <div className="flex flex-col items-center space-y-1">
              <Loader2 className="h-6 w-6 animate-spin" style={{ color: "var(--accent-gold)" }} />
            </div>
          </div>
        </div>
      );
    }

    if (status === "completed") {
      const COMPONENTS: Record<number, React.ReactNode> = {
        1: state.agentOutputs.agent1 ? <Agent1Validator data={state.agentOutputs.agent1} /> : null,
        2: state.agentOutputs.agent2 ? <Agent2Patent    data={state.agentOutputs.agent2} /> : null,
        3: state.agentOutputs.agent3 ? <Agent3Market    data={state.agentOutputs.agent3} /> : null,
        4: state.agentOutputs.agent4 ? <Agent4Competitors data={state.agentOutputs.agent4} /> : null,
        5: state.agentOutputs.agent5 ? <Agent5BusinessModel data={state.agentOutputs.agent5} /> : null,
        6: state.agentOutputs.agent6 ? <Agent6PitchDeck data={state.agentOutputs.agent6} /> : null,
        7: state.agentOutputs.agent7 ? <Agent7Investors data={state.agentOutputs.agent7} /> : null,
      };
      return <div id={`agent${stageNum}`} className="animate-fade-in">{COMPONENTS[stageNum]}</div>;
    }

    return null;
  };

  return (
    <div className="flex flex-col min-h-screen" style={{ background: "var(--background)" }}>
      {/* Ambient glow */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 0 }}>
        <div className="absolute top-[10%] left-[-5%] w-[400px] h-[400px] rounded-full opacity-10"
          style={{ background: "radial-gradient(circle, rgba(212,168,67,0.4) 0%, transparent 70%)" }} />
        <div className="absolute bottom-[5%] right-[-5%] w-[300px] h-[300px] rounded-full opacity-8"
          style={{ background: "radial-gradient(circle, rgba(239,35,60,0.3) 0%, transparent 70%)" }} />
      </div>

      <Header />

      <div className="relative flex-grow flex max-w-screen-xl w-full mx-auto" style={{ zIndex: 1 }}>
        {/* Sidebar rail */}
        <PipelineRail activeStage={activeStage} onSelectStage={handleSelectStage} />

        {/* Main panel */}
        <main className="flex-grow p-5 md:p-8 space-y-5 overflow-y-auto">

          {/* Project header card */}
          <div
            className="rounded-2xl p-6 md:p-8 animate-fade-up"
            style={{
              background: "var(--surface-elevated)",
              border: "1px solid var(--border-subtle)",
              boxShadow: "0 4px 20px rgba(0,0,0,0.05)",
            }}
          >
            {/* Breadcrumb */}
            <div className="flex items-center space-x-2 mb-5 text-[10px] font-mono uppercase tracking-widest">
              <Link href="/" onClick={resetPipeline}
                className="flex items-center space-x-1.5 transition-colors hover:opacity-80"
                style={{ color: "var(--text-muted)" }}>
                <ArrowLeft className="h-3 w-3" />
                <span>New Submission</span>
              </Link>
              <span style={{ color: "var(--border-medium)" }}>/</span>
              <span style={{ color: "var(--text-muted)" }}>Project: {state.idea_id}</span>
            </div>

            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
              <div className="flex-grow min-w-0">
                <h2 className="font-serif text-2xl md:text-3xl font-bold leading-tight mb-2" style={{ color: "var(--text-primary)" }}>
                  {state.idea_title}
                </h2>
                {state.target_market && (
                  <span
                    className="inline-flex items-center text-[9px] font-mono uppercase tracking-widest px-3 py-1 rounded-full mb-3"
                    style={{ background: "var(--accent-gold-dim)", color: "var(--accent-gold)", border: "1px solid var(--border-gold)" }}
                  >
                    Market: {state.target_market}
                  </span>
                )}
                <p className="text-sm leading-relaxed mt-2" style={{ color: "var(--text-secondary)" }}>
                  {state.idea_description}
                </p>
              </div>

              {/* Progress widget */}
              <div
                className="shrink-0 w-full md:w-44 rounded-xl p-5 text-center"
                style={{ background: "var(--surface)", border: "1px solid var(--border-subtle)" }}
              >
                <div className="font-mono text-[9px] uppercase tracking-widest mb-3" style={{ color: "var(--text-muted)" }}>
                  Pipeline Progress
                </div>
                <div className="font-serif text-4xl font-black mb-1" style={{ color: "var(--text-primary)" }}>
                  {completedCount}
                  <span className="text-xl font-normal" style={{ color: "var(--text-muted)" }}>/7</span>
                </div>
                {/* Progress bar */}
                <div className="w-full rounded-full h-1.5 mb-2" style={{ background: "var(--primary-navy-light)" }}>
                  <div
                    className="h-1.5 rounded-full transition-all duration-700"
                    style={{
                      width: `${progress}%`,
                      background: "linear-gradient(90deg, #b8891e, #d4a843, #f0c060)",
                      boxShadow: progress > 0 ? "0 0 8px rgba(212,168,67,0.5)" : "none",
                    }}
                  />
                </div>
                {state.status === "running" && (
                  <div className="flex items-center justify-center space-x-1.5 text-[9px] font-mono" style={{ color: "var(--accent-gold)" }}>
                    <Clock className="h-3 w-3" />
                    <span>Processing...</span>
                  </div>
                )}
                {state.status === "completed" && (
                  <div className="flex flex-col items-center space-y-2 mt-2">
                    <div className="flex items-center justify-center space-x-1.5 text-[9px] font-mono font-bold" style={{ color: "#4ade80" }}>
                      <CheckCircle2 className="h-3 w-3" />
                      <span>Complete</span>
                    </div>
                    <a
                      href={`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/ideas/${state.idea_id}/report`}
                      download
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center justify-center space-x-1.5 w-full bg-[#C9A227] hover:bg-[#b8921f] text-[#0B1220] font-mono text-[9px] font-bold uppercase py-1.5 px-2 rounded transition-all mt-1"
                    >
                      <Download className="h-3 w-3" />
                      <span>Download PDF</span>
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Prominent Investor Readiness Score Card */}
          {typeof readinessScore === "number" && (
            <div
              className="rounded-2xl p-6 md:p-8 animate-fade-up flex flex-col md:flex-row items-center justify-between gap-6"
              style={{
                background: "linear-gradient(135deg, #0B1220 0%, #1A2333 100%)",
                border: "1px solid rgba(201, 162, 39, 0.4)",
                boxShadow: "0 8px 32px rgba(201, 162, 39, 0.12)",
              }}
            >
              <div className="flex items-center space-x-5">
                <div
                  className="h-16 w-16 rounded-xl flex items-center justify-center font-mono text-2xl font-black shrink-0"
                  style={{
                    background: "linear-gradient(135deg, #C9A227 0%, #E5C158 100%)",
                    color: "#0B1220",
                    boxShadow: "0 4px 14px rgba(201, 162, 39, 0.3)",
                  }}
                >
                  {readinessScore}
                </div>
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="font-mono text-[10px] uppercase tracking-widest text-[#C9A227] font-bold">
                      Venture Assessment Summary
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="font-mono text-[10px] uppercase tracking-widest text-slate-400">
                      Final Report
                    </span>
                  </div>
                  <h3 className="font-serif text-2xl font-bold text-white flex flex-wrap items-center gap-3">
                    <span>Investor Readiness: {readinessScore}/100</span>
                    {typeof starRating === "number" && (
                      <span className="text-xl text-[#C9A227] tracking-widest">
                        {"★".repeat(starRating) + "☆".repeat(5 - starRating)}
                      </span>
                    )}
                  </h3>
                  <p className="text-xs text-slate-300 font-sans mt-1">
                    Synthesized score calculated across validation, IP conflict risk, market opportunity, and VC thesis matching.
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-3 shrink-0">
                <div className="text-right">
                  <span className="font-mono text-[10px] uppercase tracking-widest text-slate-400 block">
                    Star Rating
                  </span>
                  <span className="font-mono text-lg font-bold text-[#C9A227]">
                    {starRating ?? 5}/5 Stars
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Mobile stage selector bar */}
          <div className="flex md:hidden items-center overflow-x-auto space-x-2 pb-2 no-scrollbar border-b border-[var(--border-subtle)]">
            {[1, 2, 3, 4, 5, 6, 7].map((num) => {
              const status = state.agentStates[num];
              const isSel = activeStage === num;
              return (
                <button
                  key={num}
                  onClick={() => handleSelectStage(num)}
                  className={`px-3 py-1.5 rounded-full font-mono text-[10px] uppercase tracking-wider shrink-0 transition-all cursor-pointer ${
                    isSel
                      ? "bg-[var(--accent-gold)] text-[#0B1220] font-bold"
                      : status === "completed"
                      ? "bg-[#111c35] text-[var(--text-primary)] border border-emerald-500/40"
                      : status === "running"
                      ? "bg-[var(--accent-gold-dim)] text-[var(--accent-gold)] border border-[var(--accent-gold)]"
                      : "bg-[#0d1526] text-[var(--text-muted)] border border-[var(--border-subtle)]"
                  }`}
                >
                  0{num}. {STAGE_META[num].name}
                </button>
              );
            })}
          </div>

          {/* Section header */}
          <div className="flex items-center space-x-3 px-1">
            <span className="font-mono text-[9px] uppercase tracking-widest" style={{ color: "var(--text-muted)" }}>
              Active Stage Analysis — 0{activeStage} of 07
            </span>
            <div className="flex-grow h-px" style={{ background: "var(--border-subtle)" }} />
          </div>

          {/* Single active Agent Card View with fade transition */}
          <div key={activeStage} className="animate-fade-in transition-all duration-300">
            {renderAgentCard(activeStage)}
          </div>

          {/* PREV / NEXT Stage Navigation Controls */}
          <div className="flex justify-between items-center w-full bg-white border border-[#E2E8F0] p-4 font-mono text-xs rounded-xl shadow-sm mt-4">
            <button
              onClick={() => handleSelectStage(Math.max(1, activeStage - 1))}
              disabled={activeStage === 1}
              className={`flex items-center space-x-2 px-4 py-2 border transition-all font-semibold rounded ${
                activeStage === 1
                  ? "text-slate-300 border-[#E2E8F0] cursor-not-allowed bg-[#F7F8FA]"
                  : "text-[#0B1220] border-[#E2E8F0] hover:border-[#C9A227] hover:text-[#C9A227] bg-white cursor-pointer"
              }`}
            >
              <ChevronLeft className="h-4 w-4" />
              <span>PREV STAGE</span>
            </button>

            <div className="text-[#0B1220] font-semibold tracking-widest text-xs flex items-center space-x-2">
              <span className="text-[#C9A227]">STAGE 0{activeStage} OF 07</span>
              <span className="hidden sm:inline text-slate-400 font-sans text-xs">• {STAGE_META[activeStage]?.name}</span>
            </div>

            <button
              onClick={() => handleSelectStage(Math.min(7, activeStage + 1))}
              disabled={activeStage === 7}
              className={`flex items-center space-x-2 px-4 py-2 border transition-all font-semibold rounded ${
                activeStage === 7
                  ? "text-slate-300 border-[#E2E8F0] cursor-not-allowed bg-[#F7F8FA]"
                  : "text-[#0B1220] border-[#E2E8F0] hover:border-[#C9A227] hover:text-[#C9A227] bg-white cursor-pointer"
              }`}
            >
              <span>NEXT STAGE</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>

        </main>
      </div>
    </div>
  );
}

export default function PipelinePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--background)" }}>
          <Loader2 className="h-7 w-7 animate-spin" style={{ color: "var(--accent-gold)" }} />
        </div>
      }
    >
      <PipelinePageContent />
    </Suspense>
  );
}
