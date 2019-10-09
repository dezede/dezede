import i18n from "./i18n";
import Tooltip from "@material-ui/core/Tooltip";
import React from "react";

export const join = (parts, separator) => {
  if (separator === undefined) {
    separator = ', ';
  }
  parts = parts.filter(part => part !== null);
  if (parts.length > 1) {
    parts = parts.reduce((a, b) => [a, separator, b]);
  }
  return parts;
};


export const joinWithLast = (parts, separator, lastSeparator) => {
  if (lastSeparator === undefined) {
    lastSeparator = i18n.t('base:lastSeparator');
  }
  parts = join(parts, separator);
  if (parts.length > 2) {
    parts[parts.length - 2] = lastSeparator;
  }
  return parts;
};


export const removeDiacritics = text => (
  text.normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
);


const VOWELS = 'aeiouy';


export const abbreviate = (text, minLength) => {
  let pattern = `([a-z]{${minLength},}?(?<=[^${VOWELS}])(?=[${VOWELS}]))`;
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
};


export const getPluriel = text => (
  text + 's'
);
