"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { TDossierKind } from "@/app/types";

type Counts = Partial<Record<TDossierKind, number>>;

export type DossierCountsStore = {
  // Start observing a card's element; when it nears the viewport its id is
  // queued for a (batched) fetch. Returns an unobserve cleanup.
  observe: (id: number, element: Element) => () => void;
  // Subscribe to just one dossier's counts (per-id, so a fetch response only
  // re-renders the cards it actually filled in — not every card on the page).
  subscribe: (id: number, onChange: () => void) => () => void;
  getSnapshot: (id: number) => Counts | undefined;
};

// How long to gather freshly-visible cards before firing the first request.
const BATCH_DEBOUNCE_MS = 400;
// Ids per request. Kept small so each request stays fast (the counts are
// computed live, ~15ms per dossier for busy ones): a fast scroll drains as
// several quick, pipelined requests rather than one slow ~1s call.
const MAX_BATCH = 20;

const NOOP_STORE: DossierCountsStore = {
  observe: () => () => {},
  subscribe: () => () => {},
  getSnapshot: () => undefined,
};

const Ctx = createContext<DossierCountsStore>(NOOP_STORE);

export function useDossierCounts() {
  return useContext(Ctx);
}

// Builds the mutable store once (via a lazy useState initialiser): mutations
// notify only the affected ids' listeners, so React never re-renders the whole
// card grid on a counts response.
function createStore(): DossierCountsStore {
  const counts = new Map<number, Counts>();
  const listeners = new Map<number, Set<() => void>>();
  // Ids seen (queued/fetched) so we never request one twice, and the elements
  // one shared IntersectionObserver watches.
  const seen = new Set<number>();
  const pending = new Set<number>();
  const idOf = new Map<Element, number>();
  let timer: ReturnType<typeof setTimeout> | null = null;
  let observer: IntersectionObserver | null = null;
  // At most one request in flight: the dev server serialises concurrent
  // requests (each then balloons to seconds and can hit proxy timeouts), so we
  // pipeline batches one after another instead of firing them all at once.
  let inFlight = false;

  const notify = (id: number) => {
    const set = listeners.get(id);
    if (set) set.forEach((cb) => cb());
  };

  const flush = () => {
    timer = null;
    if (inFlight) return;
    const ids = [...pending].slice(0, MAX_BATCH);
    for (const id of ids) pending.delete(id);
    if (ids.length === 0) return;
    inFlight = true;
    fetch(`/api/public/dossiers/counts/?ids=${ids.join(",")}`, {
      credentials: "same-origin",
    })
      .then((response) => (response.ok ? response.json() : {}))
      .then((data: Record<string, Counts>) => {
        for (const [id, kindCounts] of Object.entries(data)) {
          const numId = Number(id);
          counts.set(numId, kindCounts);
          notify(numId);
        }
      })
      .catch(() => {
        // Let a later scroll re-request these ids.
        for (const id of ids) seen.delete(id);
      })
      .finally(() => {
        inFlight = false;
        // Drain the next chunk right away (no debounce), still one at a time.
        if (pending.size > 0) timer = setTimeout(flush, 0);
      });
  };

  const enqueue = (id: number) => {
    if (seen.has(id)) return;
    seen.add(id);
    pending.add(id);
    if (timer === null && !inFlight)
      timer = setTimeout(flush, BATCH_DEBOUNCE_MS);
  };

  const getObserver = () => {
    if (observer) return observer;
    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue;
          const id = idOf.get(entry.target);
          if (id !== undefined) {
            enqueue(id);
            // One-shot: once queued, stop watching this card.
            observer!.unobserve(entry.target);
            idOf.delete(entry.target);
          }
        }
      },
      // Start fetching a little before the card is actually on screen.
      { rootMargin: "300px" },
    );
    return observer;
  };

  return {
    observe: (id, element) => {
      if (seen.has(id)) return () => {};
      idOf.set(element, id);
      getObserver().observe(element);
      return () => {
        idOf.delete(element);
        observer?.unobserve(element);
      };
    },
    subscribe: (id, onChange) => {
      let set = listeners.get(id);
      if (!set) {
        set = new Set();
        listeners.set(id, set);
      }
      set.add(onChange);
      return () => set!.delete(onChange);
    },
    getSnapshot: (id) => counts.get(id),
  };
}

export default function DossierCountsProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [store] = useState(createStore);
  return <Ctx.Provider value={store}>{children}</Ctx.Provider>;
}
