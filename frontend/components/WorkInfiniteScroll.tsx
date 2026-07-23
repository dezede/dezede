"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Divider from "@mui/material/Divider";
import CircularProgress from "@mui/material/CircularProgress";
import Typography from "@mui/material/Typography";
import { useTranslations } from "next-intl";
import { TDossierWork, TPaginated } from "@/app/types";
import WorkListItem from "./WorkListItem";

/**
 * Appends further pages of a dossier d'œuvres' works as the user scrolls. The
 * first page is server-rendered by {@link DossierData}; this fetches the rest
 * same-origin. Mirrors {@link EntityInfiniteScroll}, but renders the rich
 * {@link WorkListItem} rows and threads the `order_by` sort param.
 *
 * `params` carries the active list filters (q/genre/individu/ensemble) merged
 * into every request, so appended pages stay consistent with the filter bar.
 */
export default function WorkInfiniteScroll({
  apiList,
  orderBy,
  perPage,
  totalCount,
  startOffset,
  params: extraParams,
}: {
  apiList: string;
  orderBy: string;
  perPage: number;
  totalCount: number;
  startOffset: number;
  params?: Record<string, string>;
}) {
  const t = useTranslations("lists");
  const [items, setItems] = useState<TDossierWork[]>([]);
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
      if (orderBy) {
        params.set("order_by", orderBy);
      }
      params.set("limit", perPage.toString());
      params.set("offset", offset.toString());
      const response = await fetch(`${apiList}?${params.toString()}`, {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data: TPaginated<TDossierWork> = await response.json();
      setItems((previous) => [...previous, ...data.results]);
      setOffset((previous) => previous + perPage);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [apiList, orderBy, perPage, offset, extraParams]);

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
      {items.length > 0 ? (
        <Stack spacing={2}>
          {items.map((work) => (
            // A divider above each appended item connects it to the
            // server-rendered first page (and to the item before it).
            <Box key={`${work.meta.type}-${work.id}`}>
              <Divider sx={{ mb: 2 }} />
              <WorkListItem work={work} />
            </Box>
          ))}
        </Stack>
      ) : null}
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
