"use client";

import InputAdornment from "@mui/material/InputAdornment";
import TextField from "@mui/material/TextField";
import CloseIcon from "@mui/icons-material/Close";
import SearchIcon from "@mui/icons-material/Search";
import React, { useCallback, useMemo, useState } from "react";
import IconButton from "@mui/material/IconButton";
import { useDebounceCallback, useUpdateSearchParams } from "@/app/hooks";

export default function SearchTextField() {
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const search = useMemo(
    () => searchParams.get("search") ?? "",
    [searchParams],
  );
  const [searchValue, setSearchValue] = useState<string>(search);

  const debouncedUpdateParam = useDebounceCallback(
    (value: string) => updateSearchParams({ search: value, page: null }),
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
      placeholder="Rechercher…"
      onChange={onChange}
      slotProps={{
        input: {
          startAdornment: (
            <InputAdornment position="start">
              <SearchIcon />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={clear}
                sx={{
                  display: searchValue === "" ? "none" : "inline-flex",
                }}
              >
                <CloseIcon />
              </IconButton>
            </InputAdornment>
          ),
        },
      }}
      value={searchValue}
      fullWidth
    />
  );
}
