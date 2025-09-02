import Image, { ImageProps } from "next/image";
import { TImage as TImageRendition } from "../types";
import React from "react";

export default function ImageRendition({
  rendition: { full_url, width, height, alt },
  ...props
}: Omit<ImageProps, "src" | "width" | "height" | "alt" | "unoptimized"> & {
  rendition: TImageRendition;
}) {
  return (
    <Image
      src={full_url}
      width={width}
      height={height}
      alt={alt}
      unoptimized
      {...props}
    />
  );
}
