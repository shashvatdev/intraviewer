"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { ArrowRight, Building2, Lock, Mail } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { getApiErrorMessage } from "@/lib/api/errors";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { RegisterRoleSwitch, submitButtonClass } from "@/components/auth/register-role-switch";
import { usePasswordVisibility } from "@/components/auth/password-toggle";

const registerSchema = z.object({
  name: z.string().min(2, "Company name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[0-9]/, "Password must contain at least one number"),
  confirm_password: z.string()
}).refine(data => data.password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"]
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function CompanyRegisterPage() {
  const router = useRouter();
  const password = usePasswordVisibility();
  
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: "", email: "", password: "", confirm_password: "" },
  });

  const onSubmit = async (data: RegisterFormValues) => {
    try {
      await apiClient.post("/auth/register/company", data);
      toast.success("Company account created! Please verify your email.");
      router.push(`/verify-email?email=${encodeURIComponent(data.email)}&purpose=EMAIL_VERIFICATION`);
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Registration failed"));
    }
  };

  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold tracking-tight">Create your company account</h2>
        <p className="mt-1.5 text-sm text-muted-foreground">Build your hiring pipeline with AI. Screen 10x faster.</p>
      </div>

      <RegisterRoleSwitch current="COMPANY" className="mb-6" />

      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Company Name"
          placeholder="Acme Inc"
          autoComplete="organization"
          icon={<Building2 />}
          {...form.register("name")}
          error={form.formState.errors.name?.message}
        />
        <Input
          label="Business Email"
          type="email"
          placeholder="you@company.com"
          autoComplete="email"
          icon={<Mail />}
          {...form.register("email")}
          error={form.formState.errors.email?.message}
        />
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label="Password"
            type={password.type}
            placeholder="••••••••"
            autoComplete="new-password"
            icon={<Lock />}
            endAdornment={password.toggle}
            {...form.register("password")}
            error={form.formState.errors.password?.message}
          />
          <Input
            label="Confirm Password"
            type={password.type}
            placeholder="••••••••"
            autoComplete="new-password"
            icon={<Lock />}
            {...form.register("confirm_password")}
            error={form.formState.errors.confirm_password?.message}
          />
        </div>
        <p className="text-xs text-muted-foreground">8+ characters with at least one uppercase letter and one number.</p>

        <Button type="submit" className={submitButtonClass} isLoading={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Creating account…" : (
            <>
              Create Company Account
              <ArrowRight className="ml-1.5 h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </Button>
      </form>

      <div className="mt-6 border-t border-white/[0.06] pt-5 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-white underline-offset-4 hover:underline">
          Sign in
        </Link>
      </div>
    </div>
  );
}
