import React from 'react';
import PropTypes from 'prop-types';
import {computed} from "mobx";
import {observer} from "mobx-react";
import Profession from "../models/Profession";
import {abbreviate} from "../utils";


@observer
class ProfessionLabel extends React.Component {
  static propTypes = {
    id: PropTypes.number.isRequired,
    feminin: PropTypes.bool.isRequired,
    pluriel: PropTypes.bool.isRequired,
  };

  @computed
  get profession() {
    return Profession.getById(this.props.id);
  }

  render() {
    const {feminin, pluriel} = this.props;
    return (
      <a href={this.profession.front_url}>
        {abbreviate(this.profession.getLabel(feminin, pluriel), 3)}
      </a>
    );
  }
}


export default ProfessionLabel;
