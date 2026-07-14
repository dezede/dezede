import { TRelatedPart } from "@/app/types";
import PianoIcon from "@mui/icons-material/Piano";
import { buildWorkLabel } from "./WorkChip";
import { LabelNodes, labelToText, TLabelNode } from "./richLabel";
import OurLink from "@/components/OurLink";
import OurChip from "@/components/OurChip";
import { PARTS_BASE } from "@/app/constants";

/**
 * A rôle/instrument label as rich-label nodes: its (plural-aware) name, plus the
 * work it belongs to in parentheses when set (mirroring Django's
 * `Partie.html(oeuvre=True)`; pass `withWork = false` for the
 * `short_html`/`oeuvre=False` form used inside pupitres and distributions).
 * An empty `nom_pluriel` falls back to `nom + "s"` like Django's `calc_pluriel`.
 */
export function buildPartLabel(
  { nom, nom_pluriel, oeuvre }: TRelatedPart,
  plural: boolean = false,
  withWork: boolean = true,
): TLabelNode[] {
  const nodes: TLabelNode[] = [
    { text: plural ? nom_pluriel || `${nom}s` : nom },
  ];
  if (withWork && oeuvre !== null) {
    nodes.push({ text: " (" }, ...buildWorkLabel(oeuvre), { text: ")" });
  }
  return nodes;
}

export function getPartLabel(
  part: TRelatedPart,
  // A `work`-scoped translator, needed to localise any tonalité of the work the
  // rôle/instrument belongs to.
  t: (key: string) => string,
  plural: boolean = false,
  withWork: boolean = true,
): string {
  return labelToText(buildPartLabel(part, plural, withWork), t);
}

export function PartLabel(part: TRelatedPart) {
  return <LabelNodes nodes={buildPartLabel(part)} />;
}

export default function PartChip(part: TRelatedPart) {
  return (
    <OurChip
      component={OurLink}
      href={`${PARTS_BASE}/id/${part.id}/`}
      label={<PartLabel {...part} />}
      clickable
      size="small"
      icon={<PianoIcon />}
    />
  );
}
