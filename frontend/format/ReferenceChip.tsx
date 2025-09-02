import {
  EModelType,
  TReference,
  TRelatedEnsemble,
  TRelatedEvent,
  TRelatedPart,
  TRelatedPerson,
  TRelatedPlace,
  TRelatedWork,
} from "@/app/types";
import PersonChip from "./PersonChip";
import PlaceChip from "./PlaceChip";
import PartChip from "./PartChip";
import EnsembleChip from "./EnsembleChip";
import EventChip from "./EventChip";
import WorkChip from "./WorkChip";

export default function RelatedChip({ reference }: { reference: TReference }) {
  switch (reference.meta.type) {
    case EModelType.PERSON:
      return <PersonChip {...(reference as TRelatedPerson)} />;
    case EModelType.PLACE:
      return <PlaceChip {...(reference as TRelatedPlace)} />;
    case EModelType.PART:
      return <PartChip {...(reference as TRelatedPart)} />;
    case EModelType.ENSEMBLE:
      return <EnsembleChip {...(reference as TRelatedEnsemble)} />;
    case EModelType.EVENT:
      return <EventChip {...(reference as TRelatedEvent)} />;
    case EModelType.WORK:
      return <WorkChip {...(reference as TRelatedWork)} />;
  }
}
