"use client";

import GlobalStyles from "@mui/material/GlobalStyles";

export default function CustomGlobalStyles() {
  return (
    <GlobalStyles
      styles={(theme) => ({
        html: {
          scrollBehavior: "smooth",
          // Small caps default to Spectral SC (the body face). Headings below
          // switch this back to Bodoni Moda SC, so small caps inside a title
          // (e.g. a person's surname) match the Bodoni display face.
          "--sc-font": "var(--font-body-sc)",
        },
        h1: { ...theme.typography.h1, "--sc-font": "var(--font-bodoni-moda-sc)" },
        h2: { ...theme.typography.h2, "--sc-font": "var(--font-bodoni-moda-sc)" },
        h3: { ...theme.typography.h3, "--sc-font": "var(--font-bodoni-moda-sc)" },
        h4: { ...theme.typography.h4, "--sc-font": "var(--font-bodoni-moda-sc)" },
        h5: { ...theme.typography.h5, "--sc-font": "var(--font-bodoni-moda-sc)" },
        h6: { ...theme.typography.h6, "--sc-font": "var(--font-bodoni-moda-sc)" },
        "a:not([class]), a[data-link-type]": {
          // Use the CSS variable (not theme.palette.*, which resolves to the
          // static light-mode literal) so the colour follows the active scheme
          // — primary.dark is lightened in the dark scheme for contrast.
          color: theme.vars.palette.primary.dark,
          textDecoration: "none",
          "&:hover, &:active, &:focus": {
            textDecoration: "underline",
          },
          '&[data-note="anchor"], &[data-note="reference"]:focus': {
            "&:focus": {
              background: `rgba(${theme.vars.palette.primary.darkChannel} / 0.15)`,
              borderRadius: 4,
            },
          },
          '&[data-note="reference"]': {
            verticalAlign: "super",
            fontSize: "0.85rem",
          },
        },
        "span.sc": {
          fontFamily: "var(--sc-font)",
        },
        ".skip-to-content": {
          position: "absolute",
          left: "-9999px",
          top: "auto",
          width: "1px",
          height: "1px",
          overflow: "hidden",
          zIndex: 9999,
          "&:focus": {
            left: 0,
            top: 0,
            width: "auto",
            height: "auto",
            overflow: "visible",
            padding: "8px 16px",
            background: theme.vars.palette.background.paper,
            color: theme.vars.palette.text.primary,
            textDecoration: "none",
            fontWeight: 600,
            outline: `3px solid ${theme.vars.palette.primary.main}`,
          },
        },
        "@media (prefers-reduced-motion: reduce)": {
          "*, *::before, *::after": {
            animationDuration: "0.01ms !important",
            animationIterationCount: "1 !important",
            transitionDuration: "0.01ms !important",
            scrollBehavior: "auto !important",
          },
        },
      })}
    />
  );
}
