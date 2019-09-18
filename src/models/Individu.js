import {observable} from "mobx";

import Model from './Model';
import Ancrage from "./Ancrage";


class Individu extends Model {
  static apiName = 'individus';

  @observable prenoms = '';
  @observable nom = '';
  @observable naissance = null;
  @observable deces = null;
  @observable professions = [];
  @observable parents = [];

  setData(data) {
    super.setData(data);
    this.prenoms = data.prenoms;
    this.nom = data.nom;
    this.naissance = Ancrage.fromObject(data.naissance);
    this.deces = Ancrage.fromObject(data.deces);
    this.professions = data.professions;
    this.parents = data.parents;
  }
}


export default Individu;
