import { TRelatedPerson } from "../types";
import PersonLabel from "./PersonLabel";
import Chip from "@mui/material/Chip";

export default function PersonLink(person: TRelatedPerson) {
  return (
    <Chip
      component="a"
      href={`/individus/id/${person.id}/`}
      label={<PersonLabel {...person} />}
      clickable
      size="small"
    />
  );
}
