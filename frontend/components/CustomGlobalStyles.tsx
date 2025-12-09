"use client";

import GlobalStyles from "@mui/material/GlobalStyles";
import { alpha } from "@mui/material/styles";

export default function CustomGlobalStyles() {
  return (
    <GlobalStyles
      styles={(theme) => ({
        html: {
          scrollBehavior: "smooth",
        },
        h1: theme.typography.h1,
        h2: theme.typography.h2,
        h3: theme.typography.h3,
        h4: theme.typography.h4,
        h5: theme.typography.h5,
        h6: theme.typography.h6,
        "a:not([class]), a[data-link-type]": {
          color: theme.palette.primary.dark,
          textDecoration: "none",
          "&:hover, &:active, &:focus": {
            textDecoration: "underline",
          },
          '&[data-note="anchor"], &[data-note="reference"]:focus': {
            "&:focus": {
              background: alpha(theme.palette.primary.dark, 0.15),
              borderRadius: 4,
            },
          },
          '&[data-note="reference"]': {
            verticalAlign: "super",
            fontSize: "0.85rem",
          },
        },
        "span.sc": {
          fontFamily: "var(--font-bodoni-moda-sc)",
        },
      })}
    />
  );
}
