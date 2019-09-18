import {computed, observable} from "mobx";
import axios from "axios";


class Model {
  static apiName = '';
  static cache = {};
  @observable loaded = false;

  @observable id = null;
  @observable str = '';
  @observable owner = null;
  @observable front_url = '';
  @observable edit_url = '';
  @observable delete_url = '';

  constructor(id) {
    this.id = id;
  }

  get key() {
    return `${this.constructor.name}-${this.id}`;
  }

  static getBaseApiUrl() {
    return (
      process.env.NODE_ENV === 'production'
        ? ''
        : 'http://localhost:8000'
    );
  }

  getApiUrl = () => (
    `${Model.getBaseApiUrl()}/api/${this.constructor.apiName}/${this.id}/`
  );

  setData(data) {
    this.str = data.str;
    this.owner = data.owner;
    this.front_url = data.front_url;
    this.edit_url = data.edit_url;
    this.delete_url = data.delete_url;
  }

  reload = async () => {
    const response = await axios.get(this.getApiUrl());
    this.setData(response.data);
    this.loaded = true;
  };

  load = async () => {
    if (!this.loaded) {
      this.reload();
    }
  };

  static getById(id) {
    if (!id) {
      return null;
    }
    const cacheKey = `${this.apiName}-${id}`;
    if (cacheKey in this.cache) {
      return this.cache[cacheKey];
    }
    const instance = new this(id);
    this.cache[cacheKey] = instance;
    instance.load();
    return instance;
  }

  @computed get label() {
    return this.str;
  }

  toString = () => {
    return this.label;
  };
}


export default Model;
