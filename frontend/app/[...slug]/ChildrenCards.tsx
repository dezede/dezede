"use client";

import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Grid";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";
import { TPage } from "../types";

export default function ChildrenCards({
  childrenData,
}: {
  childrenData: (TPage & { meta: { search_description: string } })[];
}) {
  return (
    <Grid container>
      {childrenData.map(({ id, title, meta: { slug, search_description } }) => (
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
      ))}
    </Grid>
  );
}
