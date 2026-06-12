"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Nav } from "@/components/nav";
import { useAuth } from "@/lib/auth-context";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <span className="text-gray-400 text-sm">Зареждане...</span>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <main className="max-w-5xl mx-auto px-4 pt-20 pb-8">{children}</main>
    </div>
  );
}
