/**
 * Minimal typed fetcher used by catalog hooks.
 * Converts a params object to query-string, filters empty values,
 * and returns parsed JSON.
 */
export async function fetcher<T = unknown>(
  url: string,
  params?: Record<string, string | number | boolean | undefined>,
): Promise<T> {
  let fullUrl = url;

  if (params) {
    const qs = Object.entries(params)
      .filter(([, v]) => v !== undefined && v !== '' && v !== null)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
      .join('&');

    if (qs) {
      fullUrl = `${url}?${qs}`;
    }
  }

  const res = await fetch(fullUrl, {
    headers: { Accept: 'application/json' },
  });

  if (!res.ok) {
    throw new Error(`Fetch error ${res.status}: ${res.statusText} — ${fullUrl}`);
  }

  return res.json() as Promise<T>;
}
