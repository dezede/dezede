import Grid from "@mui/material/Grid";
import PageCard from "@/components/PageCard";
import { TPagesRowBlock } from "@/app/types";

export default function PagesRowBlock({
  block: { value },
}: {
  block: TPagesRowBlock;
}) {
  return (
    <Grid container spacing={4}>
      {value.map((page, index) => (
        // We also include the index in the key, in case the same page was selected multiple times.
        <Grid key={`${page.id}:${index}`} size={{ xs: 12, lg: 6 }}>
          <PageCard page={page} />
        </Grid>
      ))}
    </Grid>
  );
}
