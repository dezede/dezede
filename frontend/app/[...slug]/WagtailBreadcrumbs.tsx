import Breadcrumbs from "@mui/material/Breadcrumbs";
import MuiLink from "@mui/material/Link";
import { TFindPageData } from "../types";
import Link from "next/link";
import { ROOT_SLUG } from "../constants";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import HomeIcon from "@mui/icons-material/Home";

export default async function WagtailBreadcrumbs({
  findPageData,
}: {
  findPageData: TFindPageData;
}) {
  if (findPageData.ancestors.length === 0) {
    return null;
  }
  return (
    <Breadcrumbs>
      {findPageData.ancestors.map(({ id, title }, index) => (
        <MuiLink
          key={id}
          component={Link}
          href={`/${ROOT_SLUG}/${findPageData.url
            .split("/")
            .slice(1, index + 1)
            .join("/")}`}
          prefetch={false}
          underline="hover"
        >
          <Stack direction="row" spacing={0.5}>
            {index === 0 ? <HomeIcon /> : null}
            <Typography>{title}</Typography>
          </Stack>
        </MuiLink>
      ))}
      <Typography>{findPageData.title}</Typography>
    </Breadcrumbs>
  );
}
