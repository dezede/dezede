import Chip from "@mui/material/Chip";
import PlaceOutlinedIcon from "@mui/icons-material/PlaceOutlined";
import { TRelatedPlace } from "@/app/types";

export function getPlaceLabel(
  place: TRelatedPlace | null,
  fuzzyPlace: string = "",
): string {
  if (fuzzyPlace) {
    return fuzzyPlace;
  }
  if (place === null) {
    return "";
  }
  const {
    nom,
    nature: { referent },
    parent,
  } = place;
  if (referent || parent === null) {
    return nom;
  }
  return `${parent.nom}, ${nom}`;
}

export function PlaceLabel(place: TRelatedPlace | null) {
  return getPlaceLabel(place);
}

export default function PlaceChip(place: TRelatedPlace | null) {
  if (place === null) {
    return null;
  }
  return (
    <Chip
      component="a"
      href={`/lieux-et-institutions/id/${place.id}/`}
      label={<PlaceLabel {...place} />}
      clickable
      size="small"
      icon={<PlaceOutlinedIcon />}
    />
  );
}
