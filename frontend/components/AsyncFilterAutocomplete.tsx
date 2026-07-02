"use client";

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import CircularProgress from "@mui/material/CircularProgress";
import { useTranslations } from "next-intl";
import { useAsyncSearch, useUpdateSearchParams } from "@/app/hooks";
import { apiGet } from "@/app/api";
import { FilterOption } from "@/app/authorityColumns";

/**
 * A URL-backed single-value autocomplete over a `{value, label}` type-ahead
 * endpoint (e.g. `/api/public/dossiers/<id>/genres/`,
 * `/api/public/sources/source_types/`). Stores the chosen pk in `?<param>=`,
 * restores its label from that pk on mount, and debounces the type-ahead. Used
 * wherever a filter's value list is too long for a plain `<select>` — genre
 * d'œuvre, type de source. The single-value sibling of
 * {@link AsyncMultiAutocomplete}; MUI's built-in clear indicator (forced visible
 * in `theme.ts`) gives it the same × clear button.
 */
export default function AsyncFilterAutocomplete({
  param,
  endpoint,
  label,
  shallow = false,
}: {
  param: string;
  endpoint: string;
  label: string;
  // Use the History API (no Next.js navigation) — matches the authority grids,
  // which never re-render server-side on a filter change.
  shallow?: boolean;
}) {
  const t = useTranslations("events");
  const tCommon = useTranslations("common");
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const urlValue = searchParams.get(param);
  const [selected, setSelected] = useState<FilterOption | null>(null);
  // Start in the loading state when the URL already carries a pk, so the field
  // shows the spinner on first paint instead of flashing empty until the restore
  // fetch resolves. Tracks only the URL-restore fetch; the type-ahead's own
  // loading comes from useAsyncSearch.
  const [restoreLoading, setRestoreLoading] = useState(
    () => urlValue != null && urlValue !== "",
  );
  // The text typed into the box, only used to pick the "type to search" vs
  // "no results" empty message (the input itself is uncontrolled so the selected
  // option's label shows).
  const [searchText, setSearchText] = useState("");

  // Type-ahead options: the endpoint returns a bare array of `{value, label}`.
  const {
    results: options,
    loading: searchLoading,
    search: runSearch,
    reset: resetSearch,
  } = useAsyncSearch<FilterOption>(
    (query, signal) =>
      apiGet<FilterOption[]>(endpoint, { params: { q: query }, signal }),
    { debounceMs: 300 },
  );
  const loading = restoreLoading || searchLoading;

  // Restore the label for the pk in the URL. `syncedRef` tracks the value we
  // last reconciled, so our own changes (onChange) don't refetch.
  const syncedRef = useRef<string | null>(null);
  useEffect(() => {
    const normalized = urlValue ?? null;
    if (syncedRef.current === normalized) {
      return;
    }
    syncedRef.current = normalized;
    let cancelled = false;
    const restore = async () => {
      if (!normalized) {
        if (!cancelled) {
          setSelected(null);
          setRestoreLoading(false);
        }
        return;
      }
      if (!cancelled) {
        setRestoreLoading(true);
      }
      try {
        const data = await apiGet<FilterOption[]>(endpoint, {
          params: { ids: normalized },
        });
        if (!cancelled) {
          setSelected(data[0] ?? null);
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
    (event: React.SyntheticEvent, value: FilterOption | null) => {
      setSelected(value);
      const encoded = value ? String(value.value) : null;
      syncedRef.current = encoded;
      updateSearchParams({ [param]: encoded, page: null }, { shallow });
    },
    [param, updateSearchParams, shallow],
  );

  // Keep the selected option in the list so it renders even when it isn't in the
  // latest search results.
  const mergedOptions = useMemo(() => {
    if (!selected) {
      return options;
    }
    return [
      selected,
      ...options.filter(
        (option) => String(option.value) !== String(selected.value),
      ),
    ];
  }, [selected, options]);

  return (
    <Autocomplete<FilterOption, false, false, false>
      fullWidth
      size="small"
      value={selected}
      onChange={onChange}
      options={mergedOptions}
      filterOptions={(items) => items}
      onInputChange={(event, value, reason) => {
        setSearchText(value);
        if (reason === "input") {
          runSearch(value);
        } else {
          resetSearch();
        }
      }}
      getOptionLabel={(option) => option.label}
      getOptionKey={(option) => option.value}
      isOptionEqualToValue={(option, value) =>
        String(option.value) === String(value.value)
      }
      loading={loading}
      loadingText={tCommon("loading")}
      noOptionsText={
        searchText.trim() === "" ? t("typeToSearch") : tCommon("noResults")
      }
      renderInput={(params) => (
        <TextField
          {...params}
          label={label}
          slotProps={{
            input: {
              ...params.InputProps,
              endAdornment: (
                <>
                  {loading ? <CircularProgress size={18} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            },
          }}
        />
      )}
    />
  );
}
