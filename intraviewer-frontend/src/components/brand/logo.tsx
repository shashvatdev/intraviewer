import Link from "next/link";
import { cn } from "@/lib/utils";

export function LogoMark({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "relative inline-flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 via-violet-500 to-cyan-400 shadow-[0_0_20px_-4px_rgba(129,140,248,0.7)]",
        className
      )}
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 text-white">
        <path d="M4 12h2" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M8.5 8v8" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M13 4.5v15" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M17.5 8v8" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
        <path d="M21 11v2" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
      </svg>
    </span>
  );
}

export function Logo({ className, href = "/" }: { className?: string; href?: string }) {
  return (
    <Link
      href={href}
      className={cn("group inline-flex items-center gap-2.5 font-semibold tracking-tight", className)}
      aria-label="IntraViewer home"
    >
      <LogoMark className="transition-transform duration-300 group-hover:scale-105" />
      <span className="text-[15px]">
        Intra<span className="text-indigo-400">Viewer</span>
      </span>
    </Link>
  );
}
