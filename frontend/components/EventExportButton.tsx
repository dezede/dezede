"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Snackbar from "@mui/material/Snackbar";
import Tooltip from "@mui/material/Tooltip";
import DownloadIcon from "@mui/icons-material/Download";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { apiPost, ApiPostError } from "@/app/api";
import { useUpdateSearchParams } from "@/app/hooks";

const EXPORT_MESSAGE_KEYS: Record<string, string> = {
  export_started: "dossiers.exportStarted",
  export_in_progress: "dossiers.exportInProgress",
  export_not_authenticated: "dossiers.exportNotAuthenticated",
  export_no_permission: "dossiers.exportNoPermission",
  export_unavailable: "dossiers.exportUnavailable",
};

/**
 * Export-as menu (CSV / XLSX / JSON) for the event list. POSTs to the DRF
 * export action carrying the current filters as query params; the backend
 * enqueues an RQ job and emails the result. Feedback is shown in a snackbar
 * so the user stays on the Next.js page.
 */
export default function EventExportButton({
  isAuthenticated,
}: {
  isAuthenticated: boolean;
}) {
  const t = useTranslations("event");
  const tPages = useTranslations("pages");
  const { searchParams } = useUpdateSearchParams();
  const [exportAnchor, setExportAnchor] = useState<null | HTMLElement>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const localise = (code?: string, format?: string): string => {
    const key = code ? EXPORT_MESSAGE_KEYS[code] : undefined;
    if (key) {
      return tPages(key, { format: format ?? "" });
    }
    return tPages("dossiers.exportError");
  };

  const handleExport = async (format: string) => {
    setExportAnchor(null);
    setBusy(true);
    try {
      const query = searchParams.toString();
      const url = `/api/evenements/export/${query ? `?${query}` : ""}`;
      const { code, format: fmt } = await apiPost<{
        code?: string;
        format?: string;
      }>(url, { format });
      setMessage(localise(code, fmt));
    } catch (error) {
      setMessage(localise(error instanceof ApiPostError ? error.code : undefined));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <Tooltip title={isAuthenticated ? "" : t("loginRequired")}>
        <Box>
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadIcon />}
            endIcon={<ArrowDropDownIcon />}
            disabled={!isAuthenticated || busy}
            onClick={(event) => setExportAnchor(event.currentTarget)}
            sx={{ height: 40, fontSize: "0.875rem" }}
          >
            {t("export")}
          </Button>
        </Box>
      </Tooltip>
      <Menu
        anchorEl={exportAnchor}
        open={Boolean(exportAnchor)}
        onClose={() => setExportAnchor(null)}
      >
        {["csv", "xlsx", "json"].map((format) => (
          <MenuItem key={format} onClick={() => handleExport(format)}>
            {format.toUpperCase()}
          </MenuItem>
        ))}
      </Menu>
      <Snackbar
        open={message !== null}
        autoHideDuration={6000}
        onClose={() => setMessage(null)}
        message={message}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      />
    </>
  );
}
