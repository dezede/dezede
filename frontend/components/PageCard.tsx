import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { TPageCard } from "@/app/types";
import Divider from "@mui/material/Divider";
import ImageRendition from "./ImageRendition";
import Box from "@mui/material/Box";
import OurLink from "./OurLink";

export default function PageCard({
  page: {
    title,
    meta: { html_url, search_description, teaser_thumbnail },
  },
}: {
  page: TPageCard;
}) {
  return (
    <Card>
      <CardActionArea component={OurLink} href={html_url}>
        <Stack direction="row">
          {teaser_thumbnail === null ? null : (
            <Box display={{ xs: "none", sm: "block" }}>
              <ImageRendition
                rendition={teaser_thumbnail}
                style={{ display: "block" }}
              />
            </Box>
          )}
          <CardContent sx={{ maxHeight: 200, overflowY: "auto" }}>
            <Stack spacing={2} divider={<Divider />}>
              <Stack
                direction="column"
                flexWrap="nowrap"
                spacing={1}
                justifyContent="space-between"
                alignItems="baseline"
              >
                <Typography variant="h3">{title}</Typography>
              </Stack>
              {search_description ? (
                <Typography variant="body2">{search_description}</Typography>
              ) : null}
            </Stack>
          </CardContent>
        </Stack>
      </CardActionArea>
    </Card>
  );
}
