import { describe, expect, it } from "vitest";

import {
  DEFAULT_TIMEFRAME,
  historyWindow,
  isTimeframe,
  timeframeSeconds,
} from "@/lib/ranges";

describe("timeframeSeconds", () => {
  it("maps presets to bucket sizes", () => {
    expect(timeframeSeconds("1m")).toBe(60);
    expect(timeframeSeconds("5m")).toBe(300);
    expect(timeframeSeconds("15m")).toBe(900);
  });
});

describe("isTimeframe", () => {
  it("accepts known timeframes", () => {
    expect(isTimeframe("5m")).toBe(true);
  });
  it("rejects unknown values", () => {
    expect(isTimeframe("24h")).toBe(false);
  });
});

describe("DEFAULT_TIMEFRAME", () => {
  it("is 1m", () => {
    expect(DEFAULT_TIMEFRAME).toBe("1m");
  });
});

describe("historyWindow", () => {
  it("returns a 24h window ending at now", () => {
    const now = new Date("2026-06-01T12:00:00Z");
    const { start, end } = historyWindow(now);
    expect(end).toBe("2026-06-01T12:00:00.000Z");
    expect(start).toBe("2026-05-31T12:00:00.000Z");
  });
});
