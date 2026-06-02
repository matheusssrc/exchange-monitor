import { useCallback, useSyncExternalStore } from "react";

function subscribe(callback: () => void): () => void {
  window.addEventListener("popstate", callback);
  return () => window.removeEventListener("popstate", callback);
}

function getSearch(): string {
  return window.location.search;
}

export function useUrlState(
  key: string,
  fallback: string,
): [string, (value: string) => void] {
  const search = useSyncExternalStore(subscribe, getSearch, getSearch);
  const value = new URLSearchParams(search).get(key) ?? fallback;

  const setValue = useCallback(
    (next: string) => {
      const params = new URLSearchParams(window.location.search);
      params.set(key, next);
      window.history.pushState(null, "", `?${params.toString()}`);
      window.dispatchEvent(new PopStateEvent("popstate"));
    },
    [key],
  );

  return [value, setValue];
}
