"use client";

import React, { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { usePipeline } from "@/context/PipelineContext";
import { ArrowRight, ShieldAlert, Zap, Search, BarChart3, Users, Brain, FileText } from "lucide-react";

const PIPELINE_STAGES = [
  { n: "01", label: "Idea Validator" },
  { n: "02", label: "Patent & IP Search" },
  { n: "03", label: "Market Research" },
  { n: "04", label: "Competitor Analysis" },
  { n: "05", label: "Business Model" },
  { n: "06", label: "Pitch Deck" },
  { n: "07", label: "Investor Matching" },
];

const FEATURE_CARDS = [
  { icon: Brain,     label: "AI Validation",      desc: "Multi-dimensional feasibility scoring" },
  { icon: Search,    label: "IP Research",         desc: "Automated patent & prior art search" },
  { icon: BarChart3, label: "Market Intelligence", desc: "TAM sizing & demographic analysis" },
  { icon: Users,     label: "Investor Matching",   desc: "Curated VC fit recommendations" },
  { icon: FileText,  label: "Pitch Deck",          desc: "Slide-by-slide deck generation" },
  { icon: Zap,       label: "Full Pipeline",       desc: "End-to-end in ~15 seconds" },
];

export default function Home() {
  const { submitIdea } = usePipeline();
  const [title, setTitle]           = useState("");
  const [description, setDescription] = useState("");
  const [market, setMarket]         = useState("");
  const [error, setError]           = useState("");
  const [isLaunching, setIsLaunching] = useState(false);
  const [launchStep, setLaunchStep]   = useState(0);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !description.trim()) {
      setError("Please fill in the Idea Title and Description to continue.");
      return;
    }
    setError("");
    setIsLaunching(true);
  };

  useEffect(() => {
    if (!isLaunching) return;

    let step = 0;
    const interval = setInterval(() => {
      step += 1;
      if (step > 3) {
        clearInterval(interval);
        submitIdea(title, description, market);
      } else {
        setLaunchStep(step);
      }
    }, 850);

    return () => clearInterval(interval);
  }, [isLaunching, title, description, market, submitIdea]);

  if (isLaunching) {
    return (
      <div className="fixed inset-0 z-[10000] flex flex-col items-center justify-center p-6 text-center animate-fade-in" style={{ background: "#06080f" }}>
        {/* Subtle grid pattern background */}
        <div className="absolute inset-0 pointer-events-none opacity-5"
          style={{ backgroundImage: "radial-gradient(rgba(212,168,67,0.25) 1px, transparent 1px)", backgroundSize: "20px 20px" }} />

        {/* Central glowing launch icon */}
        <div className="relative mb-8">
          <div className="w-16 h-16 rounded-full border-2 border-[var(--accent-gold)] flex items-center justify-center animate-spin"
            style={{ animationDuration: "3s", borderStyle: "dashed" }} />
          <div className="absolute inset-0 w-16 h-16 flex items-center justify-center">
            <div className="w-8 h-8 rotate-45"
              style={{
                background: "linear-gradient(135deg, var(--accent-gold), var(--accent-gold-bright))",
                boxShadow: "0 0 20px rgba(184, 137, 30, 0.4)",
                borderRadius: "3px",
              }}
            />
          </div>
        </div>

        {/* Booting text */}
        <h3 className="font-serif text-2xl font-bold tracking-tight mb-2" style={{ color: "#f0f2f8" }}>
          Launching Acceleration Pipeline
        </h3>
        <p className="font-mono text-[10px] uppercase tracking-[0.2em] mb-8" style={{ color: "var(--accent-gold)" }}>
          Multi-Agent System Boot Sequence
        </p>

        {/* Steps display */}
        <div className="w-full max-w-sm space-y-3 mb-8 text-left border border-white/10 p-5 rounded-xl" style={{ background: "rgba(255,255,255,0.05)" }}>
          <div className="flex items-center space-x-3 text-xs font-mono transition-opacity duration-300"
            style={{ opacity: launchStep >= 0 ? 1 : 0.3 }}>
            <span className={launchStep > 0 ? "text-emerald-500" : "animate-pulse text-[var(--accent-gold)]"}>
              {launchStep > 0 ? "✓" : "●"}
            </span>
            <span style={{ color: launchStep === 0 ? "#f0f2f8" : "#8892aa" }}>
              Assembling 7-Agent Core Orch...
            </span>
          </div>

          <div className="flex items-center space-x-3 text-xs font-mono transition-opacity duration-300"
            style={{ opacity: launchStep >= 1 ? 1 : 0.3 }}>
            <span className={launchStep > 1 ? "text-emerald-500" : launchStep === 1 ? "animate-pulse text-[var(--accent-gold)]" : "●"}>
              {launchStep > 1 ? "✓" : "●"}
            </span>
            <span style={{ color: launchStep === 1 ? "#f0f2f8" : "#8892aa" }}>
              Establishing Patent & Prior-Art Link...
            </span>
          </div>

          <div className="flex items-center space-x-3 text-xs font-mono transition-opacity duration-300"
            style={{ opacity: launchStep >= 2 ? 1 : 0.3 }}>
            <span className={launchStep > 2 ? "text-emerald-500" : launchStep === 2 ? "animate-pulse text-[var(--accent-gold)]" : "●"}>
              {launchStep > 2 ? "✓" : "●"}
            </span>
            <span style={{ color: launchStep === 2 ? "#f0f2f8" : "#8892aa" }}>
              Connecting Pitch Deck Engine...
            </span>
          </div>

          <div className="flex items-center space-x-3 text-xs font-mono transition-opacity duration-300"
            style={{ opacity: launchStep >= 3 ? 1 : 0.3 }}>
            <span className={launchStep > 3 ? "text-emerald-500" : launchStep === 3 ? "animate-pulse text-[var(--accent-gold)]" : "●"}>
              {launchStep > 3 ? "✓" : "●"}
            </span>
            <span style={{ color: launchStep === 3 ? "var(--text-primary)" : "var(--text-secondary)" }}>
              Redirecting to Deal Dashboard...
            </span>
          </div>
        </div>

        {/* Global progress indicator */}
        <div className="w-full max-w-sm rounded-full h-1.5 overflow-hidden bg-slate-100">
          <div className="h-full bg-gradient-to-r from-[var(--accent-gold-bright)] to-[var(--accent-gold)] transition-all duration-700"
            style={{ width: `${((launchStep + 1) / 4) * 100}%` }} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen" style={{ background: "var(--background)" }}>
      <Header />

      {/* ── Ambient background glows ── */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 0 }}>
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full opacity-20"
          style={{ background: "radial-gradient(circle, rgba(212,168,67,0.3) 0%, transparent 70%)" }} />
        <div className="absolute bottom-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full opacity-15"
          style={{ background: "radial-gradient(circle, rgba(239,35,60,0.25) 0%, transparent 70%)" }} />
        <div className="absolute top-[40%] left-[50%] w-[400px] h-[400px] rounded-full opacity-10"
          style={{ background: "radial-gradient(circle, rgba(212,168,67,0.2) 0%, transparent 70%)", transform: "translate(-50%,-50%)" }} />
      </div>

      <main className="relative flex-grow flex flex-col items-center justify-center px-4 py-12 md:py-16" style={{ zIndex: 1 }}>

        {/* ── Hero headline ── */}
        <div className="text-center mb-12 opacity-0 animate-fade-up" style={{ animationDelay: "0.05s", animationFillMode: "forwards" }}>
          <span className="inline-flex items-center space-x-2 text-[10px] font-mono uppercase tracking-widest mb-5 px-3 py-1.5 border rounded-full"
            style={{ color: "var(--accent-gold)", borderColor: "var(--border-gold)", background: "var(--accent-gold-dim)" }}>
            <span className="h-1.5 w-1.5 rounded-full animate-pulse" style={{ background: "var(--accent-gold)" }} />
            <span>Institutional Pitch Preparation Platform</span>
          </span>

          <h1 className="font-serif text-5xl md:text-7xl font-bold leading-none tracking-tight mb-4">
            <span style={{ color: "var(--text-primary)" }}>Launch</span>
            <span className="text-gold-gradient">Pad</span>
            <span className="italic font-light ml-3" style={{ color: "var(--text-secondary)" }}>AI</span>
          </h1>
        </div>

        {/* ── Feature grid ── */}
        <div className="w-full max-w-3xl grid grid-cols-2 md:grid-cols-3 gap-3 mb-10 opacity-0 animate-fade-up" style={{ animationDelay: "0.2s", animationFillMode: "forwards" }}>
          {FEATURE_CARDS.map(({ icon: Icon, label, desc }) => (
            <div key={label} className="glass p-4 rounded-lg hover:border-[var(--border-gold)] transition-all duration-200 group cursor-default">
              <div className="flex items-center space-x-2.5 mb-2">
                <div className="p-1.5 rounded-md" style={{ background: "var(--accent-gold-dim)" }}>
                  <Icon className="h-3.5 w-3.5" style={{ color: "var(--accent-gold)" }} />
                </div>
                <span className="font-semibold text-xs" style={{ color: "var(--text-primary)" }}>{label}</span>
              </div>
              <p className="text-[10px] leading-relaxed font-mono" style={{ color: "var(--text-muted)" }}>{desc}</p>
            </div>
          ))}
        </div>

        {/* ── Submission form card ── */}
        <div className="w-full max-w-2xl opacity-0 animate-fade-up" style={{ animationDelay: "0.35s", animationFillMode: "forwards" }}>
          <div className="glass-bright rounded-2xl p-8 md:p-10 glow-border relative overflow-hidden">
            {/* Subtle top glow line */}
            <div className="absolute top-0 left-[20%] right-[20%] h-px" style={{ background: "linear-gradient(90deg, transparent, var(--accent-gold), transparent)" }} />

            <div className="mb-7">
              <h2 className="font-serif text-2xl font-bold mb-1.5" style={{ color: "var(--text-primary)" }}>
                Submit Your Idea
              </h2>
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                The full 7-agent pipeline will kick off immediately after submission.
              </p>
            </div>

            {error && (
              <div className="mb-5 px-4 py-3 rounded-lg flex items-center space-x-2.5 text-xs font-mono"
                style={{ background: "rgba(239,35,60,0.1)", border: "1px solid rgba(239,35,60,0.3)", color: "#ff6b7a" }}>
                <ShieldAlert className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Title */}
              <div>
                <label htmlFor="title" className="block text-[11px] font-mono font-semibold uppercase tracking-widest mb-2"
                  style={{ color: "var(--accent-gold)" }}>
                  Startup Idea Title <span style={{ color: "#ef233c" }}>*</span>
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., SolarGrid — P2P Solar Energy Sharing"
                  className="input-dark w-full px-4 py-3 rounded-lg text-sm font-sans"
                />
              </div>

              {/* Description */}
              <div>
                <label htmlFor="description" className="block text-[11px] font-mono font-semibold uppercase tracking-widest mb-2"
                  style={{ color: "var(--accent-gold)" }}>
                  Concept Description <span style={{ color: "#ef233c" }}>*</span>
                </label>
                <textarea
                  id="description"
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Describe the core technology, the problem it solves, and the key benefits for your target customers..."
                  className="input-dark w-full px-4 py-3 rounded-lg text-sm font-sans resize-none"
                />
              </div>

              {/* Target Market */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label htmlFor="market" className="block text-[11px] font-mono font-semibold uppercase tracking-widest"
                    style={{ color: "var(--accent-gold)" }}>
                    Target Market
                  </label>
                  <span className="text-[9px] font-mono uppercase tracking-wider px-2 py-0.5 rounded"
                    style={{ color: "var(--text-muted)", background: "var(--primary-navy-light)", border: "1px solid var(--border-subtle)" }}>
                    Optional
                  </span>
                </div>
                <input
                  type="text"
                  id="market"
                  value={market}
                  onChange={(e) => setMarket(e.target.value)}
                  placeholder="e.g., Suburban residential neighbourhoods with solar adoption"
                  className="input-dark w-full px-4 py-3 rounded-lg text-sm font-sans"
                />
              </div>

              {/* Submit */}
              <div className="pt-2">
                <button
                  type="submit"
                  className="btn-shimmer w-full flex items-center justify-center space-x-3 px-6 py-4 rounded-xl font-mono text-xs font-bold tracking-widest uppercase transition-all duration-200 hover:scale-[1.01] active:scale-[0.99]"
                  style={{
                    background: "linear-gradient(135deg, #d4a843 0%, #b8891e 100%)",
                    color: "#06080f",
                    boxShadow: "0 4px 24px rgba(212,168,67,0.35), 0 1px 0 rgba(255,255,255,0.1) inset",
                  }}
                >
                  <span>Initiate Validation Pipeline</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </form>

            {/* Pipeline steps row */}
            <div className="mt-8 pt-6" style={{ borderTop: "1px solid var(--border-subtle)" }}>
              <p className="text-[9px] font-mono uppercase tracking-widest mb-3 text-center" style={{ color: "var(--text-muted)" }}>
                7-Stage Autonomous Pipeline
              </p>
              <div className="flex flex-wrap justify-center gap-x-4 gap-y-1.5">
                {PIPELINE_STAGES.map(({ n, label }) => (
                  <div key={n} className="flex items-center space-x-1.5 text-[9px] font-mono" style={{ color: "var(--text-muted)" }}>
                    <span style={{ color: "var(--accent-gold)" }}>{n}</span>
                    <span>{label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
