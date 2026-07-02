import { getTranslations } from "next-intl/server";
import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import LaunchIcon from "@mui/icons-material/Launch";
import {
  DOSSIERS_BASE,
  EVENTS_BASE,
  ROOT_SLUG,
  SITE_NAME,
} from "@/app/constants";
import OurLink from "@/components/OurLink";
import MobileNavDrawer from "@/components/MobileNavDrawer";
import LanguageSwitcher from "@/components/LanguageSwitcher";
import { SourceModalProvider } from "@/components/SourceModal";
import { MainScrollArea } from "@/components/MainScroll";

/**
 * Shared chrome (top navigation bar) for every page served by the Next.js app:
 * the Wagtail pages (`[...slug]`) and the dedicated event views. Page-specific
 * headers live in the nested layouts/pages.
 *
 * The shell is a viewport-height flex column: a static navbar on top and a
 * single scrollable content region below it. This keeps the navbar fixed and
 * gives pages a height-bounded area to fill (the autorité tables fit the
 * viewport with a single inner scroll), while taller content pages scroll
 * inside the region instead of the body.
 */
export default async function SiteLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const t = await getTranslations("nav");
  const tBrowse = await getTranslations("browse");
  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100dvh" }}>
      <a href="#main-content" className="skip-to-content">
        {t("skipToContent")}
      </a>
      {/*
        `relative` (not `static`) so MUI's `z-index: appBar` takes effect:
        z-index is inert on statically positioned elements, which let the
        scrollable content below paint its opaque backgrounds (e.g. the état
        info alert) over the navbar's drop shadow. Relative positioning lifts
        the navbar and its shadow above that content without altering flow.
      */}
      <AppBar position="relative">
        <Container>
          <Stack
            direction="row"
            alignItems="center"
            justifyContent="space-between"
            spacing={1}
            sx={{ py: 1 }}
          >
            <Stack direction="row" alignItems="center" spacing={1}>
              <MobileNavDrawer />
              <Button
                component={OurLink}
                href={`/${ROOT_SLUG}/`}
                color="inherit"
              >
                {SITE_NAME}
              </Button>
              <Button
                component={OurLink}
                href={`${DOSSIERS_BASE}/`}
                color="inherit"
                sx={{ display: { xs: "none", lg: "inline-flex" } }}
              >
                {tBrowse("dossiers")}
              </Button>
              <Button
                component={OurLink}
                href={`${EVENTS_BASE}/`}
                color="inherit"
                sx={{ display: { xs: "none", lg: "inline-flex" } }}
              >
                {tBrowse("events")}
              </Button>
            </Stack>
            <Stack direction="row" alignItems="center" spacing={1}>
              <LanguageSwitcher />
              <Button
                component="a"
                href="https://dezede.hypotheses.org/8934"
                color="inherit"
                variant="outlined"
                startIcon={<LaunchIcon />}
                sx={{ display: { xs: "none", lg: "inline-flex" } }}
              >
                {t("protocol")}
              </Button>
              <Button
                component="a"
                href="/"
                color="inherit"
                variant="outlined"
                startIcon={<LaunchIcon />}
                sx={{ display: { xs: "none", lg: "inline-flex" } }}
              >
                Dezède
              </Button>
            </Stack>
          </Stack>
        </Container>
      </AppBar>
      <MainScrollArea
        id="main-content"
        sx={{
          flexGrow: 1,
          minHeight: 0,
          display: "flex",
          flexDirection: "column",
          py: 4,
        }}
      >
        <SourceModalProvider>{children}</SourceModalProvider>
      </MainScrollArea>
    </Box>
  );
}
