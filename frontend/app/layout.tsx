import type { Metadata } from "next";
import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import { Bodoni_Moda, Bodoni_Moda_SC, Spectral, Spectral_SC } from "next/font/google";
import { ThemeProvider } from "@mui/material/styles";
import { NextIntlClientProvider } from "next-intl";
import { getLocale, getTranslations } from "next-intl/server";
import theme from "./theme";
import CssBaseline from "@mui/material/CssBaseline";
import CustomGlobalStyles from "@/components/CustomGlobalStyles";

const bodoniModa = Bodoni_Moda({
  variable: "--font-bodoni-moda",
  display: "swap",
});

const bodoniModaSc = Bodoni_Moda_SC({
  variable: "--font-bodoni-moda-sc",
  display: "swap",
});

// Spectral is a serif designed for on-screen body text. Bodoni Moda stays
// the display face for headings (see theme.ts); Spectral carries everything
// else so long passages — casting lists, transcriptions — read comfortably.
const spectral = Spectral({
  variable: "--font-body",
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
  display: "swap",
  subsets: ["latin"],
});

// Small-caps companion to Spectral, used for small caps in body text. Bodoni
// Moda SC stays for small caps inside headings (see CustomGlobalStyles).
const spectralSc = Spectral_SC({
  variable: "--font-body-sc",
  weight: ["400", "600"],
  display: "swap",
  subsets: ["latin"],
});

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("metadata");
  return {
    title: "Dezède",
    description: t("siteDescription"),
  };
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  return (
    <html
      lang={locale}
      className={`${bodoniModa.variable} ${bodoniModaSc.variable} ${spectral.variable} ${spectralSc.variable}`}
      // See https://nextjs.org/docs/messages/missing-data-scroll-behavior
      data-scroll-behavior="smooth"
    >
      <body>
        <AppRouterCacheProvider options={{ key: "css" }}>
          <NextIntlClientProvider>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <CustomGlobalStyles />
              {children}
            </ThemeProvider>
          </NextIntlClientProvider>
        </AppRouterCacheProvider>
      </body>
    </html>
  );
}
