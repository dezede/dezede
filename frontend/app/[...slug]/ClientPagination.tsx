"use client";

import Pagination from "@mui/material/Pagination";
import { useUpdateSearchParams } from "../hooks";
import { safeParseInt } from "../utils";
import { useEffect, useMemo, useState } from "react";
import { SxProps } from "@mui/material/styles";

export default function ClientPagination({
  totalCount,
  perPage,
  sx,
}: {
  totalCount: number;
  perPage: number;
  sx?: SxProps;
}) {
  const { updateSearchParams, searchParams } = useUpdateSearchParams();
  const pageParam = useMemo(
    () => safeParseInt(searchParams.get("page"), 1),
    [searchParams],
  );
  const [page, setPage] = useState(pageParam);

  useEffect(() => {
    setPage(pageParam);
  }, [pageParam]);

  if (totalCount === 0) {
    return null;
  }
  return (
    <Pagination
      count={Math.ceil(totalCount / perPage)}
      page={page}
      onChange={(event, value) => {
        setPage(value);
        updateSearchParams({ page: value });
      }}
      sx={sx}
    />
  );
}
