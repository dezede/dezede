"use client";

import type {} from "@mui/material/themeCssVarsAugmentation";
import { createTheme, responsiveFontSizes } from "@mui/material/styles";

const primary = {
  light: "#d97c2c",
  main: "#b45309",   // Tailwind amber-700 — 4.83:1 on cream, 5.02:1 on white
  dark: "#7c3906",   // 8.26:1 on cream, 7.97:1 on paper
  contrastText: "#ffffff",
};

export default responsiveFontSizes(
  createTheme({
    cssVariables: true,
    typography: {
      // Body / reading text uses Spectral; headings keep Bodoni Moda below.
      fontFamily: "var(--font-body)",
      body1: {
        lineHeight: 1.6,
      },
      body2: {
        lineHeight: 1.55,
      },
      h1: {
        fontFamily: "var(--font-bodoni-moda)",
        fontSize: "2.5rem",
        lineHeight: 1.15,
      },
      h2: {
        fontFamily: "var(--font-bodoni-moda)",
        fontSize: "1.875rem",
        lineHeight: 1.2,
      },
      h3: {
        fontFamily: "var(--font-bodoni-moda)",
        fontSize: "1.45rem",
      },
      h4: {
        fontFamily: "var(--font-bodoni-moda)",
        fontSize: "1.25rem",
      },
      h5: {
        fontFamily: "var(--font-bodoni-moda)",
        fontSize: "1.05rem",
      },
      h6: {
        fontFamily: "var(--font-bodoni-moda)",
        fontSize: "0.9rem",
      },
    },
    colorSchemes: {
      dark: {
        palette: {
          primary: {
            ...primary,
            dark: primary.light,  // #d97c2c — 6.5:1 on dark bg vs #7c3906's ~2:1
          },
          secondary: {
            light: "#999999",
            main: "#888888",
            dark: "#777777",
            contrastText: "#f8f8f8",
          },
          info: {
            main: "#e7e7e7",
          },
          background: {
            paper: "#1c1c1c",
            default: "#121212",
          },
        },
      },
    },
    palette: {
      text: {
        primary: "#222222",
        disabled: "#00000099",
      },
      primary,
      secondary: {
        light: "#ffffff",
        main: "#f8f8f8",
        dark: "#e7e7e7",
        contrastText: "#888888",
      },
      info: {
        main: "#e7e7e7",
      },
      background: {
        paper: "#fff7d1",
        default: "#fffbe6",
      },
    },
    components: {
      MuiAutocomplete: {
        styleOverrides: {
          // Keep the clear (×) button visible whenever a field has a value,
          // instead of only revealing it on hover/focus (and never on touch).
          clearIndicator: {
            visibility: "visible",
          },
        },
      },
      MuiButton: {
        defaultProps: {
          style: {
            textTransform: "none",
          },
        },
      },
      MuiLink: {
        styleOverrides: {
          // Reference the CSS variable so links follow the active colour scheme
          // (primary.dark is lightened in the dark scheme for contrast).
          root: ({ theme }) => ({
            color: theme.vars.palette.primary.dark,
          }),
        },
      },
      MuiListSubheader: {
        styleOverrides: {
          root: {
            lineHeight: 1.5,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          icon: ({ theme }) => ({
            [theme.getColorSchemeSelector("dark")]: {
              color: theme.vars.palette.text.primary,
            },
          }),
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: "none",
          },
        },
      },
    },
  }),
);
