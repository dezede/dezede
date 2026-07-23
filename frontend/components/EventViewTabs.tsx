"use client";

import React, { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import dynamic from "next/dynamic";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Skeleton from "@mui/material/Skeleton";
import FormatListBulletedIcon from "@mui/icons-material/FormatListBulleted";
import MapOutlinedIcon from "@mui/icons-material/MapOutlined";

// Leaflet touches `window`, so the map is client-only.
const EventMap = dynamic(() => import("./EventMap"), {
  ssr: false,
  loading: () => <Skeleton variant="rectangular" height={400} />,
});

// Stable URL hash slugs, indexed by tab position (Liste / Carte). Liste is the
// default and drops the hash to keep the URL clean.
const TAB_SLUGS = ["liste", "carte"];

function hashToTab(hash: string): number {
  const index = TAB_SLUGS.indexOf(hash.replace(/^#/, ""));
  return index >= 0 ? index : 0;
}

/**
 * List/Map switcher for the events view, rendered only for authenticated
 * visitors (the map is theirs alone). The list (a server-rendered node passed in
 * as `list`) stays mounted so its infinite-scroll state survives a switch; the
 * Leaflet map mounts on first open and stays mounted so its pan/zoom and the
 * geojson fetch are not lost when switching back.
 *
 * The active tab is mirrored into the URL hash (`#carte`) via
 * `history.replaceState` rather than a query param, so switching is instant and
 * never triggers a Next.js navigation (which would re-run the server tree and
 * reset the filter search-params handling).
 */
export default function EventViewTabs({ list }: { list: React.ReactNode }) {
  const t = useTranslations("event");
  // Starts on Liste so SSR/hydration match; the hash is read in the effect
  // below (it is not available during server rendering).
  const [tab, setTab] = useState(0);
  // Once the map has been opened we keep it mounted (hidden) so its pan/zoom and
  // the geojson fetch survive switching back to the list.
  const [hasOpenedMap, setHasOpenedMap] = useState(false);

  const selectTab = (value: number) => {
    setTab(value);
    if (value === 1) {
      setHasOpenedMap(true);
    }
  };

  useEffect(() => {
    const syncFromHash = () => selectTab(hashToTab(window.location.hash));
    syncFromHash();
    // Keep in sync with back/forward navigation and manual hash edits.
    window.addEventListener("hashchange", syncFromHash);
    return () => window.removeEventListener("hashchange", syncFromHash);
  }, []);

  const handleChange = (value: number) => {
    selectTab(value);
    // Update the hash without a Next.js navigation and without adding a history
    // entry. Liste (the default) drops the hash to keep the URL clean.
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
            icon={<FormatListBulletedIcon />}
            iconPosition="start"
            label={t("viewList")}
            id="event-view-tab-0"
            aria-controls="event-view-tabpanel-0"
          />
          <Tab
            icon={<MapOutlinedIcon />}
            iconPosition="start"
            label={t("viewMap")}
            id="event-view-tab-1"
            aria-controls="event-view-tabpanel-1"
          />
        </Tabs>
      </Box>
      <Box
        role="tabpanel"
        id="event-view-tabpanel-0"
        aria-labelledby="event-view-tab-0"
        hidden={tab !== 0}
      >
        {list}
      </Box>
      {hasOpenedMap ? (
        <Box
          role="tabpanel"
          id="event-view-tabpanel-1"
          aria-labelledby="event-view-tab-1"
          hidden={tab !== 1}
        >
          <EventMap />
        </Box>
      ) : null}
    </Box>
  );
}
