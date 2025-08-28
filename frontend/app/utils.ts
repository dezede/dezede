import { notFound } from "next/navigation";
import { TPage, TPageResults } from "./types";

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

export function djangoFetch(relativeUrl: string, init?: RequestInit) {
  return fetch(`http://django:8000${relativeUrl}`, {
    ...init,
    headers: {
      ...init?.headers,
      "Content-Type": "application/json",
    },
  });
}

export async function djangoFetchData<T>(relativeUrl: string): Promise<T> {
  const response = await djangoFetch(relativeUrl);
  if (!response.ok) {
    notFound();
  }
  return await response.json();
}

export async function fetchPages<T = TPage>(
  relativeUrl: string,
): Promise<TPageResults<T>> {
  return await djangoFetchData<TPageResults<T>>(relativeUrl);
}

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
