"use client";

import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Typography from "@mui/material/Typography";
import SpaceTime from "@/format/SpaceTime";
import { TRelatedUser } from "../app/types";
import OurLink from "./OurLink";
import UserLink from "./UserLink";
import { useEffect, useState } from "react";

export default function Citation({
  title,
  url,
  firstPublishedAt,
  editor,
}: {
  title: string;
  url: string;
  firstPublishedAt?: string;
  editor?: TRelatedUser;
}) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const absoluteUrl = `${isClient ? document.location.origin : ""}${url}`;
  return (
    <div>
      <Accordion>
        <AccordionSummary>
          <Typography variant="overline">Pour citer cette page</Typography>
        </AccordionSummary>
        <AccordionDetails>
          {editor === undefined ? null : (
            <>
              <UserLink user={editor} />
              {" (ed.), "}
            </>
          )}
          « {title} », <SpaceTime date={firstPublishedAt} hideIcon inline /> [en
          ligne] <OurLink href={absoluteUrl}>{absoluteUrl}</OurLink> (consulté
          le <SpaceTime date={new Date().toISOString()} hideIcon inline />)
        </AccordionDetails>
      </Accordion>
    </div>
  );
}
