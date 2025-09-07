import Grid from "@mui/material/Grid";
import { TPage } from "@/app/types";
import { fetchPages } from "@/app/utils";
import PageCard from "@/components/PageCard";

export default async function ChildrenCards({ pageId }: { pageId: number }) {
  const childrenData = await fetchPages<
    TPage & { meta: { search_description: string } }
  >("/api/pages/", { child_of: pageId }, ["search_description"]);
  return (
    <Grid container spacing={4}>
      {childrenData.items.map((page) => (
        <Grid key={page.id} size={{ xs: 12, md: 6, xl: 4 }}>
          <PageCard page={page} />
        </Grid>
      ))}
    </Grid>
  );
}
