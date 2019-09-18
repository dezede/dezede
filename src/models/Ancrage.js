import {observable} from "mobx";


class Ancrage {
  @observable date = null;
  @observable date_approx = '';
  @observable lieu = null;
  @observable lieu_approx = '';

  constructor(date, date_approx, lieu, lieu_approx) {
    this.date = date;
    this.date_approx = date_approx;
    this.lieu = lieu;
    this.lieu_approx = lieu_approx;
  }

  static fromObject(object) {
    return new this(
      object.date, object.date_approx, object.lieu, object.lieu_approx,
    );
  }
}


export default Ancrage;
