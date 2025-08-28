import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";
import { TPage } from "../types";
import { fetchPages } from "../utils";

export default async function ChildrenCards({ pageId }: { pageId: number }) {
  const childrenData = await fetchPages<
    TPage & { meta: { search_description: string } }
  >(`/api/pages/?child_of=${pageId}&fields=search_description`);
  return (
    <Grid container spacing={4}>
      {childrenData.items.map(
        ({ id, title, meta: { slug, search_description } }) => (
          <Grid key={id} size={{ xs: 12, sm: 6, lg: 4 }}>
            <Card>
              <CardActionArea component={Link} href={slug} prefetch={false}>
                <CardContent>
                  <Stack spacing={2}>
                    <Typography variant="h3">{title}</Typography>
                    {search_description ? (
                      <Typography variant="body2">
                        {search_description}
                      </Typography>
                    ) : null}
                  </Stack>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ),
      )}
    </Grid>
  );
}
