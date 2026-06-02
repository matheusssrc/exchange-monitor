import "@testing-library/jest-dom/vitest";

import { afterAll, afterEach, beforeAll, vi } from "vitest";

import { server } from "./server";

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

class ResizeObserverStub {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

vi.stubGlobal("ResizeObserver", ResizeObserverStub);
