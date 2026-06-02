import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";

import { useUrlState } from "@/hooks/useUrlState";

describe("useUrlState", () => {
  beforeEach(() => {
    window.history.pushState(null, "", "/");
  });

  it("returns the fallback when the key is absent", () => {
    const { result } = renderHook(() => useUrlState("pair", "USD-BRL"));
    expect(result.current[0]).toBe("USD-BRL");
  });

  it("reads an existing query param", () => {
    window.history.pushState(null, "", "/?pair=EUR-BRL");
    const { result } = renderHook(() => useUrlState("pair", "USD-BRL"));
    expect(result.current[0]).toBe("EUR-BRL");
  });

  it("updates the URL and the returned value", () => {
    const { result } = renderHook(() => useUrlState("range", "24h"));
    act(() => result.current[1]("7d"));
    expect(result.current[0]).toBe("7d");
    expect(window.location.search).toContain("range=7d");
  });
});
