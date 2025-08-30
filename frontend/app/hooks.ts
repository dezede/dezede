import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { TSearchParamsUpdate } from "./types";

export function useDebounceCallback<T>(
  callback: (...args: T[]) => void,
  debounceTimeout: number,
) {
  const [timeoutId, setTimeoutId] = useState<ReturnType<typeof setTimeout>>();

  // Cancels timeouts on unmount.
  useEffect(() => {
    return () => clearTimeout(timeoutId);
  }, [timeoutId]);

  return useCallback(
    (...args: T[]) => {
      clearTimeout(timeoutId);
      setTimeoutId(setTimeout(() => callback(...args), debounceTimeout));
    },
    [callback, debounceTimeout, timeoutId],
  );
}

export function useUpdateSearchParams() {
  const searchParams = useSearchParams();
  const router = useRouter();
  return {
    updateSearchParams: useCallback(
      (paramsUpdate: TSearchParamsUpdate) => {
        const updatedSearchParams = new URLSearchParams(searchParams);
        Object.entries(paramsUpdate).forEach(([param, value]) => {
          if (typeof value === "number") {
            value = value.toString();
          }
          if (value === null || value === undefined || value === "") {
            updatedSearchParams.delete(param);
          } else {
            updatedSearchParams.set(param, value);
          }
        });
        router.replace(`?${updatedSearchParams.toString()}`);
      },
      [router, searchParams],
    ),
    searchParams,
  };
}
