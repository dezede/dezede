import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { getTranslations } from "next-intl/server";
import { TEvent, TPaginated, TSearchParams } from "@/app/types";
import { fetchEventsJson, eventFilterParams } from "@/app/events";
import EventCard from "./EventCard";
import EventInfiniteScroll from "./EventInfiniteScroll";
import EventOrderSelect from "./EventOrderSelect";
import EventExportButton from "./EventExportButton";
import Empty from "./Empty";

export const EVENTS_PER_PAGE = 10;

/**
 * Server-rendered first page of the (filtered) event list, handing off to a
 * client infinite-scroll loader for the rest.
 */
export default async function EventList({
  searchParams,
  endpoint = "/api/evenements/",
  isAuthenticated = false,
}: {
  searchParams: TSearchParams;
  endpoint?: string;
  isAuthenticated?: boolean;
}) {
  const t = await getTranslations("events");
  const params = eventFilterParams(searchParams);
  const data = await fetchEventsJson<TPaginated<TEvent>>(endpoint, {
    ...params,
    limit: EVENTS_PER_PAGE,
    offset: 0,
  });

  if (data.count === 0) {
    return <Empty>{t("noEventsForCriteria")}</Empty>;
  }

  return (
    <Stack spacing={2}>
      <Stack
        direction="row"
        spacing={2}
        useFlexGap
        sx={{
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
        }}
      >
        <Typography
          variant="subtitle1"
          sx={{ fontWeight: 500 }}
          role="status"
          aria-live="polite"
          aria-atomic="true"
        >
          {t("eventCount", { count: data.count })}
        </Typography>
        <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
          <EventExportButton isAuthenticated={isAuthenticated} />
          <EventOrderSelect />
        </Stack>
      </Stack>
      <Stack spacing={2}>
        {data.results.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </Stack>
      <EventInfiniteScroll
        endpoint={endpoint}
        params={params}
        perPage={EVENTS_PER_PAGE}
        totalCount={data.count}
        startOffset={EVENTS_PER_PAGE}
      />
    </Stack>
  );
}
