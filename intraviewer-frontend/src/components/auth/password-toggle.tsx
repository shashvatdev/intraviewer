"use client";

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

/** Show/hide toggle meant to be passed as `endAdornment` to <Input />. */
export function usePasswordVisibility() {
  const [visible, setVisible] = useState(false);

  const toggle = (
    <button
      type="button"
      onClick={() => setVisible((v) => !v)}
      className="flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-white/5 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      aria-label={visible ? "Hide password" : "Show password"}
      tabIndex={-1}
    >
      {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
    </button>
  );

  return { type: visible ? "text" : "password", toggle } as const;
}
