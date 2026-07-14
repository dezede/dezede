"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Dialog from "@mui/material/Dialog";
import DialogContent from "@mui/material/DialogContent";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import CircularProgress from "@mui/material/CircularProgress";
import CloseIcon from "@mui/icons-material/Close";
import LaunchIcon from "@mui/icons-material/Launch";
import { useTranslations } from "next-intl";
import { apiGet } from "@/app/api";
import { ENTITIES } from "@/app/entities";
import { TSourceDetail } from "@/app/types";
import OurLink from "@/components/OurLink";
import SourceDetailContent from "@/components/SourceDetailContent";
import RelatedEventsClient from "@/components/RelatedEventsClient";

// Context exposing a single `openSource(id)` opener, fulfilled by
// `SourceModalProvider`. A no-op default keeps `useSourceModal()` safe in
// subtrees that aren't wrapped by the provider (the call simply does nothing).
const SourceModalContext = createContext<(id: number) => void>(() => {});

export function useSourceModal(): (id: number) => void {
  return useContext(SourceModalContext);
}

/**
 * Provides the in-place source popup for the whole site: an event's related
 * sources open here instead of navigating away (the modern counterpart of the
 * legacy Django Bootstrap source modal). Holds the requested source id, fetches
 * its full detail on demand and renders it — Présentation / Consulter / Index
 * tabs — inside an MUI Dialog. Mounted once, around the site shell.
 */
export function SourceModalProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const t = useTranslations("source");
  const [sourceId, setSourceId] = useState<number | null>(null);
  const [source, setSource] = useState<TSourceDetail | null>(null);
  const [error, setError] = useState(false);

  const openSource = useCallback((id: number) => {
    setSourceId(id);
  }, []);

  // Fetch whenever a new source is requested. The already-loaded source is
  // reused on re-open; switching to a different source shows the spinner until
  // its detail arrives (the content render below gates on a matching id).
  useEffect(() => {
    if (sourceId === null || source?.id === sourceId) {
      return;
    }
    const controller = new AbortController();
    const load = async () => {
      setError(false);
      try {
        const data = await apiGet<TSourceDetail>(
          `${ENTITIES.sources.apiList}${sourceId}/`,
          { signal: controller.signal },
        );
        setSource(data);
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") {
          return;
        }
        setError(true);
      }
    };
    load();
    return () => controller.abort();
  }, [sourceId, source?.id]);

  const close = () => setSourceId(null);

  // The source to show: the loaded one, unless we're switching to a *different*
  // id (then show the spinner instead of flashing the previous source). While
  // closing (`sourceId === null`) the last source stays visible through the
  // dialog's fade-out rather than collapsing to a spinner.
  const displaySource =
    !error && source !== null && (sourceId === null || source.id === sourceId)
      ? source
      : null;

  return (
    <SourceModalContext.Provider value={openSource}>
      {children}
      <Dialog
        open={sourceId !== null}
        onClose={close}
        maxWidth="lg"
        fullWidth
        scroll="body"
        slotProps={{ paper: { sx: { minHeight: "90vh" } } }}
        aria-labelledby="source-modal-title"
        aria-describedby="source-modal-content"
      >
        <Stack
          direction="row"
          spacing={1}
          sx={{
            alignItems: "flex-start",
            justifyContent: "space-between",
            px: 3,
            py: 2,
          }}
        >
          {displaySource ? (
            <Typography
              id="source-modal-title"
              variant="h2"
              component="h2"
              sx={{ m: 0, fontSize: "1.5rem", flexGrow: 1 }}
              dangerouslySetInnerHTML={{ __html: displaySource.pretty_title }}
            />
          ) : (
            <Box sx={{ flexGrow: 1 }} />
          )}
          <Stack direction="row" spacing={0.5} sx={{ flexShrink: 0 }}>
            {sourceId !== null ? (
              <Button
                component={OurLink}
                href={`${ENTITIES.sources.base}/id/${sourceId}/`}
                size="small"
                startIcon={<LaunchIcon fontSize="small" />}
                onClick={close}
              >
                {t("openFullPage")}
              </Button>
            ) : null}
            <IconButton aria-label={t("close")} onClick={close} size="small">
              <CloseIcon />
            </IconButton>
          </Stack>
        </Stack>
        <DialogContent id="source-modal-content">
          {error ? (
            <Typography color="error" sx={{ py: 4, textAlign: "center" }}>
              {t("loadError")}
            </Typography>
          ) : !displaySource ? (
            <Box sx={{ py: 8, display: "flex", justifyContent: "center" }}>
              <CircularProgress />
            </Box>
          ) : (
            <SourceDetailContent
              key={displaySource.id}
              source={displaySource}
              syncHash={false}
              relatedEvents={
                <RelatedEventsClient sourcePk={String(displaySource.id)} />
              }
            />
          )}
        </DialogContent>
      </Dialog>
    </SourceModalContext.Provider>
  );
}
