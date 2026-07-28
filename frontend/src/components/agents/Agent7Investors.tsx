"use client";

import React, { useState } from "react";
import { Agent7Output } from "@/types/agentContracts";
import { Briefcase, Target, Sparkles, Download, Loader2 } from "lucide-react";
import { usePipeline } from "@/context/PipelineContext";

interface Props {
  data: Agent7Output;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const RANK_COLORS = [
  "bg-[#C9A227] text-white",
  "bg-slate-600 text-white",
  "bg-amber-700 text-white",
];

export const Agent7Investors: React.FC<Props> = ({ data }) => {
  const { state } = usePipeline();
  const [downloading, setDownloading] = useState(false);

  const handleDownloadReport = async () => {
    if (!state.idea_id) return;
    setDownloading(true);
    try {
      const reportUrl = `${API_BASE_URL}/ideas/${state.idea_id}/report`;
      const link = document.createElement("a");
      link.href = reportUrl;
      link.download = `LaunchPad_Report_${state.idea_id.slice(0, 8)}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (e) {
      console.error("Error downloading report:", e);
    } finally {
      setTimeout(() => setDownloading(false), 1000);
    }
  };

  return (
    <div className="bg-white border border-[#E2E8F0]">
      {/* Stage header */}
      <div className="px-6 md:px-8 pt-6 pb-5 border-b border-[#E2E8F0] flex items-center justify-between">
        <div>
          <span className="font-mono text-[10px] text-[#C9A227] uppercase tracking-widest block mb-1">
            Stage 07 — Investor Matching
          </span>
          <h3 className="font-serif text-2xl font-bold text-[#0B1220] flex items-center space-x-2">
            <Briefcase className="h-5 w-5 text-slate-600 shrink-0" />
            <span>Curated Investor Matches</span>
          </h3>
        </div>
        <div className="hidden md:flex items-center space-x-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5">
          <Sparkles className="h-3.5 w-3.5 text-emerald-600" />
          <span className="font-mono text-[9px] text-emerald-700 uppercase tracking-widest font-bold">
            {data.matched_investors.length} Matches Found
          </span>
        </div>
      </div>

      {/* Investor list */}
      <div className="px-6 md:px-8 py-6 space-y-4">
        {data.matched_investors.map((inv, idx) => (
          <div
            key={idx}
            className="border border-[#E2E8F0] hover:border-[#C9A227]/40 hover:shadow-sm transition-all"
          >
            <div className="p-5">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 mb-4">
                {/* Name + rank */}
                <div className="flex items-center space-x-3">
                  <span className={`h-7 w-7 flex items-center justify-center text-xs font-bold font-mono rounded-sm shrink-0 ${RANK_COLORS[idx] ?? "bg-slate-200 text-slate-700"}`}>
                    {idx + 1}
                  </span>
                  <h4 className="font-serif text-lg font-bold text-[#0B1220]">{inv.name}</h4>
                </div>
                {/* Focus pill */}
                <span className="font-mono text-[9px] text-[#4A5568] border border-[#E2E8F0] px-3 py-1.5 bg-[#F7F8FA] uppercase tracking-wider max-w-sm">
                  {inv.focus_area}
                </span>
              </div>

              {/* Rationale */}
              <div className="border-t border-[#E2E8F0] pt-4">
                <h5 className="flex items-center space-x-1.5 font-mono text-[9px] text-[#C9A227] uppercase tracking-widest font-bold mb-2">
                  <Target className="h-3 w-3" />
                  <span>Matching Rationale</span>
                </h5>
                <p className="text-sm text-[#0B1220] leading-relaxed font-sans">{inv.reason}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Final callout banner */}
      <div className="mx-6 md:mx-8 mb-6 bg-[#0B1220] p-6 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <Sparkles className="h-8 w-8 text-[#C9A227] shrink-0" />
          <div>
            <h4 className="font-serif text-base font-bold text-white">
              Venture Intelligence Complete
            </h4>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              This startup profile meets parameters for professional due diligence submission.
            </p>
          </div>
        </div>
        <button
          onClick={handleDownloadReport}
          disabled={downloading || !state.idea_id}
          className="flex items-center space-x-2 bg-[#C9A227] hover:bg-[#b8921f] text-[#0B1220] font-mono text-xs font-bold uppercase px-5 py-3 transition-all shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {downloading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          <span>{downloading ? "Generating PDF..." : "Export Full PDF Report"}</span>
        </button>
      </div>
    </div>
  );
};
