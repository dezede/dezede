import Box from "@mui/material/Box";
import React from "react";

export default function Empty({
  children,
  height,
}: {
  children: React.ReactNode;
  height?: React.CSSProperties["height"];
}) {
  return (
    <Box height={height} py={10} textAlign="center" color="text.disabled">
      {children}
    </Box>
  );
}
