import React, {
  CSSProperties, Suspense,
  useCallback,
  useMemo,
  useState
} from 'react';
import Cropper from "react-easy-crop";
import Grid from "@material-ui/core/Grid";
import Fade from "@material-ui/core/Fade";
import Slider from "@material-ui/core/Slider";
import Fab from "@material-ui/core/Fab";
import Tooltip from "@material-ui/core/Tooltip";
import Button from "@material-ui/core/Button";
import { useTheme } from '@material-ui/core/styles';
import Skeleton from "@material-ui/lab/Skeleton";
import NavigateBeforeIcon from "@material-ui/icons/NavigateBefore";
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import GetAppIcon from '@material-ui/icons/GetApp';
import PrintIcon from '@material-ui/icons/Print';
import ModelToolbar from './ModelToolbar';
import {
  Ensemble,
  Evenement,
  Individu,
  Lieu,
  Oeuvre,
  Partie,
  Source
} from './types';
import { useTranslation } from 'react-i18next';
import { preloadApi, useApi } from './hooks';
import ModelChip from './ModelChip';
import { unstable_serialize, useSWRConfig } from 'swr';


function prefetchRelated(source: Source) {
  source.individus.map(id => preloadApi("individus", id));
  source.oeuvres.map(id => preloadApi("oeuvres", id));
  source.parties.map(id => preloadApi("parties", id));
  source.lieux.map(id => preloadApi("lieux", id));
  source.evenements.map(id => preloadApi("evenements", id));
  source.ensembles.map(id => preloadApi("ensembles", id));
}


export default function Reader({sourceId}: {sourceId: number}) {
  const theme = useTheme();
  const { cache } = useSWRConfig();
  const { t } = useTranslation(['base', 'source']);

  const [position, setPosition] = useState(0);
  const [hover, setHover] = useState(true);
  const [zoom, setZoom] = useState(1.0);
  const [crop, setCrop] = useState({x: 0, y: 0});

  const { data: source } = useApi<Source>("sources", sourceId);

  const isImage = source?.type_fichier === 1 && source.children.length === 0;

  const numPages = useMemo(() => {
    if (!source || isImage) {
      return 1;
    }
    return source.children.length;
  }, []);

  const isAtStart = useMemo(() => position <= 0, []);
  const isAtEnd = useMemo(() => position >= numPages - 1, []);

  const getCachedChild = useCallback((childId: number | undefined) => {
    return cache.get(unstable_serialize(["sources", childId])) as Source | undefined;
  }, []);

  const { data: actualChild, isLoading: isChildLoading } = useApi<Source>("sources", source?.children[position]);

  // Prefetches the previous page.
  useApi<Source>("sources", !isAtStart ? source?.children[position - 1] : undefined, {
    onSuccess: (data) => prefetchRelated(data),
  });
  // Prefetches the next page.
  useApi<Source>("sources", !isAtEnd ? source?.children[position + 1] : undefined, {
    onSuccess: (data) => prefetchRelated(data),
  });

  const child = useMemo(() => {
    if (!source) {
      return undefined;
    }
    if (isImage) {
      return source;
    }
    return actualChild;
  }, []);

  const imageSrc = useMemo(() => {
    if (!child) {
      return null;
    }
    if (zoom >= 5.0) {
      return child.fichier;
    }
    if (zoom >= 2.0) {
      return child.medium_thumbnail;
    }
    return child.small_thumbnail;
  }, []);

  const move = useCallback((newPosition) => {
    if (newPosition < 0) {
      newPosition = 0;
    } else if (newPosition >= numPages) {
      newPosition = numPages - 1;
    }
    if (!Number.isNaN(newPosition)) {
      setPosition(newPosition);
    }
  }, []);

  const prev = useCallback((event) => {
    event.preventDefault();
    move(position - 1);
  }, []);

  const next = useCallback((event) => {
    event.preventDefault();
    move(position + 1);
  }, []);

  const changePage = useCallback((event, newValue) => {
    move(newValue - 1);
  }, []);

  const onMouseEnter = useCallback(() => {
    setHover(true);
  }, []);

  const onMouseLeave = useCallback(() => {
    setHover(false);
  }, []);

  const onCropChange = useCallback(crop => {
    if (zoom === 1.0) {
      crop = {x: 0, y: 0};
    }
    setCrop(crop);
  }, []);

  const onZoomChange = useCallback(zoom => {
    setZoom(zoom);
  }, []);

  const onZoomInit = useCallback(() => {
    setZoom(1.25);
  }, []);

  const getPageName = useCallback(position => {
    const child = getCachedChild(source?.children[position]);
    if (child) {
      if (child.folio) {
        return `f. ${child.folio}`;
      }
      if (child.page) {
        return `p. ${child.page}`;
      }
    }
    return (position + 1).toString();
  }, []);

  const print = useCallback(() => {
    if (!child) {
      return;
    }
    const popup = window.open();
    if (popup) {
      popup.document.write(
        '<html><head>'
        + '<style>img { max-width: 100%; max-height: 100%; }</style>'
        + '</head><body>'
        + `<img src="${child.fichier}"`
        + ' onload="window.print(); window.close();" /></body></html>'
      );
    }
  }, []);

  const containerStyle: CSSProperties = {
    outline: 'none',
    textAlign: 'center',
  };

  const directionsStyle: CSSProperties = {
    position: 'absolute',
    top: '50%',
    transform: 'translateY(-50%)',
    backgroundColor: 'white',
    boxShadow: 'none',
    border: '1px solid rgba(0, 0, 0, 0.23)',
    zIndex: theme.zIndex.mobileStepper,
    '&:hover, &:active, &:focus': {
      backgroundColor: 'rgba(235, 235, 235)',
      boxShadow: 'none',
    }
  };

  if (!source || !child || !imageSrc || !child.fichier) {
    return <Skeleton variant="rect" style={containerStyle} />;
  }

  const imageContent = (
    <>
      {
        zoom === 1.0
          ? <img src={imageSrc} onClick={onZoomInit}
                 style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    cursor: 'zoom-in',
                    maxWidth: '100%',
                    maxHeight: '100%',
                    userSelect: 'none',
                  }} />
          : (
            <Cropper style={{
              cropAreaStyle: { display: "none" },
            }}
                     image={imageSrc} showGrid={false} aspect={16/9}
                     zoom={zoom} crop={crop} maxZoom={10}
                     onZoomChange={onZoomChange}
                     onCropChange={onCropChange} />
          )
      }
      <Fade in={hover && !isAtStart}>
        <div> {/* Div prevents Fade from overwriting Fab transition. */}
          <Fab onClick={prev}
               style={{
                 ...directionsStyle,
                 left: theme.spacing(2),
               }}
          >
            <NavigateBeforeIcon />
          </Fab>
        </div>
      </Fade>
      <Fade in={hover && !isAtEnd}>
        <div> {/* Div prevents Fade from overwriting Fab transition. */}
          <Fab onClick={next}
               style={{
                 ...directionsStyle,
                 right: theme.spacing(2),
               }}
          >
            <NavigateNextIcon />
          </Fab>
        </div>
      </Fade>
      <Fade in={hover && !isImage}>
        <ModelToolbar
          instance={child} style={{
            position: 'absolute',
            right: theme.spacing(2),
            top: theme.spacing(2),
            zIndex: theme.zIndex.mobileStepper,
          }} justify="flex-end"
          extraButtons={
            [
              <Tooltip key="download" title={t('source:download')}>
                <Button component="a" href={child.fichier}
                        download={child.fichier.replace(/^.*[\\\/]/, '')}>
                  <GetAppIcon />
                </Button>
              </Tooltip>,
              <Tooltip key="print" title={t('source:print')}>
                <Button onClick={print}>
                  <PrintIcon />
                </Button>
              </Tooltip>
            ]
          }
        />
      </Fade>
    </>
  );
  return (
    <Grid container direction="column" wrap="nowrap"
          spacing={2} style={containerStyle}>
      <Grid item xs={12} style={{
                position: 'relative',
                minHeight: theme.spacing(30),
                flexBasis: `calc(100vh - ${theme.spacing(24)}px)`,
              }}
              onMouseEnter={onMouseEnter}
              onMouseLeave={onMouseLeave}>
          {
            isChildLoading
              ? <Skeleton variant="rect" width="100%" height="100%" style={{
                  position: 'absolute',
                }} />
              : imageContent
          }
      </Grid>
      {
        numPages <= 1
          ? null
          : (
            <Grid item>
              <Slider
                value={position + 1} min={1} max={numPages}
                getAriaLabel={getPageName}
                marks={[
                  {value: position + 1, label: getPageName(position)},
                ]}
                style={{
                  width: `calc(100% - ${theme.spacing(8)}px)`,
                }}
                onChange={changePage} />
            </Grid>
          )
      }
      <Grid item>
        <Grid container spacing={2} justify="center">
          <Suspense fallback={
            <Grid item xs={12}>
              <Skeleton variant="rect" width="100%" height="48px" />
            </Grid>
          }>
            {child.individus.map(id => <Grid item key={id}><ModelChip<Individu> apiName="individus" id={id} /></Grid>)}
            {child.oeuvres.map(id => <Grid item key={id}><ModelChip<Oeuvre> apiName="oeuvres" id={id} /></Grid>)}
            {child.parties.map(id => <Grid item key={id}><ModelChip<Partie> apiName="parties" id={id} /></Grid>)}
            {child.lieux.map(id => <Grid item key={id}><ModelChip<Lieu> apiName="lieux" id={id} /></Grid>)}
            {child.evenements.map(id => <Grid item key={id}><ModelChip<Evenement> apiName="evenements" id={id} /></Grid>)}
            {child.ensembles.map(id => <Grid item key={id}><ModelChip<Ensemble> apiName="ensembles" id={id} /></Grid>)}
          </Suspense>
        </Grid>
      </Grid>
    </Grid>
  );
}
