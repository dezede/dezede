"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { useTranslations } from "next-intl";
import { TEvent, TPaginated, TQueryParams } from "@/app/types";
import { apiGet } from "@/app/api";
import EventCard from "./EventCard";
import EventCardSkeleton from "./EventCardSkeleton";

/**
 * Appends further pages of events as the user scrolls, replicating the
 * el-pagination infinite scroll of the Django event list. The first page is
 * rendered on the server; this only fetches subsequent pages (same-origin, so
 * the session cookie is sent automatically).
 */
export default function EventInfiniteScroll({
  params,
  perPage,
  totalCount,
  startOffset,
  endpoint = "/api/evenements/",
}: {
  params: TQueryParams;
  perPage: number;
  totalCount: number;
  startOffset: number;
  endpoint?: string;
}) {
  const t = useTranslations("lists");
  const [events, setEvents] = useState<TEvent[]>([]);
  const [offset, setOffset] = useState(startOffset);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const sentinelRef = useRef<HTMLDivElement | null>(null);

  const loadedCount = startOffset + events.length;
  const hasMore = !error && loadedCount < totalCount;

  const loadMore = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<TPaginated<TEvent>>(endpoint, {
        params,
        extra: { limit: perPage, offset },
      });
      setEvents((previous) => [...previous, ...data.results]);
      setOffset((previous) => previous + perPage);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [params, perPage, offset, endpoint]);

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
      {},
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [hasMore, loading, loadMore]);

  return (
    <Stack spacing={2}>
      {events.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
      {hasMore ? (
        <>
          <Box ref={sentinelRef} aria-busy={loading} aria-label={t("loading")}>
            <EventCardSkeleton />
          </Box>
          <EventCardSkeleton />
          <EventCardSkeleton />
        </>
      ) : null}
      {error ? (
        <Typography color="error" role="alert">
          {t("loadEventsError")}
        </Typography>
      ) : null}
    </Stack>
  );
}
