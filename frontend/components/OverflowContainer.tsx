"use client";

import React from "react";
import Box from "@mui/material/Box";
import { SxProps, useTheme } from "@mui/system";
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
  const theme = useTheme();
  return (
    <Box position="relative" maxHeight={maxHeight} overflow="hidden" sx={sx}>
      {children}
      <Box
        position="absolute"
        top={maxHeight - overflowHeight}
        width="100%"
        height={overflowHeight}
        sx={{
          backgroundImage: `linear-gradient(to bottom, transparent 0%, ${theme.palette.background.paper} 100%)`,
        }}
      />
    </Box>
  );
}
