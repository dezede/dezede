import Chip from "@mui/material/Chip";
import BoyOutlinedIcon from "@mui/icons-material/BoyOutlined";
import { TRelatedPerson } from "../types";
import PersonLabel from "./PersonLabel";

export default function PersonLink(person: TRelatedPerson) {
  return (
    <Chip
      component="a"
      href={`/individus/id/${person.id}/`}
      label={<PersonLabel {...person} />}
      clickable
      size="small"
      icon={<BoyOutlinedIcon />}
    />
  );
}
