import { z } from "zod";

/**
 * Safe Fetch Wrapper
 *
 * Wraps fetch calls with Zod schema validation to ensure data integrity.
 * If validation fails, it safely returns null instead of crashing the app.
 */
export async function safeFetch<T>(
  url: string,
  schema: z.ZodSchema<T>,
): Promise<T | null> {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      return null;
    }
    const json: unknown = await res.json();

    // 🛡️ The Guard: Validates data against your strict schemas
    const result = schema.safeParse(json);

    if (!result.success) {
      // "Smarter Problem Handling": Return null instead of crashing the app
      return null;
    }

    return result.data;
  } catch {
    return null;
  }
}
