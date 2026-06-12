"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ShoppingCart, TrendingDown, Tag, Plus } from "lucide-react";
import { listsApi, promotionsApi, ListSummary, Promotion } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { PromotionBadge } from "@/components/promotion-badge";
import { formatEur } from "@/lib/utils";

export default function DashboardPage() {
  const { user } = useAuth();
  const [lists, setLists] = useState<ListSummary[]>([]);
  const [promos, setPromos] = useState<Promotion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([listsApi.getAll(), promotionsApi.list({ score: "real", valid: true })])
      .then(([l, p]) => {
        setLists(l.slice(0, 3));
        setPromos(p.slice(0, 5));
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Здравей{user?.first_name ? `, ${user.first_name}` : ""}!
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">Ето какво се случва тази седмица.</p>
        </div>
        <Link href="/lists">
          <Button size="sm" className="gap-1.5">
            <Plus size={15} />
            Нов списък
          </Button>
        </Link>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard icon={<ShoppingCart size={20} />} label="Активни списъци"
          value={lists.filter(l => l.status === "active").length.toString()} />
        <StatCard icon={<TrendingDown size={20} />} label="Реални промоции"
          value={promos.length.toString()} />
        <StatCard icon={<Tag size={20} />} label="Планиран бюджет"
          value={lists[0]?.budget ? formatEur(lists[0].budget) : "—"} />
      </div>

      {/* Recent lists */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-800">Последни списъци</h2>
          <Link href="/lists" className="text-sm text-primary-500 hover:underline">Всички</Link>
        </div>
        {loading ? (
          <div className="text-sm text-gray-400">Зареждане...</div>
        ) : lists.length === 0 ? (
          <EmptyState
            title="Нямате списъци"
            description="Създайте първия си списък за пазаруване."
            action={{ label: "Нов списък", href: "/lists" }}
          />
        ) : (
          <div className="space-y-2">
            {lists.map((list) => (
              <Link key={list.id} href={`/lists/${list.id}`}>
                <div className="bg-white border border-gray-100 rounded-[12px] px-4 py-3 hover:border-primary-200 hover:shadow-sm transition-all flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{list.name}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {list.status === "active" ? "Активен" : list.status === "completed" ? "Завършен" : "Чернова"}
                    </p>
                  </div>
                  {list.budget && (
                    <span className="text-sm font-semibold text-primary-600">{formatEur(list.budget)}</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Real promotions */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-800">Реални промоции</h2>
          <Link href="/products" className="text-sm text-primary-500 hover:underline">Виж всички</Link>
        </div>
        {promos.length === 0 && !loading ? (
          <div className="text-sm text-gray-400">Няма активни реални промоции.</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {promos.map((p) => (
              <div key={p.id}
                className="bg-white border border-gray-100 rounded-[12px] px-4 py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">Продукт #{p.product_id}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <PromotionBadge score={p.score} discountPct={p.discount_pct} />
                    <span className="text-xs text-gray-400">
                      {formatEur(p.promo_price)} вместо {formatEur(p.regular_price)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="bg-white border border-gray-100 rounded-[12px] px-4 py-4">
      <div className="text-primary-500 mb-2">{icon}</div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-xs text-gray-500 mt-0.5">{label}</p>
    </div>
  );
}

function EmptyState({ title, description, action }: {
  title: string; description: string; action?: { label: string; href: string };
}) {
  return (
    <div className="bg-white border border-dashed border-gray-200 rounded-[12px] px-6 py-10 text-center">
      <p className="font-medium text-gray-700">{title}</p>
      <p className="text-sm text-gray-400 mt-1">{description}</p>
      {action && (
        <Link href={action.href}>
          <Button size="sm" className="mt-4">{action.label}</Button>
        </Link>
      )}
    </div>
  );
}
