"use client";

import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";

export type TDossierTabItem = {
  // Stable URL hash slug ('presentation', 'evenements', 'oeuvres', 'sources').
  // Kept independent of the visible labels so the link stays readable and
  // unchanged regardless of the dossier contents.
  slug: string;
  label: string;
  content: React.ReactNode;
};

// The pre-merge frontend used a fixed « Données » tab; keep that hash working
// by sending it to the first data tab (index 1).
const LEGACY_SLUGS: Record<string, number> = { donnees: 1, visualisations: 1 };

function hashToTab(hash: string, tabs: TDossierTabItem[]): number {
  // A kind panel may extend the hash with its sub-view
  // (e.g. #evenements-visualisations, see DossierKindPanel); only the first
  // segment selects the tab. Tab slugs never contain a dash.
  const slug = hash.replace(/^#/, "").split("-")[0];
  const index = tabs.findIndex((tab) => tab.slug === slug);
  if (index >= 0) {
    return index;
  }
  const legacy = LEGACY_SLUGS[slug];
  // Falls back to Présentation for a missing or out-of-range slug (e.g.
  // #oeuvres on a dossier without works).
  return legacy !== undefined && legacy < tabs.length ? legacy : 0;
}

/**
 * Client tab switcher for a dossier detail page: Présentation plus one tab per
 * kind of data the dossier presents (événements / œuvres / sources), mirroring
 * the Django dossier tabs. Every panel stays mounted (they are
 * server-rendered); the per-kind Visualisations live inside each kind's panel
 * (see DossierKindPanel) and load only when opened.
 *
 * The active tab is mirrored into the URL hash (e.g. `#evenements`) so it
 * survives reloads and is shareable. We use the hash with
 * `history.replaceState` rather than a query param so switching tabs is
 * instant: it never triggers a Next.js navigation (which would re-render the
 * server tree and lag).
 */
export default function DossierTabs({ tabs }: { tabs: TDossierTabItem[] }) {
  // Starts on Présentation so SSR/hydration match; the hash is read in the
  // effect below (the hash is not available during server rendering).
  const [tab, setTab] = useState(0);
  const slugs = tabs.map((item) => item.slug).join(",");

  useEffect(() => {
    const syncFromHash = () => setTab(hashToTab(window.location.hash, tabs));
    syncFromHash();
    // Keep in sync with back/forward navigation and manual hash edits.
    window.addEventListener("hashchange", syncFromHash);
    return () => window.removeEventListener("hashchange", syncFromHash);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slugs]);

  const handleChange = (value: number) => {
    setTab(value);
    // Update the hash without a Next.js navigation and without adding a history
    // entry. Présentation (the default) drops the hash to keep the URL clean.
    const url =
      value === 0
        ? window.location.pathname + window.location.search
        : `#${tabs[value].slug}`;
    window.history.replaceState(null, "", url);
    // replaceState fires no hashchange event; dispatch one so the kind panels
    // drop any `-visualisations` sub-view when their tab is left.
    window.dispatchEvent(new HashChangeEvent("hashchange"));
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
          {tabs.map((item, index) => (
            <Tab
              key={item.slug}
              label={item.label}
              id={`dossier-tab-${index}`}
              aria-controls={`dossier-tabpanel-${index}`}
            />
          ))}
        </Tabs>
      </Box>
      {tabs.map((item, index) => (
        <Box
          key={item.slug}
          role="tabpanel"
          id={`dossier-tabpanel-${index}`}
          aria-labelledby={`dossier-tab-${index}`}
          hidden={tab !== index}
        >
          {item.content}
        </Box>
      ))}
    </Box>
  );
}
