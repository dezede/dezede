"use client";
import {
  alpha,
  createTheme,
  PaletteColorOptions,
  responsiveFontSizes,
} from "@mui/material/styles";

const primary: PaletteColorOptions = {
  light: "#f09875",
  main: "#ec8055",
  dark: "#ea6f3e",
  contrastText: "#ffffff",
};

export default responsiveFontSizes(
  createTheme({
    typography: {
      fontFamily: "var(--font-bodoni-moda)",
      h1: {
        fontSize: "3rem",
        fontFamily: "var(--font-bodoni-moda-sc)",
      },
      h2: {
        fontSize: "2.25rem",
        fontFamily: "var(--font-bodoni-moda-sc)",
      },
      h3: {
        fontSize: "1.75rem",
        fontFamily: "var(--font-bodoni-moda-sc)",
      },
      h4: {
        fontSize: "1.5rem",
        fontFamily: "var(--font-bodoni-moda-sc)",
      },
      h5: {
        fontSize: "1.25rem",
        fontFamily: "var(--font-bodoni-moda-sc)",
      },
      h6: {
        fontSize: "1rem",
        fontFamily: "var(--font-bodoni-moda-sc)",
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
          },
        },
      },
    },
    palette: {
      text: {
        primary: "#222222",
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
          "a:not([class])": {
            color: primary.main,
            textDecoration: "none",
            "&:hover, &:active, &:focus": {
              textDecoration: "underline",
            },
            '&[data-note="anchor"], &[data-note="reference"]:focus': {
              "&:focus": {
                background: alpha(primary.main, 0.15),
                borderRadius: 4,
              },
            },
            '&[data-note="reference"]': {
              verticalAlign: "super",
              fontSize: "0.85rem",
            },
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
