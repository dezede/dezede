import type { ElementType } from "react";
import Chip, { type ChipProps } from "@mui/material/Chip";
import Stack from "@mui/material/Stack";

// FIXME: this is a workaround, not a stylistic choice. Passing an MUI icon
// element to Chip's own `icon` prop triggers a React hydration warning on
// this project's setup (server-rendered markup for the icon's <svg> mismatches
// what the client renders inside Chip's internal icon slot). Instead of using
// `icon`, we fold the icon into `label` ourselves, wrapped with it in a
// horizontal Stack, and never forward `icon` to the underlying Chip. If the
// underlying MUI/hydration issue ever gets fixed upstream, this component
// (and its callers, which all pass `icon` here instead of to Chip) can be
// dropped in favour of plain `<Chip icon={...} />`.
export default function OurChip<C extends ElementType = "div">({
  icon,
  label,
  size,
  ...props
}: ChipProps<C, { component?: C }>) {
  return (
    <Chip
      size={size}
      label={
        icon ? (
          <Stack
            direction="row"
            spacing={0.5}
            sx={{
              alignItems: "center",
              // Mirrors MUI's own `.MuiChip-icon` sizing, since the icon no
              // longer goes through that slot.
              "& svg": { fontSize: size === "medium" ? 24 : 18 },
            }}
          >
            {icon}
            <span>{label}</span>
          </Stack>
        ) : (
          label
        )
      }
      {...props}
    />
  );
}
