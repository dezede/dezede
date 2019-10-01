import React from 'react';
import PropTypes from 'prop-types';
import {computed} from "mobx";
import {observer} from "mobx-react";

import {join} from "../utils";
import Auteur from "../models/Auteur";
import AuteurLabelGroup from "./AuteurLabelGroup";


@observer
class AuteurLabelList extends React.Component {
  static propTypes = {
    ids: PropTypes.arrayOf(PropTypes.number).isRequired,
  };

  @computed
  get auteurs() {
    return this.props.ids.map(id => Auteur.getById(id));
  }

  @computed
  get groups() {
    const groupKeys = [];
    const groupContents = {};
    for (const auteur of this.auteurs) {
      const key = {professionId: auteur.professionId};
      const serializedKey = JSON.stringify(key);
      if (!(serializedKey in groupContents)) {
        groupKeys.push(key);
        groupContents[serializedKey] = {ensembleIds: [], individuIds: []};
      }
      if (auteur.ensembleId !== null) {
        groupContents[serializedKey].ensembleIds.push(auteur.ensembleId);
      }
      if (auteur.individuId !== null) {
        groupContents[serializedKey].individuIds.push(auteur.individuId);
      }
    }
    return {keys: groupKeys, contents: groupContents};
  }

  render() {
    if (!this.auteurs.every(auteur => auteur.fullyLoaded)) {
      return null;
    }
    return join(this.groups.keys.map(key => {
      const serializedKey = JSON.stringify(key);
      return (
        <AuteurLabelGroup
          key={serializedKey}
          ensembleIds={this.groups.contents[serializedKey].ensembleIds}
          individuIds={this.groups.contents[serializedKey].individuIds}
          professionId={key.professionId} />
      );
    }));
  }
}


export default AuteurLabelList;
