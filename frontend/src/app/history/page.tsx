"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { usePipeline } from "@/context/PipelineContext";
import {
  FileClock,
  Search,
  CheckCircle2,
  Clock,
  AlertCircle,
  ArrowRight,
  RefreshCw,
  PlusCircle,
  ArrowLeft,
  WifiOff
} from "lucide-react";

interface IdeaRecord {
  id: string;
  title: string;
  description: string;
  target_market?: string;
  region?: string;
  sector?: string;
  status: string;
  created_at: string;
  investor_readiness_score?: number;
  star_rating?: number;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

function formatRelativeTime(dateString: string): string {
  if (!dateString) return "Recently";
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (isNaN(diffInSeconds) || diffInSeconds < 0) return "Just now";
  if (diffInSeconds < 60) return "Just now";
  if (diffInSeconds < 3600) {
    const mins = Math.floor(diffInSeconds / 60);
    return `${mins} ${mins === 1 ? "min" : "mins"} ago`;
  }
  if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} ${hours === 1 ? "hour" : "hours"} ago`;
  }
  const days = Math.floor(diffInSeconds / 86400);
  return `${days} ${days === 1 ? "day" : "days"} ago`;
}

export default function HistoryPage() {
  const { loadIdea, resetPipeline } = usePipeline();
  const router = useRouter();

  const [ideas, setIdeas] = useState<IdeaRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const fetchHistory = async () => {
    setIsRefreshing(true);
    setErrorMessage(null);

    const baseUrl = API_BASE_URL.replace(/\/$/, "");
    const altBaseUrl = baseUrl.includes("127.0.0.1")
      ? baseUrl.replace("127.0.0.1", "localhost")
      : baseUrl.replace("localhost", "127.0.0.1");

    try {
      let response: Response | null = null;

      try {
        response = await fetch(`${baseUrl}/ideas?limit=50&offset=0`);
      } catch (err1) {
        // Fallback to alternate host (127.0.0.1 <-> localhost)
        try {
          response = await fetch(`${altBaseUrl}/ideas?limit=50&offset=0`);
        } catch (err2) {
          response = null;
        }
      }

      if (response && response.ok) {
        const data = await response.json();
        setIdeas(data);
        setErrorMessage(null);
      } else {
        setErrorMessage(
          `Unable to reach LaunchPad AI backend server at ${baseUrl}. Ensure backend server (uvicorn) is running.`
        );
      }
    } catch (err) {
      console.warn("[HistoryPage] Fetch error caught:", err);
      setErrorMessage("Network error: Unable to connect to backend server.");
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleSelectIdea = async (ideaId: string) => {
    await loadIdea(ideaId);
    router.push(`/pipeline?idea_id=${ideaId}`);
  };

  const filteredIdeas = ideas.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.target_market && item.target_market.toLowerCase().includes(searchTerm.toLowerCase())) ||
      item.description.toLowerCase().includes(searchTerm.toLowerCase());

    const normStatus = (item.status || "").toLowerCase();
    let matchesStatus = true;
    if (statusFilter === "completed") {
      matchesStatus = normStatus === "done" || normStatus === "completed";
    } else if (statusFilter === "running") {
      matchesStatus = normStatus === "running" || normStatus === "pending";
    } else if (statusFilter === "failed") {
      matchesStatus = normStatus === "error" || normStatus === "failed";
    }

    return matchesSearch && matchesStatus;
  });

  const totalCount = ideas.length;
  const completedCount = ideas.filter(
    (i) => i.status === "done" || i.status === "completed"
  ).length;

  return (
    <div className="flex flex-col min-h-screen" style={{ background: "var(--background)" }}>
      {/* Ambient glows */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 0 }}>
        <div
          className="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] rounded-full opacity-15"
          style={{ background: "radial-gradient(circle, rgba(212,168,67,0.3) 0%, transparent 70%)" }}
        />
        <div
          className="absolute bottom-[-10%] right-[-5%] w-[450px] h-[450px] rounded-full opacity-10"
          style={{ background: "radial-gradient(circle, rgba(239,35,60,0.25) 0%, transparent 70%)" }}
        />
      </div>

      <Header />

      <main className="relative flex-grow max-w-screen-xl w-full mx-auto px-4 py-8 md:py-12" style={{ zIndex: 1 }}>
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between mb-6 text-[10px] font-mono uppercase tracking-widest">
          <Link
            href="/"
            onClick={resetPipeline}
            className="flex items-center space-x-1.5 transition-colors hover:opacity-80"
            style={{ color: "var(--text-muted)" }}
          >
            <ArrowLeft className="h-3 w-3" />
            <span>Back to Dashboard</span>
          </Link>
          <span style={{ color: "var(--text-muted)" }}>Total Archived: {totalCount} Projects</span>
        </div>

        {/* Hero Title Block */}
        <div className="mb-10 text-left">
          <div className="inline-flex items-center space-x-2 text-[10px] font-mono uppercase tracking-widest mb-3 px-3 py-1 border rounded-full"
            style={{ color: "var(--accent-gold)", borderColor: "var(--border-gold)", background: "var(--accent-gold-dim)" }}>
            <FileClock className="h-3 w-3" />
            <span>Accelerator Diligence Archive</span>
          </div>

          <h1 className="font-serif text-4xl md:text-5xl font-bold tracking-tight mb-3" style={{ color: "var(--text-primary)" }}>
            Submission <span className="text-gold-gradient">History</span>
          </h1>
          <p className="text-sm max-w-2xl font-sans" style={{ color: "var(--text-secondary)" }}>
            Review past startup idea diligence reports, track autonomous multi-agent analysis status, and inspect full investor readiness evaluations.
          </p>
        </div>

        {/* Filters & Control Bar */}
        <div className="glass p-4 rounded-xl mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          {/* Search input */}
          <div className="relative flex-grow max-w-md">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4" style={{ color: "var(--text-muted)" }} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by startup title, market, or description..."
              className="w-full pl-10 pr-4 py-2.5 rounded-lg text-xs font-sans input-dark"
            />
          </div>

          {/* Status Filter Tabs & Refresh */}
          <div className="flex flex-wrap items-center gap-2">
            {[
              { id: "all", label: `All (${totalCount})` },
              { id: "completed", label: `Completed (${completedCount})` },
              { id: "running", label: "Processing" },
              { id: "failed", label: "Failed" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setStatusFilter(tab.id)}
                className={`px-3 py-1.5 rounded-lg font-mono text-[10px] uppercase tracking-wider transition-all cursor-pointer ${
                  statusFilter === tab.id
                    ? "bg-[var(--accent-gold)] text-[#0B1220] font-bold"
                    : "bg-[var(--surface-elevated)] text-[var(--text-muted)] border border-[var(--border-subtle)] hover:text-[var(--text-primary)]"
                }`}
              >
                {tab.label}
              </button>
            ))}

            <button
              onClick={fetchHistory}
              disabled={isRefreshing}
              className="p-2 rounded-lg bg-[var(--surface-elevated)] border border-[var(--border-subtle)] text-[var(--text-muted)] hover:text-[var(--accent-gold)] transition-colors cursor-pointer ml-1"
              title="Refresh submission list"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRefreshing ? "animate-spin text-[var(--accent-gold)]" : ""}`} />
            </button>
          </div>
        </div>

        {/* Error State if Backend Unreachable */}
        {errorMessage ? (
          <div className="glass-bright rounded-2xl p-10 text-center max-w-lg mx-auto glow-border my-8 border-red-500/30">
            <div className="w-14 h-14 rounded-2xl mx-auto mb-5 flex items-center justify-center bg-red-500/10 border border-red-500/30">
              <WifiOff className="h-7 w-7 text-red-400" />
            </div>
            <h3 className="font-serif text-xl font-bold mb-2 text-white">
              Backend Connection Error
            </h3>
            <p className="text-xs text-slate-300 font-sans mb-6 leading-relaxed">
              {errorMessage}
            </p>
            <button
              onClick={fetchHistory}
              disabled={isRefreshing}
              className="btn-shimmer inline-flex items-center space-x-2 px-6 py-3 rounded-xl font-mono text-xs font-bold uppercase tracking-wider cursor-pointer"
              style={{
                background: "linear-gradient(135deg, #d4a843 0%, #b8891e 100%)",
                color: "#06080f",
                boxShadow: "0 4px 20px rgba(212,168,67,0.3)",
              }}
            >
              <RefreshCw className={`h-4 w-4 ${isRefreshing ? "animate-spin" : ""}`} />
              <span>Retry Connection</span>
            </button>
          </div>
        ) : isLoading ? (
          <div className="py-20 text-center flex flex-col items-center justify-center space-y-4">
            <div className="w-10 h-10 rounded-full border-2 border-[var(--accent-gold)] border-dashed animate-spin flex items-center justify-center">
              <div className="w-5 h-5 bg-[var(--accent-gold)] rotate-45 rounded-sm" />
            </div>
            <p className="font-mono text-xs uppercase tracking-widest" style={{ color: "var(--text-muted)" }}>
              Fetching diligence archive...
            </p>
          </div>
        ) : filteredIdeas.length === 0 ? (
          <div className="glass-bright rounded-2xl p-12 text-center max-w-lg mx-auto glow-border my-8">
            <div className="w-14 h-14 rounded-2xl mx-auto mb-5 flex items-center justify-center" style={{ background: "var(--accent-gold-dim)", border: "1px solid var(--border-gold)" }}>
              <FileClock className="h-7 w-7" style={{ color: "var(--accent-gold)" }} />
            </div>
            <h3 className="font-serif text-xl font-bold mb-2" style={{ color: "var(--text-primary)" }}>
              {ideas.length === 0 ? "No Past Submissions Found" : "No Matching Results"}
            </h3>
            <p className="text-xs text-slate-400 font-sans mb-6 leading-relaxed">
              {ideas.length === 0
                ? "You haven't submitted any startup ideas to the acceleration pipeline yet. Submit an idea to generate 7-agent diligence reports."
                : "No submissions matched your search criteria. Try clearing search filters."}
            </p>
            {ideas.length === 0 ? (
              <Link
                href="/"
                onClick={resetPipeline}
                className="btn-shimmer inline-flex items-center space-x-2 px-6 py-3 rounded-xl font-mono text-xs font-bold uppercase tracking-wider"
                style={{
                  background: "linear-gradient(135deg, #d4a843 0%, #b8891e 100%)",
                  color: "#06080f",
                  boxShadow: "0 4px 20px rgba(212,168,67,0.3)",
                }}
              >
                <PlusCircle className="h-4 w-4" />
                <span>Submit Your First Idea</span>
              </Link>
            ) : (
              <button
                onClick={() => { setSearchTerm(""); setStatusFilter("all"); }}
                className="px-4 py-2 rounded-lg font-mono text-xs text-[var(--accent-gold)] border border-[var(--border-gold)] bg-[var(--accent-gold-dim)] cursor-pointer"
              >
                Clear Search Filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredIdeas.map((idea) => {
              const normStatus = (idea.status || "").toLowerCase();
              const isDone = normStatus === "done" || normStatus === "completed";
              const isRunning = normStatus === "running" || normStatus === "pending";
              const isFailed = normStatus === "error" || normStatus === "failed";

              return (
                <div
                  key={idea.id}
                  onClick={() => handleSelectIdea(idea.id)}
                  className="glass-bright p-6 rounded-xl hover:border-[var(--accent-gold)] transition-all duration-300 group cursor-pointer flex flex-col justify-between relative overflow-hidden"
                  style={{
                    boxShadow: "0 4px 16px rgba(0,0,0,0.2)",
                  }}
                >
                  {/* Subtle hover accent bar */}
                  <div className="absolute top-0 left-0 right-0 h-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                    style={{ background: "linear-gradient(90deg, transparent, var(--accent-gold), transparent)" }} />

                  <div>
                    {/* Top Row: Title & Status Badge */}
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <h3 className="font-serif text-lg font-bold leading-tight group-hover:text-[var(--accent-gold-bright)] transition-colors"
                        style={{ color: "var(--text-primary)" }}>
                        {idea.title}
                      </h3>

                      {isDone && (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[9px] font-mono uppercase tracking-wider font-bold shrink-0 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                          <CheckCircle2 className="h-3 w-3" />
                          <span>Completed</span>
                        </span>
                      )}

                      {isRunning && (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[9px] font-mono uppercase tracking-wider font-bold shrink-0 bg-[var(--accent-gold-dim)] border border-[var(--border-gold)] text-[var(--accent-gold)]">
                          <Clock className="h-3 w-3 animate-spin" />
                          <span>Processing</span>
                        </span>
                      )}

                      {isFailed && (
                        <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-[9px] font-mono uppercase tracking-wider font-bold shrink-0 bg-red-500/10 border border-red-500/30 text-red-400">
                          <AlertCircle className="h-3 w-3" />
                          <span>Failed</span>
                        </span>
                      )}
                    </div>

                    {/* Target market pill */}
                    {idea.target_market && (
                      <span className="inline-block text-[9px] font-mono uppercase tracking-widest px-2.5 py-0.5 rounded mb-3"
                        style={{ background: "var(--primary-navy-light)", color: "var(--accent-gold)", border: "1px solid var(--border-subtle)" }}>
                        Market: {idea.target_market}
                      </span>
                    )}

                    {/* Description snippet */}
                    <p className="text-xs leading-relaxed line-clamp-2 mb-5 font-sans" style={{ color: "var(--text-secondary)" }}>
                      {idea.description}
                    </p>
                  </div>

                  {/* Bottom Bar Metadata */}
                  <div className="pt-4 flex items-center justify-between border-t border-[var(--border-subtle)] text-[10px] font-mono" style={{ color: "var(--text-muted)" }}>
                    <div className="flex items-center space-x-3">
                      <span>{formatRelativeTime(idea.created_at)}</span>
                      <span>•</span>
                      <span>ID: {idea.id.substring(0, 8)}</span>
                    </div>

                    <div className="flex items-center space-x-1 group-hover:text-[var(--accent-gold)] transition-colors font-bold uppercase tracking-wider">
                      <span>View Report</span>
                      <ArrowRight className="h-3 w-3 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
