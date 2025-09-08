import { notFound } from "next/navigation";
import {
  EPageType,
  TFindPageData,
  TPage,
  TPageResults,
  TQueryParams,
} from "./types";
import { cache } from "react";

export function safeParseInt<T>(
  str: string | string[] | null | undefined,
  defaultValue: T,
): number | T {
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

export const djangoFetch = function djangoFetch(
  relativeUrl: string,
  params?: TQueryParams,
  init?: RequestInit,
) {
  const searchParams = new URLSearchParams();
  if (params !== undefined) {
    Object.entries(params).forEach(([param, value]) => {
      if (!value) {
        return;
      }
      if (typeof value === "number") {
        value = value.toString();
      }
      if (typeof value === "string") {
        searchParams.set(param, value);
      } else {
        for (const item of value) {
          searchParams.append(param, item);
        }
      }
    });
  }
  return fetch(`http://django:8000${relativeUrl}?${searchParams.toString()}`, {
    ...init,
    headers: {
      ...init?.headers,
      "Content-Type": "application/json",
    },
  });
};

export const djangoFetchData = cache(async function djangoFetchData<T>(
  relativeUrl: string,
  params?: TQueryParams,
  fields?: string[],
  extraFields?: string[],
): Promise<T> {
  const response = await djangoFetch(relativeUrl, {
    ...params,
    fields: (fields ?? []).join(","),
    extra_fields: (extraFields ?? []).join(","),
  });
  if (!response.ok) {
    notFound();
  }
  return await response.json();
});

export async function fetchPages<T = TPage>(
  relativeUrl: string,
  params?: TQueryParams,
  fields?: string[],
): Promise<TPageResults<T>> {
  return await djangoFetchData<TPageResults<T>>(relativeUrl, params, fields);
}

function decodeHeader(
  response: Response,
  header: string,
  defaultValue: string = "",
): string {
  return decodeURIComponent(response.headers.get(header) ?? defaultValue);
}

export const findPage = cache(async function findPage({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}): Promise<TFindPageData> {
  let { slug } = await params;
  if (slug.length < 1) {
    notFound();
  } else {
    slug = slug.slice(1);
  }
  const wagtailUrl = `/${(slug ?? []).map(decodeURIComponent).join("/")}`;
  const redirectResponse = await djangoFetch(
    "/api/pages/find/",
    {
      html_path: wagtailUrl,
    },
    {
      redirect: "manual",
    },
  );
  if (redirectResponse.status !== 302) {
    notFound();
  }
  return {
    id: safeParseInt(redirectResponse.headers.get("X-Page-Id"), 0),
    apiUrl: getRelativeUrl(redirectResponse.headers.get("location") ?? ""),
    type: (redirectResponse.headers.get("X-Page-Type") ??
      "wagtailcore.Page") as EPageType,
    title: decodeHeader(redirectResponse, "X-Page-Title"),
    seoTitle: decodeHeader(redirectResponse, "X-Page-Seo-Title"),
    description: decodeHeader(redirectResponse, "X-Page-Description"),
    ancestors: JSON.parse(decodeHeader(redirectResponse, "X-Page-Ancestors")),
    previous: JSON.parse(
      decodeHeader(redirectResponse, "X-Page-Previous", "null"),
    ),
    next: JSON.parse(decodeHeader(redirectResponse, "X-Page-Next", "null")),
    url: decodeURIComponent(redirectResponse.headers.get("X-Page-Url") ?? ""),
  };
});

function removeDiacritics(text: string): string {
  return text.normalize("NFKD").replaceAll(/\p{Mark}/gu, "");
}

const VOWELS_PATTERN = /^([AEIOUY]+)[^AEIOUY]+[AEIOUY]/i;
const NON_LETTER = /(\P{L}+)/u;

function abbreviateWord(word: string, minLength: number = 1): string {
  if (word.length <= minLength) {
    return word;
  }
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

export function withParticule(particule: string, nom: string): string {
  if (!particule) {
    return nom;
  }
  if (particule.endsWith("’") || particule.endsWith("'")) {
    return `${particule}${nom}`;
  }
  return `${particule} ${nom}`;
}

export function capfirst(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}
export function joinWithLast(values: string[]) {
  if (values.length === 0) {
    return "";
  }
  if (values.length === 1) {
    return values[0];
  }
  return [values.slice(0, -1).join(", "), values[values.length - 1]].join(
    " et ",
  );
}

const ROMAN_BINDINGS = [
  { n: 1000, s: "M" },
  { n: 900, s: "CM" },
  { n: 500, s: "D" },
  { n: 400, s: "CD" },
  { n: 100, s: "C" },
  { n: 90, s: "XC" },
  { n: 50, s: "L" },
  { n: 40, s: "XL" },
  { n: 10, s: "X" },
  { n: 9, s: "IX" },
  { n: 5, s: "V" },
  { n: 4, s: "IV" },
  { n: 1, s: "I" },
];

export function toRoman(integer: number): string {
  if (integer < 1) {
    return "";
  }
  let roman = "";
  for (const { n, s } of ROMAN_BINDINGS) {
    while (integer >= n) {
      integer -= n;
      roman += s;
    }
  }
  return roman;
}
