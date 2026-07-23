"use client";

import { forwardRef, useCallback, useEffect, useRef, useState } from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Skeleton from "@mui/material/Skeleton";
import { GridComponents, VirtuosoGrid } from "react-virtuoso";
import { useChunkedRows } from "@/app/hooks";
import { TEntity } from "@/app/types";
import EntityChip from "@/format/EntityChip";
import SectionLabel from "./SectionLabel";
import { countLabel } from "./entityChipRow";

// One network request covers CHUNK_SIZE consecutive chips. Kept small (and
// aligned with the backend's default page size) so arriving on the page fetches
// only roughly what fits in the visible area — most visitors never scroll a
// related-objects list, so loading the whole collection up front is wasteful.
// Cells are a fixed size so the grid stays uniform — VirtuosoGrid needs equal
// cells to compute how many fit per row and therefore the full scroll height.
const CHUNK_SIZE = 20;
const CELL_WIDTH = 260; // px
const CELL_PADDING = 4; // px around each cell
// A cell is a fixed-height content area plus its padding, so ROW_HEIGHT is the
// real rendered height of every cell — skeleton or chip alike. VirtuosoGrid has
// no `fixedItemHeight`, so it infers the scroll track by measuring a sample
// cell; pinning the content height keeps that measurement constant as chunks
// resolve, which is what stops a load near the end from shifting the geometry
// and re-triggering an adjacent load (the load/scroll flicker).
const CELL_CONTENT_HEIGHT = 24; // px — a small chip
const ROW_HEIGHT = CELL_CONTENT_HEIGHT + 2 * CELL_PADDING; // px (32)
const MAX_HEIGHT = 300; // px — cap so a huge collection never dominates the page
// Preload only a little beyond the viewport so off-screen rows (and their
// network requests) aren't fetched until the user actually scrolls toward them.
const OVERSCAN = 100; // px

type Item = TEntity | undefined;

// VirtuosoGrid layout: a flex-wrap list of fixed-width cells (the documented
// grid components pattern). Item positioning is pure CSS flow, so the only
// styling needed is the cell box; the chip's own truncation lives in
// `itemContent` below.
const gridComponents: GridComponents = {
  List: forwardRef(function GridList({ style, children, ...props }, ref) {
    return (
      <div
        ref={ref}
        {...props}
        // Cancel the cells' horizontal padding (see Item below) with a matching
        // negative margin so the first and last columns sit flush with the
        // container edge — otherwise the grid is indented 4px relative to the
        // non-virtualised `EntityChipList`, whose chips start at the edge.
        style={{
          display: "flex",
          flexWrap: "wrap",
          marginLeft: -CELL_PADDING,
          marginRight: -CELL_PADDING,
          ...style,
        }}
      >
        {children}
      </div>
    );
  }),
  Item: ({ children, style, ...props }) => (
    <div
      {...props}
      style={{
        width: CELL_WIDTH,
        maxWidth: "100%",
        padding: CELL_PADDING,
        boxSizing: "border-box",
        ...style,
      }}
    >
      {children}
    </div>
  ),
};

/**
 * A heavy related-objects section of an autorité page (Œuvres, Rôles créés…),
 * rendered as a bounded panel: a count header over a fixed-max-height scroll
 * area holding a virtualised chip grid. The grid is seeded with a fixed-length
 * sparse array sized to `count`, so its scroll area spans the whole collection
 * from the first paint; each `CHUNK_SIZE` slice is fetched lazily from
 * `apiUrl?collection=…&limit=&offset=` only as it scrolls into view. Mirrors the
 * lazy-loading mechanics of {@link EntityVirtualTable}, adapted to chips.
 */
export default function RelatedEntitiesPanel({
  apiUrl,
  collection,
  count,
  title,
  showHeader = true,
  frame = true,
}: {
  apiUrl: string;
  collection: string;
  count: number;
  title: string;
  // When embedded as a `DetailTable` row, the row's label cell already carries
  // the count, and the bordered Paper frame is dropped so the bounded scroll
  // area sits flush in the cell.
  showHeader?: boolean;
  frame?: boolean;
}) {
  // Sparse, lazily-loaded chips sized to the full collection; the hook owns the
  // chunked fetching. The total is known up front, so the panel shows its real
  // height from the first paint.
  const { rows: items, loadRange } = useChunkedRows<TEntity>({
    endpoint: apiUrl,
    params: { collection },
    chunkSize: CHUNK_SIZE,
    initialCount: count,
  });

  // Measure the panel width to derive the column count, so the scroll area can
  // be sized to the full collection (rows × ROW_HEIGHT) without overscrolling.
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [columns, setColumns] = useState(1);
  useEffect(() => {
    const element = containerRef.current;
    if (element === null) {
      return;
    }
    const update = () =>
      setColumns(Math.max(1, Math.floor(element.clientWidth / CELL_WIDTH)));
    update();
    const observer = new ResizeObserver(update);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  const itemContent = useCallback(
    (_index: number, item: Item) => (
      <Box
        sx={{
          // Pin every cell to a fixed content height and centre its contents, so
          // a skeleton cell and a chip cell measure identically and the grid's
          // sampled row height never drifts as chunks resolve. Long names
          // ellipsize so a chip stays on one line within that height.
          height: CELL_CONTENT_HEIGHT,
          display: "flex",
          alignItems: "center",
          // Re-assert single-line truncation: this panel sits inside a
          // `DetailTable`, whose `.MuiChip-root { height: auto }` /
          // `.MuiChip-label { white-space: normal }` overrides (correct for the
          // non-virtualised chip rows) would otherwise let labels wrap and grow
          // past CELL_CONTENT_HEIGHT, overlapping rows in the uniform-cell grid.
          // The doubled `&&` outweighs DetailTable's equal-specificity selectors
          // so `white-space: nowrap` actually wins — otherwise the label keeps
          // wrapping and gets hard-clipped by the pinned height with no ellipsis.
          "&& .MuiChip-root": { maxWidth: "100%", height: CELL_CONTENT_HEIGHT },
          "&& .MuiChip-label": {
            // `min-width: 0` lets the label shrink within the chip's flex row,
            // which is what allows the ellipsis to engage instead of the text
            // just being clipped at the chip's edge.
            minWidth: 0,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            display: "block",
          },
          // Some chip labels (e.g. PersonChip) wrap their content in a
          // block-level element, which swallows the ellipsis — text-overflow
          // only truncates inline content. Force that wrapper inline.
          "&& .MuiChip-label > *": { display: "inline" },
        }}
      >
        {item ? (
          <EntityChip entity={item} />
        ) : (
          <Skeleton
            variant="rounded"
            width="100%"
            height={CELL_CONTENT_HEIGHT}
            sx={{ borderRadius: 4 }}
          />
        )}
      </Box>
    ),
    [],
  );

  if (count === 0) {
    return null;
  }

  const rows = Math.ceil(count / columns);
  const height = Math.min(MAX_HEIGHT, rows * ROW_HEIGHT);

  const grid = (
    <VirtuosoGrid
      data={items}
      components={gridComponents}
      itemContent={itemContent}
      rangeChanged={loadRange}
      overscan={OVERSCAN}
      // The grid only scrolls vertically; suppress horizontal scrolling so the
      // List's -4px edge margins (which bleed past the scroller to align the
      // outer columns flush) don't surface a horizontal scrollbar.
      style={{ height, overflowX: "hidden" }}
    />
  );
  const scroller = frame ? (
    <Paper ref={containerRef} variant="outlined" sx={{ overflow: "hidden" }}>
      {grid}
    </Paper>
  ) : (
    <Box ref={containerRef} sx={{ overflow: "hidden" }}>
      {grid}
    </Box>
  );

  if (!showHeader) {
    return scroller;
  }
  return (
    <Box>
      <SectionLabel>{countLabel(title, count)}</SectionLabel>
      {scroller}
    </Box>
  );
}
