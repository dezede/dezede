export interface Ancrage {
  date: null | string;
  date_approx: string;
  lieu: null | string;
  lieu_approx: string;
}

export interface Model {
  id: number;
  str: string;
  owner: number | null;
  front_url: string;
  change_url: string;
  delete_url: string;
  can_add: boolean;
  can_change: boolean;
  can_delete: boolean;
}

export type Auteur = {
  id: number;
  owner: number | null;
  profession: number | null;
} & (
  | {
      oeuvre: number;
      source: null;
    }
  | {
      oeuvre: null;
      source: number;
    }
) &
  (
    | {
        individu: number;
        ensemble: null;
      }
    | {
        individu: null;
        ensemble: number;
      }
  );

export interface Ensemble extends Model {
  html: string;
}

export interface Evenement extends Model {}

export interface Individu extends Model {
  html: string;
  prenoms: string;
  nom: string;
  naissance: Ancrage;
  deces: Ancrage;
  professions: number[];
  parents: string[];
}

export interface Lieu extends Model {}

export interface Oeuvre extends Model {}

export interface Partie extends Model {}

export interface Profession extends Model {
  html: string;
  nom: string;
  nom_feminin: string;
  nom_pluriel: string;
  nom_feminin_pluriel: string;
}

export interface Source extends Model {
  title: string;
  folio: string;
  page: string;
  fichier: string | null;
  type_fichier: 0 | 1 | 2 | 3 | null;
  taille_fichier: string;
  telechargement_autorise: boolean;
  has_images: boolean;
  small_thumbnail: string;
  medium_thumbnail: string;
  children: number[];
  transcription: string;
  url: string;
  auteurs: number[];
  individus: number[];
  evenements: number[];
  oeuvres: number[];
  ensembles: number[];
  lieux: number[];
  parties: number[];
}

export interface User extends Model {}
