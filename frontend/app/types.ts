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

export enum EModelType {
  LETTER_IMAGE = "correspondence.LetterImage",
  LETTER_SENDER = "correspondence.LetterSender",
  LETTER_RECIPIENT = "correspondence.LetterRecipient",
  PLACE = "libretto.Lieu",
  EVENT = "libretto.Evenement",
  ENSEMBLE = "libretto.Ensemble",
  PERSON = "libretto.Individu",
  WORK = "libretto.Oeuvre",
  PART = "libretto.Partie",
  WORK_GENRA = "libretto.GenreDOeuvre",
  SECTION = "libretto.Pupitre",
  PROFESSION = "libretto.Profession",
  SOURCE = "libretto.Source",
  USER = "accounts.HierarchicUser",
}

export type TRelated<E extends string = EModelType | EPageType> = {
  id: number;
  meta: {
    type: E;
  };
};

export type TRelatedUser = TRelated<EModelType.USER> & {
  username: string;
  first_name: string;
  last_name: string;
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
  referent: boolean;
};

export type TRelatedSection = TRelated<EModelType.SECTION> & {
  partie: TRelatedPart;
  soliste: boolean;
  quantite_min: number;
  quantite_max: number;
  facultatif: boolean;
};

export enum EExtractCategory {
  // Mirrors `Oeuvre.categorie_type_extrait`, which drives `get_extrait`'s
  // formatting: NUMERO → "№ X" (morceau), ORDINAL → "X." (mouvement/pièce),
  // ROMAN → roman numeral, DEFAULT → arabic. NUMERO and ORDINAL are the
  // "hidden" types: their designator is shown only when the work has a title.
  DEFAULT = "default",
  NUMERO = "numero",
  ORDINAL = "ordinal",
  ROMAN = "roman",
}

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
  // Raw tonalité code: gamme + note + alteration (e.g. "Aa+"), or "" when unset.
  // Localised on the client (see the `tonalite` node in `richLabel`).
  tonalite: string;
  sujet: string;
  arrangement: string | null;
  surnom: string;
  nom_courant: string;
  opus: string;
  ict: string;
  extrait_de: TRelatedWork | null;
  type_extrait: string | null;
  categorie_type_extrait: EExtractCategory;
  numero_extrait: string;
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
  prenoms_complets: string;
  designation: EPersonDesignation;
  titre: EPersonTitre;
  titre_display: string;
  pseudonyme: string;
  naissance_date: string | null;
  naissance_date_approx: string;
  deces_date: string | null;
  deces_date_approx: string;
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
};

export enum EPageType {
  LETTER_INDEX = "correspondence.LetterIndex",
  LETTER_CORPUS = "correspondence.LetterCorpus",
  LETTER = "correspondence.Letter",
}

export type TSibling = { title: string; url: string } | null;

export type TFindPageData = {
  id: number;
  apiUrl: string;
  type: EPageType;
  title: string;
  seoTitle: string;
  description: string;
  ancestors: TAncestors;
  previous: TSibling;
  next: TSibling;
  url: string;
  owner: TRelatedUser;
  firstPublishedAt: string;
};

export type TAncestors = { id: number; title: string; owner: TRelatedUser }[];

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
  senders: (TRelated<EModelType.LETTER_SENDER> & {
    person: TRelatedPerson;
  })[];
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
  edition: string;
  storage_place: TRelatedPlace | null;
  storage_call_number: string;
  source_url: string;
  transcription: string;
  description: string;
  owner: TRelatedUser;
  last_published_at: string;
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

// -- Events (libretto.Evenement) -------------------------------------------

export type TRelatedProfession = TRelated<EModelType.PROFESSION> & {
  nom: string;
  nom_pluriel: string;
  nom_feminin: string;
  nom_feminin_pluriel: string;
};

export type TAuteur = {
  id: number;
  profession: TRelatedProfession | null;
  individu: TRelatedPerson | null;
  ensemble: TRelatedEnsemble | null;
};

// A work with its authors (composers, librettists…), as served by the event API.
export type TWorkFull = TRelatedWork & {
  auteurs: TAuteur[];
};

// A work as served by the dossier d'œuvres list (`DossierWorkSerializer`):
// authors, its world-premiere line, and its grouped sources.
export type TDossierWork = TWorkFull & {
  creation: string | null;
  sources: TSourceGroup[];
};

export type TDistributionElement = {
  id: number;
  individu: TRelatedPerson | null;
  ensemble: TRelatedEnsemble | null;
  partie: TRelatedPart | null;
  profession: TRelatedProfession | null;
};

export type TCaracteristique = {
  valeur: string;
  type: { nom: string } | null;
};

export enum ENumerotation {
  ORDERED = "O", // numbered: 1, 2, 3…
  BRACKETS = "B", // numbered in brackets (supposition): [1], [2]…
  BULLET = "U", // bullet, unordered
  EMPTY = "E", // no number (intermission, etc.)
}

export type TProgrammeElement = {
  id: number;
  numerotation: ENumerotation;
  numero: number | "";
  oeuvre: TWorkFull | null;
  autre: string;
  caracteristiques: TCaracteristique[];
  distribution: TDistributionElement[];
};

export type TEvent = TRelated<EModelType.EVENT> & {
  debut_date: string | null;
  debut_date_approx: string;
  debut_heure: string | null;
  debut_heure_approx: string;
  debut_lieu: TRelatedPlace | null;
  debut_lieu_approx: string;
  fin_date: string | null;
  fin_date_approx: string;
  fin_heure: string | null;
  fin_heure_approx: string;
  fin_lieu: TRelatedPlace | null;
  fin_lieu_approx: string;
  circonstance: string;
  relache: boolean;
  programme_incomplet: boolean;
  recette_generale: string | null;
  caracteristiques: TCaracteristique[];
  distribution: TDistributionElement[];
  programme: TProgrammeElement[];
  // Only present on the event *detail* payload (omitted from list rows).
  sources?: TSourceGroup[];
  etat?: TEtat | null;
  notes_publiques?: string;
};

// One "panel" of linked sources: a type heading plus its sources. Shared by the
// event payload and every autorité detail's bottom sources list.
export type TSourceGroup = {
  type: string;
  sources: TSource[];
};

// A dossier de sources' "Données" tab: one block per source type, each paginated
// on its own (the frontend appends further pages of `results` via infinite
// scroll, keyed by `type_id`).
export type TDossierSourceGroup = {
  type: string;
  // The per-group load-more key: a source-type pk when grouping by type, or a
  // year (or "" for undated rows) when grouping "Par date".
  type_id: number | string;
  count: number;
  results: TSource[];
};

export type TDossierSources = {
  count: number;
  groups: TDossierSourceGroup[];
};

// DRF LimitOffsetPagination envelope.
export type TPaginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

// -- Standalone catalogue entities (index + detail pages) -------------------

// Owner of an object, for the author link (shown to anonymous visitors too).
export type TOwner = { username: string; str: string; url: string };

// Owner + admin change/delete links added to every detail endpoint by the
// backend's `AdminLinkMixin`. Mirrors the Django frontend's `frontend_admin`
// button group. `owner` is always present; `can_*` are object-level permissions;
// `is_public` is false for unpublished records (drives the "Privé" padlock).
export type TAdminLink = {
  owner: TOwner | null;
  is_public: boolean;
  can_change: boolean;
  can_delete: boolean;
  change_url: string;
  delete_url: string;
};

// Detail payload of /api/public/individus/<pk>/ (PersonSerializer + extras).
export type TPersonDetail = TRelatedPerson &
  TAdminLink & {
    isni: string;
    biographie: string;
    naissance: string;
    deces: string;
    professions: TRelatedProfession[];
    etat: TEtat | null;
    notes_publiques: string;
    // Heavy related collections are no longer inlined; only their totals ship
    // with the detail payload. The chips are fetched a page at a time from
    // /api/public/individus/<pk>/related/?collection=… (see RelatedEntitiesPanel).
    oeuvres_count: number;
    membre_de: TRelatedEnsemble[];
    parties_creees_count: number;
    publications_count: number;
    dedicaces_count: number;
    parents: TParenteGroup[];
    enfants: TParenteGroup[];
    sources: TSourceGroup[];
  };

// One territory slice of an ensemble's diffusion donut (nom, total events,
// events held *only* there).
export type TTerritoireDiffusion = {
  nom: string;
  count: number;
  exclusive_count: number;
};

export type TEnsembleDetail = TRelatedEnsemble &
  TAdminLink & {
    type: string | null;
    etat: TEtat | null;
    isni: string;
    siege: TRelatedPlace | null;
    smart_period: string | null;
    notes_publiques: string;
    // Heavy related collections: only their totals ship; chips are fetched a
    // page at a time from /api/public/ensembles/<pk>/related/?collection=…
    membres_count: number;
    oeuvres_count: number;
    evenements_par_territoire: TTerritoireDiffusion[];
    sources: TSourceGroup[];
  };

export type TPlaceDetail = TRelatedPlace &
  TAdminLink & {
    etat: TEtat | null;
    historique: string;
    notes_publiques: string;
    has_children: boolean;
    // Heavy related collections: only their totals ship; chips are fetched a
    // page at a time from /api/public/lieux/<pk>/related/?collection=…
    individus_nes_count: number;
    individus_decedes_count: number;
    oeuvres_creees_count: number;
    sources: TSourceGroup[];
  };

export type TProfessionDetail = TRelatedProfession &
  TAdminLink & {
    etat: TEtat | null;
    // Heavy related collections: only their totals ship; chips are fetched a
    // page at a time from /api/public/professions/<pk>/related/?collection=…
    parties_count: number;
    individus_count: number;
    oeuvres_count: number;
    sources: TSource[];
    parent: TRelatedProfession | null;
    has_children: boolean;
  };

export type TPartDetail = TRelatedPart &
  TAdminLink & {
    etat: TEtat | null;
    professions: TRelatedProfession[];
    premier_interprete: TRelatedPerson | null;
    premier_interprete_feminin: boolean;
    // Heavy related collections: only their totals ship; chips are fetched a
    // page at a time from /api/public/parties/<pk>/related/?collection=…
    interpretes_count: number;
    repertoire_count: number;
    parent: TRelatedPart | null;
    has_children: boolean;
    notes_publiques: string;
    sources: TSourceGroup[];
  };

// One end of an ambitus: a chromatic note index (0 = do/C … 11 = si/B) and a
// scientific-notation octave number.
export type TPitch = {
  note: number;
  octave: number;
};

export type TAmbitus = {
  lower: TPitch;
  upper: TPitch;
};

export type TWorkDetail = TWorkFull &
  TAdminLink & {
    etat: TEtat | null;
    creation: string | null;
    // Raw ambitus endpoints (chromatic note index 0–11 + octave); the frontend
    // localises the note names. Null when no ambitus is recorded.
    ambitus: TAmbitus | null;
    notes_publiques: string;
    has_children: boolean;
    // Heavy related collection: only its total ships; chips are fetched a page
    // at a time from /api/public/oeuvres/<pk>/related/?collection=dedicataires
    dedicataires_count: number;
    parents: TParenteGroup[];
    enfants: TParenteGroup[];
    oeuvres_associees: TRelatedWork[];
    sources: TSourceGroup[];
  };

// Event detail = the event payload plus the admin links (notes/état live on the
// base TEvent as optional detail-only fields).
export type TEventDetail = TEvent & TAdminLink;

// One row of /api/evenements/yearly_counts/: a civil year and how many events
// (matching the current filters) start in it. Used by the autorité detail page
// to list events grouped by year, as the Django HTML frontend does.
export type TYearlyCount = {
  year: number;
  count: number;
};

// /api/public/sources/ card + detail.
export type TSource = TRelated<EModelType.SOURCE> & {
  title: string;
  type: string | null;
  // Present on row/grouped payloads (index table, related-sources lists): the
  // source date and its content types (image/audio/video/text/link/other).
  ancrage?: string | null;
  data_types?: string[];
};

// A promoted source as shown in the bibliothèque gallery: the source chip data
// plus a preview thumbnail or, failing that, a short transcription excerpt
// (`SourceGallerySerializer`). Both are null when the source has no preview.
export type TSourceThumbnail = {
  src: string;
  width: number;
  height: number;
};

export type TSourceGalleryItem = TSource & {
  thumbnail: TSourceThumbnail | null;
  excerpt: string | null;
  // Number of scanned page-images; > 1 marks a multi-page book in the gallery.
  pages_count: number;
};

export type TSourceMediaFile = { url: string; mimetype: string };

export type TSourceMedia = {
  kind: "audio" | "video";
  is_full: boolean;
  sources: TSourceMediaFile[];
  width?: number;
  height?: number;
};

// The Consulter-tab download button: an external permalink or a downloadable
// file (with its human-readable size). Mirrors the legacy `SourceView`.
export type TSourceDownload = {
  kind: "link" | "file";
  url: string;
  size?: string;
};

export type TSourceImage = {
  id: number;
  label: string;
  url: string;
  thumbnail: string;
  // Catalogue entities linked to this page, rendered as chips under the reader.
  related: TEntity[];
  // Per-page owner + admin links (each page is its own `Source`).
  admin: TAdminLink;
};

// Academic reference shared by every record that can be cited (source, dossier).
export type TCitation = {
  title: string;
  url: string;
  editeurs: string[];
};

export type TSourceCitation = TCitation & {
  date_publication: string | null;
};

export type TSourceDetail = TSource &
  TAdminLink & {
    etat: TEtat | null;
    pretty_title: string;
    legende: string;
    notes_publiques: string;
    has_presentation_tab: boolean;
    has_index_tab: boolean;
    parent: TSource | null;
    auteurs_html: string | null;
    nested_individus: TRelatedPerson[];
    nested_oeuvres: TRelatedWork[];
    nested_parties: TRelatedPart[];
    nested_lieux: TRelatedPlace[];
    nested_ensembles: TRelatedEnsemble[];
    is_audio: boolean;
    is_video: boolean;
    is_collection: boolean;
    is_image: boolean;
    media: TSourceMedia | null;
    images: TSourceImage[];
    collection_children: TSource[];
    transcription: string;
    download: TSourceDownload | null;
    presentation: string;
    contexte: string;
    sources_et_protocole: string;
    bibliographie: string;
    publications: string;
    developpements: string;
    citation: TSourceCitation | null;
  };

// Any entity served by the public index endpoints, dispatched on `meta.type`.
export type TEntity =
  | TRelatedWork
  | TRelatedPerson
  | TRelatedEnsemble
  | TRelatedPlace
  | TRelatedPart
  | TRelatedProfession
  | TSource;

// -- Shared detail-page shapes ----------------------------------------------

// Publication state (libretto.Etat) attached to every authority detail payload.
export type TEtat = {
  nom: string;
  message: string;
  public: boolean;
};

// A parenté type (TypeDeParente): the four labels Django picks between when
// heading a group of parents/children (singular/plural × direct/relative).
export type TTypeDeParente = {
  nom: string;
  pluriel: string;
  nom_relatif: string;
  relatif_pluriel: string;
};

// One group of related works/persons sharing a parenté type, already grouped
// server-side (mirrors the Django `{% regroup … by type %}`).
export type TParenteGroup = {
  type: TTypeDeParente;
  entities: TEntity[];
};

// One node of a lazily-loaded entity tree (œuvre extraits, partie/profession
// children) — the generic counterpart of the place tree node.
export type TTreeNode = {
  id: number;
  label: string;
  has_children: boolean;
};

// -- Global search ----------------------------------------------------------

// One hit from /api/public/search/ — a uniform shape across all entity types.
export type TSearchResult = {
  id: number;
  meta: { type: string };
  label: string;
  // Highlighted context snippet (HTML with <mark> tags) — only on the full
  // search page, omitted for the navbar's autocomplete responses.
  snippet?: string;
};

// Per-entity-type facet (model label + live count) from /api/public/search/.
export type TSearchFacet = {
  value: string;
  label: string;
  count: number;
};

// -- Dossiers ---------------------------------------------------------------

export type TDossierKind = "evenements" | "oeuvres" | "sources";

export type TDossierCard = {
  id: number;
  meta: { type: string };
  titre: string;
  titre_court: string;
  slug: string;
  // Active kinds in canonical order (a dossier can mix several), with the
  // number of items each one selects. On the index the counts are computed
  // lazily (the list() endpoint returns `null` and the frontend fetches them
  // per visible card via the `counts` action), so `counts` is nullable here;
  // the detail payload (TDossierDetail) always provides them.
  kinds: TDossierKind[];
  counts: Partial<Record<TDossierKind, number>> | null;
  children_count: number;
  cover_image: string | null;
  excerpt: string;
  categorie_id: number | null;
};

export type TDossierCategory = {
  id: number;
  nom: string;
};

export type TDossierIndex = {
  categories: TDossierCategory[];
  dossiers: TDossierCard[];
};

export type TScenarioChoice = { value: string; label: string };

// A dossier editor/contributor: display name plus the URL of their (always
// public) Django profile page, which the sidebar chip links to. The
// musicaLetters frontend has no profile route of its own.
export type TDossierUser = { name: string; url: string };

export type TDossierDetail = TDossierCard &
  TAdminLink & {
    // The detail endpoint (retrieve()) computes the counts inline, so here
    // they are always present (narrowing TDossierCard's nullable `counts`).
    counts: Partial<Record<TDossierKind, number>>;
    // Active kinds with a Visualisations panel (map + statistics).
    stats_kinds: TDossierKind[];
    presentation: string;
    contexte: string;
    sources_et_protocole: string;
    bibliographie: string;
    publications: string;
    // Sidebar metadata: editors and contributors with profile links.
    editeurs_scientifiques: TDossierUser[];
    contributors: TDossierUser[];
    date_publication: string | null;
    developpements: string;
    // Sidebar export actions, gated server-side (auth / superuser).
    can_export_pdf: boolean;
    can_export_stats: boolean;
    // Only present when `can_export_stats` is true (powers the export dialog).
    scenario_choices?: TScenarioChoice[];
    children: TDossierCard[];
    citation: TCitation;
  };

export type TPeriod = {
  name: string;
  color: string;
  text_color: string;
  count: number;
};

export type TChordNode = {
  id: number;
  individu: TRelatedPerson;
  color: string;
};

export type TChord = {
  nodes: TChordNode[];
  matrix: number[][];
  legend: { name: string; color: string }[];
};

export type TDossierStats = {
  oeuvres_par_periode: TPeriod[];
  n_oeuvres: number;
  chord: TChord | null;
};

export type TEventFacets = {
  date_range: { min_year: number; max_year: number };
  total_count: number;
  is_authenticated: boolean;
};

export type TGeoFeature = {
  type: "Feature";
  properties: { lieu_pk: number; tooltip: string; n: number };
  geometry: { type: string; coordinates: [number, number] };
};

export type TGeoJson = {
  type: "FeatureCollection";
  features: TGeoFeature[];
};
