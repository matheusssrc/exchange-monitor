const ARROW = "→";

const CURRENCY_NAMES: Record<string, string> = {
  BRL: "Real (BRL)",
  USD: "Dólar (USD)",
  EUR: "Euro (EUR)",
  ARS: "Peso Argentino (ARS)",
  UYU: "Peso Uruguaio (UYU)",
};

/** Friendly name for a single currency code; falls back to the raw code. */
export function currencyLabel(code: string): string {
  return CURRENCY_NAMES[code] ?? code;
}

/**
 * Formats a raw API pair id ("BASE-QUOTE") as a directional label
 * ("BASE → QUOTE"), making clear which currency is quoted against which.
 * Falls back to the raw id when it is not a two-part hyphenated pair.
 */
export function pairLabel(pair: string): string {
  const [base, quote] = pair.split("-");
  if (!base || !quote || pair.split("-").length !== 2) {
    return pair;
  }
  return `${base} ${ARROW} ${quote}`;
}
