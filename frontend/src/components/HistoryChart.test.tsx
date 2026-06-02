import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { HistoryChart } from "@/components/HistoryChart";
import type { Candle } from "@/lib/ohlc";

const candles: Candle[] = [
  { time: Date.parse("2026-06-01T12:00:00Z"), open: 5.0, high: 5.2, low: 4.9, close: 5.1 },
  { time: Date.parse("2026-06-01T12:01:00Z"), open: 5.1, high: 5.3, low: 5.0, close: 5.05 },
];

describe("HistoryChart", () => {
  it("shows an empty message when there are no candles", () => {
    render(<HistoryChart candles={[]} isLoading={false} />);
    expect(screen.getByText(/sem dados/i)).toBeInTheDocument();
  });

  it("renders a chart container when candles are present", () => {
    const { container } = render(<HistoryChart candles={candles} isLoading={false} />);
    expect(container.querySelector(".recharts-responsive-container")).not.toBeNull();
  });

  it("shows a loading state", () => {
    render(<HistoryChart candles={[]} isLoading />);
    expect(screen.getByRole("status", { name: "Loading" })).toBeInTheDocument();
  });
});
