import Link from "next/link";
import { ArrowLeft, ShieldCheck } from "lucide-react";
import { Logo } from "@/components/brand/logo";
import { AuthShowcase } from "@/components/auth/auth-showcase";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="theme-dark relative flex min-h-screen overflow-hidden bg-[#09090b] text-foreground">
      {/* Ambient background */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="bg-grid mask-radial absolute inset-0 opacity-60" />
        <div className="absolute -left-40 -top-40 h-[520px] w-[520px] rounded-full bg-indigo-600/25 blur-[120px]" />
        <div className="absolute bottom-[-200px] left-1/4 h-[420px] w-[420px] rounded-full bg-violet-600/15 blur-[120px]" />
        <div className="absolute -right-32 top-1/3 h-[360px] w-[360px] rounded-full bg-cyan-500/10 blur-[120px]" />
      </div>

      {/* Brand / social-proof panel — desktop only */}
      <aside className="relative hidden w-[46%] flex-col justify-between border-r border-white/[0.06] p-10 lg:flex xl:p-14">
        <Logo />

        <div className="max-w-md space-y-5">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-zinc-300 backdrop-blur-md">
            <span className="h-1.5 w-1.5 animate-glow-pulse rounded-full bg-emerald-400" />
            AI interviewers online 24/7
          </span>
          <h1 className="text-gradient text-4xl font-semibold leading-[1.1] tracking-tight xl:text-[44px]">
            Hire on signal,
            <br /> not on scheduling.
          </h1>
          <p className="text-[15px] leading-relaxed text-zinc-400">
            Autonomous technical &amp; behavioral interviews with real-time voice, live coding and
            proctoring — scored the moment they end.
          </p>
        </div>

        <AuthShowcase />
      </aside>

      {/* Form panel */}
      <main className="relative flex flex-1 flex-col">
        <header className="flex items-center justify-between px-5 py-5 sm:px-8">
          <Logo className="lg:invisible" />
          <Link
            href="/"
            className="group inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs font-medium text-zinc-400 transition-colors hover:border-white/20 hover:text-white"
          >
            <ArrowLeft className="h-3.5 w-3.5 transition-transform group-hover:-translate-x-0.5" />
            Back to home
          </Link>
        </header>

        <div className="flex flex-1 items-center justify-center px-5 pb-10 sm:px-8">
          <div className="w-full max-w-[420px] animate-fade-up">
            <div className="relative rounded-2xl border border-white/10 bg-zinc-950/70 p-6 shadow-[0_0_0_1px_rgba(255,255,255,0.02),0_24px_80px_-20px_rgba(79,70,229,0.35)] backdrop-blur-xl sm:p-8">
              <div
                aria-hidden="true"
                className="absolute inset-x-10 -top-px h-px bg-gradient-to-r from-transparent via-indigo-400/60 to-transparent"
              />
              {children}
            </div>
            <p className="mt-6 flex items-center justify-center gap-1.5 text-xs text-zinc-500">
              <ShieldCheck className="h-3.5 w-3.5" />
              Secured with encrypted sessions
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
