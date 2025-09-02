import { TRelatedEnsemble } from "@/app/types";
import { withParticule } from "@/app/utils";
import Chip from "@mui/material/Chip";
import GroupsIcon from "@mui/icons-material/Groups";
import SmallCaps from "./SmallCaps";

export function getEnsembleLabel({
  nom,
  particule_nom,
}: TRelatedEnsemble): string {
  return withParticule(particule_nom, nom);
}

export function EnsembleLabel(ensemble: TRelatedEnsemble) {
  return <SmallCaps>{getEnsembleLabel(ensemble)}</SmallCaps>;
}

export default function EnsembleChip(ensemble: TRelatedEnsemble) {
  return (
    <Chip
      component="a"
      href={`/ensembles/id/${ensemble.id}/`}
      label={<EnsembleLabel {...ensemble} />}
      clickable
      size="small"
      icon={<GroupsIcon />}
    />
  );
}
