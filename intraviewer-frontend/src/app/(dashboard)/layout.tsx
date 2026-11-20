"use client";

import { useAuthStore } from "@/lib/store/auth";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api/client";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, logout, setUser } = useAuthStore();
  const router = useRouter();
  const [loading, setLoading] = useState(!isAuthenticated);

  useEffect(() => {
    if (!isAuthenticated) {
      apiClient.get("/auth/me")
        .then(res => {
          setUser(res.data.data.user);
          setLoading(false);
        })
        .catch(() => {
          logout();
          router.push("/login");
        });
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, router, setUser, logout]);

  const handleLogout = async () => {
    try {
      await apiClient.post("/auth/logout");
    } catch(e) {}
    logout();
    toast.success("Logged out");
    router.push("/login");
  };

  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-muted/30">
      <header className="bg-background border-b border-border h-16 flex items-center justify-between px-6">
        <h1 className="text-xl font-bold text-primary">Intraviewer</h1>
        <nav className="flex items-center gap-6 text-sm font-medium">
          <Link href={`/dashboard/${user?.role?.toLowerCase()}/profile`} className="hover:text-primary transition-colors">Profile</Link>
          {user?.role === "COMPANY" && (
            <Link href="/dashboard/company/jobs" className="hover:text-primary transition-colors">Manage Jobs</Link>
          )}
          {user?.role === "CANDIDATE" && (
            <>
              <Link href="/dashboard/candidate/jobs" className="hover:text-primary transition-colors">Find Jobs</Link>
              <Link href="/dashboard/candidate/applications" className="hover:text-primary transition-colors">My Applications</Link>
            </>
          )}
        </nav>
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium">{user?.name} ({user?.role})</span>
          <Button variant="outline" size="sm" onClick={handleLogout}>Logout</Button>
        </div>
      </header>
      <main className="max-w-5xl mx-auto py-8 px-4">
        {children}
      </main>
    </div>
  );
}
