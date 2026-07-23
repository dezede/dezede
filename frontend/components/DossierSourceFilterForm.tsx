"use client";

import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import { useTranslations } from "next-intl";
import { useUpdateSearchParams } from "@/app/hooks";
import { FilterOption } from "@/app/authorityColumns";
import SearchTextField from "./SearchTextField";
import FilterSelect from "./FilterSelect";
import AsyncFilterAutocomplete from "./AsyncFilterAutocomplete";

export type TSourceFilterOptions = {
  icons: FilterOption[];
  ancrage: FilterOption[];
};

/**
 * Filter bar for a dossier de sources' "Données" tab, mirroring the standalone
 * sources index filters but scoped to the dossier: free-text search, content
 * type (icons), source type (type-ahead, see {@link AsyncFilterAutocomplete}),
 * century (ancrage), and a default ↔ by-date sort. Each control writes a URL
 * search param; the server component re-renders the list on change (see
 * {@link DossierData}).
 */
export default function DossierSourceFilterForm({
  dossierId,
  options,
}: {
  dossierId: number;
  options: TSourceFilterOptions;
}) {
  const t = useTranslations("authority");
  const tDossiers = useTranslations("dossiers");
  const tLists = useTranslations("lists");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const byDate = searchParams.get("order_by") === "date";

  return (
    <Paper sx={{ p: 1.5 }}>
      <Box
        sx={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: 1.5,
        }}
      >
        <Box sx={{ flex: "2 1 220px", minWidth: 200 }}>
          <SearchTextField
            param="q"
            placeholder={t("sources.searchPlaceholder")}
            size="small"
          />
        </Box>
        <Box sx={{ flex: "1 1 160px", minWidth: 150 }}>
          <FilterSelect
            param="icons"
            label={t("sources.filters.icons")}
            options={options.icons}
            getOptionLabel={(option) => t(`sourceTypes.${option.value}`)}
          />
        </Box>
        <Box sx={{ flex: "1 1 160px", minWidth: 150 }}>
          <AsyncFilterAutocomplete
            param="type"
            label={t("sources.filters.type")}
            endpoint={`/api/public/dossiers/${dossierId}/source_types/`}
          />
        </Box>
        <Box sx={{ flex: "1 1 160px", minWidth: 150 }}>
          <FilterSelect
            param="ancrage"
            label={t("sources.filters.ancrage")}
            options={options.ancrage}
          />
        </Box>
        <ToggleButtonGroup
          value={byDate ? "date" : "default"}
          exclusive
          size="small"
          sx={{ flex: "0 0 auto" }}
          onChange={(event, value) => {
            if (value !== null) {
              updateSearchParams({
                order_by: value === "date" ? "date" : null,
                page: null,
              });
            }
          }}
          aria-label={tLists("orderBy")}
        >
          <ToggleButton value="default">
            {tDossiers("sourceOrder.default")}
          </ToggleButton>
          <ToggleButton value="date">
            {tDossiers("sourceOrder.date")}
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>
    </Paper>
  );
}
