export type TSearchParams = {
  [key: string]: string | string[] | undefined;
};
export type TAsyncSearchParams = Promise<TSearchParams>;
export type TSearchParamsUpdate = {
  [param: string]: string | number | null | undefined;
};

export type TQueryParams = {
  [param: string]: string | string[] | number | null | undefined;
};

export type TImageRendition = {
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
  PLACE = "libretto.Lieu",
  EVENT = "libretto.Evenement",
  ENSEMBLE = "libretto.Ensemble",
  PERSON = "libretto.Individu",
  WORK = "libretto.Oeuvre",
  PART = "libretto.Partie",
  WORK_GENRA = "libretto.GenreDOeuvre",
  SECTION = "libretto.Pupitre",
}

export type TRelated<E extends string = EModelType | EPageType> = {
  id: number;
  meta: {
    type: E;
  };
};

export type TRelatedEvent = TRelated<EModelType.EVENT> & {
  debut_lieu: TRelatedPlace | null;
  debut_lieu_approx: string;
  debut_date: string | null;
  debut_date_approx: string;
  debut_heure: string | null;
  debut_heure_approx: string;
  relache: boolean;
  circonstance: string;
};

export enum EPartType {
  INSTRUMENT = 1,
  ROLE = 2,
}

export type TRelatedPart = TRelated<EModelType.PART> & {
  nom: string;
  nom_pluriel: string;
  part_type: EPartType;
  oeuvre: TRelatedWork | null;
};

export type TRelatedWorkGenra = TRelated<EModelType.WORK_GENRA> & {
  nom: string;
};

export type TRelatedSection = TRelated<EModelType.SECTION> & {
  partie: TRelatedPart;
  soliste: boolean;
  quantite_min: number;
  quantite_max: number;
  facultatif: boolean;
};

export type TRelatedWork = TRelated<EModelType.WORK> & {
  prefixe_titre: string;
  titre: string;
  coordination: string;
  prefixe_titre_secondaire: string;
  titre_secondaire: string;
  genre: TRelatedWorkGenra | null;
  numero: string;
  coupe: string;
  indeterminee: boolean;
  incipit: string;
  tempo: string;
  tonalite: string;
  sujet: string;
  arrangement: string | null;
  surnom: string;
  nom_courant: string;
  opus: string;
  ict: string;
  // extrait_de: TRelatedWork | null;
  // type_extrait: string | null;
  // numero_extrait: string;
  pupitres: TRelatedSection[];
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
    nom: string;
    referent: boolean;
  };
  parent: null | {
    nom: string;
  };
};

export type TRelatedEnsemble = TRelated<EModelType.ENSEMBLE> & {
  particule_nom: string;
  nom: string;
};

export type TReference =
  | TRelatedPlace
  | TRelatedPerson
  | TRelatedPart
  | TRelatedEnsemble
  | TRelatedEvent
  | TRelatedWork;

export type TLetterImage = TRelated<EModelType.LETTER_IMAGE> & {
  name: string;
  image: TImageRendition;
  thumbnail: TImageRendition;
  references: TReference[];
};

export enum EPageType {
  LETTER_INDEX = "correspondence.LetterIndex",
  LETTER_CORPUS = "correspondence.LetterCorpus",
  LETTER = "correspondence.Letter",
}

export type TFindPageData = {
  id: number;
  apiUrl: string;
  type: EPageType;
  title: string;
  seoTitle: string;
  description: string;
  ancestors: { id: number; title: string }[];
  url: string;
};

export type TAncestors = { id: number; title: string }[];

export type TPage<E extends string = EPageType> = {
  id: number;
  meta: {
    type: E;
    detail_url: string;
    html_url: string;
    first_published_at: string;
  };
  title: string;
};

export type TPageCard<E extends string = EPageType> = Omit<TPage<E>, "meta"> & {
  meta: Pick<TPage<E>["meta"], "type" | "html_url" | "first_published_at"> & {
    search_description: string;
    teaser_thumbnail: TImageRendition | null;
  };
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

export type TLetter = TPageDetailed & {
  sender: TRelatedPerson;
  recipients: (TRelated<EModelType.LETTER_RECIPIENT> & {
    person: TRelatedPerson;
  })[];
  writing_lieu: TRelatedPlace | null;
  writing_lieu_approx: string;
  writing_date: string | null;
  writing_date_approx: string;
  writing_heure: string | null;
  writing_heure_approx: string;
  letter_images: TLetterImage[];
  transcription: string;
  description: string;
};

export enum ELetterTab {
  ALL = "all",
  FROM = "from",
  TO = "to",
  OTHER = "other",
}

export type TYearChoice = { year: number | null; count: number };

export type TRichTextBlock = {
  id: string;
  type: "text";
  value: string;
};

export type TPagesRowBlock<E extends string = EPageType> = {
  id: string;
  type: "pages_row";
  value: TPageCard<E>[];
};

export enum ECellWidth {
  NARROW = "narrow",
  DEFAULT = "default",
  WIDE = "wide",
}

export enum ERowHeight {
  SMALL = "small",
  DEFAULT = "default",
  LARGE = "large",
}

export type TImageCellBlock = {
  image: TImageRendition;
  link_url: string;
  width: ECellWidth;
};

export type TImagesRowBlock = {
  id: string;
  type: "images_row";
  value: {
    height: ERowHeight;
    images: TImageCellBlock[];
  };
};

export type TBodyStreamBlock<EPageBlock extends string = EPageType> = (
  | TRichTextBlock
  | TPagesRowBlock<EPageBlock>
  | TImagesRowBlock
)[];
