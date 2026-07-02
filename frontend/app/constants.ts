export const ROOT_SLUG: string = "musicaletters";
export const SITE_NAME: string = "musicaLetters";

// Événements and dossiers are served by Next under the musicaLetters prefix.
// Each has an index (`BASE/`) and a permanent detail (`BASE/id/<pk>/`).
export const EVENTS_BASE: string = `/${ROOT_SLUG}/evenements`;
export const DOSSIERS_BASE: string = `/${ROOT_SLUG}/dossiers`;
// The authority catalogue (works, persons, places, sources…) is not yet part of
// the Next.js site: its chips and links point to the existing Django frontend,
// whose permanent detail URLs share the same `BASE/id/<pk>/` shape.
export const WORKS_BASE: string = "/oeuvres";
export const PERSONS_BASE: string = "/individus";
export const ENSEMBLES_BASE: string = "/ensembles";
export const PLACES_BASE: string = "/lieux-et-institutions";
export const PARTS_BASE: string = "/roles-et-instruments";
export const PROFESSIONS_BASE: string = "/professions";
export const SOURCES_BASE: string = "/sources";

export const INDIVIDU_FIELDS = [
  "particule_nom",
  "nom",
  "particule_nom_naissance",
  "nom_naissance",
  "prenoms",
  "prenoms_complets",
  "designation",
  "titre",
  "titre_display",
  "pseudonyme",
  "naissance_date",
  "naissance_date_approx",
  "deces_date",
  "deces_date_approx",
].join(",");

export const PLACE_FIELDS = ["nom", "nature(nom,referent)", "parent(nom)"].join(
  ",",
);

// The scalar fields needed to build a work's label/subtitle (mirroring Django's
// `Oeuvre.titre_html`/`get_description`). Reused, nested, for the parent-work
// chain (`extrait_de`) so excerpt labels can prepend their ancestors.
const WORK_LABEL_FIELDS = [
  "prefixe_titre",
  "titre",
  "coordination",
  "prefixe_titre_secondaire",
  "titre_secondaire",
  "genre(nom,referent)",
  "tempo",
  "numero",
  "coupe",
  "incipit",
  "tonalite",
  "sujet",
  "arrangement",
  "surnom",
  "nom_courant",
  "opus",
  "ict",
  "type_extrait",
  "categorie_type_extrait",
  "numero_extrait",
];

// Nest the label fields `depth` levels of `extrait_de` deep. Work trees are
// shallow (opera → acte → scène → morceau), so a few levels cover every case.
function workAncestorFields(depth: number): string {
  const fields = [...WORK_LABEL_FIELDS];
  if (depth > 0) {
    fields.push(`extrait_de(${workAncestorFields(depth - 1)})`);
  }
  return fields.join(",");
}

export const WORK_FIELDS = [
  ...WORK_LABEL_FIELDS,
  `extrait_de(${workAncestorFields(3)})`,
];

export const PART_FIELDS = [
  "nom",
  "nom_pluriel",
  "part_type",
  `oeuvre(${WORK_FIELDS})`,
];
WORK_FIELDS.push(
  `pupitres(partie(${PART_FIELDS}),soliste,quantite_min,quantite_max,facultatif)`,
);
export const ENSEMBLE_FIELDS = ["particule_nom", "nom"];
// Authors are added at the top level only (not in `workAncestorFields`), so the
// chip tooltip can list a work's authors without bloating its ancestor chain.
WORK_FIELDS.push(
  `auteurs(individu(${INDIVIDU_FIELDS}),ensemble(${ENSEMBLE_FIELDS.join(",")}),profession(nom,nom_pluriel,nom_feminin,nom_feminin_pluriel))`,
);

export const BODY_EXTRA_FIELDS = [
  "streamfield_page(-detail_url,html_url,search_description,first_published_at,teaser_thumbnail)",
];
