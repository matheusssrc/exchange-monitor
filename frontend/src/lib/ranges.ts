export const TIMEFRAMES = ["1m", "5m", "15m"] as const;
export type Timeframe = (typeof TIMEFRAMES)[number];

export const DEFAULT_TIMEFRAME: Timeframe = "1m";

export function isTimeframe(value: string): value is Timeframe {
  return (TIMEFRAMES as readonly string[]).includes(value);
}

const TIMEFRAME_SECONDS: Record<Timeframe, number> = {
  "1m": 60,
  "5m": 300,
  "15m": 900,
};

export function timeframeSeconds(tf: Timeframe): number {
  return TIMEFRAME_SECONDS[tf];
}

export const HISTORY_WINDOW_HOURS = 24;

export interface HistoryRange {
  start: string;
  end: string;
}

/** Fixed, generous fetch window (last 24h). The selected timeframe only drives
 * candle bucketing on the client, not the fetched window. */
export function historyWindow(now: Date = new Date()): HistoryRange {
  const start = new Date(now.getTime() - HISTORY_WINDOW_HOURS * 3600 * 1000);
  return { start: start.toISOString(), end: now.toISOString() };
}
