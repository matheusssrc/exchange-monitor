import { useQuery } from "@tanstack/react-query";

import { fetchLatestRate } from "@/lib/api";

export function useLatestRate(pair: string) {
  return useQuery({
    queryKey: ["latest", pair],
    queryFn: () => fetchLatestRate(pair),
    refetchInterval: 30_000,
    staleTime: 0,
  });
}
