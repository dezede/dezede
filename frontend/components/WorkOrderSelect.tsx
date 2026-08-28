"use client";

import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";
import { useTranslations } from "next-intl";
import { useUpdateSearchParams } from "@/app/hooks";

/**
 * "Order by" dropdown for a dossier d'œuvres works list, mirroring the two
 * Django ordering buttons. Maps onto the `order_by` query param consumed by the
 * dossier `oeuvres` endpoint (absent = work name / tree order, "creation_date" =
 * world-premiere date).
 */
export default function WorkOrderSelect() {
  const t = useTranslations("lists");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const value =
    searchParams.get("order_by") === "creation_date" ? "creation_date" : "";

  return (
    <TextField
      select
      size="small"
      label={t("orderBy")}
      value={value}
      onChange={(event) =>
        updateSearchParams({
          order_by:
            event.target.value === "creation_date" ? "creation_date" : null,
          page: null,
        })
      }
      sx={{ minWidth: 260 }}
    >
      <MenuItem value="">{t("workOrder.name")}</MenuItem>
      <MenuItem value="creation_date">{t("workOrder.creationDate")}</MenuItem>
    </TextField>
  );
}
