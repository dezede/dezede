import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { TAsyncSearchParams, TDossierDetail } from "@/app/types";
import { DOSSIERS_BASE } from "@/app/constants";
import { fetchPublicJson } from "@/app/events";
import OurLink from "@/components/OurLink";
import RichText from "@/components/RichText";
import SafeText from "@/format/SafeText";
import DetailAdminBar from "@/components/DetailAdminBar";
import DossierTabs, { TDossierTabItem } from "@/components/DossierTabs";
import DossierKindPanel from "@/components/DossierKindPanel";
import DossierData from "@/components/DossierData";
import DossierCard, { kindLabel } from "@/components/DossierCard";
import DossierStats from "@/components/DossierStats";
import DossierMapSection from "@/components/DossierMapSection";
import DossierSidebar from "@/components/DossierSidebar";
import JumpToPresentationButton from "@/components/JumpToPresentationButton";
import CitationReference from "@/components/CitationReference";

const apiBase = "/api/public/dossiers/";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ pk: string }>;
}): Promise<Metadata> {
  const { pk } = await params;
  const dossier = await fetchPublicJson<TDossierDetail>(`${apiBase}${pk}/`);
  const t = await getTranslations();
  return {
    title: t("pages.titleTemplate", {
      name: dossier.titre.replace(/<[^>]*>/g, ""),
    }),
  };
}

function Section({ title, body }: { title: string; body: string }) {
  if (!body) {
    return null;
  }
  return (
    <Stack spacing={1} component="section">
      <Typography variant="h2" sx={{ fontSize: "1.5rem" }}>
        {title}
      </Typography>
      <RichText value={body} />
    </Stack>
  );
}

export default async function DossierDetailPage({
  params,
  searchParams,
}: {
  params: Promise<{ pk: string }>;
  searchParams: TAsyncSearchParams;
}) {
  const { pk } = await params;
  const resolvedSearchParams = await searchParams;
  const t = await getTranslations("pages");
  const tDossiers = await getTranslations("dossiers");
  const dossier = await fetchPublicJson<TDossierDetail>(`${apiBase}${pk}/`);
  // One tab per active kind actually holding data; a dossier whose kinds are
  // all empty has nothing to show besides the Présentation, so the tab chrome
  // itself is dropped and only the Présentation content is rendered directly.
  const dataKinds = dossier.kinds.filter(
    (kind) => (dossier.counts[kind] ?? 0) > 0,
  );

  const subdossiers =
    dossier.children.length > 0 ? (
      <Stack spacing={2} component="section">
        <Typography variant="h2" sx={{ fontSize: "1.5rem" }}>
          {t("dossiers.subDossiers")}
        </Typography>
        <Grid container spacing={2}>
          {dossier.children.map((child) => (
            <Grid key={child.id} size={{ xs: 12, sm: 6, md: 4 }}>
              <DossierCard dossier={child} />
            </Grid>
          ))}
        </Grid>
      </Stack>
    ) : null;

  // The metadata/actions sidebar lives inside the Présentation tab (regardless
  // of the dossier kinds), so it is hidden on the per-kind data tabs.
  const presentation = (
    <Grid container spacing={4} id="presentation">
      <Grid size={{ xs: 12, md: 8 }}>
        <Stack spacing={3}>
          <Section title={t("presentation")} body={dossier.presentation} />
          <Section title={t("contexte")} body={dossier.contexte} />
          <Section
            title={t("sourcesEtProtocole")}
            body={dossier.sources_et_protocole}
          />
          <Section title={t("bibliographie")} body={dossier.bibliographie} />
          <CitationReference
            label={t("dossiers.citationLabel")}
            citation={dossier.citation}
            accessDate={new Date().toISOString().slice(0, 10)}
          />
        </Stack>
      </Grid>
      <Grid size={{ xs: 12, md: 4 }}>
        <Box sx={{ position: { md: "sticky" }, top: 16 }}>
          <DossierSidebar dossier={dossier} />
        </Box>
      </Grid>
    </Grid>
  );

  const tabs: TDossierTabItem[] = [
    {
      slug: "presentation",
      label: tDossiers("presentation"),
      content: presentation,
    },
    ...dataKinds.map((kind) => {
      // Events and works get a Visualisations sub-view (map + statistics)
      // inside their tab; sources are a plain data list.
      const visualisations = dossier.stats_kinds.includes(kind) ? (
        <Stack spacing={4}>
          <Box component="section">
            <Typography variant="h2" sx={{ fontSize: "1.25rem", mb: 1.5 }}>
              {t("dossiers.map")}
            </Typography>
            <DossierMapSection
              geojsonUrl={`${apiBase}${pk}/geojson/?kind=${kind}`}
            />
          </Box>
          <DossierStats
            statsUrl={`${apiBase}${pk}/stats/?kind=${kind}`}
            kind={kind === "oeuvres" ? "oeuvres" : "evenements"}
          />
        </Stack>
      ) : undefined;
      return {
        slug: kind,
        // Show the amount of data in the tab label (e.g. "56 événements"),
        // reusing the same count formatting as the dossier cards.
        label: kindLabel(kind, dossier.counts[kind] ?? 0, tDossiers),
        content: (
          <DossierKindPanel
            slug={kind}
            data={
              <DossierData
                dossier={dossier}
                kind={kind}
                searchParams={resolvedSearchParams}
              />
            }
            visualisations={visualisations}
          />
        ),
      };
    }),
  ];

  return (
    <Container>
      <Stack spacing={3}>
        <Button
          component={OurLink}
          href={`${DOSSIERS_BASE}/`}
          startIcon={<ChevronLeftIcon />}
          sx={{ alignSelf: "flex-start" }}
        >
          {t("dossiers.backToAll")}
        </Button>
        <Stack
          direction="row"
          spacing={2}
          sx={{
            justifyContent: "space-between",
            alignItems: "flex-start",
          }}
        >
          <Typography variant="h1" sx={{ m: 0 }}>
            <SafeText value={dossier.titre} />
          </Typography>
          <DetailAdminBar {...dossier} />
        </Stack>
        {dossier.children.length > 0 ? (
          <JumpToPresentationButton label={tDossiers("jumpToPresentation")} />
        ) : null}
        {subdossiers}
        {dataKinds.length > 0 ? <DossierTabs tabs={tabs} /> : presentation}
      </Stack>
    </Container>
  );
}
