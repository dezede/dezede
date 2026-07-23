"use client";

import { useMainScrollable } from "@/components/MainScroll";

/** Renders nothing; opts the shared `main` region out of scrolling. */
export default function MainNotScrollable() {
  useMainScrollable(false);
  return null;
}
