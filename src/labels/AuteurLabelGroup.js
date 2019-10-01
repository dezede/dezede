import React from 'react';
import PropTypes from 'prop-types';

import {joinWithLast} from "../utils";
import IndividuLabel from "./IndividuLabel";
import ProfessionLabel from "./ProfessionLabel";
import EnsembleLabel from "./EnsembleLabel";


class AuteurLabelGroup extends React.Component {
  static propTypes = {
    individuIds: PropTypes.arrayOf(PropTypes.number).isRequired,
    ensembleIds: PropTypes.arrayOf(PropTypes.number).isRequired,
    professionId: PropTypes.number,
  };

  static defaultProps = {
    professionId: null,
  };

  render() {
    const {individuIds, ensembleIds, professionId} = this.props;
    return (
      <>
        {joinWithLast(ensembleIds.map(id => (
          <EnsembleLabel key={id} id={id} />
        )))}
        {joinWithLast(individuIds.map(id => (
          <IndividuLabel key={id} id={id} />
        )))}
        {
          professionId !== null
            ? (
              <>
                {' ['}
                <ProfessionLabel
                  id={professionId}
                  feminin={false}
                  pluriel={individuIds.length > 1}
                />
                ]
              </>
            )
            : null
        }
      </>
    );
  }
}


export default AuteurLabelGroup;
