"use client";

import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Typography from "@mui/material/Typography";
import SpaceTime from "@/format/SpaceTime";
import { EPageType, TFindPageData } from "../app/types";
import OurLink from "./OurLink";
import UserLink, { UserLabel } from "./UserLink";
import { useEffect, useMemo, useState } from "react";
import { SITE_NAME } from "@/app/constants";

export default function Citation({
  findPageData: { title, type, url, firstPublishedAt, owner, ancestors },
  showParent = false,
}: {
  findPageData: TFindPageData;
  showParent?: boolean;
}) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const parentLabel = useMemo(() => {
    if (!showParent || ancestors.length === 0) {
      return null;
    }
    const parent = ancestors[ancestors.length - 1];
    return (
      <>
        <em>{ancestors[ancestors.length - 1].title}</em>, éd.{" "}
        <UserLabel user={parent.owner} />,{" "}
      </>
    );
  }, [showParent, ancestors]);

  const typeLabel = {
    [EPageType.LETTER_INDEX]: "cette page",
    [EPageType.LETTER_CORPUS]: "ce corpus",
    [EPageType.LETTER]: "cette lettre",
  }[type];
  const absoluteUrl = `${isClient ? document.location.origin : ""}${url}`;
  return (
    <div>
      <Accordion>
        <AccordionSummary>
          <Typography variant="overline">Pour citer {typeLabel}</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <>
            <UserLink user={owner} />
            {" (ed.), "}
          </>
          {`« ${title} », `}
          {parentLabel}
          <em>{SITE_NAME}</em>,{" "}
          <SpaceTime date={firstPublishedAt} hideIcon inline />, [en ligne]{" "}
          <OurLink href={absoluteUrl}>{absoluteUrl}</OurLink> (consulté le{" "}
          <SpaceTime date={new Date().toISOString()} hideIcon inline />)
        </AccordionDetails>
      </Accordion>
    </div>
  );
}
