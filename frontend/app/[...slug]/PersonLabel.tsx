import { EPersonDesignation, EPersonTitre, TRelatedPerson } from "../types";
import React from "react";
import Tooltip from "@mui/material/Tooltip";
import SmallCaps from "./SmallCaps";
import { abbreviate } from "../utils";

function withParticule(particule: string, nom: string): string {
  if (!particule) {
    return nom;
  }
  if (particule.endsWith("’") || particule.endsWith("'")) {
    return `${particule}${nom}`;
  }
  return `${particule} ${nom}`;
}

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

export function getPersonLabelString(person: TRelatedPerson): string {
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

export default function PersonLabel(person: TRelatedPerson) {
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
