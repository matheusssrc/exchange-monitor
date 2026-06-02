import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import { usePairs } from "@/hooks/usePairs";
import { server } from "@/test/server";

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("usePairs", () => {
  it("loads pairs from the API", async () => {
    server.use(
      http.get("/api/pairs", () =>
        HttpResponse.json([{ pair: "USD-BRL", base: "USD", quote: "BRL" }]),
      ),
    );
    const { result } = renderHook(() => usePairs(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.[0]?.pair).toBe("USD-BRL");
  });
});
