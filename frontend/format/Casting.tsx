"use client";

import React from "react";
import { useTranslations } from "next-intl";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import WorkOutlineIcon from "@mui/icons-material/WorkOutline";
import PianoIcon from "@mui/icons-material/Piano";
import {
  EPersonTitre,
  TRelatedEnsemble,
  TRelatedPart,
  TRelatedPerson,
  TRelatedProfession,
} from "@/app/types";
import { biGroup, joinWithLast } from "@/app/utils";
import OurLink from "@/components/OurLink";
import { PARTS_BASE, PROFESSIONS_BASE } from "@/app/constants";
import PersonChip, { PersonLabel } from "./PersonChip";
import EnsembleChip, { getEnsembleLabel } from "./EnsembleChip";
import { getPartLabel } from "./PartChip";

// Distribution elements and authors share the same shape for grouping purposes.
export type TCastingElement = {
  individu: TRelatedPerson | null;
  ensemble: TRelatedEnsemble | null;
  partie: TRelatedPart | null;
  profession: TRelatedProfession | null;
};

type TValue =
  | { kind: "individu"; id: string; individu: TRelatedPerson }
  | { kind: "ensemble"; id: string; ensemble: TRelatedEnsemble };

type TKey =
  | { kind: "partie"; id: string; partie: TRelatedPart }
  | { kind: "profession"; id: string; profession: TRelatedProfession };

function getValue(element: TCastingElement): TValue | null {
  if (element.individu !== null) {
    return {
      kind: "individu",
      id: `i${element.individu.id}`,
      individu: element.individu,
    };
  }
  if (element.ensemble !== null) {
    return {
      kind: "ensemble",
      id: `e${element.ensemble.id}`,
      ensemble: element.ensemble,
    };
  }
  return null;
}

function getKey(element: TCastingElement): TKey | null {
  if (element.partie !== null) {
    return {
      kind: "partie",
      id: `p${element.partie.id}`,
      partie: element.partie,
    };
  }
  if (element.profession !== null) {
    return {
      kind: "profession",
      id: `f${element.profession.id}`,
      profession: element.profession,
    };
  }
  return null;
}

function isFeminine(value: TValue): boolean {
  return (
    value.kind === "individu" &&
    (value.individu.titre === EPersonTitre.WOMAN ||
      value.individu.titre === EPersonTitre.GIRL)
  );
}

// Mirrors Django's `Profession.html`: the feminine form is only used when
// `nom_feminin` is set, and an empty plural falls back to the singular + "s"
// (`calc_pluriel`).
function getProfessionLabel(
  profession: TRelatedProfession,
  plural: boolean,
  feminine: boolean,
): string {
  if (plural) {
    if (feminine && profession.nom_feminin) {
      return profession.nom_feminin_pluriel || `${profession.nom_feminin}s`;
    }
    return profession.nom_pluriel || `${profession.nom}s`;
  }
  if (feminine && profession.nom_feminin) {
    return profession.nom_feminin;
  }
  return profession.nom;
}

function getKeyLabel(
  key: TKey,
  values: TValue[],
  t: (key: string) => string,
): string {
  const plural = values.length > 1;
  if (key.kind === "partie") {
    // `oeuvre=False` like Django's `ElementDeDistribution.get_verbose_key`.
    return getPartLabel(key.partie, t, plural, false);
  }
  const feminine = values.every(isFeminine);
  return getProfessionLabel(key.profession, plural, feminine);
}

/**
 * Chip-less counterpart of {@link Casting}, mirroring Django's `BiGrouper`
 * string output: people/ensembles sharing the same role(s) are grouped and the
 * role appended in brackets — "Performer1, Performer2 [Role]" — with groups
 * joined by ", ". Renders surnames in small caps and unabbreviated first
 * names. Used where chips don't fit, e.g. inside a tooltip.
 */
export function CastingText({ elements }: { elements: TCastingElement[] }) {
  // For localising the tonalité of any work a rôle/instrument belongs to.
  const tWork = useTranslations("work");
  const groups = biGroup(
    elements,
    getValue,
    getKey,
    (value) => value.id,
    (key) => key.id,
  );
  return (
    <>
      {groups.map((group, index) => {
        const keys = joinWithLast(
          group.keys
            .filter((key): key is TKey => key !== null)
            .map((key) => getKeyLabel(key, group.values, tWork)),
        );
        return (
          <React.Fragment key={index}>
            {index > 0 ? ", " : null}
            {group.values.map((value, valueIndex) => (
              <React.Fragment key={value.id}>
                {valueIndex > 0
                  ? valueIndex === group.values.length - 1
                    ? " et "
                    : ", "
                  : null}
                {value.kind === "individu" ? (
                  <PersonLabel
                    person={value.individu}
                    abbreviated={false}
                    component="span"
                  />
                ) : (
                  getEnsembleLabel(value.ensemble)
                )}
              </React.Fragment>
            ))}
            {keys ? ` [${keys}]` : null}
          </React.Fragment>
        );
      })}
    </>
  );
}

function ValueChip({ value }: { value: TValue }) {
  if (value.kind === "individu") {
    return <PersonChip {...value.individu} />;
  }
  return <EnsembleChip {...value.ensemble} />;
}

function KeyChip({ keyItem, label }: { keyItem: TKey; label: string }) {
  if (keyItem.kind === "partie") {
    return (
      <Chip
        component={OurLink}
        href={`${PARTS_BASE}/id/${keyItem.partie.id}/`}
        label={label}
        clickable
        size="small"
        icon={<PianoIcon />}
      />
    );
  }
  return (
    <Chip
      component={OurLink}
      href={`${PROFESSIONS_BASE}/id/${keyItem.profession.id}/`}
      label={label}
      clickable
      size="small"
      icon={<WorkOutlineIcon />}
    />
  );
}

/**
 * Fuses its child chips into a single segmented unit, like a button group:
 * the rounded, overflow-clipped container squares off the chips' inner corners
 * so they share one outline, with a thin separator between segments.
 */
function ChipGroup({ children }: { children: React.ReactNode }) {
  return (
    <Box
      sx={{
        display: "inline-flex",
        borderRadius: "12px",
        overflow: "hidden",
        "& .MuiChip-root": { borderRadius: 0 },
        "& .MuiChip-root:not(:first-of-type)": {
          borderLeft: "1px solid",
          borderLeftColor: "background.paper",
        },
      }}
    >
      {children}
    </Box>
  );
}

/**
 * Renders a cast (distribution) or a work's authors, grouped exactly like
 * Django's `BiGrouper`: people/ensembles sharing the same role(s) are fused
 * with that role into a single segmented "chip group".
 */
export default function Casting({ elements }: { elements: TCastingElement[] }) {
  // For localising the tonalité of any work a rôle/instrument belongs to.
  const tWork = useTranslations("work");
  const groups = biGroup(
    elements,
    getValue,
    getKey,
    (value) => value.id,
    (key) => key.id,
  );
  if (groups.length === 0) {
    return null;
  }
  return (
    <>
      {groups.map((group, index) => (
        <ChipGroup key={index}>
          {group.values.map((value) => (
            <ValueChip key={value.id} value={value} />
          ))}
          {group.keys
            .filter((key): key is TKey => key !== null)
            .map((key) => (
              <KeyChip
                key={key.id}
                keyItem={key}
                label={getKeyLabel(key, group.values, tWork)}
              />
            ))}
        </ChipGroup>
      ))}
    </>
  );
}
