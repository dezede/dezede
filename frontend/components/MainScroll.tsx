"use client";

import { createContext, useContext, useEffect, useState } from "react";
import Box, { BoxProps } from "@mui/material/Box";

const MainScrollContext = createContext<
  ((scrollable: boolean) => void) | null
>(null);

/**
 * Wraps the shared `<main>` region. `main` scrolls by default (most pages are
 * plain content taller than the viewport); pages that manage their own
 * fill-viewport layout (e.g. the virtualised authority tables, whose own body
 * is the only scroll) opt out with `useMainScrollable(false)`.
 */
export function MainScrollArea({ sx, ...props }: Omit<BoxProps, "component">) {
  const [scrollable, setScrollable] = useState(true);
  return (
    <MainScrollContext.Provider value={setScrollable}>
      <Box
        component="main"
        {...props}
        sx={{ ...sx, overflowY: scrollable ? "scroll" : "visible" }}
      />
    </MainScrollContext.Provider>
  );
}

export function useMainScrollable(scrollable: boolean) {
  const setScrollable = useContext(MainScrollContext);
  useEffect(() => {
    if (scrollable || !setScrollable) return;
    setScrollable(false);
    return () => setScrollable(true);
  }, [scrollable, setScrollable]);
}
