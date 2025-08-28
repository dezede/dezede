"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import { TLetterImage } from "../types";
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

export default function LetterImagesReader({
  letterImages,
}: {
  letterImages: TLetterImage[];
}) {
  const [page, setPage] = useState(0);
  const letterImage = useMemo(() => letterImages[page], [letterImages, page]);
  const previous = useMemo(
    () => (page >= 1 ? letterImages[page - 1] : null),
    [letterImages, page],
  );
  const next = useMemo(
    () => (page <= letterImages.length - 2 ? letterImages[page + 1] : null),
    [letterImages, page],
  );
  const {
    id,
    image: { full_url, width, height, alt },
  } = letterImage;
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
            <Typography variant="caption" textAlign="center" display="block">
              {letterImage.name}
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
            <Image
              key={id}
              src={full_url}
              width={width}
              height={height}
              alt={alt}
              unoptimized
              style={{ maxWidth: "100%", height: "auto" }}
            />
          </TransformComponent>
        </TransformWrapper>
      </Grid>
    </Grid>
  );
}
