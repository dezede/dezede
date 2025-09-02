import { TRelatedSection } from "@/app/types";
import { getPartLabel } from "./PartChip";

export function getSectionLabel({
  partie,
  quantite_min: min,
  quantite_max: max,
  facultatif,
}: TRelatedSection) {
  let label = getPartLabel(partie, max > 1);
  if (max > min) {
    label = `${min} à ${max} ${label}`;
  } else if (min > 1) {
    label = `${min} ${label}`;
  }
  if (facultatif) {
    return `${label} ad libitum`;
  }
  return label;
}
