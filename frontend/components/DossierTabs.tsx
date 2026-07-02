"use client";

import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import { useTranslations } from "next-intl";

// Stable URL hash slugs, indexed by tab position (Présentation / Données /
// Visualisations). Kept independent of the visible labels so the link stays
// readable and unchanged regardless of the dossier kind.
const TAB_SLUGS = ["presentation", "donnees", "visualisations"];

function hashToTab(hash: string, tabCount: number): number {
  // Falls back to Présentation for a missing or out-of-range slug (e.g.
  // #visualisations on a dossier without visualisations).
  const index = TAB_SLUGS.indexOf(hash.replace(/^#/, ""));
  return index >= 0 && index < tabCount ? index : 0;
}

/**
 * Client tab switcher for a dossier detail page (Présentation / Données /
 * Visualisations), mirroring the Django dossier tabs. The presentation and data
 * panels stay mounted (server-rendered); the visualisations panel is mounted on
 * demand so Leaflet and the charts load only when opened.
 *
 * The active tab is mirrored into the URL hash (e.g. `#donnees`) so it survives
 * reloads and is shareable. We use the hash with `history.replaceState` rather
 * than a query param so switching tabs is instant: it never triggers a Next.js
 * navigation (which would re-render the server tree and lag).
 */
export default function DossierTabs({
  presentation,
  data,
  visualisations,
  dataLabel,
  hasVisualisations,
}: {
  presentation: React.ReactNode;
  data: React.ReactNode;
  visualisations: React.ReactNode;
  dataLabel: string;
  hasVisualisations: boolean;
}) {
  const t = useTranslations("dossiers");
  const tabCount = hasVisualisations ? 3 : 2;
  // Starts on Présentation so SSR/hydration match; the hash is read in the
  // effect below (the hash is not available during server rendering).
  const [tab, setTab] = useState(0);

  useEffect(() => {
    const syncFromHash = () =>
      setTab(hashToTab(window.location.hash, tabCount));
    syncFromHash();
    // Keep in sync with back/forward navigation and manual hash edits.
    window.addEventListener("hashchange", syncFromHash);
    return () => window.removeEventListener("hashchange", syncFromHash);
  }, [tabCount]);

  const handleChange = (value: number) => {
    setTab(value);
    // Update the hash without a Next.js navigation and without adding a history
    // entry. Présentation (the default) drops the hash to keep the URL clean.
    const url =
      value === 0
        ? window.location.pathname + window.location.search
        : `#${TAB_SLUGS[value]}`;
    window.history.replaceState(null, "", url);
  };

  return (
    <Box>
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs
          value={tab}
          onChange={(_event, value) => handleChange(value)}
          variant="scrollable"
          allowScrollButtonsMobile
        >
          <Tab
            label={t("presentation")}
            id="dossier-tab-0"
            aria-controls="dossier-tabpanel-0"
          />
          <Tab
            label={dataLabel}
            id="dossier-tab-1"
            aria-controls="dossier-tabpanel-1"
          />
          {hasVisualisations ? (
            <Tab
              label={t("visualisations")}
              id="dossier-tab-2"
              aria-controls="dossier-tabpanel-2"
            />
          ) : null}
        </Tabs>
      </Box>
      <Box
        role="tabpanel"
        id="dossier-tabpanel-0"
        aria-labelledby="dossier-tab-0"
        hidden={tab !== 0}
      >
        {presentation}
      </Box>
      <Box
        role="tabpanel"
        id="dossier-tabpanel-1"
        aria-labelledby="dossier-tab-1"
        hidden={tab !== 1}
      >
        {data}
      </Box>
      {hasVisualisations && tab === 2 ? (
        <Box
          role="tabpanel"
          id="dossier-tabpanel-2"
          aria-labelledby="dossier-tab-2"
        >
          {visualisations}
        </Box>
      ) : null}
    </Box>
  );
}
