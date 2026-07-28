"use client";

import React from "react";
import Link from "next/link";
import { usePipeline } from "@/context/PipelineContext";
import { Sparkles, PlusCircle } from "lucide-react";

export const Header: React.FC = () => {
  const { state, resetPipeline } = usePipeline();

  const handleScrollToInvestors = () => {
    const element = document.getElementById("agent7");
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <header
      className="w-full sticky top-0 z-50 flex justify-between items-center px-6 md:px-10 py-4"
      style={{
        background: "rgba(6, 8, 15, 0.88)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(212,168,67,0.18)",
        boxShadow: "0 1px 24px rgba(0,0,0,0.35)",
      }}
    >
      {/* ── Brand ── */}
      <Link href="/" onClick={resetPipeline} className="flex items-center space-x-3 group">
        {/* Diamond logo mark */}
        <div
          className="w-5 h-5 rotate-45 transition-all duration-300 group-hover:scale-110"
          style={{
            background: "linear-gradient(135deg, #d4a843, #f0c060)",
            boxShadow: "0 0 12px rgba(212,168,67,0.5)",
            borderRadius: "3px",
          }}
        />
        <div className="flex flex-col leading-none">
          <span className="font-manrope font-black text-base tracking-tight" style={{ color: "#f0f2f8" }}>
            LAUNCHPAD
            <span className="text-gold-gradient ml-1.5">AI</span>
          </span>
          <span className="hidden md:block font-mono text-[8px] uppercase tracking-[0.2em] mt-0.5" style={{ color: "#8892aa" }}>
            Idea-to-Investor Pipeline
          </span>
        </div>
      </Link>

      {/* ── Right actions ── */}
      <div className="flex items-center space-x-3">

        {/* Running indicator */}
        {state.status === "running" && (
          <div
            className="hidden md:flex items-center space-x-2 px-3 py-1.5 rounded-full text-[10px] font-mono uppercase tracking-wider font-semibold"
            style={{
              background: "rgba(239,35,60,0.12)",
              border: "1px solid rgba(239,35,60,0.3)",
              color: "#ff8596",
            }}
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ background: "#ef233c" }} />
              <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: "#ef233c" }} />
            </span>
            <span>Stage {String(state.currentStage).padStart(2,"0")} / 07 — Processing</span>
          </div>
        )}

        {/* Investor Ready CTA */}
        {state.status === "completed" && (
          <button
            onClick={handleScrollToInvestors}
            className="btn-shimmer flex items-center space-x-2 px-4 py-2 rounded-full text-[10px] font-mono font-bold uppercase tracking-widest transition-all hover:scale-105 active:scale-95"
            style={{
              background: "linear-gradient(135deg, #d4a843 0%, #b8891e 100%)",
              color: "#06080f",
              boxShadow: "0 0 20px rgba(212,168,67,0.4)",
            }}
          >
            <Sparkles className="h-3.5 w-3.5" />
            <span>Investor Ready</span>
          </button>
        )}

        {/* New Submission */}
        <Link
          href="/"
          onClick={resetPipeline}
          className="flex items-center space-x-1.5 px-3 py-2 rounded-lg text-[11px] font-mono font-semibold uppercase tracking-wider transition-all hover:scale-105 active:scale-95"
          style={{
            background: "var(--primary-navy-light)",
            border: "1px solid var(--border-subtle)",
            color: "var(--text-secondary)",
          }}
        >
          <PlusCircle className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">New Submission</span>
        </Link>
      </div>
    </header>
  );
};
