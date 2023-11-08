import React, { useMemo } from "react";

import { join } from "../utils";
import AuteurLabelGroup from "./AuteurLabelGroup";
import { useMultipleApi } from "../hooks";
import { type Auteur } from "../types";

export default function AuteurLabelList({ ids }: { ids: number[] }) {
  const { data: auteurs } = useMultipleApi<Auteur>("auteurs", ids);

  const groups = useMemo(() => {
    const groupKeys: Array<{ professionId: number | null }> = [];
    const groupContents = {};
    for (const auteur of auteurs ?? []) {
      const key = { professionId: auteur.profession };
      const serializedKey = JSON.stringify(key);
      if (!(serializedKey in groupContents)) {
        groupKeys.push(key);
        groupContents[serializedKey] = { ensembleIds: [], individuIds: [] };
      }
      if (auteur.ensemble !== null) {
        groupContents[serializedKey].ensembleIds.push(auteur.ensemble);
      }
      if (auteur.individu !== null) {
        groupContents[serializedKey].individuIds.push(auteur.individu);
      }
    }
    return { keys: groupKeys, contents: groupContents };
  }, [auteurs]);

  if (!auteurs) {
    return null;
  }
  return (
    <>
      {join(
        groups.keys.map((key) => {
          const serializedKey = JSON.stringify(key);
          return (
            <AuteurLabelGroup
              key={serializedKey}
              ensembleIds={groups.contents[serializedKey].ensembleIds}
              individuIds={groups.contents[serializedKey].individuIds}
              professionId={key.professionId}
            />
          );
        }),
      )}
    </>
  );
}
