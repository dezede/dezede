import Box from "@mui/material/Box";
import InputAdornment from "@mui/material/InputAdornment";
import Paper from "@mui/material/Paper";
import TextField from "@mui/material/TextField";
import SearchIcon from "@mui/icons-material/Search";
import Form from "next/form";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Link from "next/link";
import Stack from "@mui/material/Stack";
import Chip from "@mui/material/Chip";
import PersonLabel from "./PersonLabel";
import {
  ELetterTab,
  TFindPageData,
  TPage,
  TRelatedPerson,
  TSearchParams,
} from "../types";
import { djangoFetchData } from "../utils";
import { INDIVIDU_FIELDS } from "../constants";

function LetterTab({
  value,
  label,
  count,
}: {
  value: ELetterTab;
  label: React.ReactNode;
  count: number;
}) {
  return (
    <Tab
      component={Link}
      href={`?tab=${value}`}
      label={
        <Stack direction="row" spacing={0.5} alignItems="center">
          <span>{label}</span>
          <Chip label={count} size="small" />
        </Stack>
      }
      value={value}
    />
  );
}

export default async function LetterCorpusForm({
  findPageData,
  searchParams,
}: {
  findPageData: TFindPageData;
  searchParams: TSearchParams;
}) {
  const { search, tab = ELetterTab.ALL } = await searchParams;

  const { person, description, total_count, from_count, to_count } =
    await djangoFetchData<
      TPage & {
        person: TRelatedPerson;
        description: string;
        total_count: number;
        from_count: number;
        to_count: number;
      }
    >(findPageData.apiUrl, {
      fields: `person(${INDIVIDU_FIELDS})`,
    });
  return (
    <Paper>
      <Box p={2}>
        <Form action="." replace scroll={false}>
          <TextField
            name="search"
            placeholder="Rechercher…"
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
        </Form>
      </Box>
      <Tabs value={tab} variant="fullWidth">
        <LetterTab value={ELetterTab.ALL} label="Tout" count={total_count} />
        <LetterTab
          value={ELetterTab.FROM}
          label={
            <span>
              <small>De</small> <PersonLabel {...person} />
            </span>
          }
          count={from_count}
        />
        <LetterTab
          value={ELetterTab.TO}
          label={
            <span>
              <small>À</small> <PersonLabel {...person} />
            </span>
          }
          count={to_count}
        />
        <LetterTab
          value={ELetterTab.OTHER}
          label="Autres"
          count={total_count - from_count - to_count}
        />
      </Tabs>
    </Paper>
  );
}
