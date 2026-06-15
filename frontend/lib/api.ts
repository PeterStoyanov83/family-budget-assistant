const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json();
}

// --- Auth ---
export const authApi = {
  register: (data: RegisterPayload) =>
    request<User>("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data: LoginPayload) =>
    request<User>("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  logout: () => request<void>("/auth/logout", { method: "POST" }),
  me: () => request<User>("/auth/me"),
  refresh: () => request<User>("/auth/refresh", { method: "POST" }),
};

// --- Lists ---
export const listsApi = {
  getAll: () => request<ListSummary[]>("/lists"),
  get: (id: number) => request<ShoppingList>(`/lists/${id}`),
  create: (data: { name: string; budget?: number }) =>
    request<ShoppingList>("/lists", { method: "POST", body: JSON.stringify(data) }),
  update: (id: number, data: Partial<{ name: string; budget: number; status: string }>) =>
    request<ShoppingList>(`/lists/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (id: number) => request<void>(`/lists/${id}`, { method: "DELETE" }),
  addItem: (listId: number, data: ListItemPayload) =>
    request<ListItem>(`/lists/${listId}/items`, { method: "POST", body: JSON.stringify(data) }),
  updateItem: (listId: number, itemId: number, data: Partial<ListItemPayload & { is_checked: boolean }>) =>
    request<ListItem>(`/lists/${listId}/items/${itemId}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteItem: (listId: number, itemId: number) =>
    request<void>(`/lists/${listId}/items/${itemId}`, { method: "DELETE" }),
};

// --- Products ---
export const productsApi = {
  search: (q: string, store?: string) =>
    request<ProductWithPrices[]>(`/products/search?q=${encodeURIComponent(q)}${store ? `&store=${store}` : ""}`),
  priceHistory: (id: number, days = 30) =>
    request<PriceHistoryPoint[]>(`/products/${id}/price-history?days=${days}`),
  alternatives: (id: number) => request<ProductWithPrices[]>(`/products/${id}/alternatives`),
};

// --- Promotions ---
export const promotionsApi = {
  list: (params?: { store?: string; score?: string; valid?: boolean }) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return request<Promotion[]>(`/promotions${qs ? `?${qs}` : ""}`);
  },
};

// --- Types ---
export interface User {
  id: number;
  email: string;
  first_name: string | null;
  household_size: number;
  plan: string;
  has_car: boolean;
  city: string | null;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name?: string;
  household_size?: number;
  city?: string;
  has_car?: boolean;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface ListSummary {
  id: number;
  name: string;
  budget: number | null;
  status: string;
  item_count: number;
  created_at: string;
}

export interface ListItem {
  id: number;
  list_id: number;
  product_id: number | null;
  name: string;
  quantity: number;
  unit: string | null;
  preferred_brand: string | null;
  note: string | null;
  is_checked: boolean;
  created_at: string;
}

export interface ShoppingList {
  id: number;
  user_id: number;
  name: string;
  budget: number | null;
  currency: string;
  status: string;
  created_at: string;
  updated_at: string;
  items: ListItem[];
}

export interface ListItemPayload {
  name: string;
  quantity?: number;
  unit?: string;
  preferred_brand?: string;
  note?: string;
  product_id?: number;
}

export interface Store {
  id: number;
  name: string;
  chain: string;
  city: string;
  address: string | null;
  lat: number | null;
  lng: number | null;
  promo_day: string | null;
}

export interface PriceOut {
  id: number;
  store_id: number;
  store: Store;
  price: number;
  unit_price: number | null;
  currency: string;
  is_member: boolean;
  scraped_at: string;
}

export interface ProductWithPrices {
  id: number;
  canonical_name: string;
  brand: string | null;
  category: string | null;
  unit_type: string | null;
  unit_size: number | null;
  unit_size_label: string | null;
  image_url: string | null;
  prices: PriceOut[];
}

export interface PriceHistoryPoint {
  price: number;
  unit_price: number | null;
  store_id: number;
  store_name: string;
  is_member: boolean;
  scraped_at: string;
}

export interface Promotion {
  id: number;
  product_id: number;
  store_id: number;
  promo_price: number;
  regular_price: number;
  discount_pct: number;
  score: "real" | "average" | "fake" | null;
  hist_avg_30d: number | null;
  valid_until: string | null;
  is_active: boolean;
}
