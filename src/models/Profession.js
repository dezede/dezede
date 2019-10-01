import Model from "./Model";
import {observable} from "mobx";
import {getPluriel} from "../utils";


class Profession extends Model {
  static apiName = 'professions';

  @observable html = '';
  @observable nom = '';
  @observable nom_feminin = '';
  @observable nom_pluriel = '';
  @observable nom_feminin_pluriel = '';

  setData(data) {
    super.setData(data);
    this.html = data.html;
    this.nom = data.nom;
    this.nom_feminin = data.nom_feminin;
    this.nom_pluriel = data.nom_pluriel;
    this.nom_feminin_pluriel = data.nom_feminin_pluriel;
  }

  getLabel(feminin, pluriel) {
    if (feminin) {
      const nomFeminin = this.nom_feminin || this.nom;
      if (pluriel) {
        return this.nom_feminin_pluriel || getPluriel(nomFeminin);
      }
      return nomFeminin;
    }
    if (pluriel) {
      return this.nom_pluriel || getPluriel(this.nom);
    }
    return this.nom;
  }

  get label() {
    return this.getLabel(false, false);
  }
}

export default Profession;
