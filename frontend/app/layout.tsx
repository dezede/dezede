import type { Metadata } from "next";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import { Bodoni_Moda, Bodoni_Moda_SC } from "next/font/google";
import { ThemeProvider } from "@mui/material/styles";
import theme from "./theme";
import CssBaseline from "@mui/material/CssBaseline";

const bodoniModa = Bodoni_Moda({
  variable: "--font-bodoni-moda",
  display: "swap",
});

const bodoniModaSc = Bodoni_Moda_SC({
  variable: "--font-bodoni-moda-sc",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Dezède",
  description: "Base de données musicologique",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${bodoniModa.variable} ${bodoniModaSc.variable}`}
      // See https://nextjs.org/docs/messages/missing-data-scroll-behavior
      data-scroll-behaviour="smooth"
    >
      <body>
        <AppRouterCacheProvider options={{ key: "css" }}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            {children}
          </ThemeProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
