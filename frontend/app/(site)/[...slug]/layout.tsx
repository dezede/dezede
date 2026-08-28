import Container from "@mui/material/Container";
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
import SiblingButton from "@/components/SiblingButton";

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
