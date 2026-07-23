import React from "react";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import { type Locale } from "@/i18n/config";
import { TSearchParams, TYearlyCount } from "@/app/types";
import { EVENTS_BASE } from "@/app/constants";
import OurLink from "./OurLink";

// Presentational, client-safe pieces of the events-by-year list, shared between
// the server `RelatedEvents` (rendered at request time) and the client
// `RelatedEventsClient` (fetched on demand inside the source popup). Neither
// `eventsHref` nor the chips touch server-only APIs, so this module can be
// imported from either side of the client boundary.

/**
 * Builds an events-page URL carrying the entity's filter (e.g. `individu=|12|`),
 * optionally narrowed to a single civil year — mirroring the links in the
 * Django autorité listing (`routines/evenement_list_def.html`).
 */
export function eventsHref(filter: TSearchParams, year?: number): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(filter)) {
    if (value === undefined) {
      continue;
    }
    for (const item of Array.isArray(value) ? value : [value]) {
      search.append(key, item);
    }
  }
  if (year !== undefined) {
    search.set("dates_0", String(year));
    search.set("dates_1", String(year));
  }
  return `${EVENTS_BASE}?${search.toString()}`;
}

/**
 * A clickable chip carrying a label and its event count in a small contrasting
 * bubble — e.g. "Toutes années (9)" or "1923 (2)" — used to list an entity's
 * events by year.
 */
function YearChip({
  href,
  label,
  count,
  locale,
}: {
  href: string;
  label: React.ReactNode;
  count: number;
  locale: Locale;
}) {
  return (
    <Chip
      component={OurLink}
      href={href}
      clickable
      size="small"
      label={
        <Box
          component="span"
          sx={{ display: "inline-flex", alignItems: "baseline", gap: 0.5 }}
        >
          {label}
          <Box
            component="span"
            sx={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              bgcolor: "primary.main",
              color: "primary.contrastText",
              borderRadius: "999px",
              px: 0.5,
              minWidth: "1rem",
              height: "1rem",
              fontSize: "0.6875rem",
              lineHeight: 1,
              fontWeight: 600,
            }}
          >
            {count.toLocaleString(locale)}
          </Box>
        </Box>
      }
    />
  );
}

export function sumYearlyCounts(yearlyCounts: TYearlyCount[]): number {
  return yearlyCounts.reduce((sum, { count }) => sum + count, 0);
}

/**
 * The wrapping line of year chips: first "Toutes années" (the full list), then
 * one chip per year, each badged with its event count.
 */
export function YearlyCountsChips({
  filter,
  yearlyCounts,
  allYearsLabel,
  locale,
}: {
  filter: TSearchParams;
  yearlyCounts: TYearlyCount[];
  allYearsLabel: string;
  locale: Locale;
}) {
  return (
    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
      <YearChip
        href={eventsHref(filter)}
        label={allYearsLabel}
        count={sumYearlyCounts(yearlyCounts)}
        locale={locale}
      />
      {yearlyCounts.map(({ year, count }) => (
        <YearChip
          key={year}
          href={eventsHref(filter, year)}
          label={year}
          count={count}
          locale={locale}
        />
      ))}
    </Box>
  );
}
