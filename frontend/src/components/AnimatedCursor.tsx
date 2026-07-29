"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";

/* ─────────────────────────────────────────────────────────
   Types
───────────────────────────────────────────────────────── */
interface Star {
  id: number;
  x: number;
  y: number;
  size: number;
  opacity: number;
  rotation: number;
  vx: number;
  vy: number;
  life: number;
  decay: number;
  scale: number;
}

interface ClickBurst {
  id: number;
  x: number;
  y: number;
  progress: number;
}

/* ─────────────────────────────────────────────────────────
   Constants
───────────────────────────────────────────────────────── */
const MAX_STARS       = 28;
const STAR_SPAWN_DIST = 4;
const BURST_COUNT     = 8;

let globalId = 0;
const nextId = () => ++globalId;

// Single gold spark color palette
const STAR_COLORS = [
  { inner: "#ffffff", mid: "#f0c060", outer: "#c9a227" },   // bright white-gold
  { inner: "#fffdf0", mid: "#d4a843", outer: "#b8891e" },   // rich warm gold
  { inner: "#fff9e6", mid: "#e5c158", outer: "#a67c1e" },   // champagne gold
];

/* ─────────────────────────────────────────────────────────
   SVG Star shape (4-pointed sparkle)
───────────────────────────────────────────────────────── */
const SparkStar = ({
  size,
  opacity,
  rotation,
  scale,
  colorIdx,
}: {
  size: number;
  opacity: number;
  rotation: number;
  scale: number;
  colorIdx: number;
}) => {
  const col = STAR_COLORS[colorIdx % STAR_COLORS.length];
  const gradId = `sg_${colorIdx}`;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 20 20"
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        opacity,
        transform: `rotate(${rotation}deg) scale(${scale})`,
        filter: `drop-shadow(0 0 ${size * 0.5}px ${col.mid}) drop-shadow(0 0 ${size * 0.2}px #fff)`,
        pointerEvents: "none",
      }}
    >
      <path
        d="M10 0 L11.5 8.5 L20 10 L11.5 11.5 L10 20 L8.5 11.5 L0 10 L8.5 8.5 Z"
        fill={`url(#${gradId})`}
      />
      <defs>
        <radialGradient id={gradId} cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor={col.inner} />
          <stop offset="50%" stopColor={col.mid} />
          <stop offset="100%" stopColor={col.outer} stopOpacity="0.6" />
        </radialGradient>
      </defs>
    </svg>
  );
};

/* ─────────────────────────────────────────────────────────
   Main cursor — small SVG arrow, works on ANY background
───────────────────────────────────────────────────────── */
const CursorDot = ({
  x,
  y,
  clicked,
  linkHovered,
  hidden,
}: {
  x: number;
  y: number;
  clicked: boolean;
  linkHovered: boolean;
  hidden: boolean;
}) => {
  const scale = clicked ? 0.75 : linkHovered ? 1.15 : 1;

  return (
    <>
      {/* Small SVG arrow cursor */}
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          pointerEvents: "none",
          zIndex: 100000,
          opacity: hidden ? 0 : 1,
          transform: `translate3d(${x}px, ${y}px, 0) scale(${scale})`,
          transition: "transform 0.04s linear, opacity 0.25s",
          willChange: "transform",
          transformOrigin: "0 0",
          filter: linkHovered
            ? "drop-shadow(0 0 6px #f0c060) drop-shadow(0 0 10px rgba(212,168,67,0.7))"
            : "drop-shadow(0 0 3px rgba(0,0,0,0.9)) drop-shadow(0 0 5px rgba(240,192,96,0.5))",
        }}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Dark outline path for visibility on light backgrounds */}
          <path
            d="M3 2 L3 15 L7 11 L10 18 L12.5 17 L9.5 10 L14.5 10 Z"
            fill="rgba(0,0,0,0.75)"
            stroke="rgba(0,0,0,0.6)"
            strokeWidth="1"
            strokeLinejoin="round"
          />
          {/* Bright fill — gold with bright gold tint on hover */}
          <path
            d="M3 2 L3 15 L7 11 L10 18 L12.5 17 L9.5 10 L14.5 10 Z"
            fill={linkHovered ? "#f0c060" : "#d4a843"}
            stroke={linkHovered ? "rgba(255,255,255,0.9)" : "rgba(255,255,255,0.5)"}
            strokeWidth="0.5"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </>
  );
};

/* ─────────────────────────────────────────────────────────
   AnimatedCursor — main export
───────────────────────────────────────────────────────── */
interface StarWithColor extends Star {
  colorIdx: number;
}

export const AnimatedCursor: React.FC = () => {
  const [pos, setPos]                 = useState({ x: -200, y: -200 });
  const [clicked, setClicked]         = useState(false);
  const [linkHovered, setLinkHovered] = useState(false);
  const [hidden, setHidden]           = useState(true);
  const [isMobile, setIsMobile]       = useState(false);
  const [stars, setStars]             = useState<StarWithColor[]>([]);
  const [bursts, setBursts]           = useState<ClickBurst[]>([]);

  const lastSpawnPos  = useRef({ x: -9999, y: -9999 });
  const rafRef        = useRef<number | null>(null);
  const starsRef      = useRef<StarWithColor[]>([]);
  const burstsRef     = useRef<ClickBurst[]>([]);
  const colorIdxRef   = useRef(0);

  /* ── helpers ── */
  const spawnStar = useCallback(
    (x: number, y: number, isBurst = false): StarWithColor => {
      const colorIdx = colorIdxRef.current++ % STAR_COLORS.length;
      return {
        id: nextId(),
        colorIdx,
        x: x + (Math.random() - 0.5) * 12,
        y: y + (Math.random() - 0.5) * 12,
        size: isBurst ? 12 + Math.random() * 10 : 7 + Math.random() * 10,
        opacity: isBurst ? 1 : 0.85 + Math.random() * 0.15,
        rotation: Math.random() * 360,
        vx: isBurst ? (Math.random() - 0.5) * 5 : (Math.random() - 0.5) * 1,
        vy: isBurst ? (Math.random() - 0.5) * 5 - 1.2 : (Math.random() - 0.5) * 1,
        life: 1,
        decay: isBurst
          ? 0.020 + Math.random() * 0.010
          : 0.024 + Math.random() * 0.018,
        scale: 1,
      };
    },
    []
  );

  /* ── animation loop ── */
  const animate = useCallback(() => {
    starsRef.current = starsRef.current
      .map((s) => ({
        ...s,
        x: s.x + s.vx,
        y: s.y + s.vy,
        vy: s.vy + 0.045,
        vx: s.vx * 0.98,
        life: s.life - s.decay,
        rotation: s.rotation + 3,
        opacity: s.life * s.opacity,
        scale: s.life < 0.35 ? s.life * 2.9 : 1,
      }))
      .filter((s) => s.life > 0);

    burstsRef.current = burstsRef.current
      .map((b) => ({ ...b, progress: b.progress + 0.038 }))
      .filter((b) => b.progress < 1);

    setStars([...starsRef.current]);
    setBursts([...burstsRef.current]);

    rafRef.current = requestAnimationFrame(animate);
  }, []);

  /* ── mount ── */
  useEffect(() => {
    const isTouchDevice =
      "ontouchstart" in window || navigator.maxTouchPoints > 0;
    setIsMobile(isTouchDevice);
    if (isTouchDevice) return;

    rafRef.current = requestAnimationFrame(animate);

    const onMove = (e: MouseEvent) => {
      const x = e.clientX;
      const y = e.clientY;
      setPos({ x, y });
      setHidden(false);
      document.documentElement.style.setProperty("--mouse-x", `${x}px`);
      document.documentElement.style.setProperty("--mouse-y", `${y}px`);

      const dx   = x - lastSpawnPos.current.x;
      const dy   = y - lastSpawnPos.current.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist >= STAR_SPAWN_DIST) {
        lastSpawnPos.current = { x, y };
        const newStar = spawnStar(x, y);
        starsRef.current = [newStar, ...starsRef.current].slice(0, MAX_STARS);
      }
    };

    const onLeave = () => setHidden(true);
    const onEnter = () => setHidden(false);
    const onDown  = () => setClicked(true);
    const onUp    = () => setClicked(false);

    const onClick = (e: MouseEvent) => {
      const burstStars = Array.from({ length: BURST_COUNT }, () =>
        spawnStar(e.clientX, e.clientY, true)
      );
      starsRef.current = [...burstStars, ...starsRef.current].slice(
        0,
        MAX_STARS + BURST_COUNT
      );
      burstsRef.current = [
        ...burstsRef.current,
        { id: nextId(), x: e.clientX, y: e.clientY, progress: 0 },
      ];
    };

    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseleave", onLeave);
    document.addEventListener("mouseenter", onEnter);
    document.addEventListener("mousedown", onDown);
    document.addEventListener("mouseup", onUp);
    document.addEventListener("click", onClick);

    const attachHover = () => {
      document
        .querySelectorAll(
          'a, button, input, textarea, select, label, [role="button"]'
        )
        .forEach((el) => {
          (el as HTMLElement).style.cursor = "none";
          el.addEventListener("mouseenter", () => setLinkHovered(true));
          el.addEventListener("mouseleave", () => setLinkHovered(false));
        });
    };
    const observer = new MutationObserver(attachHover);
    observer.observe(document.body, { childList: true, subtree: true });
    attachHover();

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseleave", onLeave);
      document.removeEventListener("mouseenter", onEnter);
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("mouseup", onUp);
      document.removeEventListener("click", onClick);
      observer.disconnect();
    };
  }, [animate, spawnStar]);

  if (isMobile) return null;

  return (
    <>
      {/* ── Star trail ── */}
      {stars.map((star) => (
        <div
          key={star.id}
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            width: star.size,
            height: star.size,
            transform: `translate3d(${star.x - star.size / 2}px, ${
              star.y - star.size / 2
            }px, 0)`,
            pointerEvents: "none",
            zIndex: 99998,
            willChange: "transform",
          }}
        >
          <SparkStar
            size={star.size}
            opacity={star.opacity}
            rotation={star.rotation}
            scale={star.scale}
            colorIdx={star.colorIdx}
          />
        </div>
      ))}

      {/* ── Click burst rings ── */}
      {bursts.map((burst) => (
        <div
          key={burst.id}
          style={{
            position: "fixed",
            top: burst.y,
            left: burst.x,
            width: 0,
            height: 0,
            pointerEvents: "none",
            zIndex: 99997,
          }}
        >
          {/* Outer gold ring */}
          <div
            style={{
              position: "absolute",
              width: 70 * burst.progress,
              height: 70 * burst.progress,
              borderRadius: "50%",
              border: `2px solid rgba(212,168,67,${1 - burst.progress})`,
              transform: "translate(-50%, -50%)",
              boxShadow: `0 0 ${14 * (1 - burst.progress)}px rgba(212,168,67,${
                0.7 * (1 - burst.progress)
              })`,
            }}
          />
          {/* Inner gold ring */}
          <div
            style={{
              position: "absolute",
              width: 40 * burst.progress,
              height: 40 * burst.progress,
              borderRadius: "50%",
              border: `1.5px solid rgba(240,192,96,${1 - burst.progress})`,
              transform: "translate(-50%, -50%)",
              boxShadow: `0 0 ${12 * (1 - burst.progress)}px rgba(240,192,96,${
                0.6 * (1 - burst.progress)
              })`,
            }}
          />
        </div>
      ))}

      {/* ── Main cursor dot ── */}
      <CursorDot
        x={pos.x}
        y={pos.y}
        clicked={clicked}
        linkHovered={linkHovered}
        hidden={hidden}
      />

      {/* ── Global cursor:none override ── */}
      <style>{`
        *, *::before, *::after { cursor: none !important; }
      `}</style>
    </>
  );
};
