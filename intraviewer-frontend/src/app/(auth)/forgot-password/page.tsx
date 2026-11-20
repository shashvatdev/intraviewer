"use client";

import { useState, useRef, Suspense } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import { getApiErrorMessage, getApiErrorStatus } from "@/lib/api/errors";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const emailSchema = z.object({
  email: z.string().email("Invalid email address"),
});

const resetSchema = z.object({
  new_password: z.string().min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[0-9]/, "Password must contain at least one number"),
  confirm_password: z.string()
}).refine(data => data.new_password === data.confirm_password, {
  message: "Passwords do not match",
  path: ["confirm_password"]
});

function ForgotPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const role = searchParams.get("role") || "CANDIDATE";
  
  const [step, setStep] = useState<"EMAIL" | "OTP" | "RESET">("EMAIL");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const emailForm = useForm<{ email: string }>({
    resolver: zodResolver(emailSchema),
    defaultValues: { email: "" },
  });

  const resetForm = useForm<z.infer<typeof resetSchema>>({
    resolver: zodResolver(resetSchema),
    defaultValues: { new_password: "", confirm_password: "" },
  });

  const onEmailSubmit = async (data: { email: string }) => {
    try {
      await apiClient.post("/auth/forgot-password", { email: data.email, role });
      setEmail(data.email);
      setStep("OTP");
      toast.success("Code sent to your email (if it exists)");
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to send code"));
    }
  };

  const handleOtpChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);
    if (value && index < 5) inputRefs.current[index + 1]?.focus();
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const onOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = otp.join("");
    if (code.length < 6) {
      toast.error("Please enter the 6-digit code");
      return;
    }
    // Just move to reset step, we verify OTP and Reset together in the backend API
    setStep("RESET");
  };

  const onResetSubmit = async (data: z.infer<typeof resetSchema>) => {
    try {
      await apiClient.post("/auth/reset-password", {
        email,
        otp: otp.join(""),
        new_password: data.new_password,
        confirm_password: data.confirm_password,
      });
      toast.success("Password reset successfully. You can now log in.");
      router.push("/login");
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to reset password"));
      if (getApiErrorStatus(error) === 400 && getApiErrorMessage(error, "").includes("Invalid reset code")) {
        setStep("OTP");
      }
    }
  };

  return (
    <div className="w-full">
      {step === "EMAIL" && (
        <>
          <div className="mb-8">
            <h2 className="text-2xl font-semibold tracking-tight">Reset your password</h2>
            <p className="text-sm text-muted-foreground mt-2">Enter your email address.</p>
          </div>
          <form onSubmit={emailForm.handleSubmit(onEmailSubmit)} className="space-y-4">
            <Input
              label="Email"
              type="email"
              placeholder="name@example.com"
              {...emailForm.register("email")}
              error={emailForm.formState.errors.email?.message}
            />
            <Button type="submit" className="w-full" isLoading={emailForm.formState.isSubmitting}>
              Send OTP
            </Button>
          </form>
          <div className="mt-6 text-center text-sm">
            <Link href="/login" className="font-medium text-primary hover:underline">
              Back to login
            </Link>
          </div>
        </>
      )}

      {step === "OTP" && (
        <>
          <div className="mb-8">
            <h2 className="text-2xl font-semibold tracking-tight">Verify OTP</h2>
            <p className="text-sm text-muted-foreground mt-2">
              We&apos;ve sent a 6-digit code to <span className="font-medium text-foreground">{email}</span>
            </p>
          </div>
          <form onSubmit={onOtpSubmit} className="space-y-6">
            <div className="flex gap-2 justify-center">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={(el) => { inputRefs.current[index] = el; }}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleOtpChange(index, e.target.value)}
                  onKeyDown={(e) => handleOtpKeyDown(index, e)}
                  className="h-12 w-10 sm:h-14 sm:w-12 text-center text-xl font-bold rounded-md border border-input bg-transparent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
              ))}
            </div>
            <Button type="submit" className="w-full">
              Continue
            </Button>
          </form>
        </>
      )}

      {step === "RESET" && (
        <>
          <div className="mb-8">
            <h2 className="text-2xl font-semibold tracking-tight">Create new password</h2>
            <p className="text-sm text-muted-foreground mt-2">Please enter your new password.</p>
          </div>
          <form onSubmit={resetForm.handleSubmit(onResetSubmit)} className="space-y-4">
            <Input
              label="New Password"
              type="password"
              placeholder="••••••••"
              {...resetForm.register("new_password")}
              error={resetForm.formState.errors.new_password?.message}
            />
            <Input
              label="Confirm Password"
              type="password"
              placeholder="••••••••"
              {...resetForm.register("confirm_password")}
              error={resetForm.formState.errors.confirm_password?.message}
            />
            <Button type="submit" className="w-full" isLoading={resetForm.formState.isSubmitting}>
              Reset Password
            </Button>
          </form>
        </>
      )}
    </div>
  );
}

export default function ForgotPasswordPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ForgotPasswordForm />
    </Suspense>
  );
}
