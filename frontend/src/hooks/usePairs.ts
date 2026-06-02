import { useQuery } from "@tanstack/react-query";

import { fetchPairs } from "@/lib/api";

export function usePairs() {
  return useQuery({
    queryKey: ["pairs"],
    queryFn: fetchPairs,
    staleTime: Infinity,
  });
}
