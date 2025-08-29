import { TRelatedPlace } from "../types";

export default function PlaceLabel({
  nom,
  nature: { referent },
  parent,
}: TRelatedPlace) {
  if (referent || parent === null) {
    return nom;
  }
  return `${parent.nom}, ${nom}`;
}
