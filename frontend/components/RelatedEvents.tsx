import { getTranslations, getLocale } from "next-intl/server";
import { type Locale } from "@/i18n/config";
import { TYearlyCount, TSearchParams } from "@/app/types";
import { fetchEventsJson, eventFilterParams } from "@/app/events";
import DetailTable, { TDetailRow } from "./DetailTable";
import { countLabel } from "./entityChipRow";
import { YearlyCountsChips, sumYearlyCounts } from "./relatedEventsView";

/**
 * Builds the `DetailTable` row for an entity's events grouped by year, so it can
 * sit alongside the page's other attributes (ISNI, notes…): the label is the
 * total ("123 apparitions") and the value is a wrapping line of chips — first
 * "Toutes années" (the full list), then one chip per year, each badged with its
 * event count. Resolves to `null` when the entity has no events.
 */
export async function eventsRow(
  filter: TSearchParams,
  title?: string,
): Promise<TDetailRow | null> {
  const t = await getTranslations("events");
  const locale = (await getLocale()) as Locale;
  const resolvedTitle = title ?? t("eventsTitle");
  const yearlyCounts = await fetchEventsJson<TYearlyCount[]>(
    "/api/evenements/yearly_counts/",
    eventFilterParams(filter),
  );
  if (yearlyCounts.length === 0) {
    return null;
  }

  return {
    key: "evenements",
    label: countLabel(resolvedTitle, sumYearlyCounts(yearlyCounts)),
    content: (
      <YearlyCountsChips
        filter={filter}
        yearlyCounts={yearlyCounts}
        allYearsLabel={t("allYears")}
        locale={locale}
      />
    ),
  };
}

/**
 * Stand-alone events-by-year list as its own one-row `DetailTable`, used where
 * there is no surrounding attribute table to fold into (e.g. the source detail
 * page). Renders nothing when the entity has no events.
 */
export default async function RelatedEvents({
  filter,
  title,
}: {
  filter: TSearchParams;
  title?: string;
}) {
  const row = await eventsRow(filter, title);
  if (row === null) {
    return null;
  }
  return <DetailTable rows={[row]} />;
}
