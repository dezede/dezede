"use client";

import { useEffect, useState } from "react";
import { useTranslations, useLocale } from "next-intl";
import { type Locale } from "@/i18n/config";
import { apiGet } from "@/app/api";
import { TYearlyCount } from "@/app/types";
import DetailTable from "./DetailTable";
import { countLabel } from "./entityChipRow";
import { YearlyCountsChips, sumYearlyCounts } from "./relatedEventsView";

/**
 * Client counterpart of the server `RelatedEvents`, used inside the source
 * popup (`SourceModal`), where the surrounding tree is a Client Component and
 * the server-only `fetchEventsJson` is unavailable. Fetches a source's events
 * grouped by year through the same-origin `/api/...` proxy and renders the
 * identical events-by-year row. Renders nothing while loading or when the
 * source has no events.
 */
export default function RelatedEventsClient({
  sourcePk,
  title,
}: {
  sourcePk: string;
  title?: string;
}) {
  const t = useTranslations("events");
  const locale = useLocale() as Locale;
  const [yearlyCounts, setYearlyCounts] = useState<TYearlyCount[] | null>(null);

  useEffect(() => {
    let cancelled = false;
    const filter = { source: `|${sourcePk}|` };
    const load = async () => {
      try {
        const data = await apiGet<TYearlyCount[]>(
          "/api/evenements/yearly_counts/",
          { params: filter },
        );
        if (!cancelled) {
          setYearlyCounts(data);
        }
      } catch {
        if (!cancelled) {
          setYearlyCounts([]);
        }
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, [sourcePk]);

  if (yearlyCounts === null || yearlyCounts.length === 0) {
    return null;
  }

  const filter = { source: `|${sourcePk}|` };
  return (
    <DetailTable
      rows={[
        {
          key: "evenements",
          label: countLabel(
            title ?? t("eventsTitle"),
            sumYearlyCounts(yearlyCounts),
          ),
          content: (
            <YearlyCountsChips
              filter={filter}
              yearlyCounts={yearlyCounts}
              allYearsLabel={t("allYears")}
              locale={locale}
            />
          ),
        },
      ]}
    />
  );
}
