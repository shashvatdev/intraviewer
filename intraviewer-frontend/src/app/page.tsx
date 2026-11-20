import type { Metadata } from "next";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  AudioLines,
  Bot,
  Briefcase,
  Building2,
  ChartColumn,
  Check,
  Code,
  Cpu,
  Eye,
  FileText,
  Play,
  ScanFace,
  ShieldCheck,
  Sparkles,
  User,
  Video,
  Zap,
} from "lucide-react";
import { Navbar } from "@/components/landing/navbar";
import { HeroPreview } from "@/components/landing/hero-preview";
import { AudienceTabs } from "@/components/landing/audience-tabs";
import { Logo } from "@/components/brand/logo";

export const metadata: Metadata = {
  title: "IntraViewer — AI-Powered Autonomous Technical & Behavioral Interviews",
  description:
    "Automate first-round interviews with human-like AI. Real-time voice & video, live coding with proctoring, and instant scorecards for recruiters and candidates.",
};

const METRICS = [
  { value: "10k+", label: "Interviews conducted" },
  { value: "94%", label: "Candidate satisfaction" },
  { value: "80%", label: "Recruiter time saved" },
  { value: "<200ms", label: "Voice response latency" },
];

const COMPANIES = ["Northwind", "Lumen Labs", "Acme Cloud", "Vertex AI", "Helios", "Quantia"];

const STEPS = [
  {
    icon: Briefcase,
    title: "Define the role",
    text: "Paste a job description. IntraViewer generates a calibrated rubric and question plan in seconds.",
  },
  {
    icon: FileText,
    title: "Match & invite",
    text: "Resumes are scored against the role and top matches are invited to interview automatically.",
  },
  {
    icon: Bot,
    title: "AI runs the interview",
    text: "A conversational AI interviewer conducts live voice/video rounds with adaptive follow-ups and proctoring.",
  },
  {
    icon: ChartColumn,
    title: "Review scorecards",
    text: "Get ranked, evidence-backed scorecards with transcripts and integrity reports the moment it ends.",
  },
];

const PLANS = [
  {
    name: "Candidate",
    price: "Free",
    period: "forever",
    description: "Everything you need to practice and get hired.",
    features: ["Unlimited mock interviews", "AI feedback on every answer", "Apply to open roles", "Interview 24/7"],
    cta: { href: "/register/candidate", label: "Start practicing" },
    highlighted: false,
  },
  {
    name: "Growth",
    price: "$199",
    period: "/ month",
    description: "For startups scaling their engineering hiring.",
    features: [
      "100 AI interviews / month",
      "Custom rubrics & question banks",
      "Live code proctoring & anti-cheat",
      "Ranked scorecards & transcripts",
      "Up to 5 recruiter seats",
    ],
    cta: { href: "/register/company", label: "Start free trial" },
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "High-volume hiring with advanced controls.",
    features: ["Unlimited interviews", "SSO & role-based access", "ATS integrations", "Dedicated success manager"],
    cta: { href: "/register/company", label: "Contact sales" },
    highlighted: false,
  },
];

function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: React.ReactNode;
  description?: string;
}) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      <span className="inline-flex items-center rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs font-medium text-zinc-300">
        {eyebrow}
      </span>
      <h2 className="text-gradient mt-4 text-3xl font-semibold tracking-tight sm:text-[42px] sm:leading-[1.1]">
        {title}
      </h2>
      {description && <p className="mt-4 text-base leading-relaxed text-zinc-400">{description}</p>}
    </div>
  );
}

export default function Home() {
  return (
    <div className="min-h-screen overflow-x-hidden bg-[#09090b] text-zinc-100 selection:bg-indigo-500/30">
      <Navbar />

      <main>
        {/* ───────────── Hero ───────────── */}
        <section className="relative -mt-16 pt-16">
          <div aria-hidden="true" className="pointer-events-none absolute inset-0">
            <div className="bg-grid mask-fade-b absolute inset-0" />
            <div className="absolute left-1/2 top-0 h-[600px] w-[1000px] -translate-x-1/2 rounded-full bg-[radial-gradient(ellipse_at_center,rgba(99,102,241,0.25),transparent_65%)]" />
            <div className="absolute right-[-10%] top-[30%] h-[400px] w-[400px] rounded-full bg-cyan-500/10 blur-[120px]" />
          </div>

          <div className="relative mx-auto max-w-7xl px-5 pb-20 pt-16 sm:px-8 sm:pt-24 lg:pb-28">
            <div className="mx-auto max-w-3xl text-center">
              <Link
                href="/register"
                className="group inline-flex animate-fade-up items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] py-1 pl-1 pr-3 text-xs text-zinc-300 backdrop-blur-md transition-colors hover:border-indigo-400/40"
              >
                <span className="rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 px-2 py-0.5 text-[11px] font-medium text-white">
                  New
                </span>
                ✨ IntraViewer 2.0 — Next-Gen AI Video Interviews
                <ArrowRight className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
              </Link>

              <h1
                className="mt-6 animate-fade-up text-4xl font-semibold leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl"
                style={{ animationDelay: "80ms" }}
              >
                <span className="text-gradient">Automate first-round interviews with </span>
                <span className="text-gradient-brand">human-like AI precision</span>
              </h1>

              <p
                className="mx-auto mt-6 max-w-2xl animate-fade-up text-base leading-relaxed text-zinc-400 sm:text-lg"
                style={{ animationDelay: "160ms" }}
              >
                Companies screen <span className="text-zinc-200">10x faster</span> with autonomous technical
                &amp; behavioral interviews. Candidates <span className="text-zinc-200">practice and get vetted</span>{" "}
                on their own schedule — with instant, structured feedback.
              </p>

              <div
                className="mt-9 flex animate-fade-up flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center"
                style={{ animationDelay: "240ms" }}
              >
                <Link
                  href="/register/company"
                  className="group inline-flex items-center justify-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-medium text-zinc-950 shadow-[0_0_30px_-8px_rgba(255,255,255,0.6)] transition-all hover:bg-zinc-200"
                >
                  <Building2 className="h-4 w-4" />
                  Start Hiring with AI
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Link>
                <Link
                  href="/register/candidate"
                  className="inline-flex items-center justify-center gap-2 rounded-full border border-white/15 bg-white/[0.03] px-6 py-3 text-sm font-medium text-white backdrop-blur-md transition-all hover:border-white/30 hover:bg-white/[0.06]"
                >
                  <User className="h-4 w-4" />
                  Practice as Candidate
                </Link>
                <a
                  href="#demo"
                  className="group inline-flex items-center justify-center gap-2 rounded-full px-4 py-3 text-sm font-medium text-zinc-300 transition-colors hover:text-white"
                >
                  <span className="flex h-6 w-6 items-center justify-center rounded-full border border-white/15 bg-white/5 transition-colors group-hover:border-indigo-400/50">
                    <Play className="h-3 w-3 fill-current" />
                  </span>
                  Live Demo
                </a>
              </div>

              <p
                className="mt-6 inline-flex animate-fade-up items-center gap-1.5 rounded-full border border-amber-400/20 bg-amber-400/[0.06] px-3 py-1 text-xs text-amber-200/90"
                style={{ animationDelay: "320ms" }}
              >
                <Zap className="h-3 w-3 fill-current" />
                Powered by Groq &amp; Real-time WebRTC
              </p>
            </div>

            <div id="demo" className="mx-auto mt-16 max-w-5xl scroll-mt-24 animate-fade-up sm:mt-20" style={{ animationDelay: "400ms" }}>
              <HeroPreview />
            </div>
          </div>
        </section>

        {/* ───────────── Metrics / social proof ───────────── */}
        <section className="border-y border-white/[0.06] bg-white/[0.015]">
          <div className="mx-auto max-w-7xl px-5 py-12 sm:px-8">
            <dl className="grid grid-cols-2 gap-y-8 lg:grid-cols-4">
              {METRICS.map((m, i) => (
                <div
                  key={m.label}
                  className={`text-center ${i > 0 ? "lg:border-l lg:border-white/[0.06]" : ""} ${i % 2 === 1 ? "border-l border-white/[0.06] lg:border-l" : ""}`}
                >
                  <dt className="sr-only">{m.label}</dt>
                  <dd className="text-gradient text-3xl font-semibold tracking-tight sm:text-4xl">{m.value}</dd>
                  <p className="mt-1 text-sm text-zinc-500">{m.label}</p>
                </div>
              ))}
            </dl>
            <div className="mt-10 flex flex-wrap items-center justify-center gap-x-10 gap-y-4">
              <span className="w-full text-center text-xs uppercase tracking-wider text-zinc-600 sm:w-auto">
                Trusted by hiring teams at
              </span>
              {COMPANIES.map((c) => (
                <span key={c} className="text-sm font-semibold tracking-tight text-zinc-500 transition-colors hover:text-zinc-300">
                  {c}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* ───────────── Features (bento) ───────────── */}
        <section id="features" className="relative scroll-mt-20 py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-5 sm:px-8">
            <SectionHeading
              eyebrow="Features"
              title="Everything a great interviewer does — at infinite scale"
              description="One platform for conversational AI interviews, live technical assessment, integrity monitoring and decision-ready analytics."
            />

            <div className="mt-16 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Voice & video — wide */}
              <article className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] p-7 backdrop-blur-md transition-colors hover:border-white/20 lg:col-span-2">
                <div aria-hidden="true" className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-indigo-500/20 blur-3xl" />
                <div className="relative flex h-full flex-col gap-8 sm:flex-row sm:items-end">
                  <div className="flex-1">
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-300">
                      <AudioLines className="h-5 w-5" />
                    </span>
                    <h3 className="mt-5 text-xl font-semibold tracking-tight text-white">
                      Real-time conversational voice &amp; video
                    </h3>
                    <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                      Natural, low-latency dialogue over WebRTC. The AI listens, interrupts politely, and asks adaptive
                      follow-ups exactly like a senior interviewer would.
                    </p>
                  </div>
                  <div className="w-full space-y-2 sm:w-64">
                    {[
                      { who: "AI", text: "Why a token bucket over a fixed window?", ai: true },
                      { who: "You", text: "It smooths bursts while keeping the average rate…", ai: false },
                      { who: "AI", text: "Great — how would you shard it across regions?", ai: true },
                    ].map((m, i) => (
                      <div
                        key={i}
                        className={`rounded-xl px-3 py-2 text-xs ${m.ai ? "mr-6 border border-indigo-400/20 bg-indigo-500/10 text-indigo-100" : "ml-6 border border-white/10 bg-white/[0.04] text-zinc-300"}`}
                      >
                        <span className="mb-0.5 block text-[10px] font-semibold uppercase tracking-wider opacity-60">{m.who}</span>
                        {m.text}
                      </div>
                    ))}
                  </div>
                </div>
              </article>

              {/* Proctoring — tall */}
              <article className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] p-7 backdrop-blur-md transition-colors hover:border-white/20 lg:row-span-2">
                <div aria-hidden="true" className="absolute -bottom-24 -left-10 h-64 w-64 rounded-full bg-emerald-500/15 blur-3xl" />
                <div className="relative flex h-full flex-col">
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/15 text-emerald-300">
                    <Code className="h-5 w-5" />
                  </span>
                  <h3 className="mt-5 text-xl font-semibold tracking-tight text-white">
                    Live code &amp; technical proctoring
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                    Built-in coding environment with anti-cheat detection: tab switches, copy-paste bursts, multiple faces
                    and gaze tracking — all flagged in real time.
                  </p>
                  <div className="mt-6 flex-1 overflow-hidden rounded-xl border border-white/10 bg-zinc-950/80 font-mono text-[11.5px] leading-relaxed">
                    <div className="flex items-center gap-1.5 border-b border-white/[0.06] px-3 py-2 text-[10px] text-zinc-500">
                      <span className="h-2 w-2 rounded-full bg-zinc-700" />
                      solution.py
                    </div>
                    <pre className="overflow-x-auto px-3 py-3 text-zinc-400">
                      <code>
                        <span className="text-violet-300">def</span> <span className="text-cyan-300">median</span>(stream):{"\n"}
                        {"  "}lo, hi = [], []{"\n"}
                        {"  "}<span className="text-violet-300">for</span> x <span className="text-violet-300">in</span> stream:{"\n"}
                        {"    "}heappush(lo, -x){"\n"}
                        {"    "}heappush(hi, -heappop(lo)){"\n"}
                        {"    "}<span className="text-zinc-600"># rebalance…</span>
                      </code>
                    </pre>
                  </div>
                  <div className="mt-4 space-y-2">
                    {[
                      { icon: Eye, label: "Gaze tracking", status: "Normal" },
                      { icon: ScanFace, label: "Face presence", status: "1 detected" },
                      { icon: ShieldCheck, label: "Tab focus", status: "Locked" },
                    ].map(({ icon: Icon, label, status }) => (
                      <div key={label} className="flex items-center justify-between rounded-lg border border-white/[0.06] bg-white/[0.02] px-3 py-2 text-xs">
                        <span className="flex items-center gap-2 text-zinc-300">
                          <Icon className="h-3.5 w-3.5 text-emerald-400" />
                          {label}
                        </span>
                        <span className="text-emerald-300">{status}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </article>

              {/* Scorecards */}
              <article className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] p-7 backdrop-blur-md transition-colors hover:border-white/20">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-violet-500/15 text-violet-300">
                  <Activity className="h-5 w-5" />
                </span>
                <h3 className="mt-5 text-xl font-semibold tracking-tight text-white">Instant scorecards &amp; analytics</h3>
                <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                  Competency scores, behavioral signals and transcript evidence — ready seconds after the call.
                </p>
                <div className="mt-6 flex h-20 items-end gap-2" aria-hidden="true">
                  {[48, 72, 60, 88, 66, 94, 80].map((h, i) => (
                    <span
                      key={i}
                      className="flex-1 rounded-t-md bg-gradient-to-t from-violet-500/30 to-violet-400 transition-all duration-500 group-hover:opacity-100"
                      style={{ height: `${h}%`, opacity: 0.55 + i * 0.06 }}
                    />
                  ))}
                </div>
              </article>

              {/* Dual portals */}
              <article className="group relative overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] p-7 backdrop-blur-md transition-colors hover:border-white/20">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-300">
                  <Cpu className="h-5 w-5" />
                </span>
                <h3 className="mt-5 text-xl font-semibold tracking-tight text-white">Dual portals, one platform</h3>
                <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                  Purpose-built workspaces for recruiters and candidates, with role-based access baked in.
                </p>
                <div className="mt-6 grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                    <Building2 className="h-4 w-4 text-cyan-300" />
                    <p className="mt-2 font-medium text-white">Recruiter</p>
                    <p className="text-zinc-500">Jobs · Pipelines</p>
                  </div>
                  <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
                    <User className="h-4 w-4 text-indigo-300" />
                    <p className="mt-2 font-medium text-white">Candidate</p>
                    <p className="text-zinc-500">Practice · Apply</p>
                  </div>
                </div>
              </article>
            </div>

            {/* Mini feature strip */}
            <div className="mt-4 grid gap-4 sm:grid-cols-3">
              {[
                { icon: Video, title: "HD recordings", text: "Replay any answer with synced transcript." },
                { icon: Sparkles, title: "Adaptive difficulty", text: "Questions scale with candidate performance." },
                { icon: ShieldCheck, title: "Bias-aware scoring", text: "Structured rubrics for consistent decisions." },
              ].map(({ icon: Icon, title, text }) => (
                <div key={title} className="flex items-start gap-3 rounded-2xl border border-white/[0.06] bg-white/[0.02] p-5">
                  <Icon className="mt-0.5 h-4 w-4 shrink-0 text-zinc-400" />
                  <div>
                    <p className="text-sm font-medium text-white">{title}</p>
                    <p className="mt-0.5 text-[13px] text-zinc-500">{text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ───────────── How it works ───────────── */}
        <section id="how-it-works" className="relative scroll-mt-20 border-t border-white/[0.06] py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-5 sm:px-8">
            <SectionHeading
              eyebrow="How It Works"
              title="From job post to shortlist in four steps"
              description="Set it up in minutes. IntraViewer handles the repetitive first round so your team can focus on final decisions."
            />
            <div className="relative mt-16">
              <div
                aria-hidden="true"
                className="absolute left-0 right-0 top-[38px] hidden h-px bg-gradient-to-r from-transparent via-indigo-400/30 to-transparent lg:block"
              />
            <ol className="relative grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {STEPS.map(({ icon: Icon, title, text }, i) => (
                <li
                  key={title}
                  className="relative rounded-2xl border border-white/10 bg-[#0c0c0f] p-6 transition-colors hover:border-indigo-400/30"
                >
                  <div className="flex items-center justify-between">
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-white/10 bg-gradient-to-br from-indigo-500/20 to-violet-500/10 text-indigo-200">
                      <Icon className="h-5 w-5" />
                    </span>
                    <span className="font-mono text-xs text-zinc-600">0{i + 1}</span>
                  </div>
                  <h3 className="mt-5 text-base font-semibold text-white">{title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-zinc-400">{text}</p>
                </li>
              ))}
            </ol>
            </div>
          </div>
        </section>

        {/* ───────────── Audience ───────────── */}
        <section className="relative scroll-mt-20 border-t border-white/[0.06] py-24 sm:py-32">
          <span id="candidates" className="absolute -top-20" aria-hidden="true" />
          <span id="recruiters" className="absolute -top-20" aria-hidden="true" />
          <div aria-hidden="true" className="pointer-events-none absolute left-1/2 top-1/3 h-[400px] w-[700px] -translate-x-1/2 rounded-full bg-indigo-600/10 blur-[120px]" />
          <div className="relative mx-auto max-w-7xl px-5 sm:px-8">
            <SectionHeading
              eyebrow="Built for both sides of the table"
              title="A better interview for everyone"
            />
            <div className="mt-10">
              <AudienceTabs />
            </div>
          </div>
        </section>

        {/* ───────────── Pricing ───────────── */}
        <section id="pricing" className="relative scroll-mt-20 border-t border-white/[0.06] py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-5 sm:px-8">
            <SectionHeading
              eyebrow="Pricing"
              title="Simple, transparent pricing"
              description="Free for candidates. Flexible plans for teams of every size."
            />
            <div className="mx-auto mt-16 grid max-w-5xl gap-4 lg:grid-cols-3">
              {PLANS.map((plan) => (
                <div
                  key={plan.name}
                  className={`relative flex flex-col rounded-3xl p-7 ${
                    plan.highlighted
                      ? "border border-indigo-400/40 bg-gradient-to-b from-indigo-500/[0.12] to-white/[0.02] shadow-[0_0_60px_-20px_rgba(99,102,241,0.6)]"
                      : "border border-white/10 bg-white/[0.02]"
                  }`}
                >
                  {plan.highlighted && (
                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 px-3 py-1 text-[11px] font-medium text-white">
                      Most popular
                    </span>
                  )}
                  <h3 className="text-sm font-medium text-zinc-300">{plan.name}</h3>
                  <p className="mt-3 flex items-baseline gap-1.5">
                    <span className="text-4xl font-semibold tracking-tight text-white">{plan.price}</span>
                    {plan.period && <span className="text-sm text-zinc-500">{plan.period}</span>}
                  </p>
                  <p className="mt-2 text-sm text-zinc-400">{plan.description}</p>
                  <ul className="mt-6 flex-1 space-y-2.5">
                    {plan.features.map((f) => (
                      <li key={f} className="flex items-start gap-2.5 text-sm text-zinc-300">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-indigo-300" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <Link
                    href={plan.cta.href}
                    className={`mt-8 inline-flex items-center justify-center rounded-full py-2.5 text-sm font-medium transition-all ${
                      plan.highlighted
                        ? "bg-white text-zinc-950 hover:bg-zinc-200"
                        : "border border-white/15 text-white hover:border-white/30 hover:bg-white/[0.04]"
                    }`}
                  >
                    {plan.cta.label}
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ───────────── CTA banner ───────────── */}
        <section className="px-5 pb-24 sm:px-8">
          <div className="relative mx-auto max-w-6xl overflow-hidden rounded-[28px] border border-white/10 bg-gradient-to-br from-indigo-600/30 via-violet-600/20 to-cyan-500/10 px-6 py-16 text-center sm:px-12 sm:py-20">
            <div aria-hidden="true" className="bg-grid mask-radial absolute inset-0 opacity-70" />
            <div aria-hidden="true" className="absolute left-1/2 top-0 h-px w-2/3 -translate-x-1/2 bg-gradient-to-r from-transparent via-white/50 to-transparent" />
            <div className="relative">
              <h2 className="text-gradient mx-auto max-w-2xl text-3xl font-semibold tracking-tight sm:text-5xl">
                Your next great hire is one interview away
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-base text-zinc-300">
                Join thousands of teams and candidates using IntraViewer to make interviewing faster, fairer and
                far less painful.
              </p>
              <div className="mt-8 flex flex-col items-stretch justify-center gap-3 sm:flex-row sm:items-center">
                <Link
                  href="/register"
                  className="group inline-flex items-center justify-center gap-2 rounded-full bg-white px-6 py-3 text-sm font-medium text-zinc-950 transition-all hover:bg-zinc-200"
                >
                  Get Started Free
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </Link>
                <Link
                  href="/login"
                  className="inline-flex items-center justify-center rounded-full border border-white/20 bg-white/5 px-6 py-3 text-sm font-medium text-white backdrop-blur-md transition-all hover:bg-white/10"
                >
                  Sign In
                </Link>
              </div>
              <p className="mt-5 text-xs text-zinc-400">No credit card required · Free forever for candidates</p>
            </div>
          </div>
        </section>
      </main>

      {/* ───────────── Footer ───────────── */}
      <footer className="border-t border-white/[0.06]">
        <div className="mx-auto max-w-7xl px-5 py-14 sm:px-8">
          <div className="grid gap-10 md:grid-cols-[1.5fr_1fr_1fr_1fr]">
            <div>
              <Logo />
              <p className="mt-4 max-w-xs text-sm leading-relaxed text-zinc-500">
                The AI-powered autonomous technical &amp; behavioral interview platform.
              </p>
              <span className="mt-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.02] px-3 py-1.5 text-xs text-zinc-400">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
                </span>
                All systems operational
              </span>
            </div>
            {[
              {
                title: "Product",
                links: [
                  { href: "#features", label: "Features" },
                  { href: "#how-it-works", label: "How It Works" },
                  { href: "#pricing", label: "Pricing" },
                  { href: "#demo", label: "Live Demo" },
                ],
              },
              {
                title: "Solutions",
                links: [
                  { href: "#candidates", label: "For Candidates" },
                  { href: "#recruiters", label: "For Recruiters" },
                  { href: "/register/company", label: "Start Hiring" },
                  { href: "/register/candidate", label: "Practice Interviews" },
                ],
              },
              {
                title: "Account",
                links: [
                  { href: "/login", label: "Sign In" },
                  { href: "/register", label: "Create Account" },
                  { href: "/forgot-password", label: "Reset Password" },
                ],
              },
            ].map((col) => (
              <div key={col.title}>
                <p className="text-sm font-medium text-white">{col.title}</p>
                <ul className="mt-4 space-y-2.5">
                  {col.links.map((l) => (
                    <li key={l.label}>
                      {l.href.startsWith("#") ? (
                        <a href={l.href} className="text-sm text-zinc-500 transition-colors hover:text-zinc-200">
                          {l.label}
                        </a>
                      ) : (
                        <Link href={l.href} className="text-sm text-zinc-500 transition-colors hover:text-zinc-200">
                          {l.label}
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-white/[0.06] pt-6 text-xs text-zinc-600 sm:flex-row">
            <p>© {new Date().getFullYear()} IntraViewer. All rights reserved.</p>
            <p className="flex items-center gap-1.5">
              <Zap className="h-3 w-3" /> Powered by Groq &amp; Real-time WebRTC
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
