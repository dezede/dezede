"use client";

import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";
import { useTranslations } from "next-intl";
import { useUpdateSearchParams } from "@/app/hooks";

/**
 * "Order by" dropdown mirroring the Django event list, sitting next to the
 * result count. Maps directly onto the `order_by` query param consumed by the
 * API (absent = chronological, "reversed" = reverse chronological).
 */
export default function EventOrderSelect() {
  const t = useTranslations("lists");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const value = searchParams.get("order_by") === "reversed" ? "reversed" : "";

  return (
    <TextField
      select
      size="small"
      label={t("orderBy")}
      value={value}
      onChange={(event) =>
        updateSearchParams({
          order_by: event.target.value === "reversed" ? "reversed" : null,
          page: null,
        })
      }
      sx={{ minWidth: 260 }}
    >
      <MenuItem value="">{t("eventOrder.asc")}</MenuItem>
      <MenuItem value="reversed">{t("eventOrder.desc")}</MenuItem>
    </TextField>
  );
}
