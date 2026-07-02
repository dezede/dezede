"use client";

import InputAdornment from "@mui/material/InputAdornment";
import TextField from "@mui/material/TextField";
import CloseIcon from "@mui/icons-material/Close";
import SearchIcon from "@mui/icons-material/Search";
import React, { useCallback, useState } from "react";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import { useTranslations } from "next-intl";
import { useDebounceCallback, useUpdateSearchParams } from "@/app/hooks";

export default function SearchTextField({
  param = "search",
  placeholder,
  size,
  shallow = false,
}: {
  param?: string;
  placeholder?: string;
  size?: "small" | "medium";
  // When true, update the URL via the History API instead of a Next.js
  // navigation. Use for pages that filter entirely client-side (e.g. the
  // virtualised autorité tables) so typing never triggers an RSC refetch.
  shallow?: boolean;
} = {}) {
  const t = useTranslations("common");
  const tLists = useTranslations("lists");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const [searchValue, setSearchValue] = useState<string>(
    searchParams.get(param) ?? "",
  );

  const debouncedUpdateParam = useDebounceCallback(
    (value: string) =>
      updateSearchParams({ [param]: value, page: null }, { shallow }),
    300,
  );

  const updateSearchValue = useCallback(
    (value: string) => {
      setSearchValue(value);
      debouncedUpdateParam(value);
    },
    [debouncedUpdateParam],
  );

  const clear = useCallback(() => updateSearchValue(""), [updateSearchValue]);

  const onChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) =>
      updateSearchValue(event.target.value),
    [updateSearchValue],
  );

  return (
    <TextField
      placeholder={placeholder ?? t("searchPlaceholder")}
      size={size}
      onChange={onChange}
      autoComplete="off"
      slotProps={{
        input: {
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <Tooltip title={tLists("clear")}>
                <IconButton
                  onClick={clear}
                  aria-label={tLists("clear")}
                  sx={{
                    display: searchValue === "" ? "none" : "inline-flex",
                  }}
                >
                  <CloseIcon />
                </IconButton>
              </Tooltip>
            </InputAdornment>
          ),
        },
      }}
      value={searchValue}
      fullWidth
    />
  );
}
