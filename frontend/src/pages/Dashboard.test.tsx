import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it } from "vitest";

import { Dashboard } from "@/pages/Dashboard";
import { server } from "@/test/server";

const makeRate = (pair: string) => ({
  pair,
  bid: "5.1200",
  ask: "5.1210",
  mid: "5.1205",
  fetched_at: "2026-05-27T12:00:00Z",
  provider_timestamp: "2026-05-27T11:59:58Z",
  provider_name: "awesomeapi",
});

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("Dashboard", () => {
  beforeEach(() => {
    window.history.pushState(null, "", "/");
    server.use(
      http.get("/api/pairs", () =>
        HttpResponse.json([
          { pair: "BRL-USD", base: "BRL", quote: "USD" },
          { pair: "BRL-EUR", base: "BRL", quote: "EUR" },
          { pair: "USD-BRL", base: "USD", quote: "BRL" },
          { pair: "USD-EUR", base: "USD", quote: "EUR" },
        ]),
      ),
      http.get("/api/rates/latest", ({ request }) => {
        const pair = new URL(request.url).searchParams.get("pair") ?? "BRL-USD";
        return HttpResponse.json(makeRate(pair));
      }),
      http.get("/api/rates/history", () =>
        HttpResponse.json({
          pair: "BRL-USD",
          start: "2026-05-27T11:00:00Z",
          end: "2026-05-27T12:00:00Z",
          count: 1,
          items: [makeRate("BRL-USD")],
        }),
      ),
    );
  });

  it("shows only the selected base's pairs in the table", async () => {
    render(<Dashboard />, { wrapper });
    // "BRL → EUR" only appears as a table row (not in the chart title/select),
    // so waiting on it guarantees the table has rendered after data loads.
    await waitFor(() =>
      expect(screen.getByText("BRL → EUR")).toBeInTheDocument(),
    );
    expect(screen.getAllByText("BRL → USD").length).toBeGreaterThan(0);
    // USD-base pairs are filtered out while base is BRL.
    expect(screen.queryByText("USD → EUR")).not.toBeInTheDocument();
  });

  it("shows the current bid for resolved pairs", async () => {
    render(<Dashboard />, { wrapper });
    await waitFor(() =>
      expect(screen.getAllByText("5.1200").length).toBeGreaterThan(0),
    );
  });
});
