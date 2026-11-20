"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { ArrowRight, Lock, Mail } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { getApiErrorMessage } from "@/lib/api/errors";
import { useAuthStore } from "@/lib/store/auth";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { RoleToggle } from "@/components/auth/role-toggle";
import { usePasswordVisibility } from "@/components/auth/password-toggle";

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<'CANDIDATE' | 'COMPANY'>('CANDIDATE');
  const setUser = useAuthStore((state) => state.setUser);
  const password = usePasswordVisibility();
  
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (data: LoginFormValues) => {
    try {
      const res = await apiClient.post("/auth/login", { ...data, role });
      const userData = res.data.data.user;
      
      setUser(userData);
      toast.success("Logged in successfully");
      router.push(`/dashboard/${role.toLowerCase()}/profile`);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to log in"));
    }
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold tracking-tight">Welcome back</h2>
        <p className="mt-1.5 text-sm text-muted-foreground">
          {role === 'CANDIDATE'
            ? "Sign in to practice, apply and join your AI interviews."
            : "Sign in to manage roles, pipelines and AI scorecards."}
        </p>
      </div>

      <RoleToggle value={role} onChange={setRole} className="mb-6" />

      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          placeholder={role === 'COMPANY' ? "you@company.com" : "name@example.com"}
          icon={<Mail />}
          {...form.register("email")}
          error={form.formState.errors.email?.message}
        />
        
        <div className="space-y-1.5">
          <Input
            label="Password"
            type={password.type}
            autoComplete="current-password"
            placeholder="••••••••"
            icon={<Lock />}
            endAdornment={password.toggle}
            {...form.register("password")}
            error={form.formState.errors.password?.message}
          />
          <div className="flex justify-end">
            <Link
              href={`/forgot-password?role=${role}`}
              className="text-xs font-medium text-indigo-400 transition-colors hover:text-indigo-300"
            >
              Forgot password?
            </Link>
          </div>
        </div>

        <Button
          type="submit"
          className="group h-11 w-full bg-gradient-to-r from-indigo-500 to-violet-500 text-white shadow-[0_8px_30px_-8px_rgba(99,102,241,0.7)] hover:from-indigo-400 hover:to-violet-400"
          isLoading={form.formState.isSubmitting}
        >
          {form.formState.isSubmitting ? "Signing in…" : (
            <>
              Sign in as {role === 'CANDIDATE' ? 'Candidate' : 'Company'}
              <ArrowRight className="ml-1.5 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </Button>
      </form>

      <div className="mt-6 border-t border-white/[0.06] pt-5 text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link
          href={`/register/${role.toLowerCase()}`}
          className="font-medium text-white underline-offset-4 hover:underline"
        >
          Create one free
        </Link>
      </div>
    </div>
  );
}
