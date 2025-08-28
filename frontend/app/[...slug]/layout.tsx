import AppBar from "@mui/material/AppBar";
import Box from "@mui/material/Box";
import Container from "@mui/material/Container";
import Link from "next/link";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import LaunchIcon from "@mui/icons-material/Launch";
import { ROOT_SLUG } from "../constants";
import Typography from "@mui/material/Typography";

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Box
      sx={{
        display: "flex",
        flexFlow: "column nowrap",
        gap: 4,
        paddingBottom: 4,
      }}
    >
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
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography>Financement :</Typography>
              <Button
                component="a"
                href="https://nbe.org.uk/wp/"
                target="_blank"
                variant="outlined"
                color="inherit"
                size="small"
              >
                New Berlioz Edition Trust
              </Button>
              <Button
                component="a"
                href="https://musica.hypotheses.org/"
                target="_blank"
                variant="outlined"
                color="inherit"
                size="small"
              >
                Consortium Musica2
              </Button>
            </Stack>
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
