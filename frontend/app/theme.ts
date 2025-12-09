"use client";

import type {} from "@mui/material/themeCssVarsAugmentation";
import { createTheme, responsiveFontSizes } from "@mui/material/styles";

const primary = {
  light: "#f09875",
  main: "#ec8055",
  dark: "#e75e27",
  contrastText: "#ffffff",
};

export default responsiveFontSizes(
  createTheme({
    cssVariables: true,
    typography: {
      fontFamily: "var(--font-bodoni-moda)",
      h1: {
        fontSize: "2.5rem",
      },
      h2: {
        fontSize: "1.875rem",
      },
      h3: {
        fontSize: "1.45rem",
      },
      h4: {
        fontSize: "1.25rem",
      },
      h5: {
        fontSize: "1.05rem",
      },
      h6: {
        fontSize: "0.9rem",
      },
    },
    colorSchemes: {
      dark: {
        palette: {
          primary,
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
      MuiButton: {
        defaultProps: {
          style: {
            textTransform: "none",
          },
        },
      },
      MuiLink: {
        styleOverrides: {
          root: {
            color: primary.dark,
          },
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
