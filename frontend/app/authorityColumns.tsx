import { useTranslations } from "next-intl";
import Box from "@mui/material/Box";
import type { GridColDef } from "@mui/x-data-grid";
import EntityChip from "@/format/EntityChip";
import PersonChip from "@/format/PersonChip";
import EnsembleChip from "@/format/EnsembleChip";
import SourceIcons from "@/format/SourceIcons";
import { TAuteur, TEntity } from "./types";
import { TEntityKey } from "./entities";
import {
  ENSEMBLES_BASE,
  PARTS_BASE,
  PERSONS_BASE,
  PROFESSIONS_BASE,
  SOURCES_BASE,
  WORKS_BASE,
} from "./constants";
import { capfirst, toRoman } from "./utils";

export type FilterOption = { value: string | number; label: string };

export type GridFilterConfig = {
  param: string;
  label: string;
  // Optional translator for the dropdown option labels. Use it for fixed,
  // enum-like values (centuries, source content types, role/instrument) that
  // the API returns hardcoded in French; leave it unset for options whose
  // labels are database text (e.g. ensemble/source types) so they pass through
  // unchanged.
  getOptionLabel?: (option: FilterOption) => string;
  // When set, the filter renders as a type-ahead autocomplete hitting this
  // endpoint (for value lists too long for a plain <select>, e.g. type de
  // source) instead of a select fed by the static `filters/` option list.
  async?: { endpoint: string };
};

export type AuthorityGridConfig = {
  key: TEntityKey;
  title: string;
  apiList: string;
  base: string;
  searchPlaceholder: string;
  columns: GridColDef[];
  filters: GridFilterConfig[];
  defaultSort?: { field: string; sort: "asc" | "desc" };
};

// The primary column renders the existing chip, which links to the detail page.
// The chip is wrapped so it stays within the fixed-width table cell and its
// label truncates with an ellipsis: the cell's own `text-overflow: ellipsis`
// only applies to direct text, not to the chip's nested label, so without this
// the whole pill is simply hard-clipped at the cell edge with no ellipsis.
export const chipCell: GridColDef["renderCell"] = (params) => (
  <Box
    sx={{
      display: "flex",
      minWidth: 0,
      "& .MuiChip-root": { maxWidth: "100%" },
      // `min-width: 0` lets the label shrink within the chip's flex row, which
      // is what allows the ellipsis to engage instead of the pill overflowing
      // and being clipped by the cell.
      "& .MuiChip-label": {
        minWidth: 0,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
      },
      // Some chip labels (e.g. PersonChip) wrap their content in a block-level
      // element, which swallows the ellipsis — text-overflow only truncates
      // inline content. Force that wrapper inline so the label can truncate.
      "& .MuiChip-label > *": { display: "inline" },
    }}
  >
    <EntityChip entity={params.row as TEntity} />
  </Box>
);

// Renders a work's authors as person/ensemble chips (linking to their detail
// pages) instead of plain text. The chips sit in a single non-wrapping row that
// clips at the cell edge, mirroring the other columns' overflow behaviour.
function AuthorsChips({ auteurs }: { auteurs?: TAuteur[] }) {
  if (!auteurs?.length) {
    return null;
  }
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 0.5,
        minWidth: 0,
        overflow: "hidden",
      }}
    >
      {auteurs.map((auteur) =>
        auteur.individu ? (
          <PersonChip key={`i${auteur.id}`} {...auteur.individu} />
        ) : auteur.ensemble ? (
          <EnsembleChip key={`e${auteur.id}`} {...auteur.ensemble} />
        ) : null,
      )}
    </Box>
  );
}

// The grid configs carry user-facing strings (title, search placeholder, column
// headers, filter labels), so they're built from the `authority` translation
// namespace rather than declared as a static constant. `t` is the namespaced
// translator obtained by the (client) caller via `useTranslations("authority")`.
type AuthorityTranslator = ReturnType<typeof useTranslations>;

// Builds the label for a century filter option ("19" -> "XIXe siècle" /
// "19th century"), driven entirely by the option value so the result follows
// the active locale instead of the French label sent by the API.
function centuryOptionLabel(t: AuthorityTranslator) {
  return (option: FilterOption) => {
    const century = Number(option.value);
    return Number.isFinite(century)
      ? t("centuries.label", { century, roman: toRoman(century) })
      : option.label;
  };
}

// Translates an enum-like option by its value under the given message prefix
// (e.g. "sourceTypes.video", "partieTypes.1").
function enumOptionLabel(t: AuthorityTranslator, prefix: string) {
  return (option: FilterOption) => t(`${prefix}.${option.value}`);
}

export function getAuthorityGrids(
  t: AuthorityTranslator,
): Record<TEntityKey, AuthorityGridConfig> {
  return {
    oeuvres: {
      key: "oeuvres",
      title: t("oeuvres.title"),
      apiList: "/api/public/oeuvres/",
      base: WORKS_BASE,
      searchPlaceholder: t("oeuvres.searchPlaceholder"),
      defaultSort: { field: "titre", sort: "asc" },
      filters: [
        {
          param: "creation",
          label: t("oeuvres.filters.creation"),
          getOptionLabel: centuryOptionLabel(t),
        },
      ],
      columns: [
        {
          field: "titre",
          headerName: t("oeuvres.columns.titre"),
          flex: 3,
          renderCell: chipCell,
        },
        {
          field: "genre",
          headerName: t("oeuvres.columns.genre"),
          flex: 1,
          sortable: false,
          renderCell: (params) => params.row.genre?.nom ?? "",
        },
        {
          field: "auteurs",
          headerName: t("oeuvres.columns.auteurs"),
          flex: 2.5,
          renderCell: (params) => <AuthorsChips auteurs={params.row.auteurs} />,
        },
        {
          field: "creation",
          headerName: t("oeuvres.columns.creation"),
          flex: 2,
          renderCell: (params) => params.row.creation ?? "",
        },
      ],
    },
    individus: {
      key: "individus",
      title: t("individus.title"),
      apiList: "/api/public/individus/",
      base: PERSONS_BASE,
      searchPlaceholder: t("individus.searchPlaceholder"),
      defaultSort: { field: "nom", sort: "asc" },
      filters: [
        {
          param: "naissance",
          label: t("individus.filters.naissance"),
          getOptionLabel: centuryOptionLabel(t),
        },
        {
          param: "deces",
          label: t("individus.filters.deces"),
          getOptionLabel: centuryOptionLabel(t),
        },
      ],
      columns: [
        {
          field: "nom",
          headerName: t("individus.columns.nom"),
          flex: 2.5,
          renderCell: chipCell,
        },
        {
          field: "professions",
          headerName: t("individus.columns.professions"),
          flex: 2.5,
          renderCell: (params) =>
            (params.row.professions ?? [])
              .map((profession: { nom: string }) => capfirst(profession.nom))
              .join(", "),
        },
        {
          field: "naissance",
          headerName: t("individus.columns.naissance"),
          flex: 1.5,
          renderCell: (params) => params.row.naissance ?? "",
        },
        {
          field: "deces",
          headerName: t("individus.columns.deces"),
          flex: 1.5,
          renderCell: (params) => params.row.deces ?? "",
        },
      ],
    },
    ensembles: {
      key: "ensembles",
      title: t("ensembles.title"),
      apiList: "/api/public/ensembles/",
      base: ENSEMBLES_BASE,
      searchPlaceholder: t("ensembles.searchPlaceholder"),
      defaultSort: { field: "nom", sort: "asc" },
      filters: [{ param: "type", label: t("ensembles.filters.type") }],
      columns: [
        {
          field: "nom",
          headerName: t("ensembles.columns.nom"),
          flex: 3,
          renderCell: chipCell,
        },
        {
          field: "type",
          headerName: t("ensembles.columns.type"),
          flex: 1,
          sortable: false,
          renderCell: (params) => params.row.type ?? "",
        },
        {
          field: "siege",
          headerName: t("ensembles.columns.siege"),
          flex: 1,
          sortable: false,
          renderCell: (params) => params.row.siege ?? "",
        },
      ],
    },
    parties: {
      key: "parties",
      title: t("parties.title"),
      apiList: "/api/public/parties/",
      base: PARTS_BASE,
      searchPlaceholder: t("parties.searchPlaceholder"),
      defaultSort: { field: "nom", sort: "asc" },
      filters: [
        {
          param: "type",
          label: t("parties.filters.type"),
          getOptionLabel: enumOptionLabel(t, "partieTypes"),
        },
      ],
      columns: [
        {
          field: "nom",
          headerName: t("parties.columns.nom"),
          flex: 4,
          renderCell: chipCell,
        },
        {
          field: "type",
          headerName: t("parties.columns.type"),
          flex: 1,
          sortable: false,
          renderCell: (params) => params.row.type_display ?? "",
        },
      ],
    },
    professions: {
      key: "professions",
      title: t("professions.title"),
      apiList: "/api/public/professions/",
      base: PROFESSIONS_BASE,
      searchPlaceholder: t("professions.searchPlaceholder"),
      defaultSort: { field: "nom", sort: "asc" },
      filters: [],
      columns: [
        {
          field: "nom",
          headerName: t("professions.columns.nom"),
          flex: 3,
          renderCell: chipCell,
        },
        {
          field: "individus_count",
          headerName: t("professions.columns.individus_count"),
          flex: 1,
          sortable: false,
          type: "number",
        },
        {
          field: "oeuvres_count",
          headerName: t("professions.columns.oeuvres_count"),
          flex: 1,
          sortable: false,
          type: "number",
        },
      ],
    },
    sources: {
      key: "sources",
      title: t("sources.title"),
      apiList: "/api/public/sources/",
      base: SOURCES_BASE,
      searchPlaceholder: t("sources.searchPlaceholder"),
      defaultSort: { field: "ancrage", sort: "asc" },
      filters: [
        {
          param: "icons",
          label: t("sources.filters.icons"),
          getOptionLabel: enumOptionLabel(t, "sourceTypes"),
        },
        {
          param: "ancrage",
          label: t("sources.filters.ancrage"),
          getOptionLabel: centuryOptionLabel(t),
        },
        {
          param: "type",
          label: t("sources.filters.type"),
          async: { endpoint: "/api/public/sources/source_types/" },
        },
      ],
      columns: [
        {
          field: "icons",
          headerName: t("sources.columns.icons"),
          flex: 1,
          sortable: false,
          renderCell: (params) => <SourceIcons types={params.row.data_types} />,
        },
        {
          field: "title",
          headerName: t("sources.columns.title"),
          flex: 4,
          sortable: false,
          renderCell: chipCell,
        },
        {
          field: "ancrage",
          headerName: t("sources.columns.ancrage"),
          flex: 1.3,
          renderCell: (params) => params.row.ancrage ?? "",
        },
        {
          field: "type",
          headerName: t("sources.columns.type"),
          flex: 1.3,
          sortable: false,
          renderCell: (params) => params.row.type ?? "",
        },
      ],
    },
    // `lieux` uses the recursive PlaceTree, not a grid; included for type
    // completeness but never rendered as a grid.
    lieux: {
      key: "lieux",
      title: t("lieux.title"),
      apiList: "/api/public/lieux/",
      base: "",
      searchPlaceholder: t("lieux.searchPlaceholder"),
      filters: [],
      columns: [],
    },
  };
}
