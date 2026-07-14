"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { TLetterImage } from "@/app/types";
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import ChevronLeftIcon from "@mui/icons-material/ChevronLeft";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import ImageRendition from "./ImageRendition";
import Empty from "./Empty";

export default function LetterImagesReader({
  letterImages,
}: {
  letterImages: TLetterImage[];
}) {
  const t = useTranslations("letter");
  const [rawPage, setPage] = useState(0);
  if (letterImages.length === 0) {
    return <Empty sx={{ height: "50vh" }}>{t("missingImage")}</Empty>;
  }
  // The page state survives client-side navigation between letters; clamp it
  // so a letter with fewer images than the previous one cannot crash.
  const page = Math.min(rawPage, letterImages.length - 1);
  const previous = page >= 1 ? letterImages[page - 1] : null;
  const next = page <= letterImages.length - 2 ? letterImages[page + 1] : null;
  const { id, name, image } = letterImages[page];
  return (
    <Grid container wrap="nowrap" sx={{ flexDirection: "column" }}>
      <Grid>
        <Grid
          container
          wrap="nowrap"
          sx={{
            justifyContent: "space-between",
            alignItems: "center",
            width: "100%",
          }}
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
              sx={{ textAlign: "center", display: "block", lineHeight: "36px" }}
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
      </Grid>
    </Grid>
  );
}
