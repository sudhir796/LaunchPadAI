"use client";

import React from "react";
import { Agent1Output } from "@/types/agentContracts";
import { ShieldCheck, ShieldAlert, Award, CheckCircle2 } from "lucide-react";

interface Props {
  data: Agent1Output;
}

export const Agent1Validator: React.FC<Props> = ({ data }) => {
  const scoreColor =
    data.validation_score >= 75 ? "text-emerald-600" :
    data.validation_score >= 50 ? "text-amber-600" :
    "text-red-600";

  const scoreBg =
    data.validation_score >= 75 ? "bg-emerald-50 border-emerald-200" :
    data.validation_score >= 50 ? "bg-amber-50 border-amber-200" :
    "bg-red-50 border-red-200";

  return (
    <div className="bg-white border border-[#E2E8F0]">
      {/* Stage header */}
      <div className="px-6 md:px-8 pt-6 pb-5 border-b border-[#E2E8F0] flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <span className="font-mono text-[10px] text-[#C9A227] uppercase tracking-widest block mb-1">
            Stage 01 — Idea Validation
          </span>
          <h3 className="font-serif text-2xl font-bold text-[#0B1220]">
            Feasibility & Venture Score
          </h3>
        </div>
        {/* Score badge */}
        <div className={`flex items-center space-x-3 border px-5 py-3 shrink-0 ${scoreBg}`}>
          <Award className={`h-5 w-5 shrink-0 ${scoreColor}`} />
          <div>
            <div className="font-mono text-[9px] text-slate-500 uppercase tracking-widest">Validation Score</div>
            <div className={`font-mono text-2xl font-black tracking-tight ${scoreColor}`}>
              {data.validation_score}<span className="text-sm font-normal text-slate-400">/100</span>
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 md:px-8 py-6 space-y-6">
        {/* Strengths & Weaknesses */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Strengths */}
          <div>
            <h4 className="flex items-center space-x-2 font-mono text-[10px] uppercase tracking-widest text-emerald-700 mb-3 font-semibold">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Identified Strengths</span>
            </h4>
            <ul className="space-y-2.5">
              {data.strengths.map((str, idx) => (
                <li key={idx} className="flex items-start space-x-2.5 text-sm text-[#0B1220] leading-relaxed">
                  <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                  <span>{str}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Weaknesses */}
          <div>
            <h4 className="flex items-center space-x-2 font-mono text-[10px] uppercase tracking-widest text-red-600 mb-3 font-semibold">
              <ShieldAlert className="h-3.5 w-3.5" />
              <span>Risks & Weaknesses</span>
            </h4>
            <ul className="space-y-2.5">
              {data.weaknesses.map((weak, idx) => (
                <li key={idx} className="flex items-start space-x-2.5 text-sm text-[#0B1220] leading-relaxed">
                  <div className="h-1.5 w-1.5 rounded-full bg-red-400 shrink-0 mt-2" />
                  <span>{weak}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Feasibility Notes */}
        <div className="border border-[#E2E8F0] p-5 bg-[#F7F8FA]">
          <h4 className="font-mono text-[10px] uppercase tracking-widest text-slate-500 mb-3 font-semibold">
            Feasibility Analysis
          </h4>
          <p className="text-sm text-[#0B1220] leading-relaxed font-sans">{data.feasibility_notes}</p>
        </div>

        {/* Recommendation */}
        <div className="flex flex-col md:flex-row md:items-center md:space-x-4 border border-[#C9A227]/40 bg-[#C9A227]/5 p-5">
          <span className="font-mono text-[9px] text-[#C9A227] uppercase tracking-widest shrink-0 mb-2 md:mb-0 font-bold">
            Recommended Pathway:
          </span>
          <p className="text-sm font-semibold text-[#0B1220] font-sans">{data.recommendation}</p>
        </div>
      </div>
    </div>
  );
};
