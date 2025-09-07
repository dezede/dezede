import Grid from "@mui/material/Grid";
import PageCard from "@/components/PageCard";
import { TPagesRowBlock } from "@/app/types";

export default function PagesRowBlock({
  block: { id, value },
}: {
  block: TPagesRowBlock;
}) {
  return (
    <Grid key={id} container alignItems="center" spacing={4}>
      {value.map((page, index) => (
        // We also include the index in the key, in case the same page was selected multiple times.
        <Grid key={`${page.id}:${index}`} size={{ xs: 12, md: 6, xl: 4 }}>
          <PageCard page={page} />
        </Grid>
      ))}
    </Grid>
  );
}
