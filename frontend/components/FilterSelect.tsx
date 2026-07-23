"use client";

import Box from "@mui/material/Box";
import MenuItem from "@mui/material/MenuItem";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import CloseIcon from "@mui/icons-material/Close";
import type { SxProps, Theme } from "@mui/material/styles";
import { useTranslations } from "next-intl";
import { useUpdateSearchParams } from "@/app/hooks";
import { FilterOption } from "@/app/authorityColumns";

/**
 * A single-value `<select>` backed by a URL search param, for the filter bars
 * (content type, century, ensemble/part type…). The leading empty option
 * ("Tous") clears the param, as does the × clear button shown once a value is
 * picked (matching the autocomplete fields' clear indicator). `getOptionLabel`
 * lets a caller localise the option text (e.g. centuries / source content types)
 * instead of using the API-sent French label. `shallow` uses the History API
 * (no server round-trip) for the authority grids, which refetch client-side.
 *
 * The clear button is an absolutely-positioned overlay rather than an
 * `endAdornment`: MUI's `Select` (rendered for `select` TextFields) discards the
 * input's `endAdornment`, so the overlay is the reliable way to add one.
 */
export default function FilterSelect({
  param,
  label,
  options,
  getOptionLabel,
  shallow = false,
  fullWidth = true,
  sx,
}: {
  param: string;
  label: string;
  options: FilterOption[];
  getOptionLabel?: (option: FilterOption) => string;
  shallow?: boolean;
  fullWidth?: boolean;
  sx?: SxProps<Theme>;
}) {
  const tCommon = useTranslations("common");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const value = searchParams.get(param) ?? "";
  const clear = () =>
    updateSearchParams({ [param]: null, page: null }, { shallow });

  return (
    <Box
      sx={[
        { position: "relative", display: fullWidth ? "block" : "inline-block" },
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
    >
      <TextField
        select
        size="small"
        fullWidth
        label={label}
        value={value}
        onChange={(event) =>
          updateSearchParams(
            { [param]: event.target.value || null, page: null },
            { shallow },
          )
        }
        // Keep the selected label clear of the overlaid × (the native dropdown
        // arrow already reserves ~32px; this widens it to fit both).
        sx={
          value !== ""
            ? { "& .MuiSelect-select": { pr: "52px !important" } }
            : undefined
        }
      >
        <MenuItem value="">{tCommon("all")}</MenuItem>
        {options.map((option) => (
          <MenuItem key={option.value} value={String(option.value)}>
            {getOptionLabel ? getOptionLabel(option) : option.label}
          </MenuItem>
        ))}
      </TextField>
      {value !== "" ? (
        <Tooltip title={tCommon("clear")}>
          <IconButton
            size="small"
            aria-label={tCommon("clear")}
            onClick={clear}
            sx={{
              position: "absolute",
              right: 26,
              top: "50%",
              transform: "translateY(-50%)",
            }}
          >
            <CloseIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      ) : null}
    </Box>
  );
}
