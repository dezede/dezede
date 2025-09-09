import { TRelatedPart } from "@/app/types";
import Chip from "@mui/material/Chip";
import PianoIcon from "@mui/icons-material/Piano";
import { getWorkLabel } from "./WorkChip";
import OurLink from "@/components/OurLink";

export function getPartLabel(
  { nom, nom_pluriel, oeuvre }: TRelatedPart,
  plural: boolean = false,
): string {
  const label = plural ? nom_pluriel : nom;
  if (oeuvre !== null) {
    return `${label} (${getWorkLabel(oeuvre)})`;
  }
  return label;
}

export function PartLabel(part: TRelatedPart) {
  return getPartLabel(part);
}

export default function PartChip(part: TRelatedPart) {
  return (
    <Chip
      component={OurLink}
      href={`/roles-et-instruments/id/${part.id}/`}
      label={<PartLabel {...part} />}
      clickable
      size="small"
      icon={<PianoIcon />}
    />
  );
}
