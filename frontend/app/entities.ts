import {
  ENSEMBLES_BASE,
  PARTS_BASE,
  PERSONS_BASE,
  PLACES_BASE,
  PROFESSIONS_BASE,
  SOURCES_BASE,
  WORKS_BASE,
} from "./constants";

// The standalone catalogue entities, mirroring the Django index/detail pages
// (/oeuvres/, /individus/, …). Each is backed by /api/public/<key>/.
//
// User-facing labels (title, search placeholder) are not stored here: they live
// in the `authority` translation namespace, keyed by `key` (e.g.
// `authority.oeuvres.title`), so the UI can switch language. This config keeps
// only the structural, language-independent wiring.
export type TEntityKey =
  | "oeuvres"
  | "individus"
  | "ensembles"
  | "lieux"
  | "parties"
  | "professions"
  | "sources";

export interface EntityConfig {
  key: TEntityKey;
  apiList: string;
  base: string;
  // Event-API filter param used to embed the related-events list on the detail
  // page (see libretto BaseEvenementListView.BINDINGS).
  eventFilter: string;
}

export const ENTITIES: Record<TEntityKey, EntityConfig> = {
  oeuvres: {
    key: "oeuvres",
    apiList: "/api/public/oeuvres/",
    base: WORKS_BASE,
    eventFilter: "oeuvre",
  },
  individus: {
    key: "individus",
    apiList: "/api/public/individus/",
    base: PERSONS_BASE,
    eventFilter: "individu",
  },
  ensembles: {
    key: "ensembles",
    apiList: "/api/public/ensembles/",
    base: ENSEMBLES_BASE,
    eventFilter: "ensemble",
  },
  lieux: {
    key: "lieux",
    apiList: "/api/public/lieux/",
    base: PLACES_BASE,
    eventFilter: "lieu",
  },
  parties: {
    key: "parties",
    apiList: "/api/public/parties/",
    base: PARTS_BASE,
    eventFilter: "partie",
  },
  professions: {
    key: "professions",
    apiList: "/api/public/professions/",
    base: PROFESSIONS_BASE,
    eventFilter: "profession",
  },
  sources: {
    key: "sources",
    apiList: "/api/public/sources/",
    base: SOURCES_BASE,
    eventFilter: "source",
  },
};
