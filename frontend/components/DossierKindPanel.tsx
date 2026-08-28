"use client";

import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted";
import QueryStatsIcon from "@mui/icons-material/QueryStats";
import { useTranslations } from "next-intl";

/**
 * The panel of one kind tab on a dossier detail page. For kinds with
 * visualisations (events and works), a prominent Données / Visualisations
 * segmented control switches between the server-rendered data list and the
 * map + statistics; the visualisations mount only when first opened so
 * Leaflet and the charts load on demand. Kinds without visualisations
 * (sources) render the data directly.
 *
 * The active sub-view is mirrored into the URL hash
 * (`#<slug>-visualisations`, extending the `#<slug>` scheme of DossierTabs)
 * so it survives reloads and can be shared. Switching tabs rewrites the hash
 * to the bare tab slug, which resets this panel to Données.
 */
export default function DossierKindPanel({
  slug,
  data,
  visualisations,
}: {
  // The owning tab's hash slug (the kind: 'evenements' | 'oeuvres').
  slug: string;
  data: React.ReactNode;
  visualisations?: React.ReactNode;
}) {
  const t = useTranslations("dossiers");
  const [view, setView] = useState<"data" | "visualisations">("data");
  const [vizMounted, setVizMounted] = useState(false);
  const hasVisualisations = visualisations !== undefined;

  useEffect(() => {
    if (!hasVisualisations) {
      return;
    }
    // Adopt the sub-view from the hash on load and whenever it changes
    // (DossierTabs dispatches a synthetic hashchange after rewriting it, so
    // leaving the tab and coming back resets the panel to Données).
    const syncFromHash = () => {
      if (window.location.hash === `#${slug}-visualisations`) {
        setVizMounted(true);
        setView("visualisations");
      } else {
        setView("data");
      }
    };
    syncFromHash();
    window.addEventListener("hashchange", syncFromHash);
    return () => window.removeEventListener("hashchange", syncFromHash);
  }, [slug, hasVisualisations]);

  if (!visualisations) {
    return <>{data}</>;
  }

  const handleChange = (
    _event: React.MouseEvent,
    value: "data" | "visualisations" | null,
  ) => {
    // Ignore clicks on the already-active button (exclusive groups emit null).
    if (value === null) {
      return;
    }
    setView(value);
    if (value === "visualisations") {
      setVizMounted(true);
    }
    // Same no-navigation hash update as DossierTabs.
    window.history.replaceState(
      null,
      "",
      value === "visualisations" ? `#${slug}-visualisations` : `#${slug}`,
    );
  };

  return (
    <Stack spacing={3}>
      {/* Centered primary segmented control, deliberately bigger and more
          colorful than the small neutral filter toggles (per type/date…) so
          the visualisations are actually discovered. */}
      <ToggleButtonGroup
        exclusive
        color="primary"
        value={view}
        onChange={handleChange}
        aria-label={t("dataOrVisualisations")}
        sx={{
          alignSelf: "center",
          "& .MuiToggleButton-root": { px: 3 },
        }}
      >
        <ToggleButton value="data">
          <FormatListBulletedIcon sx={{ mr: 1 }} />
          {t("data")}
        </ToggleButton>
        <ToggleButton value="visualisations">
          <QueryStatsIcon sx={{ mr: 1 }} />
          {t("visualisations")}
        </ToggleButton>
      </ToggleButtonGroup>
      {/* The data list stays mounted so its scroll position, filters and
          appended pages survive toggling. */}
      <Box hidden={view !== "data"}>{data}</Box>
      {vizMounted ? (
        <Box hidden={view !== "visualisations"}>{visualisations}</Box>
      ) : null}
    </Stack>
  );
}
