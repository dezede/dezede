import Stack from "@mui/material/Stack";
import { TRelatedPlace } from "../types";
import Typography from "@mui/material/Typography";
import PlaceChip from "./PlaceChip";
import Divider from "@mui/material/Divider";
import { DateLabel } from "./DateLabel";
import { TimeLabel } from "./TimeLabel";

export default function SpaceTime({
  date = null,
  fuzzyDate = "",
  time = null,
  fuzzyTime = "",
  place = null,
  fuzzyPlace = "",
}: {
  date?: string | null;
  fuzzyDate?: string;
  time?: string | null;
  fuzzyTime?: string;
  place?: TRelatedPlace | null;
  fuzzyPlace?: string;
}) {
  const hasDate = date !== null || fuzzyDate !== "";
  const hasTime = time !== null || fuzzyTime !== "";
  const hasDateTime = hasDate || hasTime;
  const hasPlace = place !== null || fuzzyPlace !== "";
  return (
    <Stack direction="row" spacing={1} alignItems="center">
      {fuzzyPlace ? (
        <span>
          <Typography component="span">{fuzzyPlace}</Typography>
        </span>
      ) : place === null ? null : (
        <PlaceChip {...place} />
      )}
      {hasDateTime && hasPlace ? (
        <Divider orientation="vertical" variant="middle" />
      ) : null}
      <Typography>
        <DateLabel dateString={date} fuzzyDate={fuzzyDate} />
      </Typography>
      {hasDate && hasTime ? <Divider orientation="vertical" /> : null}
      <Typography>
        <TimeLabel timeString={time} fuzzyTime={fuzzyTime} />
      </Typography>
    </Stack>
  );
}
