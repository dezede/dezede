"use client";

import Pagination from "@mui/material/Pagination";
import { useUpdateSearchParams } from "../hooks";
import { safeParseInt } from "../utils";
import { useState } from "react";
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
  const [page, setPage] = useState(safeParseInt(searchParams.get("page"), 1));
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
