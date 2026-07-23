// Pure locale constants and types — safe to import from both server and client
// components. This module deliberately has NO `next/headers` (or other
// server-only) import, so pulling `Locale`/`LOCALES`/`DEFAULT_LOCALE` into a
// client bundle does not drag server-only code along with it.
//
// Supported UI locales. The site defaults to English; French is the secondary
// locale. The catalogue data itself stays in French (it comes from the Django
// API) — only the surrounding interface chrome is translated.
export const LOCALES = ["en", "fr"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "en";
export const LOCALE_COOKIE = "NEXT_LOCALE";

export function resolveLocale(value: string | undefined): Locale {
  return LOCALES.includes(value as Locale) ? (value as Locale) : DEFAULT_LOCALE;
}

// Pick the best supported locale from an HTTP `Accept-Language` header,
// honouring the client's quality (`q`) preferences. Matching is done on the
// primary language subtag (`fr-FR` → `fr`), so regional variants still resolve.
// Falls back to English when nothing in the header is supported.
export function resolveAcceptLanguage(header: string | null | undefined): Locale {
  if (!header) return DEFAULT_LOCALE;
  const ranked = header
    .split(",")
    .map((part) => {
      const [tag, ...params] = part.trim().split(";");
      const q = params
        .map((p) => p.trim().match(/^q=(\d+(?:\.\d+)?)$/))
        .find(Boolean);
      return {
        language: tag.toLowerCase().split("-")[0],
        quality: q ? parseFloat(q[1]) : 1,
      };
    })
    .filter((entry) => entry.language && entry.quality > 0)
    .sort((a, b) => b.quality - a.quality);
  const match = ranked.find((entry) => LOCALES.includes(entry.language as Locale));
  return (match?.language as Locale) ?? DEFAULT_LOCALE;
}
