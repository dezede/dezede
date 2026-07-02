import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { TDossierIndex } from "@/app/types";
import { fetchPublicJson } from "@/app/events";
import DossierCard from "@/components/DossierCard";
import DossierHelpCard from "@/components/DossierHelpCard";
import DossierIndexBrowser from "@/components/DossierIndexBrowser";
import Empty from "@/components/Empty";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations();
  return {
    title: t("pages.titleTemplate", { name: t("pages.dossiers.listTitle") }),
  };
}

export default async function DossiersPage() {
  const t = await getTranslations("pages");
  const index = await fetchPublicJson<TDossierIndex>("/api/public/dossiers/");

  // Dossiers already come back most-recently-published first (see the API's
  // list() ordering); the chip filter only ever narrows this same order down
  // to one category, it never re-sorts.
  const items = index.dossiers.map((dossier) => ({
    id: dossier.id,
    categorieId: dossier.categorie_id,
    node: <DossierCard dossier={dossier} key={dossier.id} />,
  }));

  return (
    <Container>
      <Stack spacing={4}>
        <Typography variant="h1">{t("dossiers.listTitle")}</Typography>
        {index.dossiers.length === 0 ? (
          <Empty>{t("dossiers.empty")}</Empty>
        ) : null}
        <DossierIndexBrowser
          categories={index.categories}
          items={items}
          helpItem={<DossierHelpCard />}
          allLabel={t("dossiers.allCategories")}
        />
      </Stack>
    </Container>
  );
}
