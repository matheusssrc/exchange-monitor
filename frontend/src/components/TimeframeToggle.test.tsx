import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { TimeframeToggle } from "@/components/TimeframeToggle";

describe("TimeframeToggle", () => {
  it("renders all timeframes", () => {
    render(<TimeframeToggle value="1m" onChange={() => {}} />);
    expect(screen.getByRole("radio", { name: "1m" })).toBeInTheDocument();
    expect(screen.getByRole("radio", { name: "15m" })).toBeInTheDocument();
  });

  it("calls onChange when a timeframe is clicked", async () => {
    const onChange = vi.fn();
    render(<TimeframeToggle value="1m" onChange={onChange} />);
    await userEvent.click(screen.getByRole("radio", { name: "5m" }));
    expect(onChange).toHaveBeenCalledWith("5m");
  });
});
