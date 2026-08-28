"use client";

import type { ReactNode } from "react";
import Tooltip from "@mui/material/Tooltip";

// MUI <Tooltip> checks `React.isValidElement` on its child, and that returns
// inconsistent results across the RSC/SSR/hydration boundary when the child
// element is authored in a Server Component — Tooltip then wraps it in an extra
// <span> on only one side, causing a hydration mismatch. `richLabel`'s
// `renderNode` runs inside Server Components (event programmes, work chips…), so
// the tooltip's child <span> is created here, in a Client Component, keeping the
// server and client renders identical. `children` (the rich-label content) is
// just passed through as the span's contents, so it's unaffected.
export default function LabelTooltip({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <Tooltip title={title} arrow disableInteractive>
      <span>{children}</span>
    </Tooltip>
  );
}
