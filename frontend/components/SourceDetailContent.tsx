"use client";

import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { useTranslations } from "next-intl";
import { TSourceDetail } from "@/app/types";
import { capfirst, joinWithLast } from "@/app/utils";
import HashTabs, { TTabPanel } from "@/components/HashTabs";
import DetailTable from "@/components/DetailTable";
import EntityChipList from "@/components/EntityChipList";
import EtatBadge from "@/components/EtatBadge";
import RichText from "@/components/RichText";
import { entityChipRow } from "@/components/entityChipRow";
import SourceMedia from "@/components/SourceMedia";
import CitationReference from "@/components/CitationReference";
import DateLabel from "@/format/DateLabel";

// The Présentation tab's right-hand sidebar — the Next.js equivalent of the
// Django `sidebar_base.html`: the source's scientific editor(s), its online
// publication date, and any associated publications / planned developments.
// The editor names and publication date are reused from the citation payload
// (always present whenever the Présentation tab is shown). Renders nothing when
// none of these fields are set.
function PresentationSidebar({ source }: { source: TSourceDetail }) {
  const t = useTranslations("pages");
  const editeurs = source.citation?.editeurs ?? [];
  const datePublication = source.citation?.date_publication ?? null;

  const topItems: { key: string; label: string; content: React.ReactNode }[] =
    [];
  if (editeurs.length > 0) {
    topItems.push({
      key: "editeurs",
      label:
        editeurs.length < 2
          ? t("sources.editeurScientifique")
          : t("sources.editeursScientifiques"),
      content: joinWithLast(editeurs),
    });
  }
  if (datePublication) {
    topItems.push({
      key: "date",
      label: t("sources.datePublication"),
      content: <DateLabel dateString={datePublication} />,
    });
  }

  const bottomItems: {
    key: string;
    label: string;
    content: React.ReactNode;
  }[] = [];
  if (source.publications) {
    bottomItems.push({
      key: "publications",
      label: t("sources.publications"),
      content: <RichText value={source.publications} />,
    });
  }
  if (source.developpements) {
    bottomItems.push({
      key: "developpements",
      label: t("sources.developpements"),
      content: <RichText value={source.developpements} />,
    });
  }

  if (topItems.length === 0 && bottomItems.length === 0) {
    return null;
  }

  const renderItem = (item: {
    key: string;
    label: string;
    content: React.ReactNode;
  }) => (
    <Box key={item.key} component="div">
      <Typography variant="subtitle2" color="textDisabled" component="dt">
        {item.label}
      </Typography>
      <Box component="dd" sx={{ m: 0 }}>
        {item.content}
      </Box>
    </Box>
  );

  return (
    <Paper
      component="aside"
      variant="outlined"
      sx={{
        p: 2,
        width: { xs: "100%", md: 300 },
        flexShrink: 0,
        bgcolor: "action.hover",
      }}
    >
      <Stack component="dl" spacing={2} sx={{ m: 0 }}>
        {topItems.map(renderItem)}
        {topItems.length > 0 && bottomItems.length > 0 ? <Divider /> : null}
        {bottomItems.map(renderItem)}
      </Stack>
    </Paper>
  );
}

// The Présentation tab: the source's free-text editorial sections plus its
// bibliographic citation, with the metadata sidebar on the right. The leading
// "Présentation" section has no heading, matching the Django frontend.
function Presentation({ source }: { source: TSourceDetail }) {
  const t = useTranslations("pages");
  const sections: { key: string; label: string | null; value: string }[] = [
    { key: "presentation", label: null, value: source.presentation },
    { key: "contexte", label: t("contexte"), value: source.contexte },
    {
      key: "sources_et_protocole",
      label: t("sourcesEtProtocole"),
      value: source.sources_et_protocole,
    },
    {
      key: "bibliographie",
      label: t("bibliographie"),
      value: source.bibliographie,
    },
  ].filter((section) => section.value);

  return (
    <Stack
      direction={{ xs: "column", md: "row" }}
      spacing={3}
      sx={{ alignItems: "flex-start" }}
    >
      <Stack spacing={3} sx={{ flex: 1, minWidth: 0 }}>
        {sections.map((section) => (
          <Stack key={section.key} spacing={1} component="section">
            {section.label ? (
              <Typography variant="h2" sx={{ fontSize: "1.5rem" }}>
                {section.label}
              </Typography>
            ) : null}
            <RichText value={section.value} />
          </Stack>
        ))}
        {source.citation ? (
          <CitationReference
            label={t("sources.citationLabel")}
            citation={source.citation}
            accessDate={new Date().toISOString().slice(0, 10)}
          />
        ) : null}
      </Stack>
      <PresentationSidebar source={source} />
    </Stack>
  );
}

// The Index tab: the source's parent, authors and the catalogue entities it
// references, plus the events it documents and any public notes. The
// events-by-year block is supplied by the caller (server- or client-rendered),
// since the underlying events fetch differs across the client boundary.
function Index({
  source,
  relatedEvents,
}: {
  source: TSourceDetail;
  relatedEvents: React.ReactNode;
}) {
  const t = useTranslations("pages");
  return (
    <Stack spacing={3}>
      <DetailTable
        rows={[
          {
            key: "parent",
            label: t("sources.parentSource"),
            content: source.parent ? (
              <EntityChipList entities={[source.parent]} />
            ) : null,
          },
          {
            key: "auteurs",
            label: t("sources.authors"),
            content: source.auteurs_html ? (
              <RichText value={source.auteurs_html} />
            ) : null,
          },
          entityChipRow(
            "individus",
            { one: t("nouns.person.one"), other: t("nouns.person.other") },
            source.nested_individus,
          ),
          entityChipRow(
            "oeuvres",
            { one: t("nouns.work.one"), other: t("nouns.work.other") },
            source.nested_oeuvres,
          ),
          entityChipRow(
            "parties",
            {
              one: t("nouns.roleOrInstrument.one"),
              other: t("nouns.roleOrInstrument.other"),
            },
            source.nested_parties,
          ),
          entityChipRow(
            "lieux",
            { one: t("nouns.place.one"), other: t("nouns.place.other") },
            source.nested_lieux,
          ),
          entityChipRow(
            "ensembles",
            { one: t("nouns.ensemble.one"), other: t("nouns.ensemble.other") },
            source.nested_ensembles,
          ),
        ]}
      />
      {relatedEvents}
      {source.notes_publiques ? (
        <DetailTable
          rows={[
            {
              key: "notes",
              label: t("rows.notes"),
              content: <RichText value={source.notes_publiques} />,
            },
          ]}
        />
      ) : null}
    </Stack>
  );
}

/**
 * The body of a source — its type/légende meta lines, état badge and the
 * Présentation / Consulter / Index tabs (opening on Consulter when the source
 * has viewable content). Shared between the standalone source detail page,
 * which wraps it with its own title and back button, and `SourceModal`, which
 * shows it in a dialog. The modal passes `syncHash={false}` so switching tabs
 * doesn't write to the page URL hash.
 */
export default function SourceDetailContent({
  source,
  relatedEvents,
  syncHash = true,
}: {
  source: TSourceDetail;
  relatedEvents: React.ReactNode;
  syncHash?: boolean;
}) {
  const t = useTranslations("pages");

  const hasConsulterContent =
    source.media !== null ||
    source.images.length > 0 ||
    source.collection_children.length > 0 ||
    source.transcription !== "" ||
    source.download !== null;

  const panels: TTabPanel[] = [];
  if (source.has_presentation_tab) {
    panels.push({
      slug: "presentation",
      label: t("presentation"),
      content: <Presentation source={source} />,
    });
  }
  let consulterIndex = 0;
  if (hasConsulterContent) {
    consulterIndex = panels.length;
    panels.push({
      slug: "consulter",
      label: t("sources.consult"),
      content: <SourceMedia source={source} />,
    });
  }
  if (source.has_index_tab) {
    panels.push({
      slug: "index",
      label: t("sources.index"),
      content: <Index source={source} relatedEvents={relatedEvents} />,
    });
  }

  return (
    <Stack spacing={3}>
      {source.type ? (
        <Typography color="text.secondary">{capfirst(source.type)}</Typography>
      ) : null}
      {source.legende ? (
        <Typography color="text.secondary">{source.legende}</Typography>
      ) : null}
      <EtatBadge etat={source.etat} />
      <HashTabs
        panels={panels}
        defaultIndex={consulterIndex}
        syncHash={syncHash}
      />
    </Stack>
  );
}
