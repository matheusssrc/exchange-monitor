import type { z } from "zod";

import type {
  HistoryPageSchema,
  PairOutSchema,
  RateOutSchema,
} from "@/lib/schemas";

export type PairOut = z.infer<typeof PairOutSchema>;
export type RateOut = z.infer<typeof RateOutSchema>;
export type HistoryPage = z.infer<typeof HistoryPageSchema>;
