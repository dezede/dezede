import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import { TDossierWork } from "@/app/types";
import { WORKS_BASE } from "@/app/constants";
import OurLink from "@/components/OurLink";
import SourcesPanel from "@/components/SourcesPanel";
import Casting, { TCastingElement } from "@/format/Casting";
import {
  getWorkDescription,
  WorkDescription,
  WorkLabel,
} from "@/format/WorkChip";

/**
 * One work in a dossier d'œuvres list: its (linked) title, descriptive subtitle
 * (genre/characteristics), authors grouped by profession, its world-premiere
 * line ("Genèse et création") and its grouped sources. Mirrors Django's
 * `dossierdoeuvres_data_detail` per-work block.
 */
export default function WorkListItem({ work }: { work: TDossierWork }) {
  const authors: TCastingElement[] = work.auteurs.map((auteur) => ({
    individu: auteur.individu,
    ensemble: auteur.ensemble,
    partie: null,
    profession: auteur.profession,
  }));
  const hasDescription = getWorkDescription(work).length > 0;

  return (
    <Card variant="outlined" sx={{ p: 2 }}>
      <Stack spacing={1.5}>
        <Box>
          <Link
            component={OurLink}
            href={`${WORKS_BASE}/id/${work.id}/`}
            underline="hover"
            color="inherit"
            sx={{ fontWeight: 500 }}
          >
            <WorkLabel work={work} />
          </Link>
          {hasDescription ? (
            <Typography variant="body2" color="text.secondary">
              <WorkDescription work={work} />
            </Typography>
          ) : null}
        </Box>
        {authors.length > 0 ? (
          <Stack direction="row" flexWrap="wrap" useFlexGap spacing={0.5}>
            <Casting elements={authors} />
          </Stack>
        ) : null}
        {work.creation ? (
          <Typography variant="body2" color="text.secondary">
            {work.creation}
          </Typography>
        ) : null}
        {work.sources.length > 0 ? (
          <Box>
            <SourcesPanel groups={work.sources} modal />
          </Box>
        ) : null}
      </Stack>
    </Card>
  );
}
