"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { useTranslations } from "next-intl";
import { TSource, TPaginated } from "@/app/types";
import SourceList from "./SourceList";

/**
 * Appends further pages of a dossier de sources' sources as the user scrolls.
 * The first page is server-rendered by {@link DossierData}; this fetches the
 * rest same-origin. Mirrors {@link WorkInfiniteScroll}, but renders the rows
 * through the shared {@link SourceList} (icon + title + link).
 *
 * `params` carries extra query params merged into every request — used to scope
 * the scroll to a single source-type group (`{ type: "<id>" }`).
 */
export default function SourceInfiniteScroll({
  apiList,
  perPage,
  totalCount,
  startOffset,
  params: extraParams,
  modal = false,
}: {
  apiList: string;
  perPage: number;
  totalCount: number;
  startOffset: number;
  params?: Record<string, string>;
  modal?: boolean;
}) {
  const t = useTranslations("lists");
  const [items, setItems] = useState<TSource[]>([]);
  const [offset, setOffset] = useState(startOffset);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const loadedCount = startOffset + items.length;
  const hasMore = !error && loadedCount < totalCount;

  const loadMore = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams(extraParams);
      params.set("limit", perPage.toString());
      params.set("offset", offset.toString());
      const response = await fetch(`${apiList}?${params.toString()}`, {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data: TPaginated<TSource> = await response.json();
      setItems((previous) => [...previous, ...data.results]);
      setOffset((previous) => previous + perPage);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [apiList, perPage, offset, extraParams]);

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (sentinel === null || !hasMore || loading) {
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMore();
        }
      },
      { rootMargin: "200px" },
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loading, loadMore]);

  return (
    <>
      {items.length > 0 ? <SourceList sources={items} modal={modal} /> : null}
      <Box
        ref={sentinelRef}
        sx={{ display: "flex", justifyContent: "center", py: 2, minHeight: 8 }}
      >
        {loading ? <CircularProgress aria-label={t("loading")} /> : null}
        {error ? (
          <Typography color="error" role="alert">
            {t("loadMoreError")}
          </Typography>
        ) : null}
      </Box>
    </>
  );
}
