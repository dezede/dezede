import React from "react";
import Tooltip from "@mui/material/Tooltip";
import Chip from "@mui/material/Chip";
import BoyOutlinedIcon from "@mui/icons-material/BoyOutlined";
import { abbreviate, withParticule } from "@/app/utils";
import { EPersonDesignation, EPersonTitre, TRelatedPerson } from "@/app/types";
import SmallCaps from "./SmallCaps";

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

function getPseudonymeSuffix({ titre, pseudonyme }: TRelatedPerson) {
  return `${titre === EPersonTitre.MAN ? "dit" : "dite"}\u00A0${pseudonyme}`;
}

export function getPersonLabel(person: TRelatedPerson): string {
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
        label = `${label} ${getPseudonymeSuffix(person)}`;
      }
    default:
      return label;
  }
}

export function PersonLabel(person: TRelatedPerson) {
  const smallCapsLabel = <SmallCaps>{getSmallCapsLabel(person)}</SmallCaps>;
  switch (person.designation) {
    case EPersonDesignation.STANDARD:
    case EPersonDesignation.BIRTH_NAME:
      const { prenoms, titre_display, pseudonyme } = person;
      return (
        <span>
          {prenoms ? null : `${titre_display} `}
          {smallCapsLabel}
          {prenoms ? (
            <>
              {" ("}
              <Tooltip title={prenoms} placement="top" arrow disableInteractive>
                <span>{abbreviate(prenoms)}</span>
              </Tooltip>
              {")"}
            </>
          ) : null}
          {pseudonyme ? ` ${getPseudonymeSuffix(person)}` : null}
        </span>
      );
    default:
      return smallCapsLabel;
  }
}

export default function PersonChip(person: TRelatedPerson) {
  return (
    <Chip
      component="a"
      href={`/individus/id/${person.id}/`}
      label={<PersonLabel {...person} />}
      clickable
      size="small"
      icon={<BoyOutlinedIcon />}
    />
  );
}
