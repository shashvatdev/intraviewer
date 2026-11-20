"use client";

import { useRouter } from "next/navigation";
import { RoleToggle, type Role } from "@/components/auth/role-toggle";

/** Role toggle for the register flow — switches between the two register routes. */
export function RegisterRoleSwitch({ current, className }: { current: Role; className?: string }) {
  const router = useRouter();
  return (
    <RoleToggle
      value={current}
      className={className}
      onChange={(role) => {
        if (role !== current) router.push(`/register/${role.toLowerCase()}`);
      }}
    />
  );
}

export const submitButtonClass =
  "group h-11 w-full bg-gradient-to-r from-indigo-500 to-violet-500 text-white shadow-[0_8px_30px_-8px_rgba(99,102,241,0.7)] hover:from-indigo-400 hover:to-violet-400";
