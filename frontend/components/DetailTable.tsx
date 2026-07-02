import React from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";

// One labelled row of the detail "data-table". `content` is already-rendered
// (rich text, a chip list, a tree…); a row whose content is null/false/"" is
// dropped, mirroring how the Django templates only emit non-empty rows.
export type TDetailRow = {
  key: string;
  label: React.ReactNode;
  content: React.ReactNode;
  // md+ vertical alignment of the row's two cells. Defaults to "baseline" so a
  // label lines up with its first line of text — correct whenever the content's
  // first line is a real inline line box (plain text, a wrapping row of inline
  // chips). "offset" top-aligns the row instead and nudges the label down by
  // `labelOffset` px: used when the content's first text line is NOT the cell's
  // natural baseline — a virtualised chip grid (absolutely-positioned items) or
  // a flexbox list (whose synthesised baseline tracks the icon, not the title) —
  // so the label baseline is pinned to the first content line regardless of how
  // tall that first row grows.
  align?: "baseline" | "top" | "offset";
  // For "offset" rows only: top padding (px) on the label so its baseline lands
  // on the first content line's baseline. Tuned per content type to the measured
  // gap between the cell top and that first baseline.
  labelOffset?: number;
};

function isEmpty(content: React.ReactNode): boolean {
  return content == null || content === false || content === "";
}

/**
 * The Next.js equivalent of the Django `<table class="data-table">`: a list of
 * "label → value" rows where the value can be any block content (rich text,
 * chip lists, trees). Responsive like `Metadata` — a fixed-label table on
 * md+ screens, a stacked list on small ones.
 */
export default function DetailTable({
  rows,
  headerWidth = 200,
}: {
  rows: TDetailRow[];
  headerWidth?: number | string;
}) {
  const filteredRows = rows.filter((row) => !isEmpty(row.content));
  if (filteredRows.length === 0) {
    return null;
  }
  return (
    // Let long chip labels and unbroken strings wrap instead of overflowing —
    // applied to both the small-screen stacked list and the md+ table so neither
    // layout produces a horizontal scrollbar. `overflowWrap` is inherited, so it
    // reaches every text node below.
    <Box
      sx={{
        overflowWrap: "anywhere",
        // `height: auto` lets a long label wrap to several lines instead of
        // overflowing, but it also lets a single-line chip collapse below the
        // default small-chip height — making these chips visibly shorter than the
        // ones in `RelatedEntitiesPanel` (which pins them to 24px). `minHeight`
        // restores that floor so single-line chips match while wrapped ones still
        // grow.
        "& .MuiChip-root": { maxWidth: "100%", height: "auto", minHeight: 24 },
        "& .MuiChip-label": { whiteSpace: "normal" },
      }}
    >
      <Stack spacing={1.5} display={{ md: "none" }}>
        {filteredRows.map((row) => (
          <div key={`${row.key}-sm`}>
            <Typography variant="subtitle2" color="textDisabled">
              {row.label}
            </Typography>
            <div>{row.content}</div>
          </div>
        ))}
      </Stack>
      {/* No `TableContainer` (its only role is `overflow-x:auto` for wide
          tables): with `tableLayout:fixed` and wrapping content the table never
          overflows horizontally, so the wrapper would only ever add an unwanted
          scrollbar. A plain block keeps the responsive md+ visibility. */}
      <Box sx={{ display: { xs: "none", md: "block" } }}>
        <Table size="small" sx={{ tableLayout: "fixed" }}>
          <TableBody>
            {filteredRows.map((row) => {
              const isOffset = row.align === "offset";
              const label = (
                <Typography variant="subtitle2" color="textDisabled">
                  {row.label}
                </Typography>
              );
              return (
                <TableRow
                  key={row.key}
                  sx={{
                    verticalAlign: isOffset ? "top" : (row.align ?? "baseline"),
                  }}
                >
                  <TableCell
                    component="th"
                    scope="row"
                    sx={{ width: headerWidth, paddingLeft: 0, border: "none" }}
                  >
                    {isOffset ? (
                      // Top-aligned: push the label down by `labelOffset` so its
                      // baseline meets the first content line's baseline.
                      <Box sx={{ pt: `${row.labelOffset ?? 0}px` }}>{label}</Box>
                    ) : (
                      label
                    )}
                  </TableCell>
                  <TableCell sx={{ border: "none" }}>{row.content}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Box>
    </Box>
  );
}
