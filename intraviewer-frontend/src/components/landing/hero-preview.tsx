"use client";

import { useEffect, useState } from "react";
import { Bot, Eye, Mic, ScanFace, ShieldCheck, Video } from "lucide-react";
import { cn } from "@/lib/utils";

const QUESTIONS = [
  {
    topic: "System Design",
    text: "Walk me through how you'd design a rate limiter for a public API serving 50k requests per second.",
  },
  {
    topic: "Behavioral",
    text: "Tell me about a time you disagreed with a technical decision. How did you handle it?",
  },
  {
    topic: "Algorithms",
    text: "Given a stream of integers, how would you return the running median in O(log n) per insert?",
  },
];

const TRANSCRIPT = [
  "I'd start with a token bucket per API key…",
  "…backed by Redis with atomic Lua scripts…",
  "…and a sliding-window fallback for bursts.",
];

// Deterministic bar heights so server & client render identically.
const BARS = Array.from({ length: 36 }, (_, i) => Math.round(35 + 65 * Math.abs(Math.sin(i * 1.7))));

function formatTime(total: number) {
  const m = Math.floor(total / 60).toString().padStart(2, "0");
  const s = (total % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

export function HeroPreview() {
  const [seconds, setSeconds] = useState(754);
  const [q, setQ] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setSeconds((s) => s + 1), 1000);
    const r = setInterval(() => setQ((i) => (i + 1) % QUESTIONS.length), 5500);
    return () => {
      clearInterval(t);
      clearInterval(r);
    };
  }, []);

  const scores = [
    { label: "Technical depth", value: 92, color: "from-indigo-400 to-violet-400" },
    { label: "Communication", value: 88, color: "from-cyan-400 to-emerald-400" },
    { label: "Problem solving", value: 95, color: "from-violet-400 to-fuchsia-400" },
  ];

  return (
    <div className="relative">
      {/* Glow */}
      <div
        aria-hidden="true"
        className="absolute -inset-x-6 -inset-y-10 rounded-[40px] bg-gradient-to-r from-indigo-600/30 via-violet-600/20 to-cyan-500/20 blur-3xl"
      />

      <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-zinc-950/80 shadow-2xl shadow-indigo-950/40 backdrop-blur-xl">
        {/* Window chrome */}
        <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-3">
          <div className="flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
            <span className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
            <span className="h-2.5 w-2.5 rounded-full bg-zinc-700" />
          </div>
          <div className="flex items-center gap-2 text-[11px] font-medium text-zinc-400">
            <span className="flex items-center gap-1.5 rounded-full bg-red-500/10 px-2 py-0.5 text-red-400">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-red-500" />
              LIVE
            </span>
            <span className="tabular-nums">{formatTime(seconds)}</span>
          </div>
          <span className="hidden text-[11px] text-zinc-500 sm:block">Senior Backend Engineer · Round 1</span>
        </div>

        <div className="grid gap-px bg-white/[0.04] md:grid-cols-[1.35fr_1fr]">
          {/* Main stage */}
          <div className="space-y-4 bg-zinc-950 p-4 sm:p-5">
            <div className="grid grid-cols-2 gap-3">
              {/* AI interviewer tile */}
              <div className="relative flex aspect-[4/3] flex-col items-center justify-center overflow-hidden rounded-xl border border-indigo-400/20 bg-gradient-to-br from-indigo-950/80 to-zinc-950">
                <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(99,102,241,0.35),transparent_60%)]" />
                <div className="relative flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 shadow-[0_0_30px_rgba(129,140,248,0.6)]">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <span className="absolute bottom-2 left-2 rounded-md bg-black/50 px-1.5 py-0.5 text-[10px] text-zinc-300 backdrop-blur">
                  Aria · AI Interviewer
                </span>
              </div>
              {/* Candidate tile */}
              <div className="relative flex aspect-[4/3] items-center justify-center overflow-hidden rounded-xl border border-white/10 bg-gradient-to-br from-zinc-800 to-zinc-900">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-zinc-700 text-sm font-semibold text-zinc-200">
                  JD
                </div>
                <span className="absolute bottom-2 left-2 flex items-center gap-1 rounded-md bg-black/50 px-1.5 py-0.5 text-[10px] text-zinc-300 backdrop-blur">
                  <Mic className="h-2.5 w-2.5 text-emerald-400" /> You
                </span>
                <span className="absolute right-2 top-2 flex items-center gap-1 rounded-md bg-emerald-500/15 px-1.5 py-0.5 text-[10px] text-emerald-300">
                  <ScanFace className="h-2.5 w-2.5" /> Verified
                </span>
              </div>
            </div>

            {/* Question */}
            <div className="relative min-h-[92px] rounded-xl border border-white/[0.08] bg-white/[0.02] p-4">
              {QUESTIONS.map((item, i) => (
                <div
                  key={item.topic}
                  aria-hidden={i !== q}
                  className={cn(
                    "absolute inset-4 transition-all duration-500",
                    i === q ? "translate-y-0 opacity-100" : "translate-y-1 opacity-0"
                  )}
                >
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-indigo-300">
                    {item.topic}
                  </span>
                  <p className="mt-1.5 text-[13px] leading-relaxed text-zinc-200">{item.text}</p>
                </div>
              ))}
            </div>

            {/* Waveform */}
            <div className="flex items-center gap-3 rounded-xl border border-white/[0.08] bg-white/[0.02] px-4 py-3">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-500/15">
                <Mic className="h-3.5 w-3.5 text-emerald-400" />
              </span>
              <div className="flex h-8 flex-1 items-center gap-[3px]" aria-hidden="true">
                {BARS.map((h, i) => (
                  <span
                    key={i}
                    className="w-full origin-center animate-wave rounded-full bg-gradient-to-t from-indigo-500 to-cyan-300"
                    style={{ height: `${h}%`, animationDelay: `${(i % 12) * 0.08}s` }}
                  />
                ))}
              </div>
              <span className="hidden text-[11px] tabular-nums text-zinc-500 sm:block">~180ms</span>
            </div>
          </div>

          {/* Side panel */}
          <div className="hidden space-y-4 bg-zinc-950 p-5 md:block">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Live transcript</p>
              <div className="mt-2 space-y-1.5">
                {TRANSCRIPT.map((line, i) => (
                  <p
                    key={line}
                    className="animate-fade-up text-[12px] leading-relaxed text-zinc-400"
                    style={{ animationDelay: `${0.4 + i * 0.5}s` }}
                  >
                    {line}
                  </p>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Real-time signals</p>
              {scores.map((s) => (
                <div key={s.label}>
                  <div className="flex justify-between text-[11px]">
                    <span className="text-zinc-400">{s.label}</span>
                    <span className="tabular-nums text-zinc-200">{s.value}</span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                    <div className={`h-full rounded-full bg-gradient-to-r ${s.color}`} style={{ width: `${s.value}%` }} />
                  </div>
                </div>
              ))}
            </div>

            <div className="space-y-2">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Proctoring</p>
              <div className="flex flex-wrap gap-1.5">
                {[
                  { icon: Eye, label: "Gaze OK" },
                  { icon: ShieldCheck, label: "No tab switch" },
                  { icon: Video, label: "1 face" },
                ].map(({ icon: Icon, label }) => (
                  <span
                    key={label}
                    className="inline-flex items-center gap-1 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2 py-0.5 text-[10px] text-emerald-300"
                  >
                    <Icon className="h-2.5 w-2.5" />
                    {label}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating badges */}
      <div className="absolute -left-4 top-1/3 hidden animate-float rounded-xl border border-white/10 bg-zinc-900/80 px-3 py-2 shadow-xl backdrop-blur-md lg:block">
        <p className="text-[10px] text-zinc-500">Integrity score</p>
        <p className="text-sm font-semibold text-emerald-300">99.2%</p>
      </div>
      <div
        className="absolute -right-4 bottom-10 hidden animate-float rounded-xl border border-white/10 bg-zinc-900/80 px-3 py-2 shadow-xl backdrop-blur-md lg:block"
        style={{ animationDelay: "1.5s" }}
      >
        <p className="text-[10px] text-zinc-500">Scorecard ready in</p>
        <p className="text-sm font-semibold text-indigo-300">42 seconds</p>
      </div>
    </div>
  );
}
