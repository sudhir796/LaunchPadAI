"use client";

import React from "react";
import { Agent4Output } from "@/types/agentContracts";
import { ExternalLink, Swords, Lightbulb, Link2 } from "lucide-react";

interface Props {
  data: Agent4Output;
}

export const Agent4Competitors: React.FC<Props> = ({ data }) => {
  const competitors = Array.isArray(data?.competitors) ? data.competitors : [];
  const diffOpp = data?.differentiation_opportunities || "Differentiation opportunities analysis unavailable.";
  const sources = Array.isArray(data?.sources) ? data.sources : [];

  return (
    <div className="bg-white border border-[#E2E8F0] p-6 md:p-8">
      {/* Header */}
      <div className="border-b border-[#E2E8F0] pb-6 mb-6">
        <span className="font-mono text-xs text-[#C9A227] uppercase tracking-wider">
          Stage 04 — Competitor Analysis
        </span>
        <h3 className="font-serif text-2xl font-semibold text-[#1A202C] mt-1">
          Market Mapping & Competitive Matrix
        </h3>
      </div>

      {/* Competitors List */}
      <div className="space-y-4 mb-8">
        <h4 className="font-serif text-sm font-semibold text-[#1A202C] flex items-center space-x-2">
          <Swords className="h-4 w-4 text-slate-700 shrink-0" />
          <span>Primary Market Competitors</span>
        </h4>

        {competitors.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {competitors.map((comp, idx) => (
              <div key={idx} className="border border-[#E2E8F0] p-5 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center border-b border-[#E2E8F0] pb-2 mb-3">
                    <h5 className="font-serif font-bold text-[#1A202C]">
                      {comp?.name || "Unnamed Competitor"}
                    </h5>
                    {comp?.source_url ? (
                      <a
                        href={comp.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-400 hover:text-[#C9A227] transition-colors"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    ) : null}
                  </div>
                  <p className="text-sm text-[#4A5568] leading-relaxed font-sans mb-4">
                    {comp?.description || "No description provided."}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4 border-t border-[#E2E8F0] pt-3 text-xs">
                  <div>
                    <span className="font-mono text-[9px] text-[#C9A227] uppercase tracking-wider block mb-1">
                      Strengths
                    </span>
                    <span className="text-[#4A5568] leading-relaxed font-sans">
                      {comp?.strengths || "N/A"}
                    </span>
                  </div>
                  <div>
                    <span className="font-mono text-[9px] text-slate-500 uppercase tracking-wider block mb-1">
                      Weaknesses
                    </span>
                    <span className="text-[#4A5568] leading-relaxed font-sans">
                      {comp?.weaknesses || "N/A"}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="border border-[#E2E8F0] p-6 text-center text-xs font-mono text-slate-400">
            No direct commercial competitors mapped for this market category.
          </div>
        )}
      </div>

      {/* Differentiation Opportunities */}
      <div className="border-t border-[#E2E8F0] pt-6 space-y-3">
        <h4 className="font-serif text-sm font-semibold text-[#1A202C] flex items-center space-x-2">
          <Lightbulb className="h-4 w-4 text-[#C9A227] shrink-0" />
          <span>Differentiation Opportunities</span>
        </h4>
        <p className="text-sm text-[#4A5568] leading-relaxed font-sans bg-[#0B1220]/5 border border-[#0B1220]/10 p-4">
          {diffOpp}
        </p>
      </div>

      {/* Verified Secondary Sources */}
      {sources.length > 0 && (
        <div className="border-t border-[#E2E8F0] pt-6 space-y-3 mt-6">
          <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest block">
            Verified Secondary Sources
          </span>
          <div className="flex flex-wrap gap-3">
            {sources.map((url, idx) => {
              let domain = "";
              try {
                domain = new URL(url).hostname;
              } catch {
                domain = url || "Source Report";
              }
              return (
                <a
                  key={idx}
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 border border-[#E2E8F0] px-3 py-1.5 text-xs font-mono text-[#4A5568] hover:text-[#C9A227] hover:border-[#C9A227] transition-all bg-white"
                >
                  <Link2 className="h-3.5 w-3.5" />
                  <span>{domain}</span>
                </a>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
