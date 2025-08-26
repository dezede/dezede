"use client";

import Pagination, {
  PaginationRenderItemParams,
} from "@mui/material/Pagination";
import PaginationItem from "@mui/material/PaginationItem";
import Link from "next/link";

function renderItem(item: PaginationRenderItemParams) {
  return (
    <PaginationItem {...item} component={Link} href={`?page=${item.page}`} />
  );
}

export default function CustomPagination({
  page,
  count,
  perPage,
}: {
  page: number;
  perPage: number;
  count: number;
}) {
  return (
    <Pagination
      count={Math.ceil(count / perPage)}
      page={page}
      renderItem={renderItem}
    />
  );
}
