"use client";

import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Typography from "@mui/material/Typography";
import { EPageType, TFindPageData } from "../app/types";
import OurLink from "./OurLink";
import UserLink, { UserLabel } from "./UserLink";
import { useMemo, useSyncExternalStore } from "react";
import { useTranslations } from "next-intl";
import { SITE_NAME } from "@/app/constants";
import DateLabel from "@/format/DateLabel";

const subscribeNoop = () => () => {};

export default function Citation({
  findPageData: { title, type, url, firstPublishedAt, owner, ancestors },
  showParent = false, showPublicationDate = false,
}: {
  findPageData: TFindPageData;
  showParent?: boolean;
  showPublicationDate?: boolean;
}) {
  const t = useTranslations("letter");
  const tSource = useTranslations("source");
  const isClient = useSyncExternalStore(
    subscribeNoop,
    () => true,
    () => false,
  );

  const parentLabel = useMemo(() => {
    if (!showParent || ancestors.length === 0) {
      return null;
    }
    const parent = ancestors[ancestors.length - 1];
    return (
      <>
        <em>{ancestors[ancestors.length - 1].title}</em>, {tSource("editor")}{" "}
        <UserLabel user={parent.owner} />,{" "}
      </>
    );
  }, [showParent, ancestors, tSource]);

  const typeLabel = {
    [EPageType.LETTER_INDEX]: t("citeThisPage"),
    [EPageType.LETTER_CORPUS]: t("citeThisCorpus"),
    [EPageType.LETTER]: t("citeThisLetter"),
  }[type];

  const absoluteUrl = `${isClient ? document.location.origin : ""}${url}`;

  const publicationDate = showPublicationDate ? (
    <>, <DateLabel dateString={firstPublishedAt} /></>
  ) : null;

  return (
    <div>
      <Accordion>
        <AccordionSummary>
          <Typography variant="overline">
            {t("citePrefix", { target: typeLabel })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <>
            <UserLink user={owner} />
            {` ${tSource("editorParen")}, `}
          </>
          {`« ${title} », `}
          {parentLabel}
          <em>{SITE_NAME}</em>{publicationDate}{" "}
          {tSource("online")}{" "}
          <OurLink href={absoluteUrl}>{"dezede.org"}{decodeURI(url)}</OurLink> ({tSource("consultedOn")}{" "}
          <DateLabel dateString={new Date().toISOString().slice(0, 10)} />)
        </AccordionDetails>
      </Accordion>
    </div>
  );
}
