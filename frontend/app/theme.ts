"use client";
import { createTheme } from "@mui/material/styles";

export default createTheme({
  typography: {
    fontFamily: "var(--font-roboto)",
    h1: {
      fontSize: "3rem",
    },
    h2: {
      fontSize: "2.25rem",
    },
    h3: {
      fontSize: "1.75rem",
    },
    h4: {
      fontSize: "1.5rem",
    },
    h5: {
      fontSize: "1.25rem",
    },
    h6: {
      fontSize: "1rem",
    },
  },
  colorSchemes: {
    dark: true,
  },
  palette: {
    primary: {
      light: "#f09875",
      main: "#ec8055",
      dark: "#ea6f3e",
      contrastText: "#ffffff",
    },
    secondary: {
      light: "#ffffff",
      main: "#f8f8f8",
      dark: "#e7e7e7",
      contrastText: "#888888",
    },
    background: {
      paper: "#fff7d1",
      default: "#fffbe6",
    },
  },
});
