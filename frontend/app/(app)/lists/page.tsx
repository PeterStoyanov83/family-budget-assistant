"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Trash2 } from "lucide-react";
import { listsApi, ListSummary } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatEur } from "@/lib/utils";

export default function ListsPage() {
  const [lists, setLists] = useState<ListSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const [newBudget, setNewBudget] = useState("");

  useEffect(() => {
    listsApi.getAll().then(setLists).finally(() => setLoading(false));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const list = await listsApi.create({
        name: newName.trim(),
        budget: newBudget ? parseFloat(newBudget) : undefined,
      });
      setLists((prev) => [{ ...list, item_count: 0 }, ...prev]);
      setNewName("");
      setNewBudget("");
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: number) {
    await listsApi.delete(id);
    setLists((prev) => prev.filter((l) => l.id !== id));
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Списъци за пазаруване</h1>

      {/* Create form */}
      <form onSubmit={handleCreate}
        className="bg-white border border-gray-100 rounded-[12px] p-4 flex gap-3 items-end">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">Нов списък</label>
          <Input placeholder="Седмично пазаруване" value={newName}
            onChange={(e) => setNewName(e.target.value)} />
        </div>
        <div className="w-32">
          <label className="block text-sm font-medium text-gray-700 mb-1">Бюджет (€)</label>
          <Input type="number" step="0.01" placeholder="30.00" value={newBudget}
            onChange={(e) => setNewBudget(e.target.value)} />
        </div>
        <Button type="submit" disabled={creating || !newName.trim()} className="gap-1.5">
          <Plus size={16} />
          Добави
        </Button>
      </form>

      {/* List */}
      {loading ? (
        <div className="text-sm text-gray-400">Зареждане...</div>
      ) : lists.length === 0 ? (
        <div className="text-center text-gray-400 py-12 text-sm">Нямате списъци.</div>
      ) : (
        <div className="space-y-2">
          {lists.map((list) => (
            <div key={list.id}
              className="bg-white border border-gray-100 rounded-[12px] px-4 py-3 flex items-center justify-between hover:border-primary-200 transition-colors">
              <Link href={`/lists/${list.id}`} className="flex-1 min-w-0">
                <p className="font-medium text-gray-900 truncate">{list.name}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {list.status === "active" ? "Активен" : list.status === "completed" ? "Завършен" : "Чернова"}
                  {list.budget ? ` · бюджет ${formatEur(list.budget)}` : ""}
                </p>
              </Link>
              <button
                onClick={() => handleDelete(list.id)}
                className="ml-3 p-2 text-gray-400 hover:text-red-500 transition-colors rounded-[8px] hover:bg-red-50"
              >
                <Trash2 size={15} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
