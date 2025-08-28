export type TImage = {
  url: string;
  full_url: string;
  width: number;
  height: number;
  alt: string;
};

export enum EBlockType {
  LIEU = "lieu",
}

export type TBlock<E extends string = EBlockType, T = number> = {
  id: string;
  type: E;
  value: T;
};

export enum EModelType {
  LETTER_IMAGE = "correspondence.LetterImage",
  LETTER_RECIPIENT = "correspondence.LetterRecipient",
  PERSON = "libretto.Individu",
  PLACE = "libretto.Lieu",
}

export type TRelated<E extends string = EModelType> = {
  id: number;
  meta: {
    type: E;
  };
};

export enum EPersonTitre {
  MAN = "M",
  GIRL = "J",
  WOMAN = "F",
}

export enum EPersonDesignation {
  STANDARD = "S",
  PSEUDONYME = "P",
  LAST_NAME = "L",
  BIRTH_NAME = "B",
  FIRST_NAME = "F",
}

export type TRelatedPerson = TRelated<EModelType.PERSON> & {
  particule_nom: string;
  nom: string;
  particule_nom_naissance: string;
  nom_naissance: string;
  prenoms: string;
  designation: EPersonDesignation;
  titre: EPersonTitre;
  titre_display: string;
  pseudonyme: string;
};

export type TRelatedPlace = TRelated<EModelType.PLACE> & {
  nom: string;
  nature: {
    referent: boolean;
  };
  parent: null | {
    nom: string;
  };
};

export type TLetterImage = TRelated<EModelType.LETTER_IMAGE> & {
  name: string;
  image: TImage;
  thumbnail: TImage;
  references: TBlock<EBlockType.LIEU>[];
};

export enum EPageType {
  LETTER_INDEX = "correspondence.LetterIndex",
  LETTER_CORPUS = "correspondence.LetterCorpus",
  LETTER = "correspondence.Letter",
}

export type TFindPage = {
  id: number;
  apiUrl: string;
  type: EPageType;
  title: string;
  description: string;
};

export type TAncestors = { id: number; title: string }[];

export type TPage = {
  id: number;
  meta: {
    type: EPageType;
    detail_url: string;
    html_url: string;
    slug: string;
    first_published_at: string;
  };
  title: string;
};

export type TPageDetailed = Omit<TPage, "meta"> & {
  meta: TPage["meta"] & {
    show_in_menus: boolean;
    seo_title: string;
    search_description: string;
  };
  ancestors: TAncestors;
};

export type TPageResults<T = TPage> = {
  meta: {
    total_count: number;
  };
  items: T[];
};
