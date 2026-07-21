"use client";

import type { ReactNode } from "react";
import Button from "@mui/material/Button";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import { TSibling } from "@/app/types";
import OurLink from "@/components/OurLink";

// Rendered as a Client Component on purpose: the <Tooltip> child element must be
// created on the client side. When this lived inline in the server layout, the
// IconButton element crossed the RSC boundary and `React.isValidElement` returned
// false for it during server rendering, so Tooltip fell back to wrapping it in an
// extra <span> on the server only — a hydration mismatch against the client, which
// renders the anchor directly. Authoring it here keeps both passes identical.
export default function SiblingButton({
  sibling,
  icon,
  right = false,
}: {
  sibling: TSibling;
  icon: ReactNode;
  right?: boolean;
}) {
  if (sibling === null) {
    // We keep an empty DOM object to preserve the alignment of the other sibling button.
    return <span />;
  }
  return (
    <>
      <Tooltip title={sibling.title}>
        <IconButton
          component={OurLink}
          href={sibling.url}
          size="large"
          aria-label={sibling.title}
          sx={{ display: { md: "none" } }}
        >
          {icon}
        </IconButton>
      </Tooltip>
      <Button
        component={OurLink}
        href={sibling.url}
        startIcon={right ? undefined : icon}
        endIcon={right ? icon : undefined}
        sx={{ maxWidth: "50%", display: { xs: "none", md: "flex" } }}
      >
        {sibling.title}
      </Button>
    </>
  );
}
