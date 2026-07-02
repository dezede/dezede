"use client";

import React, { useEffect, useState } from "react";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";

export type TTabPanel = {
  // Stable URL-hash slug for this tab (kept independent of the visible label).
  slug: string;
  label: string;
  content: React.ReactNode;
  // When true the panel mounts only while active (for heavy/interactive panels).
  lazy?: boolean;
};

/**
 * Generic client tab switcher whose active tab is mirrored into the URL hash
 * (e.g. `#index`), like `DossierTabs`. The hash is updated with
 * `history.replaceState` so switching never triggers a Next.js navigation.
 * `defaultIndex` is used when the URL has no (matching) hash.
 *
 * Set `syncHash={false}` to keep the active tab purely local — used when the
 * tabs live inside a modal (`SourceModal`), where writing to the page URL hash
 * would be misleading and would fight the underlying page's own hash state.
 */
export default function HashTabs({
  panels,
  defaultIndex = 0,
  syncHash = true,
}: {
  panels: TTabPanel[];
  defaultIndex?: number;
  syncHash?: boolean;
}) {
  const [tab, setTab] = useState(defaultIndex);

  useEffect(() => {
    if (!syncHash) {
      return;
    }
    const syncFromHash = () => {
      const slug = window.location.hash.replace(/^#/, "");
      const index = panels.findIndex((panel) => panel.slug === slug);
      setTab(index >= 0 ? index : defaultIndex);
    };
    syncFromHash();
    window.addEventListener("hashchange", syncFromHash);
    return () => window.removeEventListener("hashchange", syncFromHash);
    // `panels` is rebuilt each render but its slugs are stable.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [defaultIndex, syncHash]);

  const handleChange = (value: number) => {
    setTab(value);
    if (!syncHash) {
      return;
    }
    const url =
      value === defaultIndex
        ? window.location.pathname + window.location.search
        : `#${panels[value].slug}`;
    window.history.replaceState(null, "", url);
  };

  if (panels.length === 0) {
    return null;
  }

  return (
    <Box>
      <Box sx={{ borderBottom: 1, borderColor: "divider", mb: 3 }}>
        <Tabs
          value={tab}
          onChange={(_event, value) => handleChange(value)}
          variant="scrollable"
          allowScrollButtonsMobile
        >
          {panels.map((panel) => (
            <Tab
              key={panel.slug}
              label={panel.label}
              id={`hash-tab-${panel.slug}`}
              aria-controls={`hash-tabpanel-${panel.slug}`}
            />
          ))}
        </Tabs>
      </Box>
      {panels.map((panel, index) =>
        panel.lazy ? (
          tab === index ? (
            <Box
              key={panel.slug}
              role="tabpanel"
              id={`hash-tabpanel-${panel.slug}`}
              aria-labelledby={`hash-tab-${panel.slug}`}
            >
              {panel.content}
            </Box>
          ) : null
        ) : (
          <Box
            key={panel.slug}
            role="tabpanel"
            id={`hash-tabpanel-${panel.slug}`}
            aria-labelledby={`hash-tab-${panel.slug}`}
            hidden={tab !== index}
          >
            {panel.content}
          </Box>
        ),
      )}
    </Box>
  );
}
