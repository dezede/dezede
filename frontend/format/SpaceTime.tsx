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
  wrap = false,
  inline = false,
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
  wrap?: boolean;
  inline?: boolean;
}) {
  const hasPlace = place !== null || fuzzyPlace !== "";
  const hasDate = date !== null || fuzzyDate !== "";
  const hasTime = time !== null || fuzzyTime !== "";
  const hasDateTime = hasDate || hasTime;
  const placeNode = hasPlace ? (
    chip && place !== null ? (
      <PlaceChip {...place} />
    ) : (
      <Stack direction="row" spacing={0.5} sx={{ alignItems: "center" }}>
        <PlaceOutlinedIcon fontSize="small" />
        <Typography variant={variant} sx={{ fontSize: "inherit" }}>
          {/* Like Django's `lieu_str` (and the date/time labels), the
              approximation wins over the exact place when both are set. */}
          {fuzzyPlace || (place === null ? null : <PlaceLabel {...place} />)}
        </Typography>
      </Stack>
    )
  ) : null;
  const dateTimeNode = hasDateTime ? (
    <Stack
      direction="row"
      spacing={0.5}
      sx={{ alignItems: "center", flexWrap: "nowrap" }}
    >
      {hideIcon ? null : <EventOutlinedIcon fontSize="small" />}
      {hasDate ? (
        <Typography
          variant={variant}
          noWrap
          suppressHydrationWarning
          sx={{ fontSize: "inherit" }}
        >
          <DateLabel dateString={date} fuzzyDate={fuzzyDate} />
        </Typography>
      ) : null}
      {hasTime ? (
        <Typography
          variant={variant}
          noWrap
          suppressHydrationWarning
          sx={{ fontSize: "inherit" }}
        >
          <TimeLabel timeString={time} fuzzyTime={fuzzyTime} />
        </Typography>
      ) : null}
    </Stack>
  ) : null;
  return (
    <Stack
      direction="row"
      spacing={1}
      useFlexGap
      sx={{
        alignItems: "center",
        flexWrap: wrap ? "wrap" : "nowrap",
        maxWidth: "100%",
        display: inline ? "inline-flex" : undefined,
      }}
    >
      {placeNode}
      {dateTimeNode}
    </Stack>
  );
}
