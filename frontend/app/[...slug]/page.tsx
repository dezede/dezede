import { Suspense } from "react";
import { EPageType, TAsyncSearchParams } from "../types";
import { findPage } from "../utils";
import ChildrenCards from "./ChildrenCards";
import dynamic from "next/dynamic";
import Container from "@mui/material/Container";
import Skeleton from "@mui/material/Skeleton";
import LetterCorpus from "./LetterCorpus";

const Letter = dynamic(() => import("./Letter"));

type TProps = {
  params: Promise<{ slug: string[] }>;
  searchParams: TAsyncSearchParams;
};

export default async function WagtailPage({ params, searchParams }: TProps) {
  const findPageData = await findPage({ params });
  switch (findPageData.type) {
    case EPageType.LETTER:
      return <Letter findPageData={findPageData} />;
    case EPageType.LETTER_CORPUS:
      return (
        <LetterCorpus findPageData={findPageData} searchParams={searchParams} />
      );
  }

  return (
    <Container>
      <Suspense fallback={<Skeleton variant="rectangular" height={200} />}>
        <ChildrenCards pageId={findPageData.id} />
      </Suspense>
    </Container>
  );
}
