import React from 'react';
import PropTypes from 'prop-types';
import {computed} from "mobx";
import {observer} from "mobx-react";

import Ensemble from "../models/Ensemble";


@observer
class EnsembleLabel extends React.Component {
  static propTypes = {
    id: PropTypes.number.isRequired,
  };

  @computed
  get ensemble() {
    return Ensemble.getById(this.props.id);
  }

  render() {
    if (this.ensemble === null || !this.ensemble.loaded) {
      return null;
    }
    return (
      <span dangerouslySetInnerHTML={{__html: this.ensemble.html}} />
    );
  }
}


export default EnsembleLabel;
