import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { TSourceGroup } from "@/app/types";
import SourceGroupPanel from "@/components/SourceGroupPanel";
import SourceList from "@/components/SourceList";
import { TDetailRow } from "@/components/DetailTable";
import { countLabel } from "@/components/entityChipRow";

// Top padding (px) that lands the row label's baseline on the first source
// title's baseline. The sources render as a flexbox `List` whose synthesised
// baseline tracks the leading icon (not the title text) and shifts as the first
// title wraps, so a plain baseline-aligned label drifts; top-aligning the row
// and nudging the label down by this fixed amount pins it to the first title's
// first line. Tuned empirically against the rendered page: the label baseline
// sits 21px below the cell top, the first source title's first line 29px, so an
// 8px nudge closes the gap.
const LABEL_OFFSET = 8;

// One `DetailTable` row per source-type group ("3 monographies", "1 manuscrit"),
// so an autorité's linked sources sit alongside its other attributes instead of
// in a separate panel below the table. Mirrors the SourcesPanel grouping. These
// keep navigating to the source page (no `modal`).
export function sourceGroupRows(groups: TSourceGroup[]): TDetailRow[] {
  return groups.map((group, index) => ({
    key: `source-${group.type}-${index}`,
    // Larger, darker than the table's other (textDisabled subtitle2) labels so
    // the source type reads as a heading, matching SourceGroupPanel elsewhere.
    label: (
      <Typography
        component="span"
        sx={{ fontWeight: 500, fontSize: "0.95rem", color: "text.primary" }}
      >
        {countLabel(group.type, group.sources.length)}
      </Typography>
    ),
    content: <SourceList sources={group.sources} />,
    align: "offset",
    labelOffset: LABEL_OFFSET,
  }));
}

// Linked-sources panel: one block per type group (heading + clickable sources),
// grouped server-side. Rendered inside EventCard (every event, list and detail),
// mirroring the Django `include/sources.html` panel. `modal` opens each source
// in the in-place popup rather than navigating (used by event cards).
export default function SourcesPanel({
  groups,
  modal = false,
}: {
  groups: TSourceGroup[];
  modal?: boolean;
}) {
  if (groups.length === 0) {
    return null;
  }
  return (
    <Stack spacing={1.5}>
      {groups.map((group, index) => (
        <SourceGroupPanel key={`${group.type}-${index}`} heading={group.type}>
          <SourceList sources={group.sources} modal={modal} px={1.5} />
        </SourceGroupPanel>
      ))}
    </Stack>
  );
}
