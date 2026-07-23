import { Suspense } from "react";
import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { TAsyncSearchParams, TEventFacets } from "@/app/types";
import { fetchEventsJson, eventFilterParams } from "@/app/events";
import EventFilterForm from "@/components/EventFilterForm";
import EventList, { EVENTS_PER_PAGE } from "@/components/EventList";
import EventViewTabs from "@/components/EventViewTabs";
import EventCardSkeleton from "@/components/EventCardSkeleton";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return {
    title: t("pages.titleTemplate", { name: t("pages.evenements.listTitle") }),
    description: t("pages.evenements.listDescription"),
  };
}

export default async function EvenementsPage({
  searchParams,
}: {
  searchParams: TAsyncSearchParams;
}) {
  const t = await getTranslations("pages");
  const resolvedSearchParams = await searchParams;
  const params = eventFilterParams(resolvedSearchParams);
  const facets = await fetchEventsJson<TEventFacets>(
    "/api/evenements/facets/",
    params,
  );
  const listKey = JSON.stringify(params);

  const listNode = (
    <Suspense
      key={listKey}
      fallback={
        <Stack spacing={2}>
          {[...Array(EVENTS_PER_PAGE).keys()].map((index) => (
            <EventCardSkeleton key={index} />
          ))}
        </Stack>
      }
    >
      <EventList
        searchParams={resolvedSearchParams}
        isAuthenticated={facets.is_authenticated}
      />
    </Suspense>
  );

  return (
    <Container>
      <Stack spacing={3}>
        <Typography variant="h1">{t("evenements.listTitle")}</Typography>
        {/* Sticky filter bar: tucks flush under the (static) AppBar while the
            list/map scroll underneath. top is -32 to negate the scrollable
            <main>'s py: 4 (32px) — sticky insets its stick point by the scroll
            container's top padding, so top: 0 would pin 32px too low. The opaque
            background + high z-index keep the Leaflet map and event cards from
            showing through. */}
        <Box
          sx={{
            position: "sticky",
            top: -32,
            // theme.zIndex.appBar; a literal because an sx callback cannot be
            // passed from this server component to the (client) Box.
            zIndex: 1100,
            bgcolor: "background.default",
          }}
        >
          <EventFilterForm facets={facets} />
        </Box>
        {facets.is_authenticated ? (
          <EventViewTabs list={listNode} />
        ) : (
          listNode
        )}
      </Stack>
    </Container>
  );
}
