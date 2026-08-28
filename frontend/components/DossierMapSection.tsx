"use client";

import dynamic from "next/dynamic";
import Skeleton from "@mui/material/Skeleton";

// Leaflet touches `window`, so the map is client-only.
const EventMap = dynamic(() => import("./EventMap"), {
  ssr: false,
  loading: () => <Skeleton variant="rectangular" height={400} />,
});

/**
 * The dossier events map: same Leaflet map as the event list, but fed by the
 * dossier's own GeoJSON endpoint and without click-to-filter (a dossier is a
 * fixed selection).
 */
export default function DossierMapSection({
  geojsonUrl,
}: {
  geojsonUrl: string;
}) {
  return <EventMap geojsonUrl={geojsonUrl} clickFilter={false} />;
}
