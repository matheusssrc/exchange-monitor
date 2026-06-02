import { describe, expect, it } from "vitest";

import { HistoryPageSchema, PairOutSchema, RateOutSchema } from "@/lib/schemas";

const validRate = {
  pair: "USD-BRL",
  bid: "5.1200",
  ask: "5.1210",
  mid: "5.1205",
  fetched_at: "2026-05-27T12:00:00Z",
  provider_timestamp: "2026-05-27T11:59:58Z",
  provider_name: "awesomeapi",
};

describe("schemas", () => {
  it("parses a valid pair", () => {
    expect(PairOutSchema.parse({ pair: "USD-BRL", base: "USD", quote: "BRL" })).toEqual({
      pair: "USD-BRL",
      base: "USD",
      quote: "BRL",
    });
  });

  it("parses a valid rate keeping decimals as strings", () => {
    const parsed = RateOutSchema.parse(validRate);
    expect(parsed.bid).toBe("5.1200");
    expect(typeof parsed.mid).toBe("string");
  });

  it("rejects a rate missing required fields", () => {
    expect(() => RateOutSchema.parse({ pair: "USD-BRL" })).toThrow();
  });

  it("parses a history page with nested items", () => {
    const page = HistoryPageSchema.parse({
      pair: "USD-BRL",
      start: "2026-05-27T00:00:00Z",
      end: "2026-05-27T23:59:59Z",
      count: 1,
      items: [validRate],
    });
    expect(page.count).toBe(1);
    expect(page.items[0]?.pair).toBe("USD-BRL");
  });
});
