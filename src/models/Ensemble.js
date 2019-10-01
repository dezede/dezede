import Model from "./Model";
import {observable} from "mobx";


class Ensemble extends Model {
  static apiName = 'ensembles';

  @observable html = '';

  setData(data) {
    super.setData(data);
    this.html = data.html;
  }
}


export default Ensemble;
