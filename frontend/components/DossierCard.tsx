import { ReactElement } from "react";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import EventOutlinedIcon from "@mui/icons-material/EventOutlined";
import HistoryEduOutlinedIcon from "@mui/icons-material/HistoryEduOutlined";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import FolderOutlinedIcon from "@mui/icons-material/FolderOutlined";
import { getTranslations } from "next-intl/server";
import { TDossierCard } from "@/app/types";
import { DOSSIERS_BASE } from "@/app/constants";
import OurLink from "./OurLink";

// `dossiers`-namespace translator, threaded into the plain helper so it can be
// called from both server components (DossierCard) and pages without a hook.
type DossierTranslator = Awaited<ReturnType<typeof getTranslations<"dossiers">>>;

export function kindLabel(
  dossier: TDossierCard,
  t: DossierTranslator,
): string {
  if (dossier.kind === "evenements") {
    return t("eventCount", { count: dossier.count });
  }
  if (dossier.kind === "oeuvres") {
    return t("workCount", { count: dossier.count });
  }
  if (dossier.kind === "sources") {
    return t("sourceCount", { count: dossier.count });
  }
  return "";
}

// Same event/work icons used across the site (see SearchResultItem), so a
// dossier's type reads at a glance on its count chip.
export function kindIcon(dossier: TDossierCard): ReactElement | undefined {
  if (dossier.kind === "evenements") return <EventOutlinedIcon />;
  if (dossier.kind === "oeuvres") return <HistoryEduOutlinedIcon />;
  if (dossier.kind === "sources") return <DescriptionOutlinedIcon />;
  return undefined;
}

export function subdossierLabel(
  dossier: TDossierCard,
  t: DossierTranslator,
): string {
  if (!dossier.children_count) return "";
  return t("subdossierCount", { count: dossier.children_count });
}

// Chips shown on a dossier card: its content-kind count (events/works/sources)
// plus, when it has any, how many sub-dossiers it groups.
function DossierChips({
  dossier,
  t,
  onImage = false,
}: {
  dossier: TDossierCard;
  t: DossierTranslator;
  // When laid over the cover image, chips get a translucent light backing and
  // dark text so they stay legible on the gradient scrim (an outlined chip would
  // wash out against the artwork).
  onImage?: boolean;
}) {
  const kind = kindLabel(dossier, t);
  const subdossiers = subdossierLabel(dossier, t);
  if (!kind && !subdossiers) return null;
  const chipSx = onImage
    ? {
        bgcolor: "rgba(255,255,255,0.9)",
        color: "rgba(0,0,0,0.87)",
        "& .MuiChip-icon": { color: "primary.dark" },
        "& .MuiChip-label": { lineHeight: 1 },
      }
    : { "& .MuiChip-icon": { marginLeft: "6px" }, "& .MuiChip-label": { lineHeight: 1 } };
  return (
    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
      {kind ? (
        <Chip
          icon={kindIcon(dossier)}
          label={kind}
          size="small"
          variant={onImage ? "filled" : "outlined"}
          sx={chipSx}
        />
      ) : null}
      {subdossiers ? (
        <Chip
          icon={<FolderOutlinedIcon />}
          label={subdossiers}
          size="small"
          variant={onImage ? "filled" : "outlined"}
          sx={chipSx}
        />
      ) : null}
    </Stack>
  );
}

const hoverLift = {
  transition: "box-shadow 0.2s, transform 0.2s",
  "&:hover": { boxShadow: 6, transform: "translateY(-2px)" },
} as const;

export default async function DossierCard({
  dossier,
}: {
  dossier: TDossierCard;
}) {
  const t = await getTranslations("dossiers");
  const href = `${DOSSIERS_BASE}/id/${dossier.id}/`;

  if (dossier.cover_image) {
    return (
      <Card
        elevation={0}
        sx={{ overflow: "hidden", ...hoverLift }}
      >
        <CardActionArea component={OurLink} href={href}>
          {/* No fixed aspect ratio or object-fit: cover here — the image keeps
              its natural proportions (never cropped), which is what lets the
              surrounding masonry layout pack cards of differing heights. */}
          <Box sx={{ position: "relative", display: "block" }}>
            <Box
              component="img"
              src={dossier.cover_image}
              alt=""
              loading="lazy"
              sx={{ display: "block", width: "100%", height: "auto" }}
            />
            {/* Title and count/subdossier chips are both laid over the cover,
                magazine-style, so the whole card reads as one framed picture.
                The gradient lives on the content wrapper (not the full image),
                so its height hugs the text + chips instead of covering most of
                the picture. */}
            <Box
              sx={{
                position: "absolute",
                insetInline: 0,
                bottom: 0,
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
                {dossier.titre}
              </Typography>
              <DossierChips dossier={dossier} t={t} onImage />
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
            {dossier.titre}
          </Typography>
          {dossier.excerpt ? (
            <Typography variant="body2" color="text.secondary">
              {dossier.excerpt}
            </Typography>
          ) : null}
          <DossierChips dossier={dossier} t={t} />
        </Stack>
      </CardActionArea>
    </Card>
  );
}
