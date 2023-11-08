import React, { type CSSProperties } from "react";
import { useTranslation } from "react-i18next";
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import ButtonGroup from "@mui/material/ButtonGroup";
import Tooltip from "@mui/material/Tooltip";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import PersonIcon from "@mui/icons-material/Person";
import LinkIcon from "@mui/icons-material/Link";
import { type Model, type User } from "./types";
import { useApi } from "./hooks";

export default function ModelToolbar({
  instance,
  extraButtons,
  style,
}: {
  instance: Model;
  extraButtons?: React.ReactNode;
  style?: CSSProperties;
}) {
  const { t } = useTranslation("base");
  const { data: owner } = useApi<User>("users", instance.owner);

  const buttonGroupStyle = { background: "white" };

  return (
    <Grid container spacing={1} style={style}>
      <Grid item>
        <ButtonGroup variant="outlined" size="small" style={buttonGroupStyle}>
          {instance.can_change ? (
            <Tooltip title={t("base:edit")}>
              <Button component="a" href={instance.change_url}>
                <EditIcon />
              </Button>
            </Tooltip>
          ) : null}
          {instance.can_delete ? (
            <Tooltip title={t("base:delete")}>
              <Button component="a" href={instance.delete_url}>
                <DeleteIcon />
              </Button>
            </Tooltip>
          ) : null}
          {owner ? (
            <Tooltip title={owner.str}>
              <Button component="a" href={owner.front_url}>
                <PersonIcon />
              </Button>
            </Tooltip>
          ) : null}
        </ButtonGroup>
      </Grid>
      <Grid item>
        <ButtonGroup variant="outlined" size="small" style={buttonGroupStyle}>
          {extraButtons}
          <Tooltip title={t("base:permalink")}>
            <Button component="a" href={instance.front_url}>
              <LinkIcon />
            </Button>
          </Tooltip>
        </ButtonGroup>
      </Grid>
    </Grid>
  );
}
