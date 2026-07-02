import { TParenteGroup } from "@/app/types";
import EntityChipList from "./EntityChipList";
import { TDetailRow } from "./DetailTable";
import { countLabel } from "./entityChipRow";

/**
 * Turns the server-grouped parenté lists into `DetailTable` rows — one row per
 * parenté type, headed by the singular/plural label (and, for the relative
 * direction, the `*_relatif` labels), mirroring the Django `{% regroup … %}`
 * blocks on the œuvre and individu pages.
 *
 * `relative` selects the heading: false for the object's parents (mères /
 * parents), true for its children (filles / enfants).
 */
export function parenteRows(
  groups: TParenteGroup[],
  relative: boolean,
  keyPrefix: string,
): TDetailRow[] {
  return groups.map((group, index) => {
    const { type, entities } = group;
    const plural = entities.length > 1;
    const label = relative
      ? plural
        ? type.relatif_pluriel
        : type.nom_relatif
      : plural
        ? type.pluriel
        : type.nom;
    return {
      key: `${keyPrefix}-${index}`,
      label: countLabel(label, entities.length),
      content: entities.length ? <EntityChipList entities={entities} /> : null,
    };
  });
}
