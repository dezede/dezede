import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { ENumerotation, TProgrammeElement } from "@/app/types";
import WorkChip from "./WorkChip";
import Casting, { TCastingElement } from "./Casting";
import Characteristics from "./Characteristics";

function NumberPrefix({
  numerotation,
  numero,
}: {
  numerotation: ENumerotation;
  numero: number | "";
}) {
  let text = "";
  switch (numerotation) {
    case ENumerotation.ORDERED:
      text = `${numero}.`;
      break;
    case ENumerotation.BRACKETS:
      text = `[${numero}.]`;
      break;
    case ENumerotation.BULLET:
      text = "•";
      break;
    case ENumerotation.EMPTY:
      return null;
  }
  return (
    <Typography component="span" sx={{ fontVariantNumeric: "tabular-nums" }}>
      {text}
    </Typography>
  );
}

function ProgrammeItem({ element }: { element: TProgrammeElement }) {
  const { oeuvre, autre, distribution, caracteristiques } = element;
  const hasOeuvre = oeuvre !== null;
  const hasAutre = !hasOeuvre && autre !== "";
  const hasDistribution = distribution.length > 0;
  // Mirrors ElementDeProgramme.html: distribution is the main content only when
  // there is neither a work nor free text; otherwise it is appended after ". —".
  const appendDistribution = (hasOeuvre || hasAutre) && hasDistribution;
  const mainIsDistribution = !hasOeuvre && !hasAutre && hasDistribution;

  const composers: TCastingElement[] = hasOeuvre
    ? oeuvre.auteurs.map((auteur) => ({
        individu: auteur.individu,
        ensemble: auteur.ensemble,
        partie: null,
        profession: auteur.profession,
      }))
    : [];

  return (
    <Box component="li" sx={{ listStyle: "none" }}>
      <Stack
        direction="row"
        useFlexGap
        spacing={0.5}
        sx={{ flexWrap: "wrap", alignItems: "center" }}
      >
        <NumberPrefix
          numerotation={element.numerotation}
          numero={element.numero}
        />
        {hasOeuvre ? (
          <>
            <Casting elements={composers} />
            <WorkChip {...oeuvre} />
          </>
        ) : null}
        {hasAutre ? <Typography component="span">{autre}</Typography> : null}
        {mainIsDistribution ? <Casting elements={distribution} /> : null}
        <Characteristics caracteristiques={caracteristiques} />
        {appendDistribution ? (
          <>
            <Typography component="span" color="text.secondary">
              . —
            </Typography>
            <Casting elements={distribution} />
          </>
        ) : null}
      </Stack>
    </Box>
  );
}

export default function Programme({
  elements,
}: {
  elements: TProgrammeElement[];
}) {
  if (elements.length === 0) {
    return null;
  }
  return (
    <Stack component="ol" spacing={1} sx={{ pl: 0, my: 0 }}>
      {elements.map((element) => (
        <ProgrammeItem key={element.id} element={element} />
      ))}
    </Stack>
  );
}
