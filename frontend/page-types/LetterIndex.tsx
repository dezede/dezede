import { TFindPageData, TPage, TBodyStreamBlock } from "@/app/types";
import Stack from "@mui/material/Stack";
import Container from "@mui/material/Container";
import React, { Suspense } from "react";
import Skeleton from "@mui/material/Skeleton";
import { djangoFetchData } from "@/app/utils";
import ReadMore from "@/components/ReadMore";
import BodyStream from "@/blocks/BodyStream";
import ChildrenCards from "@/components/ChildrenCards";
import { BODY_EXTRA_FIELDS } from "@/app/constants";

export default async function LetterIndex({
  findPageData,
}: {
  findPageData: TFindPageData;
}) {
  const { body } = await djangoFetchData<TPage & { body: TBodyStreamBlock }>(
    findPageData.apiUrl,
    {},
    ["body"],
    BODY_EXTRA_FIELDS,
  );
  return (
    <Container>
      <Stack spacing={4}>
        <ReadMore maxHeight={200}>
          <BodyStream value={body} />
        </ReadMore>
        <Suspense fallback={<Skeleton variant="rectangular" height={200} />}>
          <ChildrenCards pageId={findPageData.id} />
        </Suspense>
      </Stack>
    </Container>
  );
}
