"use client";

import Box from "@mui/material/Box";
import InputAdornment from "@mui/material/InputAdornment";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import SearchIcon from "@mui/icons-material/Search";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import PersonLabel from "./PersonLabel";
import { ELetterTab, TRelatedPerson } from "../types";
import { ChangeEvent, useMemo, useState } from "react";
import { useDebounceCallback, useUpdateSearchParams } from "../hooks";

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
  totalCount,
  fromCount,
  toCount,
}: {
  person: TRelatedPerson;
  totalCount: number;
  fromCount: number;
  toCount: number;
}) {
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const [tab, setTab] = useState(searchParams.get("tab") ?? ELetterTab.ALL);
  const search = useMemo(
    () => searchParams.get("search") ?? "",
    [searchParams],
  );
  const handleSearch = useDebounceCallback(
    (event: ChangeEvent<HTMLInputElement>) =>
      updateSearchParams({ search: event.target.value }),
    300,
  );
  return (
    <Paper>
      <Box p={2}>
        <TextField
          name="search"
          placeholder="Rechercher…"
          onChange={handleSearch}
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
      </Box>
      <Tabs
        value={tab}
        onChange={(event, value) => {
          setTab(value);
          updateSearchParams({ tab: value });
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
