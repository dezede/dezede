"use client";

import React from "react";
import Box from "@mui/material/Box";
import { SxProps } from "@mui/system";
import { Theme } from "@mui/material/styles";

export default function OverflowContainer({
  maxHeight,
  overflowHeight = 30,
  children,
  sx,
}: {
  maxHeight: number;
  overflowHeight?: number;
  sx?: SxProps<Theme>;
  children: React.ReactNode;
}) {
  return (
    <Box
      sx={{
        position: "relative",
        maxHeight,
        overflow: "hidden",
        ...sx,
      }}
    >
      {children}
      <Box
        sx={{
          position: "absolute",
          top: maxHeight - overflowHeight,
          width: "100%",
          height: overflowHeight,
          backgroundImage: (theme) =>
            `linear-gradient(to bottom, transparent 0%, ${theme.vars.palette.background.paper} 100%)`,
        }}
      />
    </Box>
  );
}
