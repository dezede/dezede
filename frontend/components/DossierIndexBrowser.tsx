"use client";

import { ReactNode, useMemo, useState, useSyncExternalStore } from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import Skeleton from "@mui/material/Skeleton";
import useMediaQuery from "@mui/material/useMediaQuery";
import { useTheme } from "@mui/material/styles";
import { TDossierCategory } from "@/app/types";

export type TDossierMasonryItem = {
  id: number;
  categorieId: number | null;
  node: ReactNode;
};

// Client-side chip filter + masonry grid for the dossiers index. The heavy
// (async, server-rendered) DossierCard/DossierHelpCard elements are built by
// the server component and handed down as already-rendered `node`s, so this
// component only ever toggles which of them are visible — it never re-renders
// their content.
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
  // False during SSR and the first client render, true once hydrated — lets us
  // tell "we don't know the viewport yet" from "we do".
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
  const theme = useTheme();
  // Before mount, assume the widest layout so the server-rendered markup shows
  // the correct 3-column grid straight away (right for md+ screens). On smaller
  // screens the real column count is only known after mount, so until then we
  // hide the grid via CSS and show a skeleton in its place instead of flashing
  // the wrong layout.
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

  // We distribute the cards into explicit columns ourselves (rather than relying
  // on CSS `column-count`, which balances by height and so can't pin a card to a
  // given column). Items are spread round-robin — item i goes to column i % n —
  // which reads left-to-right, row by row, and keeps the columns evenly filled.
  const columns = useMemo(() => {
    const cols: ReactNode[][] = Array.from({ length: columnCount }, () => []);
    visibleItems.forEach((item, i) => {
      cols[i % columnCount].push(
        <Box key={item.id} sx={{ mb: 2 }}>
          {item.node}
        </Box>,
      );
    });
    if (selected === null) {
      const help = (
        <Box key="help" sx={{ mb: 2 }}>
          {helpItem}
        </Box>
      );
      if (columnCount === 1) {
        // Single column: help card reads best just below the first card.
        cols[0].splice(1, 0, help);
      } else {
        // Multi-column: help card sits at the top of the last column, so it
        // reliably lands in the first visual row's last position.
        cols[columnCount - 1].unshift(help);
      }
    }
    return cols;
  }, [visibleItems, columnCount, selected, helpItem]);

  return (
    <Stack spacing={2}>
      <Stack
        direction="row"
        spacing={1}
        useFlexGap
        sx={{ flexWrap: "wrap" }}
      >
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
          // On md+ the 3-column layout is correct from the first paint, so show
          // it immediately. On smaller screens keep it hidden until mount, when
          // the real column count is known.
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
            // 1 column on xs, 2 on sm — matching the real layout at each size.
            gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr" },
            gap: 2,
          }}
        >
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton
              key={i}
              variant="rounded"
              height={180}
              sx={{
                borderRadius: 2,
                // xs is a single column, so keep it to 4 cards; sm has two
                // columns and shows all 8 (twice as many).
                display: i < 4 ? "block" : { xs: "none", sm: "block" },
              }}
            />
          ))}
        </Box>
      )}
    </Stack>
  );
}
