"use client";

import { useState, useEffect, useCallback } from "react";
import { Search } from "lucide-react";
import { productsApi, ProductWithPrices } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { PromotionBadge } from "@/components/promotion-badge";
import { formatEur, formatUnitPrice } from "@/lib/utils";

const CHAIN_LABELS: Record<string, string> = {
  lidl: "Lidl",
  kaufland: "Kaufland",
  billa: "Billa",
  fantastico: "Fantastico",
  tmarket: "T-Market",
};

export default function ProductsPage() {
  const [query, setQuery] = useState("");
  const [products, setProducts] = useState<ProductWithPrices[]>([]);
  const [loading, setLoading] = useState(false);

  const search = useCallback(async (q: string) => {
    setLoading(true);
    try {
      const results = await productsApi.search(q);
      setProducts(results);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    search("");
  }, [search]);

  useEffect(() => {
    const t = setTimeout(() => search(query), 300);
    return () => clearTimeout(t);
  }, [query, search]);

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-bold text-gray-900">Сравнение на цени</h1>

      <div className="relative">
        <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
        <Input
          placeholder="Търсете продукт..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {loading && <div className="text-sm text-gray-400">Търсене...</div>}

      {!loading && products.length === 0 && (
        <div className="text-center text-gray-400 py-12 text-sm">
          {query ? "Няма резултати." : "Въведете продукт за търсене."}
        </div>
      )}

      <div className="space-y-3">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}

function ProductCard({ product }: { product: ProductWithPrices }) {
  const sortedPrices = [...product.prices].sort((a, b) => a.price - b.price);
  const bestPrice = sortedPrices[0];
  const worstPrice = sortedPrices[sortedPrices.length - 1];
  const saving = worstPrice && bestPrice ? worstPrice.price - bestPrice.price : 0;

  return (
    <div className="bg-white border border-gray-100 rounded-[12px] overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-50">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">{product.canonical_name}</h3>
            {product.brand && <p className="text-xs text-gray-400">{product.brand}</p>}
          </div>
          {saving > 0.01 && (
            <span className="text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full whitespace-nowrap">
              до {formatEur(saving)} разлика
            </span>
          )}
        </div>
      </div>

      <div className="divide-y divide-gray-50">
        {sortedPrices.map((price, i) => (
          <div
            key={price.id}
            className={`px-4 py-2.5 flex items-center justify-between ${i === 0 ? "bg-green-50/40" : ""}`}
          >
            <div className="flex items-center gap-2">
              {i === 0 && (
                <span className="text-xs text-[#52B788] font-semibold">★</span>
              )}
              <span className="text-sm text-gray-700">
                {CHAIN_LABELS[price.store?.chain] ?? price.store?.name ?? `Магазин ${price.store_id}`}
              </span>
              {price.is_member && (
                <span className="text-xs bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded-full">
                  карта
                </span>
              )}
            </div>
            <div className="text-right">
              <span className="font-semibold text-gray-900">{formatEur(price.price)}</span>
              {price.unit_price && (
                <p className="text-xs text-gray-400">
                  {formatUnitPrice(price.unit_price, product.unit_type)}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {sortedPrices.length === 0 && (
        <div className="px-4 py-3 text-sm text-gray-400">Няма данни за цени.</div>
      )}
    </div>
  );
}
