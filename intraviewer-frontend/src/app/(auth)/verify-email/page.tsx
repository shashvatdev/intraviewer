"use client";

import { useState, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { apiClient } from "@/lib/api/client";
import { getApiErrorMessage } from "@/lib/api/errors";
import { Button } from "@/components/ui/button";

function VerifyEmailForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get("email") || "";
  const purpose = searchParams.get("purpose") || "EMAIL_VERIFICATION";
  
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);

    // move to next
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text/plain").slice(0, 6).replace(/\D/g, "");
    if (!pasted) return;
    
    const newOtp = [...otp];
    for (let i = 0; i < pasted.length; i++) {
      newOtp[i] = pasted[i];
    }
    setOtp(newOtp);
    const focusIndex = Math.min(pasted.length, 5);
    inputRefs.current[focusIndex]?.focus();
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const code = otp.join("");
    if (code.length < 6) {
      toast.error("Please enter the 6-digit code");
      return;
    }
    
    setIsSubmitting(true);
    try {
      await apiClient.post("/auth/verify-otp", {
        email,
        otp: code,
        purpose
      });
      toast.success("Email verified successfully");
      router.push("/login");
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Invalid code"));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResend = async () => {
    setIsResending(true);
    try {
      await apiClient.post("/auth/resend-otp", {
        email,
        purpose
      });
      toast.success("Code resent to your email");
      setOtp(["", "", "", "", "", ""]);
      inputRefs.current[0]?.focus();
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to resend code"));
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="w-full">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold tracking-tight">Verify your email</h2>
        <p className="text-sm text-muted-foreground mt-2">
          We&apos;ve sent a 6-digit verification code to <span className="font-medium text-foreground">{email}</span>
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-6">
        <div className="flex gap-2 justify-center" onPaste={handlePaste}>
          {otp.map((digit, index) => (
            <input
              key={index}
              ref={(el) => { inputRefs.current[index] = el; }}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              className="h-12 w-10 sm:h-14 sm:w-12 text-center text-xl font-bold rounded-md border border-input bg-transparent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          ))}
        </div>

        <Button type="submit" className="w-full" isLoading={isSubmitting}>
          Verify Email
        </Button>
      </form>

      <div className="mt-6 text-center text-sm">
        <span className="text-muted-foreground">Didn&apos;t receive the code?</span>{" "}
        <button 
          type="button" 
          onClick={handleResend}
          disabled={isResending}
          className="font-medium text-primary hover:underline disabled:opacity-50"
        >
          Resend OTP
        </button>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <VerifyEmailForm />
    </Suspense>
  );
}
