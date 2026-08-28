"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import Divider from "@mui/material/Divider";
import Drawer from "@mui/material/Drawer";
import IconButton from "@mui/material/IconButton";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import LaunchIcon from "@mui/icons-material/Launch";
import MenuIcon from "@mui/icons-material/Menu";
import OurLink from "./OurLink";
import { DOSSIERS_BASE, EVENTS_BASE, ROOT_SLUG, SITE_NAME } from "@/app/constants";

export default function MobileNavDrawer() {
  const t = useTranslations("browse");
  const tNav = useTranslations("nav");
  const [open, setOpen] = useState(false);

  const close = () => setOpen(false);

  const topLinks = [
    { label: SITE_NAME, href: `/${ROOT_SLUG}` },
    { label: t("dossiers"), href: `${DOSSIERS_BASE}/` },
    { label: t("events"), href: `${EVENTS_BASE}/` },
  ];

  return (
    <>
      <IconButton
        color="inherit"
        edge="start"
        onClick={() => setOpen(true)}
        aria-label={tNav("openMenu")}
        sx={{ display: { xs: "flex", lg: "none" } }}
      >
        <MenuIcon />
      </IconButton>
      <Drawer anchor="left" open={open} onClose={close}>
        <List sx={{ width: 240, pt: 1 }}>
          {topLinks.map((link) => (
            <ListItemButton
              key={link.href}
              component={OurLink}
              href={link.href}
              onClick={close}
            >
              <ListItemText primary={link.label} />
            </ListItemButton>
          ))}
          <Divider />
          <ListItemButton
            component="a"
            href="https://dezede.hypotheses.org/8934"
            onClick={close}
          >
            <LaunchIcon fontSize="small" sx={{ mr: 1, opacity: 0.6 }} />
            <ListItemText primary={tNav("protocol")} />
          </ListItemButton>
          <ListItemButton component="a" href="/" onClick={close}>
            <LaunchIcon fontSize="small" sx={{ mr: 1, opacity: 0.6 }} />
            <ListItemText primary="Dezède" />
          </ListItemButton>
        </List>
      </Drawer>
    </>
  );
}
