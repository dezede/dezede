"use client";

import { ReactNode } from "react";
import { useTranslations } from "next-intl";
import Box from "@mui/material/Box";
import Tooltip from "@mui/material/Tooltip";
import VideocamOutlinedIcon from "@mui/icons-material/VideocamOutlined";
import VolumeUpOutlinedIcon from "@mui/icons-material/VolumeUpOutlined";
import ImageOutlinedIcon from "@mui/icons-material/ImageOutlined";
import AttachFileOutlinedIcon from "@mui/icons-material/AttachFileOutlined";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import LaunchOutlinedIcon from "@mui/icons-material/LaunchOutlined";

// One icon per source content type (image/audio/video/text/link/other),
// mirroring the Django ``Source.ICONS``. Shared between the sources index grid
// and the related-sources lists.
const SOURCE_TYPE_ICONS: Record<string, ReactNode> = {
  video: <VideocamOutlinedIcon fontSize="small" />,
  audio: <VolumeUpOutlinedIcon fontSize="small" />,
  image: <ImageOutlinedIcon fontSize="small" />,
  other: <AttachFileOutlinedIcon fontSize="small" />,
  text: <DescriptionOutlinedIcon fontSize="small" />,
  link: <LaunchOutlinedIcon fontSize="small" />,
};

// Renders a source's content types as a row of tooltipped icons. Returns null
// when the source carries no known type, so callers can fall back to a generic
// icon.
export default function SourceIcons({
  types,
  color = "text.secondary",
}: {
  types?: string[];
  color?: string;
}) {
  const t = useTranslations("authority");
  if (!types?.length) {
    return null;
  }
  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, color }}>
      {types.map((type) => {
        const node = SOURCE_TYPE_ICONS[type];
        return node ? (
          <Tooltip key={type} title={t(`sourceTypes.${type}`)}>
            <Box sx={{ display: "inline-flex" }}>
              {node}
            </Box>
          </Tooltip>
        ) : null;
      })}
    </Box>
  );
}
