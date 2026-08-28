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
import WorkChip from "./WorkChip";
import PersonChip from "./PersonChip";
import EnsembleChip from "./EnsembleChip";
import PlaceChip from "./PlaceChip";
import PartChip from "./PartChip";
import ProfessionChip from "./ProfessionChip";
import SourceChip from "./SourceChip";

/**
 * Renders the appropriate chip for any public catalogue entity, dispatching on
 * its `meta.type`. Lets the generic index list stay model-agnostic.
 */
export default function EntityChip({ entity }: { entity: TEntity }) {
  switch (entity.meta.type) {
    case EModelType.WORK:
      return <WorkChip {...(entity as TRelatedWork)} />;
    case EModelType.PERSON:
      return <PersonChip {...(entity as TRelatedPerson)} />;
    case EModelType.ENSEMBLE:
      return <EnsembleChip {...(entity as TRelatedEnsemble)} />;
    case EModelType.PLACE:
      return <PlaceChip {...(entity as TRelatedPlace)} />;
    case EModelType.PART:
      return <PartChip {...(entity as TRelatedPart)} />;
    case EModelType.PROFESSION:
      return <ProfessionChip {...(entity as TRelatedProfession)} />;
    case EModelType.SOURCE:
      return <SourceChip {...(entity as TSource)} />;
    default:
      return null;
  }
}
