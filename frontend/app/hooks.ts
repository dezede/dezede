import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import { TQueryParams, TSearchParamsUpdate } from "./types";
import { apiGet, buildQuery } from "./api";

export function useDebounceCallback<T>(
  callback: (...args: T[]) => void,
  debounceTimeout: number,
) {
  // The timer lives in a ref, not state, so scheduling a call never re-renders
  // the caller (typing in a search box would otherwise re-render on every
  // keystroke). The latest callback is kept in a ref too, so the returned
  // function stays stable regardless of inline callbacks.
  const timeoutId = useRef<ReturnType<typeof setTimeout>>(undefined);
  const callbackRef = useRef(callback);
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Cancels a pending timeout on unmount.
  useEffect(() => {
    return () => clearTimeout(timeoutId.current);
  }, []);

  return useCallback(
    (...args: T[]) => {
      clearTimeout(timeoutId.current);
      timeoutId.current = setTimeout(
        () => callbackRef.current(...args),
        debounceTimeout,
      );
    },
    [debounceTimeout],
  );
}

export function useUpdateSearchParams() {
  const searchParams = useSearchParams();
  const router = useRouter();
  return {
    updateSearchParams: useCallback(
      (paramsUpdate: TSearchParamsUpdate, options?: { shallow?: boolean }) => {
        const updatedSearchParams = new URLSearchParams(searchParams);
        Object.entries(paramsUpdate).forEach(([param, value]) => {
          if (typeof value === "number") {
            value = value.toString();
          }
          if (value === null || value === undefined || value === "") {
            updatedSearchParams.delete(param);
          } else {
            updatedSearchParams.set(param, value);
          }
        });
        // Keep the current URL hash: the dossier detail page mirrors its active
        // tab into the hash (e.g. `#donnees`, see DossierTabs), and dropping it
        // here would fire a `hashchange` that bounces the user back to the first
        // tab when they change a filter. No-op where there is no hash.
        const hash = typeof window === "undefined" ? "" : window.location.hash;
        const url = `?${updatedSearchParams.toString()}${hash}`;
        if (options?.shallow) {
          // Pages whose state is handled entirely client-side (e.g. the
          // virtualised autorité tables) only need the URL kept in sync for
          // sharing/reload. Use the native History API so the update never
          // triggers a Next.js navigation or RSC refetch (mirrors
          // EventViewTabs/HashTabs); useSearchParams still updates, so the
          // subscribed client components re-render and refetch.
          window.history.replaceState(null, "", url);
        } else {
          router.replace(url, { scroll: false });
        }
      },
      [router, searchParams],
    ),
    searchParams,
  };
}

/**
 * Windowed, lazily-loaded data source for react-virtuoso lists/tables. Holds a
 * sparse `rows` array whose length is the total result `count`, so the
 * virtualised scroll area spans the whole result set from the first paint;
 * entries stay `undefined` until the `CHUNK_SIZE`-sized chunk covering them is
 * scrolled into view and fetched (each chunk at most once, a failed one retried
 * on a later scroll). Every request is stamped with an epoch so responses for a
 * superseded `params`/`endpoint` are discarded instead of polluting the current
 * list. Extracted from EntityVirtualTable and shared with RelatedEntitiesPanel.
 *
 * Two modes:
 * - dynamic total (no `initialCount`): the row count is read from each response,
 *   and the list resets (re-sizes to 0, refetches chunk 0) whenever `params`
 *   change — used by the autorité tables, whose sort/search/filters vary.
 * - known total (`initialCount` given): the array is sized up front and the
 *   count never changes — used by a related-objects panel, whose collection
 *   total ships with the page, so the panel shows its real height immediately.
 */
export function useChunkedRows<T>({
  endpoint,
  params,
  chunkSize,
  initialCount,
}: {
  endpoint: string;
  params?: TQueryParams;
  chunkSize: number;
  initialCount?: number;
}): {
  rows: (T | undefined)[];
  count: number;
  loading: boolean;
  loadRange: (range: { startIndex: number; endIndex: number }) => void;
} {
  const [rows, setRows] = useState<(T | undefined)[]>(
    () => new Array<T | undefined>(initialCount ?? 0),
  );
  const [count, setCount] = useState(initialCount ?? 0);
  const [loading, setLoading] = useState(false);

  const requestedChunks = useRef<Set<number>>(new Set());
  const inFlight = useRef(0);
  const epoch = useRef(0);

  // Latest fetch inputs, read inside the (referentially stable) loaders so a
  // params change doesn't churn their identity — the reset effect drives
  // refetches instead. `dynamicCount` selects the mode above.
  const dynamicCount = initialCount === undefined;
  const fetchArgs = useRef({ endpoint, params, chunkSize, dynamicCount });
  fetchArgs.current = { endpoint, params, chunkSize, dynamicCount };

  // Stable string identity of the server query; changing it resets the list.
  const paramsKey = buildQuery(params ?? {});

  const loadChunk = useCallback((chunkIndex: number) => {
    if (requestedChunks.current.has(chunkIndex)) {
      return;
    }
    requestedChunks.current.add(chunkIndex);
    const args = fetchArgs.current;
    const currentEpoch = epoch.current;
    const offset = chunkIndex * args.chunkSize;
    inFlight.current += 1;
    setLoading(true);
    apiGet<{ results?: T[]; count?: number }>(args.endpoint, {
      params: args.params,
      extra: { limit: args.chunkSize, offset },
    })
      .then((data) => {
        if (epoch.current !== currentEpoch) {
          return;
        }
        const results = data.results ?? [];
        const responseCount =
          typeof data.count === "number" ? data.count : undefined;
        setRows((previous) => {
          const targetLength = Math.max(
            previous.length,
            responseCount ?? 0,
            offset + results.length,
          );
          const next = new Array<T | undefined>(targetLength);
          for (let i = 0; i < previous.length; i += 1) {
            next[i] = previous[i];
          }
          for (let i = 0; i < results.length; i += 1) {
            next[offset + i] = results[i];
          }
          return next;
        });
        if (args.dynamicCount && responseCount !== undefined) {
          setCount(responseCount);
        }
      })
      .catch(() => {
        // Let a later scroll retry this chunk.
        requestedChunks.current.delete(chunkIndex);
      })
      .finally(() => {
        if (epoch.current !== currentEpoch) {
          return;
        }
        inFlight.current -= 1;
        if (inFlight.current === 0) {
          setLoading(false);
        }
      });
  }, []);

  // Reset whenever the endpoint or the query content changes: bump the epoch (so
  // in-flight responses are dropped), clear the requested-chunk record, re-seed
  // the array, and fetch chunk 0 — which, in dynamic mode, brings back the new
  // total so the scroll area resizes to the new result set.
  useEffect(() => {
    epoch.current += 1;
    requestedChunks.current = new Set();
    inFlight.current = 0;
    if (dynamicCount) {
      setRows([]);
      setCount(0);
    } else {
      setRows(new Array<T | undefined>(initialCount ?? 0));
      setCount(initialCount ?? 0);
    }
    loadChunk(0);
    // initialCount is stable in known-total mode; loadChunk is stable.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpoint, paramsKey]);

  // Request every chunk overlapping the visible range. Debounced so a fast
  // scroll doesn't fire a request for every chunk that briefly flies past.
  const loadVisibleChunks = useCallback(
    (range: { startIndex: number; endIndex: number }) => {
      const firstChunk = Math.floor(range.startIndex / chunkSize);
      const lastChunk = Math.floor(range.endIndex / chunkSize);
      for (let chunk = firstChunk; chunk <= lastChunk; chunk += 1) {
        loadChunk(chunk);
      }
    },
    [chunkSize, loadChunk],
  );
  const loadRange = useDebounceCallback(loadVisibleChunks, 200);

  return { rows, count, loading, loadRange };
}

/**
 * Debounced, self-cancelling type-ahead search. `search(query)` enters the
 * loading state synchronously (so the UI shows a spinner during the debounce
 * gap rather than a stale "no results"), then — after `debounceMs` of quiet —
 * runs `fetcher` with a fresh `AbortSignal`, aborting any request still in
 * flight so a slower earlier response can't land after a faster later one and
 * overwrite the results. Queries shorter than `minLength` (after trimming) clear
 * the results without fetching; `reset()` clears and cancels. Extracted from the
 * abort-ref + debounce boilerplate repeated across the navbar and filter search
 * boxes.
 */
export function useAsyncSearch<T>(
  fetcher: (query: string, signal: AbortSignal) => Promise<T[]>,
  opts?: { debounceMs?: number; minLength?: number },
): {
  results: T[];
  loading: boolean;
  search: (query: string) => void;
  reset: () => void;
} {
  const { debounceMs = 250, minLength = 1 } = opts ?? {};
  const [results, setResults] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);

  // Holds the in-flight request so a new keystroke can abort the previous one.
  const abortRef = useRef<AbortController | null>(null);
  // The latest fetcher, kept in a ref so the debounced runner stays stable even
  // when the caller passes an inline closure.
  const fetcherRef = useRef(fetcher);
  useEffect(() => {
    fetcherRef.current = fetcher;
  }, [fetcher]);

  const run = useDebounceCallback((query: string) => {
    const controller = new AbortController();
    abortRef.current = controller;
    fetcherRef
      .current(query, controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) {
          setResults(data);
        }
      })
      .catch(() => {
        // An abort rejects here too; only clear for a genuine failure so a
        // superseded request never blanks the newer one's results.
        if (!controller.signal.aborted) {
          setResults([]);
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });
  }, debounceMs);

  const search = useCallback(
    (query: string) => {
      abortRef.current?.abort();
      if (query.trim().length < minLength) {
        setResults([]);
        setLoading(false);
        return;
      }
      setLoading(true);
      run(query);
    },
    [run, minLength],
  );

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setResults([]);
    setLoading(false);
  }, []);

  return { results, loading, search, reset };
}
