import React from "react";
import Typography from "@mui/material/Typography";

// Small uppercase section heading shared by EventCard (Distribution, Programme)
// and SourcesPanel (per-group). Rendered as a div, not a heading, so it doesn't
// disturb the card's h1/h2 outline, whose level varies between list and detail.
export default function SectionLabel({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <Typography
      variant="overline"
      component="div"
      color="text.secondary"
      sx={{ display: "block", lineHeight: 1.5, fontWeight: 600 }}
    >
      {children}
    </Typography>
  );
}
