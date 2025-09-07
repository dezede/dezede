import React from "react";
import Image, { ImageProps } from "next/image";
import { TImageRendition as TImageRendition } from "@/app/types";

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
