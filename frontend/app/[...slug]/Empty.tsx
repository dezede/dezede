import Box from "@mui/material/Box";
import React from "react";

export default function Empty({
  children,
  width,
  height,
}: {
  children: React.ReactNode;
  width?: React.CSSProperties["width"];
  height?: React.CSSProperties["height"];
}) {
  return (
    <Box
      width={width}
      height={height}
      py={10}
      textAlign="center"
      color="text.disabled"
      display="flex"
      justifyContent="center"
      alignItems="center"
    >
      {children}
    </Box>
  );
}
