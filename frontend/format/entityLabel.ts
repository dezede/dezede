import {
  EModelType,
  TEntity,
  TRelatedEnsemble,
  TRelatedPart,
  TRelatedPerson,
  TRelatedPlace,
  TRelatedProfession,
  TRelatedWork,
  TSource,
} from "@/app/types";
import { getWorkLabel } from "./WorkChip";
import { getPersonLabel, type TKnownAsTranslator } from "./PersonChip";
import { getEnsembleLabel } from "./EnsembleChip";
import { getPlaceLabel } from "./PlaceChip";
import { getPartLabel } from "./PartChip";
import { getProfessionLabel } from "./ProfessionChip";
import { getSourceLabel } from "./SourceChip";

/**
 * A plain-text label for any public catalogue entity, dispatching on its
 * `meta.type`. Reuses the same getters the chips use, for the autocomplete
 * option text and any non-chip rendering.
 */
export function labelForEntity(
  entity: TEntity,
  // A `work`-scoped translator, needed to localise the tonalité of works (and of
  // the works rôles/instruments belong to).
  t: (key: string) => string,
  // A `common`-scoped translator, for the pseudonyme suffix of people.
  tAka: TKnownAsTranslator,
): string {
  switch (entity.meta.type) {
    case EModelType.WORK:
      return getWorkLabel(entity as TRelatedWork, t);
    case EModelType.PERSON:
      return getPersonLabel(entity as TRelatedPerson, tAka);
    case EModelType.ENSEMBLE:
      return getEnsembleLabel(entity as TRelatedEnsemble);
    case EModelType.PLACE:
      return getPlaceLabel(entity as TRelatedPlace);
    case EModelType.PART:
      return getPartLabel(entity as TRelatedPart, t);
    case EModelType.PROFESSION:
      return getProfessionLabel(entity as TRelatedProfession);
    case EModelType.SOURCE:
      return getSourceLabel(entity as TSource);
    default:
      return "";
  }
}
