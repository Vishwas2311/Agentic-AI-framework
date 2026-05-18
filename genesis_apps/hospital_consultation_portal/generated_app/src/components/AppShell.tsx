"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useApp } from "@/context/AppContext";
import { Sidebar } from "./Sidebar";
import { TopHeader } from "./TopHeader";

interface AppShellProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  requireAuth?: boolean;
}

export function AppShell({ children, title, subtitle, requireAuth = true }: AppShellProps) {
  const { state } = useApp();
  const router = useRouter();

  useEffect(() => {
    if (requireAuth && !state.session.isLoggedIn) {
      router.replace("/");
    }
  }, [state.session.isLoggedIn, requireAuth, router]);

  if (requireAuth && !state.session.isLoggedIn) return null;

  return (
    <div className="min-h-screen bg-surface p-4">
      <div className="max-w-[1400px] mx-auto">
        <TopHeader title={title} subtitle={subtitle} />
        <div className="flex gap-4">
          <Sidebar />
          <main className="flex-1 min-w-0">{children}</main>
        </div>
      </div>
    </div>
  );
}
