import AppBar from "@mui/material/AppBar";
import Container from "@mui/material/Container";
import Link from "next/link";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import LaunchIcon from "@mui/icons-material/Launch";
import { ROOT_SLUG } from "../constants";
import Typography from "@mui/material/Typography";
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
  return { title: `${seoTitle || title} · OpenLetter × Dezède`, description };
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
              <Stack direction="row" spacing={1} alignItems="center">
                <Typography>Financement :</Typography>
                <Button
                  component="a"
                  href="https://nbe.org.uk/wp/"
                  target="_blank"
                  variant="outlined"
                  color="inherit"
                  size="small"
                >
                  New Berlioz Edition Trust
                </Button>
                <Button
                  component="a"
                  href="https://musica.hypotheses.org/"
                  target="_blank"
                  variant="outlined"
                  color="inherit"
                  size="small"
                >
                  Consortium Musica2
                </Button>
              </Stack>
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
