import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { TypographyVariant } from "@mui/material/styles";
import PlaceOutlinedIcon from "@mui/icons-material/PlaceOutlined";
import EventOutlinedIcon from "@mui/icons-material/EventOutlined";
import { TRelatedPlace } from "@/app/types";
import PlaceChip, { PlaceLabel } from "./PlaceChip";
import DateLabel from "./DateLabel";
import { TimeLabel } from "./TimeLabel";

export default function SpaceTime({
  date = null,
  fuzzyDate = "",
  time = null,
  fuzzyTime = "",
  place = null,
  fuzzyPlace = "",
  chip = false,
  variant = "body1",
  hideIcon = false,
}: {
  date?: string | null;
  fuzzyDate?: string;
  time?: string | null;
  fuzzyTime?: string;
  place?: TRelatedPlace | null;
  fuzzyPlace?: string;
  chip?: boolean;
  variant?: TypographyVariant;
  hideIcon?: boolean;
}) {
  const hasPlace = place !== null || fuzzyPlace !== "";
  const hasDate = date !== null || fuzzyDate !== "";
  const hasTime = time !== null || fuzzyTime !== "";
  const hasDateTime = hasDate || hasTime;
  return (
    <Stack
      direction="row"
      spacing={1}
      alignItems="center"
      flexWrap="wrap"
      useFlexGap
      maxWidth="100%"
    >
      {hasPlace ? (
        chip && place !== null ? (
          <PlaceChip {...place} />
        ) : (
          <Stack direction="row" spacing={0.5} alignItems="center">
            <PlaceOutlinedIcon fontSize="small" />
            <Typography variant={variant} fontSize="inherit">
              {place === null ? fuzzyPlace : <PlaceLabel {...place} />}
            </Typography>
          </Stack>
        )
      ) : null}
      {hasDateTime ? (
        <Stack direction="row" spacing={0.5} alignItems="center">
          {hideIcon ? null : <EventOutlinedIcon fontSize="small" />}
          <Typography variant={variant} fontSize="inherit">
            <DateLabel dateString={date} fuzzyDate={fuzzyDate} />
          </Typography>
          <Typography variant={variant} fontSize="inherit">
            <TimeLabel timeString={time} fuzzyTime={fuzzyTime} />
          </Typography>
        </Stack>
      ) : null}
    </Stack>
  );
}
