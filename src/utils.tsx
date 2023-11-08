import Tooltip from "@material-ui/core/Tooltip";
import React from "react";

import i18n from "./i18n";


export function join(parts: React.ReactNode[], separator?: string, lastSeparator?: string) {
  if (separator === undefined) {
    separator = ', ';
  }
  if (lastSeparator === undefined) {
    lastSeparator = separator;
  }
  parts = parts.filter(part => part !== null);
  if (parts.length === 0) {
    return null;
  }
  if (parts.length === 1) {
    return parts[0];
  }
  return parts.reduce((a, b, index) => [a, index === parts.length - 1 ? lastSeparator : separator, b]);
}


export const joinWithLast = (parts: React.ReactNode[], separator?: string, lastSeparator?: string) => {
  if (lastSeparator === undefined) {
    lastSeparator = i18n.t('base:lastSeparator');
  }
  return join(parts, separator, lastSeparator);
};


export function removeDiacritics(text: string) {
  return text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '');
}


const VOWELS = 'aeiouy';


export function abbreviate(text: string, minLength: number) {
  let pattern = `([a-z]{${minLength - 1},}?[^${VOWELS}](?=[${VOWELS}]))`;
  if (minLength === 1) { // Handles the special case for a single vowel.
    pattern = `([${VOWELS}]|${pattern})`;
  }
  const regexp = new RegExp(`${pattern}[a-z]{2,}`, 'gi');
  let short = '';
  let lastEnd = 0;
  const normalizedText = removeDiacritics(text);
  let match;
  while ((match = regexp.exec(normalizedText)) !== null) {
    const start = match.index;
    short += text.substring(lastEnd, start);
    short += text.substring(start, start + match[1].length) + '.';
    lastEnd = start + match[0].length;
  }
  short += text.substring(lastEnd);
  return (
    <Tooltip title={text}>
      <span>{short}</span>
    </Tooltip>
  );
}


export function getPluriel(text: string) {
  return text + 's';
}
