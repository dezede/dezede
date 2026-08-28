import { ReactNode } from "react";
import { useLocale } from "next-intl";
import { DEFAULT_LOCALE, type Locale } from "@/i18n/config";

// One formatter per locale, built lazily and cached. Each renders a long date
// (e.g. "1 janvier 1789" / "January 1, 1789") in the active UI language.
const dateFormatters = new Map<string, Intl.DateTimeFormat>();

function getFormatter(locale: string): Intl.DateTimeFormat {
  let formatter = dateFormatters.get(locale);
  if (!formatter) {
    formatter = new Intl.DateTimeFormat(locale, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    dateFormatters.set(locale, formatter);
  }
  return formatter;
}

function formatDateParts(
  dateString: string,
  locale: string,
): {
  parts: Intl.DateTimeFormatPart[];
  isFirst: boolean;
} {
  const segments = dateString.split("-").map(Number);
  const [y, m = 1, d = 1] = segments;
  const date = new Date(y, m - 1, d);
  if (isNaN(date.getTime())) {
    return { parts: [{ type: "literal", value: dateString }], isFirst: false };
  }
  const parts = getFormatter(locale).formatToParts(date);
  const dayPart = parts.find((part) => part.type === "day");
  // French marks the first of the month with the ordinal "1er"; other locales
  // (English) don't, so the superscript is suppressed below for them.
  const isFirst = locale.startsWith("fr") && dayPart?.value === "1";
  return { parts, isFirst };
}

export function getDateLabel(
  dateString: string | null = null,
  fuzzyDate: string = "",
  locale: Locale = DEFAULT_LOCALE,
): string {
  if (fuzzyDate !== "") {
    return fuzzyDate;
  }
  if (dateString === null) {
    return "";
  }
  const { parts, isFirst } = formatDateParts(dateString, locale);
  return parts
    .map((part) =>
      isFirst && part.type === "day" ? `${part.value}er` : part.value,
    )
    .join("");
}

export default function DateLabel({
  dateString = null,
  fuzzyDate = "",
}: {
  dateString?: string | null;
  fuzzyDate?: string;
}): ReactNode {
  const locale = useLocale();
  if (fuzzyDate !== "") {
    return fuzzyDate;
  }
  if (dateString === null) {
    return null;
  }
  const { parts, isFirst } = formatDateParts(dateString, locale);
  if (!isFirst) {
    return parts.map((part) => part.value).join("");
  }
  const dayIndex = parts.findIndex((part) => part.type === "day");
  const before = parts
    .slice(0, dayIndex)
    .map((part) => part.value)
    .join("");
  const after = parts
    .slice(dayIndex + 1)
    .map((part) => part.value)
    .join("");
  return (
    <>
      {before}
      {parts[dayIndex].value}
      <sup
        style={{
          fontSize: "0.75em",
          lineHeight: 0,
          position: "relative",
          top: "-0.4em",
          verticalAlign: "baseline",
        }}
      >
        er
      </sup>
      {after}
    </>
  );
}
