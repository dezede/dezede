import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "next/link";
import { TPageCard } from "@/app/types";
import OverflowContainer from "./OverflowContainer";
import Divider from "@mui/material/Divider";

export default function PageCard({
  page: {
    title,
    meta: { html_url, search_description },
  },
}: {
  page: TPageCard;
}) {
  return (
    <Card>
      <CardActionArea component={Link} href={html_url} prefetch={false}>
        <OverflowContainer maxHeight={200}>
          <CardContent>
            <Stack spacing={2} divider={<Divider />}>
              <Typography variant="h3">{title}</Typography>
              {search_description ? (
                <Typography variant="body2">{search_description}</Typography>
              ) : null}
            </Stack>
          </CardContent>
        </OverflowContainer>
      </CardActionArea>
    </Card>
  );
}
