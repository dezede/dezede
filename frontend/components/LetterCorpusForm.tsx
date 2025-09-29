"use client";

import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import { getPersonLabel, PersonLabel } from "@/format/PersonChip";
import {
  ELetterTab,
  TRelatedPerson,
  TRelatedPlace,
  TYearChoice,
} from "@/app/types";
import React, { SyntheticEvent, useCallback, useState } from "react";
import { useUpdateSearchParams } from "@/app/hooks";
import { getPlaceLabel } from "@/format/PlaceChip";
import Autocomplete, {
  AutocompleteProps,
  createFilterOptions,
} from "@mui/material/Autocomplete";
import Box from "@mui/material/Box";
import SearchTextField from "./SearchTextField";

function AutocompleteFilter<T>({
  param,
  label,
  options,
  getOptionKey: getParamValue,
  renderOption,
  ...props
}: Omit<
  AutocompleteProps<T, undefined, undefined, undefined>,
  "renderInput" | "renderOption"
> & {
  param: string;
  label: React.ReactNode;
  options: T[];
  getOptionKey: (option: T | null) => string;
  renderOption?: (option: T) => React.ReactNode;
}) {
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const [selected, setSelected] = useState<string>(
    searchParams.get(param) ?? "",
  );
  const onChange = useCallback(
    (event: SyntheticEvent, value: T | null) => {
      setSelected(getParamValue(value));
      updateSearchParams({ [param]: getParamValue(value), page: null });
    },
    [getParamValue, param, updateSearchParams],
  );
  return (
    <Autocomplete
      value={
        options.find((option) => getParamValue(option) === selected) ?? null
      }
      onChange={onChange}
      options={options}
      getOptionKey={getParamValue}
      renderOption={
        renderOption === undefined
          ? undefined
          : ({ key, ...props }, option) => (
              <Box key={key} component="li" {...props}>
                {renderOption(option)}
              </Box>
            )
      }
      renderInput={(params) => <TextField {...params} label={label} />}
      fullWidth
      noOptionsText="Aucun choix disponible"
      {...props}
    />
  );
}

function LetterTabLabel({
  children,
  count,
}: {
  children: React.ReactNode;
  count: number;
}) {
  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <span>{children}</span>
      <Chip label={count} size="small" />
    </Stack>
  );
}

export default function LetterCorpusForm({
  person,
  yearChoices,
  personChoices,
  writingPlaceChoices,
  totalCount,
  fromCount,
  toCount,
}: {
  person: TRelatedPerson;
  yearChoices: TYearChoice[];
  personChoices: TRelatedPerson[];
  writingPlaceChoices: TRelatedPlace[];
  totalCount: number;
  fromCount: number;
  toCount: number;
}) {
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const [tab, setTab] = useState(searchParams.get("tab") ?? ELetterTab.ALL);
  const placeFilterOptions = createFilterOptions<TRelatedPlace>({
    matchFrom: "any",
    stringify: getPlaceLabel,
  });
  const tabSx = { flexGrow: 1, maxWidth: "100%" };
  return (
    <Paper>
      <Stack
        direction={{ xs: "column", md: "row" }}
        flexWrap="nowrap"
        p={2}
        spacing={2}
      >
        <SearchTextField />
        <AutocompleteFilter
          param="year"
          label="Année"
          options={yearChoices}
          getOptionKey={(option) =>
            (option?.year === null ? "null" : (option?.year ?? "")).toString()
          }
          getOptionLabel={(option) => (option.year ?? "Inconnue").toString()}
          renderOption={(option) => (
            <Stack
              direction="row"
              spacing={1}
              justifyContent="space-between"
              width="100%"
            >
              <span>{option.year ?? "Inconnue"}</span>
              <span>{option.count} lettres</span>
            </Stack>
          )}
        />
        <AutocompleteFilter
          param="person"
          label="Correspondant"
          options={personChoices}
          getOptionKey={(option) => (option?.id ?? "").toString()}
          getOptionLabel={getPersonLabel}
        />
        <AutocompleteFilter
          param="writing_place"
          label="Lieu de rédaction"
          options={writingPlaceChoices}
          groupBy={(option) => option.nature.nom}
          getOptionKey={(option) => (option?.id ?? "").toString()}
          getOptionLabel={getPlaceLabel}
          filterOptions={placeFilterOptions}
        />
      </Stack>
      <Tabs
        value={tab}
        onChange={(event, value) => {
          setTab(value);
          updateSearchParams({ tab: value, page: null });
        }}
        variant="scrollable"
        scrollButtons="auto"
      >
        <Tab
          value={ELetterTab.ALL}
          label={<LetterTabLabel count={totalCount}>Tout</LetterTabLabel>}
          sx={tabSx}
        />
        <Tab
          value={ELetterTab.FROM}
          label={
            <LetterTabLabel count={fromCount}>
              <small>De</small> <PersonLabel {...person} />
            </LetterTabLabel>
          }
          sx={tabSx}
        />
        <Tab
          value={ELetterTab.TO}
          label={
            <LetterTabLabel count={toCount}>
              <small>À</small> <PersonLabel {...person} />
            </LetterTabLabel>
          }
          sx={tabSx}
        />
        <Tab
          value={ELetterTab.OTHER}
          label={
            <LetterTabLabel count={totalCount - fromCount - toCount}>
              Autres
            </LetterTabLabel>
          }
          sx={tabSx}
        />
      </Tabs>
    </Paper>
  );
}
