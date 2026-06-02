import { describe, expect, it } from "vitest";

import { env } from "@/lib/env";

describe("env", () => {
  it("defaults VITE_API_BASE_URL to /api when unset", () => {
    expect(env.VITE_API_BASE_URL).toBe("/api");
  });
});
