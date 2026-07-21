"use client";

import {
  ReactNode,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import { TDossierCategory } from "@/app/types";
import DossierCountsProvider from "./DossierCountsProvider";

export type TDossierMasonryItem = {
  id: number;
  categorieId: number | null;
  node: ReactNode;
};

// useLayoutEffect on the client, useEffect on the server (avoids the SSR
// "useLayoutEffect does nothing on the server" warning).
const useIsoLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect;

// Client-side chip filter + masonry grid for the dossiers index. The heavy
// (server-rendered) DossierCard / DossierHelpCard elements are built by the
// server component and handed down as already-rendered `node`s.
//
// Layout is real, independent flex columns (which scroll smoothly — unlike a
// CSS multi-column block, whose balanced reflow janks a long scroll). To keep
// the columns level we place each card into the currently *shortest* column,
// measured from the rendered heights, instead of round-robin (which balances
// card count, not height, and so let one column trail off with an overhang).
// Measurement runs only on mount and on resize — never during scroll — and card
// heights are stable (the count skeleton is the same size as the loaded chip,
// and only a handful of cards carry an image), so the balanced layout holds.
export default function DossierIndexBrowser({
  categories,
  items,
  helpItem,
  allLabel,
}: {
  categories: TDossierCategory[];
  items: TDossierMasonryItem[];
  helpItem: ReactNode;
  allLabel: string;
}) {
  const [selected, setSelected] = useState<number | null>(null);
  // False during SSR and the first client render, true once hydrated.
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
  const theme = useTheme();
  // Before mount assume the widest layout so the server markup shows the 3-column
  // grid straight away (right for md+). On smaller screens the real count is only
  // known after mount, so until then the grid is hidden and a skeleton shown.
  const isMd = useMediaQuery(theme.breakpoints.up("md"), {
    defaultMatches: true,
  });
  const isSm = useMediaQuery(theme.breakpoints.up("sm"), {
    defaultMatches: true,
  });
  const columnCount = isMd ? 3 : isSm ? 2 : 1;

  const visibleItems = useMemo(
    () =>
      selected === null
        ? items
        : items.filter((item) => item.categorieId === selected),
    [items, selected],
  );

  // The cells to lay out, in source order. The help card is placed a couple of
  // cells in so it lands in the first row's last column (or just below the first
  // card in a single column).
  const cells = useMemo(() => {
    const list: { key: string; node: ReactNode }[] = visibleItems.map(
      (item) => ({ key: `d${item.id}`, node: item.node }),
    );
    if (selected === null) {
      const helpIndex = columnCount === 1 ? 1 : columnCount - 1;
      list.splice(Math.min(helpIndex, list.length), 0, {
        key: "help",
        node: helpItem,
      });
    }
    return list;
  }, [visibleItems, selected, helpItem, columnCount]);

  const refs = useRef(new Map<string, HTMLElement>());
  // Column index per cell; empty until measured (falls back to round-robin).
  const [assign, setAssign] = useState<number[]>([]);
  // Bumped on resize to trigger a re-measure.
  const [resizeTick, setResizeTick] = useState(0);

  // Measure the rendered card heights and pack each into the shortest column.
  // Heights are the same in any column (equal widths), so one pass is exact.
  useIsoLayoutEffect(() => {
    if (!mounted) return;
    const heights = new Array(columnCount).fill(0);
    const next = cells.map((cell) => {
      const el = refs.current.get(cell.key);
      // + 16 for the card's `mb: 2` gap, so columns with more cards aren't
      // under-counted and the packing stays balanced.
      const h = (el ? el.getBoundingClientRect().height : 0) + 16;
      let shortest = 0;
      for (let c = 1; c < columnCount; c++) {
        if (heights[c] < heights[shortest]) shortest = c;
      }
      heights[shortest] += h;
      return shortest;
    });
    // Only update when the assignment actually changed, so the effect converges.
    setAssign((prev) =>
      prev.length === next.length && prev.every((v, i) => v === next[i])
        ? prev
        : next,
    );
  }, [mounted, cells, columnCount, resizeTick]);

  // Re-measure on window resize (card widths, and so heights, change). Debounced
  // to a frame; resizes never happen mid-scroll, so this can't jank scrolling.
  useEffect(() => {
    if (!mounted) return;
    let raf = 0;
    const onResize = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => setResizeTick((t) => t + 1));
    };
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      cancelAnimationFrame(raf);
    };
  }, [mounted]);

  const columns = useMemo(() => {
    const cols: ReactNode[][] = Array.from({ length: columnCount }, () => []);
    cells.forEach((cell, i) => {
      const c = assign[i] ?? i % columnCount;
      cols[Math.min(c, columnCount - 1)].push(
        <Box
          key={cell.key}
          ref={(el: HTMLElement | null) => {
            if (el) refs.current.set(cell.key, el);
            else refs.current.delete(cell.key);
          }}
          sx={{ mb: 2 }}
        >
          {cell.node}
        </Box>,
      );
    });
    return cols;
  }, [cells, assign, columnCount]);

  return (
    <DossierCountsProvider>
      <Stack spacing={2}>
        <Stack direction="row" spacing={1} useFlexGap sx={{ flexWrap: "wrap" }}>
          <Chip
            label={allLabel}
            color={selected === null ? "primary" : undefined}
            variant={selected === null ? "filled" : "outlined"}
            onClick={() => setSelected(null)}
          />
          {categories.map((category) => (
            <Chip
              key={category.id}
              label={category.nom}
              color={selected === category.id ? "primary" : undefined}
              variant={selected === category.id ? "filled" : "outlined"}
              onClick={() => setSelected(category.id)}
            />
          ))}
        </Stack>
        <Box
          sx={{
            gap: 2,
            alignItems: "flex-start",
            // md+ is correct from the first paint; keep it hidden on smaller
            // screens until mount, when the real column count is known.
            display: mounted ? "flex" : { xs: "none", md: "flex" },
          }}
        >
          {columns.map((col, i) => (
            <Box key={i} sx={{ flex: 1, minWidth: 0 }}>
              {col}
            </Box>
          ))}
        </Box>
        {!mounted && (
          <Box
            sx={{
              display: { xs: "grid", md: "none" },
              gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
              gap: 2,
            }}
          >
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton
                key={i}
                variant="rounded"
                height={180}
                animation={false}
                sx={{
                  borderRadius: 2,
                  display: i < 4 ? "block" : { xs: "none", sm: "block" },
                }}
              />
            ))}
          </Box>
        )}
      </Stack>
    </DossierCountsProvider>
  );
}
