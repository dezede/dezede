import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import Box from '@material-ui/core/Box';
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";
import { useTheme } from '@material-ui/core/styles';
import GetAppIcon from '@material-ui/icons/GetApp';
import LaunchIcon from '@material-ui/icons/Launch';

import Reader from "./Reader";
import AuteurLabelList from "./labels/AuteurLabelList";
import { useApi } from './hooks';
import { Source } from './types';


export default function SourceView({ id }: {id: number}) {
  const theme = useTheme();
  const {t} = useTranslation("source");

  const { data: source } = useApi<Source>("sources", id);

  const isOther = source?.type_fichier === 0;

  const downloadButton = useMemo(() => {
    if (!source?.telechargement_autorise) {
      return null;
    }
    let url = source.url;
    let icon;
    let label;
    if (url) {
      icon = <LaunchIcon fontSize="small" />;
      label = t('source:originalOn', {url: new URL(url).hostname});
    } else if (isOther && source.fichier) {
      url = source.fichier;
      icon = <GetAppIcon fontSize="small" />;
      label = `${t('source:download')} (${source.taille_fichier})`;
    } else {
      return null;
    }
    return (
      <Grid item>
        <Typography align="center">
          <Button component="a" target="_blank" href={url} startIcon={icon}
                  color="primary" variant="outlined" size="small">
            {label}
          </Button>
        </Typography>
      </Grid>
    );
  }, []);

  const transcription = useMemo(() => {
    if (!source?.transcription) {
      return null;
    }
    return (
      <Grid item>
        <blockquote>
          <Box
            dangerouslySetInnerHTML={{__html: source.transcription}}
            sx={{
              fontFamily: theme.typography.fontFamily,
              // Makes sure tables in the transcription have enough space between cells.
              '& table td+td': {
                paddingLeft: theme.spacing(1),
              },
            }}
          />
          {
            source.auteurs.length > 0
              ? (
                <Box component="footer" marginTop={theme.spacing(1)}>
                  <AuteurLabelList ids={source.auteurs} />
                </Box>
              )
              : null
          }
        </blockquote>
      </Grid>
    );
  }, []);

  const reader = useMemo(() => {
    if (!source?.has_images) {
      return null;
    }
    return (
      <Grid item>
        <Reader sourceId={id} />
      </Grid>
    );
  }, []);

  return (
    <Grid container direction="column" wrap="nowrap" spacing={4}>
      {downloadButton}
      {reader}
      {transcription}
    </Grid>
  );
}
