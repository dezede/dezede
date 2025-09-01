import Box from "@mui/material/Box";
import { SxProps } from "@mui/material/styles";
import React from "react";

export default function Empty({
  children,
  sx,
}: {
  children: React.ReactNode;
  sx?: SxProps;
}) {
  return (
    <Box
      py={10}
      textAlign="center"
      color="text.disabled"
      display="flex"
      justifyContent="center"
      alignItems="center"
      bgcolor="#00000014"
      sx={sx}
    >
      {children}
    </Box>
  );
}
