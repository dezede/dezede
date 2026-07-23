"use client";

import { useState } from "react";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import Snackbar from "@mui/material/Snackbar";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import IconButton from "@mui/material/IconButton";
import PictureAsPdfOutlinedIcon from "@mui/icons-material/PictureAsPdfOutlined";
import TableChartOutlinedIcon from "@mui/icons-material/TableChartOutlined";
import AddIcon from "@mui/icons-material/Add";
import DeleteOutlineIcon from "@mui/icons-material/DeleteOutlined";
import { useTranslations } from "next-intl";
import { apiPost, ApiPostError } from "@/app/api";
import { TScenarioChoice } from "@/app/types";

// Maps the API's stable response `code` to a frontend i18n key, so the snackbar
// is localised in the user's locale instead of echoing Django's French `detail`.
const EXPORT_MESSAGE_KEYS: Record<string, string> = {
  export_started: "dossiers.exportStarted",
  export_in_progress: "dossiers.exportInProgress",
  export_not_authenticated: "dossiers.exportNotAuthenticated",
  export_no_permission: "dossiers.exportNoPermission",
  export_unavailable: "dossiers.exportUnavailable",
  export_no_scenario: "dossiers.exportNoScenario",
};

/**
 * Sidebar export actions, the React counterpart of the Django dossier sidebar's
 * "Exporter en PDF" link and the superuser "Exporter les statistiques" modal
 * (`dossierdevenements_sidebar.html`). Both POST to the dossier API, which
 * enqueues an rq job and emails the result; we surface the API's localised
 * status message (success or "already in progress") in a snackbar.
 */
export default function DossierExportButtons({
  dossierId,
  canExportPdf,
  canExportStats,
  scenarioChoices,
}: {
  dossierId: number;
  canExportPdf: boolean;
  canExportStats: boolean;
  scenarioChoices: TScenarioChoice[];
}) {
  const t = useTranslations("pages");
  const [message, setMessage] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  // One entry per scenario row in the dialog; mirrors the Django formset whose
  // rows the user adds/removes. Defaults to a single row on the first choice.
  const [rows, setRows] = useState<string[]>([scenarioChoices[0]?.value ?? ""]);

  // Localise an API export response (success or error) from its stable `code`,
  // falling back to the server's `detail` and then to a generic error string.
  const localise = (code?: string, format?: string, detail?: string): string => {
    const key = code ? EXPORT_MESSAGE_KEYS[code] : undefined;
    if (key) {
      return t(key, { format: format ?? "" });
    }
    return detail || t("dossiers.exportError");
  };

  const post = async (path: string, body?: unknown) => {
    setBusy(true);
    try {
      const { code, format, detail } = await apiPost<{
        code?: string;
        format?: string;
        detail?: string;
      }>(path, body);
      setMessage(localise(code, format, detail));
    } catch (error) {
      if (error instanceof ApiPostError) {
        setMessage(localise(error.code, undefined, error.message));
      } else {
        setMessage(t("dossiers.exportError"));
      }
    } finally {
      setBusy(false);
    }
  };

  const exportPdf = () =>
    post(`/api/public/dossiers/${dossierId}/export_pdf/`);

  const submitScenarios = async () => {
    const scenarios = rows
      .filter(Boolean)
      .map((scenario) => ({ scenario }));
    setDialogOpen(false);
    await post(`/api/public/dossiers/${dossierId}/export_scenario/`, {
      scenarios,
    });
  };

  return (
    <>
      <Stack spacing={1}>
        {canExportPdf ? (
          <Button
            variant="outlined"
            fullWidth
            startIcon={<PictureAsPdfOutlinedIcon />}
            disabled={busy}
            onClick={exportPdf}
          >
            {t("dossiers.exportPdf")}
          </Button>
        ) : null}
        {canExportStats ? (
          <Button
            variant="outlined"
            fullWidth
            startIcon={<TableChartOutlinedIcon />}
            disabled={busy}
            onClick={() => setDialogOpen(true)}
          >
            {t("dossiers.exportStats")}
          </Button>
        ) : null}
      </Stack>

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>{t("dossiers.exportStatsTitle")}</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ mt: 1 }}>
            {rows.map((value, index) => (
              <Stack
                key={index}
                direction="row"
                spacing={1}
                sx={{ alignItems: "center" }}
              >
                <FormControl fullWidth size="small">
                  <InputLabel id={`scenario-label-${index}`}>
                    {t("dossiers.scenarioPlaceholder")}
                  </InputLabel>
                  <Select
                    labelId={`scenario-label-${index}`}
                    label={t("dossiers.scenarioPlaceholder")}
                    value={value}
                    displayEmpty
                    onChange={(event) =>
                      setRows((prev) =>
                        prev.map((row, i) =>
                          i === index ? event.target.value : row,
                        ),
                      )
                    }
                  >
                    <MenuItem value="" disabled />
                    {scenarioChoices.map((choice) => (
                      <MenuItem key={choice.value} value={choice.value}>
                        {choice.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <IconButton
                  aria-label={t("dossiers.removeScenario")}
                  disabled={rows.length < 2}
                  onClick={() =>
                    setRows((prev) => prev.filter((_, i) => i !== index))
                  }
                >
                  <DeleteOutlineIcon />
                </IconButton>
              </Stack>
            ))}
            <Button
              startIcon={<AddIcon />}
              onClick={() =>
                setRows((prev) => [...prev, scenarioChoices[0]?.value ?? ""])
              }
              sx={{ alignSelf: "flex-start" }}
            >
              {t("dossiers.addScenario")}
            </Button>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            {t("dossiers.cancel")}
          </Button>
          <Button
            variant="contained"
            disabled={busy || rows.filter(Boolean).length === 0}
            onClick={submitScenarios}
          >
            {t("dossiers.export")}
          </Button>
        </DialogActions>
      </Dialog>

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
