import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Link from "next/link";
import Button from "@mui/material/Button";
import { ROOT_SLUG } from "../constants";
import Stack from "@mui/material/Stack";

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
            <Button component={Link} href="/" prefetch={false} color="inherit">
              Dezède
            </Button>
          </Stack>
        </Container>
      </AppBar>
      <Container>{children}</Container>
    </Box>
  );
}
