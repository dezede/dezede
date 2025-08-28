import Skeleton from "@mui/material/Skeleton";
import { Suspense } from "react";
import WagtailBreadcrumbs from "./WagtailBreadcrumbs";
import Typography from "@mui/material/Typography";
import { findPage } from "../utils";
import Stack from "@mui/material/Stack";

export default async function PageHeader({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}) {
  const findPageData = await findPage({ params });
  return (
    <Stack direction="column" flexWrap="nowrap" spacing={4}>
      <Suspense fallback={<Skeleton variant="rectangular" height={24} />}>
        <WagtailBreadcrumbs findPageData={findPageData} />
      </Suspense>
      <Typography variant="h1">{findPageData.title}</Typography>
    </Stack>
  );
}
