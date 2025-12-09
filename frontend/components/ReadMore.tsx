"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { SxProps } from "@mui/system";
import { Theme } from "@mui/material/styles";
import Button from "@mui/material/Button";
import Collapse from "@mui/material/Collapse";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

export default function ReadMore({
  maxHeight,
  overflowHeight = 100,
  children,
  sx,
}: {
  maxHeight: number;
  overflowHeight?: number;
  sx?: SxProps<Theme>;
  children: React.ReactNode;
}) {
  const [collapseRequired, setCollapseRequired] = useState(false);
  const [open, setOpen] = useState(false);

  const collapseRef = useRef<HTMLDivElement>(undefined);
  const collapseCoverRef = useRef<HTMLDivElement>(undefined);

  const updateCollapseRequired = useCallback(() => {
    const collapse = collapseRef.current;
    const collapseCover = collapseCoverRef.current;
    if (collapse && collapseCover) {
      setCollapseRequired(
        collapse.scrollHeight - collapseCover.scrollHeight > maxHeight,
      );
    }
  }, [maxHeight]);

  useEffect(() => {
    updateCollapseRequired();
  }, [updateCollapseRequired]);

  useEffect(() => {
    window.addEventListener("resize", updateCollapseRequired);
    return () => {
      window.removeEventListener("resize", updateCollapseRequired);
    };
  }, [updateCollapseRequired]);

  const collapsed = collapseRequired && !open;
  return (
    <Collapse
      ref={collapseRef}
      in={!collapsed}
      collapsedSize={collapseRequired ? maxHeight : 0}
      exit={false}
      sx={{ position: "relative", ...sx }}
    >
      {children}
      <Collapse
        ref={collapseCoverRef}
        in={collapsed}
        enter={false}
        sx={(theme) => ({
          position: "absolute",
          bottom: 0,
          width: "100%",
          "& .MuiCollapse-wrapperInner": {
            display: "flex",
            justifyContent: "center",
            alignItems: "end",
            minHeight: overflowHeight,
            backgroundImage: `linear-gradient(to bottom, transparent 0%, ${theme.vars.palette.background.default} 100%)`,
          },
        })}
      >
        <Button
          variant="contained"
          color="info"
          onClick={() => setOpen(true)}
          disableElevation
          endIcon={<ExpandMoreIcon />}
          sx={{ borderRadius: 4 }}
        >
          Lire plus
        </Button>
      </Collapse>
    </Collapse>
  );
}
