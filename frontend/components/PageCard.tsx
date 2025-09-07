import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";
import { TPageCard } from "@/app/types";
import OverflowContainer from "./OverflowContainer";
import Divider from "@mui/material/Divider";
import ImageRendition from "./ImageRendition";
import SpaceTime from "@/format/SpaceTime";
import Box from "@mui/material/Box";

export default function PageCard({
  page: {
    title,
    meta: {
      html_url,
      search_description,
      first_published_at,
      teaser_thumbnail,
    },
  },
}: {
  page: TPageCard;
}) {
  return (
    <Card>
      <CardActionArea component={Link} href={html_url} prefetch={false}>
        <Stack direction="row">
          {teaser_thumbnail === null ? null : (
            <Box display={{ xs: "none", sm: "block" }}>
              <ImageRendition
                rendition={teaser_thumbnail}
                style={{ display: "block" }}
              />
            </Box>
          )}
          <OverflowContainer maxHeight={200}>
            <CardContent>
              <Stack spacing={2} divider={<Divider />}>
                <Stack
                  direction="column"
                  flexWrap="nowrap"
                  spacing={1}
                  justifyContent="space-between"
                  alignItems="baseline"
                >
                  <Typography variant="h3">{title}</Typography>
                  <SpaceTime date={first_published_at} />
                </Stack>
                {search_description ? (
                  <Typography variant="body2">{search_description}</Typography>
                ) : null}
              </Stack>
            </CardContent>
          </OverflowContainer>
        </Stack>
      </CardActionArea>
    </Card>
  );
}
