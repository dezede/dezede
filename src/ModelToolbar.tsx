import React, { CSSProperties } from 'react';
import { useTranslation } from 'react-i18next';
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import Tooltip from "@material-ui/core/Tooltip";
import EditIcon from "@material-ui/icons/Edit";
import DeleteIcon from "@material-ui/icons/Delete";
import PersonIcon from "@material-ui/icons/Person";
import LinkIcon from "@material-ui/icons/Link";
import { Model, User } from "./types";
import { GridJustification } from '@material-ui/core/Grid/Grid';
import { useApi } from './hooks';


export default function ModelToolbar({instance, extraButtons, style, justify}: {instance: Model; extraButtons?: React.ReactNode; style?: CSSProperties; justify?: GridJustification}) {
  const { t } = useTranslation("base");
  const { data: owner } = useApi<User>("users", instance.owner);

  const buttonGroupStyle = {background: 'white'};

  return (
    <Grid container spacing={1} justify={justify} style={style}>
      <Grid item>
        <ButtonGroup variant="outlined" size="small" style={buttonGroupStyle}>
          {
            instance.can_change
              ? (
                <Tooltip title={t('base:edit')}>
                  <Button component="a" href={instance.change_url}>
                    <EditIcon />
                  </Button>
                </Tooltip>
              )
              : null
          }
          {
            instance.can_delete
              ? (
                <Tooltip title={t('base:delete')}>
                  <Button component="a" href={instance.delete_url}>
                    <DeleteIcon />
                  </Button>
                </Tooltip>
              )
              : null
          }
          {
            owner
              ? (
                <Tooltip title={owner.toString()}>
                  <Button component="a" href={owner.front_url}>
                    <PersonIcon />
                  </Button>
                </Tooltip>
              )
              : null
          }
        </ButtonGroup>
      </Grid>
      <Grid item>
        <ButtonGroup variant="outlined" size="small" style={buttonGroupStyle}>
          {extraButtons}
          <Tooltip title={t('base:permalink')}>
            <Button component="a" href={instance.front_url}>
              <LinkIcon />
            </Button>
          </Tooltip>
        </ButtonGroup>
      </Grid>
    </Grid>
  );
}
