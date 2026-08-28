"use client";

import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import { useTranslations } from "next-intl";
import { TRelatedEnsemble, TRelatedPerson } from "@/app/types";
import { getPersonLabel } from "@/format/PersonChip";
import { getEnsembleLabel } from "@/format/EnsembleChip";
import SearchTextField from "./SearchTextField";
import AsyncFilterAutocomplete from "./AsyncFilterAutocomplete";
import AsyncMultiAutocomplete from "./AsyncMultiAutocomplete";

/**
 * Filter bar for a dossier d'œuvres' "Données" tab: free-text search, a genre
 * type-ahead (scoped to the genres present in the dossier, see
 * {@link AsyncFilterAutocomplete}) and author/composer multi-selects reusing the
 * shared {@link AsyncMultiAutocomplete} over the events' individu/ensemble
 * type-ahead endpoints. The name/premiere sort stays in the existing
 * {@link WorkOrderSelect} above the list.
 */
export default function DossierWorkFilterForm({
  dossierId,
}: {
  dossierId: number;
}) {
  const t = useTranslations("authority");
  const tEvents = useTranslations("events");
  const tCommon = useTranslations("common");

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
            placeholder={t("oeuvres.searchPlaceholder")}
            size="small"
          />
        </Box>
        <Box sx={{ flex: "1 1 180px", minWidth: 160 }}>
          <AsyncFilterAutocomplete
            param="genre"
            label={t("oeuvres.columns.genre")}
            endpoint={`/api/public/dossiers/${dossierId}/genres/`}
          />
        </Box>
        <Box sx={{ flex: "1 1 200px", minWidth: 180 }}>
          <AsyncMultiAutocomplete<TRelatedPerson>
            param="individu"
            endpoint="individus"
            label={tEvents("filterPerson")}
            getOptionLabel={(option) => getPersonLabel(option, tCommon)}
          />
        </Box>
        <Box sx={{ flex: "1 1 200px", minWidth: 180 }}>
          <AsyncMultiAutocomplete<TRelatedEnsemble>
            param="ensemble"
            endpoint="ensembles"
            label={tEvents("filterEnsemble")}
            getOptionLabel={getEnsembleLabel}
          />
        </Box>
      </Box>
    </Paper>
  );
}
