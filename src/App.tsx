import React from "react";
import { createTheme, ThemeProvider } from "@mui/material/styles";
import LinearProgress from "@mui/material/LinearProgress";

import SourceView from "./SourceView";

const theme = createTheme({
  palette: {
    primary: {
      main: "#e75e27",
    },
    secondary: {
      main: "#fff7d1",
    },
  },
  typography: {
    fontFamily: "'Linux Biolinum', Arial, sans-serif",
  },
  components: {
    MuiButtonBase: {
      styleOverrides: {
        root: {
          "&:hover": {
            color: "inherit",
          },
        },
      },
    },
  },
});

export default function App({ div }: { div: Element }) {
  const sourceId = div.getAttribute("data-id");
  return (
    <ThemeProvider theme={theme}>
      <React.Suspense
        fallback={
          <LinearProgress
            style={{ position: "absolute", top: 0, left: 0, width: "100%" }}
          />
        }
      >
        {sourceId && <SourceView id={parseInt(sourceId)} />}
      </React.Suspense>
    </ThemeProvider>
  );
}
