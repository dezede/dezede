"use client";

import Accordion from "@mui/material/Accordion";
import AccordionDetails from "@mui/material/AccordionDetails";
import AccordionSummary from "@mui/material/AccordionSummary";
import Typography from "@mui/material/Typography";
import { TCitation } from "@/app/types";
import { joinWithLast } from "@/app/utils";
import { useTranslations } from "next-intl";
import OurLink from "./OurLink";
import DateLabel from "@/format/DateLabel";

/**
 * "Pour citer …" accordion shared by sources and dossiers. It mirrors the letter
 * citation (see {@link Citation}) so every record type is cited the same way:
 * an accordion whose summary reads « Pour citer {label} » and whose body links
 * to the canonical dezede.org page through the shared {@link OurLink}.
 */
export default function CitationReference({
  label,
  citation,
  accessDate,
}: {
  label: string;
  citation: TCitation;
  accessDate: string;
}) {
  const t = useTranslations("letter");
  const tSource = useTranslations("source");
  const editeurs =
    citation.editeurs.length > 0
      ? `${joinWithLast(citation.editeurs)} ${tSource("editorParen")}, `
      : "";

  return (
    <div>
      <Accordion>
        <AccordionSummary>
          <Typography variant="overline">
            {t("citePrefix", { target: label })}
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          {editeurs}
          {`« ${citation.title} », `}
          <em>Dezède</em> {tSource("online")}{" "}
          <OurLink href={citation.url}>
            {"dezede.org"}
            {decodeURI(citation.url)}
          </OurLink>{" "}
          ({tSource("consultedOn")} <DateLabel dateString={accessDate} />)
        </AccordionDetails>
      </Accordion>
    </div>
  );
}
