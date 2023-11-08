import React from "react";

import { useApi } from "../hooks";
import { type Individu } from "../types";

export default function IndividuLabel({ id }: { id: number }) {
  const { data: individu } = useApi<Individu>("individus", id);

  if (!individu) {
    return null;
  }
  return <span dangerouslySetInnerHTML={{ __html: individu.html }} />;
}
