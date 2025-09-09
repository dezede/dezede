import { TRelatedEvent } from "@/app/types";
import Chip from "@mui/material/Chip";
import EventOutlinedIcon from "@mui/icons-material/EventOutlined";
import { getDateLabel } from "./DateLabel";
import { getPlaceLabel } from "./PlaceChip";
import { getTimeLabel } from "./TimeLabel";
import OurLink from "@/components/OurLink";

export function getEventLabel(event: TRelatedEvent): string {
  const left = [
    getDateLabel(event.debut_date, event.debut_date_approx),
    getTimeLabel(event.debut_heure, event.debut_heure_approx),
  ]
    .filter((value) => value !== "")
    .join(" ");
  const right = [
    getPlaceLabel(event.debut_lieu, event.debut_lieu_approx),
    event.circonstance,
    event.relache ? "Relâche" : "",
  ]
    .filter((value) => value !== "")
    .join(", ");
  if (left && right) {
    return `${left} • ${right}`;
  }
  return left || right;
}

export function EventLabel(event: TRelatedEvent) {
  return getEventLabel(event);
}

export default function EventChip(event: TRelatedEvent) {
  return (
    <Chip
      component={OurLink}
      href={`/evenements/id/${event.id}/`}
      label={<EventLabel {...event} />}
      clickable
      size="small"
      icon={<EventOutlinedIcon />}
    />
  );
}
