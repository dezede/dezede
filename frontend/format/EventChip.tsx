import { TRelatedEvent } from "@/app/types";
import Chip from "@mui/material/Chip";
import EventOutlinedIcon from "@mui/icons-material/EventOutlined";
import { useLocale, useTranslations } from "next-intl";
import { DEFAULT_LOCALE, type Locale } from "@/i18n/config";
import { getDateLabel } from "./DateLabel";
import { getPlaceLabel } from "./PlaceChip";
import { getTimeLabel } from "./TimeLabel";
import OurLink from "@/components/OurLink";
import { EVENTS_BASE } from "@/app/constants";

// Plain helper (no hooks): the caller threads the active `locale` so dates/times
// render in the UI language, and the already-translated `relacheLabel` for the
// "no performance" marker. Both have defaults so non-React callers still work.
export function getEventLabel(
  event: TRelatedEvent,
  locale: Locale = DEFAULT_LOCALE,
  relacheLabel: string = "Relâche",
): string {
  const left = [
    getDateLabel(event.debut_date, event.debut_date_approx, locale),
    getTimeLabel(event.debut_heure, event.debut_heure_approx, locale),
  ]
    .filter((value) => value !== "")
    .join(" ");
  const right = [
    getPlaceLabel(event.debut_lieu, event.debut_lieu_approx),
    event.circonstance,
    event.relache ? relacheLabel : "",
  ]
    .filter((value) => value !== "")
    .join(", ");
  if (left && right) {
    return `${left} • ${right}`;
  }
  return left || right;
}

export function EventLabel(event: TRelatedEvent) {
  const locale = useLocale() as Locale;
  const t = useTranslations("event");
  return getEventLabel(event, locale, t("relache"));
}

export default function EventChip(event: TRelatedEvent) {
  return (
    <Chip
      component={OurLink}
      href={`${EVENTS_BASE}/id/${event.id}/`}
      label={<EventLabel {...event} />}
      clickable
      size="small"
      icon={<EventOutlinedIcon />}
    />
  );
}
