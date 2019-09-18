import React from 'react';
import PropTypes from 'prop-types';
import {computed, observable} from "mobx";
import {observer} from "mobx-react";
import Cropper from "react-easy-crop";
import Grid from "@material-ui/core/Grid";
import Chip from "@material-ui/core/Chip";
import Fade from "@material-ui/core/Fade";
import Slider from "@material-ui/core/Slider";
import Fab from "@material-ui/core/Fab";
import Tooltip from "@material-ui/core/Tooltip";
import Button from "@material-ui/core/Button";
import {withStyles} from "@material-ui/styles";
import Skeleton from "@material-ui/lab/Skeleton";
import NavigateBeforeIcon from "@material-ui/icons/NavigateBefore";
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import GetAppIcon from '@material-ui/icons/GetApp';
import PrintIcon from '@material-ui/icons/Print';
import ModelToolbar from './ModelToolbar';
import Source from './models/Source';
import strings from './strings';


const styles = theme => ({
  container: {
    outline: 'none',
    minHeight: '500px',
    height: '80vh',
    textAlign: 'center',
  },
  imageContainer: {
    position: 'relative',
  },
  imageSubContainer: {
    position: 'relative',
    height: '100%',
  },
  unzoomedImage: {
    cursor: 'zoom-in',
  },
  cropper: {
    display: 'none',
  },
  image: {
    width: '100%',
    height: '100%'
  },
  directions: {
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
  },
  prev: {
    left: theme.spacing(2),
  },
  next: {
    right: theme.spacing(2),
  },
  tools: {
    position: 'absolute',
    right: theme.spacing(2),
    top: theme.spacing(2),
    zIndex: theme.zIndex.mobileStepper,
  },
  linkedSkeleton: {
    width: '100%',
    height: '48px',
  },
  pageField: {
    maxWidth: '250px',
    textAlign: 'right',
  }
});


@withStyles(styles)
@observer
class Reader extends React.Component {
  @observable position = 0;
  @observable hover = true;
  @observable zoom = 1.0;
  @observable crop = {x: 0, y: 0};

  static propTypes = {
    sourceId: PropTypes.number.isRequired,
  };

  constructor(props) {
    super(props);
    this.source = Source.getById(this.props.sourceId);
  }

  get sourceIsImage() {
    return this.source.type_fichier === 1 && this.source.children.length === 0;
  }

  @computed get numPages() {
    if (this.sourceIsImage) {
      return 1;
    }
    return this.source.children.length;
  }

  @computed get isAtStart() {
    return this.position <= 0;
  }

  @computed get isAtEnd() {
    return this.position >= this.numPages - 1;
  }

  getLinkedObjects(child) {
    return [
      ...child.individusList,
      ...child.oeuvresList,
      ...child.evenementsList,
      ...child.ensemblesList,
      ...child.lieuxList,
      ...child.partiesList,
    ];
  }

  get linkedObjects() {
    return this.getLinkedObjects(this.child);
  }

  @computed get fullyLoaded() {
    return (
      this.child.loaded
      && this.linkedObjects.every(instance => instance.loaded)
    );
  }

  prefetch = position => {
    const child = this.source.getChild(position);
    if (child) {
      this.getLinkedObjects(child);
    }
  };

  @computed get child() {
    if (this.sourceIsImage) {
      return this.source;
    }
    if (!this.isAtStart) {
      // Prefetches the previous page.
      this.prefetch(this.position - 1);
    }
    if (!this.isAtEnd) {
      // Prefetches the next page.
      this.prefetch(this.position + 1);
    }
    return this.source.getChild(this.position);
  }

  @computed get imageSrc() {
    if (this.zoom >= 5.0) {
      return this.child.fichier;
    }
    if (this.zoom >= 2.0) {
      return this.child.medium_thumbnail;
    }
    return this.child.small_thumbnail;
  }

  move = (newPosition) => {
    const {position} = this;
    if (newPosition < 0) {
      newPosition = 0;
    } else if (newPosition >= this.numPages) {
      newPosition = this.numPages - 1;
    }
    if ((newPosition !== position) && !Number.isNaN(newPosition)) {
      this.position = newPosition;
    }
  };

  prev = (event) => {
    event.preventDefault();
    this.move(this.position - 1);
  };

  next = (event) => {
    event.preventDefault();
    this.move(this.position + 1);
  };

  changePage = (event, newValue) => {
    this.move(newValue - 1);
  };

  onKeyDown = event => {
    switch (event.keyCode) {
      case 37: // Left
        this.prev(event);
        break;
      case 39: // Right
        this.next(event);
        break;
      case 33: // Page up
        this.move(this.position - 10);
        break;
      case 34: // Page down
        this.move(this.position + 10);
        break;
      case 36: // Origin
        this.move(0);
        break;
      case 35: // End
        this.move(this.numPages - 1);
        break;
    }
  };

  onMouseEnter = () => {
    this.hover = true;
  };

  onMouseLeave = () => {
    this.hover = false;
  };

  onCropChange = crop => {
    if (this.zoom === 1.0) {
      crop = {x: 0, y: 0};
    }
    this.crop = crop;
  };

  onZoomChange = zoom => {
    this.zoom = zoom;
  };

  onZoomInit = () => {
    this.zoom = 1.25;
  };

  getPageName = position => {
    const child = this.source.getChild(position);
    if (child.folio) {
      return `Folio ${child.folio}`;
    }
    return (position + 1).toString();
  };

  print = () => {
    const popup = window.open();
    popup.document.write(
      '<html><head>'
      + '<style>img { max-width: 100%; max-height: 100%; }</style>'
      + '</head><body>'
      + `<img src="${this.child.fichier}"`
      + ' onload="window.print(); window.close();" /></body></html>'
    );
  };

  render() {
    const {classes} = this.props;
    const {position} = this;
    if (!this.child) {
      return <Skeleton variant="rect" className={classes.container} />;
    }
    const imageContent = (
      <>
        <Fade in={this.hover && !this.isAtStart}>
          <div> {/* Div prevents Fade from overwriting Fab transition. */}
            <Fab onClick={this.prev}
                 className={`${classes.directions} ${classes.prev}`}>
              <NavigateBeforeIcon />
            </Fab>
          </div>
        </Fade>
        <Fade in={this.hover && !this.isAtEnd}>
          <div> {/* Div prevents Fade from overwriting Fab transition. */}
            <Fab onClick={this.next}
                 className={`${classes.directions} ${classes.next}`}>
              <NavigateNextIcon />
            </Fab>
          </div>
        </Fade>
        <Fade in={this.hover && !this.sourceIsImage}>
          <ModelToolbar
            instance={this.child} className={classes.tools} justify="flex-end"
            extraButtons={
              [
                <Tooltip key="download" title={strings.download}>
                  <Button component="a" href={this.child.fichier}
                          download={this.child.nomFichier}>
                    <GetAppIcon />
                  </Button>
                </Tooltip>,
                <Tooltip key="print" title={strings.print}>
                  <Button onClick={this.print}>
                    <PrintIcon />
                  </Button>
                </Tooltip>
              ]
            }
          />
        </Fade>
        <div className={classes.imageSubContainer}>
          {
            this.zoom === 1.0
              ? <img src={this.imageSrc} onClick={this.onZoomInit}
                     className={classes.unzoomedImage} />
              : <Cropper classes={{cropAreaClassName: classes.cropper}}
                         image={this.imageSrc} showGrid={false} aspect={16/9}
                         zoom={this.zoom} crop={this.crop} maxZoom={10}
                         onZoomChange={this.onZoomChange}
                         onCropChange={this.onCropChange} />
          }
        </div>
      </>
    );
    return (
      <Grid container direction="column" wrap="nowrap"
            spacing={2} onKeyDown={this.onKeyDown}
            tabIndex={-1}  // For key press capture.
            className={classes.container}>
        <Grid item xs={12} className={classes.imageContainer}
                onMouseEnter={this.onMouseEnter}
                onMouseLeave={this.onMouseLeave}>
            {
              this.fullyLoaded
                ? imageContent
                : <Skeleton variant="rect"
                            className={classes.imageSubContainer} />
            }
        </Grid>
        <Grid item>
          <Grid container spacing={2} justify="center">
            {
              this.fullyLoaded
                ? this.linkedObjects.map(instance => {
                    if (!instance.loaded) {
                      return null;
                    }
                    return (
                      <Grid item key={instance.key}>
                        <Chip label={instance.toString()}
                              clickable component="a"
                              href={instance.front_url}/>
                      </Grid>
                    );
                  })
                : (
                  <Grid item xs={12}>
                    <Skeleton variant="rect"
                              className={classes.linkedSkeleton} />
                  </Grid>
                )
            }
          </Grid>
        </Grid>
        {
          this.numPages <= 1
            ? null
            : (
              <Grid item>
                <Slider
                  value={position + 1} min={1} step={1}
                  getAriaLabel={value => this.source.getChild(value).folio}
                  marks={[
                    {value: position + 1, label: this.getPageName(position)},
                  ]}
                  max={this.numPages}
                  onChange={this.changePage} />
              </Grid>
            )
        }
      </Grid>
    );
  }
}

export default Reader;
