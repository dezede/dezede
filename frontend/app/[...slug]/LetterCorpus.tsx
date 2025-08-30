import {
  TFindPageData,
  TPage,
  TRelatedPerson,
  TAsyncSearchParams,
  ELetterTab,
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
  const { search, tab, page } = await searchParams;
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
          totalCount={total_count}
          fromCount={from_count}
          toCount={to_count}
        />
        {pagination}
        <Suspense
          key={`${search} ${tab} ${page}`}
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
