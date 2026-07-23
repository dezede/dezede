"use server";

import { cookies } from "next/headers";
import { revalidatePath } from "next/cache";
import { DEFAULT_LOCALE, LOCALE_COOKIE, LOCALES, type Locale } from "@/i18n/config";

// Persist the chosen UI locale in a cookie (read back in `i18n/request.ts`).
// next-intl has no URL routing here, so we revalidate the whole tree to
// re-render server components with the new locale's messages.
export async function setLocale(locale: Locale): Promise<void> {
  const value = LOCALES.includes(locale) ? locale : DEFAULT_LOCALE;
  const store = await cookies();
  store.set(LOCALE_COOKIE, value, {
    path: "/",
    maxAge: 60 * 60 * 24 * 365,
    sameSite: "lax",
  });
  revalidatePath("/", "layout");
}
