import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatEur(amount: number): string {
  return new Intl.NumberFormat("bg-BG", { style: "currency", currency: "EUR" }).format(amount);
}

export function formatUnitPrice(unitPrice: number | null, unitType: string | null): string {
  if (!unitPrice || !unitType) return "";
  const unit = unitType === "kg" ? "кг" : unitType === "l" ? "л" : "бр";
  return `${formatEur(unitPrice)}/${unit}`;
}
