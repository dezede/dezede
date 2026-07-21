"use client";

import { useEffect, useRef, useSyncExternalStore } from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Skeleton from "@mui/material/Skeleton";
import EventOutlinedIcon from "@mui/icons-material/EventOutlined";
import HistoryEduOutlinedIcon from "@mui/icons-material/HistoryEduOutlined";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import FolderOutlinedIcon from "@mui/icons-material/FolderOutlined";
import { useTranslations } from "next-intl";
import { TDossierKind } from "@/app/types";
import OurChip from "./OurChip";
import { useDossierCounts } from "./DossierCountsProvider";

function kindIcon(kind: TDossierKind) {
  if (kind === "evenements") return <EventOutlinedIcon />;
  if (kind === "oeuvres") return <HistoryEduOutlinedIcon />;
  return <DescriptionOutlinedIcon />;
}

// One count chip per active kind, plus the sub-dossier count. On the index a
// chip's count is fetched once its card scrolls into view (batched, per-id);
// until then the chip is a chip-shaped skeleton of the same fixed footprint, so
// the real chip replacing it never changes the row's wrap layout (no shift).
// Once loaded the chip shows its icon + "N événements", centred, truncating the
// word with an ellipsis if a number ever overflows. On the detail page children
// carry precomputed counts, so their chips render loaded from the first paint.
export default function DossierCountChips({
  dossierId,
  kinds,
  initialCounts,
  childrenCount,
  onImage = false,
}: {
  dossierId: number;
  kinds: TDossierKind[];
  initialCounts: Partial<Record<TDossierKind, number>> | null;
  childrenCount: number;
  // When laid over the cover image, chips get a translucent light backing and
  // dark text so they stay legible on the gradient scrim.
  onImage?: boolean;
}) {
  const t = useTranslations("dossiers");
  const lazy = initialCounts == null;
  const ref = useRef<HTMLDivElement>(null);
  const store = useDossierCounts();

  const fetched = useSyncExternalStore(
    (onChange) => store.subscribe(dossierId, onChange),
    () => store.getSnapshot(dossierId),
    () => undefined,
  );

  useEffect(() => {
    if (!lazy || !ref.current) return;
    return store.observe(dossierId, ref.current);
  }, [lazy, dossierId, store]);

  const counts = lazy ? fetched : initialCounts;

  const subdossiers = childrenCount
    ? t("subdossierCount", { count: childrenCount })
    : "";
  if (kinds.length === 0 && !subdossiers) return null;

  const chipSx = {
    maxWidth: "100%",
    ...(onImage
      ? {
          bgcolor: "rgba(255,255,255,0.9)",
          color: "rgba(0,0,0,0.87)",
          "& .MuiChip-label svg": { color: "primary.dark" },
        }
      : {}),
    // Let the label fill the fixed-width chip and centre its content; the text
    // still truncates (the inner span below carries the ellipsis).
    "& .MuiChip-label": {
      lineHeight: 1,
      flex: 1,
      minWidth: 0,
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
    },
  };

  function kindWord(kind: TDossierKind) {
    return kind === "evenements"
      ? t("eventLabel")
      : kind === "oeuvres"
        ? t("workLabel")
        : t("sourceLabel");
  }

  // Icon + "N événements", the text truncating with an ellipsis if it ever
  // overflows the fixed-width chip (so the number always stays visible).
  function countContent(kind: TDossierKind) {
    const count = counts?.[kind] ?? 0;
    return (
      <Box
        component="span"
        sx={{
          display: "inline-flex",
          alignItems: "center",
          gap: 0.5,
          minWidth: 0,
          "& svg": { fontSize: 18, flexShrink: 0 },
        }}
      >
        {kindIcon(kind)}
        <Box
          component="span"
          sx={{
            minWidth: 0,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
            fontVariantNumeric: "tabular-nums",
          }}
        >
          {kind === "evenements"
            ? t("eventCount", { count })
            : kind === "oeuvres"
              ? t("workCount", { count })
              : t("sourceCount", { count })}
        </Box>
      </Box>
    );
  }

  return (
    <Stack
      ref={ref}
      direction="row"
      spacing={1}
      useFlexGap
      sx={{ flexWrap: "wrap", alignItems: "center" }}
    >
      {kinds.map((kind) => {
        // Fixed footprint (icon + 6-digit number + word + chip padding) shared
        // by the loaded chip and its loading skeleton, so one replacing the
        // other never shifts the row.
        const width = `${12 + kindWord(kind).length}ch`;
        return counts?.[kind] === undefined ? (
          <Skeleton
            key={kind}
            variant="rounded"
            // `width` is in `ch`, which resolves against the element's own
            // font-size — so pin it to the small chip's font (0.8125rem), or
            // the skeleton (inheriting the larger body font) comes out wider
            // than the chip it stands in for.
            sx={{
              width,
              height: 24,
              borderRadius: "16px",
              fontSize: "0.8125rem",
            }}
          />
        ) : (
          <OurChip
            key={kind}
            label={countContent(kind)}
            size="small"
            variant={onImage ? "filled" : "outlined"}
            sx={{ ...chipSx, width }}
          />
        );
      })}
      {subdossiers ? (
        <OurChip
          icon={<FolderOutlinedIcon />}
          label={subdossiers}
          size="small"
          variant={onImage ? "filled" : "outlined"}
          sx={chipSx}
        />
      ) : null}
    </Stack>
  );
}
