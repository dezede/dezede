"use client";

import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Link from "next/link";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import LaunchIcon from "@mui/icons-material/Launch";
import { ROOT_SLUG } from "../constants";

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Box sx={{ display: "flex", flexFlow: "column nowrap", gap: 4 }}>
      <AppBar position="static">
        <Container>
          <Stack direction="row" justifyContent="space-between" sx={{ py: 1 }}>
            <Button
              component={Link}
              href={`/${ROOT_SLUG}`}
              prefetch={false}
              color="inherit"
            >
              OpenLetter
            </Button>
            <Button
              component="a"
              href="/"
              color="inherit"
              variant="outlined"
              startIcon={<LaunchIcon />}
            >
              Dezède
            </Button>
          </Stack>
        </Container>
      </AppBar>
      {children}
    </Box>
  );
}
