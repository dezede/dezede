"use client";

import Button from "@mui/material/Button";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";

// Scrolls smoothly instead of relying on CSS `scroll-behavior`, which some
// browsers skip for hash navigation depending on user/OS motion settings.
// Also dispatches a `hashchange` event manually, since `history.replaceState`
// doesn't fire one, so DossierTabs still switches to the Présentation tab.
export default function JumpToPresentationButton({ label }: { label: string }) {
  const handleClick = (event: React.MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    // Switch to the Présentation tab first: while another tab is active the
    // `#presentation` element sits in a `display: none` panel, on which
    // `scrollIntoView` is a no-op.
    window.history.replaceState(null, "", "#presentation");
    window.dispatchEvent(new HashChangeEvent("hashchange"));
    // Two frames so DossierTabs has re-rendered and the panel is visible
    // before scrolling (also fine when it was already visible).
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        document
          .getElementById("presentation")
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      }),
    );
  };

  return (
    <Button
      component="a"
      href="#presentation"
      startIcon={<ArrowDownwardIcon />}
      onClick={handleClick}
      sx={{ alignSelf: "flex-start" }}
    >
      {label}
    </Button>
  );
}
