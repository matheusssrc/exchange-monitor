import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import { useAllLatestRates } from "@/hooks/useAllLatestRates";
import { server } from "@/test/server";

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

const baseRate = {
  bid: "1.0000",
  ask: "1.1000",
  mid: "1.0500",
  fetched_at: "2026-05-27T12:00:00Z",
  provider_timestamp: "2026-05-27T11:59:58Z",
  provider_name: "awesomeapi",
};

describe("useAllLatestRates", () => {
  it("returns the latest rate for each pair", async () => {
    server.use(
      http.get("/api/rates/latest", ({ request }) => {
        const pair = new URL(request.url).searchParams.get("pair") ?? "";
        return HttpResponse.json({ ...baseRate, pair });
      }),
    );
    const { result } = renderHook(
      () => useAllLatestRates(["BRL-USD", "BRL-EUR"]),
      { wrapper },
    );
    await waitFor(() =>
      expect(result.current.every((e) => !e.isLoading)).toBe(true),
    );
    expect(result.current).toHaveLength(2);
    expect(result.current[0]?.data?.pair).toBe("BRL-USD");
    expect(result.current[1]?.data?.pair).toBe("BRL-EUR");
  });

  it("maps a 404 pair to null data", async () => {
    server.use(
      http.get("/api/rates/latest", () =>
        HttpResponse.json(
          { detail: { error: "rate_not_found", message: "none" } },
          { status: 404 },
        ),
      ),
    );
    const { result } = renderHook(() => useAllLatestRates(["BRL-ARS"]), {
      wrapper,
    });
    await waitFor(() => expect(result.current[0]?.isLoading).toBe(false));
    expect(result.current[0]?.data).toBeNull();
  });
});
