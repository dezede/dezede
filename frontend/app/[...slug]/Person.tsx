import { EPersonDesignation, EPersonTitre, TRelatedPerson } from "../types";
import React from "react";
import Tooltip from "@mui/material/Tooltip";
import SmallCaps from "./SmallCaps";
import { abbreviate } from "../utils";

function withParticule(particule: string, nom: string) {
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
}: TRelatedPerson): React.ReactNode {
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

export default function Person(person: TRelatedPerson) {
  const smallCapsLabel = <SmallCaps>{getSmallCapsLabel(person)}</SmallCaps>;
  switch (person.designation) {
    case EPersonDesignation.STANDARD:
    case EPersonDesignation.BIRTH_NAME:
      const { prenoms, titre, titre_display, pseudonyme } = person;
      return (
        <span>
          {prenoms ? null : `${titre_display} `}
          {smallCapsLabel}
          {prenoms ? (
            <>
              {" ("}
              <Tooltip title={prenoms} placement="top" arrow>
                <span>{abbreviate(prenoms)}</span>
              </Tooltip>
              {")"}
            </>
          ) : null}
          {pseudonyme
            ? ` ${titre === EPersonTitre.MAN ? "dit" : "dite"}\u00A0${pseudonyme}`
            : null}
        </span>
      );
    default:
      return smallCapsLabel;
  }
}
