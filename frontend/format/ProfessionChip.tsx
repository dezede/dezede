import Chip from "@mui/material/Chip";
import WorkOutlineIcon from "@mui/icons-material/WorkOutline";
import { TRelatedProfession } from "@/app/types";
import { capfirst } from "@/app/utils";
import OurLink from "@/components/OurLink";
import { PROFESSIONS_BASE } from "@/app/constants";

export function getProfessionLabel({ nom }: TRelatedProfession): string {
  return capfirst(nom);
}

export default function ProfessionChip(profession: TRelatedProfession) {
  return (
    <Chip
      component={OurLink}
      href={`${PROFESSIONS_BASE}/id/${profession.id}/`}
      label={getProfessionLabel(profession)}
      clickable
      size="small"
      icon={<WorkOutlineIcon />}
    />
  );
}
