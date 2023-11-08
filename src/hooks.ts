import axios from 'axios';
import useSWR, { preload, SWRConfiguration } from 'swr';

function getBaseApiUrl() {
  return (
    process.env.NODE_ENV === 'production'
      ? ''
      : 'http://localhost:8000'
  );
}

type FetcherArgs = [apiName: string, id: number];

async function fetcher<T>([apiName, id]: FetcherArgs) {
  const url = `${getBaseApiUrl()}/api/${apiName}/${id}/`;
  const response = await axios.get(url);
  return response.data as T;
}

async function multipleFetcher<T>([apiName, ...ids]: [apiName: string, ...ids: number[]]) {
  const promises = ids.map(id => fetcher<T>([apiName, id]));
  return await (Promise.all(promises) as Promise<T[]>);
}

export function useApi<T>(apiName: string, id: number | undefined | null, config?: SWRConfiguration<T>) {
  return useSWR<T>(id ? [apiName, id] : null, fetcher<T>, config);
}

export function useMultipleApi<T>(apiName: string, ids: (number | undefined | null)[], config?: SWRConfiguration<T[]>) {
  return useSWR<T[]>(ids.some(id => !id) ? null : [apiName, ...ids], multipleFetcher<T>, config);
}

export function preloadApi<T>(apiName: string, id: number | undefined | null) {
  if (!id) {
    return preload<T>(null, fetcher<T>);
  }
  return preload<T>([apiName, id], fetcher<T>);
}
