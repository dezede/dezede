"use client";
import { alpha, createTheme, responsiveFontSizes } from "@mui/material/styles";

const primary = {
  light: "#f09875",
  main: "#ec8055",
  dark: "#e75e27",
  contrastText: "#ffffff",
};

const theme = responsiveFontSizes(
  createTheme({
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
      MuiCssBaseline: {
        styleOverrides: {
          html: {
            scrollBehavior: "smooth",
          },
          "a:not([class]), a[data-link-type]": {
            color: primary.dark,
            textDecoration: "none",
            "&:hover, &:active, &:focus": {
              textDecoration: "underline",
            },
            '&[data-note="anchor"], &[data-note="reference"]:focus': {
              "&:focus": {
                background: alpha(primary.dark, 0.15),
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

const baseCssOverrides = theme.components?.MuiCssBaseline?.styleOverrides;
if (typeof baseCssOverrides === "object") {
  baseCssOverrides.h2 = theme.typography.h2;
  baseCssOverrides.h3 = theme.typography.h3;
  baseCssOverrides.h4 = theme.typography.h4;
  baseCssOverrides.h5 = theme.typography.h5;
  baseCssOverrides.h6 = theme.typography.h6;
}

export default theme;
