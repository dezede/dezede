import { Suspense } from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";
import {
  TDossierDetail,
  TDossierSources,
  TDossierWork,
  TEventFacets,
  TPaginated,
  TQueryParams,
  TSearchParams,
  TSource,
} from "@/app/types";
import { getTranslations } from "next-intl/server";
import {
  fetchPublicJson,
  eventFilterParams,
  sourceFilterParams,
  workFilterParams,
} from "@/app/events";
import EventFilterForm from "./EventFilterForm";
import EventList, { EVENTS_PER_PAGE } from "./EventList";
import WorkInfiniteScroll from "./WorkInfiniteScroll";
import WorkListItem from "./WorkListItem";
import WorkOrderSelect from "./WorkOrderSelect";
import DossierWorkFilterForm from "./DossierWorkFilterForm";
import SourceList from "./SourceList";
import SourceInfiniteScroll from "./SourceInfiniteScroll";
import SourceGroupPanel from "./SourceGroupPanel";
import Paper from "@mui/material/Paper";
import DossierSourceFilterForm, {
  TSourceFilterOptions,
} from "./DossierSourceFilterForm";
import { FilterOption } from "@/app/authorityColumns";
import Empty from "./Empty";

// The sticky filter-bar wrapper used by every "Données" tab: top is -32 to
// negate the scrollable <main>'s py: 4 so it tucks under the navbar.
const stickyBarSx = {
  position: "sticky" as const,
  top: -32,
  zIndex: 1100,
  bgcolor: "background.default",
};

// Keep only the string-valued query params (the filter values stored in the URL)
// so they can be merged into a client component's fetch URLSearchParams.
function toStringParams(params: TQueryParams): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [key, value] of Object.entries(params)) {
    if (typeof value === "string" && value !== "") {
      out[key] = value;
    }
  }
  return out;
}

const WORKS_PER_PAGE = 40;
const SOURCES_PER_PAGE = 40;

/**
 * The dossier's "Données" tab: its events (filter bar + cards + infinite scroll)
 * for a DossierDEvenements, its works (sortable rich list: title, authors,
 * genèse/création and sources) for a DossierDOeuvres, or its sources (icon +
 * title list) for a DossierDeSources.
 */
export default async function DossierData({
  dossier,
  searchParams,
}: {
  dossier: TDossierDetail;
  searchParams: TSearchParams;
}) {
  const t = await getTranslations("dossiers");
  if (dossier.kind === "evenements") {
    if (dossier.count === 0) {
      return <Empty>{t("noEventsInDossier")}</Empty>;
    }
    const endpoint = `/api/public/dossiers/${dossier.id}/evenements/`;
    const params = eventFilterParams(searchParams);
    // Same filters as the global event list, scoped to this dossier. The facets
    // (date-slider bounds + auth flag) come from the dossier's own event range.
    const facets = await fetchPublicJson<TEventFacets>(
      `/api/public/dossiers/${dossier.id}/facets/`,
      params,
    );
    return (
      <Stack spacing={3}>
        {/* Sticky filter bar, mirroring the global events page: top is -32 to
            negate the scrollable <main>'s py: 4 so it tucks under the navbar. */}
        <Box
          sx={{
            position: "sticky",
            top: -32,
            zIndex: 1100,
            bgcolor: "background.default",
          }}
        >
          <EventFilterForm facets={facets} />
        </Box>
        <Suspense
          key={JSON.stringify(params)}
          fallback={
            <Stack spacing={2}>
              {[...Array(EVENTS_PER_PAGE).keys()].map((index) => (
                <Skeleton key={index} variant="rectangular" height={140} />
              ))}
            </Stack>
          }
        >
          <EventList
            searchParams={searchParams}
            endpoint={endpoint}
            isAuthenticated={facets.is_authenticated}
          />
        </Suspense>
      </Stack>
    );
  }

  if (dossier.kind === "oeuvres") {
    const endpoint = `/api/public/dossiers/${dossier.id}/oeuvres/`;
    const params = workFilterParams(searchParams);
    // Two sort modes, mirroring DossierDOeuvresDataDetail: work name (default,
    // tree order) or world-premiere date.
    const orderBy = params.order_by === "creation_date" ? "creation_date" : "";
    const data = await fetchPublicJson<TPaginated<TDossierWork>>(endpoint, {
      ...params,
      limit: WORKS_PER_PAGE,
      offset: 0,
    });
    // Filter params (minus the sort, which the scroll threads separately)
    // forwarded to the infinite scroll so appended pages stay consistent with
    // the active filters.
    const scrollParams = toStringParams(params);
    delete scrollParams.order_by;
    return (
      <Stack spacing={3}>
        <Box sx={stickyBarSx}>
          <DossierWorkFilterForm dossierId={dossier.id} />
        </Box>
        {data.count === 0 ? (
          <Empty>{t("noWorksInDossier")}</Empty>
        ) : (
          <Stack spacing={2}>
            <Stack
              direction="row"
              spacing={2}
              alignItems="center"
              justifyContent="space-between"
              flexWrap="wrap"
              useFlexGap
            >
              <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                {t("workCount", { count: data.count })}
              </Typography>
              <WorkOrderSelect />
            </Stack>
            <Stack spacing={2}>
              {data.results.map((work) => (
                <WorkListItem
                  key={`${work.meta.type}-${work.id}`}
                  work={work}
                />
              ))}
            </Stack>
            {/* Keyed by the active filters+sort so it remounts (drops appended
                pages) whenever they change. */}
            <WorkInfiniteScroll
              key={JSON.stringify(params)}
              apiList={endpoint}
              orderBy={orderBy}
              params={scrollParams}
              perPage={WORKS_PER_PAGE}
              totalCount={data.count}
              startOffset={WORKS_PER_PAGE}
            />
          </Stack>
        )}
      </Stack>
    );
  }

  if (dossier.kind === "sources") {
    const endpoint = `/api/public/dossiers/${dossier.id}/sources/`;
    const params = sourceFilterParams(searchParams);
    const stringParams = toStringParams(params);
    const options = await fetchPublicJson<TSourceFilterOptions>(
      `/api/public/dossiers/${dossier.id}/sources_filters/`,
    );
    // When a single source type is selected, the backend returns a flat
    // paginated list of just that type; otherwise it groups by type (one block
    // per type, each paginated on its own — mirroring the related-sources panels
    // on autorité/event pages).
    const typeFilter = stringParams.type;
    // "Par date" drops the type grouping for a single flat chronological list
    // (mirrored by the backend's order_by=date branch).
    const byDate = stringParams.order_by === "date";
    const filterBar = (
      <Box sx={stickyBarSx}>
        <DossierSourceFilterForm dossierId={dossier.id} options={options} />
      </Box>
    );

    if (typeFilter && !byDate) {
      // A single selected source type: one flat paginated list under that type's
      // heading (fetched from the same type-ahead endpoint the filter uses).
      const data = await fetchPublicJson<TPaginated<TSource>>(endpoint, {
        ...params,
        limit: SOURCES_PER_PAGE,
        offset: 0,
      });
      const typeOptions = await fetchPublicJson<FilterOption[]>(
        `/api/public/dossiers/${dossier.id}/source_types/`,
        { ids: typeFilter },
      );
      const typeLabel = typeOptions[0]?.label;
      const list = (
        <>
          <SourceList sources={data.results} modal px={1.5} />
          {data.count > data.results.length ? (
            <SourceInfiniteScroll
              key={JSON.stringify(stringParams)}
              apiList={endpoint}
              params={stringParams}
              perPage={SOURCES_PER_PAGE}
              totalCount={data.count}
              startOffset={data.results.length}
              modal
            />
          ) : null}
        </>
      );
      return (
        <Stack spacing={3}>
          {filterBar}
          {data.count === 0 ? (
            <Empty>{t("noSourcesInDossier")}</Empty>
          ) : (
            <Stack spacing={2}>
              <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                {t("sourceCount", { count: data.count })}
              </Typography>
              {typeLabel ? (
                <SourceGroupPanel heading={typeLabel}>{list}</SourceGroupPanel>
              ) : (
                <Paper variant="outlined">{list}</Paper>
              )}
            </Stack>
          )}
        </Stack>
      );
    }

    // Grouped blocks: by year when sorting "Par date", otherwise by source type.
    // Both share the {count, groups} shape; only the per-group load-more param
    // differs (year vs type).
    const groupParam = byDate ? "year" : "type";
    const data = await fetchPublicJson<TDossierSources>(endpoint, params);
    return (
      <Stack spacing={3}>
        {filterBar}
        {data.count === 0 ? (
          <Empty>{t("noSourcesInDossier")}</Empty>
        ) : (
          <Stack spacing={2}>
            <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
              {t("sourceCount", { count: data.count })}
            </Typography>
            <Stack spacing={1.5}>
              {data.groups.map((group) => (
                <SourceGroupPanel
                  key={`${groupParam}-${group.type_id}`}
                  heading={group.type}
                >
                  <SourceList sources={group.results} modal px={1.5} />
                  {group.count > group.results.length ? (
                    <SourceInfiniteScroll
                      key={JSON.stringify(stringParams)}
                      apiList={endpoint}
                      params={{
                        ...stringParams,
                        [groupParam]: String(group.type_id),
                      }}
                      perPage={SOURCES_PER_PAGE}
                      totalCount={group.count}
                      startOffset={group.results.length}
                      modal
                    />
                  ) : null}
                </SourceGroupPanel>
              ))}
            </Stack>
          </Stack>
        )}
      </Stack>
    );
  }

  return <Empty>{t("dataUnavailable")}</Empty>;
}
