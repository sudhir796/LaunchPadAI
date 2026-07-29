"use client";

import React from "react";
import { Agent5Output } from "@/types/agentContracts";
import { DollarSign, Landmark, Compass, Target, Layers } from "lucide-react";

interface Props {
  data: Agent5Output;
}

const safeRender = (val: any): string => {
  if (val === null || val === undefined) return "";
  if (typeof val === "string") return val;
  if (typeof val === "number" || typeof val === "boolean") return String(val);
  if (typeof val === "object") {
    if (Array.isArray(val)) return val.map(safeRender).join(", ");
    return val.description || val.text || val.title || val.name || val.value || val.content || JSON.stringify(val);
  }
  return String(val);
};

export const Agent5BusinessModel: React.FC<Props> = ({ data }) => {
  const customerSegments = Array.isArray(data?.customer_segments) ? data.customer_segments : [];
  const channels = Array.isArray(data?.channels) ? data.channels : [];
  const revenueStreams = Array.isArray(data?.revenue_streams) ? data.revenue_streams : [];
  const costStructure = Array.isArray(data?.cost_structure) ? data.cost_structure : [];

  return (
    <div className="bg-white border border-[#E2E8F0] p-6 md:p-8">
      {/* Header */}
      <div className="border-b border-[#E2E8F0] pb-6 mb-6">
        <span className="font-mono text-xs text-[#C9A227] uppercase tracking-wider">
          Stage 05 — Business Model Canvas
        </span>
        <h3 className="font-serif text-2xl font-semibold text-[#1A202C] mt-1">
          Strategic Monetization & Value Architecture
        </h3>
      </div>

      {/* Value Proposition Hero */}
      <div className="border border-[#E2E8F0] p-6 mb-8 bg-[#0B1220] text-white">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 mb-3">
          <Landmark className="h-4 w-4 text-[#C9A227] shrink-0" />
          <span className="font-mono text-[10px] tracking-wider uppercase text-slate-400">
            Core Value Proposition
          </span>
        </div>
        <p className="font-serif text-lg leading-relaxed text-[#F7F8FA]">
          {safeRender(data?.value_proposition)}
        </p>
      </div>

      {/* Structured Canvas Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Customer Segments */}
        <div className="border border-[#E2E8F0] p-5">
          <div className="flex items-center space-x-2 border-b border-[#E2E8F0] pb-2 mb-3">
            <Target className="h-4 w-4 text-slate-700 shrink-0" />
            <span className="font-serif text-sm font-semibold text-[#1A202C]">
              Customer Segments
            </span>
          </div>
          <ul className="space-y-2 text-xs text-[#4A5568] leading-relaxed">
            {customerSegments.map((seg, idx) => (
              <li key={idx} className="pl-3 border-l border-[#C9A227]">
                {safeRender(seg)}
              </li>
            ))}
          </ul>
        </div>

        {/* Channels */}
        <div className="border border-[#E2E8F0] p-5">
          <div className="flex items-center space-x-2 border-b border-[#E2E8F0] pb-2 mb-3">
            <Compass className="h-4 w-4 text-slate-700 shrink-0" />
            <span className="font-serif text-sm font-semibold text-[#1A202C]">
              Acquisition Channels
            </span>
          </div>
          <ul className="space-y-2 text-xs text-[#4A5568] leading-relaxed">
            {channels.map((chan, idx) => (
              <li key={idx} className="pl-3 border-l border-slate-300">
                {safeRender(chan)}
              </li>
            ))}
          </ul>
        </div>

        {/* Key Resources / Layer Info */}
        <div className="border border-[#E2E8F0] p-5 bg-[#F7F8FA]">
          <div className="flex items-center space-x-2 border-b border-[#E2E8F0] pb-2 mb-3">
            <Layers className="h-4 w-4 text-[#C9A227] shrink-0" />
            <span className="font-serif text-sm font-semibold text-[#1A202C]">
              Strategic Alignment
            </span>
          </div>
          <p className="text-xs text-[#4A5568] leading-relaxed font-sans">
            The revenue and cost models map directly to local hardware deployments, utilizing 
            SaaS licensing to reduce customer acquisition friction in initial target clusters.
          </p>
        </div>
      </div>

      {/* Revenue & Cost Structure Side-by-Side */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-[#E2E8F0] pt-6">
        {/* Revenue Streams */}
        <div className="space-y-4">
          <h4 className="font-serif text-sm font-semibold text-[#1A202C] flex items-center space-x-2">
            <DollarSign className="h-4 w-4 text-[#C9A227] shrink-0" />
            <span>Monetization & Revenue Streams</span>
          </h4>
          <ul className="space-y-2.5 text-xs text-[#4A5568] leading-relaxed font-mono">
            {revenueStreams.map((rev, idx) => (
              <li key={idx} className="p-3 bg-[#F7F8FA] border border-[#E2E8F0]">
                {safeRender(rev)}
              </li>
            ))}
          </ul>
        </div>

        {/* Cost Structure */}
        <div className="space-y-4">
          <h4 className="font-serif text-sm font-semibold text-[#1A202C] flex items-center space-x-2">
            <Landmark className="h-4 w-4 text-slate-700 shrink-0" />
            <span>Operational Cost Structure</span>
          </h4>
          <ul className="space-y-2.5 text-xs text-[#4A5568] leading-relaxed font-mono">
            {costStructure.map((cost, idx) => (
              <li key={idx} className="p-3 bg-white border border-[#E2E8F0]">
                {safeRender(cost)}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
