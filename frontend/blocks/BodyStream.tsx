import Stack from "@mui/material/Stack";
import { TBodyStreamBlock } from "@/app/types";
import RichText from "@/components/RichText";
import ImagesRowBlock from "@/blocks/ImagesRowBlock";
import PagesRowBlock from "@/blocks/PagesRowBlock";

export default function BodyStream({ value }: { value: TBodyStreamBlock }) {
  return (
    <Stack direction="column" flexWrap="nowrap" spacing={2}>
      {value.map((block) => {
        const { id, type, value } = block;
        switch (type) {
          case "text":
            return <RichText key={id} value={value} />;
          case "pages_row":
            return <PagesRowBlock key={id} block={block} />;
          case "images_row":
            return <ImagesRowBlock key={id} block={block} />;
        }
      })}
    </Stack>
  );
}
