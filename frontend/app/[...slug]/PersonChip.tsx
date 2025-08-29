import Chip from "@mui/material/Chip";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
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
      icon={<PersonOutlinedIcon />}
    />
  );
}
