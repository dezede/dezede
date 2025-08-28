import Box from "@mui/material/Box";
import React from "react";

export default function SmallCaps({ children }: { children: React.ReactNode }) {
  return (
    <Box component="span" sx={{ fontFamily: "var(--font-bodoni-moda-sc)" }}>
      {children}
    </Box>
  );
}
