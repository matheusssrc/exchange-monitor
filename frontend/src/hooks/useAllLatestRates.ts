import { useQueries } from "@tanstack/react-query";

import { fetchLatestRate } from "@/lib/api";
import type { RateOut } from "@/types/api";

export interface LatestRateEntry {
  pair: string;
  data: RateOut | null;
  isLoading: boolean;
}

export function useAllLatestRates(pairs: string[]): LatestRateEntry[] {
  const results = useQueries({
    queries: pairs.map((pair) => ({
      queryKey: ["latest", pair],
      queryFn: () => fetchLatestRate(pair),
      refetchInterval: 30_000,
      staleTime: 0,
    })),
  });

  return pairs.map((pair, index) => ({
    pair,
    data: results[index]?.data ?? null,
    isLoading: results[index]?.isLoading ?? false,
  }));
}
