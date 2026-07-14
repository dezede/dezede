"use client";

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import CircularProgress from "@mui/material/CircularProgress";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import { useTranslations } from "next-intl";
import { useAsyncSearch, useUpdateSearchParams } from "@/app/hooks";
import { apiGet } from "@/app/api";

type TEntity = { id: number };

/** `"|12|34|"` ↔ `[12, 34]` — the events' pipe-delimited pk-list URL encoding,
 * shared by every filter that stores a multi-selection in the URL. */
export function parsePkList(value: string | null): number[] {
  if (!value) {
    return [];
  }
  return value
    .split("|")
    .map((pk) => parseInt(pk, 10))
    .filter((pk) => !Number.isNaN(pk));
}

export function encodePkList(ids: number[]): string | null {
  return ids.length === 0 ? null : `|${ids.join("|")}|`;
}

/**
 * A URL-backed multi-select autocomplete over one of the
 * `/api/evenements/<endpoint>/` type-ahead endpoints (lieux, oeuvres, individus,
 * ensembles). Stores the selection as a pipe-delimited pk list in `?<param>=`,
 * restores the labels from that list on mount, and debounces the type-ahead.
 *
 * Shared by the events filter bar ({@link EventFilterForm}) and the dossier
 * d'œuvres filter bar ({@link DossierWorkFilterForm}).
 */
export default function AsyncMultiAutocomplete<T extends TEntity>({
  param,
  endpoint,
  label,
  getOptionLabel,
  renderOption,
}: {
  param: string;
  endpoint: string;
  label: string;
  getOptionLabel: (option: T) => string;
  renderOption?: (option: T) => React.ReactNode;
}) {
  const t = useTranslations("events");
  const tCommon = useTranslations("common");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const urlValue = searchParams.get(param);
  const [selected, setSelected] = useState<T[]>([]);
  // Start in the loading state when the URL already carries a pk list, so the
  // field shows the spinner on the first paint instead of flashing empty until
  // the restore fetch below resolves. This tracks only the URL-restore fetch;
  // the type-ahead's own loading comes from useAsyncSearch.
  const [restoreLoading, setRestoreLoading] = useState(
    () => parsePkList(urlValue).length > 0,
  );
  const [inputValue, setInputValue] = useState("");

  // Type-ahead options: the search endpoint returns a bare array of entities.
  const {
    results: options,
    loading: searchLoading,
    search: runSearch,
    reset: resetSearch,
  } = useAsyncSearch<T>(
    (query, signal) =>
      apiGet<T[]>(`/api/evenements/${endpoint}/`, { params: { q: query }, signal }),
    { debounceMs: 300 },
  );
  const loading = restoreLoading || searchLoading;

  // Restore the selection (labels) from the pk list in the URL. `syncedRef`
  // tracks the value we last reconciled, so our own changes don't refetch.
  const syncedRef = useRef<string | null>(null);
  useEffect(() => {
    const normalized = urlValue ?? null;
    if (syncedRef.current === normalized) {
      return;
    }
    syncedRef.current = normalized;
    const ids = parsePkList(urlValue);
    let cancelled = false;
    const restore = async () => {
      if (ids.length === 0) {
        if (!cancelled) {
          setSelected([]);
          setRestoreLoading(false);
        }
        return;
      }
      if (!cancelled) {
        setRestoreLoading(true);
      }
      try {
        const response = await fetch(
          `/api/evenements/${endpoint}/?ids=${encodeURIComponent(urlValue!)}`,
        );
        const data: T[] = response.ok ? await response.json() : [];
        if (!cancelled) {
          setSelected(data);
        }
      } catch {
        /* keep the previous selection on error */
      } finally {
        if (!cancelled) {
          setRestoreLoading(false);
        }
      }
    };
    restore();
    return () => {
      cancelled = true;
    };
  }, [urlValue, endpoint]);

  const onChange = useCallback(
    (event: React.SyntheticEvent, value: T[]) => {
      setSelected(value);
      const encoded = encodePkList(value.map((option) => option.id));
      syncedRef.current = encoded;
      updateSearchParams({ [param]: encoded, page: null });
    },
    [param, updateSearchParams],
  );

  const clearInput = useCallback(() => {
    setInputValue("");
    resetSearch();
  }, [resetSearch]);

  const mergedOptions = useMemo(() => {
    const ids = new Set(selected.map((option) => option.id));
    return [...selected, ...options.filter((option) => !ids.has(option.id))];
  }, [selected, options]);

  return (
    <Autocomplete<T, true, false, false>
      multiple
      fullWidth
      size="small"
      value={selected}
      onChange={onChange}
      options={mergedOptions}
      filterOptions={(items) => items}
      inputValue={inputValue}
      onInputChange={(event, value, reason) => {
        setInputValue(value);
        // The hook enters the loading state synchronously and clears on empty.
        // Only react to typing so we don't clobber the URL-restore spinner;
        // clearing/selecting drops the stale type-ahead options.
        if (reason === "input") {
          runSearch(value);
        } else {
          resetSearch();
        }
      }}
      getOptionLabel={getOptionLabel}
      getOptionKey={(option) => option.id}
      isOptionEqualToValue={(option, value) => option.id === value.id}
      renderOption={
        renderOption === undefined
          ? undefined
          : ({ key, ...props }, option) => (
              <Box key={key} component="li" {...props}>
                {renderOption(option)}
              </Box>
            )
      }
      loading={loading}
      loadingText={tCommon("loading")}
      noOptionsText={
        inputValue.trim() === "" ? t("typeToSearch") : tCommon("noResults")
      }
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          slotProps={{
            ...params.slotProps,
            input: {
              ...params.slotProps?.input,
              endAdornment: (
                <>
                  {loading ? <CircularProgress size={18} /> : null}
                  {inputValue !== "" && selected.length === 0 ? (
                    <Tooltip title={t("clearSearch")}>
                      <IconButton
                        size="small"
                        aria-label={t("clearSearch")}
                        onClick={clearInput}
                      >
                        <CloseIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  ) : null}
                  {params.slotProps?.input?.endAdornment}
                </>
              ),
            },
          }}
        />
      )}
    />
  );
}
