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
    document
      .getElementById("presentation")
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
    window.history.replaceState(null, "", "#presentation");
    window.dispatchEvent(new HashChangeEvent("hashchange"));
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
