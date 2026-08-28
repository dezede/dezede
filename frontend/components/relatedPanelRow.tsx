import RelatedEntitiesPanel from "./RelatedEntitiesPanel";
import { TDetailRow } from "./DetailTable";
import { countLabel, TCountedLabel } from "./entityChipRow";

// Top padding (px) that lands the row label's baseline on the first chip's text
// baseline. The grid's first chip sits a fixed distance below the cell top
// (cell padding + the chip centred in its content row), so a constant offset
// aligns the two baselines regardless of how many rows of chips follow. Tuned
// empirically against the rendered page: the label baseline sits 21px below the
// cell top, the first chip's baseline 25.25px, so a ~4px nudge closes the gap.
const LABEL_OFFSET = 4.25;

/**
 * Builds a `DetailTable` row for a heavy related collection: the label cell
 * carries the count ("123 œuvres") and the value cell holds a bounded,
 * virtualised `RelatedEntitiesPanel` that scrolls internally — so a huge
 * collection gets its own scrollbar inside the cell while the table never grows
 * a global vertical scrollbar. The chips are lazy-loaded from
 * `apiUrl?collection=…&limit=&offset=`. Like `entityChipRow`, the row drops out
 * (null content) when the collection is empty, so no blank labelled row remains.
 */
export function relatedPanelRow(
  apiUrl: string,
  collection: string,
  count: number,
  title: TCountedLabel,
): TDetailRow {
  // The panel's `title` prop is a plain string and its header is hidden here
  // (`showHeader={false}`), so feed it the plural/invariant form as a fallback.
  const panelTitle =
    title !== null && typeof title === "object" && "other" in title
      ? String(title.other)
      : String(title);
  return {
    key: collection,
    label: count ? countLabel(title, count) : panelTitle,
    content: count ? (
      <RelatedEntitiesPanel
        apiUrl={apiUrl}
        collection={collection}
        count={count}
        title={panelTitle}
        showHeader={false}
        frame={false}
      />
    ) : null,
    align: "offset",
    labelOffset: LABEL_OFFSET,
  };
}
