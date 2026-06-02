import { describe, expect, it } from "vitest";

import { currencyLabel, pairLabel } from "@/lib/pairs";

describe("pairLabel", () => {
  it("formats a pair as base → quote", () => {
    expect(pairLabel("BRL-USD")).toBe("BRL → USD");
    expect(pairLabel("EUR-BRL")).toBe("EUR → BRL");
  });

  it("falls back to the raw id when not a two-part pair", () => {
    expect(pairLabel("WEIRD")).toBe("WEIRD");
    expect(pairLabel("A-B-C")).toBe("A-B-C");
  });
});

describe("currencyLabel", () => {
  it("maps known currency codes to friendly names", () => {
    expect(currencyLabel("BRL")).toBe("Real (BRL)");
    expect(currencyLabel("USD")).toBe("Dólar (USD)");
  });

  it("falls back to the raw code for unknown currencies", () => {
    expect(currencyLabel("XYZ")).toBe("XYZ");
  });
});
