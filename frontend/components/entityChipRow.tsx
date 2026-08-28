import React from "react";
import { TEntity } from "@/app/types";
import EntityChipList from "./EntityChipList";
import { TDetailRow } from "./DetailTable";

// See `entityChipRow` below: top padding (px) that lands the row label's
// baseline on the first chip row's text baseline. The chips sit flush at the
// cell top, so the gap is tiny — 21px label baseline vs 21.25px chip baseline.
const CHIP_LABEL_OFFSET = 0.25;

/**
 * A related-objects label that either inflects with the count (`{ one, other }`,
 * e.g. `{ one: "Œuvre", other: "Œuvres" }`) or is invariant (a plain node, used
 * for phrase labels like "Membre de" that don't pluralize).
 */
export type TCountedLabel =
  | React.ReactNode
  | { one: React.ReactNode; other: React.ReactNode };

/**
 * Picks the singular or plural form for `count`. French rule: singular for a
 * count of 1, plural for 2+ (count is never 0 here — empty rows are dropped by
 * `DetailTable`). Mirrors the `parenteRows` `entities.length > 1` switch.
 */
function resolveLabel(label: TCountedLabel, count: number): React.ReactNode {
  if (
    label !== null &&
    typeof label === "object" &&
    "one" in label &&
    "other" in label
  ) {
    return count > 1 ? label.other : label.one;
  }
  return label as React.ReactNode;
}

/**
 * Prefixes a related-objects label with its count, lowercasing the noun so it
 * reads as a phrase ("Œuvres" → "123 œuvres"). Inflecting labels switch between
 * their singular/plural forms ("1 œuvre" vs "3 œuvres"); non-string labels
 * (rare) are kept verbatim after the count.
 */
export function countLabel(
  label: TCountedLabel,
  count: number,
): React.ReactNode {
  const resolved = resolveLabel(label, count);
  if (typeof resolved === "string") {
    return `${count} ${resolved.toLowerCase()}`;
  }
  return (
    <>
      {count} {resolved}
    </>
  );
}

/**
 * Builds a `DetailTable` row for a list of catalogue entities, dropping the row
 * entirely (null content) when the list is empty — so an empty list never leaves
 * a labelled row with a blank value cell. Mirrors the `parenteRows` helper. The
 * label is prefixed with the related-objects count (e.g. "123 œuvres").
 */
export function entityChipRow(
  key: string,
  label: TCountedLabel,
  entities: TEntity[],
): TDetailRow {
  return {
    key,
    label: entities.length
      ? countLabel(label, entities.length)
      : resolveLabel(label, entities.length),
    content: entities.length ? <EntityChipList entities={entities} /> : null,
    // `EntityChipList` is a flex row, whose synthesised baseline doesn't track
    // the chip text, so top-align and nudge the label onto the first chip row's
    // baseline (see `DetailTable`'s "offset").
    align: "offset",
    labelOffset: CHIP_LABEL_OFFSET,
  };
}
