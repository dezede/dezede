import React from 'react';
import PropTypes from 'prop-types';
import {computed} from "mobx";
import {withTranslation} from "react-i18next";
import Grid from "@material-ui/core/Grid";
import Button from "@material-ui/core/Button";
import ButtonGroup from "@material-ui/core/ButtonGroup";
import Tooltip from "@material-ui/core/Tooltip";
import {withStyles} from "@material-ui/core/styles";
import EditIcon from "@material-ui/icons/Edit";
import DeleteIcon from "@material-ui/icons/Delete";
import PersonIcon from "@material-ui/icons/Person";
import LinkIcon from "@material-ui/icons/Link";
import User from "./models/User";


const styles = theme => ({
  buttonGroup: {
    background: 'white',
  },
});


@withStyles(styles)
@withTranslation('base')
class ModelToolbar extends React.Component {
  static propTypes = {
    instance: PropTypes.any.isRequired,
    extraButtons: PropTypes.any,
    className: PropTypes.string,
    justify: PropTypes.string,
  };

  @computed get owner() {
    return User.getById(this.props.instance.owner);
  }

  render() {
    const {
      instance, extraButtons, className, justify, classes, style, t,
    } = this.props;
    return (
      <Grid container spacing={1} justify={justify} className={className}
            style={style}>
        <Grid item>
          <ButtonGroup variant="outlined" size="small"
                       className={classes.buttonGroup}>
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
              this.owner
                ? (
                  <Tooltip title={this.owner.toString()}>
                    <Button component="a" href={this.owner.front_url}>
                      <PersonIcon />
                    </Button>
                  </Tooltip>
                )
                : null
            }
          </ButtonGroup>
        </Grid>
        <Grid item>
          <ButtonGroup variant="outlined" size="small"
                       className={classes.buttonGroup}>
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
}


export default ModelToolbar;
