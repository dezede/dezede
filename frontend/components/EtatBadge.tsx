import Alert from "@mui/material/Alert";
import { TEtat } from "@/app/types";
import RichText from "./RichText";

/**
 * Surfaces an authority's publication-state notice — the Django
 * `include/etat.html` info alert, shown only when the état carries a message.
 * (The "Privé" padlock for unpublished records lives in `DetailAdminBar`,
 * mirroring `routines/lock.html`.)
 */
export default function EtatBadge({ etat }: { etat: TEtat | null }) {
  if (etat == null || !etat.message) {
    return null;
  }
  return (
    <Alert
      severity="info"
      sx={{
        // The état message is wrapped in a `<p>`; strip its default browser
        // margins so the text aligns with the top-anchored info icon and the
        // alert stays compact instead of inheriting paragraph spacing.
        "& p": { margin: 0 },
      }}
    >
      <RichText value={etat.message} />
    </Alert>
  );
}
