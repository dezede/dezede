"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import { useLocale } from "next-intl";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import ListItemText from "@mui/material/ListItemText";
import Check from "@mui/icons-material/Check";
import TranslateIcon from "@mui/icons-material/Translate";
import { setLocale } from "@/app/locale-actions";
import { LOCALES, type Locale } from "@/i18n/config";

const LOCALE_LABELS: Record<Locale, string> = {
  en: "English",
  fr: "Français",
};

// Name of the BroadcastChannel used to keep the UI language in sync across
// all open tabs of the site.
const LOCALE_CHANNEL = "dezede-locale";

/**
 * Navbar control to switch the UI language. The choice is stored in a cookie
 * by the `setLocale` server action; the page tree re-renders with the new
 * locale's messages once the action resolves. The change is also broadcast to
 * every other open tab, which refresh to pick up the new locale cookie.
 */
export default function LanguageSwitcher() {
  const locale = useLocale() as Locale;
  const router = useRouter();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [isPending, startTransition] = useTransition();
  const channelRef = useRef<BroadcastChannel | null>(null);

  // Listen for locale changes made in other tabs. The originating tab does not
  // receive its own messages, so any message here means a sibling tab switched
  // language; refreshing re-renders the tree with the (already updated) cookie.
  useEffect(() => {
    if (typeof BroadcastChannel === "undefined") return;
    const channel = new BroadcastChannel(LOCALE_CHANNEL);
    channelRef.current = channel;
    channel.onmessage = (event) => {
      if (event.data !== locale) {
        router.refresh();
      }
    };
    return () => {
      channel.close();
      channelRef.current = null;
    };
  }, [locale, router]);

  const handleSelect = (next: Locale) => {
    setAnchorEl(null);
    if (next !== locale) {
      startTransition(async () => {
        await setLocale(next);
        // Tell every other open tab to pick up the new locale cookie.
        channelRef.current?.postMessage(next);
      });
    }
  };

  return (
    <>
      <IconButton
        color="inherit"
        onClick={(event) => setAnchorEl(event.currentTarget)}
        aria-label={LOCALE_LABELS[locale]}
        disabled={isPending}
      >
        <TranslateIcon />
      </IconButton>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        {LOCALES.map((code) => (
          <MenuItem
            key={code}
            selected={code === locale}
            onClick={() => handleSelect(code)}
          >
            <Check
              fontSize="small"
              sx={{ mr: 1, visibility: code === locale ? "visible" : "hidden" }}
            />
            <ListItemText>{LOCALE_LABELS[code]}</ListItemText>
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}
