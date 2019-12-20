import {computed, observable} from "mobx";

import Model from './Model';
import Individu from "./Individu";
import Evenement from "./Evenement";
import Oeuvre from './Oeuvre';
import Ensemble from "./Ensemble";
import Lieu from './Lieu';
import Partie from './Partie';
import Auteur from "./Auteur";


class Source extends Model {
  static apiName = 'sources';

  @observable title = '';
  @observable folio = '';
  @observable fichier = '';
  @observable type_fichier = -1;
  @observable taille_fichier = '';
  @observable telechargement_autorise = true;
  @observable has_images = false;
  @observable small_thumbnail = '';
  @observable medium_thumbnail = '';
  @observable children = [];
  @observable transcription = '';
  @observable url = '';
  @observable auteurs = [];
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
    this.taille_fichier = data.taille_fichier;
    this.telechargement_autorise = data.telechargement_autorise;
    this.has_images = data.has_images;
    this.small_thumbnail = data.small_thumbnail;
    this.medium_thumbnail = data.medium_thumbnail;
    this.children = data.children;
    this.url = data.url;
    this.transcription = data.transcription;
    this.auteurs = data.auteurs;
    this.individus = data.individus;
    this.evenements = data.evenements;
    this.oeuvres = data.oeuvres;
    this.ensembles = data.ensembles;
    this.lieux = data.lieux;
    this.parties = data.parties;
  }

  get isOther() {
    return this.type_fichier === 0;
  }

  get isImage() {
    return this.type_fichier === 1 && this.children.length === 0;
  }

  get isAudio() {
    return this.type_fichier === 2;
  }

  get isVideo() {
    return this.type_fichier === 3;
  }

  getChild(position) {
    if (!this.loaded) {
      return null;
    }
    return this.constructor.getById(this.children[position]);
  }

  get auteursList() {
    return this.auteurs.map(id => Auteur.getById(id));
  }

  get individusList() {
    return this.individus.map(id => Individu.getById(id));
  }

  get oeuvresList() {
    return this.oeuvres.map(id => Oeuvre.getById(id));
  }

  get partiesList() {
    return this.parties.map(id => Partie.getById(id));
  }

  get lieuxList() {
    return this.lieux.map(id => Lieu.getById(id));
  }

  get evenementsList() {
    return this.evenements.map(id => Evenement.getById(id));
  }

  get ensemblesList() {
    return this.ensembles.map(id => Ensemble.getById(id));
  }

  @computed get linkedObjects() {
    return [
      ...this.individusList,
      ...this.oeuvresList,
      ...this.partiesList,
      ...this.lieuxList,
      ...this.evenementsList,
      ...this.ensemblesList,
    ];
  }

  @computed get fullyLoaded() {
    return (
      this.loaded
      && this.linkedObjects.every(instance => instance.loaded)
    );
  }

  get nomFichier() {
    return this.fichier.replace(/^.*[\\\/]/, '');
  }
}


export default Source;
