import Box from "@mui/material/Box";
import { TEntity } from "@/app/types";
import EntityChip from "@/format/EntityChip";

/**
 * A wrapped, flexible row of catalogue-entity chips — the Next.js equivalent of
 * a Django `data_table_list` cell. Reuses the per-type `EntityChip` dispatcher,
 * so any mix of works/persons/places/parts/professions/sources renders with the
 * right chip. Returns null when empty so `DetailTable` can drop the whole row.
 */
export default function EntityChipList({
  entities,
  justifyContent = "flex-start",
}: {
  entities: TEntity[];
  justifyContent?: "flex-start" | "center";
}) {
  if (entities.length === 0) {
    return null;
  }
  return (
    <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, justifyContent }}>
      {entities.map((entity) => (
        <EntityChip key={`${entity.meta.type}-${entity.id}`} entity={entity} />
      ))}
    </Box>
  );
}
