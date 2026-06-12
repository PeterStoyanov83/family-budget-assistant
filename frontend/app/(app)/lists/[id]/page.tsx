"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Plus, Trash2, Check, ChevronLeft } from "lucide-react";
import Link from "next/link";
import { listsApi, ShoppingList, ListItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatEur } from "@/lib/utils";

export default function ListDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [list, setList] = useState<ShoppingList | null>(null);
  const [loading, setLoading] = useState(true);
  const [itemName, setItemName] = useState("");
  const [itemQty, setItemQty] = useState("1");
  const [adding, setAdding] = useState(false);

  useEffect(() => {
    listsApi.get(Number(id)).then(setList).finally(() => setLoading(false));
  }, [id]);

  async function handleAddItem(e: React.FormEvent) {
    e.preventDefault();
    if (!itemName.trim() || !list) return;
    setAdding(true);
    try {
      const item = await listsApi.addItem(list.id, {
        name: itemName.trim(),
        quantity: parseFloat(itemQty) || 1,
      });
      setList((prev) => prev ? { ...prev, items: [...prev.items, item] } : prev);
      setItemName("");
      setItemQty("1");
    } finally {
      setAdding(false);
    }
  }

  async function toggleCheck(item: ListItem) {
    if (!list) return;
    const updated = await listsApi.updateItem(list.id, item.id, { is_checked: !item.is_checked });
    setList((prev) =>
      prev ? { ...prev, items: prev.items.map((i) => (i.id === item.id ? updated : i)) } : prev
    );
  }

  async function deleteItem(item: ListItem) {
    if (!list) return;
    await listsApi.deleteItem(list.id, item.id);
    setList((prev) =>
      prev ? { ...prev, items: prev.items.filter((i) => i.id !== item.id) } : prev
    );
  }

  if (loading) {
    return <div className="text-sm text-gray-400 pt-8 text-center">Зареждане...</div>;
  }
  if (!list) {
    return <div className="text-sm text-gray-400 pt-8 text-center">Списъкът не е намерен.</div>;
  }

  const checkedCount = list.items.filter((i) => i.is_checked).length;
  const remaining = list.items.filter((i) => !i.is_checked);
  const checked = list.items.filter((i) => i.is_checked);

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-3">
        <Link href="/lists" className="text-gray-400 hover:text-gray-700">
          <ChevronLeft size={20} />
        </Link>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-gray-900">{list.name}</h1>
          <p className="text-xs text-gray-400">
            {checkedCount}/{list.items.length} отметнати
            {list.budget ? ` · бюджет ${formatEur(list.budget)}` : ""}
          </p>
        </div>
      </div>

      {/* Progress bar */}
      {list.items.length > 0 && (
        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-500 transition-all"
            style={{ width: `${(checkedCount / list.items.length) * 100}%` }}
          />
        </div>
      )}

      {/* Add item form */}
      <form onSubmit={handleAddItem}
        className="bg-white border border-gray-100 rounded-[12px] p-4 flex gap-3 items-end">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">Продукт</label>
          <Input placeholder="Кисело мляко" value={itemName}
            onChange={(e) => setItemName(e.target.value)} />
        </div>
        <div className="w-20">
          <label className="block text-sm font-medium text-gray-700 mb-1">Кол.</label>
          <Input type="number" step="0.5" min="0.5" value={itemQty}
            onChange={(e) => setItemQty(e.target.value)} />
        </div>
        <Button type="submit" disabled={adding || !itemName.trim()} size="icon">
          <Plus size={16} />
        </Button>
      </form>

      {/* Remaining items */}
      {remaining.length > 0 && (
        <div className="space-y-1.5">
          {remaining.map((item) => (
            <ItemRow key={item.id} item={item} onCheck={toggleCheck} onDelete={deleteItem} />
          ))}
        </div>
      )}

      {/* Checked items */}
      {checked.length > 0 && (
        <div>
          <p className="text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">Купени</p>
          <div className="space-y-1.5 opacity-60">
            {checked.map((item) => (
              <ItemRow key={item.id} item={item} onCheck={toggleCheck} onDelete={deleteItem} />
            ))}
          </div>
        </div>
      )}

      {list.items.length === 0 && (
        <div className="text-center text-gray-400 py-10 text-sm">Добавете продукти.</div>
      )}
    </div>
  );
}

function ItemRow({ item, onCheck, onDelete }: {
  item: ListItem;
  onCheck: (item: ListItem) => void;
  onDelete: (item: ListItem) => void;
}) {
  return (
    <div className="bg-white border border-gray-100 rounded-[12px] px-4 py-2.5 flex items-center gap-3">
      <button
        onClick={() => onCheck(item)}
        className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
          item.is_checked
            ? "bg-primary-500 border-primary-500 text-white"
            : "border-gray-300 hover:border-primary-400"
        }`}
      >
        {item.is_checked && <Check size={11} strokeWidth={3} />}
      </button>
      <div className="flex-1 min-w-0">
        <span className={`text-sm ${item.is_checked ? "line-through text-gray-400" : "text-gray-900"}`}>
          {item.name}
        </span>
        {item.quantity !== 1 && (
          <span className="text-xs text-gray-400 ml-1.5">× {item.quantity}</span>
        )}
      </div>
      <button
        onClick={() => onDelete(item)}
        className="p-1.5 text-gray-300 hover:text-red-400 transition-colors"
      >
        <Trash2 size={13} />
      </button>
    </div>
  );
}
