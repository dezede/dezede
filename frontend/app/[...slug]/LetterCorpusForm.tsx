"use client";

import InputAdornment from "@mui/material/InputAdornment";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import SearchIcon from "@mui/icons-material/Search";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import PersonLabel, { getPersonLabelString } from "./PersonLabel";
import {
  ELetterTab,
  TRelatedPerson,
  TRelatedPlace,
  TYearChoice,
} from "../types";
import {
  ChangeEvent,
  SyntheticEvent,
  useCallback,
  useMemo,
  useState,
} from "react";
import { useDebounceCallback, useUpdateSearchParams } from "../hooks";
import MenuItem from "@mui/material/MenuItem";
import PlaceLabel from "./PlaceLabel";
import Autocomplete from "@mui/material/Autocomplete";
import Box from "@mui/material/Box";
import { safeParseInt } from "../utils";

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
  const [year, setYear] = useState(searchParams.get("year") ?? "");
  const [selectedPerson, setSelectedPerson] = useState(
    safeParseInt(searchParams.get("person"), null),
  );
  const [writingPlace, setWritingPlace] = useState(
    searchParams.get("writing_place") ?? "",
  );
  const search = useMemo(
    () => searchParams.get("search") ?? "",
    [searchParams],
  );
  const onSearchChange = useDebounceCallback(
    (event: ChangeEvent<HTMLInputElement>) =>
      updateSearchParams({ search: event.target.value, page: 1 }),
    300,
  );
  const onYearChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      setYear(event.target.value);
      updateSearchParams({ year: event.target.value, page: 1 });
    },
    [updateSearchParams],
  );
  const onPersonChange = useCallback(
    (event: SyntheticEvent, value: TRelatedPerson | null) => {
      setSelectedPerson(value?.id ?? null);
      updateSearchParams({ person: value?.id, page: 1 });
    },
    [updateSearchParams],
  );
  const onWritingPlaceChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      setWritingPlace(event?.target.value);
      updateSearchParams({ writing_place: event.target.value, page: 1 });
    },
    [updateSearchParams],
  );
  return (
    <Paper>
      <Stack direction="row" p={2} spacing={2}>
        <TextField
          placeholder="Rechercher…"
          onChange={onSearchChange}
          slotProps={{
            input: {
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            },
          }}
          defaultValue={search}
          fullWidth
        />
        <TextField
          label="Année"
          value={year}
          onChange={onYearChange}
          select
          fullWidth
          sx={{ maxWidth: 175 }}
        >
          {yearChoices.map(({ year, count }) => (
            <MenuItem key={year} value={year ?? "null"}>
              <Stack
                direction="row"
                spacing={1}
                justifyContent="space-between"
                width="100%"
              >
                <span>{year ?? "Inconnue"}</span> <span>{count} lettres</span>
              </Stack>
            </MenuItem>
          ))}
        </TextField>
        <Autocomplete
          value={personChoices.find((person) => person.id === selectedPerson) ?? null}
          onChange={onPersonChange}
          options={personChoices}
          getOptionKey={(option) => option.id}
          getOptionLabel={(option) => getPersonLabelString(option)}
          renderOption={(props, option) => {
            const { key, ...optionsProps } = props;
            return (
              <Box key={key} component="li" {...optionsProps}>
                <Stack
                  direction="row"
                  spacing={1}
                  justifyContent="space-between"
                  width="100%"
                >
                  {getPersonLabelString(option)}
                </Stack>
              </Box>
            );
          }}
          renderInput={(params) => (
            <TextField {...params} label="Correspondant" />
          )}
          fullWidth
        />
        <TextField
          label="Lieu de rédaction"
          value={writingPlace}
          onChange={onWritingPlaceChange}
          select
          fullWidth
        >
          {writingPlaceChoices.map((place) => (
            <MenuItem key={place.id} value={place.id}>
              <PlaceLabel {...place} />
            </MenuItem>
          ))}
        </TextField>
      </Stack>
      <Tabs
        value={tab}
        onChange={(event, value) => {
          setTab(value);
          updateSearchParams({ tab: value, page: null });
        }}
        variant="fullWidth"
      >
        <Tab
          value={ELetterTab.ALL}
          label={<LetterTabLabel count={totalCount}>Tout</LetterTabLabel>}
        />
        <Tab
          value={ELetterTab.FROM}
          label={
            <LetterTabLabel count={fromCount}>
              <small>De</small> <PersonLabel {...person} />
            </LetterTabLabel>
          }
        />
        <Tab
          value={ELetterTab.TO}
          label={
            <LetterTabLabel count={toCount}>
              <small>À</small> <PersonLabel {...person} />
            </LetterTabLabel>
          }
        />
        <Tab
          value={ELetterTab.OTHER}
          label={
            <LetterTabLabel count={totalCount - fromCount - toCount}>
              Autres
            </LetterTabLabel>
          }
        />
      </Tabs>
    </Paper>
  );
}
