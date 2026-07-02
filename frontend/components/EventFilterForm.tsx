"use client";

import { useState } from "react";
import Paper from "@mui/material/Paper";
import Slider from "@mui/material/Slider";
import Typography from "@mui/material/Typography";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Box from "@mui/material/Box";
import { useTranslations } from "next-intl";
import { useUpdateSearchParams } from "@/app/hooks";
import SearchTextField from "./SearchTextField";
import AsyncMultiAutocomplete from "./AsyncMultiAutocomplete";
import {
  TEventFacets,
  TRelatedEnsemble,
  TRelatedPerson,
  TRelatedPlace,
  TWorkFull,
} from "@/app/types";
import { getPlaceLabel } from "@/format/PlaceChip";
import { getPersonLabel } from "@/format/PersonChip";
import { getEnsembleLabel } from "@/format/EnsembleChip";
import { getWorkLabel } from "@/format/WorkChip";

function YearRange({ min, max }: { min: number; max: number }) {
  const t = useTranslations("events");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const start = parseInt(searchParams.get("dates_0") ?? "", 10);
  const end = parseInt(searchParams.get("dates_1") ?? "", 10);
  const [value, setValue] = useState<number[]>([
    Number.isNaN(start) ? min : start,
    Number.isNaN(end) ? max : end,
  ]);

  return (
    <Box>
      <Typography
        variant="body2"
        color="text.primary"
        sx={{ display: "block", lineHeight: 1.2, fontWeight: 500, textAlign: "center" }}
      >
        {t("years", { start: value[0], end: value[1] })}
      </Typography>
      <Box px={1}>
        <Slider
          size="small"
          value={value}
          min={min}
          max={max}
          onChange={(event, newValue) => setValue(newValue as number[])}
          onChangeCommitted={(event, newValue) => {
            const [low, high] = newValue as number[];
            updateSearchParams({
              dates_0: low,
              dates_1: high,
              page: null,
            });
          }}
          valueLabelDisplay="auto"
          disableSwap
          aria-label={t("allYears")}
          sx={{ mt: 0, mb: 0, py: 0.5 }}
        />
      </Box>
    </Box>
  );
}

export default function EventFilterForm({ facets }: { facets: TEventFacets }) {
  const t = useTranslations("events");
  // For localising the tonalité in work option labels.
  const tWork = useTranslations("work");
  // For localising the pseudonyme suffix in person option labels.
  const tCommon = useTranslations("common");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const bySeason = searchParams.get("par_saison") === "True";

  // Sticky top bar: a short first row (free search, year range, season toggle)
  // above a second row holding all four autocomplete filters together.
  return (
    <Paper sx={{ p: 1.5 }}>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
        <Box
          sx={{
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            gap: 1.5,
          }}
        >
          <Box sx={{ flex: "2 1 240px", minWidth: 220 }}>
            <SearchTextField
              param="q"
              placeholder={t("freeSearchPlaceholder")}
              size="small"
            />
          </Box>
          <Box sx={{ flex: "1 1 220px", minWidth: 200 }}>
            <YearRange
              min={facets.date_range.min_year}
              max={facets.date_range.max_year}
            />
          </Box>
          <ToggleButtonGroup
            value={bySeason ? "season" : "civil"}
            exclusive
            size="small"
            sx={{ flex: "0 0 auto" }}
            onChange={(event, value) => {
              if (value !== null) {
                updateSearchParams({
                  par_saison: value === "season" ? "True" : null,
                  page: null,
                });
              }
            }}
          >
            <ToggleButton value="civil">{t("byCivilYear")}</ToggleButton>
            <ToggleButton value="season">{t("bySeason")}</ToggleButton>
          </ToggleButtonGroup>
        </Box>
        <Box
          sx={{
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            gap: 1.5,
          }}
        >
          <Box sx={{ flex: "1 1 200px", minWidth: 180 }}>
            <AsyncMultiAutocomplete<TRelatedPlace>
              param="lieu"
              endpoint="lieux"
              label={t("filterPlace")}
              getOptionLabel={(option) => getPlaceLabel(option)}
              groupBy={(option) => option.nature?.nom ?? ""}
            />
          </Box>
          <Box sx={{ flex: "1 1 200px", minWidth: 180 }}>
            <AsyncMultiAutocomplete<TWorkFull>
              param="oeuvre"
              endpoint="oeuvres"
              label={t("filterWork")}
              getOptionLabel={(option) => getWorkLabel(option, tWork)}
            />
          </Box>
          <Box sx={{ flex: "1 1 200px", minWidth: 180 }}>
            <AsyncMultiAutocomplete<TRelatedPerson>
              param="individu"
              endpoint="individus"
              label={t("filterPerson")}
              getOptionLabel={(option) => getPersonLabel(option, tCommon)}
            />
          </Box>
          <Box sx={{ flex: "1 1 200px", minWidth: 180 }}>
            <AsyncMultiAutocomplete<TRelatedEnsemble>
              param="ensemble"
              endpoint="ensembles"
              label={t("filterEnsemble")}
              getOptionLabel={getEnsembleLabel}
            />
          </Box>
        </Box>
      </Box>
    </Paper>
  );
}
