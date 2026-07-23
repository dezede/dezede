import { useLocale } from "next-intl";
import { DEFAULT_LOCALE, type Locale } from "@/i18n/config";

export function getTimeLabel(
  timeString: string | null = null,
  fuzzyTime: string = "",
  locale: Locale = DEFAULT_LOCALE,
): string {
  if (fuzzyTime !== "") {
    return fuzzyTime;
  }
  if (timeString === null) {
    return "";
  }
  return new Date(`0001-01-01T${timeString}`).toLocaleTimeString(locale, {
    hour: "numeric",
    minute: "numeric",
  });
}

export function TimeLabel({
  timeString = null,
  fuzzyTime = "",
}: {
  timeString?: string | null;
  fuzzyTime?: string;
}): string | null {
  const locale = useLocale() as Locale;
  return getTimeLabel(timeString, fuzzyTime, locale);
}
