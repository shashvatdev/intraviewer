"use client";

import { useEffect, useState } from "react";
import { Quote } from "lucide-react";
import { cn } from "@/lib/utils";

const TESTIMONIALS = [
  {
    quote:
      "IntraViewer replaced our entire first-round loop. We screen 10x more applicants and our engineers finally got their calendars back.",
    name: "Sarah Jenkins",
    title: "VP of Engineering, Northwind",
    initials: "SJ",
  },
  {
    quote:
      "The scorecards are uncannily close to what our senior interviewers would write — and they arrive minutes after the session ends.",
    name: "Marcus Chen",
    title: "Head of Talent, Lumen Labs",
    initials: "MC",
  },
  {
    quote:
      "I practiced three mock interviews the night before my onsite. The feedback on my system-design answers was the reason I got the offer.",
    name: "Priya Raman",
    title: "Software Engineer, hired via IntraViewer",
    initials: "PR",
  },
];

const METRICS = [
  { value: "10k+", label: "Interviews run" },
  { value: "80%", label: "Time saved" },
  { value: "94%", label: "Candidate CSAT" },
];

export function AuthShowcase() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setIndex((i) => (i + 1) % TESTIMONIALS.length), 6000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-3">
        {METRICS.map((m) => (
          <div
            key={m.label}
            className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 backdrop-blur-md"
          >
            <p className="text-xl font-semibold tracking-tight text-white">{m.value}</p>
            <p className="mt-0.5 text-xs text-zinc-400">{m.label}</p>
          </div>
        ))}
      </div>

      <figure className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur-md">
        <Quote className="absolute right-5 top-5 h-8 w-8 text-white/5" aria-hidden="true" />
        <div className="relative min-h-[96px]">
          {TESTIMONIALS.map((t, i) => (
            <blockquote
              key={t.name}
              aria-hidden={i !== index}
              className={cn(
                "absolute inset-0 text-[15px] leading-relaxed text-zinc-300 transition-all duration-700",
                i === index ? "translate-y-0 opacity-100" : "pointer-events-none translate-y-2 opacity-0"
              )}
            >
              &ldquo;{t.quote}&rdquo;
            </blockquote>
          ))}
        </div>
        <figcaption className="mt-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 text-xs font-semibold text-white">
              {TESTIMONIALS[index].initials}
            </div>
            <div>
              <p className="text-sm font-medium text-white">{TESTIMONIALS[index].name}</p>
              <p className="text-xs text-zinc-500">{TESTIMONIALS[index].title}</p>
            </div>
          </div>
          <div className="flex gap-1.5" role="tablist" aria-label="Testimonials">
            {TESTIMONIALS.map((t, i) => (
              <button
                key={t.name}
                type="button"
                role="tab"
                aria-selected={i === index}
                aria-label={`Show testimonial ${i + 1}`}
                onClick={() => setIndex(i)}
                className={cn(
                  "h-1.5 rounded-full transition-all duration-300",
                  i === index ? "w-5 bg-indigo-400" : "w-1.5 bg-white/20 hover:bg-white/40"
                )}
              />
            ))}
          </div>
        </figcaption>
      </figure>
    </div>
  );
}
