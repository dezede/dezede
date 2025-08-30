"use client";

import InputAdornment from "@mui/material/InputAdornment";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import SearchIcon from "@mui/icons-material/Search";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import PersonLabel from "./PersonLabel";
import { ELetterTab, TRelatedPerson, TYearChoice } from "../types";
import { ChangeEvent, useCallback, useMemo, useState } from "react";
import { useDebounceCallback, useUpdateSearchParams } from "../hooks";
import MenuItem from "@mui/material/MenuItem";

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
  totalCount,
  fromCount,
  toCount,
}: {
  person: TRelatedPerson;
  yearChoices: TYearChoice[];
  personChoices: TRelatedPerson[];
  totalCount: number;
  fromCount: number;
  toCount: number;
}) {
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const [tab, setTab] = useState(searchParams.get("tab") ?? ELetterTab.ALL);
  const [year, setYear] = useState(searchParams.get("year") ?? "");
  const [selectedPerson, setSelectedPerson] = useState(
    searchParams.get("person") ?? "",
  );
  const search = useMemo(
    () => searchParams.get("search") ?? "",
    [searchParams],
  );
  const onSearchChange = useDebounceCallback(
    (event: ChangeEvent<HTMLInputElement>) =>
      updateSearchParams({ search: event.target.value }),
    300,
  );
  const onYearChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      setYear(event.target.value);
      updateSearchParams({ year: event.target.value });
    },
    [updateSearchParams],
  );
  const onPersonChange = useCallback(
    (event: ChangeEvent<HTMLInputElement>) => {
      setSelectedPerson(event.target.value);
      updateSearchParams({ person: event.target.value });
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
        />
        <TextField
          label="Année"
          value={year}
          onChange={onYearChange}
          select
          sx={{ width: 200 }}
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
        <TextField
          label="Correspondant"
          value={selectedPerson}
          onChange={onPersonChange}
          select
          sx={{ width: 200 }}
        >
          {personChoices.map((person) => (
            <MenuItem key={person.id} value={person.id}>
              <Stack
                direction="row"
                spacing={1}
                justifyContent="space-between"
                width="100%"
              >
                <PersonLabel {...person} />
              </Stack>
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
