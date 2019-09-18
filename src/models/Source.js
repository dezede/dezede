import {observable} from "mobx";

import Model from './Model';
import Individu from "./Individu";
import Evenement from "./Evenement";
import Oeuvre from './Oeuvre';
import Ensemble from "./Ensemble";
import Lieu from './Lieu';
import Partie from './Partie';


class Source extends Model {
  static apiName = 'sources';

  @observable title = '';
  @observable folio = '';
  @observable fichier = '';
  @observable type_fichier = '';
  @observable small_thumbnail = '';
  @observable medium_thumbnail = '';
  @observable children = [];
  @observable individus = [];
  @observable evenements = [];
  @observable oeuvres = [];
  @observable ensembles = [];
  @observable lieux = [];
  @observable parties = [];

  setData(data) {
    super.setData(data);
    this.title = data.title;
    this.folio = data.folio;
    this.fichier = data.fichier;
    this.type_fichier = data.type_fichier;
    this.small_thumbnail = data.small_thumbnail;
    this.medium_thumbnail = data.medium_thumbnail;
    this.children = data.children;
    this.individus = data.individus;
    this.evenements = data.evenements;
    this.oeuvres = data.oeuvres;
    this.ensembles = data.ensembles;
    this.lieux = data.lieux;
    this.parties = data.parties;
  }

  getChild(position) {
    if (!this.loaded) {
      return null;
    }
    return this.constructor.getById(this.children[position]);
  }

  get individusList() {
    return this.individus.map(id => Individu.getById(id));
  }

  get evenementsList() {
    return this.evenements.map(id => Evenement.getById(id));
  }

  get oeuvresList() {
    return this.oeuvres.map(id => Oeuvre.getById(id));
  }

  get ensemblesList() {
    return this.ensembles.map(id => Ensemble.getById(id));
  }

  get lieuxList() {
    return this.lieux.map(id => Lieu.getById(id));
  }

  get partiesList() {
    return this.parties.map(id => Partie.getById(id));
  }

  get nomFichier() {
    return this.fichier.replace(/^.*[\\\/]/, '');
  }
}


export default Source;
