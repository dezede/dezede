import Chip from "@mui/material/Chip";
import { TRelatedPlace } from "../types";

export default function PlaceChip({
  id,
  nom,
  nature: { referent },
  parent,
}: TRelatedPlace) {
  let label = nom;
  if (!referent && parent !== null) {
    label = `${parent.nom}, ${nom}`;
  }
  return (
    <Chip
      component="a"
      href={`/lieux/id/${id}/`}
      label={label}
      clickable
      size="small"
    />
  );
}
