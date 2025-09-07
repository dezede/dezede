import { ECellWidth, ERowHeight } from "@/app/types";
import Grid from "@mui/material/Grid";
import ImageRendition from "@/components/ImageRendition";
import Card from "@mui/material/Card";
import CardActionArea from "@mui/material/CardActionArea";
import { Breakpoint } from "@mui/material/styles";
import { TImagesRowBlock } from "@/app/types";

function LinkCard({
  linkUrl,
  children,
}: {
  linkUrl: string;
  children: React.ReactNode;
}) {
  if (linkUrl) {
    return (
      <Card>
        <CardActionArea component="a" href={linkUrl}>
          {children}
        </CardActionArea>
      </Card>
    );
  }
  return children;
}

const HEIGHTS: { [height in ERowHeight]: number } = {
  small: 100,
  default: 300,
  large: 500,
};

const WIDTHS: { [width in ECellWidth]: { [key in Breakpoint]?: number } } = {
  narrow: { xs: 6, sm: 4, lg: 2, xl: 1 },
  default: { xs: 12, sm: 6, lg: 4, xl: 3 },
  wide: { xs: 12 },
};

export default function ImagesRowBlock({
  block: { id, value },
}: {
  block: TImagesRowBlock;
}) {
  return (
    <Grid key={id} container alignItems="center" spacing={4}>
      {value.images.map(({ image, link_url, width }, index) => (
        <Grid
          key={`${index}:${image.url}`}
          size={WIDTHS[width]}
          display="flex"
          justifyContent="center"
        >
          <LinkCard linkUrl={link_url}>
            <ImageRendition
              rendition={image}
              style={{
                display: "block",
                width: "auto",
                maxWidth: "100%",
                height: "auto",
                maxHeight: HEIGHTS[value.height],
              }}
            />
          </LinkCard>
        </Grid>
      ))}
    </Grid>
  );
}
