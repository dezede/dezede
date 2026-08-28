import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import { TSource } from "@/app/types";
import OurLink from "@/components/OurLink";
import OurChip from "@/components/OurChip";
import { SOURCES_BASE } from "@/app/constants";

export function getSourceLabel(source: TSource): string {
  return source.title;
}

export default function SourceChip(source: TSource) {
  return (
    <OurChip
      component={OurLink}
      href={`${SOURCES_BASE}/id/${source.id}/`}
      label={getSourceLabel(source)}
      clickable
      size="small"
      icon={<DescriptionOutlinedIcon />}
    />
  );
}
