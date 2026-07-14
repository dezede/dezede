import { ReactNode } from "react";
import Card from "@mui/material/Card";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Divider from "@mui/material/Divider";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import { getLocale, getTranslations } from "next-intl/server";
import { TDossierDetail, TDossierUser } from "@/app/types";
import type { Locale } from "@/i18n/config";
import { getDateLabel } from "@/format/DateLabel";
import RichText from "@/components/RichText";
import DossierExportButtons from "@/components/DossierExportButtons";

// One labelled metadata block, dropped entirely when it has no content — the
// same "only emit non-empty rows" rule the Django sidebar follows with its
// `{% if %}` guards.
function Field({ label, children }: { label: string; children: ReactNode }) {
  if (!children) {
    return null;
  }
  return (
    <Stack spacing={0.5}>
      <Typography variant="subtitle2" color="textDisabled">
        {label}
      </Typography>
      <div>{children}</div>
    </Stack>
  );
}

// Renders a list of people (scientific editors, contributors) as person chips,
// each linking to that user's public Django profile page (`url`). The
// musicaLetters frontend has no profile route, so these are plain anchors that
// trigger a full navigation to the legacy site rather than Next.js links.
// Returns null when empty so the surrounding `Field` drops the whole block.
function UserChips({ users }: { users: TDossierUser[] }) {
  if (users.length === 0) {
    return null;
  }
  return (
    <Stack direction="row" spacing={0.5} useFlexGap sx={{ flexWrap: "wrap" }}>
      {users.map((user, index) => (
        <Chip
          key={`${user.url}-${index}`}
          component="a"
          href={user.url}
          clickable
          icon={<PersonOutlineIcon />}
          label={user.name}
          size="small"
          variant="outlined"
        />
      ))}
    </Stack>
  );
}

/**
 * Right-hand metadata/actions panel for a dossier detail page, porting the
 * Django dossier sidebar (`dossiers/include/sidebar_base.html` +
 * `dossierdevenements_sidebar.html`): scientific editors, contributors, the
 * publication date, the associated-publications / planned-developments
 * notes, and — for the right users — the PDF and statistics exports.
 */
export default async function DossierSidebar({
  dossier,
}: {
  dossier: TDossierDetail;
}) {
  const t = await getTranslations("pages");
  const locale = (await getLocale()) as Locale;

  const publicationDate = dossier.date_publication
    ? getDateLabel(dossier.date_publication, "", locale)
    : "";
  const hasNotes = Boolean(dossier.publications || dossier.developpements);
  const canExport = dossier.can_export_pdf || dossier.can_export_stats;

  return (
    <Card variant="outlined" component="aside">
      <Stack spacing={2.5} sx={{ p: 2.5 }}>
        <Field
          label={t("dossiers.scientificEditors", {
            count: dossier.editeurs_scientifiques.length,
          })}
        >
          <UserChips users={dossier.editeurs_scientifiques} />
        </Field>

        <Field
          label={t("dossiers.contributors", {
            count: dossier.contributors.length,
          })}
        >
          <UserChips users={dossier.contributors} />
        </Field>

        <Field label={t("dossiers.publicationDate")}>{publicationDate}</Field>

        {hasNotes ? <Divider /> : null}

        <Field label={t("dossiers.associatedPublications")}>
          {dossier.publications ? (
            <RichText value={dossier.publications} />
          ) : null}
        </Field>

        <Field label={t("dossiers.plannedDevelopments")}>
          {dossier.developpements ? (
            <RichText value={dossier.developpements} />
          ) : null}
        </Field>

        {canExport ? (
          <DossierExportButtons
            dossierId={dossier.id}
            canExportPdf={dossier.can_export_pdf}
            canExportStats={dossier.can_export_stats}
            scenarioChoices={dossier.scenario_choices ?? []}
          />
        ) : null}
      </Stack>
    </Card>
  );
}
