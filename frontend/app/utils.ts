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
      // Keep 0 (a valid offset/limit); only drop absent or empty values.
      if (value === undefined || value === null || value === "") {
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

function parseJsonHeader(
  response: Response,
  header: string,
  defaultValue: string = "",
) {
  return JSON.parse(decodeHeader(response, header, defaultValue));
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

  const {
    id,
    type,
    title,
    seo_title,
    search_description,
    ancestors,
    previous,
    next,
    url,
    owner,
    first_published_at,
  } = parseJsonHeader(redirectResponse, "X-Page-Data");

  return {
    id,
    apiUrl: getRelativeUrl(redirectResponse.headers.get("location") ?? ""),
    type: (type ?? "wagtailcore.Page") as EPageType,
    title,
    seoTitle: seo_title,
    description: search_description,
    ancestors,
    previous,
    next,
    url,
    owner,
    firstPublishedAt: first_published_at,
  };
});

function removeDiacritics(text: string): string {
  return text.normalize("NFKD").replaceAll(/\p{Mark}/gu, "");
}

const NON_LETTER = /(\P{L}+)/u;
const VOWELS = "AEIOUYaeiouy";

function isVowel(letter: string): boolean {
  return VOWELS.includes(letter);
}

// Mirrors Django's `common.utils.abbreviate` (with its default `min_len=1`):
// a single leading vowel followed by a consonant is kept alone ("Amélie" →
// "A."); otherwise everything up to and including the first consonant that is
// followed by a vowel is kept ("Auguste" → "Aug.", "François" → "Fr.").
// Words the rule cannot shorten ("de", "La", "A.-J.") stay intact.
function abbreviateWord(word: string): string {
  const normalizedWord = removeDiacritics(word);
  if (
    normalizedWord.length >= 3 &&
    isVowel(normalizedWord[0]) &&
    !isVowel(normalizedWord[1])
  ) {
    return `${word[0]}.`;
  }
  for (let i = 0; i + 2 < normalizedWord.length; i++) {
    if (!isVowel(normalizedWord[i]) && isVowel(normalizedWord[i + 1])) {
      return `${word.substring(0, i + 1)}.`;
    }
  }
  return word;
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

// French spelling of 1–9, mirroring Django's `humanize.apnumber` (used for
// pupitre quantities, e.g. "un à quatre contrebasses"). Numbers ≥ 10 (or < 1)
// stay as digits.
const FRENCH_NUMBERS = [
  "un",
  "deux",
  "trois",
  "quatre",
  "cinq",
  "six",
  "sept",
  "huit",
  "neuf",
];
export function apnumber(value: number): string {
  return value >= 1 && value <= 9 ? FRENCH_NUMBERS[value - 1] : String(value);
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

// Query params understood by the event API (and stored verbatim in the URL).
export const EVENT_FILTER_PARAMS = [
  "q",
  "lieu",
  "oeuvre",
  "individu",
  "ensemble",
  "source",
  "partie",
  "profession",
  "dates_0",
  "dates_1",
  "par_saison",
  "order_by",
] as const;

/**
 * Replicates Django's `common.utils.text.BiGrouper`: groups values by their
 * identical (ordered) tuple of keys, preserving first-seen order. Used to render
 * a distribution as "performer1, performer2 [role]".
 */
export function biGroup<E, V, K>(
  elements: E[],
  getValue: (element: E) => V | null,
  getKey: (element: E) => K | null,
  valueId: (value: V) => string,
  keyId: (key: K) => string,
): { values: V[]; keys: (K | null)[] }[] {
  const order: string[] = [];
  const valueOf = new Map<string, V>();
  const keysOf = new Map<string, (K | null)[]>();
  for (const element of elements) {
    const value = getValue(element);
    if (value === null) {
      continue;
    }
    const vid = valueId(value);
    if (!valueOf.has(vid)) {
      valueOf.set(vid, value);
      keysOf.set(vid, []);
      order.push(vid);
    }
    keysOf.get(vid)!.push(getKey(element));
  }
  const signatureOrder: string[] = [];
  const groupValues = new Map<string, V[]>();
  const groupKeys = new Map<string, (K | null)[]>();
  for (const vid of order) {
    const keys = keysOf.get(vid)!;
    const signature = keys
      .map((key) => (key === null ? "\0" : keyId(key)))
      .join("|");
    if (!groupValues.has(signature)) {
      groupValues.set(signature, []);
      groupKeys.set(signature, keys);
      signatureOrder.push(signature);
    }
    groupValues.get(signature)!.push(valueOf.get(vid)!);
  }
  return signatureOrder.map((signature) => ({
    values: groupValues.get(signature)!,
    keys: groupKeys.get(signature)!,
  }));
}

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
