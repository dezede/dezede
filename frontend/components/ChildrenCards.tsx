import { TPageCard } from "@/app/types";
import { fetchPages } from "@/app/utils";
import PageCard from "@/components/PageCard";
import Stack from "@mui/material/Stack";

export default async function ChildrenCards({ pageId }: { pageId: number }) {
  const childrenData = await fetchPages<TPageCard>(
    "/api/pages/",
    { child_of: pageId },
    ["search_description", "teaser_thumbnail"],
  );
  return (
    <Stack flexWrap="nowrap" spacing={4}>
      {childrenData.items.map((page) => (
        <PageCard key={page.id} page={page} />
      ))}
    </Stack>
  );
}
