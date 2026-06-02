import { z } from "zod";

import { env } from "@/lib/env";
import { HistoryPageSchema, PairOutSchema, RateOutSchema } from "@/lib/schemas";
import type { HistoryPage, PairOut, RateOut } from "@/types/api";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    path: string,
  ) {
    super(`API request failed (${status}): ${path}`);
    this.name = "ApiError";
  }
}

async function getJson(path: string): Promise<unknown> {
  const response = await fetch(`${env.VITE_API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new ApiError(response.status, path);
  }
  return response.json();
}

export async function fetchPairs(): Promise<PairOut[]> {
  const data = await getJson("/pairs");
  return z.array(PairOutSchema).parse(data);
}

export async function fetchLatestRate(pair: string): Promise<RateOut | null> {
  const path = `/rates/latest?pair=${encodeURIComponent(pair)}`;
  const response = await fetch(`${env.VITE_API_BASE_URL}${path}`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new ApiError(response.status, path);
  }
  return RateOutSchema.parse(await response.json());
}

export async function fetchRateHistory(
  pair: string,
  start: string,
  end: string,
  limit = 1000,
  offset = 0,
): Promise<HistoryPage> {
  const params = new URLSearchParams({
    pair,
    start_date: start,
    end_date: end,
    limit: String(limit),
    offset: String(offset),
  });
  const data = await getJson(`/rates/history?${params.toString()}`);
  return HistoryPageSchema.parse(data);
}
