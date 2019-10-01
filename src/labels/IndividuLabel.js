import React from 'react';
import PropTypes from 'prop-types';
import {computed} from "mobx";
import {observer} from "mobx-react";

import Individu from "../models/Individu";


@observer
class IndividuLabel extends React.Component {
  static propTypes = {
    id: PropTypes.number.isRequired,
  };

  @computed
  get individu() {
    return Individu.getById(this.props.id);
  }

  render() {
    if (this.individu === null || !this.individu.loaded) {
      return null;
    }
    return (
      <span dangerouslySetInnerHTML={{__html: this.individu.html}} />
    );
  }
}


export default IndividuLabel;
