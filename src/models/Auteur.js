import Model from "./Model";
import {computed, observable} from "mobx";

import Individu from "./Individu";
import Ensemble from "./Ensemble";
import Profession from "./Profession";


class Auteur extends Model {
  static apiName = 'auteurs';

  @observable individuId = null;
  @observable ensembleId = null;
  @observable professionId = null;

  setData(data) {
    super.setData(data);
    this.individuId = data.individu;
    this.ensembleId = data.ensemble;
    this.professionId = data.profession;
  }

  @computed
  get individu() {
    return Individu.getById(this.individuId);
  }

  @computed
  get ensemble() {
    return Ensemble.getById(this.ensembleId);
  }

  @computed
  get profession() {
    return Profession.getById(this.professionId);
  }

  get fullyLoaded() {
    return (
      this.loaded
      && (this.individuId === null || this.individu.loaded)
      && (this.ensembleId === null || this.ensemble.loaded)
      && (this.professionId === null || this.profession.loaded)
    );
  }
}

export default Auteur;
