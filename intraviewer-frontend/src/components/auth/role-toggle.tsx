"use client";

import { User, Building2 } from "lucide-react";
import { cn } from "@/lib/utils";

export type Role = "CANDIDATE" | "COMPANY";

const OPTIONS: { value: Role; label: string; icon: typeof User }[] = [
  { value: "CANDIDATE", label: "Candidate", icon: User },
  { value: "COMPANY", label: "Company", icon: Building2 },
];

interface RoleToggleProps {
  value: Role;
  onChange: (role: Role) => void;
  className?: string;
}

/** Animated segmented pill for switching between Candidate and Company. */
export function RoleToggle({ value, onChange, className }: RoleToggleProps) {
  const activeIndex = OPTIONS.findIndex((o) => o.value === value);

  return (
    <div
      role="radiogroup"
      aria-label="Account type"
      className={cn(
        "relative grid grid-cols-2 rounded-full border border-white/10 bg-white/[0.03] p-1",
        className
      )}
    >
      <span
        aria-hidden="true"
        className="absolute inset-y-1 left-1 w-[calc(50%-4px)] rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 shadow-[0_4px_20px_-4px_rgba(99,102,241,0.6)] transition-transform duration-300 ease-[cubic-bezier(0.32,0.72,0,1)]"
        style={{ transform: `translateX(${activeIndex * 100}%)` }}
      />
      {OPTIONS.map(({ value: optionValue, label, icon: Icon }) => {
        const active = optionValue === value;
        return (
          <button
            key={optionValue}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(optionValue)}
            className={cn(
              "relative z-10 flex items-center justify-center gap-2 rounded-full py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              active ? "text-white" : "text-zinc-400 hover:text-zinc-200"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        );
      })}
    </div>
  );
}
