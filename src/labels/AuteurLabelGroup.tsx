import React from 'react';

import {joinWithLast} from "../utils";
import IndividuLabel from "./IndividuLabel";
import ProfessionLabel from "./ProfessionLabel";
import EnsembleLabel from "./EnsembleLabel";


export default function AuteurLabelGroup({ individuIds, ensembleIds, professionId = null }: {individuIds: number[]; ensembleIds: number[]; professionId: number | null}) {
  return (
    <>
      {joinWithLast(ensembleIds.map(id => (
        <EnsembleLabel key={id} id={id} />
      )))}
      {joinWithLast(individuIds.map(id => (
        <IndividuLabel key={id} id={id} />
      )))}
      {
        professionId !== null
          ? (
            <>
              {' ['}
              <ProfessionLabel
                id={professionId}
                feminin={false}
                pluriel={individuIds.length > 1}
              />
              ]
            </>
          )
          : null
      }
    </>
  );
}
