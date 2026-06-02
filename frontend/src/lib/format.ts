export type TrendDirection = "up" | "down" | "flat";

export interface Trend {
  direction: TrendDirection;
  deltaAbs: string;
  deltaPct: string;
}

export function formatNumber(value: string | number, fractionDigits = 4): string {
  const num = typeof value === "string" ? Number(value) : value;
  return num.toLocaleString("en-US", {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });
}

export function formatTimestamp(iso: string): string {
  return new Date(iso).toLocaleString("pt-BR", {
    dateStyle: "short",
    timeStyle: "medium",
    timeZone: "UTC",
  });
}

export function computeTrend(
  latestMid: string,
  baselineMid: string | undefined,
): Trend {
  if (baselineMid === undefined) {
    return { direction: "flat", deltaAbs: "—", deltaPct: "—" };
  }
  const latest = Number(latestMid);
  const baseline = Number(baselineMid);
  const delta = latest - baseline;
  const pct = baseline !== 0 ? (delta / baseline) * 100 : 0;
  const direction: TrendDirection = delta > 0 ? "up" : delta < 0 ? "down" : "flat";
  const sign = delta > 0 ? "+" : delta < 0 ? "-" : "";
  return {
    direction,
    deltaAbs: `${sign}${formatNumber(Math.abs(delta))}`,
    deltaPct: `${sign}${Math.abs(pct).toFixed(2)}%`,
  };
}
