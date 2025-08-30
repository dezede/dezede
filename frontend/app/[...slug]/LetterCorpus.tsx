import {
  TFindPageData,
  TPage,
  TRelatedPerson,
  TAsyncSearchParams,
  ELetterTab,
  TYearChoice,
} from "../types";
import Stack from "@mui/material/Stack";
import Container from "@mui/material/Container";
import React, { Suspense } from "react";
import LetterList from "./LetterList";
import Skeleton from "@mui/material/Skeleton";
import LetterCorpusForm from "./LetterCorpusForm";
import { djangoFetchData } from "../utils";
import { INDIVIDU_FIELDS } from "../constants";
import ClientPagination from "./ClientPagination";

export default async function LetterCorpus({
  findPageData,
  searchParams,
}: {
  findPageData: TFindPageData;
  searchParams: TAsyncSearchParams;
}) {
  const {
    search,
    year,
    person: selectedPerson,
    tab,
    page,
  } = await searchParams;
  const {
    person,
    year_choices,
    person_choices,
    total_count,
    from_count,
    to_count,
  } = await djangoFetchData<
    TPage & {
      person: TRelatedPerson;
      year_choices: TYearChoice[];
      person_choices: TRelatedPerson[];
      total_count: number;
      from_count: number;
      to_count: number;
    }
  >(`/api/correspondance/${findPageData.id}/`, {
    search,
    year,
    person: selectedPerson,
    fields: `person(${INDIVIDU_FIELDS}),person_choices(${INDIVIDU_FIELDS})`,
  });
  const count =
    {
      [ELetterTab.ALL]: total_count,
      [ELetterTab.FROM]: from_count,
      [ELetterTab.TO]: to_count,
      [ELetterTab.OTHER]: total_count - from_count - to_count,
    }[typeof tab === "string" ? tab : ELetterTab.ALL] ?? total_count;
  const perPage = 2;
  const pagination = (
    <ClientPagination
      totalCount={count}
      perPage={perPage}
      sx={{ alignSelf: "center" }}
    />
  );
  return (
    <Container>
      <Stack spacing={2}>
        <LetterCorpusForm
          person={person}
          yearChoices={year_choices}
          personChoices={person_choices}
          totalCount={total_count}
          fromCount={from_count}
          toCount={to_count}
        />
        {pagination}
        <Suspense
          key={`${search} ${year} ${selectedPerson} ${tab} ${page}`}
          fallback={
            <Stack spacing={2}>
              {[...Array(perPage).keys()].map((value) => (
                <Skeleton key={value} variant="rectangular" height={200} />
              ))}
            </Stack>
          }
        >
          <LetterList
            parentPageId={findPageData.id}
            searchParams={searchParams}
            perPage={perPage}
          />
        </Suspense>
        {pagination}
      </Stack>
    </Container>
  );
}
