"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Building2,
  ChartColumn,
  CircleCheck,
  FileText,
  GraduationCap,
  Mic,
  Target,
  TrendingUp,
  User,
  Users,
  Workflow,
} from "lucide-react";
import { cn } from "@/lib/utils";

type Audience = "candidates" | "recruiters";

const CONTENT = {
  candidates: {
    eyebrow: "For Candidates",
    title: "Practice like it's real. Get hired when it is.",
    description:
      "Rehearse with an AI interviewer that adapts to your answers, then sit official first rounds on your own schedule — no more waiting weeks for a calendar slot.",
    cta: { href: "/register/candidate", label: "Practice as Candidate" },
    points: [
      { icon: Mic, title: "Unlimited mock interviews", text: "Technical, system design & behavioral — tailored to the role." },
      { icon: TrendingUp, title: "Actionable feedback", text: "Per-answer coaching on clarity, depth and structure." },
      { icon: GraduationCap, title: "Interview on your time", text: "24/7 availability across every time zone." },
      { icon: FileText, title: "One profile, many roles", text: "Upload your resume once and apply in a click." },
    ],
    stat: { value: "3.2x", label: "more likely to pass onsite after 3+ practice sessions" },
  },
  recruiters: {
    eyebrow: "For Recruiting Teams",
    title: "Screen every applicant. Interview only the best.",
    description:
      "Define the role once and let IntraViewer run consistent, bias-aware first rounds at any scale — with structured scorecards your hiring managers actually trust.",
    cta: { href: "/register/company", label: "Start Hiring with AI" },
    points: [
      { icon: Workflow, title: "Automated pipelines", text: "Resume match → AI interview → shortlist, hands-free." },
      { icon: Target, title: "Role-calibrated rubrics", text: "Custom competencies, difficulty and question banks." },
      { icon: ChartColumn, title: "Comparable scorecards", text: "Side-by-side rankings with transcript evidence." },
      { icon: Users, title: "Team collaboration", text: "Share, comment and move candidates in one place." },
    ],
    stat: { value: "10x", label: "faster time-to-shortlist vs. manual phone screens" },
  },
} as const;

export function AudienceTabs() {
  const [tab, setTab] = useState<Audience>("candidates");

  // Allow navbar anchors (#candidates / #recruiters) to select the matching tab.
  useEffect(() => {
    const sync = () => {
      const hash = window.location.hash.replace("#", "");
      if (hash === "candidates" || hash === "recruiters") setTab(hash);
    };
    sync();
    window.addEventListener("hashchange", sync);
    return () => window.removeEventListener("hashchange", sync);
  }, []);

  const data = CONTENT[tab];

  return (
    <div>
      <div className="flex justify-center">
        <div
          role="tablist"
          aria-label="Audience"
          className="relative grid grid-cols-2 rounded-full border border-white/10 bg-white/[0.03] p-1"
        >
          <span
            aria-hidden="true"
            className="absolute inset-y-1 left-1 w-[calc(50%-4px)] rounded-full bg-white transition-transform duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
            style={{ transform: `translateX(${tab === "candidates" ? 0 : 100}%)` }}
          />
          {(
            [
              { id: "candidates", label: "Candidates", icon: User },
              { id: "recruiters", label: "Recruiters", icon: Building2 },
            ] as const
          ).map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              role="tab"
              aria-selected={tab === id}
              onClick={() => setTab(id)}
              className={cn(
                "relative z-10 flex items-center justify-center gap-2 rounded-full px-5 py-2 text-sm font-medium transition-colors sm:px-8",
                tab === id ? "text-zinc-950" : "text-zinc-400 hover:text-white"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </div>
      </div>

      <div
        key={tab}
        role="tabpanel"
        className="mt-12 grid animate-fade-up items-center gap-10 lg:grid-cols-2 lg:gap-16"
      >
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-300">{data.eyebrow}</span>
          <h3 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">{data.title}</h3>
          <p className="mt-4 text-base leading-relaxed text-zinc-400">{data.description}</p>
          <ul className="mt-6 space-y-2.5">
            {data.points.map((p) => (
              <li key={p.title} className="flex items-start gap-2.5 text-sm text-zinc-300">
                <CircleCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                <span>
                  <span className="font-medium text-white">{p.title}</span>
                  <span className="text-zinc-400"> — {p.text}</span>
                </span>
              </li>
            ))}
          </ul>
          <Link
            href={data.cta.href}
            className="group mt-8 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 px-5 py-2.5 text-sm font-medium text-white shadow-[0_8px_30px_-8px_rgba(99,102,241,0.7)] transition-all hover:from-indigo-400 hover:to-violet-400"
          >
            {data.cta.label}
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          {data.points.map(({ icon: Icon, title, text }) => (
            <div
              key={title}
              className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-md transition-colors hover:border-white/20 hover:bg-white/[0.05]"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-500/15 text-indigo-300">
                <Icon className="h-4 w-4" />
              </span>
              <p className="mt-4 text-sm font-medium text-white">{title}</p>
              <p className="mt-1 text-[13px] leading-relaxed text-zinc-400">{text}</p>
            </div>
          ))}
          <div className="rounded-2xl border border-indigo-400/20 bg-gradient-to-br from-indigo-500/15 via-violet-500/10 to-transparent p-5 sm:col-span-2">
            <p className="text-3xl font-semibold tracking-tight text-white">{data.stat.value}</p>
            <p className="mt-1 text-sm text-zinc-400">{data.stat.label}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
