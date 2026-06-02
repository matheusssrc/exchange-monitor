import type { RateOut } from "@/types/api";

export interface Candle {
  time: number; // bucket start, epoch ms
  open: number;
  high: number;
  low: number;
  close: number;
}

export function buildOHLC(data: RateOut[], bucketSeconds: number): Candle[] {
  if (data.length === 0) {
    return [];
  }
  const bucketMs = bucketSeconds * 1000;
  const sorted = [...data].sort(
    (a, b) => new Date(a.fetched_at).getTime() - new Date(b.fetched_at).getTime(),
  );
  const buckets = new Map<number, Candle>();
  for (const rate of sorted) {
    const t = new Date(rate.fetched_at).getTime();
    const mid = Number(rate.mid);
    const key = Math.floor(t / bucketMs) * bucketMs;
    const existing = buckets.get(key);
    if (!existing) {
      buckets.set(key, { time: key, open: mid, high: mid, low: mid, close: mid });
    } else {
      existing.high = Math.max(existing.high, mid);
      existing.low = Math.min(existing.low, mid);
      existing.close = mid;
    }
  }
  return [...buckets.values()].sort((a, b) => a.time - b.time);
}
