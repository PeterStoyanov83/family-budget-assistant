import { cn } from "@/lib/utils";

type Score = "real" | "average" | "fake" | null;

const LABEL: Record<NonNullable<Score>, string> = {
  real: "РЕАЛНА",
  average: "СРЕДНА",
  fake: "ФАЛШИВА",
};

const COLOR: Record<NonNullable<Score>, string> = {
  real: "bg-[#52B788] text-white",
  average: "bg-[#F4A261] text-white",
  fake: "bg-[#E63946] text-white",
};

export function PromotionBadge({ score, discountPct }: { score: Score; discountPct?: number }) {
  if (!score) return null;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold",
        COLOR[score]
      )}
    >
      {LABEL[score]}
      {discountPct != null && ` -${discountPct.toFixed(0)}%`}
    </span>
  );
}
