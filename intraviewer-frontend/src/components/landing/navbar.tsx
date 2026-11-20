"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Menu, X } from "lucide-react";
import { Logo } from "@/components/brand/logo";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { href: "#features", label: "Features" },
  { href: "#how-it-works", label: "How It Works" },
  { href: "#candidates", label: "For Candidates" },
  { href: "#recruiters", label: "For Recruiters" },
  { href: "#pricing", label: "Pricing" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 w-full border-b transition-all duration-300",
        scrolled || open
          ? "border-white/[0.08] bg-[#09090b]/75 backdrop-blur-xl"
          : "border-transparent bg-transparent"
      )}
    >
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-8">
        <Logo />

        <ul className="hidden items-center gap-1 lg:flex">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="rounded-full px-3.5 py-2 text-sm text-zinc-400 transition-colors hover:bg-white/[0.04] hover:text-white"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <div className="hidden items-center gap-2 lg:flex">
          <Link
            href="/login"
            className="rounded-full px-4 py-2 text-sm font-medium text-zinc-300 transition-colors hover:text-white"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="group inline-flex items-center gap-1.5 rounded-full bg-white px-4 py-2 text-sm font-medium text-zinc-950 shadow-[0_0_20px_-6px_rgba(255,255,255,0.6)] transition-all hover:bg-zinc-200"
          >
            Get Started Free
            <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>

        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 text-zinc-300 lg:hidden"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
        >
          {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </button>
      </nav>

      {/* Mobile menu */}
      <div
        className={cn(
          "overflow-hidden border-t border-white/[0.06] transition-[max-height,opacity] duration-300 lg:hidden",
          open ? "max-h-[calc(100vh-4rem)] opacity-100" : "max-h-0 border-transparent opacity-0"
        )}
      >
        <div className="space-y-1 px-5 py-4 sm:px-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className="block rounded-lg px-3 py-2.5 text-sm text-zinc-300 hover:bg-white/[0.04] hover:text-white"
            >
              {link.label}
            </a>
          ))}
          <div className="grid grid-cols-2 gap-2 pt-3">
            <Link
              href="/login"
              className="rounded-full border border-white/10 py-2.5 text-center text-sm font-medium text-zinc-200"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="rounded-full bg-white py-2.5 text-center text-sm font-medium text-zinc-950"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
