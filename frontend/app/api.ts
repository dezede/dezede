import { TQueryParams } from "./types";

/**
 * Canonical query-string serializer for the public/event APIs, shared by the
 * server (`djangoFetch`) and every client component. Mirrors DRF's expectations:
 * skips empty values (`null`/`undefined`/`""`), appends array values as repeated
 * params, and stringifies numbers. `extra` holds params the caller always wants
 * sent verbatim — typically `limit`/`offset`, where an `offset` of `0` must be
 * kept rather than dropped as falsy.
 */
export function buildQuery(
  params: TQueryParams,
  extra?: Record<string, string | number>,
): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === null || value === undefined || value === "") {
      continue;
    }
    if (Array.isArray(value)) {
      value.forEach((item) => search.append(key, item));
    } else {
      search.set(key, String(value));
    }
  }
  if (extra) {
    for (const [key, value] of Object.entries(extra)) {
      search.set(key, String(value));
    }
  }
  return search.toString();
}

/**
 * Same-origin JSON GET against the Next.js `/api/...` proxy, the client-side
 * counterpart to the server's `fetchPublicJson`. Sets the `Accept` header,
 * forwards an optional `AbortSignal` (so callers can cancel superseded
 * requests), throws on a non-2xx response, and returns the parsed body typed as
 * `T`. `AbortError` propagates unchanged so callers can distinguish a deliberate
 * cancellation from a real failure.
 */
export async function apiGet<T>(
  url: string,
  opts?: {
    params?: TQueryParams;
    extra?: Record<string, string | number>;
    signal?: AbortSignal;
  },
): Promise<T> {
  const query =
    opts?.params || opts?.extra
      ? buildQuery(opts.params ?? {}, opts.extra)
      : "";
  const response = await fetch(query ? `${url}?${query}` : url, {
    headers: { Accept: "application/json" },
    signal: opts?.signal,
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

/**
 * Same-origin JSON POST against the Next.js `/api/...` proxy, used for the few
 * state-changing public endpoints (the dossier exports). The browser forwards
 * the Django session cookie automatically; the backend's
 * `CsrfExemptSessionAuthentication` means no CSRF token is needed. On a non-2xx
 * response it throws an `ApiPostError` carrying the API's stable `code` and
 * `detail` so callers can localise the message themselves (falling back to the
 * French `detail`).
 */
export class ApiPostError extends Error {
  code?: string;
  status: number;
  constructor(status: number, detail?: string, code?: string) {
    super(detail || `HTTP ${status}`);
    this.name = "ApiPostError";
    this.status = status;
    this.code = code;
  }
}

export async function apiPost<T>(
  url: string,
  body?: unknown,
): Promise<T> {
  const response = await fetch(url, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = (await response.json().catch(() => null)) as
    | (T & { detail?: string; code?: string })
    | null;
  if (!response.ok) {
    throw new ApiPostError(response.status, data?.detail, data?.code);
  }
  return data as T;
}
