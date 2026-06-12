"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ShoppingCart, LayoutDashboard, Search, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { authApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

const links = [
  { href: "/dashboard", label: "Табло", icon: LayoutDashboard },
  { href: "/lists", label: "Списъци", icon: ShoppingCart },
  { href: "/products", label: "Продукти", icon: Search },
];

export function Nav() {
  const pathname = usePathname();
  const router = useRouter();
  const { setUser, user } = useAuth();

  async function handleLogout() {
    await authApi.logout();
    setUser(null);
    router.push("/login");
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-100 shadow-sm">
      <div className="max-w-5xl mx-auto px-4 flex items-center justify-between h-14">
        <span className="font-bold text-primary-500 text-lg tracking-tight">
          Family Budget
        </span>
        <div className="flex items-center gap-1">
          {links.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-1.5 px-3 h-10 rounded-[10px] text-sm font-medium transition-colors",
                pathname.startsWith(href)
                  ? "bg-primary-50 text-primary-600"
                  : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
              )}
            >
              <Icon size={16} />
              <span className="hidden sm:inline">{label}</span>
            </Link>
          ))}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 h-10 rounded-[10px] text-sm font-medium text-gray-500 hover:text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut size={16} />
            <span className="hidden sm:inline">Изход</span>
          </button>
        </div>
      </div>
    </nav>
  );
}
