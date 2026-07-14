import Container from "@mui/material/Container";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import Grid from "@mui/material/Grid";
import PageHeader from "@/components/PageHeader";
import { Suspense } from "react";
import Skeleton from "@mui/material/Skeleton";
import { findPage } from "@/app/utils";
import Paper from "@mui/material/Paper";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { TSibling } from "@/app/types";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import OurLink from "@/components/OurLink";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string[] }>;
}): Promise<Metadata> {
  const { title, seoTitle, description } = await findPage({ params });
  const t = await getTranslations();
  // TODO: Add teaser_thumbnail as an open graph image.
  return {
    title: seoTitle || t("pages.titleTemplate", { name: title }),
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
      <Tooltip title={sibling.title}>
        <IconButton
          component={OurLink}
          href={sibling.url}
          size="large"
          aria-label={sibling.title}
          sx={{ display: { md: "none" } }}
        >
          {icon}
        </IconButton>
      </Tooltip>
      <Button
        component={OurLink}
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
      wrap="nowrap"
      spacing={4}
      sx={{ flexDirection: "column" }}
    >
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
              <Stack
                direction="row"
                spacing={2}
                useFlexGap
                sx={{ justifyContent: "space-between" }}
              >
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
