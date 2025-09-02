import Stack from "@mui/material/Stack";
import { TReference } from "@/app/types";
import { SxProps } from "@mui/material/styles";
import ReferenceChip from "./ReferenceChip";

export default function References({
  references,
  sx,
}: {
  references: TReference[];
  sx?: SxProps;
}) {
  return (
    <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" sx={sx}>
      {references.map((reference) => (
        <ReferenceChip key={reference.id} reference={reference} />
      ))}
    </Stack>
  );
}
