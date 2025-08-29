import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import { findPage } from "../utils";
import Breadcrumbs from "@mui/material/Breadcrumbs";
import MuiLink from "@mui/material/Link";
import HomeIcon from "@mui/icons-material/Home";
import Link from "next/link";
import { ROOT_SLUG } from "../constants";

export default async function PageHeader({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}) {
  const { title, ancestors, url } = await findPage({ params });
  return (
    <Stack direction="column" flexWrap="nowrap" spacing={4}>
      {ancestors.length === 0 ? null : (
        <Breadcrumbs>
          {ancestors.map(({ id, title }, index) => (
            <MuiLink
              key={id}
              component={Link}
              href={`/${ROOT_SLUG}/${url
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
          <Typography>{title}</Typography>
        </Breadcrumbs>
      )}
      <Typography variant="h1">{title}</Typography>
    </Stack>
  );
}
