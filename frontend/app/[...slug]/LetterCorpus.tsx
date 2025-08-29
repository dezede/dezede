import { TFindPageData, TSearchParams } from "../types";
import Stack from "@mui/material/Stack";
import Container from "@mui/material/Container";
import React, { Suspense } from "react";
import LetterList from "./LetterList";
import Skeleton from "@mui/material/Skeleton";
import LetterCorpusForm from "./LetterCorpusForm";

export default async function LetterCorpus({
  findPageData,
  searchParams,
}: {
  findPageData: TFindPageData;
  searchParams: TSearchParams;
}) {
  return (
    <Container>
      <Stack spacing={4}>
        <Suspense fallback={<Skeleton variant="rectangular" height={136} />}>
          <LetterCorpusForm
            findPageData={findPageData}
            searchParams={searchParams}
          />
        </Suspense>
        <Suspense fallback={<Skeleton variant="rectangular" height={200} />}>
          <LetterList
            parentPageId={findPageData.id}
            searchParams={searchParams}
          />
        </Suspense>
      </Stack>
    </Container>
  );
}
