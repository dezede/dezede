"use client";

import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { useTranslations } from "next-intl";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import Slider from "@mui/material/Slider";
import CircularProgress from "@mui/material/CircularProgress";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import DownloadIcon from "@mui/icons-material/Download";
import PrintIcon from "@mui/icons-material/Print";
import LinkIcon from "@mui/icons-material/Link";
import {
  TransformWrapper,
  TransformComponent,
  type ReactZoomPanPinchRef,
} from "react-zoom-pan-pinch";
import { TSourceImage } from "@/app/types";
import { SOURCES_BASE } from "@/app/constants";
import OurLink from "./OurLink";
import DetailAdminBar from "./DetailAdminBar";
import EntityChipList from "./EntityChipList";
import Empty from "./Empty";

function pageLabel(
  image: TSourceImage,
  index: number,
  t: ReturnType<typeof useTranslations>,
): string {
  return image.label || t("page", { number: index + 1 });
}

function fileName(url: string): string {
  return url.replace(/^.*[\\/]/, "");
}

// Large, translucent circular nav arrows floating over the image edges. The dark
// surface stays legible over pages of any colour, in both light and dark mode.
const arrowSx = {
  position: "absolute",
  top: "50%",
  transform: "translateY(-50%)",
  zIndex: 2,
  color: "#fff",
  bgcolor: "rgba(0, 0, 0, 0.45)",
  backdropFilter: "blur(2px)",
  transition: "background-color 0.2s",
  "&:hover": { bgcolor: "rgba(0, 0, 0, 0.65)" },
} as const;

// A translucent pill backing a floating row of per-page controls, so the buttons
// stay legible over a page of any colour without obscuring much of it.
const pillSx = {
  borderRadius: 2,
  bgcolor: "rgba(255, 255, 255, 0.85)",
  backdropFilter: "blur(2px)",
  boxShadow: 1,
  color: "rgba(0,0,0,0.6)",
  "& .MuiIconButton-root:not([class*='MuiIconButton-color'])": { color: "rgba(0,0,0,0.6)" },
} as const;

/**
 * Page-by-page reader for a source's scanned images — the Next.js equivalent of
 * the old `source-view` React viewer. Reaches feature parity with it: zoom/pan,
 * prev/next + a page slider, download, print, and progressive resolution
 * loading (the medium thumbnail paints first, then the full file swaps in).
 * Images are served directly by the source detail endpoint (full file +
 * thumbnail URLs), so no per-page round-trip is needed.
 */
export default function SourceImagesReader({
  images,
}: {
  images: TSourceImage[];
}) {
  const t = useTranslations("source");
  const [page, setPage] = useState(0);
  // What is actually painted on the stage: the source currently shown plus the
  // page it belongs to. We only update it once an image has *decoded*, so the
  // previous page keeps painting until the next one is ready to replace it
  // atomically — no empty flash, no collapse.
  const [displayed, setDisplayed] = useState<{
    src: string;
    page: number;
  } | null>(null);
  // Rendered height of the last painted image, used to hold the stage open so a
  // switch to a not-yet-decoded page can never collapse it.
  const [stageHeight, setStageHeight] = useState<number | null>(null);
  const transformRef = useRef<ReactZoomPanPinchRef>(null);
  // Tallest height the related-chips area has needed so far. Holding it open at
  // that height keeps the document height stable across pages: shrinking it
  // near the bottom of the page would force the browser to clamp the scroll
  // position, which reads as the whole reader jumping around.
  const [relatedMinHeight, setRelatedMinHeight] = useState(0);
  const relatedRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const height = relatedRef.current?.offsetHeight ?? 0;
    // The height can only be read from the DOM after layout, so it can't be
    // derived during render.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setRelatedMinHeight((previousMax) => Math.max(previousMax, height));
  }, [page]);

  const image = images[page] as TSourceImage | undefined;

  const previous = page >= 1 ? images[page - 1] : null;
  const next = page <= images.length - 2 ? images[page + 1] : null;

  // Progressive, decode-then-swap loading: decode the thumbnail and the full
  // file off-screen and only swap `displayed` once a source is ready. The
  // thumbnail paints first (unless the full is already cached, in which case it
  // wins the race and the thumbnail step is skipped), then the full upgrades it.
  useEffect(() => {
    if (!image) {
      return;
    }
    let cancelled = false;
    let fullShown = false;
    const thumb = image.thumbnail || image.url;

    const decode = async (src: string) => {
      const probe = new window.Image();
      probe.src = src;
      try {
        await probe.decode();
      } catch {
        // Decode can reject on cancelled/broken images; ignore and move on.
      }
      return !cancelled;
    };

    decode(thumb).then((ok) => {
      if (ok && !fullShown) {
        setDisplayed({ src: thumb, page });
      }
    });
    decode(image.url).then((ok) => {
      if (ok) {
        fullShown = true;
        setDisplayed({ src: image.url, page });
      }
    });

    return () => {
      cancelled = true;
    };
  }, [image, page]);

  // Reset zoom/pan whenever a new page is actually shown (the image element is
  // now persistent, so react-zoom-pan-pinch no longer resets on its own).
  useEffect(() => {
    transformRef.current?.resetTransform();
  }, [displayed?.page]);

  // Warms the cache for the neighbouring pages (both resolutions) so paging
  // feels instant.
  useEffect(() => {
    [previous, next].forEach((neighbour) => {
      if (neighbour) {
        new window.Image().src = neighbour.url;
        if (neighbour.thumbnail) {
          new window.Image().src = neighbour.thumbnail;
        }
      }
    });
  }, [previous, next]);

  const goTo = useCallback(
    (value: number) => setPage(Math.min(Math.max(value, 0), images.length - 1)),
    [images.length],
  );

  // Left/Right arrow keys page through the source, for a keyboard-friendly read.
  // Bail when the focus is on the slider or a form field so we never fight their
  // own arrow-key handling.
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") {
        return;
      }
      const active = document.activeElement;
      const tag = active?.tagName;
      if (
        active?.getAttribute("role") === "slider" ||
        tag === "INPUT" ||
        tag === "TEXTAREA" ||
        tag === "SELECT" ||
        (active as HTMLElement | null)?.isContentEditable
      ) {
        return;
      }
      goTo(e.key === "ArrowLeft" ? page - 1 : page + 1);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [goTo, page]);

  const handlePrint = useCallback(() => {
    if (!image) {
      return;
    }
    const popup = window.open();
    if (!popup) {
      return;
    }
    // A short delay before printing is required, otherwise it does not fire on
    // Chrome (matches the old `src/Reader.tsx` behaviour).
    popup.document.write(
      "<html><head>" +
        "<style>img { max-width: 100%; max-height: 100%; }</style>" +
        "</head><body>" +
        `<img src="${image.url}"` +
        ' onload="setTimeout(function () {' +
        "window.print(); window.close();" +
        '}, 200);" /></body></html>',
    );
    popup.focus();
  }, [image]);

  if (images.length === 0 || !image) {
    return <Empty sx={{ height: "50vh" }}>{t("missingImage")}</Empty>;
  }

  // Loading while nothing is painted yet, the painted page is stale, or only the
  // thumbnail (not the full file) is showing for the current page.
  const loading =
    !displayed || displayed.page !== page || displayed.src !== image.url;
  const displayedSrc = displayed?.src;

  return (
    <Stack spacing={1}>
      <Box
        sx={{
          position: "relative",
          // Hold the stage open with the last rendered image's height so a
          // switch to a not-yet-decoded page can never collapse it (the API
          // gives no per-image dimensions to reserve space ahead of time).
          minHeight: stageHeight ?? "40vh",
          // A subtle framed surface so the letterboxing around pages of any
          // aspect ratio reads as intentional rather than empty.
          borderRadius: 2,
          border: 1,
          borderColor: "divider",
          bgcolor: "action.hover",
          overflow: "hidden",
        }}
      >
        <TransformWrapper ref={transformRef}>
          <TransformComponent
            wrapperStyle={{ width: "100%", height: "100%" }}
            contentStyle={{
              width: "100%",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            {displayedSrc ? (
              <Box
                component="img"
                src={displayedSrc}
                alt={pageLabel(image, page, t)}
                onLoad={(e) =>
                  setStageHeight(e.currentTarget.clientHeight || null)
                }
                sx={{
                  // Bound the image by the stage width and the viewport height,
                  // letting the other dimension follow naturally so the aspect
                  // ratio is always preserved (no stretching of tall pages).
                  // Because the thumbnail and the full file share the same
                  // ratio, both resolve to the same on-screen size and the
                  // progressive swap stays shift-free.
                  maxWidth: "100%",
                  maxHeight: "80vh",
                  width: "auto",
                  height: "auto",
                  display: "block",
                  filter: loading ? "blur(2px)" : undefined,
                  transition: "filter 0.2s",
                }}
              />
            ) : null}
          </TransformComponent>
        </TransformWrapper>
        {previous ? (
          <Tooltip title={pageLabel(previous, page - 1, t)} placement="right">
            <IconButton
              onClick={() => goTo(page - 1)}
              aria-label={t("previousPage")}
              size="large"
              sx={{ ...arrowSx, left: { xs: 4, sm: 16 } }}
            >
              <ChevronLeftIcon fontSize="large" />
            </IconButton>
          </Tooltip>
        ) : null}
        {next ? (
          <Tooltip title={pageLabel(next, page + 1, t)} placement="left">
            <IconButton
              onClick={() => goTo(page + 1)}
              aria-label={t("nextPage")}
              size="large"
              sx={{ ...arrowSx, right: { xs: 4, sm: 16 } }}
            >
              <ChevronRightIcon fontSize="large" />
            </IconButton>
          </Tooltip>
        ) : null}
        {loading ? (
          <Box
            sx={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              pointerEvents: "none",
              zIndex: 3,
            }}
          >
            <CircularProgress aria-label={t("loading")} />
          </Box>
        ) : null}
        {/* Per-page controls, floating over the top-right of the image — they
            all act on the page currently shown (each page is its own `Source`).
            The admin row sits on the first line; download/print on a second line
            so neither grows too wide. The admin row is shown only for a
            multi-page source: when the source is already just a single page,
            linking to "the source of this page" would point back at the page
            being viewed, so — like the Django frontend — that row (and its
            permalink) is omitted. */}
        <Stack
          spacing={0.5}
          sx={{
            position: "absolute",
            top: 8,
            right: 8,
            zIndex: 2,
            alignItems: "flex-end",
          }}
        >
          {images.length > 1 ? (
            <Stack
              direction="row"
              spacing={0.5}
              sx={{ ...pillSx, alignItems: "flex-start" }}
            >
              <DetailAdminBar {...image.admin} />
              <Tooltip title={t("pageSource")}>
                <IconButton
                  component={OurLink}
                  href={`${SOURCES_BASE}/id/${image.id}/`}
                  aria-label={t("pageSource")}
                >
                  <LinkIcon />
                </IconButton>
              </Tooltip>
            </Stack>
          ) : null}
          <Stack direction="row" spacing={0.5} sx={pillSx}>
            <Tooltip title={t("download")}>
              <IconButton
                component="a"
                href={image.url}
                download={fileName(image.url)}
                aria-label={t("download")}
              >
                <DownloadIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title={t("print")}>
              <IconButton onClick={handlePrint} aria-label={t("print")}>
                <PrintIcon />
              </IconButton>
            </Tooltip>
          </Stack>
        </Stack>
      </Box>
      {images.length > 1 ? (
        <Stack
          direction="row"
          alignItems="center"
          spacing={2}
          sx={{ px: 2 }}
        >
          <Slider
            value={page + 1}
            min={1}
            max={images.length}
            onChange={(_, value) => goTo((value as number) - 1)}
            aria-label={t("goToPage")}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) =>
              pageLabel(images[value - 1], value - 1, t)
            }
            sx={{ flex: 1 }}
          />
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ whiteSpace: "nowrap", minWidth: "4ch", textAlign: "right" }}
          >
            {page + 1} / {images.length}
          </Typography>
        </Stack>
      ) : null}
      <Box
        ref={relatedRef}
        sx={{ mt: 3, minHeight: relatedMinHeight || undefined }}
      >
        {image.related.length > 0 ? (
          <EntityChipList entities={image.related} justifyContent="center" />
        ) : null}
      </Box>
    </Stack>
  );
}
