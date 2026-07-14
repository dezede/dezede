"use client";

import { useTranslations } from "next-intl";
import Tooltip from "@mui/material/Tooltip";
import BoyOutlinedIcon from "@mui/icons-material/BoyOutlined";
import OurChip from "@/components/OurChip";
import { abbreviate, withParticule } from "@/app/utils";
import { EPersonDesignation, TRelatedPerson } from "@/app/types";
import SmallCaps from "./SmallCaps";
import OurLink from "@/components/OurLink";
import SafeText from "./SafeText";
import { PERSONS_BASE } from "@/app/constants";
import Box, { type BoxProps } from "@mui/material/Box";
import Typography from "@mui/material/Typography";

function getSmallCapsLabel({
  designation,
  particule_nom,
  nom,
  particule_nom_naissance,
  nom_naissance,
  prenoms,
  pseudonyme,
}: TRelatedPerson): string {
  switch (designation) {
    case EPersonDesignation.STANDARD:
    case EPersonDesignation.LAST_NAME:
      return withParticule(particule_nom, nom);
    case EPersonDesignation.FIRST_NAME:
      return prenoms;
    case EPersonDesignation.PSEUDONYME:
      return pseudonyme;
    case EPersonDesignation.BIRTH_NAME:
      return withParticule(particule_nom_naissance, nom_naissance);
  }
}

// A `common`-scoped translator, used to localise the pseudonyme prefix
// ("dit"/"dite" in French, "also known as" in English \u2014 see the `knownAs` key).
export type TKnownAsTranslator = (
  key: string,
  values?: Record<string, string | number>,
) => string;

function getPseudonymeSuffix(
  { titre, pseudonyme }: TRelatedPerson,
  t: TKnownAsTranslator,
) {
  return `${t("knownAs", { titre })}\u00A0${pseudonyme}`;
}

export function getPersonLabel(
  person: TRelatedPerson,
  t: TKnownAsTranslator,
): string {
  const { prenoms, titre_display, pseudonyme } = person;
  let label = getSmallCapsLabel(person);
  switch (person.designation) {
    case EPersonDesignation.STANDARD:
    case EPersonDesignation.BIRTH_NAME:
      if (titre_display && !prenoms) {
        label = `${titre_display} ${label}`;
      }
      if (prenoms) {
        label = `${label} (${prenoms})`;
      }
      if (pseudonyme) {
        label = `${label} ${getPseudonymeSuffix(person, t)}`;
      }
      break;
  }
  return label;
}

// Mirrors Django's `Individu.nom_complet()` — i.e. `html(lon=True,
// designation='S')`: the long, standard form used as the detail page heading.
// First names come *before* the surname with no parentheses, `prenoms_complets`
// is preferred over `prenoms`, the title prefix only shows when there are no
// first names, and the person's own `designation` is ignored (always standard).
export function getPersonFullName(
  person: TRelatedPerson,
  t: TKnownAsTranslator,
): string {
  const surname = withParticule(person.particule_nom, person.nom);
  const prenoms = person.prenoms_complets || person.prenoms;
  let label = surname;
  if (prenoms) {
    label = `${prenoms} ${surname}`;
  } else if (surname && person.titre_display) {
    label = `${person.titre_display} ${surname}`;
  }
  if (person.pseudonyme) {
    label = `${label} ${getPseudonymeSuffix(person, t)}`;
  }
  return label;
}

// JSX counterpart of `getPersonFullName`, rendering the surname in small caps
// (like Django's `sc`). Used for the individu detail page heading.
export function PersonFullName({
  person,
  ...boxProps
}: { person: TRelatedPerson } & BoxProps) {
  const t = useTranslations("common");
  const surname = withParticule(person.particule_nom, person.nom);
  const prenoms = person.prenoms_complets || person.prenoms;
  const { titre_display, pseudonyme } = person;
  return (
    <Box component="span" {...boxProps}>
      {prenoms
        ? `${prenoms} `
        : surname && titre_display
          ? `${titre_display} `
          : null}
      <SmallCaps>{surname}</SmallCaps>
      {pseudonyme ? (
        <SafeText value={` ${getPseudonymeSuffix(person, t)}`} />
      ) : null}
    </Box>
  );
}

export function PersonLabel({
  person,
  abbreviated = true,
  ...boxProps
}: { person: TRelatedPerson; abbreviated?: boolean } & BoxProps) {
  const t = useTranslations("common");
  const smallCapsLabel = <SmallCaps>{getSmallCapsLabel(person)}</SmallCaps>;
  switch (person.designation) {
    case EPersonDesignation.STANDARD:
    case EPersonDesignation.BIRTH_NAME:
      const { prenoms, titre_display, pseudonyme } = person;
      return (
        <Box {...boxProps}>
          {!prenoms && titre_display ? `${titre_display} ` : null}
          {smallCapsLabel}
          {prenoms ? ` (${abbreviated ? abbreviate(prenoms) : prenoms})` : null}
          <SafeText
            value={pseudonyme ? ` ${getPseudonymeSuffix(person, t)}` : ""}
          />
        </Box>
      );
    default:
      return smallCapsLabel;
  }
}

// "1810–1849" from the plain date columns, falling back to the free-text
// approximations ("vers 1810"), spaced around the dash when one is present.
function getLifeDates({
  naissance_date,
  naissance_date_approx,
  deces_date,
  deces_date_approx,
}: TRelatedPerson): string {
  const birth = naissance_date?.slice(0, 4) || naissance_date_approx || "";
  const death = deces_date?.slice(0, 4) || deces_date_approx || "";
  if (!birth && !death) {
    return "";
  }
  const spaced = !naissance_date || !deces_date;
  return `${birth}${spaced ? " – " : "–"}${death}`;
}

/**
 * The person's detail shown on chip hover — full unabbreviated name (in the
 * long, standard order of {@link PersonFullName}), birth name, pseudonyme and
 * life dates — with surnames in small caps, like the rest of the site.
 */
function PersonTooltipBody(person: TRelatedPerson) {
  const t = useTranslations("common");
  const { titre_display, pseudonyme } = person;
  const surname = withParticule(person.particule_nom, person.nom);
  const prenoms = person.prenoms_complets || person.prenoms;
  const birthName =
    person.nom_naissance && person.nom_naissance !== person.nom
      ? withParticule(person.particule_nom_naissance, person.nom_naissance)
      : "";
  const lifeDates = getLifeDates(person);
  return (
    <Box>
      <Typography variant="body2" sx={{ fontWeight: "bold" }}>
        {prenoms
          ? `${prenoms} `
          : surname && titre_display
            ? `${titre_display} `
            : null}
        <SmallCaps>{surname}</SmallCaps>
        {birthName ? (
          <>
            {` ${t("bornAs", { titre: person.titre })} `}
            <SmallCaps>{birthName}</SmallCaps>
          </>
        ) : null}
        {pseudonyme ? (
          <SafeText value={` ${getPseudonymeSuffix(person, t)}`} />
        ) : null}
      </Typography>
      {lifeDates ? (
        <Typography
          variant="caption"
          color="inherit"
          sx={{ display: "block" }}
        >
          {lifeDates}
        </Typography>
      ) : null}
    </Box>
  );
}

export default function PersonChip(person: TRelatedPerson) {
  return (
    <Tooltip
      title={<PersonTooltipBody {...person} />}
      placement="top"
      arrow
      disableInteractive
    >
      <OurChip
        component={OurLink}
        href={`${PERSONS_BASE}/id/${person.id}/`}
        label={<PersonLabel person={person} />}
        clickable
        size="small"
        icon={<BoyOutlinedIcon />}
      />
    </Tooltip>
  );
}
