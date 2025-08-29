import Chip from "@mui/material/Chip";
import PlaceOutlinedIcon from "@mui/icons-material/PlaceOutlined";
import { TRelatedPlace } from "../types";
import PlaceLabel from "./PlaceLabel";

export default function PlaceChip(place: TRelatedPlace) {
  return (
    <Chip
      component="a"
      href={`/lieux/id/${place.id}/`}
      label={<PlaceLabel {...place} />}
      clickable
      size="small"
      icon={<PlaceOutlinedIcon />}
    />
  );
}
