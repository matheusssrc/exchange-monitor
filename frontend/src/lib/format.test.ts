import { describe, expect, it } from "vitest";

import { computeTrend, formatNumber } from "@/lib/format";

describe("formatNumber", () => {
  it("formats a string decimal to 4 fraction digits", () => {
    expect(formatNumber("5.12")).toBe("5.1200");
  });
});

describe("computeTrend", () => {
  it("returns flat with em dashes when baseline is undefined", () => {
    const trend = computeTrend("5.12", undefined);
    expect(trend.direction).toBe("flat");
    expect(trend.deltaAbs).toBe("—");
    expect(trend.deltaPct).toBe("—");
  });

  it("returns up when latest exceeds baseline", () => {
    const trend = computeTrend("5.20", "5.00");
    expect(trend.direction).toBe("up");
    expect(trend.deltaPct).toBe("+4.00%");
  });

  it("returns down when latest is below baseline", () => {
    const trend = computeTrend("4.80", "5.00");
    expect(trend.direction).toBe("down");
    expect(trend.deltaPct).toBe("-4.00%");
  });

  it("returns flat when equal", () => {
    expect(computeTrend("5.00", "5.00").direction).toBe("flat");
  });
});
