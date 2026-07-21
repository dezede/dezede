"use client";

import Stack from "@mui/material/Stack";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import PersonIcon from "@mui/icons-material/Person";
import LockIcon from "@mui/icons-material/Lock";
import { useTranslations } from "next-intl";
import { TAdminLink } from "@/app/types";

/**
 * The detail-page button group mirroring the Django frontend's `frontend_admin`
 * / `ownership` includes: an admin *edit* and *delete* link shown only when the
 * visitor may change/delete the object, and an *author* link to the owner's
 * profile shown to everyone (including anonymous visitors) when an owner exists.
 * An unpublished record (`is_public === false`) also shows a disabled "Privé"
 * padlock, mirroring `routines/lock.html`.
 *
 * These targets are Django routes (same origin, outside the Next.js app), so they
 * use plain `<a>` anchors for a full navigation rather than client-side routing.
 *
 * Rendered as a Client Component on purpose: MUI <Tooltip> checks
 * `React.isValidElement` on its child, and that returns inconsistent results
 * across the RSC/SSR/hydration boundary for a child element authored in a Server
 * Component — so Tooltip wraps the child in an extra <span> on only one side,
 * causing a hydration mismatch. Authoring the Tooltips here keeps both passes
 * identical.
 */
export default function DetailAdminBar({
  owner,
  is_public,
  can_change,
  can_delete,
  change_url,
  delete_url,
}: TAdminLink) {
  const t = useTranslations("detail");
  if (!owner && !can_change && !can_delete && is_public !== false) {
    return null;
  }
  return (
    <Stack direction="row" spacing={0.5} sx={{ alignItems: "flex-start" }}>
      {can_change ? (
        <Tooltip title={t("edit")}>
          <IconButton
            component="a"
            href={change_url}
            color="primary"
            aria-label={t("edit")}
          >
            <EditIcon />
          </IconButton>
        </Tooltip>
      ) : null}
      {can_delete ? (
        <Tooltip title={t("delete")}>
          <IconButton
            component="a"
            href={delete_url}
            color="error"
            aria-label={t("delete")}
          >
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      ) : null}
      {is_public === false ? (
        <Tooltip title={t("private")}>
          <span>
            <IconButton color="warning" disabled aria-label={t("private")}>
              <LockIcon />
            </IconButton>
          </span>
        </Tooltip>
      ) : null}
      {owner ? (
        <Tooltip title={t("author", { name: owner.str })}>
          <IconButton
            component="a"
            href={owner.url}
            aria-label={t("author", { name: owner.str })}
          >
            <PersonIcon />
          </IconButton>
        </Tooltip>
      ) : null}
    </Stack>
  );
}
