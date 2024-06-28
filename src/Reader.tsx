import React, {
  type CSSProperties,
  Suspense,
  useCallback,
  useMemo,
  useState,
  useEffect,
} from "react";
import Cropper from "react-easy-crop";
import Grid from "@mui/material/Grid";
import Fade from "@mui/material/Fade";
import Slider from "@mui/material/Slider";
import Fab from "@mui/material/Fab";
import Tooltip from "@mui/material/Tooltip";
import Button from "@mui/material/Button";
import { useTheme } from "@mui/material/styles";
import Skeleton from "@mui/material/Skeleton";
import NavigateBeforeIcon from "@mui/icons-material/NavigateBefore";
import NavigateNextIcon from "@mui/icons-material/NavigateNext";
import GetAppIcon from "@mui/icons-material/GetApp";
import PrintIcon from "@mui/icons-material/Print";
import ModelToolbar from "./ModelToolbar";
import {
  type Ensemble,
  type Evenement,
  type Individu,
  type Lieu,
  type Oeuvre,
  type Partie,
  type Source,
} from "./types";
import { useTranslation } from "react-i18next";
import { preloadApi, useApi } from "./hooks";
import ModelChip from "./ModelChip";
import { unstable_serialize, useSWRConfig } from "swr";
import { type SxProps } from "@mui/system";

function Related({ source }: { source: Source | undefined }) {
  const fallback = (
    <Grid item xs={12}>
      <Fade in>
        <Skeleton variant="rectangular" width="100%" height="48px" />
      </Fade>
    </Grid>
  );

  if (!source) {
    return fallback;
  }
  return (
    <Suspense fallback={fallback}>
      {source.individus.map((id) => (
        <Grid item key={id}>
          <ModelChip<Individu> apiName="individus" id={id} />
        </Grid>
      ))}
      {source.oeuvres.map((id) => (
        <Grid item key={id}>
          <ModelChip<Oeuvre> apiName="oeuvres" id={id} />
        </Grid>
      ))}
      {source.parties.map((id) => (
        <Grid item key={id}>
          <ModelChip<Partie> apiName="parties" id={id} />
        </Grid>
      ))}
      {source.lieux.map((id) => (
        <Grid item key={id}>
          <ModelChip<Lieu> apiName="lieux" id={id} />
        </Grid>
      ))}
      {source.evenements.map((id) => (
        <Grid item key={id}>
          <ModelChip<Evenement> apiName="evenements" id={id} />
        </Grid>
      ))}
      {source.ensembles.map((id) => (
        <Grid item key={id}>
          <ModelChip<Ensemble> apiName="ensembles" id={id} />
        </Grid>
      ))}
    </Suspense>
  );
}

function prefetchRelated(source: Source) {
  source.individus.map(async (id) => await preloadApi("individus", id));
  source.oeuvres.map(async (id) => await preloadApi("oeuvres", id));
  source.parties.map(async (id) => await preloadApi("parties", id));
  source.lieux.map(async (id) => await preloadApi("lieux", id));
  source.evenements.map(async (id) => await preloadApi("evenements", id));
  source.ensembles.map(async (id) => await preloadApi("ensembles", id));
}

export default function Reader({ sourceId }: { sourceId: number }) {
  const theme = useTheme();
  const { cache } = useSWRConfig();
  const { t } = useTranslation(["base", "source"]);

  const [sliderPosition, setSliderPosition] = useState(0);
  const [position, setPosition] = useState(0);
  const [hover, setHover] = useState(true);
  const [zoom, setZoom] = useState(1.0);
  const [crop, setCrop] = useState({ x: 0, y: 0 });

  const { data: source } = useApi<Source>("sources", sourceId);

  const isImage = source?.type_fichier === 1 && source.children.length === 0;

  const numPages = useMemo(() => {
    if (!source || isImage) {
      return 1;
    }
    return source.children.length;
  }, [isImage, source]);

  const isAtStart = useMemo(() => position <= 0, [position]);
  const isAtEnd = useMemo(() => position >= numPages - 1, [numPages, position]);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setPosition(sliderPosition);
    }, 400);
    return () => {
      clearTimeout(timeout);
    };
  }, [sliderPosition]);

  const getCachedChild = useCallback(
    (childId: number | undefined) => {
      return cache.get(unstable_serialize(["sources", childId]))?.data as
        | Source
        | undefined;
    },
    [cache],
  );

  const { data: actualChild, isLoading: isChildLoading } = useApi<Source>(
    "sources",
    source?.children[position],
  );

  // Prefetches the previous page.
  useApi<Source>(
    "sources",
    !isAtStart ? source?.children[position - 1] : undefined,
    {
      onSuccess: (data) => {
        prefetchRelated(data);
      },
    },
  );
  // Prefetches the next page.
  useApi<Source>(
    "sources",
    !isAtEnd ? source?.children[position + 1] : undefined,
    {
      onSuccess: (data) => {
        prefetchRelated(data);
      },
    },
  );

  const child = useMemo(() => {
    if (!source) {
      return undefined;
    }
    if (isImage) {
      return source;
    }
    return actualChild;
  }, [actualChild, isImage, source]);

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
  }, [child, zoom]);

  const move = useCallback(
    (newSliderPosition) => {
      if (newSliderPosition < 0) {
        newSliderPosition = 0;
      } else if (newSliderPosition >= numPages) {
        newSliderPosition = numPages - 1;
      }
      if (!Number.isNaN(newSliderPosition)) {
        setSliderPosition(newSliderPosition);
      }
    },
    [numPages],
  );

  const prev = useCallback(
    (event) => {
      event.preventDefault();
      move(position - 1);
    },
    [move, position],
  );

  const next = useCallback(
    (event) => {
      event.preventDefault();
      move(position + 1);
    },
    [move, position],
  );

  const changePage = useCallback(
    (event, newValue) => {
      move(newValue - 1);
    },
    [move],
  );

  const onMouseEnter = useCallback(() => {
    setHover(true);
  }, []);

  const onMouseLeave = useCallback(() => {
    setHover(false);
  }, []);

  const onCropChange = useCallback(
    (crop) => {
      if (zoom === 1.0) {
        crop = { x: 0, y: 0 };
      }
      setCrop(crop);
    },
    [zoom],
  );

  const onZoomChange = useCallback((zoom) => {
    setZoom(zoom);
  }, []);

  const onZoomInit = useCallback(() => {
    setZoom(1.25);
  }, []);

  const getPageName = useCallback(
    (position) => {
      const child = getCachedChild(source?.children[position]);
      if (child) {
        if (child.folio) {
          return `f. ${child.folio}`; // eslint-disable-line no-irregular-whitespace
        }
        if (child.page) {
          return `p. ${child.page}`; // eslint-disable-line no-irregular-whitespace
        }
      }
      return (position + 1).toString();
    },
    [getCachedChild, source?.children],
  );

  const print = useCallback(() => {
    if (!child) {
      return;
    }
    const popup = window.open();
    if (popup) {
      // We add a 200 ms delay before triggering print,
      // otherwise it does not work on Chrome currently.
      popup.document.write(
        "<html><head>" +
          "<style>img { max-width: 100%; max-height: 100%; }</style>" +
          "</head><body>" +
          `<img src="${child.fichier}"` +
          ' onload="setTimeout(function () {' +
          "window.print(); window.close();" +
          '}, 200);" /></body></html>',
      );
      popup.focus();
    }
  }, [child]);

  const containerStyle: CSSProperties = {
    height: "100%",
    outline: "none",
    textAlign: "center",
  };

  const imageContent = useMemo(() => {
    if (!imageSrc || !child?.fichier) {
      return null;
    }

    const directionsStyle: SxProps = {
      position: "absolute",
      top: "50%",
      transform: "translateY(-50%)",
      backgroundColor: "white",
      boxShadow: "none",
      border: "1px solid rgba(0, 0, 0, 0.23)",
      zIndex: theme.zIndex.mobileStepper,
      "&:hover, &:active, &:focus": {
        backgroundColor: "rgba(235, 235, 235)",
        boxShadow: "none",
      },
    };

    return (
      <>
        {zoom === 1.0 ? (
          <img
            src={imageSrc}
            onClick={onZoomInit}
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              cursor: "zoom-in",
              maxWidth: "100%",
              maxHeight: "100%",
              userSelect: "none",
            }}
          />
        ) : (
          <Cropper
            style={{
              cropAreaStyle: { display: "none" },
            }}
            image={imageSrc}
            showGrid={false}
            aspect={16 / 9}
            zoom={zoom}
            crop={crop}
            maxZoom={10}
            onZoomChange={onZoomChange}
            onCropChange={onCropChange}
          />
        )}
        <Fade in={hover && !isAtStart}>
          {/* Div is required, otherwise MUI crashes. */}
          <div>
            <Fab
              onClick={prev}
              sx={{
                ...directionsStyle,
                left: theme.spacing(2),
              }}
            >
              <NavigateBeforeIcon />
            </Fab>
          </div>
        </Fade>
        <Fade in={hover && !isAtEnd}>
          {/* Div is required, otherwise MUI crashes. */}
          <div>
            <Fab
              onClick={next}
              sx={{
                ...directionsStyle,
                right: theme.spacing(2),
              }}
            >
              <NavigateNextIcon />
            </Fab>
          </div>
        </Fade>
        <Fade in={hover && !isImage}>
          {/* Div is required, otherwise MUI crashes. */}
          <div>
            <ModelToolbar
              instance={child}
              style={{
                position: "absolute",
                right: theme.spacing(2),
                top: theme.spacing(2),
                justifyContent: "flex-end",
                zIndex: theme.zIndex.mobileStepper,
              }}
              extraButtons={[
                <Tooltip key="download" title={t("source:download")}>
                  <Button
                    component="a"
                    href={child.fichier}
                    download={child.fichier.replace(/^.*[\\/]/, "")}
                  >
                    <GetAppIcon />
                  </Button>
                </Tooltip>,
                <Tooltip key="print" title={t("source:print")}>
                  <Button onClick={print}>
                    <PrintIcon />
                  </Button>
                </Tooltip>,
              ]}
            />
          </div>
        </Fade>
      </>
    );
  }, [
    child,
    crop,
    hover,
    imageSrc,
    isAtEnd,
    isAtStart,
    isImage,
    next,
    onCropChange,
    onZoomChange,
    onZoomInit,
    prev,
    print,
    t,
    theme,
    zoom,
  ]);

  return (
    <Grid
      container
      direction="column"
      wrap="nowrap"
      rowSpacing={2}
      style={containerStyle}
    >
      <Grid
        item
        xs={12}
        style={{
          position: "relative",
          minHeight: theme.spacing(30),
          flexBasis: `calc(100vh - ${theme.spacing(24)})`,
        }}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
      >
        {isChildLoading ? (
          <Fade in>
            <Skeleton
              variant="rectangular"
              width="100%"
              height="100%"
              style={{
                position: "absolute",
              }}
            />
          </Fade>
        ) : (
          imageContent
        )}
      </Grid>
      {numPages <= 1 ? null : (
        <Grid item>
          <Slider
            value={sliderPosition + 1}
            min={1}
            max={numPages}
            getAriaLabel={getPageName}
            marks={[
              { value: sliderPosition + 1, label: getPageName(sliderPosition) },
            ]}
            style={{
              width: `calc(100% - ${theme.spacing(8)})`,
            }}
            onChange={changePage}
          />
        </Grid>
      )}
      <Grid item>
        <Grid container spacing={2} justifyContent="center">
          <Related source={child} />
        </Grid>
      </Grid>
    </Grid>
  );
}
