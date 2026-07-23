import React from "react";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

/**
 * A bordered panel for one source-type group: a tinted heading bar (e.g.
 * "3 monographies") above the group's clickable source list. Mirrors the
 * Django frontend's Bootstrap `panel panel-default` (`include/sources.html`) so
 * consecutive source types read as clearly boxed, separated blocks rather than
 * bare lists under a rule. Shared by the related-sources panels
 * ({@link SourcesPanel}) and the dossier de sources groups ({@link DossierData}).
 */
export default function SourceGroupPanel({
  heading,
  children,
}: {
  heading: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <Paper variant="outlined" sx={{ overflow: "hidden" }}>
      <Box
        sx={{
          px: 1.5,
          py: 0.75,
          bgcolor: "action.hover",
          borderBottom: 1,
          borderColor: "divider",
        }}
      >
        <Typography
          variant="subtitle1"
          component="div"
          sx={{ fontWeight: 500, lineHeight: 1.4 }}
        >
          {heading}
        </Typography>
      </Box>
      {/* No padding here: each source row carries its own `px` so the hover
          background spans the panel's full width and height with no gap. */}
      {children}
    </Paper>
  );
}
