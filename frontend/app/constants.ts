export const ROOT_SLUG: string = "openletter";

export const INDIVIDU_FIELDS = [
  "particule_nom",
  "nom",
  "particule_nom_naissance",
  "nom_naissance",
  "prenoms",
  "designation",
  "titre",
  "titre_display",
  "pseudonyme",
].join(",");

export const PLACE_FIELDS = ["nom", "nature(nom,referent)", "parent(nom)"].join(
  ",",
);

export const WORK_FIELDS = [
  "prefixe_titre",
  "titre",
  "coordination",
  "prefixe_titre_secondaire",
  "titre_secondaire",
  "genre(nom)",
  "tempo",
  "numero",
  "coupe",
  "incipit",
  "tonalite",
  "arrangement",
  "surnom",
  "nom_courant",
  "opus",
  "ict",
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

export const EVENT_FIELDS = [
  `debut_lieu(${PLACE_FIELDS})`,
  "debut_lieu_approx",
  "debut_date",
  "debut_date_approx",
  "debut_heure",
  "debut_heure_approx",
  "circonstance",
  "relache",
];

export const BODY_EXTRA_FIELDS = ["streamfield_page(-detail_url,html_url,search_description)"];
