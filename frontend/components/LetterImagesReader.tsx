"use client";

import { useMemo, useState } from "react";
import { TLetterImage } from "@/app/types";
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import ImageRendition from "./ImageRendition";
import Empty from "./Empty";
import References from "@/format/References";

export default function LetterImagesReader({
  letterImages,
}: {
  letterImages: TLetterImage[];
}) {
  const [page, setPage] = useState(0);
  const previous = useMemo(
    () => (page >= 1 ? letterImages[page - 1] : null),
    [letterImages, page],
  );
  const next = useMemo(
    () => (page <= letterImages.length - 2 ? letterImages[page + 1] : null),
    [letterImages, page],
  );
  if (letterImages.length === 0) {
    return <Empty sx={{ height: "50vh" }}>Image manquante</Empty>;
  }
  const { id, name, image, references } = letterImages[page];
  return (
    <Grid container direction="column" wrap="nowrap">
      <Grid>
        <Grid
          container
          justifyContent="space-between"
          alignItems="center"
          wrap="nowrap"
          width="100%"
        >
          <Grid size={4}>
            <Button
              startIcon={<ChevronLeftIcon />}
              onClick={() => setPage((value) => Math.max(value - 1, 0))}
              sx={{ display: previous === null ? "none" : null }}
            >
              {previous?.name}
            </Button>
          </Grid>
          <Grid size={4}>
            <Typography
              textAlign="center"
              display="block"
              sx={{ lineHeight: "36px" }}
            >
              {name}
            </Typography>
          </Grid>
          <Grid size={4} sx={{ textAlign: "right" }}>
            <Button
              endIcon={<ChevronRightIcon />}
              onClick={() =>
                setPage((value) => Math.min(value + 1, letterImages.length - 1))
              }
              sx={{ display: next === null ? "none" : null }}
            >
              {next?.name}
            </Button>
          </Grid>
        </Grid>
      </Grid>
      <Grid>
        <TransformWrapper>
          <TransformComponent
            wrapperStyle={{ width: "100%", height: "100%" }}
            contentStyle={{ maxWidth: "100%", maxHeight: "100%" }}
          >
            <ImageRendition
              key={id}
              rendition={image}
              priority
              style={{ maxWidth: "100%", height: "auto" }}
            />
          </TransformComponent>
        </TransformWrapper>
        <References
          references={references}
          sx={{ p: 2, justifyContent: "center" }}
        />
      </Grid>
    </Grid>
  );
}
