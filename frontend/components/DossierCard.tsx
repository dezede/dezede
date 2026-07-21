import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { getTranslations } from "next-intl/server";
import { TDossierCard, TDossierKind } from "@/app/types";
import { DOSSIERS_BASE } from "@/app/constants";
import OurLink from "./OurLink";
import DossierCountChips from "./DossierCountChips";
import SafeText from "@/format/SafeText";

// `dossiers`-namespace translator, threaded into the plain helpers so they can
// be called from both server components (DossierCard) and pages without a hook.
type DossierTranslator = Awaited<
  ReturnType<typeof getTranslations<"dossiers">>
>;

export function kindLabel(
  kind: TDossierKind,
  count: number,
  t: DossierTranslator,
): string {
  if (kind === "evenements") {
    return t("eventCount", { count });
  }
  if (kind === "oeuvres") {
    return t("workCount", { count });
  }
  return t("sourceCount", { count });
}

const hoverLift = {
  transition: "box-shadow 0.2s, transform 0.2s",
  "&:hover": { boxShadow: 6, transform: "translateY(-2px)" },
} as const;

export default function DossierCard({ dossier }: { dossier: TDossierCard }) {
  const href = `${DOSSIERS_BASE}/id/${dossier.id}/`;

  if (dossier.cover_image) {
    return (
      <Card elevation={0} sx={{ overflow: "hidden", ...hoverLift }}>
        <CardActionArea component={OurLink} href={href}>
          {/* No fixed aspect ratio or object-fit: cover here — the image keeps
              its natural proportions (never cropped), which is what lets the
              surrounding masonry layout pack cards of differing heights.
              Image and overlay are stacked via CSS grid (same grid area)
              rather than absolute positioning, so the container grows to fit
              the overlay's content even when a very wide/short image would
              otherwise be too short to hold the title and chips. */}
          <Box sx={{ display: "grid" }}>
            <Box
              component="img"
              src={dossier.cover_image}
              alt=""
              loading="lazy"
              sx={{
                gridArea: "1 / 1",
                display: "block",
                width: "100%",
                height: "auto",
              }}
            />
            {/* Title and count/subdossier chips are both laid over the cover,
                magazine-style, so the whole card reads as one framed picture.
                The gradient lives on the content wrapper (not the full image),
                so its height hugs the text + chips instead of covering most of
                the picture. */}
            <Box
              sx={{
                gridArea: "1 / 1",
                alignSelf: "end",
                display: "flex",
                flexDirection: "column",
                gap: 1,
                px: 1.5,
                pb: 1.5,
                pt: 4,
                background:
                  "linear-gradient(to top, rgba(0,0,0,0.82) 0%, rgba(0,0,0,0.55) 55%, rgba(0,0,0,0) 100%)",
              }}
            >
              <Typography
                variant="h3"
                sx={{
                  m: 0,
                  fontSize: "1.1rem",
                  lineHeight: 1.25,
                  color: "common.white",
                  textShadow: "0 1px 3px rgba(0,0,0,0.6)",
                }}
              >
                <SafeText value={dossier.titre} />
              </Typography>
              <DossierCountChips
                dossierId={dossier.id}
                kinds={dossier.kinds}
                initialCounts={dossier.counts}
                childrenCount={dossier.children_count}
                onImage
              />
            </Box>
          </Box>
        </CardActionArea>
      </Card>
    );
  }

  return (
    <Card variant="outlined" sx={{ height: "100%", ...hoverLift }}>
      <CardActionArea
        component={OurLink}
        href={href}
        sx={{ height: "100%", alignItems: "flex-start", p: 2 }}
      >
        <Stack spacing={1} sx={{ width: "100%" }}>
          <Typography variant="h3" sx={{ fontSize: "1.1rem", m: 0 }}>
            <SafeText value={dossier.titre} />
          </Typography>
          {dossier.excerpt ? (
            <Typography variant="body2" color="text.secondary">
              {dossier.excerpt}
            </Typography>
          ) : null}
          <DossierCountChips
            dossierId={dossier.id}
            kinds={dossier.kinds}
            initialCounts={dossier.counts}
            childrenCount={dossier.children_count}
          />
        </Stack>
      </CardActionArea>
    </Card>
  );
}
