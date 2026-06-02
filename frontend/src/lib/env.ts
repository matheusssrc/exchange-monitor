import { z } from "zod";

const EnvSchema = z.object({
  VITE_API_BASE_URL: z.string().min(1).default("/api"),
});

export const env = EnvSchema.parse({
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
});
