"use client";

import React, { useState } from "react";
import { Agent6Output } from "@/types/agentContracts";
import { ChevronLeft, ChevronRight, Presentation } from "lucide-react";

interface Props {
  data: Agent6Output;
}

export const Agent6PitchDeck: React.FC<Props> = ({ data }) => {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  const slides = Array.isArray(data?.slides) ? data.slides : [];
  const currentSlide = slides[currentSlideIndex];

  const handlePrev = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex(currentSlideIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentSlideIndex < slides.length - 1) {
      setCurrentSlideIndex(currentSlideIndex + 1);
    }
  };

  if (slides.length === 0) {
    return (
      <div className="bg-white border border-[#E2E8F0] p-6 text-center text-slate-500 font-mono text-sm">
        No slides generated for this pitch deck.
      </div>
    );
  }

  // Parse slide content: lines starting with bullet points or standard paragraphs
  const slideContent: any = currentSlide?.content;
  const rawContent: string = typeof slideContent === "string"
    ? slideContent
    : (slideContent && typeof slideContent === "object" ? (slideContent.description || slideContent.text || JSON.stringify(slideContent)) : String(slideContent || ""));

  const parsedContent: string[] = rawContent ? rawContent.split("\n").filter((line: string) => line && line.trim() !== "") : ["Content unavailable for this slide."];

  return (
    <div className="bg-white border border-[#E2E8F0]">
      {/* Stage header */}
      <div className="px-6 md:px-8 pt-6 pb-5 border-b border-[#E2E8F0] flex items-center justify-between">
        <div>
          <span className="font-mono text-[10px] text-[#C9A227] uppercase tracking-widest block mb-1">
            Stage 06 — Pitch Deck
          </span>
          <h3 className="font-serif text-2xl font-bold text-[#0B1220] flex items-center space-x-2">
            <Presentation className="h-5 w-5 text-slate-600 shrink-0" />
            <span>Investor Pitch Deck Simulator</span>
          </h3>
        </div>
        <span className="hidden md:block font-mono text-[9px] text-slate-400 uppercase tracking-widest border border-[#E2E8F0] px-3 py-1.5">
          Use arrows to navigate slides
        </span>
      </div>

      {/* Slide canvas */}
      <div className="px-6 md:px-8 pb-8">
        <div className="w-full flex flex-col items-center">
          <div className="relative w-full aspect-[16/9] bg-[#0B1220] border border-[#1A202C] text-[#F7F8FA] p-8 md:p-12 lg:p-16 flex flex-col justify-between overflow-hidden shadow-lg">
            {/* Slide header */}
            <div className="flex justify-between items-center border-b border-slate-800 pb-4">
              <span className="font-mono text-[9px] uppercase tracking-widest text-[#C9A227] font-semibold">
                LAUNCHPAD AI // PROJECT DECK
              </span>
              <span className="font-mono text-[9px] uppercase tracking-widest text-slate-500">
                BOARDROOM COPY
              </span>
            </div>

            {/* Slide body */}
            <div className="my-auto py-4">
              <h4 className="font-serif text-2xl md:text-3xl lg:text-4xl font-semibold text-white tracking-tight leading-tight mb-4 md:mb-6">
                {currentSlide?.title || "Untitled Slide"}
              </h4>
              <div className="space-y-2 md:space-y-3">
                {parsedContent.map((paragraph, index) => {
                  const isBullet = paragraph.trim().startsWith("•") || paragraph.trim().startsWith("-");
                  const text = isBullet ? paragraph.substring(1).trim() : paragraph;
                  return (
                    <div key={index} className="flex items-start text-xs md:text-sm lg:text-base text-slate-300 leading-relaxed font-sans">
                      {isBullet ? <span className="text-[#C9A227] mr-2 text-base leading-none shrink-0">•</span> : null}
                      <span>{text}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Slide footer */}
            <div className="flex justify-between items-center border-t border-slate-800 pt-4 text-[9px] font-mono text-slate-500">
              <span>CONFIDENTIAL &amp; PROPRIETARY</span>
              <span>
                {String(currentSlideIndex + 1).padStart(2, "0")} / {String(slides.length).padStart(2, "0")}
              </span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex justify-between items-center w-full mt-4 bg-white border border-[#E2E8F0] p-3 font-mono text-xs">
            <button
              onClick={handlePrev}
              disabled={currentSlideIndex === 0}
              className={`flex items-center space-x-1.5 px-3 py-1.5 border transition-all font-semibold ${
                currentSlideIndex === 0
                  ? "text-slate-300 border-[#E2E8F0] cursor-not-allowed bg-[#F7F8FA]"
                  : "text-[#0B1220] border-[#E2E8F0] hover:border-[#C9A227] hover:text-[#C9A227] bg-white cursor-pointer"
              }`}
            >
              <ChevronLeft className="h-4 w-4" />
              <span>PREV</span>
            </button>

            <div className="text-[#0B1220] font-semibold tracking-widest text-[10px]">
              SLIDE {currentSlideIndex + 1} OF {slides.length}
            </div>

            <button
              onClick={handleNext}
              disabled={currentSlideIndex === slides.length - 1}
              className={`flex items-center space-x-1.5 px-3 py-1.5 border transition-all font-semibold ${
                currentSlideIndex === slides.length - 1
                  ? "text-slate-300 border-[#E2E8F0] cursor-not-allowed bg-[#F7F8FA]"
                  : "text-[#0B1220] border-[#E2E8F0] hover:border-[#C9A227] hover:text-[#C9A227] bg-white cursor-pointer"
              }`}
            >
              <span>NEXT</span>
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
