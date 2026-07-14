import { TRelatedEnsemble } from "@/app/types";
import { withParticule } from "@/app/utils";
import GroupsIcon from "@mui/icons-material/Groups";
import SmallCaps from "./SmallCaps";
import OurLink from "@/components/OurLink";
import OurChip from "@/components/OurChip";
import { ENSEMBLES_BASE } from "@/app/constants";

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
    <OurChip
      component={OurLink}
      href={`${ENSEMBLES_BASE}/id/${ensemble.id}/`}
      label={<EnsembleLabel {...ensemble} />}
      clickable
      size="small"
      icon={<GroupsIcon />}
    />
  );
}
