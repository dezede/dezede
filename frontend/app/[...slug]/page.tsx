import { Suspense } from "react";
import { EPageType } from "../types";
import { findPage } from "../utils";
import ChildrenCards from "./ChildrenCards";
import dynamic from "next/dynamic";
import Container from "@mui/material/Container";
import Skeleton from "@mui/material/Skeleton";

const Letter = dynamic(() => import("./Letter"));

type TProps = { params: Promise<{ slug: string[] }> };

export default async function WagtailPage({ params }: TProps) {
  const findPageData = await findPage({ params });
  switch (findPageData.type) {
    case EPageType.LETTER:
      return <Letter findPageData={findPageData} />;
  }

  return (
    <Container>
      <Suspense fallback={<Skeleton variant="rectangular" height={200} />}>
        <ChildrenCards pageId={findPageData.id} />
      </Suspense>
    </Container>
  );
}
