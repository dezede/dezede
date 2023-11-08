import { useApi } from './hooks';
import { Model } from './types';
import Chip from '@material-ui/core/Chip';
import React from 'react';

export default function ModelChip<T extends Model>({apiName, id}: {apiName: string; id: number}) {
  const { data: instance } = useApi<T>(apiName, id, { suspense: true });
  if (!instance) {
    return null;
  }
  return (
    <Chip label={instance.str} clickable component="a" href={instance.front_url} />
  );
}
