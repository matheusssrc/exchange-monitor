import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { CurrencySelect } from "@/components/CurrencySelect";

const options = [
  { value: "BRL", label: "Real (BRL)" },
  { value: "USD", label: "Dólar (USD)" },
];

describe("CurrencySelect", () => {
  it("renders a labelled combobox trigger", () => {
    render(
      <CurrencySelect
        value="BRL"
        onChange={() => {}}
        options={options}
        ariaLabel="Moeda base"
      />,
    );
    expect(
      screen.getByRole("combobox", { name: "Moeda base" }),
    ).toBeInTheDocument();
  });
});
