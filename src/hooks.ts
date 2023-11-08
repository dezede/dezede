import axios from "axios";
import { preload, type SWRConfiguration } from "swr";
import useSWRImmutable from 'swr/immutable';

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

async function multipleFetcher<T>([apiName, ...ids]: [
  apiName: string,
  ...ids: number[],
]) {
  const promises = ids.map(async (id) => await fetcher<T>([apiName, id]));
  return await (Promise.all(promises) as Promise<T[]>);
}

export function useApi<T>(
  apiName: string,
  id: number | undefined | null,
  config?: SWRConfiguration<T>,
) {
  return useSWRImmutable<T>(id ? [apiName, id] : null, fetcher<T>, config);
}

export function useMultipleApi<T>(
  apiName: string,
  ids: Array<number | undefined | null>,
  config?: SWRConfiguration<T[]>,
) {
  return useSWRImmutable<T[]>(
    ids.some((id) => !id) ? null : [apiName, ...ids],
    multipleFetcher<T>,
    config,
  );
}

export async function preloadApi<T>(
  apiName: string,
  id: number | undefined | null,
) {
  if (!id) {
    return await preload<T>(null, fetcher<T>);
  }
  return await preload<T>([apiName, id], fetcher<T>);
}
