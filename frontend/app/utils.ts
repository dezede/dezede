import { notFound } from "next/navigation";
import { EPageType, TFindPageData, TPage, TPageResults } from "./types";
import { cache } from "react";
import { ROOT_SLUG } from "./constants";

export function safeParseInt(
  str: string | string[] | null | undefined,
  defaultValue: number = 0,
): number {
  if (typeof str === "string") {
    if (/^\d+$/.test(str)) {
      return parseInt(str);
    }
  }
  return defaultValue;
}

export function getRelativeUrl(absoluteUrl: string): string {
  return new URL(absoluteUrl).pathname;
}

export const djangoFetch = cache(function djangoFetch(
  relativeUrl: string,
  init?: RequestInit,
) {
  return fetch(`http://django:8000${relativeUrl}`, {
    ...init,
    headers: {
      ...init?.headers,
      "Content-Type": "application/json",
    },
  });
});

export const djangoFetchData = cache(async function djangoFetchData<T>(
  relativeUrl: string,
): Promise<T> {
  const response = await djangoFetch(relativeUrl);
  if (!response.ok) {
    notFound();
  }
  return await response.json();
});

export async function fetchPages<T = TPage>(
  relativeUrl: string,
): Promise<TPageResults<T>> {
  return await djangoFetchData<TPageResults<T>>(relativeUrl);
}

export const findPage = cache(async function findPage({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}): Promise<TFindPageData> {
  let { slug } = await params;
  if (slug.length < 1 || slug[0] !== ROOT_SLUG) {
    notFound();
  } else {
    slug = slug.slice(1);
  }
  const wagtailUrl = `/${(slug ?? []).join("/")}`;
  const redirectResponse = await djangoFetch(
    `/api/pages/find/?html_path=${wagtailUrl}`,
    {
      redirect: "manual",
    },
  );
  if (redirectResponse.status !== 302) {
    notFound();
  }
  return {
    id: safeParseInt(redirectResponse.headers.get("X-Page-Id")),
    apiUrl: getRelativeUrl(redirectResponse.headers.get("location") ?? ""),
    type: (redirectResponse.headers.get("X-Page-Type") ??
      "wagtailcore.Page") as EPageType,
    title: decodeURIComponent(
      redirectResponse.headers.get("X-Page-Title") ?? "",
    ),
    seoTitle: decodeURIComponent(
      redirectResponse.headers.get("X-Page-Seo-Title") ?? "",
    ),
    description: decodeURIComponent(
      redirectResponse.headers.get("X-Page-Description") ?? "",
    ),
    ancestors: JSON.parse(
      decodeURIComponent(
        redirectResponse.headers.get("X-Page-Ancestors") ?? "[]",
      ),
    ),
    url: decodeURIComponent(redirectResponse.headers.get("X-Page-Url") ?? ""),
  };
});

function removeDiacritics(text: string): string {
  return text.normalize("NFKD").replaceAll(/\p{Mark}/gu, "");
}

const VOWELS_PATTERN = /^([AEIOUY]+)[^AEIOUY]+[AEIOUY]/i;
const NON_LETTER = /(\P{L}+)/u;

function abbreviateWord(word: string, minLength: number = 1): string {
  const normalizedWord = removeDiacritics(word);
  if (minLength === 1) {
    const vowelMatch = normalizedWord.match(VOWELS_PATTERN);
    if (vowelMatch !== null) {
      return `${word.substring(0, vowelMatch[1].length)}.`;
    }
  }
  const generalMatch = normalizedWord.match(
    new RegExp(`^(\\w{${minLength},}?)[AEIOUY]\\w+`, "i"),
  );
  if (generalMatch === null) {
    return `${word[0]}.`;
  }
  return `${word.substring(0, generalMatch[1].length)}.`;
}

export function abbreviate(text: string): string {
  return text
    .split(NON_LETTER)
    .map((bit) => (bit.match(NON_LETTER) === null ? abbreviateWord(bit) : bit))
    .join("");
}
