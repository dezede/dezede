import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import LaunchIcon from "@mui/icons-material/Launch";
import GetAppIcon from "@mui/icons-material/GetApp";
import { useTranslations } from "next-intl";
import { TSourceDetail } from "@/app/types";
import EntityChipList from "./EntityChipList";
import SourceImagesReader from "./SourceImagesReader";
import RichText from "./RichText";
import Empty from "./Empty";

/**
 * The "Consulter" tab content: the playable/viewable media of a source —
 * an audio/video player (full file or excerpt, decided server-side), a
 * page-image reader, or the child sources of a collection — plus an optional
 * download/external-link button and the transcribed text. These can coexist
 * (e.g. an audio source may also carry a transcription), so each is rendered
 * as an independent stacked section. Mirrors the Django `source_content.html`
 * and the legacy `SourceView`.
 */
export default function SourceMedia({ source }: { source: TSourceDetail }) {
  const t = useTranslations("source");
  const { media, download } = source;

  const downloadButton = download ? (
    <Box sx={{ textAlign: "center" }}>
      <Button
        component="a"
        href={download.url}
        target="_blank"
        variant="outlined"
        size="small"
        startIcon={
          download.kind === "link" ? (
            <LaunchIcon fontSize="small" />
          ) : (
            <GetAppIcon fontSize="small" />
          )
        }
      >
        {download.kind === "link"
          ? t("originalOn", { url: new URL(download.url).hostname })
          : `${t("download")} (${download.size})`}
      </Button>
    </Box>
  ) : null;

  let viewer = null;
  if (media) {
    viewer = (
      <Stack spacing={1} sx={{ alignItems: "center" }}>
        {media.kind === "audio" ? (
          <audio controls preload="auto" style={{ width: "100%" }}>
            {media.sources.map((file) => (
              <source key={file.url} src={file.url} type={file.mimetype} />
            ))}
          </audio>
        ) : (
          <Box
            component="video"
            controls
            preload="auto"
            width={media.width || 640}
            height={media.height || 360}
            sx={{ maxWidth: "100%", height: "auto" }}
          >
            {media.sources.map((file) => (
              <source key={file.url} src={file.url} type={file.mimetype} />
            ))}
          </Box>
        )}
        {!media.is_full ? (
          <Typography variant="caption" color="text.secondary">
            {t("excerptLoginPrompt")}
          </Typography>
        ) : null}
      </Stack>
    );
  } else if (source.images.length > 0) {
    viewer = <SourceImagesReader images={source.images} />;
  } else if (source.collection_children.length > 0) {
    viewer = <EntityChipList entities={source.collection_children} />;
  }

  const transcription = source.transcription ? (
    <Box
      component="blockquote"
      sx={{
        m: 0,
        pl: 2,
        borderLeft: 4,
        borderColor: "primary.main",
        color: "text.secondary",
        fontStyle: "italic",
      }}
    >
      <RichText value={source.transcription} />
      {source.auteurs_html ? (
        <Box
          component="footer"
          sx={{ mt: 1, fontStyle: "normal", color: "text.primary" }}
        >
          <RichText value={source.auteurs_html} />
        </Box>
      ) : null}
    </Box>
  ) : null;

  if (!downloadButton && !viewer && !transcription) {
    return <Empty sx={{ py: 6 }}>{t("noViewableContent")}</Empty>;
  }

  return (
    <Stack spacing={4}>
      {downloadButton}
      {viewer}
      {transcription}
    </Stack>
  );
}
