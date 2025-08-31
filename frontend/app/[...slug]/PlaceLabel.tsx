import { TRelatedPlace } from "../types";

export function getPlaceLabel({
  nom,
  nature: { referent },
  parent,
}: TRelatedPlace): string {
  if (referent || parent === null) {
    return nom;
  }
  return `${parent.nom}, ${nom}`;
}

export default function PlaceLabel(place: TRelatedPlace) {
  return getPlaceLabel(place);
}
