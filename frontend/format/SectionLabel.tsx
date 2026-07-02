import { TRelatedSection } from "@/app/types";
import { apnumber } from "@/app/utils";
import { buildPartLabel } from "./PartChip";
import { TLabelNode } from "./richLabel";

/**
 * A pupitre's label as rich-label nodes, mirroring Django's `Pupitre.__str__`:
 * the quantity (spelled out via `apnumber`), the part name, and an italicized
 * "ad libitum" (`<em>`) when the part is facultatif.
 */
export function buildSectionLabel({
  partie,
  quantite_min: min,
  quantite_max: max,
  facultatif,
}: TRelatedSection): TLabelNode[] {
  const nodes: TLabelNode[] = [];
  if (max > min) {
    nodes.push({ text: `${apnumber(min)} à ${apnumber(max)} ` });
  } else if (min > 1) {
    nodes.push({ text: `${apnumber(min)} ` });
  }
  // `oeuvre=False` like Django's `Pupitre.__str__`: no work suffix here.
  nodes.push(...buildPartLabel(partie, max > 1, false));
  if (facultatif) {
    nodes.push({ text: " " }, { text: "ad libitum", em: true });
  }
  return nodes;
}
