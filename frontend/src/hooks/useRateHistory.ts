import { useQuery } from "@tanstack/react-query";

import { fetchRateHistory } from "@/lib/api";
import { historyWindow } from "@/lib/ranges";

export function useRateHistory(pair: string) {
  return useQuery({
    queryKey: ["history", pair],
    queryFn: () => {
      const { start, end } = historyWindow();
      return fetchRateHistory(pair, start, end, 1000);
    },
    refetchInterval: 30_000,
    staleTime: 0,
  });
}
