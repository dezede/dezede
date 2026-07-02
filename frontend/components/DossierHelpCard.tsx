import { ReactNode } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Link from "@mui/material/Link";
import { getTranslations } from "next-intl/server";

// Mirrors the "Qu'est-ce qu'un dossier ?" help box from the Django dossiers index
// (dossiers/templates/dossiers/categoriededossiers_list.html). Shaped like a
// DossierCard but informational, so it sits naturally in the dossiers grid.
export default async function DossierHelpCard() {
  const t = await getTranslations("pages.dossiers");
  return (
    <Card variant="outlined" sx={{ height: "100%" }}>
      <CardContent sx={{ p: 2 }}>
        <Stack spacing={1}>
          <Typography variant="h3" sx={{ fontSize: "1.1rem", m: 0 }}>
            {t("helpTitle")}
          </Typography>
          <Typography variant="body2">
            {t.rich("helpText", {
              // /comite-editorial is served by Django, not the Next router, so a
              // plain anchor (full page navigation) rather than a Next link.
              link: (chunks: ReactNode) => (
                <Link href="/comite-editorial">{chunks}</Link>
              ),
            })}
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
