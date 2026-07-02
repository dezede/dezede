import {
  EExtractCategory,
  EPartType,
  TAuteur,
  TRelatedWork,
} from "@/app/types";
import Chip from "@mui/material/Chip";
import Tooltip from "@mui/material/Tooltip";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import HistoryEduOutlinedIcon from "@mui/icons-material/HistoryEduOutlined";
import { capfirst, toRoman } from "@/app/utils";
import { buildSectionLabel } from "./SectionLabel";
import {
  joinNodes,
  joinNodesWithLast,
  LabelNodes,
  labelToText,
  TLabelNode,
} from "./richLabel";
import { CastingText, type TCastingElement } from "./Casting";
import OurLink from "@/components/OurLink";
import { WORKS_BASE } from "@/app/constants";
import { useTranslations } from "next-intl";

/**
 * The work's characteristics, each a list of label nodes, mirroring Django's
 * `Oeuvre.caracteristiques_iterator`: most are wrapped in a tooltip whose type
 * label comes from the `work` translation namespace (Django's `hlp(valeur,
 * type)` `title="…"` span); the tonalité italicizes its note name (`em(note)`);
 * and the editor-authored fields (sujet/surnom/nom_courant) pass through as raw
 * `html`.
 */
function* getFeaturesList({
  numero,
  coupe,
  incipit,
  tempo,
  genre,
  tonalite,
  sujet,
  arrangement,
  surnom,
  nom_courant,
  opus,
  ict,
}: TRelatedWork): Generator<TLabelNode[]> {
  if (numero) {
    yield [{ text: `n° ${numero}` }];
  }
  if (coupe) {
    yield [{ text: `en ${coupe}`, tooltipKey: "coupe" }];
  }
  if (incipit) {
    yield [{ text: `« ${incipit} »`, tooltipKey: "incipit" }];
  }
  if (tempo && genre) {
    yield [{ text: tempo, tooltipKey: "tempo" }];
  }
  if (tonalite) {
    // The raw tonalité code; localised (note italicised) at render time by
    // `tonaliteNodes` — see {@link TLabelNode.tonalite}.
    yield [{ tonalite }];
  }
  if (sujet) {
    yield [{ html: `sur ${sujet}`, tooltipKey: "sujet" }];
  }
  if (arrangement) {
    yield [{ text: `(${arrangement})` }];
  }
  if (surnom) {
    yield [{ html: `(${surnom})`, tooltipKey: "surnom" }];
  }
  if (nom_courant) {
    yield [{ html: nom_courant, tooltipKey: "nomCourant" }];
  }
  if (opus) {
    yield [{ text: `op. ${opus}`, tooltipKey: "opus" }];
  }
  if (ict) {
    yield [{ text: ict, tooltipKey: "thematicCatalogueNumber" }];
  }
}

function getSignificantTitle({
  prefixe_titre,
  titre,
  coordination,
  prefixe_titre_secondaire,
  titre_secondaire,
}: TRelatedWork): string {
  return `${prefixe_titre}${titre}${coordination}${prefixe_titre_secondaire}${titre_secondaire}`;
}

function getSections(work: TRelatedWork): TLabelNode[] {
  const { pupitres } = work;
  // `pupitres` is absent on ancestor (`extrait_de`) payloads, which carry only
  // label fields; a titleless ancestor would otherwise reach here and throw.
  if (!pupitres || pupitres.length === 0) {
    return [];
  }
  const soloSections = pupitres.filter(({ soliste }) => soliste);
  const instrumentSections = joinNodesWithLast(
    soloSections
      .filter(({ partie: { part_type } }) => part_type === EPartType.INSTRUMENT)
      .map((section) => buildSectionLabel(section)),
  );
  const roleSections = joinNodesWithLast(
    soloSections
      .filter(({ partie: { part_type } }) => part_type === EPartType.ROLE)
      .map((section) => buildSectionLabel(section)),
  );
  if (roleSections.length > 0) {
    const output: TLabelNode[] = [{ text: "de " }, ...roleSections];
    if (instrumentSections.length > 0) {
      output.push({ text: " avec " }, ...instrumentSections);
    }
    return output;
  }
  // No solo sections at all → no "pour …" clause (mirrors Django's
  // `get_pupitres_str(solistes=True)` returning '' when there are none).
  if (instrumentSections.length > 0) {
    return [{ text: "pour " }, ...instrumentSections];
  }
  return [];
}

function getNonSignificantTitle(
  work: TRelatedWork,
  caps: boolean,
): TLabelNode[] {
  const { genre, tempo } = work;
  if (!tempo && genre === null) {
    return [];
  }
  const head = genre === null ? tempo : genre.nom;
  const firstFeature = getFeaturesList(work).next().value ?? [];
  return joinNodes(
    [[{ text: caps ? capfirst(head) : head }], getSections(work), firstFeature],
    " ",
  );
}

/** Whether the work's excerpt type hides its designator when the work has no
 * title (Django's `TYPES_EXTRAIT_CACHES`: morceau, mouvement, pièce). */
function isHiddenExtrait({ categorie_type_extrait }: TRelatedWork): boolean {
  return (
    categorie_type_extrait === EExtractCategory.NUMERO ||
    categorie_type_extrait === EExtractCategory.ORDINAL
  );
}

/**
 * The excerpt designator ("№ 5", "Acte II", "1.", …), mirroring Django's
 * `Oeuvre.get_extrait`. `showType` prepends the excerpt's type name ("acte 2");
 * it is dropped when this work is rendered as an ancestor of another.
 */
function getExtrait(work: TRelatedWork, showType: boolean): string {
  const { type_extrait, numero_extrait, categorie_type_extrait } = work;
  if (!type_extrait || !numero_extrait) {
    return "";
  }
  const match = /^([1-9]\d*)([^\d.\-]*)$/.exec(numero_extrait);
  if (match === null) {
    return "";
  }
  const [, digits, suffix] = match;
  const number =
    categorie_type_extrait === EExtractCategory.ROMAN
      ? toRoman(parseInt(digits, 10))
      : digits;
  const out = `${number}${suffix}`;
  switch (categorie_type_extrait) {
    case EExtractCategory.NUMERO:
      return `№ ${out}`;
    case EExtractCategory.ORDINAL:
      return `${out}.`;
    default:
      return showType ? `${type_extrait} ${out}` : out;
  }
}

/**
 * The parent-work chain prepended to an excerpt's title, mirroring Django's
 * `Oeuvre.get_referent_ancestors_html`: the parent's full label (recursively,
 * with its excerpt *type* dropped and, when `links`, each ancestor linked to
 * its own page), unless this work has no parent or its own genre is a "referent"
 * (a genre that stands on its own, e.g. an opera's overture).
 */
function getReferentAncestors(
  work: TRelatedWork,
  links: boolean,
): TLabelNode[] {
  const { extrait_de, genre } = work;
  if (extrait_de === null || genre?.referent) {
    return [];
  }
  return buildWorkLabel(extrait_de, {
    showTypeExtrait: false,
    links,
    linkSelf: links,
  });
}

type WorkLabelOptions = {
  showTypeExtrait?: boolean;
  // Link the ancestor chain (each ancestor → its own page).
  links?: boolean;
  // Link this work's own title to its page (used for ancestors, not the root).
  linkSelf?: boolean;
};

/**
 * Build an œuvre's label as rich-label nodes, mirroring Django's
 * `Oeuvre.titre_html` (ancestors + excerpt designator + title), with the
 * significant title wrapped in `<cite>` and editor HTML preserved. Rendered to
 * JSX by {@link WorkLabel} and to plain text by {@link getWorkLabel}.
 */
export function buildWorkLabel(
  work: TRelatedWork,
  {
    showTypeExtrait = true,
    links = false,
    linkSelf = false,
  }: WorkLabelOptions = {},
): TLabelNode[] {
  const ancestors = getReferentAncestors(work, links);
  const hidden = isHiddenExtrait(work);
  let title: TLabelNode[] = work.titre
    ? [{ html: getSignificantTitle(work), cite: true }]
    : getNonSignificantTitle(work, work.type_extrait === null || hidden);
  const extrait = capfirst(getExtrait(work, showTypeExtrait));
  if (extrait) {
    if (title.length > 0) {
      title = [{ text: `${extrait} ` }, ...title];
    } else if (!hidden) {
      title = [{ text: extrait }];
    }
  }
  if (linkSelf && work.id && title.length > 0) {
    title = [{ href: `${WORKS_BASE}/id/${work.id}/`, children: title }];
  }
  return joinNodes([ancestors, title], ", ");
}

export function getWorkLabel(
  work: TRelatedWork,
  // A `work`-scoped translator (`useTranslations("work")` /
  // `getTranslations("work")`), needed to localise any tonalité in the label.
  t: (key: string) => string,
  options?: WorkLabelOptions,
): string {
  return labelToText(buildWorkLabel(work, options), t);
}

/**
 * The work's descriptive subtitle — genre/tempo and characteristics — as a list
 * of per-characteristic node lists, mirroring Django's `Oeuvre.get_description`
 * (`description_html`, the `<h4>` under the title). When the work has a
 * significant title, the description leads with its genre/tempo and full
 * characteristics; otherwise that genre + first characteristic is already in
 * {@link getWorkLabel}, so only the remaining characteristics are shown here.
 */
export function getWorkDescription(work: TRelatedWork): TLabelNode[][] {
  const { genre, tempo, titre } = work;
  const hasSignificantTitle = Boolean(titre);
  const hasNonSignificantTitle = Boolean(tempo) || genre !== null;
  const characteristics = [...getFeaturesList(work)];

  const parts: TLabelNode[][] = [];
  // When there's a real title, the genre/tempo + first characteristic (the
  // non-significant title, minus the sections reserved for an actual title)
  // lead the description.
  if (hasSignificantTitle && hasNonSignificantTitle) {
    parts.push([{ text: genre === null ? tempo : genre.nom }]);
    if (characteristics[0]) {
      parts.push(characteristics[0]);
    }
  }
  // The first characteristic is consumed by the (non-)significant title above.
  const rest = hasNonSignificantTitle
    ? characteristics.slice(1)
    : characteristics;
  parts.push(...rest);
  return parts.filter((nodes) => labelToText(nodes) !== "");
}

/**
 * Renders a work's descriptive subtitle (the output of
 * {@link getWorkDescription}), with each characteristic's type as a tooltip and
 * the tonalité note italicized. Returns `null` when there is nothing to show.
 */
export function WorkDescription({ work }: { work: TRelatedWork }) {
  const features = getWorkDescription(work);
  if (features.length === 0) {
    return null;
  }
  return <LabelNodes nodes={joinNodes(features, " ")} />;
}

/** The formatted (JSX) work label. `links` turns the ancestor chain into links
 * (use only where the label isn't already inside a link, to avoid nested `<a>`). */
export function WorkLabel({
  work,
  links = false,
}: {
  work: TRelatedWork;
  links?: boolean;
}) {
  return <LabelNodes nodes={buildWorkLabel(work, { links })} />;
}

// A work as rendered by a chip: the base related work, optionally carrying the
// authors that richer endpoints (programme, dossier list, search) expose.
type TWorkChip = TRelatedWork & { auteurs?: TAuteur[] };

/** The authors as {@link TCastingElement}s, grouped and bracketed like
 * Django's `BiGrouper` ("Mozart [compositeur], Da Ponte [librettiste]") by
 * {@link CastingText}. */
function getAuthorElements(auteurs: TAuteur[] | undefined): TCastingElement[] {
  return (auteurs ?? []).map((auteur) => ({
    individu: auteur.individu,
    ensemble: auteur.ensemble,
    partie: null,
    profession: auteur.profession,
  }));
}

/**
 * The work's detail shown on chip hover — authors, full title and descriptive
 * subtitle. Mostly plain text (not {@link WorkLabel}/{@link WorkDescription})
 * to avoid nesting the interactive tooltips those emit; the authors keep their
 * small-caps surnames via {@link CastingText}.
 */
function WorkTooltipBody(work: TWorkChip) {
  // The `work` namespace localises the tonalité vocabulary inside the label.
  const t = useTranslations("work");
  const authorElements = getAuthorElements(work.auteurs);
  const title = getWorkLabel(work, t);
  const subtitle = labelToText(joinNodes(getWorkDescription(work), " "), t);
  return (
    <Box>
      {authorElements.length > 0 ? (
        <Typography variant="caption" color="inherit" display="block">
          <CastingText elements={authorElements} />
        </Typography>
      ) : null}
      <Typography variant="body2" sx={{ fontWeight: "bold" }}>
        {title}
      </Typography>
      {subtitle ? (
        <Typography variant="caption" color="inherit" display="block">
          {subtitle}
        </Typography>
      ) : null}
    </Box>
  );
}

export default function WorkChip(work: TWorkChip) {
  return (
    <Tooltip
      title={<WorkTooltipBody {...work} />}
      placement="top"
      arrow
      disableInteractive
    >
      <Chip
        component={OurLink}
        href={`${WORKS_BASE}/id/${work.id}/`}
        label={<WorkLabel work={work} />}
        clickable
        size="small"
        icon={<HistoryEduOutlinedIcon />}
      />
    </Tooltip>
  );
}
