import { TRelatedPerson } from "../types";
import Person from "./Person";
import Chip from "@mui/material/Chip";

export default function PersonLink(person: TRelatedPerson) {
  return (
    <Chip
      component="a"
      href={`/individus/id/${person.id}/`}
      label={<Person {...person} />}
      clickable
      size="small"
    />
  );
}
