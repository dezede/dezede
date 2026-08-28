import { cookies, headers } from "next/headers";
import { getRequestConfig } from "next-intl/server";
import { LOCALE_COOKIE, resolveAcceptLanguage, resolveLocale } from "./config";

// No URL-based routing: the active locale is read from a cookie so URLs stay
// language-agnostic. When the user has explicitly picked a locale (cookie set),
// that wins; otherwise we negotiate the browser's `Accept-Language` header and
// fall back to English when none of its languages are supported.
export default getRequestConfig(async () => {
  const store = await cookies();
  const cookieValue = store.get(LOCALE_COOKIE)?.value;
  const locale = cookieValue
    ? resolveLocale(cookieValue)
    : resolveAcceptLanguage((await headers()).get("accept-language"));
  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});
