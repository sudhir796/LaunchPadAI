"use client";

import React from "react";
import { Agent3Output } from "@/types/agentContracts";
import { TrendingUp, Users, FileText, Link2 } from "lucide-react";

interface Props {
  data: Agent3Output;
}

export const Agent3Market: React.FC<Props> = ({ data }) => {
  return (
    <div className="bg-white border border-[#E2E8F0] p-6 md:p-8">
      {/* Header */}
      <div className="border-b border-[#E2E8F0] pb-6 mb-6">
        <span className="font-mono text-xs text-[#C9A227] uppercase tracking-wider">
          Stage 03 — Market Research
        </span>
        <h3 className="font-serif text-2xl font-semibold text-[#1A202C] mt-1">
          Market Sizing & Demographics
        </h3>
      </div>

      {/* Grid of Key Market Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* TAM Card */}
        <div className="border border-[#E2E8F0] p-5 bg-[#F7F8FA] flex flex-col justify-between">
          <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest">
            Total Addressable Market (TAM)
          </span>
          <div className="mt-4">
            <span className="font-mono text-2xl md:text-3xl font-bold tracking-tight text-[#0B1220]">
              {data.market_size_estimate.split(" ")[0]}
            </span>
            <span className="font-serif text-base text-[#4A5568] ml-2">
              {data.market_size_estimate.split(" ").slice(1).join(" ")}
            </span>
          </div>
          <span className="font-mono text-[9px] text-[#C9A227] uppercase tracking-widest mt-2">
            Projected Estimate
          </span>
        </div>

        {/* Demographics Summary Card */}
        <div className="border border-[#E2E8F0] p-5 flex flex-col justify-between">
          <div className="flex items-center space-x-2 border-b border-[#E2E8F0] pb-2 mb-3">
            <Users className="h-4 w-4 text-[#C9A227] shrink-0" />
            <span className="font-serif text-sm font-semibold text-[#1A202C]">
              Primary Target Demographics
            </span>
          </div>
          <p className="text-sm text-[#4A5568] leading-relaxed font-sans">
            {data.target_demographics}
          </p>
        </div>
      </div>

      {/* Growth Trends & Industry Analysis */}
      <div className="space-y-4 mb-8">
        <h4 className="font-serif text-sm font-semibold text-[#1A202C] flex items-center space-x-2 border-b border-[#E2E8F0] pb-1.5">
          <TrendingUp className="h-4 w-4 text-slate-700 shrink-0" />
          <span>Growth Trends & Macro Factors</span>
        </h4>
        <p className="text-sm text-[#4A5568] leading-relaxed font-sans">
          {data.growth_trends}
        </p>
      </div>

      {/* Verified Sources */}
      <div className="border-t border-[#E2E8F0] pt-6 space-y-3">
        <span className="font-mono text-[10px] text-slate-500 uppercase tracking-widest block">
          Verified Secondary Sources
        </span>
        <div className="flex flex-wrap gap-3">
          {data.sources.map((url, idx) => {
            let domain = "";
            try {
              domain = new URL(url).hostname;
            } catch {
              domain = "Source Report";
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
    </div>
  );
};
