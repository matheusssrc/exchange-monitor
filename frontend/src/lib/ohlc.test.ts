import { describe, expect, it } from "vitest";

import { buildOHLC, type Candle } from "@/lib/ohlc";
import type { RateOut } from "@/types/api";

function tick(fetched_at: string, mid: string): RateOut {
  return {
    pair: "BRL-USD",
    bid: mid,
    ask: mid,
    mid,
    fetched_at,
    provider_timestamp: fetched_at,
    provider_name: "awesomeapi",
  };
}

describe("buildOHLC", () => {
  it("returns empty for no data", () => {
    expect(buildOHLC([], 60)).toEqual([]);
  });

  it("groups ticks into one 1-minute candle with correct OHLC", () => {
    const data = [
      tick("2026-06-01T12:00:05.000Z", "5.00"),
      tick("2026-06-01T12:00:20.000Z", "5.20"),
      tick("2026-06-01T12:00:40.000Z", "4.90"),
      tick("2026-06-01T12:00:55.000Z", "5.10"),
    ];
    const candles = buildOHLC(data, 60);
    expect(candles).toHaveLength(1);
    const c = candles[0] as Candle;
    expect(c.open).toBe(5.0);
    expect(c.high).toBe(5.2);
    expect(c.low).toBe(4.9);
    expect(c.close).toBe(5.1);
    expect(c.time).toBe(new Date("2026-06-01T12:00:00.000Z").getTime());
  });

  it("splits ticks across separate buckets and sorts ascending", () => {
    const data = [
      tick("2026-06-01T12:01:10.000Z", "6.00"),
      tick("2026-06-01T12:00:10.000Z", "5.00"),
      tick("2026-06-01T12:00:50.000Z", "5.50"),
    ];
    const candles = buildOHLC(data, 60);
    expect(candles).toHaveLength(2);
    expect(candles[0]?.time).toBeLessThan(candles[1]?.time ?? 0);
    expect(candles[0]?.open).toBe(5.0);
    expect(candles[0]?.close).toBe(5.5);
    expect(candles[1]?.open).toBe(6.0);
  });
});
