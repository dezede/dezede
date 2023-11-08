import React from 'react';

import { useApi } from '../hooks';
import { Ensemble } from '../types';


export default function EnsembleLabel({id}: { id: number }) {
  const { data: ensemble } = useApi<Ensemble>("ensembles", id);

  if (!ensemble) {
    return null;
  }
  return (
    <span dangerouslySetInnerHTML={{__html: ensemble.html}} />
  );
}
