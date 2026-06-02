import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { RatesTable, type RatesTableRow } from "@/components/RatesTable";

const rows: RatesTableRow[] = [
  {
    pair: "BRL-USD",
    bid: "5.1200",
    ask: "5.1210",
    fetchedAt: "2026-05-27T12:00:00Z",
  },
  { pair: "WEIRD", bid: null, ask: null, fetchedAt: null },
];

describe("RatesTable", () => {
  it("renders the pair as base → quote with bid/ask", () => {
    render(<RatesTable rows={rows} isLoading={false} selectedPair="BRL-USD" />);
    expect(screen.getByText("BRL → USD")).toBeInTheDocument();
    expect(screen.getByText("5.1200")).toBeInTheDocument();
  });

  it("falls back to the raw id when not a two-part pair", () => {
    render(<RatesTable rows={rows} isLoading={false} selectedPair="BRL-USD" />);
    expect(screen.getByText("WEIRD")).toBeInTheDocument();
  });

  it("shows an em dash for a pair with no rate yet", () => {
    render(<RatesTable rows={rows} isLoading={false} selectedPair="BRL-USD" />);
    expect(screen.getAllByText("—").length).toBeGreaterThanOrEqual(2);
  });

  it("calls onSelectPair when a row is clicked", async () => {
    const onSelectPair = vi.fn();
    render(
      <RatesTable
        rows={rows}
        isLoading={false}
        selectedPair="BRL-USD"
        onSelectPair={onSelectPair}
      />,
    );
    await userEvent.click(screen.getByText("WEIRD"));
    expect(onSelectPair).toHaveBeenCalledWith("WEIRD");
  });

  it("renders a loading state", () => {
    render(<RatesTable rows={[]} isLoading selectedPair="BRL-USD" />);
    expect(screen.getByRole("status", { name: "Loading" })).toBeInTheDocument();
  });
});
