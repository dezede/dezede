"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Tooltip,
  useMap,
  useMapEvents,
} from "react-leaflet";
import { LatLngBounds } from "leaflet";
import "leaflet/dist/leaflet.css";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import CircularProgress from "@mui/material/CircularProgress";
import Skeleton from "@mui/material/Skeleton";
import { useTheme } from "@mui/material/styles";
import { useTranslations } from "next-intl";
import { useUpdateSearchParams } from "@/app/hooks";
import { EVENT_FILTER_PARAMS } from "@/app/utils";
import { TGeoFeature, TGeoJson } from "@/app/types";

// Marker sizing mirrors libretto/templates/libretto/include/map.html: the radius
// grows from MIN_RADIUS to MAX_RADIUS as the event count goes from the smallest
// to the largest in the current set, shaped by the "growth" exponent.
const MIN_RADIUS = 5;
const MAX_RADIUS = 30;

// Fixed map tuning. These used to be user-adjustable ("Niveau de détail" and
// "Proportion des points" sliders); they are now hard-coded defaults.
const MIN_PLACES = 10;
const GROWTH = 0.5;

function computeRadius(
  n: number,
  minValue: number,
  maxValue: number,
  growth: number,
): number {
  if (maxValue <= minValue) {
    return MIN_RADIUS;
  }
  return (
    MIN_RADIUS +
    Math.pow((n - minValue) / (maxValue - minValue), growth) *
      (MAX_RADIUS - MIN_RADIUS)
  );
}

// `geojsonUrl` may already carry query params (the dossier maps pass
// `…/geojson/?kind=oeuvres`); merge them with the map's own params so the
// final URL never ends up with two `?`.
function buildGeojsonUrl(geojsonUrl: string, params: URLSearchParams): string {
  const [path, query] = geojsonUrl.split("?", 2);
  if (query) {
    for (const [key, value] of new URLSearchParams(query)) {
      params.set(key, value);
    }
  }
  return `${path}?${params.toString()}`;
}

function MapLayer({
  filterQuery,
  minPlaces,
  growth,
  onLoadingChange,
  geojsonUrl,
  clickFilter,
  initialFeatures,
}: {
  filterQuery: string;
  minPlaces: number;
  growth: number;
  onLoadingChange: (loading: boolean) => void;
  geojsonUrl: string;
  clickFilter: boolean;
  initialFeatures: TGeoFeature[];
}) {
  const theme = useTheme();
  const map = useMap();
  const { updateSearchParams } = useUpdateSearchParams();
  // Seeded with the features the parent already fetched to frame the map, so the
  // markers are visible immediately rather than after a second round-trip.
  const [features, setFeatures] = useState<TGeoFeature[]>(initialFeatures);
  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(async () => {
    const params = new URLSearchParams(filterQuery);
    params.set("min_places", minPlaces.toString());
    // Like the Django map, scope the aggregation to the current viewport so the
    // "niveau de détail" slider adapts to what is on screen.
    try {
      params.set("bbox", map.getBounds().toBBoxString());
    } catch {
      // Map not ready yet; fetch without a bbox.
    }
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    onLoadingChange(true);
    try {
      const response = await fetch(buildGeojsonUrl(geojsonUrl, params), {
        signal: controller.signal,
      });
      const data: TGeoJson | null = response.ok ? await response.json() : null;
      const feats = data?.features ?? [];
      setFeatures(feats);
      // The map is framed once by the parent before mount; panning/zooming
      // afterwards must not be fought by an automatic re-centring.
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        setFeatures([]);
      }
    } finally {
      // An aborted request must not hide the spinner of its replacement.
      if (!controller.signal.aborted) {
        onLoadingChange(false);
      }
    }
  }, [filterQuery, minPlaces, map, onLoadingChange, geojsonUrl]);

  useEffect(() => {
    load();
  }, [load]);

  // Refetch with the new bounding box whenever the user pans or zooms.
  useMapEvents({
    moveend: () => {
      load();
    },
  });

  const maxValue = features.reduce(
    (max, feature) => Math.max(max, feature.properties.n),
    1,
  );

  return (
    <>
      {features.map((feature) => (
        <CircleMarker
          key={feature.properties.lieu_pk}
          center={[
            feature.geometry.coordinates[1],
            feature.geometry.coordinates[0],
          ]}
          radius={computeRadius(feature.properties.n, 1, maxValue, growth)}
          pathOptions={{
            color: theme.palette.primary.main,
            fillColor: theme.palette.primary.main,
            weight: 1,
            fillOpacity: 0.6,
          }}
          eventHandlers={
            clickFilter
              ? {
                  click: () =>
                    updateSearchParams({
                      lieu: `|${feature.properties.lieu_pk}|`,
                      page: null,
                    }),
                }
              : {}
          }
        >
          <Tooltip>{feature.properties.tooltip}</Tooltip>
        </CircleMarker>
      ))}
    </>
  );
}

export default function EventMap({
  geojsonUrl = "/api/evenements/geojson/",
  clickFilter = true,
}: {
  geojsonUrl?: string;
  clickFilter?: boolean;
} = {}) {
  const t = useTranslations("events");
  const { searchParams } = useUpdateSearchParams();
  const [loading, setLoading] = useState(true);

  // Current filters, so the map reflects the same subset as the list.
  const filterQuery = (() => {
    const params = new URLSearchParams();
    for (const key of EVENT_FILTER_PARAMS) {
      const value = searchParams.get(key);
      if (value) {
        params.set(key, value);
      }
    }
    return params.toString();
  })();

  const handleLoadingChange = useCallback(
    (value: boolean) => setLoading(value),
    [],
  );

  // Fetch the GeoJSON once before mounting the map so it can be initialised
  // directly at the data's extent. This avoids the visible pan/zoom Leaflet
  // would otherwise animate when fitting bounds after the map is already shown.
  // `null` means "still loading"; once set, `bounds === null` means no features.
  const [initialView, setInitialView] = useState<{
    bounds: LatLngBounds | null;
    features: TGeoFeature[];
  } | null>(null);

  useEffect(() => {
    // The cleanup aborts the in-flight request; the aborted fetch is caught as
    // an AbortError below and ignored, so React StrictMode's double-mount (dev)
    // simply re-runs the fetch rather than leaving the map stuck on loading.
    const controller = new AbortController();
    (async () => {
      const params = new URLSearchParams(filterQuery);
      params.set("min_places", MIN_PLACES.toString());
      try {
        const response = await fetch(buildGeojsonUrl(geojsonUrl, params), {
          signal: controller.signal,
        });
        const data: TGeoJson | null = response.ok
          ? await response.json()
          : null;
        const feats = data?.features ?? [];
        let bounds: LatLngBounds | null = null;
        if (feats.length > 0) {
          const b = new LatLngBounds(
            feats.map((feature) => [
              feature.geometry.coordinates[1],
              feature.geometry.coordinates[0],
            ]),
          );
          if (b.isValid()) {
            bounds = b;
          }
        }
        setInitialView({ bounds, features: feats });
      } catch (error) {
        if ((error as Error).name !== "AbortError") {
          setInitialView({ bounds: null, features: [] });
        }
      }
    })();
    return () => controller.abort();
    // Run once on mount: the initial frame is fixed from the filters in effect
    // at that moment. Later filter changes update the markers via MapLayer, not
    // the framing.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Initialise the map already framed on the data; fall back to the France-wide
  // default view only when the first fetch returned no features.
  const viewProps = initialView?.bounds
    ? {
        bounds: initialView.bounds,
        boundsOptions: { padding: [40, 40] as [number, number] },
      }
    : { center: [46.6, 2.4] as [number, number], zoom: 5 };

  return (
    <Stack spacing={1}>
      {initialView === null ? (
        <Skeleton variant="rectangular" height={400} />
      ) : (
        <Box
          sx={{ height: 400, position: "relative" }}
          role="img"
          aria-label={t("map")}
        >
          {loading ? (
            <Box
              sx={{
                position: "absolute",
                zIndex: 1000,
                top: 8,
                right: 8,
              }}
            >
              <CircularProgress size={24} />
            </Box>
          ) : null}
          <MapContainer
            {...viewProps}
            minZoom={2}
            maxZoom={16}
            style={{ height: "100%", width: "100%" }}
            scrollWheelZoom
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapLayer
              filterQuery={filterQuery}
              minPlaces={MIN_PLACES}
              growth={GROWTH}
              onLoadingChange={handleLoadingChange}
              geojsonUrl={geojsonUrl}
              clickFilter={clickFilter}
              initialFeatures={initialView.features}
            />
          </MapContainer>
        </Box>
      )}
    </Stack>
  );
}
