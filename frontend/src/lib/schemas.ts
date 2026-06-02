import { z } from "zod";

export const PairOutSchema = z.object({
  pair: z.string(),
  base: z.string(),
  quote: z.string(),
});

export const RateOutSchema = z.object({
  pair: z.string(),
  bid: z.string(),
  ask: z.string(),
  mid: z.string(),
  fetched_at: z.string(),
  provider_timestamp: z.string(),
  provider_name: z.string(),
});

export const HistoryPageSchema = z.object({
  pair: z.string(),
  start: z.string(),
  end: z.string(),
  count: z.number(),
  items: z.array(RateOutSchema),
});

export const ErrorOutSchema = z.object({
  error: z.string(),
  message: z.string(),
  details: z.record(z.string(), z.unknown()).nullish(),
});
