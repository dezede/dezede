import AppBar from "@mui/material/AppBar";
import Container from "@mui/material/Container";
import Link from "next/link";
import Button, { ButtonProps } from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import LaunchIcon from "@mui/icons-material/Launch";
import { ROOT_SLUG } from "@/app/constants";
import Grid from "@mui/material/Grid";
import PageHeader from "@/components/PageHeader";
import { Suspense } from "react";
import Skeleton from "@mui/material/Skeleton";
import { findPage } from "@/app/utils";
import Paper from "@mui/material/Paper";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { TSibling } from "../types";
import IconButton from "@mui/material/IconButton";

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

function SiblingButton({
  sibling,
  icon,
  right = false,
}: {
  sibling: TSibling;
  icon: React.ReactNode;
  right?: boolean;
}) {
  if (sibling === null) {
    // We keep an empty DOM object to preserve the alignment of the other sibling button.
    return <span />;
  }
  return (
    <>
      <IconButton
        component={Link}
        href={sibling.url}
        size="large"
        sx={{ display: { md: "none" } }}
      >
        {icon}
      </IconButton>
      <Button
        component={Link}
        href={sibling.url}
        startIcon={right ? undefined : icon}
        endIcon={right ? icon : undefined}
        sx={{ maxWidth: "50%", display: { xs: "none", md: "flex" } }}
      >
        {sibling.title}
      </Button>
    </>
  );
}

export default async function Layout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ slug: string[] }>;
}>) {
  const { previous, next } = await findPage({ params });
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
      {previous !== null || next !== null ? (
        <Grid>
          <Container>
            <Paper sx={{ padding: { xs: 1, md: 0 } }}>
              <Stack direction="row" justifyContent="space-between" spacing={2}>
                <SiblingButton sibling={previous} icon={<ChevronLeftIcon />} />
                <SiblingButton
                  sibling={next}
                  icon={<ChevronRightIcon />}
                  right
                />
              </Stack>
            </Paper>
          </Container>
        </Grid>
      ) : null}
    </Grid>
  );
}
