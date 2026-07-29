"use client";

import React from "react";
import { Agent2Output } from "@/types/agentContracts";
import { ExternalLink, AlertTriangle, Scale } from "lucide-react";

interface Props {
  data: Agent2Output;
}

export const Agent2Patent: React.FC<Props> = ({ data }) => {
  const riskLevel = (data?.risk_level || "MEDIUM").toString();

  const getRiskColors = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "low":
        return {
          bg: "bg-green-50 text-green-700 border-green-200",
          dot: "bg-green-600",
        };
      case "high":
        return {
          bg: "bg-red-50 text-red-700 border-red-200",
          dot: "bg-red-600",
        };
      case "medium":
      default:
        return {
          bg: "bg-yellow-50 text-yellow-800 border-yellow-200",
          dot: "bg-yellow-600",
        };
    }
  };

  const riskStyle = getRiskColors(riskLevel);
  const similarPatents = Array.isArray(data?.similar_patents) ? data.similar_patents : [];
  const notes = data?.notes || "Freedom to operate analysis unavailable.";

  return (
    <div className="bg-white border border-[#E2E8F0] p-6 md:p-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-start border-b border-[#E2E8F0] pb-6 mb-6">
        <div>
          <span className="font-mono text-xs text-[#C9A227] uppercase tracking-wider">
            Stage 02 — Patent & Prior Art Search
          </span>
          <h3 className="font-serif text-2xl font-semibold text-[#1A202C] mt-1">
            Intellectual Property Risk Assessment
          </h3>
        </div>
        <div className={`mt-4 md:mt-0 flex items-center space-x-2 border px-3.5 py-1.5 font-mono text-xs uppercase tracking-wider ${riskStyle.bg}`}>
          <span className={`h-2.5 w-2.5 rounded-full ${riskStyle.dot}`}></span>
          <span>{riskLevel} IP Conflict Risk</span>
        </div>
      </div>

      {/* Prior Art Table */}
      <div className="space-y-4 mb-6">
        <h4 className="font-serif text-sm font-semibold text-[#1A202C] flex items-center space-x-2">
          <Scale className="h-4 w-4 text-slate-700 shrink-0" />
          <span>Relevant Prior Art Patents</span>
        </h4>

        <div className="overflow-x-auto border border-[#E2E8F0]">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#F7F8FA] border-b border-[#E2E8F0] font-mono text-[10px] text-slate-500 uppercase tracking-widest">
                <th className="p-4 w-1/3">Patent Title</th>
                <th className="p-4 w-1/2">Technical Summary</th>
                <th className="p-4 text-right">Reference</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E2E8F0] text-sm text-[#4A5568]">
              {similarPatents.length > 0 ? (
                similarPatents.map((pat, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 transition-colors">
                    <td className="p-4 font-serif font-semibold text-[#1A202C] leading-snug">
                      {pat?.title || "Untitled Patent"}
                    </td>
                    <td className="p-4 leading-relaxed font-sans">
                      {pat?.summary || "No technical summary provided."}
                    </td>
                    <td className="p-4 text-right">
                      {pat?.source_url ? (
                        <a
                          href={pat.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center space-x-1.5 text-xs font-mono text-[#C9A227] hover:text-[#0B1220] transition-colors font-bold"
                        >
                          <span>PATENT LINK</span>
                          <ExternalLink className="h-3.5 w-3.5" />
                        </a>
                      ) : (
                        <span className="text-xs font-mono text-slate-400">N/A</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={3} className="p-6 text-center text-xs font-mono text-slate-400">
                    No direct prior art patent conflicts detected for this query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Legal & Integration Notes */}
      <div className="space-y-2 border-t border-[#E2E8F0] pt-6">
        <h4 className="font-serif text-sm font-semibold text-[#1A202C] flex items-center space-x-2">
          <AlertTriangle className="h-4 w-4 text-[#C9A227] shrink-0" />
          <span>Freedom to Operate Analysis</span>
        </h4>
        <p className="text-sm text-[#4A5568] leading-relaxed font-sans">
          {notes}
        </p>
      </div>
    </div>
  );
};
