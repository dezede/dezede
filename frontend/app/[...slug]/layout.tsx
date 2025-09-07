import AppBar from "@mui/material/AppBar";
import Container from "@mui/material/Container";
import Link from "next/link";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import LaunchIcon from "@mui/icons-material/Launch";
import { ROOT_SLUG } from "../constants";
import Grid from "@mui/material/Grid";
import PageHeader from "@/components/PageHeader";
import { Suspense } from "react";
import Skeleton from "@mui/material/Skeleton";
import { findPage } from "../utils";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}) {
  const { title, seoTitle, description } = await findPage({ params });
  // TODO: Add teaser_thumbnail as an open graph image.
  return {
    title: seoTitle || `${title} · OpenLetter × Dezède`,
    description,
    openGraph: {
      siteName: "Dezède",
    },
    formatDetection: {
      email: false,
      address: false,
      telephone: false,
    },
  };
}

export default async function Layout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ slug: string[] }>;
}>) {
  return (
    <Grid
      container
      direction="column"
      wrap="nowrap"
      spacing={4}
      paddingBottom={4}
    >
      <Grid>
        <AppBar position="static">
          <Container>
            <Stack
              direction="row"
              justifyContent="space-between"
              sx={{ py: 1 }}
            >
              <Button
                component={Link}
                href={`/${ROOT_SLUG}`}
                prefetch={false}
                color="inherit"
              >
                OpenLetter
              </Button>
              <Button
                component="a"
                href="/"
                color="inherit"
                variant="outlined"
                startIcon={<LaunchIcon />}
              >
                Dezède
              </Button>
            </Stack>
          </Container>
        </AppBar>
      </Grid>
      <Grid>
        <Container>
          <Suspense
            fallback={
              <Stack spacing={4}>
                <Skeleton variant="rectangular" height={24} />
                <Skeleton variant="rectangular" height={56} />
              </Stack>
            }
          >
            <PageHeader params={params} />
          </Suspense>
        </Container>
      </Grid>
      <Grid>{children}</Grid>
    </Grid>
  );
}
