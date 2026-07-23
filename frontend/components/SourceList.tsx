"use client";

import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import { TSource } from "@/app/types";
import OurLink from "@/components/OurLink";
import SourceIcons from "@/format/SourceIcons";
import { useSourceModal } from "@/components/SourceModal";
import { SOURCES_BASE } from "@/app/constants";

// The clickable list of sources for a single type group — shared between the
// stand-alone SourcesPanel (event cards) and the per-group detail-table rows.
// Each row leads with the source's content-type icons (image/audio/video/text/
// link), falling back to a generic document icon. The list-item padding is
// stripped so that first icon sits flush-left with the group's label/heading.
//
// With `modal`, a plain left-click opens the source in the in-place popup
// (`SourceModal`) instead of navigating; the underlying source-page link is
// kept so middle-click / ⌘-click / "open in new tab" and crawlers still work,
// mirroring the legacy `data-toggle="modal"` + `href` fallback.
//
// `px` is the horizontal padding of each row: 0 (default) keeps the leading icon
// flush-left (detail-table rows), while inside a `SourceGroupPanel` it matches
// the heading's padding so each row's hover background spans the panel's full
// width while its icon/text stay aligned with the type heading.
export default function SourceList({
  sources,
  modal = false,
  px = 0,
}: {
  sources: TSource[];
  modal?: boolean;
  px?: number;
}) {
  const openSource = useSourceModal();
  return (
    <List dense disablePadding>
      {sources.map((source) => (
        <ListItemButton
          key={source.id}
          component={OurLink}
          href={`${SOURCES_BASE}/id/${source.id}/`}
          sx={{ px }}
          onClick={
            modal
              ? (event: React.MouseEvent) => {
                  if (
                    event.metaKey ||
                    event.ctrlKey ||
                    event.shiftKey ||
                    event.altKey ||
                    event.button !== 0
                  ) {
                    return;
                  }
                  event.preventDefault();
                  openSource(source.id);
                }
              : undefined
          }
        >
          <ListItemIcon sx={{ minWidth: 0, mr: 1 }}>
            {source.data_types?.length ? (
              <SourceIcons types={source.data_types} />
            ) : (
              <DescriptionOutlinedIcon fontSize="small" />
            )}
          </ListItemIcon>
          <ListItemText primary={source.title} />
        </ListItemButton>
      ))}
    </List>
  );
}
