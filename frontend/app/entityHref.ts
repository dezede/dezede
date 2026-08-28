import {
  DOSSIERS_BASE,
  ENSEMBLES_BASE,
  EVENTS_BASE,
  PARTS_BASE,
  PERSONS_BASE,
  PLACES_BASE,
  PROFESSIONS_BASE,
  SOURCES_BASE,
  WORKS_BASE,
} from "./constants";

// `meta.type` -> the Next base path of that entity's detail pages. Every type
// (including événements and dossiers) is reachable at `BASE/id/<pk>/`.
const BASES: Record<string, string> = {
  "libretto.Oeuvre": WORKS_BASE,
  "libretto.Individu": PERSONS_BASE,
  "libretto.Ensemble": ENSEMBLES_BASE,
  "libretto.Lieu": PLACES_BASE,
  "libretto.Partie": PARTS_BASE,
  "libretto.Profession": PROFESSIONS_BASE,
  "libretto.Source": SOURCES_BASE,
  "libretto.Evenement": EVENTS_BASE,
  "dossiers.Dossier": DOSSIERS_BASE,
};

export function entityHref(metaType: string, id: number): string | null {
  const base = BASES[metaType];
  return base ? `${base}/id/${id}/` : null;
}
