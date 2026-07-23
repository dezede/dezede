import React from "react";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";
import { TCaracteristique } from "@/app/types";
import { capfirst } from "@/app/utils";

/**
 * Renders a list of caractéristiques as "[valeur1, valeur2]", each showing its
 * type as a tooltip (mirroring Django's `hlp(valeur, type)`). Used both at the
 * event level and per programme item.
 */
export default function Characteristics({
  caracteristiques,
  brackets = true,
  caps = false,
}: {
  caracteristiques: TCaracteristique[];
  brackets?: boolean;
  caps?: boolean;
}) {
  if (caracteristiques.length === 0) {
    return null;
  }
  return (
    <Typography component="span" variant="body2" color="text.secondary">
      {brackets ? "[" : null}
      {caracteristiques.map((caracteristique, index) => {
        const valeur =
          caps && index === 0
            ? capfirst(caracteristique.valeur)
            : caracteristique.valeur;
        return (
          <React.Fragment key={index}>
            {index > 0 ? ", " : null}
            {caracteristique.type ? (
              <Tooltip title={caracteristique.type.nom} arrow disableInteractive>
                <span>{valeur}</span>
              </Tooltip>
            ) : (
              valeur
            )}
          </React.Fragment>
        );
      })}
      {brackets ? "]" : null}
    </Typography>
  );
}
