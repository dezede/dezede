// Server-only: importing next/headers makes this module unusable from client
// components (it will fail the build if imported client-side).
import { cookies } from "next/headers";
import { notFound } from "next/navigation";
import { djangoFetch, EVENT_FILTER_PARAMS } from "./utils";
import { TQueryParams, TSearchParams } from "./types";

/**
 * Server-side fetch for the event API that forwards the visitor's Django
 * session cookie, so server-rendered results respect the logged-in user
 * (private events, `is_authenticated`). The browser reaches `/api/...` on the
 * same origin, so client-side fetches send the cookie automatically.
 */
export async function fetchEventsJson<T>(
  relativeUrl: string,
  params?: TQueryParams,
): Promise<T> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();
  const response = await djangoFetch(relativeUrl, params, {
    headers: cookieHeader ? { Cookie: cookieHeader } : {},
  });
  if (!response.ok) {
    notFound();
  }
  return (await response.json()) as T;
}

/**
 * Generic server-side fetch for the public catalogue API (works, persons,
 * places…). Identical cookie-forwarding behaviour as {@link fetchEventsJson};
 * named separately for clarity at call sites.
 */
export const fetchPublicJson = fetchEventsJson;

/** Picks the listed keys out of the page's searchParams (dropping empties). */
function pickParams(
  searchParams: TSearchParams,
  keys: readonly string[],
): TQueryParams {
  const params: TQueryParams = {};
  for (const key of keys) {
    const value = searchParams[key];
    if (value !== undefined) {
      params[key] = value;
    }
  }
  return params;
}

/** Picks the event filter params out of the page's searchParams. */
export function eventFilterParams(searchParams: TSearchParams): TQueryParams {
  return pickParams(searchParams, EVENT_FILTER_PARAMS);
}

// Query params understood by the dossier de sources list (free text, content
// type, century) plus the date sort. `type` is the per-group key handled by the
// sources action, so it is forwarded too.
const SOURCE_FILTER_PARAMS = [
  "q",
  "icons",
  "ancrage",
  "order_by",
  "type",
] as const;

/** Picks the dossier de sources filter params out of the page's searchParams. */
export function sourceFilterParams(searchParams: TSearchParams): TQueryParams {
  return pickParams(searchParams, SOURCE_FILTER_PARAMS);
}

// Query params understood by the dossier d'œuvres list (free text, genre,
// author) plus the name/premiere sort.
const WORK_FILTER_PARAMS = [
  "q",
  "genre",
  "individu",
  "ensemble",
  "order_by",
] as const;

/** Picks the dossier d'œuvres filter params out of the page's searchParams. */
export function workFilterParams(searchParams: TSearchParams): TQueryParams {
  return pickParams(searchParams, WORK_FILTER_PARAMS);
}
