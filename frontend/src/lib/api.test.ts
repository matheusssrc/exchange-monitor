import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { fetchLatestRate, fetchPairs, fetchRateHistory } from "@/lib/api";
import { server } from "@/test/server";

const rate = {
  pair: "USD-BRL",
  bid: "5.1200",
  ask: "5.1210",
  mid: "5.1205",
  fetched_at: "2026-05-27T12:00:00Z",
  provider_timestamp: "2026-05-27T11:59:58Z",
  provider_name: "awesomeapi",
};

describe("fetchPairs", () => {
  it("returns parsed pairs", async () => {
    server.use(
      http.get("/api/pairs", () =>
        HttpResponse.json([{ pair: "USD-BRL", base: "USD", quote: "BRL" }]),
      ),
    );
    const pairs = await fetchPairs();
    expect(pairs).toHaveLength(1);
    expect(pairs[0]?.base).toBe("USD");
  });
});

describe("fetchLatestRate", () => {
  it("returns the rate on 200", async () => {
    server.use(http.get("/api/rates/latest", () => HttpResponse.json(rate)));
    const result = await fetchLatestRate("USD-BRL");
    expect(result?.mid).toBe("5.1205");
  });

  it("returns null on 404", async () => {
    server.use(
      http.get("/api/rates/latest", () =>
        HttpResponse.json(
          { detail: { error: "rate_not_found", message: "none" } },
          { status: 404 },
        ),
      ),
    );
    expect(await fetchLatestRate("USD-BRL")).toBeNull();
  });

  it("throws when the payload fails schema validation", async () => {
    server.use(
      http.get("/api/rates/latest", () => HttpResponse.json({ pair: "USD-BRL" })),
    );
    await expect(fetchLatestRate("USD-BRL")).rejects.toThrow();
  });
});

describe("fetchRateHistory", () => {
  it("returns a parsed history page", async () => {
    server.use(
      http.get("/api/rates/history", () =>
        HttpResponse.json({
          pair: "USD-BRL",
          start: "2026-05-27T00:00:00Z",
          end: "2026-05-27T23:59:59Z",
          count: 1,
          items: [rate],
        }),
      ),
    );
    const page = await fetchRateHistory(
      "USD-BRL",
      "2026-05-27T00:00:00Z",
      "2026-05-27T23:59:59Z",
    );
    expect(page.count).toBe(1);
  });
});
