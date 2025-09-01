import Image from "next/image";
import { TImage as TImageRendition } from "../types";
import React from "react";

export default function ImageRendition({
  rendition: { full_url, width, height, alt },
  style,
}: {
  rendition: TImageRendition;
  style?: React.CSSProperties;
}) {
  return (
    <Image
      src={full_url}
      width={width}
      height={height}
      alt={alt}
      unoptimized
      style={style}
    />
  );
}
