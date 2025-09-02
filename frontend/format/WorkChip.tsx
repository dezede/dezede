import { EPartType, TRelatedWork } from "@/app/types";
import Chip from "@mui/material/Chip";
import HistoryEduOutlinedIcon from "@mui/icons-material/HistoryEduOutlined";
import { capfirst, joinWithLast } from "@/app/utils";
import { getSectionLabel } from "./SectionLabel";

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
}: TRelatedWork): Generator<string> {
  if (numero) {
    yield `n° ${numero}`;
  }
  if (coupe) {
    yield `en ${coupe}`;
  }
  if (incipit) {
    yield `« ${incipit} »`;
  }
  if (tempo && genre) {
    yield tempo;
  }
  if (tonalite) {
    yield `en ${tonalite}`;
  }
  if (sujet) {
    yield `sur ${sujet}`;
  }
  if (arrangement) {
    yield `(${arrangement})`;
  }
  if (surnom) {
    yield `(${surnom})`;
  }
  if (nom_courant) {
    yield nom_courant;
  }
  if (opus) {
    yield `op. ${opus}`;
  }
  if (ict) {
    yield ict;
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

function getSections({ pupitres }: TRelatedWork): string {
  if (pupitres.length === 0) {
    return "";
  }
  const soloSections = pupitres.filter(({ soliste }) => soliste);
  const instrumentSections = joinWithLast(
    soloSections
      .filter(({ partie: { part_type } }) => part_type === EPartType.INSTRUMENT)
      .map(getSectionLabel),
  );
  const roleSections = joinWithLast(
    soloSections
      .filter(({ partie: { part_type } }) => part_type === EPartType.ROLE)
      .map(getSectionLabel),
  );
  if (roleSections) {
    let output = "";
    output += `de ${roleSections}`;
    if (instrumentSections) {
      output += ` avec ${instrumentSections}`;
    }
    return output;
  }
  return `pour ${instrumentSections}`;
}

function getNonSignificantTitle(work: TRelatedWork): string {
  const { genre, tempo } = work;
  const parts = [];
  if (genre === null) {
    parts.push(tempo);
  } else {
    parts.push(genre.nom);
  }
  parts.push(getSections(work));
  parts.push(getFeaturesList(work).next().value);
  return parts.join(" ");
}

export function getWorkLabel(work: TRelatedWork): string {
  // TODO: Add authors.
  // TODO: Handle ancestors recursively.
  const significantTitle = getSignificantTitle(work);
  if (significantTitle) {
    return capfirst(significantTitle);
  }
  return capfirst(getNonSignificantTitle(work));
}

export function WorkLabel(work: TRelatedWork) {
  return getWorkLabel(work);
}

export default function WorkChip(work: TRelatedWork) {
  return (
    <Chip
      component="a"
      href={`/oeuvres/id/${work.id}/`}
      label={<WorkLabel {...work} />}
      clickable
      size="small"
      icon={<HistoryEduOutlinedIcon />}
    />
  );
}
