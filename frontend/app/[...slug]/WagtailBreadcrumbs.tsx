import Breadcrumbs from "@mui/material/Breadcrumbs";
import MuiLink from "@mui/material/Link";
import { TPageDetailed } from "../types";
import Link from "next/link";
import { ROOT_SLUG } from "../constants";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import HomeIcon from "@mui/icons-material/Home";
import { getRelativeUrl } from "../utils";

export default function WagtailBreadcrumbs({
  pageData,
}: {
  pageData: TPageDetailed;
}) {
  if (pageData.ancestors.length === 0) {
    return null;
  }
  const pathname = getRelativeUrl(pageData.meta.html_url);
  return (
    <Breadcrumbs>
      {pageData.ancestors.map(({ id, title }, index) => (
        <MuiLink
          key={id}
          component={Link}
          href={`/${ROOT_SLUG}/${pathname
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
      <Typography>{pageData.title}</Typography>
    </Breadcrumbs>
  );
}
